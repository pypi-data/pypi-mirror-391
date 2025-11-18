"""Init csproj command - Convert existing .csproj to CI-compatible format."""

import os
import sys
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

from ..lib import get_nuget_package_name

# ANSI color codes
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color


def print_color(text: str, color: str = NC):
    """Print colored text."""
    print(f"{color}{text}{NC}")


def is_system_reference(include: str) -> bool:
    """Check if a reference is a standard .NET system assembly."""
    system_refs = {
        'System', 'System.Core', 'System.Xml.Linq',
        'System.Data.DataSetExtensions', 'Microsoft.CSharp',
        'System.Data', 'System.Net.Http', 'System.Xml',
        'System.Drawing', 'System.Windows.Forms'
    }
    return include in system_refs


def extract_references(csproj_path: Path) -> Tuple[List[ET.Element], List[ET.Element]]:
    """
    Extract references from a .csproj file.

    Returns:
        Tuple of (system_references, spt_references)
    """
    try:
        tree = ET.parse(csproj_path)
        root = tree.getroot()

        system_refs = []
        spt_refs = []

        # Find all Reference elements
        for ref in root.findall('.//Reference'):
            include = ref.get('Include')
            if include:
                if is_system_reference(include):
                    system_refs.append(ref)
                else:
                    spt_refs.append(ref)

        return system_refs, spt_refs

    except ET.ParseError as e:
        print_color(f"Error parsing .csproj file: {e}", RED)
        sys.exit(1)
    except Exception as e:
        print_color(f"Error reading .csproj file: {e}", RED)
        sys.exit(1)


def has_choose_block(csproj_path: Path) -> bool:
    """Check if the .csproj already has a Choose block."""
    try:
        tree = ET.parse(csproj_path)
        root = tree.getroot()
        return root.find('.//Choose') is not None
    except Exception:
        return False


def backup_csproj(csproj_path: Path) -> Path:
    """Create a backup of the original .csproj file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = csproj_path.with_suffix(f'.csproj.backup.{timestamp}')

    with open(csproj_path, 'r', encoding='utf-8') as src:
        content = src.read()

    with open(backup_path, 'w', encoding='utf-8') as dst:
        dst.write(content)

    return backup_path


def get_package_name(csproj_path: Path) -> str:
    """Extract or infer the package name for the NuGet reference."""
    try:
        tree = ET.parse(csproj_path)
        root = tree.getroot()

        # Try to find PackageId or AssemblyName
        for prop in ['PackageId', 'AssemblyName', 'RootNamespace']:
            elem = root.find(f'.//PropertyGroup/{prop}')
            if elem is not None and elem.text:
                return elem.text

        # Fallback to filename without extension
        return csproj_path.stem

    except Exception:
        return csproj_path.stem


def convert_csproj(csproj_path: Path, package_version: str = "1.0.0", force: bool = False) -> None:
    """
    Convert a .csproj file to the CI-compatible format.

    Args:
        csproj_path: Path to the .csproj file
        package_version: Version of the NuGet package to reference
        force: Force conversion even if Choose block exists
    """
    if not csproj_path.exists():
        print_color(f"Error: {csproj_path} not found", RED)
        sys.exit(1)

    # Check if already converted
    if has_choose_block(csproj_path) and not force:
        print_color("This .csproj file already has a <Choose> block.", YELLOW)
        print_color("Use --force to convert anyway.", YELLOW)
        sys.exit(0)

    # Backup original file
    print(f"Backing up original .csproj...")
    backup_path = backup_csproj(csproj_path)
    print_color(f"✓ Backup created: {backup_path}", GREEN)

    # Extract references
    print("\nAnalyzing references...")
    system_refs, spt_refs = extract_references(csproj_path)

    if not spt_refs:
        print_color("Warning: No SPT/game references found to convert.", YELLOW)
        print_color("This project may not need CI conversion.", YELLOW)
        if not force:
            sys.exit(0)

    print(f"  Found {len(system_refs)} system references")
    print(f"  Found {len(spt_refs)} SPT/game references")

    # Parse the .csproj
    tree = ET.parse(csproj_path)
    root = tree.getroot()

    # Get package name
    package_name = get_package_name(csproj_path)
    nuget_package_name = get_nuget_package_name(package_name)

    print(f"\nNuGet package name: {nuget_package_name}")

    # Remove existing reference ItemGroups
    for item_group in root.findall('.//ItemGroup'):
        # Remove if it contains any Reference elements
        if item_group.find('.//Reference') is not None:
            root.remove(item_group)

    # Create system references ItemGroup (outside Choose)
    if system_refs:
        system_group = ET.SubElement(root, 'ItemGroup')
        comment = ET.Comment(' Standard .NET references (both local and CI) ')
        system_group.append(comment)

        for ref in system_refs:
            new_ref = ET.SubElement(system_group, 'Reference')
            new_ref.set('Include', ref.get('Include'))

    # Create Choose block
    choose = ET.SubElement(root, 'Choose')
    choose.append(ET.Comment(' CI Build: Use private NuGet package '))

    # When condition (CI build)
    when = ET.SubElement(choose, 'When')
    when.set('Condition', "'$(CI)' == 'true'")
    when_group = ET.SubElement(when, 'ItemGroup')

    package_ref = ET.SubElement(when_group, 'PackageReference')
    package_ref.set('Include', nuget_package_name)
    package_ref.set('Version', package_version)

    # Otherwise condition (local build)
    choose.append(ET.Comment(' Local Build: Use file references from SPT installation '))
    otherwise = ET.SubElement(choose, 'Otherwise')
    otherwise_group = ET.SubElement(otherwise, 'ItemGroup')

    for ref in spt_refs:
        # Clone the reference element
        new_ref = ET.SubElement(otherwise_group, 'Reference')
        new_ref.set('Include', ref.get('Include'))

        # Copy child elements (HintPath, etc.)
        for child in ref:
            new_child = ET.SubElement(new_ref, child.tag)
            new_child.text = child.text
            for attr_name, attr_value in child.attrib.items():
                new_child.set(attr_name, attr_value)

    # Write the modified .csproj
    print("\nWriting updated .csproj...")

    # Format the XML nicely
    indent_xml(root)

    tree.write(csproj_path, encoding='utf-8', xml_declaration=True)

    print_color(f"✓ Conversion complete!", GREEN)
    print(f"\nNext steps:")
    print(f"1. Create the NuGet reference package:")
    print(f"   sptbuild setup-ci {csproj_path.name} --upload")
    print(f"2. Test local build:")
    print(f"   dotnet build {csproj_path.name}")
    print(f"3. Commit the updated .csproj to your repository")


def indent_xml(elem, level=0):
    """Add indentation to XML for pretty printing."""
    indent = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent


def run(argv=None):
    """Run the init-csproj command with arguments."""
    parser = argparse.ArgumentParser(
        description='Convert .csproj to CI-compatible format with Choose block'
    )
    parser.add_argument('csproj', help='Path to .csproj file to convert')
    parser.add_argument(
        '--version', '-v',
        default='1.0.0',
        help='Version of NuGet package to reference (default: 1.0.0)'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force conversion even if Choose block already exists'
    )

    args = parser.parse_args(argv)

    csproj_path = Path(args.csproj)

    print("=== SPT Build .csproj Converter ===\n")

    convert_csproj(csproj_path, args.version, args.force)


def main():
    """Main entry point for init-csproj command."""
    run()


if __name__ == '__main__':
    main()
