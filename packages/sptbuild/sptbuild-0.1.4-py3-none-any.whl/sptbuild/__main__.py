"""Main CLI entry point for sptbuild."""

import sys
import argparse
from . import __version__
from .commands import package, upload, release, setup_ci, init_config, init_csproj


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='sptbuild',
        description='Build and release tool for SPT client plugins',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  package       Create a zip package for SPT plugin
  upload        Upload release zip to GitLab project uploads
  release       Create GitLab release with package registry (CI mode)
  setup-ci      Setup NuGet package with SPT/EFT reference assemblies
  init-config   Generate example plugin.toml configuration file
  init-csproj   Convert .csproj to CI-compatible format

Environment Variables:
  Required for most commands:
    UPLOAD_PACKAGE_NAME     Package name (e.g., flir.enemymarkers)
    VERSION_SOURCE_FILE     Path to file containing version string
    GITLAB_PROJECT_ID       GitLab project ID
    GITLAB_USERNAME         GitLab username
    GITLAB_PROJECT_NAME     GitLab project name

  For authentication (non-CI):
    GITLAB_SECRET_TOKEN     Personal access token with 'api' scope

  For CI mode:
    CI_JOB_TOKEN           CI job token (auto-provided in GitLab CI)
    CI_API_V4_URL          CI API URL (auto-provided in GitLab CI)

Examples:
  # Package your plugin
  sptbuild package

  # Upload to GitLab
  sptbuild upload

  # Upload and create release
  sptbuild upload --release

  # Setup CI references package
  sptbuild setup-ci myproject.csproj --upload

  # Generate plugin.toml configuration
  sptbuild init-config

  # Convert .csproj to CI-compatible format
  sptbuild init-csproj yourproject.csproj

For more information on a specific command:
  sptbuild <command> --help
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Package command
    package_parser = subparsers.add_parser(
        'package',
        help='Create a zip package for SPT plugin'
    )

    # Upload command
    upload_parser = subparsers.add_parser(
        'upload',
        help='Upload release zip to GitLab project uploads'
    )
    upload_parser.add_argument(
        '-r', '--release',
        action='store_true',
        help='Create a GitLab release after uploading'
    )

    # Release command (CI mode)
    release_parser = subparsers.add_parser(
        'release',
        help='Create GitLab release with package registry (CI mode)'
    )

    # Setup-CI command
    setup_ci_parser = subparsers.add_parser(
        'setup-ci',
        help='Setup NuGet package with SPT/EFT reference assemblies'
    )
    setup_ci_parser.add_argument(
        'csproj',
        help='Path to the .csproj file'
    )
    setup_ci_parser.add_argument(
        '-u', '--upload',
        action='store_true',
        help='Upload package to GitLab after building'
    )
    setup_ci_parser.add_argument(
        '-m', '--modify',
        action='store_true',
        help='Update the .csproj with the new package version'
    )

    # Init-config command
    init_config_parser = subparsers.add_parser(
        'init-config',
        help='Generate example plugin.toml configuration file'
    )
    init_config_parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Overwrite existing file'
    )
    init_config_parser.add_argument(
        '-o', '--output',
        default='plugin.toml',
        help='Output file path (use "-" for stdout, default: plugin.toml)'
    )

    # Init-csproj command
    init_csproj_parser = subparsers.add_parser(
        'init-csproj',
        help='Convert .csproj to CI-compatible format'
    )
    init_csproj_parser.add_argument(
        'csproj',
        help='Path to the .csproj file to convert'
    )
    init_csproj_parser.add_argument(
        '-v', '--version',
        default='1.0.0',
        help='Version of NuGet package to reference (default: 1.0.0)'
    )
    init_csproj_parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Force conversion even if Choose block already exists'
    )

    args = parser.parse_args()

    # If no command provided, show help
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to appropriate command
    try:
        if args.command == 'package':
            package.run()
        elif args.command == 'upload':
            # Pass the release flag to upload command
            upload.run(['-r'] if args.release else [])
        elif args.command == 'release':
            release.run()
        elif args.command == 'setup-ci':
            # Build args list for setup-ci
            setup_args = [args.csproj]
            if args.upload:
                setup_args.append('--upload')
            if args.modify:
                setup_args.append('--modify')
            setup_ci.run(setup_args)
        elif args.command == 'init-config':
            # Build args list for init-config
            init_args = []
            if args.force:
                init_args.append('--force')
            if args.output:
                init_args.extend(['--output', args.output])
            init_config.run(init_args)
        elif args.command == 'init-csproj':
            # Build args list for init-csproj
            init_csproj_args = [args.csproj]
            if args.version:
                init_csproj_args.extend(['--version', args.version])
            if args.force:
                init_csproj_args.append('--force')
            init_csproj.run(init_csproj_args)
    except KeyboardInterrupt:
        print("\n\nAborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
