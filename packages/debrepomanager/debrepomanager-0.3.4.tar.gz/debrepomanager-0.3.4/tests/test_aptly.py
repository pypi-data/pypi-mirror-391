"""Tests for debrepomanager.aptly module."""

import json
import subprocess
from pathlib import Path

import pytest

from debrepomanager.aptly import AptlyError, AptlyManager
from debrepomanager.config import Config


@pytest.fixture
def config(tmp_path):
    """Create test configuration."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        f"""
aptly:
  root_base: {tmp_path / 'aptly'}
  publish_base: {tmp_path / 'repo'}
  aptly_path: aptly

gpg:
  key_id: TEST_KEY_ID

repositories:
  codenames: [bookworm, noble]
  components: [jethome-tools]
  architectures: [amd64, arm64]
  auto_create: true
  dual_format:
    enabled: true
    method: symlink
    auto_symlink: true

advanced:
  max_snapshots: 10
  snapshot_format: "{{component}}-{{codename}}-%Y%m%d-%H%M%S%f"
"""
    )
    return Config(str(config_file))


@pytest.fixture
def manager(config):
    """Create AptlyManager instance."""
    return AptlyManager(config)


class TestNamingConvention:
    """Tests for repository naming."""

    def test_get_repo_name(self, manager):
        """Test repository naming convention."""
        name = manager._get_repo_name("bookworm", "jethome-tools")
        assert name == "jethome-tools-bookworm"

        name = manager._get_repo_name("noble", "jethome-armbian")
        assert name == "jethome-armbian-noble"

    def test_get_repo_name_consistency(self, manager):
        """Test naming is consistent."""
        name1 = manager._get_repo_name("bookworm", "main")
        name2 = manager._get_repo_name("bookworm", "main")
        assert name1 == name2


class TestConfigPath:
    """Tests for aptly config path generation."""

    def test_get_aptly_config_path(self, manager, config):
        """Test getting aptly config path."""
        path = manager._get_aptly_config_path("bookworm")

        assert isinstance(path, Path)
        assert str(path).endswith("bookworm/aptly.conf")
        assert "aptly" in str(path)

    def test_get_aptly_config_path_different_codenames(self, manager):
        """Test different paths for different codenames."""
        path1 = manager._get_aptly_config_path("bookworm")
        path2 = manager._get_aptly_config_path("noble")

        assert path1 != path2
        assert "bookworm" in str(path1)
        assert "noble" in str(path2)


class TestEnsureAptlyRoot:
    """Tests for aptly root directory creation."""

    def test_ensure_aptly_root_creates_directory(self, manager, tmp_path):
        """Test that aptly root directory is created."""
        root = manager._ensure_aptly_root("bookworm")

        assert root.exists()
        assert root.is_dir()
        assert root.name == "bookworm"

    def test_ensure_aptly_root_creates_config(self, manager, tmp_path):
        """Test that aptly.conf is created."""
        manager._ensure_aptly_root("bookworm")

        config_file = manager._get_aptly_config_path("bookworm")
        assert config_file.exists()

        # Verify config content
        with config_file.open() as f:
            config_data = json.load(f)

        assert "rootDir" in config_data
        assert "architectures" in config_data
        assert config_data["gpgDisableSign"] is False

    def test_ensure_aptly_root_idempotent(self, manager):
        """Test that calling ensure multiple times is safe."""
        root1 = manager._ensure_aptly_root("bookworm")
        root2 = manager._ensure_aptly_root("bookworm")

        assert root1 == root2
        assert root1.exists()

    def test_ensure_aptly_root_multiple_codenames(self, manager):
        """Test creating roots for multiple codenames."""
        root1 = manager._ensure_aptly_root("bookworm")
        root2 = manager._ensure_aptly_root("noble")

        assert root1.exists()
        assert root2.exists()
        assert root1 != root2


class TestCreateAptlyConfig:
    """Tests for aptly config file creation."""

    def test_create_aptly_config(self, manager, tmp_path):
        """Test aptly config creation."""
        # Ensure root exists first
        manager._ensure_aptly_root("bookworm")

        config_file = manager._get_aptly_config_path("bookworm")
        assert config_file.exists()

        # Parse and verify
        with config_file.open() as f:
            config_data = json.load(f)

        assert isinstance(config_data, dict)
        assert "rootDir" in config_data
        assert "architectures" in config_data
        assert "amd64" in config_data["architectures"]
        assert "arm64" in config_data["architectures"]
        assert config_data["gpgProvider"] == "gpg"

    def test_create_aptly_config_uses_config_architectures(self, manager):
        """Test that config uses architectures from Config."""
        manager._ensure_aptly_root("bookworm")

        config_file = manager._get_aptly_config_path("bookworm")
        with config_file.open() as f:
            config_data = json.load(f)

        expected_archs = manager.config.get_architectures()
        assert config_data["architectures"] == expected_archs


class TestRunAptly:
    """Tests for running aptly commands."""

    def test_run_aptly_success(self, manager, mocker):
        """Test successful aptly command execution."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="success", stderr="")

        manager._run_aptly(["repo", "list"], "bookworm")

        # Verify subprocess was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]

        # Should include aptly binary, -config, and our arguments
        assert manager.config.aptly_path in args
        assert "-config" in args
        assert "repo" in args
        assert "list" in args

    def test_run_aptly_with_config_path(self, manager, mocker):
        """Test that aptly is called with correct -config path."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        manager._run_aptly(["repo", "list"], "bookworm")

        args = mock_run.call_args[0][0]
        # Find -config argument
        config_index = args.index("-config")
        config_path = args[config_index + 1]

        assert "bookworm" in config_path
        assert config_path.endswith("aptly.conf")

    def test_run_aptly_failure(self, manager, mocker):
        """Test aptly command failure handling."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["aptly"], stderr="error message"
        )

        with pytest.raises(AptlyError, match="Aptly command failed"):
            manager._run_aptly(["repo", "create", "test"], "bookworm")

    def test_run_aptly_binary_not_found(self, manager, mocker):
        """Test handling when aptly binary not found."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = FileNotFoundError("aptly not found")

        with pytest.raises(AptlyError, match="aptly binary not found"):
            manager._run_aptly(["repo", "list"], "bookworm")

    def test_run_aptly_creates_root_if_needed(self, manager, tmp_path, mocker):
        """Test that _run_aptly ensures root exists."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        # Root doesn't exist yet
        aptly_root = Path(manager.config.get_aptly_root("bookworm"))
        assert not aptly_root.exists()

        # Run command
        manager._run_aptly(["repo", "list"], "bookworm")

        # Root should now exist
        assert aptly_root.exists()

    def test_run_aptly_different_codenames(self, manager, mocker):
        """Test running aptly for different codenames uses different configs."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        manager._run_aptly(["repo", "list"], "bookworm")
        bookworm_args = mock_run.call_args_list[0][0][0]

        manager._run_aptly(["repo", "list"], "noble")
        noble_args = mock_run.call_args_list[1][0][0]

        # Config paths should be different
        bookworm_config = bookworm_args[bookworm_args.index("-config") + 1]
        noble_config = noble_args[noble_args.index("-config") + 1]

        assert bookworm_config != noble_config
        assert "bookworm" in bookworm_config
        assert "noble" in noble_config


class TestRepoExists:
    """Tests for repository existence check."""

    def test_repo_exists_true(self, manager, mocker):
        """Test repo_exists returns True when repo exists."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="repo info", stderr="")

        exists = manager.repo_exists("bookworm", "jethome-tools")

        assert exists is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "repo" in args
        assert "show" in args

    def test_repo_exists_false(self, manager, mocker):
        """Test repo_exists returns False when repo doesn't exist."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["aptly"], stderr="not found"
        )

        exists = manager.repo_exists("bookworm", "nonexistent")

        assert exists is False


class TestCreateRepo:
    """Tests for repository creation."""

    def test_create_repo_new(self, manager, mocker):
        """Test creating new repository."""
        # Mock repo_exists to return False (repo doesn't exist)
        mocker.patch.object(manager, "repo_exists", return_value=False)

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        result = manager.create_repo("bookworm", "jethome-tools")

        assert result is True

        # Should have called: repo create, snapshot create
        assert mock_run.call_count >= 2

        # Check repo create was called
        create_calls = [
            call for call in mock_run.call_args_list if "create" in call[0][0]
        ]
        assert len(create_calls) >= 1

    def test_create_repo_with_architectures(self, manager, mocker):
        """Test creating repository with custom architectures."""
        # Mock repo_exists to return False
        mocker.patch.object(manager, "repo_exists", return_value=False)

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        manager.create_repo("bookworm", "jethome-tools", architectures=["amd64"])

        # Find the repo create call
        create_call = None
        for call in mock_run.call_args_list:
            args = call[0][0]
            if "repo" in args and "create" in args:
                create_call = args
                break

        assert create_call is not None
        assert "amd64" in ",".join(create_call)

    def test_create_repo_exists_without_force(self, manager, mocker):
        """Test creating repo that exists without force raises error."""
        # Mock repo_exists to return True (repo exists)
        mocker.patch.object(manager, "repo_exists", return_value=True)

        with pytest.raises(ValueError, match="already exists"):
            manager.create_repo("bookworm", "jethome-tools", force=False)

    def test_create_repo_exists_with_force(self, manager, mocker):
        """Test creating repo with force deletes and recreates."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        # Mock repo_exists to return True initially
        mocker.patch.object(manager, "repo_exists", side_effect=[True, False])

        result = manager.create_repo("bookworm", "jethome-tools", force=True)

        assert result is True

        # Should have called delete (repo drop)
        drop_calls = [call for call in mock_run.call_args_list if "drop" in call[0][0]]
        assert len(drop_calls) > 0

    def test_create_repo_creates_snapshot(self, manager, mocker):
        """Test that create_repo creates initial snapshot."""
        # Mock repo_exists to return False
        mocker.patch.object(manager, "repo_exists", return_value=False)

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        manager.create_repo("bookworm", "jethome-tools")

        # Should have called snapshot create
        snapshot_calls = [
            call
            for call in mock_run.call_args_list
            if "snapshot" in call[0][0] and "create" in call[0][0]
        ]
        assert len(snapshot_calls) > 0


class TestDeleteRepo:
    """Tests for repository deletion."""

    def test_delete_repo(self, manager, mocker):
        """Test deleting repository."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        result = manager.delete_repo("bookworm", "jethome-tools")

        assert result is True
        # Should have called snapshot list and repo drop
        assert mock_run.call_count >= 2

        # Check repo drop was called
        drop_calls = [
            call
            for call in mock_run.call_args_list
            if "drop" in call[0][0] and "repo" in call[0][0]
        ]
        assert len(drop_calls) == 1
        assert "-force" in drop_calls[0][0][0]

    def test_delete_repo_failure(self, manager, mocker):
        """Test delete_repo handles failures."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["aptly"], stderr="cannot delete"
        )

        with pytest.raises(AptlyError):
            manager.delete_repo("bookworm", "jethome-tools")


class TestAddPackages:
    """Tests for adding packages to repository."""

    def test_add_packages_to_existing_repo(self, manager, mocker, tmp_path):
        """Test adding packages to existing repository."""
        # Mock repo exists
        mocker.patch.object(manager, "repo_exists", return_value=True)

        # Create test package file
        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        result = manager.add_packages("bookworm", "jethome-tools", [str(pkg_file)])

        assert result is True

        # Should have called repo add
        add_calls = [call for call in mock_run.call_args_list if "add" in call[0][0]]
        assert len(add_calls) > 0

    def test_add_packages_auto_create_repo(self, manager, mocker, tmp_path):
        """Test adding packages auto-creates repo if enabled."""
        # Mock repo doesn't exist, then exists after create
        mocker.patch.object(manager, "repo_exists", side_effect=[False, True])
        mocker.patch.object(manager, "create_repo", return_value=True)

        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        # auto_create is True by default
        result = manager.add_packages("bookworm", "jethome-tools", [str(pkg_file)])

        assert result is True
        manager.create_repo.assert_called_once()

    def test_add_packages_repo_not_exists_no_auto_create(
        self, manager, mocker, tmp_path
    ):
        """Test adding to non-existent repo fails if auto_create disabled."""
        mocker.patch.object(manager, "repo_exists", return_value=False)
        # Patch the config dict directly
        manager.config._config["repositories"]["auto_create"] = False

        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        with pytest.raises(ValueError, match="doesn't exist"):
            manager.add_packages("bookworm", "jethome-tools", [str(pkg_file)])

    def test_add_packages_file_not_found(self, manager, mocker):
        """Test adding non-existent package file raises error."""
        mocker.patch.object(manager, "repo_exists", return_value=True)

        with pytest.raises(FileNotFoundError, match="not found"):
            manager.add_packages("bookworm", "jethome-tools", ["/nonexistent.deb"])

    def test_add_packages_creates_snapshot(self, manager, mocker, tmp_path):
        """Test that adding packages creates snapshot."""
        mocker.patch.object(manager, "repo_exists", return_value=True)

        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        manager.add_packages("bookworm", "jethome-tools", [str(pkg_file)])

        # Should have called snapshot create
        snapshot_calls = [
            call
            for call in mock_run.call_args_list
            if "snapshot" in call[0][0] and "create" in call[0][0]
        ]
        assert len(snapshot_calls) > 0

    def test_add_packages_without_snapshot(self, manager, mocker, tmp_path):
        """Test adding packages without creating snapshot."""
        mocker.patch.object(manager, "repo_exists", return_value=True)

        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        manager.add_packages(
            "bookworm", "jethome-tools", [str(pkg_file)], create_snapshot=False
        )

        # Should NOT have called snapshot create
        snapshot_calls = [
            call for call in mock_run.call_args_list if "snapshot" in call[0][0]
        ]
        assert len(snapshot_calls) == 0


class TestListRepos:
    """Tests for listing repositories."""

    def test_list_repos_for_codename(self, manager, mocker):
        """Test listing repos for specific codename."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(
            returncode=0, stdout="repo1-bookworm\nrepo2-bookworm\n", stderr=""
        )

        repos = manager.list_repos("bookworm")

        assert len(repos) == 2
        assert "repo1-bookworm" in repos
        assert "repo2-bookworm" in repos

    def test_list_repos_empty(self, manager, mocker):
        """Test listing repos when none exist."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        repos = manager.list_repos("bookworm")

        assert repos == []

    def test_list_repos_all_codenames(self, manager, mocker):
        """Test listing all repos from metadata (v0.2+)."""
        # Mock metadata to return repositories
        mock_repos = [
            {"codename": "bookworm", "component": "repo1", "created": "2025-11-07"},
            {"codename": "noble", "component": "repo2", "created": "2025-11-07"},
        ]
        mocker.patch.object(
            manager.metadata, "list_repositories", return_value=mock_repos
        )

        repos = manager.list_repos()  # No codename - uses metadata

        assert "repo1-bookworm" in repos
        assert "repo2-noble" in repos


class TestListPackages:
    """Tests for listing packages in repository."""

    def test_list_packages(self, manager, mocker):
        """Test listing packages in repository."""
        mocker.patch.object(manager, "repo_exists", return_value=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(
            returncode=0,
            stdout="""Name: jethome-tools-bookworm
Packages:
  jethome-tool_1.0_amd64
  jethome-util_2.0_amd64

Number of packages: 2
""",
            stderr="",
        )

        packages = manager.list_packages("bookworm", "jethome-tools")

        assert len(packages) == 2
        assert "jethome-tool_1.0_amd64" in packages
        assert "jethome-util_2.0_amd64" in packages

    def test_list_packages_empty_repo(self, manager, mocker):
        """Test listing packages in empty repository."""
        mocker.patch.object(manager, "repo_exists", return_value=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(
            returncode=0,
            stdout="""Name: test-repo
Packages:

Number of packages: 0
""",
            stderr="",
        )

        packages = manager.list_packages("bookworm", "test")

        assert packages == []

    def test_list_packages_repo_not_exists(self, manager, mocker):
        """Test listing packages in non-existent repo raises error."""
        mocker.patch.object(manager, "repo_exists", return_value=False)

        with pytest.raises(ValueError, match="doesn't exist"):
            manager.list_packages("bookworm", "nonexistent")


class TestGetPublishedSnapshot:
    """Tests for getting published snapshot."""

    def test_get_published_snapshot_not_published(self, manager, mocker):
        """Test getting snapshot when repo not published."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(
            returncode=0, stdout="", stderr=""  # No published repos
        )

        snapshot = manager.get_published_snapshot("bookworm", "jethome-tools")

        assert snapshot is None

    def test_get_published_snapshot_published(self, manager, mocker):
        """Test getting snapshot when repo is published."""
        mock_run = mocker.patch("subprocess.run")

        # First call: publish list
        # Second call: publish show
        mock_run.side_effect = [
            mocker.Mock(
                returncode=0, stdout="bookworm/jethome-tools:jethome-tools\n", stderr=""
            ),
            mocker.Mock(
                returncode=0,
                stdout="""Distribution: jethome-tools
Snapshot: jethome-tools-bookworm-20251101-123456
""",
                stderr="",
            ),
        ]

        snapshot = manager.get_published_snapshot("bookworm", "jethome-tools")

        assert snapshot == "jethome-tools-bookworm-20251101-123456"


class TestVerifyRepo:
    """Tests for repository verification."""

    def test_verify_repo_exists_not_published(self, manager, mocker):
        """Test verifying repository that exists but not published."""
        mocker.patch.object(manager, "repo_exists", return_value=True)
        mocker.patch.object(manager, "get_published_snapshot", return_value=None)

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        result = manager.verify_repo("bookworm", "jethome-tools")

        assert result is True

    def test_verify_repo_exists_published(self, manager, mocker):
        """Test verifying published repository."""
        mocker.patch.object(manager, "repo_exists", return_value=True)
        mocker.patch.object(
            manager,
            "get_published_snapshot",
            return_value="jethome-tools-bookworm-20251101-123456",
        )

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        result = manager.verify_repo("bookworm", "jethome-tools")

        assert result is True

        # Should have verified snapshot
        show_calls = [
            call
            for call in mock_run.call_args_list
            if "snapshot" in call[0][0] and "show" in call[0][0]
        ]
        assert len(show_calls) > 0

    def test_verify_repo_not_exists(self, manager, mocker):
        """Test verifying non-existent repo raises error."""
        mocker.patch.object(manager, "repo_exists", return_value=False)

        with pytest.raises(ValueError, match="doesn't exist"):
            manager.verify_repo("bookworm", "nonexistent")


class TestEdgeCases:
    """Tests for edge cases and error paths."""

    def test_ensure_aptly_root_permission_error(self, manager, tmp_path, mocker):
        """Test _ensure_aptly_root handles permission error."""
        # Mock mkdir to raise PermissionError
        mocker.patch("pathlib.Path.mkdir", side_effect=PermissionError("denied"))

        with pytest.raises(AptlyError, match="Permission denied"):
            manager._ensure_aptly_root("bookworm")

    def test_ensure_aptly_root_os_error(self, manager, tmp_path, mocker):
        """Test _ensure_aptly_root handles OS error."""
        # Mock mkdir to raise OSError
        mocker.patch("pathlib.Path.mkdir", side_effect=OSError("disk full"))

        with pytest.raises(AptlyError, match="Failed to create"):
            manager._ensure_aptly_root("bookworm")

    def test_create_aptly_config_permission_error(self, manager, tmp_path, mocker):
        """Test _create_aptly_config handles permission error."""
        # Ensure root exists first
        aptly_root = Path(manager.config.get_aptly_root("bookworm"))
        aptly_root.mkdir(parents=True, exist_ok=True)

        # Mock Path.open to raise PermissionError
        mock_open = mocker.mock_open()
        mock_open.side_effect = PermissionError("denied")
        mocker.patch("pathlib.Path.open", mock_open)

        with pytest.raises(AptlyError, match="Permission denied writing config"):
            manager._create_aptly_config("bookworm")

    def test_create_aptly_config_os_error(self, manager, tmp_path, mocker):
        """Test _create_aptly_config handles OS error."""
        # Ensure root exists first
        aptly_root = Path(manager.config.get_aptly_root("bookworm"))
        aptly_root.mkdir(parents=True, exist_ok=True)

        # Mock Path.open to raise OSError
        mock_open = mocker.mock_open()
        mock_open.side_effect = OSError("write failed")
        mocker.patch("pathlib.Path.open", mock_open)

        with pytest.raises(AptlyError, match="Failed to write config"):
            manager._create_aptly_config("bookworm")

    def test_cleanup_snapshots_non_critical(self, manager, mocker):
        """Test cleanup_old_snapshots doesn't fail on errors."""
        mock_run = mocker.patch("subprocess.run")
        # snapshot list succeeds
        mock_run.return_value = mocker.Mock(
            returncode=0,
            stdout="snap1-bookworm-20251101-123456\nsnap2-bookworm-20251101-123457",
            stderr="",
        )

        # _cleanup_old_snapshots catches errors and returns 0
        # This tests the except block that doesn't raise
        result = manager._cleanup_old_snapshots("bookworm", "component", keep=1)

        # Should not raise, even if aptly commands fail internally
        assert isinstance(result, int)

    def test_list_repos_error_returns_empty(self, manager, mocker):
        """Test list_repos returns empty list on error."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["aptly"], stderr="error"
        )

        # Should catch error and return empty list
        repos = manager.list_repos("bookworm")

        assert repos == []

    def test_add_packages_failure_logs_error(self, manager, mocker, tmp_path):
        """Test add_packages logs error on failure."""
        mocker.patch.object(manager, "repo_exists", return_value=True)

        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["aptly"], stderr="add failed"
        )

        with pytest.raises(AptlyError):
            manager.add_packages("bookworm", "test", [str(pkg_file)])

    def test_run_aptly_ensure_root_called(self, manager, mocker, tmp_path):
        """Test _run_aptly calls _ensure_aptly_root."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        mock_ensure = mocker.patch.object(manager, "_ensure_aptly_root")

        manager._run_aptly(["repo", "list"], "bookworm")

        mock_ensure.assert_called_once_with("bookworm")

    def test_create_repo_calls_ensure_root(self, manager, mocker):
        """Test create_repo ensures aptly root exists."""
        mocker.patch.object(manager, "repo_exists", return_value=False)
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        manager.create_repo("bookworm", "test")

        # _run_aptly should have been called, which calls _ensure_aptly_root
        assert mock_run.called

    def test_cleanup_snapshots_empty_list(self, manager, mocker):
        """Test cleanup with empty snapshot list."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        result = manager._cleanup_old_snapshots("bookworm", "test", keep=10)

        assert result == 0

    def test_cleanup_snapshots_all_kept(self, manager, mocker):
        """Test cleanup when all snapshots should be kept."""
        mock_run = mocker.patch("subprocess.run")
        # Only 3 snapshots, keep 10
        mock_run.return_value = mocker.Mock(
            returncode=0,
            stdout="test-bookworm-1\ntest-bookworm-2\ntest-bookworm-3",
            stderr="",
        )

        result = manager._cleanup_old_snapshots("bookworm", "test", keep=10)

        # No snapshots removed
        assert result == 0

    def test_list_repos_metadata_error_handling(self, manager, mocker):
        """Test list_repos handles metadata errors gracefully (v0.2+)."""
        # Mock metadata.list_repositories to raise exception
        mocker.patch.object(
            manager.metadata,
            "list_repositories",
            side_effect=Exception("Metadata corrupted"),
        )

        # Should return empty list on error, not raise
        result = manager.list_repos()
        assert result == []

    def test_get_published_snapshot_parse_failure(self, manager, mocker):
        """Test get_published_snapshot handles malformed output."""
        mock_run = mocker.patch("subprocess.run")
        # Return published but show has no Snapshot: line
        mock_run.side_effect = [
            mocker.Mock(returncode=0, stdout="bookworm/test:test", stderr=""),
            mocker.Mock(returncode=0, stdout="No snapshot info", stderr=""),
        ]

        result = manager.get_published_snapshot("bookworm", "test")

        # Should return None if can't parse
        assert result is None

    def test_verify_repo_with_snapshot_failure(self, manager, mocker):
        """Test verify_repo handles snapshot verification failure."""
        mocker.patch.object(manager, "repo_exists", return_value=True)
        mocker.patch.object(manager, "get_published_snapshot", return_value="snap-123")

        mock_run = mocker.patch("subprocess.run")
        # First call (repo show) succeeds, second (snapshot show) fails
        mock_run.side_effect = [
            mocker.Mock(returncode=0, stdout="", stderr=""),
            subprocess.CalledProcessError(1, ["aptly"], stderr="snapshot not found"),
        ]

        with pytest.raises(AptlyError):
            manager.verify_repo("bookworm", "test")

    def test_ensure_aptly_root_creates_config_on_error(self, manager, mocker, tmp_path):
        """Test _ensure_aptly_root handles config creation error."""
        # Let mkdir succeed but config creation fail
        mocker.patch.object(
            manager, "_create_aptly_config", side_effect=Exception("config error")
        )

        with pytest.raises(AptlyError, match="Failed to create aptly config"):
            manager._ensure_aptly_root("bookworm")


class TestPublishSnapshot:
    """Tests for snapshot publishing with GPG."""

    def test_publish_snapshot_initial(self, manager, mocker):
        """Test initial snapshot publication."""
        mocker.patch.object(manager.gpg, "check_key_available", return_value=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        result = manager._publish_snapshot(
            "bookworm", "jethome-tools", "snap-init", is_initial=True
        )

        assert result is True

        # Check publish snapshot was called
        publish_calls = [
            call
            for call in mock_run.call_args_list
            if "publish" in call[0][0] and "snapshot" in call[0][0]
        ]
        assert len(publish_calls) > 0

        # Check GPG key was used
        args = publish_calls[0][0][0]
        assert "-gpg-key" in args

    def test_publish_snapshot_switch(self, manager, mocker):
        """Test switching to new snapshot."""
        mocker.patch.object(manager.gpg, "check_key_available", return_value=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        result = manager._publish_snapshot(
            "bookworm", "jethome-tools", "snap-new", is_initial=False
        )

        assert result is True

        # Check publish switch was called
        switch_calls = [
            call for call in mock_run.call_args_list if "switch" in call[0][0]
        ]
        assert len(switch_calls) > 0

    def test_publish_snapshot_gpg_key_not_available(self, manager, mocker):
        """Test publish fails when GPG key not available."""
        mocker.patch.object(manager.gpg, "check_key_available", return_value=False)

        with pytest.raises(AptlyError, match="GPG key.*not found"):
            manager._publish_snapshot("bookworm", "test", "snap", is_initial=True)

    def test_publish_snapshot_failure(self, manager, mocker):
        """Test publish handles failure."""
        mocker.patch.object(manager.gpg, "check_key_available", return_value=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["aptly"], stderr="publish failed"
        )

        with pytest.raises(AptlyError, match="Aptly command failed"):
            manager._publish_snapshot("bookworm", "test", "snap", is_initial=True)


class TestGPGIntegration:
    """Tests for GPG integration in create_repo and add_packages."""

    def test_create_repo_publishes_with_gpg(self, manager, mocker):
        """Test create_repo publishes with GPG signing."""
        mocker.patch.object(manager, "repo_exists", return_value=False)
        mocker.patch.object(manager.gpg, "check_key_available", return_value=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        manager.create_repo("bookworm", "test")

        # Should have called publish with -gpg-key
        publish_calls = [
            call for call in mock_run.call_args_list if "publish" in call[0][0]
        ]
        assert len(publish_calls) > 0

        # Verify GPG key parameter
        args = publish_calls[0][0][0]
        assert "-gpg-key" in args

    def test_add_packages_publishes_with_gpg(self, manager, mocker, tmp_path):
        """Test add_packages publishes snapshot with GPG."""
        mocker.patch.object(manager, "repo_exists", return_value=True)
        mocker.patch.object(manager.gpg, "check_key_available", return_value=True)

        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        manager.add_packages("bookworm", "test", [str(pkg_file)])

        # Should have called publish switch
        switch_calls = [
            call for call in mock_run.call_args_list if "switch" in call[0][0]
        ]
        assert len(switch_calls) > 0


class TestDualFormatSupport:
    """Tests for dual format URL support (old and new formats)."""

    def test_create_dual_format_symlinks(self, manager, tmp_path):
        """Test creating symlinks for old format access."""
        # Create new format directory structure
        new_path = (
            tmp_path / "repo" / "bookworm" / "jethome-tools" / "dists" / "jethome-tools"
        )
        new_path.mkdir(parents=True, exist_ok=True)

        # Create a test file in new format location
        (new_path / "Release").write_text("test")

        # Create symlinks
        manager._create_dual_format_symlinks("bookworm", "jethome-tools")

        # Check symlink was created
        old_path = tmp_path / "repo" / "dists" / "bookworm" / "jethome-tools"
        assert old_path.exists()
        assert old_path.is_symlink()

        # Check symlink points to correct location
        target = old_path.resolve()
        assert target == new_path.resolve()

        # Verify we can access through symlink
        assert (old_path / "Release").exists()
        assert (old_path / "Release").read_text() == "test"

    def test_create_dual_format_symlinks_relative_path(self, manager, tmp_path):
        """Test symlinks use relative paths."""
        # Create new format directory
        new_path = (
            tmp_path / "repo" / "bookworm" / "jethome-tools" / "dists" / "jethome-tools"
        )
        new_path.mkdir(parents=True, exist_ok=True)

        manager._create_dual_format_symlinks("bookworm", "jethome-tools")

        old_path = tmp_path / "repo" / "dists" / "bookworm" / "jethome-tools"

        # Read symlink target (should be relative)
        import os

        link_target = os.readlink(old_path)
        assert not link_target.startswith("/")  # Relative path
        assert ".." in link_target  # Uses parent directory references

    def test_create_dual_format_symlinks_update_existing(self, manager, tmp_path):
        """Test updating existing symlinks."""
        # Create new format directory
        new_path = (
            tmp_path / "repo" / "bookworm" / "jethome-tools" / "dists" / "jethome-tools"
        )
        new_path.mkdir(parents=True, exist_ok=True)

        old_path = tmp_path / "repo" / "dists" / "bookworm" / "jethome-tools"

        # Create initial symlink
        manager._create_dual_format_symlinks("bookworm", "jethome-tools")
        assert old_path.is_symlink()

        # Create symlink again (should update)
        manager._create_dual_format_symlinks("bookworm", "jethome-tools")
        assert old_path.is_symlink()

    def test_create_dual_format_symlinks_new_path_not_exists(self, manager, tmp_path):
        """Test graceful handling when new format path doesn't exist."""
        # Don't create new format directory
        # Should not raise error, just log warning
        manager._create_dual_format_symlinks("bookworm", "jethome-tools")

        # Symlink should not be created
        old_path = tmp_path / "repo" / "dists" / "bookworm" / "jethome-tools"
        assert not old_path.exists()

    def test_create_dual_format_symlinks_existing_directory(self, manager, tmp_path):
        """Test handling when old path exists as directory (not symlink)."""
        # Create new format directory
        new_path = (
            tmp_path / "repo" / "bookworm" / "jethome-tools" / "dists" / "jethome-tools"
        )
        new_path.mkdir(parents=True, exist_ok=True)

        # Create old path as directory (not symlink)
        old_path = tmp_path / "repo" / "dists" / "bookworm" / "jethome-tools"
        old_path.mkdir(parents=True, exist_ok=True)
        (old_path / "important_file").write_text("data")

        # Should not overwrite directory (to avoid data loss)
        manager._create_dual_format_symlinks("bookworm", "jethome-tools")

        # Old path should still be directory
        assert old_path.is_dir()
        assert not old_path.is_symlink()
        assert (old_path / "important_file").exists()

    def test_publish_snapshot_creates_symlinks_when_enabled(
        self, manager, mocker, tmp_path
    ):
        """Test that publish_snapshot creates dual format symlinks when enabled."""
        mocker.patch.object(manager.gpg, "check_key_available", return_value=True)
        # Patch the internal _config dict
        manager.config._config["repositories"]["dual_format"]["enabled"] = True
        manager.config._config["repositories"]["dual_format"]["auto_symlink"] = True

        # Create new format directory structure
        new_path = (
            tmp_path / "repo" / "bookworm" / "jethome-tools" / "dists" / "jethome-tools"
        )
        new_path.mkdir(parents=True, exist_ok=True)

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        manager._publish_snapshot("bookworm", "jethome-tools", "snap-test")

        # Check symlink was created
        old_path = tmp_path / "repo" / "dists" / "bookworm" / "jethome-tools"
        assert old_path.is_symlink()

    def test_publish_snapshot_skips_symlinks_when_disabled(
        self, manager, mocker, tmp_path
    ):
        """Test that publish_snapshot skips symlinks when dual format disabled."""
        mocker.patch.object(manager.gpg, "check_key_available", return_value=True)
        # Patch the internal _config dict
        manager.config._config["repositories"]["dual_format"]["enabled"] = False

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        manager._publish_snapshot("bookworm", "jethome-tools", "snap-test")

        # Symlink should not be created
        old_path = tmp_path / "repo" / "dists" / "bookworm" / "jethome-tools"
        assert not old_path.exists()

    def test_publish_snapshot_continues_on_symlink_error(self, manager, mocker):
        """Test that publish continues even if symlink creation fails."""
        mocker.patch.object(manager.gpg, "check_key_available", return_value=True)
        # Patch the internal _config dict
        manager.config._config["repositories"]["dual_format"]["enabled"] = True
        manager.config._config["repositories"]["dual_format"]["auto_symlink"] = True

        # Mock symlink creation to raise error
        mocker.patch.object(
            manager,
            "_create_dual_format_symlinks",
            side_effect=AptlyError("Symlink failed"),
        )

        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.Mock(returncode=0, stdout="", stderr="")

        # Should not raise error, just log warning
        result = manager._publish_snapshot("bookworm", "test", "snap")
        assert result is True
