import argparse
import sys

from colorama import Fore, Style, init

from ._core import bumpuvError, update_version

# Initialize colorama
init()


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="bumpuv",
        description="Version bumping tool for Python projects using pyproject.toml",
    )
    parser.add_argument(
        "version",
        nargs="?",
        default="bump",
        help="Version to set or bump type (major|minor|patch|bump)",
    )

    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    try:
        version_info = update_version(args.version, args.dry_run)

        # Display results
        print(f"Updated: {version_info.path}")
        print(f"Version: {version_info.old_version} → {version_info.new_version}")
        print(f"Commit: {version_info.commit_message}")
        print(f"Tag: {version_info.tag}")

        if args.dry_run:
            print("(dry run - no changes made)")

    except bumpuvError as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
