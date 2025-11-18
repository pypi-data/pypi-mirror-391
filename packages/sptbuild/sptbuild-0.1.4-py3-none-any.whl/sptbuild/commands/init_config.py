"""Init-config command - Generate example plugin.toml configuration file."""

import os
import sys


EXAMPLE_PLUGIN_TOML = """# Plugin bundling configuration for sptbuild
# This file tells sptbuild which additional files/directories to bundle
# alongside your plugin DLL in the final zip package.

# All bundled files will be placed in: BepInEx/plugins/{PackageName}/

[bundle]

# Individual files to include (relative to project root)
# These will maintain their directory structure in the plugin folder
files = [
    "README.md",
    # "LICENSE.txt",
    # "config/settings.json",
]

# Directories to include recursively (relative to project root)
# All files within these directories will be copied
directories = [
    # "assets",
    # "localization",
]

# Optional: Custom file mappings for renaming or restructuring files
# Uncomment and modify as needed:

# [[bundle.custom]]
# source = "docs/UserGuide.md"
# destination = "GUIDE.md"  # Renamed in the zip
#
# [[bundle.custom]]
# source = "configs/default.json"
# destination = "config/default.json"  # Placed in subfolder

# Example resulting zip structure:
# BepInEx/
#   plugins/
#     MyPlugin/
#       MyPlugin.dll          (your compiled plugin)
#       README.md             (from files list)
#       assets/               (from directories list)
#         icon.png
#         banner.png
"""


def run(args=None):
    """Generate example plugin.toml file."""
    force = args and '--force' in args
    output = None

    # Parse output argument if present
    if args:
        for i, arg in enumerate(args):
            if arg == '--output' and i + 1 < len(args):
                output = args[i + 1]
                break

    # Default to plugin.toml if no output specified
    if output is None:
        output = "plugin.toml"

    # Special case: stdout
    if output == '-':
        sys.stdout.write(EXAMPLE_PLUGIN_TOML)
        return

    # Check if file already exists
    if os.path.exists(output) and not force:
        print(f"Error: {output} already exists", file=sys.stderr)
        print(f"Use 'sptbuild init-config --force' to overwrite", file=sys.stderr)
        sys.exit(1)

    # Write the example file
    try:
        with open(output, 'w') as f:
            f.write(EXAMPLE_PLUGIN_TOML)

        if force and os.path.exists(output):
            print(f"Overwritten: {output}")
        else:
            print(f"Created: {output}")

        print("\nEdit this file to specify which files/directories to bundle with your plugin.")
        print("For more information, see: https://gitlab.com/flir063-spt/sptbuild")

    except Exception as e:
        print(f"Error: Could not create {output}", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
