"""Upload command - Upload release zip to GitLab project uploads."""

import os
import sys
import json
import argparse
import requests

from ..lib import (
    get_secret_token,
    get_project_id,
    get_package_name,
    get_version,
    upload_dirname,
    get_zip_name,
    print_env_setup_instructions,
    get_changelog_for_version,
    get_ci_job_token,
    is_ci_environment,
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


def create_release(project_id: str, secret_token: str, version: str, download_url: str, package_name: str):
    """Create a GitLab release with the uploaded file."""
    print(f"\nCreating GitLab release for version {version}...")

    api_root = "https://gitlab.com/api/v4"

    # Generate release notes
    release_notes = generate_release_notes(version)

    # Use JOB-TOKEN in CI, PRIVATE-TOKEN otherwise
    if is_ci_environment():
        headers = {
            'JOB-TOKEN': secret_token,
            'Content-Type': 'application/json',
        }
    else:
        headers = {
            'PRIVATE-TOKEN': secret_token,
            'Content-Type': 'application/json',
        }

    release_data = {
        "name": f"Release {version}",
        "tag_name": f"v{version}",
        "description": release_notes,
        "assets": {
            "links": [{
                "name": f"{package_name}-v{version}.zip",
                "url": download_url,
                "link_type": "package"
            }]
        }
    }

    uri = f'{api_root}/projects/{project_id}/releases'

    r_release = requests.post(uri, headers=headers, data=json.dumps(release_data))

    if r_release.status_code in (200, 201):
        release = r_release.json()
        print("✓ Release created successfully!")

        # Get release details
        tag_name = release.get('tag_name', f'v{version}')

        # Fetch project info to get the path_with_namespace
        project_uri = f'{api_root}/projects/{project_id}'
        r_project = requests.get(project_uri, headers={'PRIVATE-TOKEN': secret_token})

        if r_project.status_code == 200:
            project_data = r_project.json()
            path_with_namespace = project_data.get('path_with_namespace', '')
            gitlab_server = "https://gitlab.com"
            web_url = f"{gitlab_server}/{path_with_namespace}/-/releases/{tag_name}"
            print(f"Release page: {web_url}")
        else:
            print(f"Tag: {tag_name}")
            print("View release in GitLab: Navigate to your project → Releases")
    else:
        print(f"Error: Failed to create release (status {r_release.status_code})")
        print(f"Response: {r_release.text}")
        sys.exit(1)


def run(args=None):
    """Main execution function for the upload command."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Upload release zip to GitLab project uploads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sptbuild upload              Upload zip file only
  sptbuild upload --release    Upload zip and create GitLab release
  sptbuild upload -r           Same as --release (short form)
        """
    )
    parser.add_argument(
        '-r', '--release',
        action='store_true',
        help='Create a GitLab release after uploading'
    )

    parsed_args = parser.parse_args(args)

    # Get environment variables
    package_name = get_package_name()
    package_version = get_version()

    # In CI, use CI_JOB_TOKEN directly; otherwise use GITLAB_SECRET_TOKEN
    if is_ci_environment():
        secret_token = get_ci_job_token()
        print("Running in CI mode")
        print(f"Token length: {len(secret_token) if secret_token else 0}")
    else:
        secret_token = get_secret_token()

    project_id = get_project_id()

    # Check for missing variables
    missing = []
    if not package_name:
        print("Error: UPLOAD_PACKAGE_NAME environment variable not set")
        missing.append('UPLOAD_PACKAGE_NAME')
    if not package_version:
        print("Error: VERSION_SOURCE_FILE environment variable not set or version not found")
        missing.append('VERSION_SOURCE_FILE')
    if not secret_token:
        if is_ci_environment():
            print("Error: CI_JOB_TOKEN environment variable not set")
            missing.append('CI_JOB_TOKEN')
        else:
            print("Error: GITLAB_SECRET_TOKEN environment variable not set")
            missing.append('GITLAB_SECRET_TOKEN')
    if not project_id:
        print("Error: GITLAB_PROJECT_ID environment variable not set")
        missing.append('GITLAB_PROJECT_ID')

    if missing:
        print_env_setup_instructions()
        sys.exit(1)

    file_path = get_zip_name()
    if not file_path:
        print("Error: Could not determine zip file name")
        print_env_setup_instructions()
        sys.exit(1)

    file_name = os.path.basename(file_path)

    api_root = "https://gitlab.com/api/v4"
    gitlab_server = "https://gitlab.com"

    # Use JOB-TOKEN in CI, PRIVATE-TOKEN otherwise
    if is_ci_environment():
        headers = {
            'JOB-TOKEN': secret_token,
        }
        print("Using JOB-TOKEN authentication")
    else:
        headers = {
            'PRIVATE-TOKEN': secret_token,
        }
        print("Using PRIVATE-TOKEN authentication")

    # Upload to project uploads endpoint (publicly accessible, not package registry)
    uri = f'{api_root}/projects/{project_id}/uploads'

    print(f"Uploading {file_name} to project uploads...")
    print(f"URI: {uri}")

    with open(file_path, 'rb') as f:
        files = {'file': (file_name, f, 'application/zip')}
        r_upload = requests.post(uri, headers=headers, files=files)

        if r_upload.status_code not in (200, 201):
            print(f"Error: Upload API responded with status {r_upload.status_code}")
            print(f"Response: {r_upload.text}")
            sys.exit(1)

        upload = r_upload.json()

        # Extract the full download URL
        upload_path = upload.get('full_path', upload.get('url', ''))
        full_download_url = f"{gitlab_server}{upload_path}"

        print("✓ Upload successful!")
        print(f"Download URL: {full_download_url}")
        print(f"\nResponse: {upload}")

        # Create release if requested
        if parsed_args.release:
            create_release(project_id, secret_token, package_version, full_download_url, package_name)
