"""Tests for debrepomanager.gpg module."""

import subprocess

import pytest

from debrepomanager.config import Config
from debrepomanager.gpg import GPGError, GPGManager


@pytest.fixture
def config(tmp_path):
    """Create test configuration."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
gpg:
  key_id: TEST_KEY_1234567890ABCDEF
  use_agent: true
  gpg_path: gpg

aptly:
  root_base: /srv/aptly
  publish_base: /srv/repo

repositories:
  codenames: [bookworm]
  components: [main]
  architectures: [amd64]
"""
    )
    return Config(str(config_file))


@pytest.fixture
def gpg_manager(config):
    """Create GPGManager instance."""
    return GPGManager(config)


class TestCheckKeyAvailable:
    """Tests for GPG key availability check."""

    def test_check_key_available_success(self, gpg_manager, mocker):
        """Test checking available key."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(
            returncode=0, stdout="sec   rsa2048/TEST_KEY", stderr=""
        )

        result = gpg_manager.check_key_available()

        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "gpg" in args
        assert "--list-secret-keys" in args

    def test_check_key_available_not_found(self, gpg_manager, mocker):
        """Test checking non-existent key."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=2, stdout="", stderr="not found")

        result = gpg_manager.check_key_available()

        assert result is False

    def test_check_key_available_with_specific_id(self, gpg_manager, mocker):
        """Test checking specific key ID."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        result = gpg_manager.check_key_available("CUSTOM_KEY_ID")

        assert result is True
        args = mock_run.call_args[0][0]
        assert "CUSTOM_KEY_ID" in args

    def test_check_key_available_timeout(self, gpg_manager, mocker):
        """Test checking key handles timeout."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.TimeoutExpired(["gpg"], 10)

        result = gpg_manager.check_key_available()

        assert result is False

    def test_check_key_available_gpg_not_found(self, gpg_manager, mocker):
        """Test checking key when GPG binary not found."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = FileNotFoundError("gpg not found")

        result = gpg_manager.check_key_available()

        assert result is False

    def test_check_key_no_config(self, gpg_manager, mocker):
        """Test checking key when key_id not in config."""
        # Set empty key_id in config dict to trigger exception
        gpg_manager.config._config["gpg"]["key_id"] = ""

        result = gpg_manager.check_key_available()

        # Should return False when key_id raises ConfigError
        assert result is False


class TestGetPassphrase:
    """Tests for passphrase handling."""

    def test_get_passphrase_with_agent(self, gpg_manager):
        """Test get_passphrase returns None when using gpg-agent."""
        # Config has use_agent: true by default
        passphrase = gpg_manager.get_passphrase()

        assert passphrase is None

    def test_get_passphrase_without_agent(self, gpg_manager, mocker):
        """Test get_passphrase prompts user when not using agent."""
        # Disable agent
        gpg_manager.config._config["gpg"]["use_agent"] = False

        mock_getpass = mocker.patch("getpass.getpass", return_value="secret123")

        passphrase = gpg_manager.get_passphrase()

        assert passphrase == "secret123"
        mock_getpass.assert_called_once()

    def test_get_passphrase_cached(self, gpg_manager, mocker):
        """Test get_passphrase uses cached value."""
        gpg_manager.config._config["gpg"]["use_agent"] = False
        gpg_manager._passphrase_cache = "cached_secret"

        mock_getpass = mocker.patch("getpass.getpass")

        passphrase = gpg_manager.get_passphrase()

        assert passphrase == "cached_secret"
        mock_getpass.assert_not_called()

    def test_get_passphrase_force_prompt(self, gpg_manager, mocker):
        """Test get_passphrase with force prompts even if cached."""
        gpg_manager.config._config["gpg"]["use_agent"] = False
        gpg_manager._passphrase_cache = "old_secret"

        mock_getpass = mocker.patch("getpass.getpass", return_value="new_secret")

        passphrase = gpg_manager.get_passphrase(force=True)

        assert passphrase == "new_secret"
        mock_getpass.assert_called_once()

    def test_get_passphrase_keyboard_interrupt(self, gpg_manager, mocker):
        """Test get_passphrase handles keyboard interrupt."""
        gpg_manager.config._config["gpg"]["use_agent"] = False

        mocker.patch("getpass.getpass", side_effect=KeyboardInterrupt())

        with pytest.raises(GPGError, match="cancelled"):
            gpg_manager.get_passphrase()

    def test_get_passphrase_eof_error(self, gpg_manager, mocker):
        """Test get_passphrase handles EOF."""
        gpg_manager.config._config["gpg"]["use_agent"] = False

        mocker.patch("getpass.getpass", side_effect=EOFError())

        with pytest.raises(GPGError, match="cancelled"):
            gpg_manager.get_passphrase()


class TestTestSigning:
    """Tests for GPG signing test."""

    def test_test_signing_key_not_available(self, gpg_manager, mocker):
        """Test signing fails when key not available."""
        mocker.patch.object(gpg_manager, "check_key_available", return_value=False)

        with pytest.raises(GPGError, match="not found in keyring"):
            gpg_manager.test_signing()

    def test_test_signing_success(self, gpg_manager, mocker):
        """Test successful signing."""
        mocker.patch.object(gpg_manager, "check_key_available", return_value=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(
            returncode=0,
            stdout=b"-----BEGIN PGP SIGNATURE-----\ntest\n-----END PGP SIGNATURE-----",
            stderr=b"",
        )

        result = gpg_manager.test_signing()

        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "--default-key" in args
        assert gpg_manager.config.gpg_key_id in args
        assert "--detach-sign" in args

    def test_test_signing_with_agent(self, gpg_manager, mocker):
        """Test signing with gpg-agent uses --batch."""
        mocker.patch.object(gpg_manager, "check_key_available", return_value=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(
            returncode=0,
            stdout=b"-----BEGIN PGP SIGNATURE-----\ntest\n-----END PGP SIGNATURE-----",
            stderr=b"",
        )

        gpg_manager.test_signing()

        args = mock_run.call_args[0][0]
        assert "--batch" in args

    def test_test_signing_failure(self, gpg_manager, mocker):
        """Test signing failure handling."""
        mocker.patch.object(gpg_manager, "check_key_available", return_value=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            2, ["gpg"], stderr=b"signing failed"
        )

        with pytest.raises(GPGError, match="signing failed"):
            gpg_manager.test_signing()

    def test_test_signing_timeout(self, gpg_manager, mocker):
        """Test signing handles timeout."""
        mocker.patch.object(gpg_manager, "check_key_available", return_value=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.TimeoutExpired(["gpg"], 30)

        with pytest.raises(GPGError, match="timed out"):
            gpg_manager.test_signing()

    def test_test_signing_gpg_not_found(self, gpg_manager, mocker):
        """Test signing handles GPG binary not found."""
        mocker.patch.object(gpg_manager, "check_key_available", return_value=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = FileNotFoundError("gpg not found")

        with pytest.raises(GPGError, match="not found"):
            gpg_manager.test_signing()

    def test_test_signing_no_signature_in_output(self, gpg_manager, mocker):
        """Test signing fails when no signature in output."""
        mocker.patch.object(gpg_manager, "check_key_available", return_value=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(
            returncode=0, stdout=b"No signature here", stderr=b""
        )

        with pytest.raises(GPGError, match="No signature"):
            gpg_manager.test_signing()


class TestConfigureForAptly:
    """Tests for aptly configuration."""

    def test_configure_for_aptly(self, gpg_manager):
        """Test getting aptly GPG configuration."""
        config = gpg_manager.configure_for_aptly()

        assert isinstance(config, dict)
        assert "gpg_key" in config
        assert config["gpg_key"] == gpg_manager.config.gpg_key_id
        assert config["gpg_provider"] == "gpg"
        assert config["skip_signing"] is False
