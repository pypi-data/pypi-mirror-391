"""Repository metadata management for Debian Repository Manager.

This module handles tracking of created repositories in metadata file,
allowing efficient listing without scanning all aptly roots.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from debrepomanager.aptly import AptlyManager

logger = logging.getLogger(__name__)


class MetadataError(Exception):
    """Metadata operation errors."""


class MetadataManager:
    """Manages repository metadata tracking.

    Stores repository information in JSON file for fast lookups.
    Metadata is automatically updated on create/delete operations.

    Attributes:
            metadata_path: Path to metadata.json file
            _metadata: In-memory metadata cache

    Example:
            >>> metadata = MetadataManager("/srv/aptly")
            >>> metadata.add_repository("bookworm", "tools")
            >>> repos = metadata.list_repositories()
    """

    def __init__(self, aptly_root_base: str):
        """Initialize metadata manager.

        Args:
                aptly_root_base: Base directory for aptly roots

        Example:
                >>> metadata = MetadataManager("/srv/aptly")
        """
        self.aptly_root_base = Path(aptly_root_base)
        self.metadata_dir = self.aptly_root_base / ".repomanager"
        self.metadata_path = self.metadata_dir / "metadata.json"
        self._metadata: Optional[Dict[str, Any]] = None
        self.logger = logging.getLogger("debrepomanager.metadata")

    def _ensure_metadata_dir(self) -> None:
        """Create metadata directory if it doesn't exist."""
        try:
            self.metadata_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Ensured metadata directory: {self.metadata_dir}")
        except OSError as e:
            raise MetadataError(f"Failed to create metadata directory: {e}") from e

    def load(self) -> Dict[str, Any]:
        """Load metadata from file.

        Returns:
                Metadata dictionary

        Raises:
                MetadataError: If metadata file is corrupted
        """
        if self._metadata is not None:
            return self._metadata

        if not self.metadata_path.exists():
            # No metadata file yet - return empty metadata
            self._metadata = {
                "repositories": [],
                "last_updated": datetime.now().isoformat(),
            }
            return self._metadata

        try:
            with self.metadata_path.open("r") as f:
                self._metadata = json.load(f)

            self.logger.debug(f"Loaded metadata from {self.metadata_path}")
            return self._metadata

        except json.JSONDecodeError as e:
            raise MetadataError(f"Corrupted metadata file: {e}") from e
        except OSError as e:
            raise MetadataError(f"Failed to read metadata: {e}") from e

    def save(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Save metadata to file.

        Args:
                metadata: Metadata dict to save. If None, saves cached metadata.

        Raises:
                MetadataError: If save fails
        """
        if metadata is None:
            metadata = self._metadata

        if metadata is None:
            raise MetadataError("No metadata to save")

        self._ensure_metadata_dir()

        # Update last_updated timestamp
        metadata["last_updated"] = datetime.now().isoformat()

        try:
            with self.metadata_path.open("w") as f:
                json.dump(metadata, f, indent=2, sort_keys=True)

            self.logger.debug(f"Saved metadata to {self.metadata_path}")

        except OSError as e:
            raise MetadataError(f"Failed to write metadata: {e}") from e

    def add_repository(self, codename: str, component: str) -> None:
        """Add repository to metadata.

        Args:
                codename: Distribution codename
                component: Repository component

        Example:
                >>> metadata.add_repository("bookworm", "tools")
        """
        metadata = self.load()

        # Check if already exists
        repos = metadata["repositories"]
        for repo in repos:
            if repo["codename"] == codename and repo["component"] == component:
                self.logger.debug(
                    f"Repository {codename}/{component} already in metadata"
                )
                return

        # Add new repository
        new_repo = {
            "codename": codename,
            "component": component,
            "created": datetime.now().isoformat(),
        }
        metadata["repositories"].append(new_repo)

        self.save(metadata)
        self.logger.info(f"Added repository to metadata: {codename}/{component}")

    def remove_repository(self, codename: str, component: str) -> None:
        """Remove repository from metadata.

        Args:
                codename: Distribution codename
                component: Repository component

        Example:
                >>> metadata.remove_repository("bookworm", "tools")
        """
        metadata = self.load()

        # Filter out the repository
        repos = metadata["repositories"]
        original_count = len(repos)
        metadata["repositories"] = [
            r
            for r in repos
            if not (r["codename"] == codename and r["component"] == component)
        ]

        removed_count = original_count - len(metadata["repositories"])
        if removed_count > 0:
            self.save(metadata)
            self.logger.info(
                f"Removed repository from metadata: {codename}/{component}"
            )
        else:
            self.logger.debug(
                f"Repository {codename}/{component} not found in metadata"
            )

    def list_repositories(self, codename: Optional[str] = None) -> List[Dict[str, str]]:
        """List all repositories from metadata.

        Args:
            codename: Optional filter by codename

        Returns:
            List of repository dicts with codename, component, created fields

        Example:
            >>> repos = metadata.list_repositories()
            >>> repos = metadata.list_repositories("bookworm")
        """
        metadata = self.load()
        repos: List[Dict[str, str]] = list(metadata["repositories"])

        if codename:
            repos = [r for r in repos if r["codename"] == codename]

        return repos

    def sync_from_aptly(self, aptly_manager: "AptlyManager") -> int:
        """Sync metadata with actual aptly repository state.

        Scans all aptly roots to find existing repositories and
        rebuilds metadata from scratch.

        Args:
                aptly_manager: AptlyManager instance to query aptly

        Returns:
                Number of repositories found and synced

        Example:
                >>> from debrepomanager import AptlyManager
                >>> manager = AptlyManager(config)
                >>> count = metadata.sync_from_aptly(manager)
        """
        self.logger.info("Starting metadata sync from aptly state...")

        new_repositories: List[Dict[str, str]] = []
        new_metadata: Dict[str, Any] = {
            "repositories": new_repositories,
            "last_updated": datetime.now().isoformat(),
        }

        # Scan all codename directories under aptly_root_base
        if not self.aptly_root_base.exists():
            self.logger.warning(f"Aptly root base not found: {self.aptly_root_base}")
            self.save(new_metadata)
            return 0

        synced_count = 0

        # Scan all subdirectories (each is a potential codename)
        for codename_dir in self.aptly_root_base.iterdir():
            if not codename_dir.is_dir():
                continue

            # Skip metadata directory
            if codename_dir.name == ".repomanager":
                continue

            codename = codename_dir.name

            # Check if this directory has aptly.conf (indicates valid aptly root)
            aptly_conf = codename_dir / "aptly.conf"
            if not aptly_conf.exists():
                self.logger.debug(f"Skipping {codename} - no aptly.conf found")
                continue

            # List repos for this codename
            try:
                repos = aptly_manager.list_repos(codename)

                for repo_name in repos:
                    # Parse repo name: {component}-{codename}
                    # Extract component by removing -{codename} suffix
                    if repo_name.endswith(f"-{codename}"):
                        component = repo_name[: -len(f"-{codename}")]

                        new_repositories.append(
                            {
                                "codename": codename,
                                "component": component,
                                "created": datetime.now().isoformat(),
                            }
                        )
                        synced_count += 1
                        self.logger.debug(f"Synced repository: {codename}/{component}")

            except Exception as e:
                self.logger.warning(f"Failed to list repos for {codename}: {e}")
                continue

        self.save(new_metadata)
        self.logger.info(f"Sync complete: {synced_count} repositories")
        self._metadata = new_metadata

        return synced_count
