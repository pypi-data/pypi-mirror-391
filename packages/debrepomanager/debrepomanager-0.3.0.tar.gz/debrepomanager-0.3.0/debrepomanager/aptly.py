"""Aptly wrapper for Debian Repository Manager.

This module provides a high-level interface for managing Debian repositories
using aptly with support for multiple codenames, components, and architectures.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import List, Optional

from debrepomanager.config import Config
from debrepomanager.gpg import GPGManager
from debrepomanager.metadata import MetadataManager

logger = logging.getLogger(__name__)


class AptlyError(Exception):
    """Aptly operation errors."""


class AptlyManager:
    """Manager for aptly repository operations.

    Provides high-level interface for creating, managing, and publishing
    Debian repositories using aptly with snapshot-based atomic updates.

    Each codename has its own aptly root directory for isolation.

    Attributes:
        config: Configuration object
        logger: Logger instance

    Example:
        >>> config = Config("config.yaml")
        >>> manager = AptlyManager(config)
        >>> manager.create_repo("bookworm", "jethome-tools")
    """

    def __init__(self, config: Config):
        """Initialize aptly manager.

        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger("debrepomanager.aptly")
        self.gpg = GPGManager(config)
        self.metadata = MetadataManager(config.aptly_root_base)

    def _get_repo_name(self, codename: str, component: str) -> str:
        """Get internal repository name.

        Convention: {component}-{codename}

        Args:
            codename: Distribution codename
            component: Repository component

        Returns:
            Internal repository name

        Example:
            >>> manager._get_repo_name("bookworm", "jethome-tools")
            'jethome-tools-bookworm'
        """
        return f"{component}-{codename}"

    def _get_aptly_config_path(self, codename: str) -> Path:
        """Get path to aptly config file for codename.

        Args:
            codename: Distribution codename

        Returns:
            Path to aptly.conf

        Example:
            >>> path = manager._get_aptly_config_path("bookworm")
            >>> str(path)
            '/srv/aptly/bookworm/aptly.conf'
        """
        aptly_root = Path(self.config.get_aptly_root(codename))
        return aptly_root / "aptly.conf"

    def _ensure_aptly_root(self, codename: str) -> Path:
        """Ensure aptly root directory exists for codename.

        Creates directory and aptly.conf if they don't exist.

        Args:
            codename: Distribution codename

        Returns:
            Path to aptly root directory

        Raises:
            AptlyError: If directory creation fails
        """
        aptly_root = Path(self.config.get_aptly_root(codename))
        config_file = self._get_aptly_config_path(codename)

        # Create directory if doesn't exist
        try:
            aptly_root.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Ensured aptly root exists: {aptly_root}")
        except PermissionError as e:
            raise AptlyError(
                f"Permission denied creating aptly root: {aptly_root}"
            ) from e
        except OSError as e:
            raise AptlyError(f"Failed to create aptly root: {aptly_root}: {e}") from e

        # Create aptly.conf if doesn't exist
        if not config_file.exists():
            try:
                self._create_aptly_config(codename)
            except Exception as e:
                raise AptlyError(f"Failed to create aptly config: {e}") from e

        return aptly_root

    def _create_aptly_config(self, codename: str) -> None:
        """Create aptly.conf for codename.

        Args:
            codename: Distribution codename

        Raises:
            AptlyError: If config creation fails
        """
        aptly_root = Path(self.config.get_aptly_root(codename))
        config_file = self._get_aptly_config_path(codename)

        aptly_config = {
            "rootDir": str(aptly_root),
            "architectures": self.config.get_architectures(),
            "gpgProvider": "gpg",
            "gpgDisableSign": False,
            "gpgDisableVerify": False,
        }

        try:
            with config_file.open("w") as f:
                json.dump(aptly_config, f, indent=2)

            self.logger.info(f"Created aptly config: {config_file}")
        except PermissionError as e:
            raise AptlyError(f"Permission denied writing config: {config_file}") from e
        except OSError as e:
            raise AptlyError(f"Failed to write config: {config_file}: {e}") from e

    def _run_aptly(
        self, args: List[str], codename: str, capture_output: bool = True
    ) -> subprocess.CompletedProcess[str]:
        """Run aptly command with proper config.

        Args:
            args: Aptly command arguments (e.g., ['repo', 'create', 'myrepo'])
            codename: Distribution codename (determines which aptly root to use)
            capture_output: Whether to capture stdout/stderr

        Returns:
            CompletedProcess with command result

        Raises:
            AptlyError: If aptly command fails

        Example:
            >>> result = manager._run_aptly(['repo', 'list'], 'bookworm')
            >>> print(result.stdout)
        """
        # Ensure aptly root exists
        self._ensure_aptly_root(codename)

        config_path = self._get_aptly_config_path(codename)
        cmd = [self.config.aptly_path, "-config", str(config_path)] + args

        self.logger.debug(f"Running aptly: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, capture_output=capture_output, text=True, check=True
            )
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Aptly command failed: {' '.join(cmd)}")
            self.logger.error(f"Exit code: {e.returncode}")
            self.logger.error(f"Stderr: {e.stderr}")
            raise AptlyError(f"Aptly command failed: {e.stderr}") from e
        except FileNotFoundError as e:
            raise AptlyError(f"aptly binary not found: {self.config.aptly_path}") from e

    def repo_exists(self, codename: str, component: str) -> bool:
        """Check if repository exists.

        Args:
            codename: Distribution codename
            component: Repository component

        Returns:
            True if repository exists, False otherwise

        Example:
            >>> manager.repo_exists("bookworm", "jethome-tools")
            True
        """
        repo_name = self._get_repo_name(codename, component)

        try:
            self._run_aptly(["repo", "show", repo_name], codename)
            return True
        except AptlyError:
            return False

    def create_repo(
        self,
        codename: str,
        component: str,
        architectures: Optional[List[str]] = None,
        force: bool = False,
    ) -> bool:
        """Create new local repository.

        Args:
            codename: Distribution codename (e.g., 'bookworm')
            component: Repository component (e.g., 'jethome-tools')
            architectures: List of architectures. If None, uses config default.
            force: If True, delete and recreate if repository exists

        Returns:
            True if successful

        Raises:
            AptlyError: If creation fails
            ValueError: If repository exists and force=False

        Example:
            >>> manager.create_repo("bookworm", "jethome-tools")
            True
            >>> manager.create_repo("bookworm", "jethome-tools", force=True)
            True
        """
        repo_name = self._get_repo_name(codename, component)

        # Check if exists
        if self.repo_exists(codename, component):
            if force:
                self.logger.warning(
                    f"Repository {repo_name} exists, deleting (--force)"
                )
                self.delete_repo(codename, component)
            else:
                raise ValueError(
                    f"Repository {repo_name} already exists. Use force=True to recreate."
                )

        # Use config architectures if not specified
        if architectures is None:
            architectures = self.config.get_architectures()

        # Create local repository
        try:
            self._run_aptly(
                [
                    "repo",
                    "create",
                    "-distribution",
                    component,
                    "-component",
                    "main",
                    "-architectures",
                    ",".join(architectures),
                    repo_name,
                ],
                codename,
            )
            self.logger.info(f"Created repository: {repo_name}")

            # Create initial empty snapshot
            snapshot_name = f"{repo_name}-init"
            self._run_aptly(
                ["snapshot", "create", snapshot_name, "from", "repo", repo_name],
                codename,
            )
            self.logger.info(f"Created initial snapshot: {snapshot_name}")

            # Initial publish with GPG signing
            self._publish_snapshot(codename, component, snapshot_name, is_initial=True)
            self.logger.info(f"Published repository: {codename}/{component}")

            # Add to metadata
            self.metadata.add_repository(codename, component)

            return True

        except AptlyError:
            self.logger.error(f"Failed to create repository: {repo_name}")
            raise

    def delete_repo(self, codename: str, component: str) -> bool:
        """Delete repository and all its snapshots.

        Args:
            codename: Distribution codename
            component: Repository component

        Returns:
            True if successful

        Raises:
            AptlyError: If deletion fails

        Example:
            >>> manager.delete_repo("bookworm", "jethome-tools")
            True
        """
        repo_name = self._get_repo_name(codename, component)
        prefix = f"{codename}/{component}"

        try:
            # First, unpublish if published
            try:
                self._run_aptly(["publish", "drop", component, prefix], codename)
                self.logger.debug(f"Unpublished: {prefix}")
            except AptlyError:
                # Not published or already dropped - OK
                pass

            # Delete all snapshots for this repo
            result = self._run_aptly(["snapshot", "list", "-raw"], codename)
            all_snapshots = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )

            # Filter snapshots for this repo
            repo_snapshots = [s for s in all_snapshots if s.startswith(f"{repo_name}-")]

            # Delete each snapshot
            for snapshot in repo_snapshots:
                try:
                    self._run_aptly(["snapshot", "drop", snapshot], codename)
                    self.logger.debug(f"Deleted snapshot: {snapshot}")
                except AptlyError as e:
                    self.logger.warning(f"Failed to delete snapshot {snapshot}: {e}")

            # Delete local repository
            # -force flag removes repo even if it has snapshots (shouldn't be needed now)
            self._run_aptly(["repo", "drop", "-force", repo_name], codename)
            self.logger.info(f"Deleted repository: {repo_name}")

            # Remove from metadata
            self.metadata.remove_repository(codename, component)

            return True

        except AptlyError:
            self.logger.error(f"Failed to delete repository: {repo_name}")
            raise

    def _create_dual_format_symlinks(self, codename: str, component: str) -> None:
        """Create symlinks for old format repository access.

        Creates symlinks to support old format URLs while keeping data in new format.

        Old format: deb http://repo.site.com bookworm component
        New format: deb http://repo.site.com/bookworm component main

        Args:
            codename: Distribution codename
            component: Repository component

        Raises:
            AptlyError: If symlink creation fails

        Example:
            >>> manager._create_dual_format_symlinks("bookworm", "jethome-tools")
        """
        import os

        publish_base = Path(self.config.publish_base)

        # Path to new format (actual data location)
        # /srv/repo/public/bookworm/jethome-tools/dists/jethome-tools
        new_path = publish_base / codename / component / "dists" / component

        # Path for old format (symlink location)
        # /srv/repo/public/dists/bookworm/jethome-tools
        old_path = publish_base / "dists" / codename / component

        # Check if new format path exists
        if not new_path.exists():
            self.logger.warning(
                f"New format path doesn't exist yet: {new_path}. "
                "Skipping symlink creation."
            )
            return

        try:
            # Create parent directory for old format symlink
            old_path.parent.mkdir(parents=True, exist_ok=True)

            # Calculate relative path from old_path to new_path
            # This makes symlinks portable if the repo is moved
            relative_path = os.path.relpath(new_path, old_path.parent)

            # Remove existing symlink if present
            if old_path.exists() or old_path.is_symlink():
                if old_path.is_symlink():
                    old_path.unlink()
                    self.logger.debug(f"Removed old symlink: {old_path}")
                else:
                    # Path exists but is not a symlink - don't touch it
                    self.logger.warning(
                        f"Path exists but is not a symlink: {old_path}. "
                        "Skipping symlink creation to avoid data loss."
                    )
                    return

            # Create symlink
            os.symlink(relative_path, old_path)
            self.logger.info(
                f"Created dual format symlink: {old_path} -> {relative_path}"
            )

        except OSError as e:
            raise AptlyError(f"Failed to create symlink {old_path}: {e}") from e
        except Exception as e:
            raise AptlyError(f"Unexpected error creating symlink: {e}") from e

    def _publish_snapshot(
        self,
        codename: str,
        component: str,
        snapshot_name: str,
        is_initial: bool = False,
    ) -> bool:
        """Publish or switch to snapshot with GPG signing.

        Args:
            codename: Distribution codename
            component: Repository component
            snapshot_name: Snapshot name to publish
            is_initial: If True, initial publish. If False, switch existing.

        Returns:
            True if successful

        Raises:
            AptlyError: If publish fails

        Example:
            >>> manager._publish_snapshot("bookworm", "jethome-tools", "snap-123")
            True
        """
        prefix = f"{codename}/{component}"

        # Check GPG key available
        if not self.gpg.check_key_available():
            raise AptlyError(
                f"GPG key {self.config.gpg_key_id} not found. "
                "Please import the key first."
            )

        try:
            if is_initial:
                # Initial publish
                self._run_aptly(
                    [
                        "publish",
                        "snapshot",
                        "-distribution",
                        component,
                        "-gpg-key",
                        self.config.gpg_key_id,
                        snapshot_name,
                        prefix,
                    ],
                    codename,
                )
                self.logger.info(f"Published snapshot: {snapshot_name} at {prefix}")
            else:
                # Switch existing publication
                self._run_aptly(
                    [
                        "publish",
                        "switch",
                        component,  # distribution
                        prefix,
                        snapshot_name,
                    ],
                    codename,
                )
                self.logger.info(f"Switched to snapshot: {snapshot_name}")

            # Create/update symlinks for dual format support
            if self.config.dual_format_enabled and self.config.dual_format_auto_symlink:
                try:
                    self._create_dual_format_symlinks(codename, component)
                except AptlyError as e:
                    # Log warning but don't fail the publish
                    self.logger.warning(f"Failed to create dual format symlinks: {e}")

            return True

        except AptlyError:
            self.logger.error(f"Failed to publish snapshot: {snapshot_name}")
            raise

    def add_packages(
        self,
        codename: str,
        component: str,
        packages: List[str],
        create_snapshot: bool = True,
    ) -> bool:
        """Add packages to repository with atomic snapshot publication.

        Args:
            codename: Distribution codename
            component: Repository component
            packages: List of .deb file paths to add
            create_snapshot: If True, create snapshot after adding (default: True)

        Returns:
            True if successful

        Raises:
            AptlyError: If operation fails
            ValueError: If repository doesn't exist and auto_create is disabled
            FileNotFoundError: If package files don't exist

        Example:
            >>> manager.add_packages("bookworm", "jethome-tools", ["pkg.deb"])
            True
        """
        repo_name = self._get_repo_name(codename, component)

        # Check if repo exists
        if not self.repo_exists(codename, component):
            if self.config.auto_create_repos:
                self.logger.info(
                    f"Repository {repo_name} doesn't exist, creating (auto_create=True)"
                )
                self.create_repo(codename, component)
            else:
                raise ValueError(
                    f"Repository {repo_name} doesn't exist. "
                    "Create it first or enable auto_create in config."
                )

        # Validate package files exist
        for pkg in packages:
            pkg_path = Path(pkg)
            if not pkg_path.exists():
                raise FileNotFoundError(f"Package file not found: {pkg}")
            if not pkg_path.is_file():
                raise ValueError(f"Not a file: {pkg}")

        # Add packages to repository
        try:
            self._run_aptly(["repo", "add", repo_name] + packages, codename)
            self.logger.info(f"Added {len(packages)} package(s) to {repo_name}")

            # Create snapshot if requested
            if create_snapshot:
                snapshot_name = self._create_snapshot(codename, component)
                self.logger.info(f"Created snapshot: {snapshot_name}")

                # Publish snapshot (atomic switch)
                self._publish_snapshot(
                    codename, component, snapshot_name, is_initial=False
                )
                self.logger.info(f"Published snapshot: {snapshot_name}")

                # Cleanup old snapshots
                cleaned = self._cleanup_old_snapshots(codename, component)
                if cleaned > 0:
                    self.logger.info(f"Cleaned up {cleaned} old snapshot(s)")

            return True

        except AptlyError:
            self.logger.error(f"Failed to add packages to {repo_name}")
            raise

    def _create_snapshot(self, codename: str, component: str) -> str:
        """Create snapshot from repository.

        Args:
            codename: Distribution codename
            component: Repository component

        Returns:
            Snapshot name

        Raises:
            AptlyError: If snapshot creation fails
        """
        from datetime import datetime

        repo_name = self._get_repo_name(codename, component)

        # Generate snapshot name with timestamp
        # First substitute component and codename, then apply strftime for timestamp
        format_template = self.config.snapshot_format
        format_with_names = format_template.format(
            component=component, codename=codename
        )
        snapshot_name = datetime.now().strftime(format_with_names)

        try:
            self._run_aptly(
                ["snapshot", "create", snapshot_name, "from", "repo", repo_name],
                codename,
            )
            return snapshot_name

        except AptlyError:
            self.logger.error(f"Failed to create snapshot: {snapshot_name}")
            raise

    def _cleanup_old_snapshots(
        self, codename: str, component: str, keep: Optional[int] = None
    ) -> int:
        """Remove old snapshots, keeping last N.

        Args:
            codename: Distribution codename
            component: Repository component
            keep: Number of snapshots to keep. If None, uses config.max_snapshots

        Returns:
            Number of snapshots removed

        Raises:
            AptlyError: If cleanup fails
        """
        if keep is None:
            keep = self.config.max_snapshots

        repo_name = self._get_repo_name(codename, component)
        prefix = f"{repo_name}-"

        try:
            # List all snapshots
            result = self._run_aptly(["snapshot", "list", "-raw"], codename)
            all_snapshots = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )

            # Filter snapshots for this repo (excluding -init snapshot)
            repo_snapshots = [
                s
                for s in all_snapshots
                if s.startswith(prefix) and not s.endswith("-init")
            ]

            # Sort by name (timestamp is in name)
            repo_snapshots.sort()

            # Keep last N, remove others
            to_remove = repo_snapshots[:-keep] if len(repo_snapshots) > keep else []

            removed_count = 0
            for snapshot in to_remove:
                try:
                    self._run_aptly(["snapshot", "drop", snapshot], codename)
                    removed_count += 1
                    self.logger.debug(f"Removed snapshot: {snapshot}")
                except AptlyError as e:
                    self.logger.warning(f"Failed to remove snapshot {snapshot}: {e}")

            return removed_count

        except AptlyError:
            self.logger.error("Failed to cleanup snapshots")
            # Don't raise - cleanup is not critical
            return 0

    def list_repos(self, codename: Optional[str] = None) -> List[str]:
        """List repositories.

        Args:
            codename: Optional codename filter. If None, lists all from metadata.

        Returns:
            List of repository names

        Example:
            >>> repos = manager.list_repos("bookworm")
            >>> print(repos)
            ['jethome-tools-bookworm', 'jethome-armbian-bookworm']
        """
        if codename:
            # List repos for specific codename from aptly
            try:
                result = self._run_aptly(["repo", "list", "-raw"], codename)
                repos = (
                    result.stdout.strip().split("\n") if result.stdout.strip() else []
                )
                return repos
            except AptlyError:
                return []
        else:
            # List all repos from metadata
            try:
                repo_list = self.metadata.list_repositories()
                # Convert to repo names: {component}-{codename}
                return [f"{repo['component']}-{repo['codename']}" for repo in repo_list]
            except Exception as e:
                self.logger.warning(f"Failed to load metadata: {e}")
                return []

    def list_packages(self, codename: str, component: str) -> List[str]:
        """List packages in repository.

        Args:
            codename: Distribution codename
            component: Repository component

        Returns:
            List of package references (Name Version Architecture)

        Raises:
            AptlyError: If operation fails
            ValueError: If repository doesn't exist

        Example:
            >>> packages = manager.list_packages("bookworm", "jethome-tools")
            >>> for pkg in packages:
            ...     print(pkg)
            jethome-tool_1.0_amd64
        """
        repo_name = self._get_repo_name(codename, component)

        # Check if repo exists
        if not self.repo_exists(codename, component):
            raise ValueError(f"Repository {repo_name} doesn't exist")

        try:
            result = self._run_aptly(
                ["repo", "show", "-with-packages", repo_name], codename
            )

            # Parse output to extract package list
            packages = []
            in_packages = False

            for line in result.stdout.split("\n"):
                line = line.strip()

                if line.startswith("Packages:"):
                    in_packages = True
                    continue

                if in_packages:
                    if line and not line.startswith("Number"):
                        packages.append(line)
                    elif line.startswith("Number"):
                        # End of packages section
                        break

            return packages

        except AptlyError:
            self.logger.error(f"Failed to list packages in {repo_name}")
            raise

    def remove_packages(
        self,
        codename: str,
        component: str,
        package_refs: List[str],
        dry_run: bool = False,
    ) -> bool:
        """Remove packages from repository.

        Args:
            codename: Distribution codename
            component: Repository component
            package_refs: List of package references (name_version_arch)
            dry_run: If True, only show what would be removed without actually removing

        Returns:
            True if successful

        Raises:
            AptlyError: If removal fails
            ValueError: If repository doesn't exist

        Example:
            >>> manager.remove_packages(
            ...     "bookworm",
            ...     "jethome-tools",
            ...     ["pkg_1.0_amd64", "pkg_2.0_arm64"],
            ...     dry_run=True
            ... )
            True
        """
        repo_name = self._get_repo_name(codename, component)

        # Check if repo exists
        if not self.repo_exists(codename, component):
            raise ValueError(f"Repository {repo_name} doesn't exist")

        if not package_refs:
            self.logger.warning("No packages to remove")
            return True

        if dry_run:
            self.logger.info(
                f"[DRY RUN] Would remove {len(package_refs)} packages from {repo_name}"
            )
            for ref in package_refs[:10]:  # Show first 10
                self.logger.info(f"  - {ref}")
            if len(package_refs) > 10:
                self.logger.info(f"  ... and {len(package_refs) - 10} more")
            return True

        try:
            self.logger.info(f"Removing {len(package_refs)} packages from {repo_name}")

            # aptly repo remove supports multiple package refs at once
            # But to avoid command line length limits, we batch them
            batch_size = 50
            for i in range(0, len(package_refs), batch_size):
                batch = package_refs[i : i + batch_size]
                cmd = ["repo", "remove", repo_name] + batch

                self.logger.debug(
                    f"Removing batch {i // batch_size + 1}: {len(batch)} packages"
                )
                self._run_aptly(cmd, codename)

            self.logger.info(f"Successfully removed {len(package_refs)} packages")

            # Republish after removal to update the published repository
            self.logger.info("Republishing repository after package removal...")
            # Create new snapshot and publish
            snapshot_name = self._create_snapshot(codename, component)
            self._publish_snapshot(codename, component, snapshot_name, is_initial=False)

            return True

        except AptlyError:
            self.logger.error(f"Failed to remove packages from {repo_name}")
            raise

    def get_published_snapshot(self, codename: str, component: str) -> Optional[str]:
        """Get currently published snapshot for repository.

        Args:
            codename: Distribution codename
            component: Repository component

        Returns:
            Snapshot name if published, None if not published

        Example:
            >>> snapshot = manager.get_published_snapshot("bookworm", "jethome-tools")
            >>> print(snapshot)
            jethome-tools-bookworm-20251101-123456
        """
        try:
            result = self._run_aptly(["publish", "list", "-raw"], codename)

            # Parse publish list output
            # Format: prefix:distribution
            prefix = f"{codename}/{component}"

            for line in result.stdout.split("\n"):
                if line.strip().startswith(prefix):
                    # Published entry found
                    # Now get snapshot name from publish show
                    try:
                        show_result = self._run_aptly(
                            ["publish", "show", component, prefix], codename
                        )

                        # Parse show output for snapshot info
                        for show_line in show_result.stdout.split("\n"):
                            if "Snapshot:" in show_line:
                                # Extract snapshot name
                                parts = show_line.split(":")
                                if len(parts) >= 2:
                                    return parts[1].strip()

                    except AptlyError:
                        pass

            return None

        except AptlyError:
            # Not published yet
            return None

    def verify_repo(self, codename: str, component: str) -> bool:
        """Verify repository consistency.

        Args:
            codename: Distribution codename
            component: Repository component

        Returns:
            True if repository is consistent

        Raises:
            AptlyError: If verification fails
            ValueError: If repository doesn't exist

        Example:
            >>> manager.verify_repo("bookworm", "jethome-tools")
            True
        """
        repo_name = self._get_repo_name(codename, component)

        if not self.repo_exists(codename, component):
            raise ValueError(f"Repository {repo_name} doesn't exist")

        try:
            # Verify repository
            self._run_aptly(["repo", "show", repo_name], codename)

            # Check if published
            snapshot = self.get_published_snapshot(codename, component)

            if snapshot:
                # Verify snapshot exists
                self._run_aptly(["snapshot", "show", snapshot], codename)
                self.logger.info(
                    f"Repository {repo_name} verified (published: {snapshot})"
                )
            else:
                self.logger.info(f"Repository {repo_name} verified (not published)")

            return True

        except AptlyError:
            self.logger.error(f"Failed to verify repository {repo_name}")
            raise

    def sync_metadata(self) -> int:
        """Sync metadata with actual aptly state.

        Scans all aptly roots to find existing repositories and
        rebuilds metadata from scratch. Useful after manual aptly
        operations or to recover from metadata corruption.

        Returns:
            Number of repositories found and synced

        Example:
            >>> count = manager.sync_metadata()
            >>> print(f"Synced {count} repositories")
        """
        return self.metadata.sync_from_aptly(self)
