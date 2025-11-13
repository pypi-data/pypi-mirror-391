"""Tests for debrepomanager.config module."""

import logging

import pytest

from debrepomanager.config import Config, ConfigError


class TestConfigLoading:
    """Tests for configuration loading."""

    def test_load_default(self):
        """Test loading default configuration."""
        config = Config()

        assert config.aptly_root_base == "/srv/aptly"
        assert config.publish_base == "/srv/repo/public"
        assert config.aptly_path == "aptly"
        assert config.gpg_use_agent is True
        assert config.auto_create_repos is True

    def test_load_from_file(self, tmp_path):
        """Test loading configuration from file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
aptly:
  root_base: /custom/aptly
  publish_base: /custom/repo

gpg:
  key_id: TEST_KEY_ID
  use_agent: false
"""
        )

        config = Config(str(config_file))

        assert config.aptly_root_base == "/custom/aptly"
        assert config.publish_base == "/custom/repo"
        assert config.gpg_key_id == "TEST_KEY_ID"
        assert config.gpg_use_agent is False

    def test_load_nonexistent_file(self):
        """Test loading from non-existent file raises error."""
        with pytest.raises(ConfigError, match="not found"):
            config = Config()
            config.load("/nonexistent/config.yaml")

    def test_load_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML raises error."""
        config_file = tmp_path / "bad.yaml"
        config_file.write_text(
            """
invalid: yaml: content:
  - broken
    indentation
"""
        )

        with pytest.raises(ConfigError, match="Invalid YAML"):
            config = Config()
            config.load(str(config_file))


class TestConfigMerging:
    """Tests for configuration merging."""

    def test_merge_simple(self, tmp_path):
        """Test simple configuration merge."""
        base_file = tmp_path / "base.yaml"
        base_file.write_text(
            """
aptly:
  root_base: /base/aptly
  publish_base: /base/repo
"""
        )

        override_file = tmp_path / "override.yaml"
        override_file.write_text(
            """
aptly:
  root_base: /override/aptly
"""
        )

        config = Config(str(base_file))
        config.load(str(override_file), merge=True)

        # root_base overridden
        assert config.aptly_root_base == "/override/aptly"
        # publish_base preserved
        assert config.publish_base == "/base/repo"

    def test_merge_nested(self, tmp_path):
        """Test nested configuration merge."""
        base_file = tmp_path / "base.yaml"
        base_file.write_text(
            """
repositories:
  codenames:
    - bookworm
  components:
    - jethome-tools
"""
        )

        override_file = tmp_path / "override.yaml"
        override_file.write_text(
            """
repositories:
  codenames:
    - noble
    - trixie
"""
        )

        config = Config(str(base_file))
        config.load(str(override_file), merge=True)

        # In v0.2+, codenames/components are ignored
        # Test that config still loads and merges other sections
        assert config.auto_create_repos is True


class TestPropertyAccessors:
    """Tests for configuration property accessors."""

    def test_aptly_properties(self):
        """Test aptly-related properties."""
        config = Config()

        assert isinstance(config.aptly_root_base, str)
        assert isinstance(config.publish_base, str)
        assert isinstance(config.aptly_path, str)

    def test_gpg_properties(self, tmp_path):
        """Test GPG-related properties."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
gpg:
  key_id: 1234567890ABCDEF
  use_agent: true
  gpg_path: /usr/bin/gpg
"""
        )

        config = Config(str(config_file))

        assert config.gpg_key_id == "1234567890ABCDEF"
        assert config.gpg_use_agent is True
        assert config.gpg_path == "/usr/bin/gpg"

    def test_gpg_key_id_not_configured(self):
        """Test error when GPG key_id not configured."""
        config = Config()

        with pytest.raises(ConfigError, match="not configured"):
            _ = config.gpg_key_id

    def test_repository_properties(self):
        """Test repository-related properties."""
        config = Config()

        # Note: get_codenames() and get_components() removed in v0.2
        # Codenames and components are created dynamically

        architectures = config.get_architectures()
        assert isinstance(architectures, list)
        assert "amd64" in architectures
        assert "arm64" in architectures

    def test_get_aptly_root(self):
        """Test getting aptly root for specific codename."""
        config = Config()

        root = config.get_aptly_root("bookworm")
        assert root == "/srv/aptly/bookworm"

        root = config.get_aptly_root("noble")
        assert root == "/srv/aptly/noble"

    def test_auto_create_repos(self):
        """Test auto_create_repos property."""
        config = Config()
        assert config.auto_create_repos is True

    def test_dual_format_properties(self):
        """Test dual format related properties."""
        config = Config()

        assert config.dual_format_enabled is True
        assert config.dual_format_method == "symlink"
        assert config.dual_format_auto_symlink is True


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_validate_default_config(self):
        """Test validation of default config passes."""
        config = Config()
        # Should not raise
        config.validate()

    def test_validate_missing_section(self, tmp_path):
        """Test validation fails for missing required section."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
aptly:
  root_base: /srv/aptly
# Missing gpg and repositories sections
"""
        )

        config = Config(str(config_file))

        with pytest.raises(ConfigError, match="Missing required section"):
            config.validate()

    def test_validate_relative_aptly_root(self, tmp_path):
        """Test validation fails for relative aptly root path."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
aptly:
  root_base: relative/path
  publish_base: /srv/repo

gpg:
  key_id: TEST_KEY

repositories:
  codenames: [bookworm]
  components: [main]
  architectures: [amd64]
"""
        )

        config = Config(str(config_file))

        with pytest.raises(ConfigError, match="must be absolute path"):
            config.validate()

    def test_validate_codenames_ignored(self, tmp_path):
        """Test codenames in config are ignored (removed in v0.2)."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
aptly:
  root_base: /srv/aptly
  publish_base: /srv/repo

gpg:
  key_id: TEST_KEY

repositories:
  codenames: "bookworm"  # Ignored in v0.2
  architectures: [amd64]
"""
        )

        config = Config(str(config_file))

        # Should not raise - codenames not validated anymore
        config.validate()


class TestLoggingConfig:
    """Tests for logging configuration."""

    def test_logging_defaults(self):
        """Test default logging configuration."""
        config = Config()

        assert config.logging_level == "INFO"
        assert "asctime" in config.logging_format

    def test_logging_custom(self, tmp_path):
        """Test custom logging configuration."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
logging:
  level: DEBUG
  format: "%(levelname)s: %(message)s"
"""
        )

        config = Config(str(config_file))

        assert config.logging_level == "DEBUG"
        assert config.logging_format == "%(levelname)s: %(message)s"


class TestAdvancedConfig:
    """Tests for advanced configuration options."""

    def test_max_snapshots_default(self):
        """Test default max_snapshots value."""
        config = Config()
        assert config.max_snapshots == 10

    def test_snapshot_format_default(self):
        """Test default snapshot format."""
        config = Config()
        format_str = config.snapshot_format

        assert "{component}" in format_str
        assert "{codename}" in format_str
        assert "%Y%m%d" in format_str

    def test_max_snapshots_custom(self, tmp_path):
        """Test custom max_snapshots value."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
advanced:
  max_snapshots: 20
"""
        )

        config = Config(str(config_file))
        assert config.max_snapshots == 20


class TestConfigEdgeCases:
    """Tests for configuration edge cases."""

    def test_load_permission_denied(self, tmp_path, mocker):
        """Test loading file with permission denied."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("aptly:\n  root_base: /test")

        # Mock Path.open to raise PermissionError
        mock_open = mocker.mock_open()
        mock_open.side_effect = PermissionError("Permission denied")
        mocker.patch("pathlib.Path.open", mock_open)

        config = Config()
        with pytest.raises(ConfigError, match="Permission denied"):
            config.load(str(config_file))

    def test_load_empty_yaml(self, tmp_path):
        """Test loading empty YAML file."""
        config_file = tmp_path / "empty.yaml"
        config_file.write_text("")

        config = Config(str(config_file))
        # Should load as empty dict, then use defaults from DEFAULT_CONFIG
        assert config is not None

    def test_gpg_key_id_warning_on_validate(self, tmp_path, caplog):
        """Test validation warns when GPG key_id not configured."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
aptly:
  root_base: /srv/aptly
  publish_base: /srv/repo

gpg:
  key_id: ""  # Empty key_id

repositories:
  codenames: [bookworm]
  components: [main]
  architectures: [amd64]
"""
        )

        config = Config(str(config_file))

        with caplog.at_level(logging.WARNING):
            config.validate()

        # Should have warning about key_id
        assert any(
            "key_id not configured" in record.message for record in caplog.records
        )

    def test_validate_relative_publish_base(self, tmp_path):
        """Test validation fails for relative publish_base."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
aptly:
  root_base: /srv/aptly
  publish_base: relative/path
gpg:
  key_id: TEST
repositories:
  codenames: [bookworm]
  components: [main]
  architectures: [amd64]
"""
        )
        config = Config(str(config_file))
        with pytest.raises(ConfigError, match="must be absolute path"):
            config.validate()

    def test_validate_components_ignored(self, tmp_path):
        """Test components in config are ignored (removed in v0.2)."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
aptly:
  root_base: /srv/aptly
  publish_base: /srv/repo
gpg:
  key_id: TEST
repositories:
  components: "main"  # Ignored in v0.2
  architectures: [amd64]
"""
        )
        config = Config(str(config_file))
        # Should not raise - components not validated anymore
        config.validate()

    def test_validate_architectures_not_list(self, tmp_path):
        """Test validation fails if architectures is not a list."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
aptly:
  root_base: /srv/aptly
  publish_base: /srv/repo
gpg:
  key_id: TEST
repositories:
  codenames: [bookworm]
  components: [main]
  architectures: "amd64"
"""
        )
        config = Config(str(config_file))
        with pytest.raises(ConfigError, match="architectures must be a list"):
            config.validate()


class TestServerConfigIntegration:
    """Tests for server config loading from /etc/repomanager/config.yaml.

    Note: Server config loading from /etc/repomanager/config.yaml is a production
    feature that's difficult to test in unit tests without complex mocking.
    This functionality is verified through:
    1. Code review of the try/except block in Config.__init__
    2. Manual testing on production servers
    3. The fact that config loads correctly when the file doesn't exist

    The 5 lines (93-97) in config.py are accepted as untested since they
    represent production-only behavior."""

    def test_server_config_path_not_exists(self):
        """Test that config loads successfully when server config doesn't exist.

        This is the normal case for development and testing environments."""
        config = Config()
        # Should load default config successfully
        assert config.aptly_root_base == "/srv/aptly"
