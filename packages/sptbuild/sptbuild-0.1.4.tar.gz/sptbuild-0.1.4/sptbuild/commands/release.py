"""Release command - Create a GitLab release linking to job artifacts (CI mode)."""

import os
import sys
import json
import requests

from ..lib import (
    get_version,
    get_changelog_for_version,
    get_project_id,
    get_ci_job_token,
    get_ci_api_url,
    get_package_name,
    get_version_file,
)


def generate_release_notes(version: str) -> str:
    """
    Generate release notes by parsing CHANGELOG.md.

    This extracts the release notes for the specified version from CHANGELOG.md.
    This approach works correctly with the intended workflow where maintainers
    run 'towncrier build --version X.Y.Z' before tagging, which consumes the
    fragment files and updates CHANGELOG.md.
    """
    notes = get_changelog_for_version(version)
    if notes:
        return notes
    else:
        print(f"Warning: No changelog entries found for version {version}")
        return f"Release {version}"


def run():
    """Create GitLab release with package registry link."""
    # Get CI environment variables
    project_id = get_project_id()
    job_token = get_ci_job_token()
    api_url = get_ci_api_url()
    package_name = get_package_name()
    version_file = get_version_file()
    ci_commit_tag = os.environ.get('CI_COMMIT_TAG')

    # Validate required variables
    if not all([project_id, job_token, api_url, package_name, version_file]):
        print("Error: Missing required CI environment variables")
        sys.exit(1)

    if not ci_commit_tag:
        print("Error: CI_COMMIT_TAG environment variable is required (this command should only run on tag pipelines)")
        sys.exit(1)

    # Get version from Plugin.cs
    version = get_version()
    if not version:
        print("Error: Could not determine version")
        sys.exit(1)

    print(f"Creating release for version {version}")

    # Generate release notes
    release_notes = generate_release_notes(version)

    # Build paths
    zip_filename = f"{package_name}-v{version}.zip"
    zip_path = f"bin/upload/{zip_filename}"

    # Verify zip file exists
    if not os.path.exists(zip_path):
        print(f"Error: Zip file not found: {zip_path}")
        sys.exit(1)

    # Upload to Package Registry (generic packages)
    print(f"Uploading {zip_filename} to Package Registry...")
    package_url = f"{api_url}/projects/{project_id}/packages/generic/{package_name}/{version}/{zip_filename}"

    headers = {
        'JOB-TOKEN': job_token,
    }

    with open(zip_path, 'rb') as f:
        upload_response = requests.put(package_url, headers=headers, data=f)

    if upload_response.status_code not in (200, 201):
        print(f"Error: Failed to upload to Package Registry (status {upload_response.status_code})")
        print(f"Response: {upload_response.text}")
        sys.exit(1)

    print("✓ Package uploaded to Package Registry")
    print(f"Package URL: {package_url}")

    # Create release
    release_url = f"{api_url}/projects/{project_id}/releases"
    headers = {
        'JOB-TOKEN': job_token,
        'Content-Type': 'application/json',
    }

    data = {
        'name': f'Release {version}',
        'tag_name': ci_commit_tag,
        'ref': ci_commit_tag,
        'description': release_notes,
        'assets': {
            'links': [{
                'name': f'{package_name}-v{version}.zip',
                'url': package_url,
                'link_type': 'package'
            }]
        }
    }

    print(f"Creating release at: {release_url}")
    response = requests.post(release_url, headers=headers, json=data)

    print(f"Status: {response.status_code}")
    if response.status_code not in (200, 201):
        print(f"Error: {response.text}")
        sys.exit(1)

    print("✓ Release created successfully!")
    print(f"Download URL: {package_url}")
    print("Package will be available in Package Registry → Generic packages")
