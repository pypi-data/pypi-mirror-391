import subprocess
from dataclasses import dataclass
from pathlib import Path

import git
from colorama import Fore, Style, init
from packaging.version import InvalidVersion, Version

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]
import tomli_w

# Initialize colorama
init()

# Tag prefix constants
PRERELEASE_TAG_PREFIX = "test-"
RELEASE_TAG_PREFIX = "v"


@dataclass
class VersionInfo:
    path: str
    old_version: str
    new_version: str
    commit_message: str
    tag: str


class bumpuvError(Exception):
    pass


def load_pyproject_toml(path: Path) -> dict:
    """Load pyproject.toml and return parsed content."""
    if not path.exists():
        raise bumpuvError(f"pyproject.toml not found in {path.parent}")

    with open(path, "rb") as f:
        data = tomllib.load(f)

    if "project" not in data or "version" not in data["project"]:
        raise bumpuvError("project.version not found in pyproject.toml")

    return data


def save_pyproject_toml(path: Path, data: dict) -> None:
    """Save data to pyproject.toml."""
    with open(path, "wb") as f:
        tomli_w.dump(data, f)


def validate_version(version_str: str) -> Version:
    """Validate version string according to PEP 440."""
    try:
        return Version(version_str)
    except InvalidVersion:
        raise bumpuvError(f"Invalid version format: {version_str}")


def bump_version(current: Version, bump_type: str) -> Version:
    """Bump version according to type."""
    if bump_type == "major":
        return Version(f"{current.major + 1}.0.0")
    elif bump_type == "minor":
        return Version(f"{current.major}.{current.minor + 1}.0")
    elif bump_type == "patch":
        return Version(f"{current.major}.{current.minor}.{current.micro + 1}")
    elif bump_type == "bump":
        if current.is_prerelease:
            # Increment pre-release number
            pre = current.pre
            if pre:
                pre_type, pre_num = pre
                return Version(f"{current.base_version}{pre_type}{pre_num + 1}")
            else:
                raise bumpuvError(
                    "Cannot bump pre-release version without pre-release number"
                )
        else:
            # Same as patch
            return Version(f"{current.major}.{current.minor}.{current.micro + 1}")
    else:
        raise bumpuvError(f"Unknown bump type: {bump_type}")


def check_git_status(repo: git.Repo, dry_run: bool = False) -> None:
    """Check git repository status."""
    if repo.is_dirty(untracked_files=False):
        if dry_run:
            print(
                f"{Fore.YELLOW}Warning: Repository has unstaged changes{Style.RESET_ALL}"
            )
        else:
            raise bumpuvError(
                "Repository has unstaged changes. Please commit before running"
            )

    if repo.index.diff("HEAD"):
        if dry_run:
            print(
                f"{Fore.YELLOW}Warning: Repository has staged changes{Style.RESET_ALL}"
            )
        else:
            raise bumpuvError(
                "Repository has staged changes. Please commit before running"
            )


def update_version(new_version: str, dry_run: bool = False) -> VersionInfo:
    """Update version in pyproject.toml and create git commit and tag."""
    # Find pyproject.toml and uv.lock
    pyproject_path = Path.cwd() / "pyproject.toml"
    uv_lock_path = Path.cwd() / "uv.lock"

    # Load and validate current version
    data = load_pyproject_toml(pyproject_path)
    current_version_str = data["project"]["version"]
    current_version = validate_version(current_version_str)

    # Validate new version
    if isinstance(new_version, str):
        if new_version in ["major", "minor", "patch", "bump"]:
            new_version_obj = bump_version(current_version, new_version)
        else:
            new_version_obj = validate_version(new_version)
    else:
        new_version_obj = new_version

    # Check version progression
    if new_version_obj <= current_version:
        raise bumpuvError(
            f"New version {new_version_obj} must be greater than current version {current_version}"
        )

    # Check git repository
    try:
        repo = git.Repo(".")
    except git.InvalidGitRepositoryError:
        raise bumpuvError("Not a git repository")

    check_git_status(repo, dry_run)

    # Prepare version info
    new_version_str = str(new_version_obj)
    commit_message = new_version_str
    tag_prefix = (
        PRERELEASE_TAG_PREFIX if new_version_obj.is_prerelease else RELEASE_TAG_PREFIX
    )
    tag = f"{tag_prefix}{new_version_str}"

    version_info = VersionInfo(
        path=str(pyproject_path.absolute()),
        old_version=current_version_str,
        new_version=new_version_str,
        commit_message=commit_message,
        tag=tag,
    )

    if not dry_run:
        # Update version using uv if uv.lock exists, otherwise update pyproject.toml directly
        if uv_lock_path.exists():
            try:
                subprocess.run(
                    ["uv", "version", new_version_str], check=True, cwd=Path.cwd()
                )
            except subprocess.CalledProcessError as e:
                raise bumpuvError(f"Failed to update version with uv: {e}")
        else:
            # Update pyproject.toml directly
            data["project"]["version"] = new_version_str
            save_pyproject_toml(pyproject_path, data)

        # Git commit and tag
        repo.index.add([str(pyproject_path)])
        if uv_lock_path.exists():
            repo.index.add([str(uv_lock_path)])
        repo.index.commit(commit_message)
        repo.create_tag(tag, message=commit_message)

    return version_info
