"""Setup CI command - Setup script for creating and uploading GitLab CI NuGet package."""

import os
import sys
import re
import shutil
import subprocess
import argparse
import xml.etree.ElementTree as ET
import requests
import semver
from pathlib import Path
from typing import List, Tuple, Optional

from ..lib import (
    get_secret_token,
    get_project_id,
    get_gitlab_username,
    get_project_name,
    get_nuget_package_name,
    print_env_setup_instructions,
)

# ANSI color codes
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color


def print_color(text: str, color: str = NC):
    """Print colored text."""
    print(f"{color}{text}{NC}")


def solution_references_csproj(sln_path: Path, csproj_path: Path) -> bool:
    """
    Check if a .sln file references the given .csproj file.

    Args:
        sln_path: Path to the .sln file
        csproj_path: Path to the .csproj file

    Returns:
        True if the .sln references the .csproj, False otherwise
    """
    try:
        with open(sln_path, 'r', encoding='utf-8-sig') as f:
            sln_content = f.read()

        # Get the csproj filename
        csproj_name = csproj_path.name

        # Solution files reference projects with lines like:
        # Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "ProjectName", "path\to\project.csproj", "{GUID}"
        # We'll look for the .csproj filename in the solution content

        # Match project lines in the solution file
        # The pattern looks for: Project(...) = "...", "...", "..."
        pattern = r'Project\([^)]+\)\s*=\s*"[^"]*",\s*"([^"]+)"'

        for match in re.finditer(pattern, sln_content):
            project_path = match.group(1)
            # Normalize path separators
            project_path = project_path.replace('\\', os.sep)

            # Check if this project path matches our csproj
            # Could be relative or just the filename
            if csproj_name in project_path:
                # Resolve the path relative to the solution directory
                resolved_project = (sln_path.parent / project_path).resolve()
                if resolved_project == csproj_path.resolve():
                    return True

        return False
    except (IOError, OSError):
        return False


def find_solution_dir(csproj_path: str) -> str:
    """
    Find the directory containing the .sln file for the given .csproj.
    Searches upward from the .csproj directory and verifies the .sln
    actually references the .csproj.

    Args:
        csproj_path: Path to the .csproj file

    Returns:
        Absolute path to the directory containing the .sln file,
        or the .csproj directory if no valid .sln is found
    """
    # Start from the directory containing the .csproj
    csproj_path_obj = Path(csproj_path).resolve()
    current_dir = csproj_path_obj.parent

    # Search upward through parent directories
    max_depth = 5  # Don't search too far up
    for _ in range(max_depth):
        # Look for any .sln file in this directory
        sln_files = list(current_dir.glob('*.sln'))

        for sln_file in sln_files:
            # Check if this .sln references our .csproj
            if solution_references_csproj(sln_file, csproj_path_obj):
                # Found a valid solution file, return this directory with trailing slash
                return str(current_dir) + os.sep

        # Move up to parent directory
        parent = current_dir.parent
        if parent == current_dir:
            # Reached filesystem root
            break
        current_dir = parent

    # No valid .sln found, return the .csproj directory
    return str(csproj_path_obj.parent) + os.sep


def parse_properties(root, csproj_path: str) -> dict:
    """
    Parse all PropertyGroup elements and build a dictionary of properties.
    Handles variable expansion like $(TarkovDir).

    Args:
        root: XML root element of the .csproj
        csproj_path: Path to the .csproj file

    Returns dict of property_name -> expanded_value
    """
    solution_dir = find_solution_dir(csproj_path)
    project_dir = str(Path(csproj_path).resolve().parent)

    properties = {
        # Built-in MSBuild properties
        'SolutionDir': solution_dir,
        'MSBuildProjectDirectory': project_dir,
    }

    # Find all PropertyGroup elements
    for prop_group in root.findall('.//PropertyGroup'):
        for prop in prop_group:
            # Skip if it has a condition (we'll use the default value instead)
            prop_name = prop.tag.split('}')[-1]  # Remove namespace if present
            prop_value = prop.text

            if prop_value:
                properties[prop_name] = prop_value.strip()

    # Expand variables in property values (may need multiple passes)
    max_iterations = 10  # Prevent infinite loops
    for _ in range(max_iterations):
        changed = False
        for key, value in properties.items():
            # Find all $(Variable) patterns
            expanded = re.sub(
                r'\$\(([^)]+)\)',
                lambda m: properties.get(m.group(1), f'$({m.group(1)})'),
                value
            )
            if expanded != value:
                properties[key] = expanded
                changed = True

        if not changed:
            break

    return properties


def expand_path(hint_path: str, properties: dict) -> str:
    """
    Expand MSBuild variables in a path string.

    Args:
        hint_path: Path with potential $(Variable) references
        properties: Dict of property_name -> value

    Returns:
        Expanded path with variables substituted
    """
    expanded = re.sub(
        r'\$\(([^)]+)\)',
        lambda m: properties.get(m.group(1), f'$({m.group(1)})'),
        hint_path
    )
    return expanded


def parse_csproj_references(csproj_path: str) -> List[Tuple[str, str]]:
    """
    Parse .csproj file and extract HintPath references from the <Otherwise> block.

    Returns list of tuples: (reference_name, hint_path)
    """
    print_color(f"Step 1: Parsing {csproj_path} for references", GREEN)

    tree = ET.parse(csproj_path)
    root = tree.getroot()

    # Parse property definitions
    properties = parse_properties(root, csproj_path)

    if properties:
        print(f"  Solution directory: {properties.get('SolutionDir', 'Not found')}")
        print("  Parsed MSBuild properties:")
        for key, value in properties.items():
            if key not in ['MSBuildProjectDirectory', 'SolutionDir']:  # Show custom props only
                print(f"    {key} = {value}")

    references = []

    # Find the <Otherwise> block within <Choose>
    for choose in root.findall('.//Choose'):
        otherwise = choose.find('Otherwise')
        if otherwise is not None:
            # Find all Reference elements with HintPath
            for ref in otherwise.findall('.//Reference'):
                include = ref.get('Include')
                hint_path_elem = ref.find('HintPath')

                if hint_path_elem is not None and hint_path_elem.text:
                    hint_path = hint_path_elem.text.strip()
                    # Expand variables in hint path
                    expanded_path = expand_path(hint_path, properties)
                    references.append((include, expanded_path))
                    print(f"  Found: {include}")
                    if hint_path != expanded_path:
                        print(f"    {hint_path} -> {expanded_path}")
                    else:
                        print(f"    {hint_path}")

    if not references:
        print_color("Error: No references found in <Otherwise> block", RED)
        sys.exit(1)

    print_color(f"✓ Found {len(references)} references\n", GREEN)
    return references


def copy_references(references: List[Tuple[str, str]], refs_dir: Path):
    """Copy referenced DLLs to refs/ directory."""
    print_color("Step 2: Copying reference assemblies", GREEN)

    refs_dir.mkdir(exist_ok=True)

    # Exclude .NET Framework facade assemblies that are already provided by the framework
    excluded_assemblies = {
        'System.Runtime.dll',
        'System.Runtime.InteropServices.dll',
        'System.Collections.dll',
        'System.Linq.dll',
        'System.Threading.dll',
        'System.Threading.Tasks.dll',
        'System.IO.dll',
        'System.Reflection.dll',
        'System.Diagnostics.Debug.dll',
        'mscorlib.dll',
    }

    copied = []
    warnings = []
    skipped = []

    for name, hint_path in references:
        # Convert Windows path separators to OS-appropriate ones
        hint_path = hint_path.replace('\\', os.sep)
        source_path = Path(hint_path)

        # Determine target filename
        target_name = source_path.name

        # Skip .NET Framework facade assemblies
        if target_name in excluded_assemblies:
            skipped.append(target_name)
            print_color(f"  Skipped: {target_name} (framework assembly)", YELLOW)
            continue

        if not source_path.exists():
            msg = f"Warning: {hint_path} not found"
            print_color(f"  {msg}", YELLOW)
            warnings.append(msg)
            continue

        target_path = refs_dir / target_name

        shutil.copy2(source_path, target_path)
        print(f"  Copied: {target_name}")
        copied.append((name, target_name))

    if not copied:
        print_color("Error: No files were copied", RED)
        sys.exit(1)

    if skipped:
        print_color(f"✓ Skipped {len(skipped)} framework assemblies", GREEN)
    print_color(f"✓ Copied {len(copied)} assemblies\n", GREEN)
    return copied


def get_existing_version(package_csproj: Path) -> Optional[str]:
    """Extract existing version from ReferencePackage.csproj if it exists."""
    if not package_csproj.exists():
        return None

    try:
        tree = ET.parse(package_csproj)
        root = tree.getroot()
        version_elem = root.find('.//Version')
        if version_elem is not None and version_elem.text:
            return version_elem.text.strip()
    except Exception:
        pass

    return None


def suggest_version(current_version: Optional[str]) -> str:
    """Suggest a new version based on current version (bumps patch)."""
    if not current_version:
        return "1.0.0"

    try:
        ver = semver.VersionInfo.parse(current_version)
        return str(ver.bump_patch())
    except ValueError:
        # If current version is invalid, suggest 1.0.0
        return "1.0.0"


def ask_for_version(suggested: str) -> str:
    """Ask user for package version, with a suggested default."""
    print_color(f"\nPackage version:", YELLOW)
    print(f"  Suggested: {suggested}")

    while True:
        user_input = input(f"  Enter version (press Enter for {suggested}): ").strip()

        # Use suggested if user just presses Enter
        if not user_input:
            return suggested

        # Validate semver
        try:
            semver.VersionInfo.parse(user_input)
            return user_input
        except ValueError:
            print_color(f"  Error: '{user_input}' is not a valid semantic version (e.g., 1.0.0)", RED)
            print_color(f"  Please use format: MAJOR.MINOR.PATCH", RED)


def update_reference_package(copied_refs: List[Tuple[str, str]], package_csproj: Path, username: str, project_name: str, version: str):
    """Update ReferencePackage.csproj with the collected references."""
    print_color("Step 3: Generating ReferencePackage.csproj", GREEN)

    # Generate package name using common function
    nuget_package_name = get_nuget_package_name(project_name)

    # Create the package project file
    content = f'''<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net472</TargetFramework>
    <PackageId>{nuget_package_name}</PackageId>
    <Version>{version}</Version>
    <Authors>{username}</Authors>
    <Description>Private reference assemblies for {project_name} SPT4 mod development. Contains all SPT, EFT, and Unity assemblies needed for CI builds.</Description>
    <PackageProjectUrl>https://gitlab.com/{username}/{project_name}</PackageProjectUrl>
    <IncludeBuildOutput>false</IncludeBuildOutput>
    <SuppressDependenciesWhenPacking>true</SuppressDependenciesWhenPacking>

    <!-- Disable compilation - this project only packages DLLs, doesn't build code -->
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <EnableDefaultItems>false</EnableDefaultItems>
    <GenerateAssemblyInfo>false</GenerateAssemblyInfo>
  </PropertyGroup>

  <ItemGroup>
'''

    # Add each reference as a Content item
    for ref_name, file_name in copied_refs:
        # Handle special case where Assembly-CSharp comes from hollowed.dll
        if file_name == 'hollowed.dll':
            pack_path = 'lib/net472/Assembly-CSharp.dll'
        else:
            pack_path = f'lib/net472/{file_name}'

        content += f'''    <Content Include="refs/{file_name}">
      <Pack>true</Pack>
      <PackagePath>{pack_path}</PackagePath>
    </Content>
'''

    content += '''  </ItemGroup>

</Project>
'''

    package_csproj.write_text(content)
    print_color("✓ ReferencePackage.csproj updated\n", GREEN)


def create_nuget_package() -> str:
    """Create NuGet package using dotnet pack."""
    print_color("Step 4: Creating NuGet package", GREEN)

    result = subprocess.run(
        ['dotnet', 'pack', 'ReferencePackage.csproj', '--configuration', 'Release', '--output', '.'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print_color("Error: dotnet pack failed", RED)
        print(result.stderr)
        sys.exit(1)

    # Find the created package - use glob pattern matching package name
    project_name = get_project_name()
    if not project_name:
        print_color("Error: GITLAB_PROJECT_NAME not set", RED)
        sys.exit(1)

    # Use common function to generate package name
    nuget_package_name = get_nuget_package_name(project_name)
    package_files = list(Path('.').glob(f'{nuget_package_name}.*.nupkg'))
    if not package_files:
        print_color("Error: Package file not created", RED)
        sys.exit(1)

    package_file = str(package_files[0])
    print_color(f"✓ Package created: {package_file}\n", GREEN)
    return package_file


def check_nuget_config():
    """Verify nuget.config exists and uses environment variable interpolation. Create if missing."""
    print_color("Step 5: Checking nuget.config", GREEN)

    nuget_config_path = Path('nuget.config')

    if not nuget_config_path.exists():
        print_color("  nuget.config not found, creating default configuration...", YELLOW)

        # Create default nuget.config with environment variable interpolation
        # %CI_PROJECT_ID% will be expanded by NuGet from the CI_PROJECT_ID env var
        default_config = '''<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <!-- Public NuGet.org feed -->
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" protocolVersion="3" />

    <!-- GitLab private package registry -->
    <!-- Uses %CI_PROJECT_ID% environment variable (provided by GitLab CI) -->
    <add key="GitLab" value="https://gitlab.com/api/v4/projects/%CI_PROJECT_ID%/packages/nuget/index.json" />
    <add key="gitlab-upload" value="https://gitlab.com/api/v4/projects/%CI_PROJECT_ID%/packages/nuget/index.json" />
  </packageSources>

  <packageSourceCredentials>
    <GitLab>
      <!-- CI uses CI_JOB_TOKEN automatically, local dev would need personal access token -->
      <add key="Username" value="gitlab-ci-token" />
      <add key="ClearTextPassword" value="%CI_JOB_TOKEN%" />
    </GitLab>
  </packageSourceCredentials>
</configuration>
'''
        nuget_config_path.write_text(default_config)
        print_color("  ✓ Created nuget.config with GitLab CI integration", GREEN)
    else:
        content = nuget_config_path.read_text()
        if '%CI_PROJECT_ID%' not in content:
            print_color("  Warning: nuget.config doesn't contain %CI_PROJECT_ID% variable", YELLOW)
            print_color("  CI builds use NuGet's variable interpolation for this", YELLOW)
        else:
            print_color("  ✓ nuget.config exists and looks good", GREEN)

    print_color("✓ nuget.config verified\n", GREEN)


def upload_package(package_file: str, project_id: str, token: str):
    """Upload package to GitLab Package Registry using dotnet nuget push."""
    print_color("Step 6: Uploading package to GitLab", GREEN)

    api_root = "https://gitlab.com/api/v4"
    source_url = f'{api_root}/projects/{project_id}/packages/nuget/index.json'
    source_name = 'gitlab-upload'

    # Add the NuGet source with credentials
    print("  Configuring NuGet source...")
    result = subprocess.run(
        [
            'dotnet', 'nuget', 'add', 'source', source_url,
            '--name', source_name,
            '--username', 'api',
            '--password', token,
            '--store-password-in-clear-text'
        ],
        capture_output=True,
        text=True
    )

    # Source might already exist, which is fine
    if result.returncode != 0 and 'already exists' not in result.stderr:
        print_color(f"Warning: Could not add NuGet source: {result.stderr}", YELLOW)
        # Try to update the source instead
        subprocess.run(
            [
                'dotnet', 'nuget', 'update', 'source', source_name,
                '--username', 'api',
                '--password', token,
                '--store-password-in-clear-text'
            ],
            capture_output=True,
            text=True
        )

    # Push the package with API key
    print("  Pushing package...")
    result = subprocess.run(
        [
            'dotnet', 'nuget', 'push', package_file,
            '--source', source_name,
            '--api-key', token
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print_color("Error: Package push failed", RED)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)

    print_color("\n✓ Package uploaded successfully!\n", GREEN)
    if result.stdout:
        print(result.stdout)


def update_gitignore():
    """Add refs/ and *.nupkg to .gitignore if not already present."""
    gitignore_path = Path('.gitignore')

    lines = []
    if gitignore_path.exists():
        lines = gitignore_path.read_text().splitlines()

    modified = False

    if 'refs/' not in lines:
        lines.append('refs/')
        modified = True
        print_color("✓ Added refs/ to .gitignore", GREEN)

    if '*.nupkg' not in lines:
        lines.append('*.nupkg')
        modified = True
        print_color("✓ Added *.nupkg to .gitignore", GREEN)

    if modified:
        gitignore_path.write_text('\n'.join(lines) + '\n')
        print()


def update_csproj_version(csproj_path: str, new_version: str):
    """Update the PackageReference version in csproj for any *.SPT.References package."""
    print_color(f"Updating {csproj_path} to reference version {new_version}", GREEN)

    # Read the file as text to preserve formatting
    with open(csproj_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Use regex to find and replace any package matching *.SPT.References
    pattern = r'(<PackageReference\s+Include="[^"]*\.SPT\.References"\s+Version=")([^"]+)("\s*/?>)'

    def replace_version(match):
        return f'{match.group(1)}{new_version}{match.group(3)}'

    new_content, count = re.subn(pattern, replace_version, content)

    if count == 0:
        print_color("Warning: Could not find *.SPT.References PackageReference to update", YELLOW)
        return False

    # Write back to file
    with open(csproj_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print_color(f"✓ Updated PackageReference version to {new_version}\n", GREEN)
    return True


def run(args=None):
    """Main execution function for the setup-ci command."""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description="Build NuGet package with SPT/EFT reference assemblies",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  sptbuild setup-ci myproject.csproj              Build package only
  sptbuild setup-ci myproject.csproj --upload     Build and upload to GitLab Package Registry
  sptbuild setup-ci myproject.csproj -u           Same as --upload (short form)
  sptbuild setup-ci myproject.csproj -u -m        Upload and update csproj with new version
            """
        )
        parser.add_argument(
            'csproj',
            help='Path to the .csproj file'
        )
        parser.add_argument(
            '-u', '--upload',
            action='store_true',
            help='Upload package to GitLab after building (requires env vars)'
        )
        parser.add_argument(
            '-m', '--modify',
            action='store_true',
            help='Update the .csproj with the new package version'
        )

        parsed_args = parser.parse_args(args)

        print_color("=== SPT Build CI Package Setup ===\n", GREEN)

        # Export GITLAB_PROJECT_ID as CI_PROJECT_ID for local environments
        # This allows nuget.config to use %CI_PROJECT_ID% variable interpolation
        # both locally and in CI (where CI_PROJECT_ID is already set)
        if 'CI_PROJECT_ID' not in os.environ:
            gitlab_project_id = get_project_id()
            if gitlab_project_id:
                os.environ['CI_PROJECT_ID'] = gitlab_project_id
                print_color(f"Setting CI_PROJECT_ID={gitlab_project_id} for NuGet config\n", GREEN)

        # Get username and project name (needed for package metadata)
        username = get_gitlab_username()
        project_name = get_project_name()

        # Check for missing variables
        missing = []
        if not username:
            print_color("Error: GITLAB_USERNAME environment variable not set", RED)
            missing.append('GITLAB_USERNAME')
        if not project_name:
            print_color("Error: GITLAB_PROJECT_NAME environment variable not set", RED)
            missing.append('GITLAB_PROJECT_NAME')

        # Only check upload-specific environment variables if uploading
        if parsed_args.upload:
            project_id = get_project_id()
            token = get_secret_token()

            if not project_id:
                print_color("Error: GITLAB_PROJECT_ID environment variable not set", RED)
                missing.append('GITLAB_PROJECT_ID')
            if not token:
                print_color("Error: GITLAB_SECRET_TOKEN environment variable not set", RED)
                missing.append('GITLAB_SECRET_TOKEN')

        if missing:
            print_color("This is needed for package metadata and URLs", YELLOW)
            print_env_setup_instructions()
            sys.exit(1)

        print(f"Using GitLab Username: {username}")
        print(f"Using GitLab Project Name: {project_name}")
        if parsed_args.upload:
            print(f"Using GitLab Project ID: {project_id}")
        print()

        # Verify csproj file exists
        csproj_path = parsed_args.csproj
        if not os.path.exists(csproj_path):
            print_color(f"Error: .csproj file not found: {csproj_path}", RED)
            sys.exit(1)

        print(f"Using .csproj file: {csproj_path}\n")

        # Parse .csproj for references
        references = parse_csproj_references(csproj_path)

        # Copy DLLs to refs/
        refs_dir = Path('refs')
        copied_refs = copy_references(references, refs_dir)

        # Ask for version
        package_csproj_path = Path('ReferencePackage.csproj')
        existing_version = get_existing_version(package_csproj_path)
        suggested_version = suggest_version(existing_version)

        if existing_version:
            print(f"Current version: {existing_version}")

        version = ask_for_version(suggested_version)
        print_color(f"✓ Using version: {version}\n", GREEN)

        # Generate ReferencePackage.csproj
        update_reference_package(copied_refs, package_csproj_path, username, project_name, version)

        # Create NuGet package
        package_file = create_nuget_package()

        # Check nuget.config exists
        check_nuget_config()

        # Update .gitignore
        update_gitignore()

        # Update csproj if requested
        csproj_modified = False
        if parsed_args.modify:
            csproj_modified = update_csproj_version(csproj_path, version)

        # Upload if requested
        if parsed_args.upload:
            upload_package(package_file, project_id, token)
            print_color("=== Setup Complete ===\n", GREEN)
            print("Next steps:")
            print("  1. Verify package in GitLab: Deploy → Package Registry")
            if not csproj_modified:
                print(f"  2. Update {csproj_path} to reference the new version:")
                print(f"     <PackageReference Include=\"*.SPT.References\" Version=\"{version}\" />")
                print("  3. Commit the changes:")
            else:
                print("  2. Commit the changes:")
            print(f"     git add {csproj_path} ReferencePackage.csproj")
            print(f"     git commit -m 'Update reference package to v{version}'")
            print("     git push")
        else:
            print_color("=== Package Built ===\n", GREEN)
            print(f"Package created: {package_file}")
            if csproj_modified:
                print(f"✓ {csproj_path} updated with new version")
            print()
            print("To upload to GitLab, run:")
            print_color(f"  sptbuild setup-ci {csproj_path} --upload", YELLOW)
            if not csproj_modified:
                print(f"\nTo update {csproj_path} with the new version, add -m flag:")
                print_color(f"  sptbuild setup-ci {csproj_path} -m", YELLOW)

    except KeyboardInterrupt:
        print_color("\n\nAborted by user", YELLOW)
        sys.exit(1)
    except Exception as e:
        print_color(f"\n\nUnexpected error: {e}", RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
