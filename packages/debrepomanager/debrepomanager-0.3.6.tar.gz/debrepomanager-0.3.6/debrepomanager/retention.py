"""Retention policy engine for automatic package cleanup.

This module provides functionality to automatically clean up old package versions
based on configurable retention policies (min_versions, max_age_days).
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from debian.debian_support import Version

from debrepomanager.aptly import AptlyManager
from debrepomanager.config import Config

logger = logging.getLogger(__name__)


@dataclass
class PackageInfo:
    """Information about a package for retention analysis.

    Attributes:
        name: Package name
        version: Package version string
        architecture: Package architecture (amd64, arm64, etc.)
        upload_date: Date when package was uploaded
        full_ref: Full package reference (name_version_arch)
        size_bytes: Package size in bytes (if available)
    """

    name: str
    version: str
    architecture: str
    upload_date: datetime
    full_ref: str
    size_bytes: int = 0

    @property
    def version_obj(self) -> Version:
        """Get debian.debian_support.Version object for comparison."""
        return Version(self.version)

    @property
    def age_days(self) -> int:
        """Get package age in days."""
        return (datetime.now() - self.upload_date).days


class RetentionPolicy:
    """Retention policy engine for package cleanup.

    This class implements the logic for determining which packages to remove
    based on retention policies (min_versions, max_age_days).
    """

    def __init__(self, config: Config, aptly: AptlyManager):
        """Initialize retention policy engine.

        Args:
            config: Configuration object
            aptly: AptlyManager instance
        """
        self.config = config
        self.aptly = aptly
        self.logger = logging.getLogger(__name__)

    def get_policy(self, component: str) -> Dict[str, Any]:
        """Get retention policy for a component.

        Args:
            component: Repository component name

        Returns:
            Dictionary with min_versions and max_age_days

        Example:
            >>> policy = retention.get_policy("jethome-tools")
            >>> policy
            {'min_versions': 5, 'max_age_days': 90}
        """
        retention_config = self.config._config.get("retention", {})
        default_policy = retention_config.get("default", {})
        overrides = retention_config.get("overrides", {})

        # Check for component-specific override
        if component in overrides:
            self.logger.debug(f"Using override policy for {component}")
            return dict(overrides[component])

        self.logger.debug(f"Using default policy for {component}")
        return dict(default_policy)

    def _parse_package_ref(self, ref: str) -> Optional[tuple]:
        """Parse package reference into components.

        Args:
            ref: Package reference (e.g., "pkg_1.0_amd64")

        Returns:
            Tuple of (name, version, arch) or None if parsing fails

        Example:
            >>> self._parse_package_ref("jethome-tool_1.2.3_amd64")
            ('jethome-tool', '1.2.3', 'amd64')
        """
        # Format: name_version_arch
        # Version can contain underscores, so we parse from the end
        parts = ref.rsplit("_", 2)

        if len(parts) != 3:
            self.logger.warning(f"Failed to parse package ref: {ref}")
            return None

        name, version, arch = parts
        return (name, version, arch)

    def _get_package_upload_date(
        self, codename: str, component: str, package_ref: str
    ) -> datetime:
        """Get upload date for a package from aptly pool file mtime.

        Args:
            codename: Distribution codename
            component: Repository component
            package_ref: Package reference (name_version_arch)

        Returns:
            Upload date from pool file mtime, or datetime.now() if not found

        Example:
            >>> date = retention._get_package_upload_date("bookworm", "tools", "pkg_1.0_amd64")
        """
        from pathlib import Path

        # Get aptly pool directory for this codename
        aptly_root = self.config.get_aptly_root(codename)
        pool_dir = Path(aptly_root) / ".aptly" / "pool"

        if not pool_dir.exists():
            self.logger.warning(f"Pool directory not found: {pool_dir}")
            return datetime.now()

        # Search for .deb file in pool
        deb_filename = f"{package_ref}.deb"

        try:
            # Pool structure: pool/XX/YY/package.deb (2-level hash)
            # Search recursively (should be fast with limited depth)
            for deb_file in pool_dir.rglob(deb_filename):
                if deb_file.is_file():
                    # Get file modification time
                    mtime = deb_file.stat().st_mtime
                    upload_date = datetime.fromtimestamp(mtime)
                    self.logger.debug(
                        f"Found {deb_filename}: uploaded {upload_date.isoformat()}"
                    )
                    return upload_date

        except (OSError, PermissionError) as e:
            self.logger.warning(f"Error accessing pool directory: {e}")

        # Fallback: file not found (shouldn't happen for existing packages)
        # Treat as "new" package - won't be cleaned by age
        self.logger.debug(
            f"Package file not found in pool: {deb_filename}, treating as new"
        )
        return datetime.now()

    def analyze_repository(
        self, codename: str, component: str
    ) -> Dict[str, List[PackageInfo]]:
        """Analyze repository and group packages by name.

        Args:
            codename: Distribution codename
            component: Repository component

        Returns:
            Dictionary mapping package names to lists of PackageInfo objects

        Example:
            >>> packages = retention.analyze_repository("bookworm", "jethome-tools")
            >>> packages.keys()
            dict_keys(['pkg1', 'pkg2', 'pkg3'])
            >>> len(packages['pkg1'])
            5
        """
        self.logger.info(f"Analyzing repository {codename}/{component}")

        # Get all packages from repository
        package_refs = self.aptly.list_packages(codename, component)

        # Group by package name
        grouped: Dict[str, List[PackageInfo]] = {}

        for ref in package_refs:
            parsed = self._parse_package_ref(ref)
            if not parsed:
                continue

            name, version, arch = parsed

            # Get upload date
            upload_date = self._get_package_upload_date(codename, component, ref)

            # Create PackageInfo
            pkg_info = PackageInfo(
                name=name,
                version=version,
                architecture=arch,
                upload_date=upload_date,
                full_ref=ref,
            )

            # Add to group
            if name not in grouped:
                grouped[name] = []
            grouped[name].append(pkg_info)

        self.logger.info(
            f"Found {len(package_refs)} packages in {len(grouped)} unique packages"
        )

        return grouped

    def get_packages_to_remove(
        self, codename: str, component: str
    ) -> List[PackageInfo]:
        """Determine which packages to remove based on retention policy.

        Algorithm:
        1. Group packages by name
        2. For each group:
           - Sort by version (newest first)
           - Always keep keep_latest versions (default: 1)
           - Keep minimum min_versions packages
           - From remaining, remove aged packages (older than max_age_days)
           - Safety: never delete last version unless delete_last_aged_version=true

        Args:
            codename: Distribution codename
            component: Repository component

        Returns:
            List of PackageInfo objects to remove

        Example:
            >>> to_remove = retention.get_packages_to_remove("bookworm", "jethome-tools")
            >>> len(to_remove)
            15
        """
        policy = self.get_policy(component)
        min_versions = policy.get("min_versions", 5)
        max_age_days = policy.get("max_age_days", 90)
        keep_latest = policy.get("keep_latest", 1)
        delete_last_aged_version = policy.get("delete_last_aged_version", False)

        self.logger.info(
            f"Retention policy: min_versions={min_versions}, max_age_days={max_age_days}, "
            f"keep_latest={keep_latest}, delete_last_aged_version={delete_last_aged_version}"
        )

        # Analyze repository
        grouped = self.analyze_repository(codename, component)

        to_remove: List[PackageInfo] = []

        # Process each package group
        for pkg_name, packages in grouped.items():
            # Sort by version (newest first)
            sorted_packages = sorted(
                packages, key=lambda p: p.version_obj, reverse=True
            )

            # Determine how many to keep
            # Start with max(min_versions, keep_latest) to ensure both constraints
            keep_count = max(min_versions, keep_latest)

            # Keep newest keep_count packages unconditionally
            to_keep = sorted_packages[:keep_count]
            candidates = sorted_packages[keep_count:]

            self.logger.debug(
                f"{pkg_name}: {len(packages)} versions, keeping {len(to_keep)}, "
                f"{len(candidates)} candidates for removal"
            )

            # Safety check: if this is the ONLY version of package, don't delete unless explicit
            is_only_version = len(sorted_packages) == 1

            # From candidates, remove those older than max_age_days
            for pkg in candidates:
                if pkg.age_days > max_age_days:
                    # Safety: never delete if it's the only version (unless explicitly allowed)
                    if is_only_version and not delete_last_aged_version:
                        self.logger.warning(
                            f"  - Keeping only version despite age: {pkg.full_ref} "
                            f"(age: {pkg.age_days} days, delete_last_aged_version=false)"
                        )
                        continue

                    self.logger.debug(
                        f"  - Marking for removal: {pkg.full_ref} "
                        f"(age: {pkg.age_days} days)"
                    )
                    to_remove.append(pkg)
                else:
                    self.logger.debug(
                        f"  - Keeping: {pkg.full_ref} (age: {pkg.age_days} days)"
                    )

        self.logger.info(f"Total packages to remove: {len(to_remove)}")

        return to_remove

    def cleanup(
        self, codename: str, component: str, dry_run: bool = True
    ) -> Dict[str, Any]:
        """Execute cleanup based on retention policy.

        Args:
            codename: Distribution codename
            component: Repository component
            dry_run: If True, only analyze without removing packages

        Returns:
            Dictionary with cleanup results:
            - analyzed: Number of packages analyzed
            - to_remove: Number of packages to remove
            - removed: Number of packages actually removed
            - space_mb: Estimated space to free (MB)
            - packages: List of package refs that would be/were removed

        Example:
            >>> result = retention.cleanup("bookworm", "jethome-tools", dry_run=True)
            >>> result['analyzed']
            50
            >>> result['to_remove']
            15
        """
        self.logger.info(
            f"Starting cleanup for {codename}/{component} (dry_run={dry_run})"
        )

        # Get packages to remove (calls analyze_repository internally)
        to_remove = self.get_packages_to_remove(codename, component)

        # Calculate total packages
        # NOTE: This calls analyze_repository again (inefficient but acceptable for MVP)
        # TODO for v0.3: Cache analyzed data to avoid duplicate aptly calls
        grouped = self.analyze_repository(codename, component)
        total_packages = sum(len(packages) for packages in grouped.values())

        # Estimate space (rough estimate: 1MB per package)
        # In real implementation, we'd get actual sizes from aptly
        estimated_space_mb = len(to_remove) * 1

        result = {
            "analyzed": total_packages,
            "to_remove": len(to_remove),
            "removed": 0,
            "space_mb": estimated_space_mb,
            "packages": [pkg.full_ref for pkg in to_remove],
        }

        # Actually remove if not dry_run
        if not dry_run and to_remove:
            self.logger.info(f"Removing {len(to_remove)} packages...")
            package_refs = [pkg.full_ref for pkg in to_remove]

            try:
                self.aptly.remove_packages(
                    codename, component, package_refs, dry_run=False
                )
                result["removed"] = len(to_remove)
                self.logger.info(f"Successfully removed {len(to_remove)} packages")
            except Exception as e:
                self.logger.error(f"Failed to remove packages: {e}")
                raise
        elif dry_run:
            self.logger.info(
                f"[DRY RUN] Would remove {len(to_remove)} packages: "
                f"{[pkg.full_ref for pkg in to_remove[:5]]}..."
            )

        return result
