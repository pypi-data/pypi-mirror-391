"""
Debian Repository Manager (debrepomanager)

A system for managing Debian-like repositories with support for multiple
distributions, architectures, and components.
"""

__version__ = "0.3.0"
__author__ = "Viacheslav Bocharov"
__email__ = "vb@jethome.com"

# Phase 1: Aptly Base ✅
from debrepomanager.aptly import AptlyError, AptlyManager

# Note: Imports added as modules are implemented
# Phase 1: Config ✅
from debrepomanager.config import Config, ConfigError

# Phase 4: GPG ✅
from debrepomanager.gpg import GPGError, GPGManager

# Phase 9: GPG Rotation ✅
from debrepomanager.gpg_rotation import GPGRotationError, GPGRotationManager

# v0.2: Metadata ✅
from debrepomanager.metadata import MetadataError, MetadataManager

# Phase 1: Utils ✅
from debrepomanager.utils import (
    PackageInfo,
    compare_versions,
    find_deb_files,
    get_package_age,
    parse_deb_metadata,
    setup_logging,
)

# Phase 8: Retention (not in MVP)
# from debrepomanager.retention import RetentionPolicy

__all__ = [
    "Config",
    "ConfigError",
    "AptlyManager",
    "AptlyError",
    "GPGManager",
    "GPGError",
    "GPGRotationManager",
    "GPGRotationError",
    "MetadataManager",
    "MetadataError",
    "PackageInfo",
    "setup_logging",
    "parse_deb_metadata",
    "compare_versions",
    "find_deb_files",
    "get_package_age",
    "__version__",
]
