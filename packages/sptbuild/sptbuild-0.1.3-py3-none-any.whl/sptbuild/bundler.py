"""File bundling logic for plugin packages."""

import os
import shutil
import sys
from typing import Optional
from pathlib import Path

from .plugin_config import PluginConfig


class FileBundler:
    """Handles copying files and directories to the zip build directory."""

    def __init__(self, dest_root: str):
        """
        Initialize the file bundler.

        Args:
            dest_root: Root destination directory (e.g., bin/zipbuild/BepInEx/plugins/PluginName)
        """
        self.dest_root = dest_root

    def _validate_source_exists(self, source: str) -> None:
        """
        Validate that a source file or directory exists.

        Args:
            source: Path to validate

        Raises:
            SystemExit if source doesn't exist
        """
        if not os.path.exists(source):
            print(f"Error: Source path not found: {source}")
            print("All files and directories specified in plugin.toml must exist.")
            sys.exit(1)

    def _copy_file(self, source: str, dest: str) -> None:
        """
        Copy a single file to destination, creating directories as needed.

        Args:
            source: Source file path
            dest: Destination file path
        """
        # Ensure destination directory exists
        dest_dir = os.path.dirname(dest)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)

        # Copy the file
        shutil.copy2(source, dest)
        print(f"  Bundled: {source} -> {os.path.relpath(dest, self.dest_root)}")

    def _copy_directory(self, source: str, dest: str) -> None:
        """
        Copy an entire directory recursively to destination.

        Args:
            source: Source directory path
            dest: Destination directory path
        """
        # Walk through source directory
        for root, dirs, files in os.walk(source):
            # Calculate relative path from source
            rel_path = os.path.relpath(root, source)

            # Calculate destination path
            if rel_path == ".":
                dest_path = dest
            else:
                dest_path = os.path.join(dest, rel_path)

            # Create destination directory
            os.makedirs(dest_path, exist_ok=True)

            # Copy all files in this directory
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_path, file)
                shutil.copy2(src_file, dst_file)

        print(f"  Bundled: {source}/ -> {os.path.relpath(dest, self.dest_root)}/")

    def bundle_file(self, source: str, relative_dest: Optional[str] = None) -> None:
        """
        Bundle a single file.

        Args:
            source: Source file path (relative to project root)
            relative_dest: Optional destination path relative to dest_root.
                          If None, maintains source's relative path.
        """
        self._validate_source_exists(source)

        if not os.path.isfile(source):
            print(f"Error: {source} is not a file")
            sys.exit(1)

        # Determine destination
        if relative_dest:
            dest = os.path.join(self.dest_root, relative_dest)
        else:
            dest = os.path.join(self.dest_root, source)

        self._copy_file(source, dest)

    def bundle_directory(self, source: str, relative_dest: Optional[str] = None) -> None:
        """
        Bundle an entire directory recursively.

        Args:
            source: Source directory path (relative to project root)
            relative_dest: Optional destination path relative to dest_root.
                          If None, maintains source's relative path.
        """
        self._validate_source_exists(source)

        if not os.path.isdir(source):
            print(f"Error: {source} is not a directory")
            sys.exit(1)

        # Determine destination
        if relative_dest:
            dest = os.path.join(self.dest_root, relative_dest)
        else:
            dest = os.path.join(self.dest_root, source)

        self._copy_directory(source, dest)

    def bundle_from_config(self, config: PluginConfig) -> None:
        """
        Bundle all files and directories from plugin configuration.

        Args:
            config: PluginConfig instance
        """
        if not config.has_config():
            # No plugin.toml, nothing to bundle
            return

        print("Bundling additional files from plugin.toml:")

        # Bundle individual files
        for file_path in config.get_files():
            self.bundle_file(file_path)

        # Bundle directories
        for dir_path in config.get_directories():
            self.bundle_directory(dir_path)

        # Bundle custom mappings
        for mapping in config.get_custom_mappings():
            source = mapping["source"]
            destination = mapping["destination"]

            self._validate_source_exists(source)

            if os.path.isfile(source):
                self.bundle_file(source, destination)
            elif os.path.isdir(source):
                self.bundle_directory(source, destination)
            else:
                print(f"Error: {source} is neither a file nor directory")
                sys.exit(1)
