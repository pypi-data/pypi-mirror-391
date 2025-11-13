"""Tests for debrepomanager.gpg_rotation module."""

import subprocess

import pytest

from debrepomanager.aptly import AptlyManager
from debrepomanager.config import Config
from debrepomanager.gpg_rotation import GPGRotationError, GPGRotationManager


@pytest.fixture
def config():
    """Create test config."""
    cfg = Config()
    cfg._config["gpg"]["key_id"] = "OLDKEY123"
    return cfg


@pytest.fixture
def mock_aptly(mocker):
    """Create mock AptlyManager."""
    aptly = mocker.Mock(spec=AptlyManager)
    aptly.metadata = mocker.Mock()
    return aptly


@pytest.fixture
def rotation_manager(config, mock_aptly):
    """Create GPGRotationManager instance."""
    return GPGRotationManager(config, mock_aptly)


class TestValidateNewKey:
    """Tests for validate_new_key()."""

    def test_validate_new_key_success(self, rotation_manager, mocker):
        """Test successful key validation."""
        # Mock GPG list-keys and sign test
        mock_results = [
            mocker.Mock(  # list-keys
                returncode=0,
                stdout="pub   rsa4096 2025-11-11 [SC]\n      NEWKEY123\nuid     Test User",
                stderr="",
            ),
            mocker.Mock(  # sign test
                returncode=0,
                stdout="-----BEGIN PGP SIGNED MESSAGE-----\nHash: SHA512\n\nTest message",
                stderr="",
            ),
        ]
        mock_run = mocker.patch("subprocess.run", side_effect=mock_results)

        result = rotation_manager.validate_new_key("NEWKEY123")

        assert result is True
        assert mock_run.call_count == 2  # list-keys + sign test

    def test_validate_new_key_not_found(self, rotation_manager, mocker):
        """Test key validation fails if key not found."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(
            returncode=0,
            stdout="No keys found",
            stderr="",
        )

        with pytest.raises(GPGRotationError, match="not found in output"):
            rotation_manager.validate_new_key("NEWKEY123")

    def test_validate_new_key_gpg_error(self, rotation_manager, mocker):
        """Test key validation handles GPG errors."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["gpg"], stderr="GPG error"
        )

        with pytest.raises(GPGRotationError, match="Failed to list keys"):
            rotation_manager.validate_new_key("NEWKEY123")

    def test_validate_new_key_timeout(self, rotation_manager, mocker):
        """Test key validation handles timeout."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.TimeoutExpired(["gpg"], 10)

        with pytest.raises(GPGRotationError, match="timed out"):
            rotation_manager.validate_new_key("NEWKEY123")


class TestGetAllPublishedRepos:
    """Tests for get_all_published_repos()."""

    def test_get_all_published_repos(self, rotation_manager, mock_aptly):
        """Test getting all published repositories."""
        mock_aptly.metadata.list_repositories.return_value = [
            {"codename": "bookworm", "component": "tools"},
            {"codename": "noble", "component": "armbian"},
        ]

        repos = rotation_manager.get_all_published_repos()

        assert len(repos) == 2
        assert repos[0]["codename"] == "bookworm"
        assert repos[1]["component"] == "armbian"


class TestResignRepository:
    """Tests for resign_repository()."""

    def test_resign_repository_success(self, rotation_manager, mock_aptly, mocker):
        """Test successful repository re-signing."""
        mock_aptly.get_published_snapshot.return_value = "tools-bookworm-20251111"
        mock_aptly._run_aptly = mocker.Mock()

        result = rotation_manager.resign_repository("bookworm", "tools", "NEWKEY123")

        assert result is True
        # Should call unpublish + publish
        assert mock_aptly._run_aptly.call_count >= 1

    def test_resign_repository_not_published(self, rotation_manager, mock_aptly):
        """Test re-signing skips non-published repositories."""
        mock_aptly.get_published_snapshot.return_value = None

        result = rotation_manager.resign_repository("bookworm", "tools", "NEWKEY123")

        assert result is False

    def test_resign_repository_error(self, rotation_manager, mock_aptly, mocker):
        """Test re-signing handles errors with rollback."""
        mock_aptly.get_published_snapshot.return_value = "snapshot"

        # Mock _run_aptly to fail on publish with new key, succeed on rollback
        call_count = [0]

        def mock_run_aptly(args, codename):
            call_count[0] += 1
            if call_count[0] == 1:  # drop
                return
            elif call_count[0] == 2:  # publish with new key - FAIL
                raise Exception("Publish failed")
            else:  # rollback with old key - SUCCESS
                return

        mock_aptly._run_aptly = mocker.Mock(side_effect=mock_run_aptly)

        # Should raise but after successful rollback
        with pytest.raises(
            GPGRotationError, match="Failed to publish with new key, rolled back"
        ):
            rotation_manager.resign_repository("bookworm", "tools", "NEWKEY123")


class TestRotateAllRepos:
    """Tests for rotate_all_repos()."""

    def test_rotate_all_repos_success(self, rotation_manager, mock_aptly, mocker):
        """Test successful rotation of all repositories."""
        # Mock validate_new_key
        mocker.patch.object(rotation_manager, "validate_new_key", return_value=True)

        # Mock get_all_published_repos
        mock_aptly.metadata.list_repositories.return_value = [
            {"codename": "bookworm", "component": "tools"},
            {"codename": "noble", "component": "armbian"},
        ]

        # Mock resign_repository
        mocker.patch.object(rotation_manager, "resign_repository", return_value=True)

        result = rotation_manager.rotate_all_repos("NEWKEY123", grace_period=False)

        assert result["total"] == 2
        assert result["success"] == 2
        assert result["failed"] == 0

    def test_rotate_all_repos_partial_failure(
        self, rotation_manager, mock_aptly, mocker
    ):
        """Test rotation with some failures."""
        mocker.patch.object(rotation_manager, "validate_new_key", return_value=True)

        mock_aptly.metadata.list_repositories.return_value = [
            {"codename": "bookworm", "component": "tools"},
            {"codename": "noble", "component": "armbian"},
        ]

        # Mock resign - first succeeds, second fails
        def mock_resign(codename, component, key_id):
            if component == "tools":
                return True
            raise Exception("Resign failed")

        mocker.patch.object(
            rotation_manager, "resign_repository", side_effect=mock_resign
        )

        result = rotation_manager.rotate_all_repos("NEWKEY123")

        assert result["total"] == 2
        assert result["success"] == 1
        assert result["failed"] == 1
        assert len(result["failures"]) == 1

    def test_rotate_all_repos_invalid_key(self, rotation_manager, mocker):
        """Test rotation fails if new key invalid."""
        mocker.patch.object(
            rotation_manager,
            "validate_new_key",
            side_effect=GPGRotationError("Invalid key"),
        )

        with pytest.raises(
            GPGRotationError, match="New key validation failed: Invalid key"
        ):
            rotation_manager.rotate_all_repos("BADKEY")


class TestVerifyRotation:
    """Tests for verify_rotation()."""

    def test_verify_rotation(self, rotation_manager, mock_aptly):
        """Test rotation verification."""
        mock_aptly.metadata.list_repositories.return_value = [
            {"codename": "bookworm", "component": "tools"},
            {"codename": "noble", "component": "armbian"},
        ]

        mock_aptly.get_published_snapshot.return_value = "snapshot"

        result = rotation_manager.verify_rotation("NEWKEY123")

        assert result["total"] == 2
        assert result["correct"] == 2


class TestRollbackRotation:
    """Tests for rollback_rotation()."""

    def test_rollback_rotation(self, rotation_manager, mocker):
        """Test rollback to old key."""
        mocker.patch.object(rotation_manager, "validate_new_key", return_value=True)
        mocker.patch.object(
            rotation_manager,
            "rotate_all_repos",
            return_value={"total": 2, "success": 2, "failed": 0, "skipped": 0},
        )

        result = rotation_manager.rollback_rotation("OLDKEY123")

        assert result["success"] == 2

    def test_rollback_rotation_old_key_not_available(self, rotation_manager, mocker):
        """Test rollback fails if old key not available."""
        mocker.patch.object(
            rotation_manager,
            "validate_new_key",
            side_effect=GPGRotationError("Key not found"),
        )

        with pytest.raises(GPGRotationError):
            rotation_manager.rollback_rotation("OLDKEY123")


class TestGracePeriod:
    """Tests for grace period functionality."""

    def test_grace_period_flag_preserved(self, rotation_manager, mock_aptly, mocker):
        """Test grace_period flag is passed through."""
        mocker.patch.object(rotation_manager, "validate_new_key", return_value=True)
        mock_aptly.metadata.list_repositories.return_value = []

        result = rotation_manager.rotate_all_repos("NEWKEY123", grace_period=True)

        # Grace period doesn't change rotation logic, just logging
        assert "success" in result
        assert "failed" in result
