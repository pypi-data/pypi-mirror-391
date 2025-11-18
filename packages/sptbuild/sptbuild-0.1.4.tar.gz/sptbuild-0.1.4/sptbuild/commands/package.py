"""Package command - Creates a zip package for SPT plugin."""

import os
import shutil
import zipfile
import sys
from pathlib import Path

from ..lib import (
    get_package_name,
    get_version,
    upload_dirname,
    get_zip_name,
    print_env_setup_instructions,
)
from ..plugin_config import PluginConfig
from ..bundler import FileBundler


def zip_root_dirname() -> str:
    """Get the zip build root directory."""
    return "bin/zipbuild"


def package_zip_root() -> str:
    """Get the package zip root directory."""
    return os.path.join(zip_root_dirname(), "BepInEx")


def full_zip_dirname() -> str:
    """Get the full path to the plugin directory in the zip."""
    return os.path.join(package_zip_root(), "plugins", get_package_name())


def dll_name() -> str:
    """Get the DLL name based on package name."""
    return get_package_name()+".dll"


def prepare_zip_dir():
    """Create the zip directory structure."""
    os.makedirs(
        full_zip_dirname(),
        exist_ok=True
    )


def zip_directory(directory_path, zip_path):
    """
    Create a zip file from a directory.

    Args:
        directory_path: Path to the directory to zip
        zip_path: Path to the output zip file
    """
    # Create a new zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the directory
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                # Create the full file path
                file_path = os.path.join(root, file)
                # Calculate the relative path for the zip
                rel_path = os.path.relpath(file_path, os.path.dirname(directory_path))
                # Add file to the zip
                zipf.write(file_path, rel_path)


def copy_files_to_zipdir():
    """Copy DLL files and additional bundled files to the zip directory."""
    # First, prepare the directory structure
    prepare_zip_dir()

    # Copy the main DLL
    source = os.path.join("bin", "Release", "net472", dll_name())

    if not os.path.exists(source):
        print(f"Error: Source file not found: {source}")
        print("Did you run 'dotnet build --configuration Release' first?")
        sys.exit(1)

    dest = os.path.join(full_zip_dirname(), dll_name())
    shutil.copy(source, dest)
    print(f"Copied DLL: {dll_name()}")

    # Load plugin configuration and bundle additional files
    config = PluginConfig()
    if config.has_config():
        bundler = FileBundler(full_zip_dirname())
        bundler.bundle_from_config(config)
    else:
        print("No plugin.toml found - bundling DLL only")


def delete_file(file_path):
    """Delete a file with error handling."""
    try:
        os.remove(file_path)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied to delete '{file_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Could not delete '{file_path}' - {e}")
        sys.exit(1)


def remove_dir(dir_path):
    """Remove a directory with error handling."""
    try:
        shutil.rmtree(dir_path)
    except FileNotFoundError:
        print(f"Error: Directory '{dir_path}' not found")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied to remove '{dir_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Could not remove '{dir_path}' - {e}")
        sys.exit(1)


def create_zip():
    """Create the zip file from the prepared directory."""
    zip_name = get_zip_name()

    # first delete any existing file of the same name
    if os.path.exists(zip_name):
        delete_file(zip_name)

    # ensure dest dir
    os.makedirs(upload_dirname(), exist_ok=True)

    # touch the target file
    Path(os.path.join(zip_name)).touch(mode=0o600)

    # then create the zip file
    zip_directory(package_zip_root(), zip_name)


def run():
    """Main execution function for the package command."""
    # Validate environment variables
    package_name = get_package_name()
    version = get_version()

    missing = []
    if not package_name:
        print("Error: UPLOAD_PACKAGE_NAME environment variable not set")
        missing.append('UPLOAD_PACKAGE_NAME')
    if not version:
        print("Error: VERSION_SOURCE_FILE environment variable not set or version not found")
        missing.append('VERSION_SOURCE_FILE')

    if missing:
        print_env_setup_instructions()
        sys.exit(1)

    # first remove zipdir
    full_zip_dir = full_zip_dirname()
    if os.path.exists(full_zip_dir):
        remove_dir(full_zip_dir)

    # then create the dir
    copy_files_to_zipdir()

    # then zip
    create_zip()

    zip_name = get_zip_name()
    print(f"zip created: '{zip_name}'")
