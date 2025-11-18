"""Plugin configuration handling for plugin.toml."""

import os
import sys
from typing import Optional, Dict, List, Any

# Use tomllib for Python 3.11+ or tomli for earlier versions
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


class PluginConfig:
    """Handles reading and parsing plugin.toml configuration."""

    def __init__(self, config_path: str = "plugin.toml"):
        """
        Initialize plugin configuration.

        Args:
            config_path: Path to the plugin.toml file
        """
        self.config_path = config_path
        self.config: Optional[Dict[str, Any]] = None
        self._load_config()

    def _load_config(self):
        """Load and parse the plugin.toml file if it exists."""
        if not os.path.exists(self.config_path):
            # plugin.toml is optional
            self.config = None
            return

        try:
            with open(self.config_path, "rb") as f:
                self.config = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            print(f"Error: Invalid TOML syntax in {self.config_path}")
            print(f"Details: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: Could not read {self.config_path}")
            print(f"Details: {e}")
            sys.exit(1)

    def has_config(self) -> bool:
        """Check if a plugin.toml configuration exists."""
        return self.config is not None

    def get_files(self) -> List[str]:
        """
        Get the list of files to bundle.

        Returns:
            List of file paths relative to project root
        """
        if not self.config:
            return []

        bundle = self.config.get("bundle", {})
        files = bundle.get("files", [])

        if not isinstance(files, list):
            print("Error: 'bundle.files' must be a list")
            sys.exit(1)

        return files

    def get_directories(self) -> List[str]:
        """
        Get the list of directories to bundle.

        Returns:
            List of directory paths relative to project root
        """
        if not self.config:
            return []

        bundle = self.config.get("bundle", {})
        directories = bundle.get("directories", [])

        if not isinstance(directories, list):
            print("Error: 'bundle.directories' must be a list")
            sys.exit(1)

        return directories

    def get_custom_mappings(self) -> List[Dict[str, str]]:
        """
        Get custom file mappings (source -> destination).

        Returns:
            List of dicts with 'source' and 'destination' keys
        """
        if not self.config:
            return []

        bundle = self.config.get("bundle", {})
        custom = bundle.get("custom", [])

        if not isinstance(custom, list):
            print("Error: 'bundle.custom' must be a list")
            sys.exit(1)

        # Validate each custom mapping
        for idx, mapping in enumerate(custom):
            if not isinstance(mapping, dict):
                print(f"Error: bundle.custom[{idx}] must be a table/dict")
                sys.exit(1)
            if "source" not in mapping:
                print(f"Error: bundle.custom[{idx}] missing required 'source' field")
                sys.exit(1)
            if "destination" not in mapping:
                print(f"Error: bundle.custom[{idx}] missing required 'destination' field")
                sys.exit(1)

        return custom

    def get_package_name_override(self) -> Optional[str]:
        """
        Get package name override if specified.

        Returns:
            Package name or None if not overridden
        """
        if not self.config:
            return None

        package = self.config.get("package", {})
        return package.get("name")
