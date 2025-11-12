"""Tests for config v0.2 features (auto-detection, ENV variables)."""

import os
from pathlib import Path

from debrepomanager.config import Config


class TestConfigAutoDetection:
    """Tests for config auto-detection (v0.2+)."""

    def test_find_config_file_no_configs(self, mocker):
        """Test _find_config_file when no configs exist."""
        # Mock all paths to not exist
        mocker.patch.object(Path, "exists", return_value=False)

        config = Config()
        result = config._find_config_file()

        assert result is None

    def test_load_config_chain_with_temp_files(self, tmp_path, mocker):
        """Test _load_config_chain loads configs in order."""
        # Create temp config
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(
            """
gpg:
  key_id: TEST_KEY
aptly:
  root_base: /srv/aptly
  publish_base: /srv/repo
"""
        )

        # Mock cwd to return tmp_path
        mocker.patch("pathlib.Path.cwd", return_value=tmp_path)

        # Load with explicit path (skips chain)
        config = Config(str(config_file))

        assert config.gpg_key_id == "TEST_KEY"

    def test_apply_env_overrides_string_values(self, mocker):
        """Test _apply_env_overrides with string values."""
        # Set ENV before creating config
        mocker.patch.dict(
            os.environ,
            {
                "REPOMANAGER_APTLY_ROOT_BASE": "/custom/path",
                "REPOMANAGER_GPG_KEY_ID": "ENVKEY123",
            },
            clear=False,
        )

        config = Config()
        # ENV overrides should be applied

        assert config.aptly_root_base == "/custom/path"
        assert config.gpg_key_id == "ENVKEY123"

    def test_apply_env_overrides_boolean_true(self, mocker):
        """Test _apply_env_overrides boolean parsing - true values."""
        for true_value in ["true", "1", "yes"]:
            mocker.patch.dict(
                os.environ, {"REPOMANAGER_GPG_USE_AGENT": true_value}, clear=False
            )

            config = Config()

            assert config.gpg_use_agent is True, f"Failed for value: {true_value}"

    def test_apply_env_overrides_boolean_false(self, mocker):
        """Test _apply_env_overrides boolean parsing - false values."""
        for false_value in ["false", "0", "no"]:
            mocker.patch.dict(
                os.environ, {"REPOMANAGER_GPG_USE_AGENT": false_value}, clear=False
            )

            config = Config()

            assert config.gpg_use_agent is False, f"Failed for value: {false_value}"

    def test_init_explicit_path_provided(self, tmp_path):
        """Test Config with explicit path doesn't use auto-detection."""
        config_file = tmp_path / "my_config.yaml"
        config_file.write_text(
            """
gpg:
  key_id: EXPLICIT_KEY
aptly:
  root_base: /srv/aptly
  publish_base: /srv/repo
"""
        )

        config = Config(str(config_file))

        assert config.gpg_key_id == "EXPLICIT_KEY"

    def test_init_no_path_uses_defaults(self):
        """Test Config() without path uses defaults."""
        config = Config()

        # Should have default values
        assert config.aptly_root_base == "/srv/aptly"
        assert config.publish_base == "/srv/repo/public"

    def test_find_config_file_checks_all_paths(self, tmp_path, mocker):
        """Test _find_config_file checks all standard locations."""
        # Create local config
        local_config = tmp_path / "repomanager.yaml"
        local_config.write_text("gpg:\n  key_id: LOCAL")

        # Mock cwd to return tmp_path
        mocker.patch("pathlib.Path.cwd", return_value=tmp_path)

        config = Config()
        result = config._find_config_file()

        # Should find local config
        assert result == str(local_config)

    def test_load_config_chain_handles_yaml_errors(self, tmp_path, mocker):
        """Test _load_config_chain handles YAML errors gracefully."""
        # Create invalid YAML file
        bad_config = tmp_path / "repomanager.yaml"
        bad_config.write_text("{ invalid yaml ")

        # Mock cwd to return tmp_path
        mocker.patch("pathlib.Path.cwd", return_value=tmp_path)

        # Should not crash, just log warning and use defaults
        config = Config()

        # Should still have defaults (error was logged but not raised)
        assert config.aptly_root_base == "/srv/aptly"

    def test_load_config_chain_handles_permission_errors(self, tmp_path, mocker):
        """Test _load_config_chain handles permission errors gracefully."""
        # Create config file
        config_file = tmp_path / "repomanager.yaml"
        config_file.write_text("gpg:\n  key_id: TEST")
        config_file.chmod(0o000)  # No permissions

        # Mock cwd to return tmp_path
        mocker.patch("pathlib.Path.cwd", return_value=tmp_path)

        try:
            # Should not crash, just log warning
            config = Config()

            # Should still have defaults
            assert config.aptly_root_base == "/srv/aptly"
        finally:
            # Restore permissions for cleanup
            config_file.chmod(0o644)

    def test_apply_env_overrides_partial(self, mocker):
        """Test _apply_env_overrides with only some variables set."""
        # Set only one ENV variable
        mocker.patch.dict(
            os.environ,
            {"REPOMANAGER_APTLY_ROOT_BASE": "/only/this"},
            clear=False,
        )

        config = Config()

        # Only root_base should be overridden
        assert config.aptly_root_base == "/only/this"
        # Others should be defaults
        assert config.publish_base == "/srv/repo/public"
