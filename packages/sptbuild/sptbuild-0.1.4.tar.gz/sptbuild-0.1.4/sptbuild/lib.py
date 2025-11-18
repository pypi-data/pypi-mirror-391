"""Shared utility functions for sptbuild."""

import os
import sys
import re
from typing import Optional, TextIO

version_pattern = r'public const string Version = "(\d\.\d\.\d)";'
re_version_pattern = re.compile(version_pattern)


def print_env_setup_instructions() -> None:
    """Print instructions for setting up environment variables."""
    print()
    print("Please set the required environment variables:")
    print()
    print("1. Get your GitLab Project ID:")
    print("   - Go to your GitLab project page")
    print("   - Look under the project name for 'Project ID: XXXXX'")
    print()
    print("2. Create a Personal Access Token:")
    print("   - GitLab → Settings → Access Tokens")
    print("   - Create token with 'api' scope")
    print()
    print("3. Export the variables:")
    print("   export GITLAB_PROJECT_ID=your_project_id")
    print("   export GITLAB_SECRET_TOKEN=your_personal_access_token")
    print("   export GITLAB_USERNAME=your_gitlab_username")
    print("   export GITLAB_PROJECT_NAME=your_project_name")
    print()
    print("For package and upload commands, also set:")
    print("   export UPLOAD_PACKAGE_NAME=your_package_name")
    print("   export VERSION_SOURCE_FILE=path/to/version/file")
    print()


def get_secret_token() -> Optional[str]:
    """Get GitLab secret token from environment. Returns None if not set."""
    return os.environ.get("GITLAB_SECRET_TOKEN", None)


def get_project_id() -> Optional[str]:
    """Get GitLab project ID from environment. Returns None if not set."""
    # In CI, use CI_PROJECT_ID; otherwise use GITLAB_PROJECT_ID
    return os.environ.get("GITLAB_PROJECT_ID") or os.environ.get("CI_PROJECT_ID")


def get_gitlab_username() -> Optional[str]:
    """Get GitLab username from environment. Returns None if not set."""
    return os.environ.get("GITLAB_USERNAME", None)


def get_project_name() -> Optional[str]:
    """Get GitLab project name from environment. Returns None if not set."""
    return os.environ.get("GITLAB_PROJECT_NAME", None)


def get_ci_job_token() -> Optional[str]:
    """Get CI job token from environment. Returns None if not set."""
    return os.environ.get("CI_JOB_TOKEN", None)


def get_ci_api_url() -> Optional[str]:
    """Get CI API URL from environment. Returns None if not set."""
    return os.environ.get("CI_API_V4_URL", None)


def is_ci_environment() -> bool:
    """Check if running in CI environment."""
    return get_ci_job_token() is not None


def get_package_name() -> Optional[str]:
    """Get package name from environment. Returns None if not set."""
    return os.environ.get("UPLOAD_PACKAGE_NAME", None)


def version_line(fp: TextIO) -> Optional[str]:
    """Find and return the line containing version string. Returns None if not found."""
    for line in fp:
        if "public const string Version" in line.strip():
            return line
    return None


def get_version_file() -> Optional[str]:
    """Get version source file from environment. Returns None if not set."""
    return os.environ.get("VERSION_SOURCE_FILE", None)


def get_version() -> Optional[str]:
    """Get version from version file. Returns None if version file not set or not found."""
    version_file = get_version_file()
    if not version_file:
        return None
    try:
        with open(version_file, "r") as plugin:
            vl = version_line(plugin)
            if vl:
                match = re_version_pattern.search(vl)
                if match:
                    return match.group(1)
    except (FileNotFoundError, IOError):
        return None
    return None


def get_changelog_for_version(version: str, changelog_path: str = "CHANGELOG.md") -> Optional[str]:
    """
    Extract release notes for a specific version from CHANGELOG.md.

    Args:
        version: Version string (e.g., "1.1.2")
        changelog_path: Path to CHANGELOG.md file

    Returns:
        Release notes for the version, or None if not found
    """
    try:
        with open(changelog_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find the line with the version header
        # Format: ## [version] - date
        version_header = f"## [{version}]"
        start_idx = None

        for idx, line in enumerate(lines):
            if line.strip().startswith(version_header):
                start_idx = idx
                break

        if start_idx is None:
            return None

        # Extract content until the next ## header or end of file
        content_lines = []
        for idx in range(start_idx + 1, len(lines)):
            line = lines[idx]
            # Stop at next version header
            if line.strip().startswith("## ["):
                break
            content_lines.append(line)

        # Join and strip whitespace
        content = "".join(content_lines).strip()

        if not content:
            return None

        return content

    except (FileNotFoundError, IOError) as e:
        print(f"Error reading changelog: {e}")
        return None


def upload_dirname() -> str:
    """Get the upload directory path."""
    return os.path.join("bin", "upload")


def get_nuget_package_name(base_name: str) -> str:
    """
    Generate standardized NuGet package name for SPT references.

    Args:
        base_name: Base project/package name

    Returns:
        Formatted NuGet package name: {base_name}.SPT.References
    """
    return f"{base_name}.SPT.References"


def get_zip_name() -> Optional[str]:
    """Get zip file name. Returns None if version or package name not available."""
    version = get_version()
    package_name = get_package_name()

    if not version or not package_name:
        return None

    return os.path.join(
        upload_dirname(),
        package_name+"-v"+version+".zip",
    )
