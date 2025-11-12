"""Configuration management for Debian Repository Manager.

This module handles loading and merging configuration from YAML files,
with support for multi-level config hierarchy and environment variables.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Configuration related errors."""


class Config:
    """Configuration manager for debrepomanager.

    Loads configuration from YAML files with priority chain:
    1. /etc/repomanager/config.yaml (system-wide, lowest priority)
    2. ~/.repomanager/config.yaml (user-level)
    3. ./repomanager.yaml (local directory)
    4. Environment variables REPOMANAGER_* (highest priority)

    Attributes:
        _config: Internal configuration dictionary

    Example:
        >>> config = Config()  # Auto-detects config files
        >>> aptly_root = config.get_aptly_root("bookworm")
        >>> config = Config("/path/to/config.yaml")  # Explicit path
    """

    DEFAULT_CONFIG: Dict[str, Any] = {
        "aptly": {
            "root_base": "/srv/aptly",
            "publish_base": "/srv/repo/public",
            "aptly_path": "aptly",
        },
        "gpg": {
            "key_id": "",
            "use_agent": True,
            "gpg_path": "gpg",
        },
        "retention": {
            "default": {
                "min_versions": 5,
                "max_age_days": 90,
            },
            "overrides": {},
        },
        "repositories": {
            # Note: codenames and components are created dynamically
            # No need to list them in config
            "architectures": ["amd64", "arm64", "riscv64"],
            "auto_create": True,
            "dual_format": {
                "enabled": True,
                "method": "symlink",
                "auto_symlink": True,
            },
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "advanced": {
            "max_snapshots": 10,
            "snapshot_format": "{component}-{codename}-%Y%m%d-%H%M%S%f",
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration with priority chain.

        Config loading priority (low to high):
        1. /etc/repomanager/config.yaml
        2. ~/.repomanager/config.yaml
        3. ./repomanager.yaml
        4. Explicit config_path (if provided)
        5. Environment variables REPOMANAGER_*

        Args:
            config_path: Optional explicit path to config file.
                        If not provided, uses auto-detection.
        """
        self._config: Dict[str, Any] = {}
        self.load_default()

        if config_path:
            # Explicit config path provided - load only this one
            self.load(config_path)
        else:
            # Auto-detect and load configs in priority order
            self._load_config_chain()

        # Apply environment variable overrides (highest priority)
        self._apply_env_overrides()

    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations.

        Checks in order:
        1. /etc/repomanager/config.yaml
        2. ~/.repomanager/config.yaml
        3. ./repomanager.yaml

        Returns:
            Path to first found config file, or None
        """
        search_paths = [
            Path("/etc/repomanager/config.yaml"),
            Path.home() / ".repomanager" / "config.yaml",
            Path.cwd() / "repomanager.yaml",
        ]

        for path in search_paths:
            if path.exists():
                logger.debug(f"Found config file: {path}")
                return str(path)

        logger.debug("No config file found in standard locations")
        return None

    def _load_config_chain(self) -> None:
        """Load and merge configs from all standard locations.

        Loads configs in priority order (each overrides previous):
        1. /etc/repomanager/config.yaml
        2. ~/.repomanager/config.yaml
        3. ./repomanager.yaml
        """
        config_paths = [
            Path("/etc/repomanager/config.yaml"),
            Path.home() / ".repomanager" / "config.yaml",
            Path.cwd() / "repomanager.yaml",
        ]

        for path in config_paths:
            if path.exists():
                try:
                    self.load(str(path), merge=True)
                    logger.info(f"Loaded config from {path}")
                except Exception as e:
                    logger.warning(f"Failed to load config from {path}: {e}")

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration.

        Supported environment variables:
        - REPOMANAGER_APTLY_ROOT_BASE
        - REPOMANAGER_APTLY_PUBLISH_BASE
        - REPOMANAGER_GPG_KEY_ID
        - REPOMANAGER_GPG_USE_AGENT
        """
        env_mappings = {
            "REPOMANAGER_APTLY_ROOT_BASE": ("aptly", "root_base"),
            "REPOMANAGER_APTLY_PUBLISH_BASE": ("aptly", "publish_base"),
            "REPOMANAGER_GPG_KEY_ID": ("gpg", "key_id"),
            "REPOMANAGER_GPG_USE_AGENT": ("gpg", "use_agent"),
        }

        for env_var, (section, key) in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                # Handle boolean conversion for use_agent
                if key == "use_agent":
                    final_value: Any = env_value.lower() in ("true", "1", "yes")
                else:
                    final_value = env_value

                self._config[section][key] = final_value
                logger.debug(f"Applied env override: {env_var} = {final_value}")

    def load_default(self) -> None:
        """Load default configuration."""
        self._config = self._deep_copy_dict(self.DEFAULT_CONFIG)
        logger.debug("Loaded default configuration")

    def load(self, config_path: str, merge: bool = False) -> None:
        """Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file
            merge: If True, merge with existing config. If False, replace.

        Raises:
            ConfigError: If file not found or invalid YAML
        """
        path = Path(config_path)

        if not path.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")

        try:
            with path.open("r") as f:
                loaded_config = yaml.safe_load(f)

            if loaded_config is None:
                loaded_config = {}

            if merge:
                self._merge_dict(self._config, loaded_config)
                logger.debug(f"Merged configuration from {config_path}")
            else:
                self._config = loaded_config
                logger.debug(f"Loaded configuration from {config_path}")

        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in {config_path}: {e}")
        except PermissionError:
            raise ConfigError(f"Permission denied reading {config_path}")

    def _deep_copy_dict(self, d: Dict) -> Dict:
        """Deep copy a dictionary."""
        import copy

        return copy.deepcopy(d)

    def _merge_dict(self, base: Dict, override: Dict) -> None:
        """Recursively merge override dict into base dict.

        Args:
            base: Base dictionary (modified in place)
            override: Override dictionary
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dict(base[key], value)
            else:
                base[key] = value

    # Property accessors for main config sections

    @property
    def aptly_root_base(self) -> str:
        """Get aptly root base directory."""
        return str(self._config["aptly"]["root_base"])

    @property
    def publish_base(self) -> str:
        """Get publish base directory."""
        return str(self._config["aptly"]["publish_base"])

    @property
    def aptly_path(self) -> str:
        """Get path to aptly binary."""
        return str(self._config["aptly"].get("aptly_path", "aptly"))

    @property
    def gpg_key_id(self) -> str:
        """Get GPG key ID."""
        key_id = self._config["gpg"]["key_id"]
        if not key_id:
            raise ConfigError("GPG key_id not configured")
        return str(key_id)

    @property
    def gpg_use_agent(self) -> bool:
        """Check if gpg-agent should be used."""
        return bool(self._config["gpg"].get("use_agent", True))

    @property
    def gpg_path(self) -> str:
        """Get path to gpg binary."""
        return str(self._config["gpg"].get("gpg_path", "gpg"))

    def get_aptly_root(self, codename: str) -> str:
        """Get aptly root directory for specific codename.

        Args:
            codename: Distribution codename (e.g., 'bookworm')

        Returns:
            Path to aptly root for this codename
        """
        return str(Path(self.aptly_root_base) / codename)

    def get_architectures(self) -> List[str]:
        """Get list of supported architectures.

        Returns:
            List of architectures (e.g., ['amd64', 'arm64', 'riscv64'])
        """
        return list(self._config["repositories"]["architectures"])

    @property
    def auto_create_repos(self) -> bool:
        """Check if repositories should be auto-created.

        Returns:
            True if auto-create is enabled
        """
        return bool(self._config["repositories"].get("auto_create", True))

    @property
    def dual_format_enabled(self) -> bool:
        """Check if dual format support is enabled.

        Returns:
            True if dual format (old + new URL) is enabled
        """
        dual_format = self._config["repositories"].get("dual_format", {})
        return bool(dual_format.get("enabled", True))

    @property
    def dual_format_method(self) -> str:
        """Get dual format implementation method.

        Returns:
            Method name: 'symlink', 'nginx', or 'dual_publish'
        """
        dual_format = self._config["repositories"].get("dual_format", {})
        return str(dual_format.get("method", "symlink"))

    @property
    def dual_format_auto_symlink(self) -> bool:
        """Check if symlinks should be created automatically.

        Returns:
            True if auto-symlink is enabled
        """
        dual_format = self._config["repositories"].get("dual_format", {})
        return bool(dual_format.get("auto_symlink", True))

    @property
    def logging_level(self) -> str:
        """Get logging level.

        Returns:
            Logging level string (DEBUG, INFO, WARNING, ERROR)
        """
        return str(self._config["logging"].get("level", "INFO"))

    @property
    def logging_format(self) -> str:
        """Get logging format string.

        Returns:
            Python logging format string
        """
        return str(
            self._config["logging"].get(
                "format", "%(asctime)s - %(levelname)s - %(message)s"
            )
        )

    @property
    def max_snapshots(self) -> int:
        """Get maximum number of snapshots to keep.

        Returns:
            Maximum snapshots count
        """
        return int(self._config["advanced"].get("max_snapshots", 10))

    @property
    def snapshot_format(self) -> str:
        """Get snapshot naming format.

        Returns:
            Snapshot format string with placeholders
        """
        return str(
            self._config["advanced"].get(
                "snapshot_format", "{component}-{codename}-%Y%m%d-%H%M%S"
            )
        )

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ConfigError: If configuration is invalid
        """
        # Check required sections
        required_sections = ["aptly", "gpg", "repositories"]
        for section in required_sections:
            if section not in self._config:
                raise ConfigError(f"Missing required section: {section}")

        # Validate aptly paths
        aptly_root = Path(self.aptly_root_base)
        if not aptly_root.is_absolute():
            raise ConfigError(f"aptly.root_base must be absolute path: {aptly_root}")

        publish_base = Path(self.publish_base)
        if not publish_base.is_absolute():
            raise ConfigError(
                f"aptly.publish_base must be absolute path: {publish_base}"
            )

        # Validate GPG key_id is set
        if not self._config["gpg"]["key_id"]:
            logger.warning("GPG key_id not configured - signing will fail")

        # Validate architectures is a list (if present)
        repos = self._config["repositories"]
        if "architectures" in repos and not isinstance(repos["architectures"], list):
            raise ConfigError("repositories.architectures must be a list")

        logger.debug("Configuration validation passed")
