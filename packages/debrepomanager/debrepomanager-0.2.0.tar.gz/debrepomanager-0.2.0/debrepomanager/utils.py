"""Utility functions for Debian Repository Manager.

This module provides helper functions for logging, package metadata parsing,
version comparison, and file operations.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from debian.debfile import DebFile


@dataclass
class PackageInfo:
    """Information about a Debian package.

    Attributes:
        name: Package name
        version: Package version
        architecture: Package architecture (amd64, arm64, etc.)
        file_path: Path to .deb file
        modification_time: File modification timestamp
    """

    name: str
    version: str
    architecture: str
    file_path: str
    modification_time: datetime


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
        log_format: Optional logging format string

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging("DEBUG", "/var/log/debrepomanager.log")
        >>> logger.info("Logging configured")
    """
    logger = logging.getLogger("debrepomanager")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Default format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def parse_deb_metadata(deb_path: str) -> PackageInfo:
    """Extract metadata from .deb file.

    Args:
        deb_path: Path to .deb file

    Returns:
        PackageInfo object with package metadata

    Raises:
        FileNotFoundError: If .deb file doesn't exist
        ValueError: If file is not a valid .deb package

    Example:
        >>> info = parse_deb_metadata("package_1.0_amd64.deb")
        >>> print(info.name, info.version)
    """
    path = Path(deb_path)

    if not path.exists():
        raise FileNotFoundError(f"Package file not found: {deb_path}")

    if not path.is_file():
        raise ValueError(f"Not a file: {deb_path}")

    try:
        with DebFile(str(path)) as deb:
            control = deb.debcontrol()

            name = control.get("Package", "")
            version = control.get("Version", "")
            architecture = control.get("Architecture", "")

            if not name or not version:
                raise ValueError(
                    f"Invalid .deb file (missing Package or Version): {deb_path}"
                )

            # Get file modification time
            stat = path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)

            return PackageInfo(
                name=name,
                version=version,
                architecture=architecture,
                file_path=str(path.absolute()),
                modification_time=mtime,
            )

    except Exception as e:
        if isinstance(e, (FileNotFoundError, ValueError)):
            raise
        raise ValueError(f"Failed to parse .deb file {deb_path}: {e}")


def compare_versions(version1: str, version2: str) -> int:
    """Compare Debian package versions.

    Uses Debian version comparison rules (apt_pkg).

    Args:
        version1: First version string
        version2: Second version string

    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2

    Example:
        >>> compare_versions("1.0", "2.0")
        -1
        >>> compare_versions("2.0", "1.0")
        1
        >>> compare_versions("1.0", "1.0")
        0
    """
    try:
        import apt_pkg

        apt_pkg.init_system()
        return int(apt_pkg.version_compare(version1, version2))
    except ImportError:
        # Fallback to simple string comparison if apt_pkg not available
        # This is not accurate but better than nothing
        logging.getLogger(__name__).warning(
            "apt_pkg not available, using simple comparison"
        )
        if version1 < version2:
            return -1
        elif version1 > version2:
            return 1
        else:
            return 0


def find_deb_files(directory: str, recursive: bool = True) -> List[str]:
    """Find all .deb files in directory.

    Args:
        directory: Directory path to search
        recursive: If True, search recursively in subdirectories

    Returns:
        List of absolute paths to .deb files

    Raises:
        FileNotFoundError: If directory doesn't exist
        ValueError: If path is not a directory

    Example:
        >>> files = find_deb_files("/path/to/packages")
        >>> print(f"Found {len(files)} packages")
    """
    path = Path(directory)

    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not path.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    pattern = "**/*.deb" if recursive else "*.deb"
    deb_files = [str(p.absolute()) for p in path.glob(pattern) if p.is_file()]

    return sorted(deb_files)


def get_package_age(deb_path: str) -> int:
    """Get package age in days based on modification time.

    Args:
        deb_path: Path to .deb file

    Returns:
        Age in days (integer)

    Raises:
        FileNotFoundError: If file doesn't exist

    Example:
        >>> age = get_package_age("package.deb")
        >>> if age > 90:
        ...     print("Old package")
    """
    path = Path(deb_path)

    if not path.exists():
        raise FileNotFoundError(f"Package file not found: {deb_path}")

    stat = path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime)
    age = (datetime.now() - mtime).days

    return age
