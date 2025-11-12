"""Tests for debrepomanager.cli module."""

import pytest
from click.testing import CliRunner

from debrepomanager.aptly import AptlyError
from debrepomanager.cli import cli


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def test_config(tmp_path):
    """Create test configuration file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        f"""
aptly:
  root_base: {tmp_path / 'aptly'}
  publish_base: {tmp_path / 'repo'}

gpg:
  key_id: TEST_KEY

repositories:
  codenames: [bookworm, noble]
  components: [jethome-tools]
  architectures: [amd64]
  auto_create: true

advanced:
  max_snapshots: 10
  snapshot_format: "{{component}}-{{codename}}-%Y%m%d-%H%M%S%f"
"""
    )
    return str(config_file)


class TestCLIHelp:
    """Tests for CLI help and basic functionality."""

    def test_cli_help(self, runner):
        """Test main CLI help."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Debian Repository Manager" in result.output
        assert "add" in result.output

    def test_cli_version_in_help(self, runner):
        """Test that help includes commands."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        # Should list available commands
        assert "Commands:" in result.output or "Options:" in result.output


class TestAddCommand:
    """Tests for add command."""

    def test_add_help(self, runner):
        """Test add command help."""
        result = runner.invoke(cli, ["add", "--help"])

        assert result.exit_code == 0
        assert "--codename" in result.output
        assert "--component" in result.output
        assert "--packages" in result.output
        assert "--package-dir" in result.output
        assert "--force" in result.output

    def test_add_missing_codename(self, runner):
        """Test add without codename fails."""
        result = runner.invoke(cli, ["add", "--component", "test"])

        assert result.exit_code != 0
        assert (
            "codename" in result.output.lower() or "required" in result.output.lower()
        )

    def test_add_missing_component(self, runner):
        """Test add without component fails."""
        result = runner.invoke(cli, ["add", "--codename", "bookworm"])

        assert result.exit_code != 0
        assert (
            "component" in result.output.lower() or "required" in result.output.lower()
        )

    def test_add_no_packages(self, runner, test_config):
        """Test add without packages fails."""
        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "add",
                "--codename",
                "bookworm",
                "--component",
                "test",
            ],
        )

        assert result.exit_code != 0
        assert "No packages" in result.output

    def test_add_with_packages(self, runner, test_config, tmp_path, mocker):
        """Test add with package files."""
        # Create test package
        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        # Mock AptlyManager
        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = True
        mock_manager.add_packages.return_value = True

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "add",
                "--codename",
                "bookworm",
                "--component",
                "jethome-tools",
                "--packages",
                str(pkg_file),
            ],
        )

        assert result.exit_code == 0
        assert "added successfully" in result.output.lower()
        mock_manager.add_packages.assert_called_once()

    def test_add_with_package_dir(self, runner, test_config, tmp_path, mocker):
        """Test add with package directory."""
        # Create test packages in directory
        pkg_dir = tmp_path / "packages"
        pkg_dir.mkdir()
        (pkg_dir / "pkg1.deb").touch()
        (pkg_dir / "pkg2.deb").touch()

        # Mock AptlyManager
        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = True
        mock_manager.add_packages.return_value = True

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "add",
                "--codename",
                "bookworm",
                "--component",
                "jethome-tools",
                "--package-dir",
                str(pkg_dir),
            ],
        )

        assert result.exit_code == 0
        # Should have found 2 packages
        mock_manager.add_packages.assert_called_once()
        call_args = mock_manager.add_packages.call_args[0]
        assert len(call_args[2]) == 2  # packages list

    def test_add_repo_not_exists_with_force(
        self, runner, test_config, tmp_path, mocker
    ):
        """Test add creates repo with --force."""
        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        # Mock AptlyManager
        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = False
        mock_manager.create_repo.return_value = True
        mock_manager.add_packages.return_value = True

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "add",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--packages",
                str(pkg_file),
                "--force",
            ],
        )

        assert result.exit_code == 0
        assert "created" in result.output.lower()
        mock_manager.create_repo.assert_called_once()
        mock_manager.add_packages.assert_called_once()

    def test_add_dry_run(self, runner, test_config, tmp_path):
        """Test add in dry-run mode."""
        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "--dry-run",
                "add",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--packages",
                str(pkg_file),
            ],
        )

        assert result.exit_code == 0
        assert "Dry-run mode" in result.output
        assert "Would add" in result.output
        assert pkg_file.name in result.output

    def test_add_verbose_mode(self, runner, test_config, tmp_path, mocker):
        """Test add in verbose mode."""
        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        # Mock AptlyManager
        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = True
        mock_manager.add_packages.return_value = True

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "--verbose",
                "add",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--packages",
                str(pkg_file),
            ],
        )

        assert result.exit_code == 0
        assert "Adding" in result.output

    def test_add_handles_aptly_error(self, runner, test_config, tmp_path, mocker):
        """Test add handles AptlyError gracefully."""
        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        # Mock AptlyManager to raise error
        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = True
        mock_manager.add_packages.side_effect = AptlyError("aptly failed")

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "add",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--packages",
                str(pkg_file),
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.output
        assert "aptly failed" in result.output


class TestCreateRepoCommand:
    """Tests for create-repo command."""

    def test_create_repo_help(self, runner):
        """Test create-repo help."""
        result = runner.invoke(cli, ["create-repo", "--help"])

        assert result.exit_code == 0
        assert "--codename" in result.output
        assert "--component" in result.output
        assert "--force" in result.output

    def test_create_repo_success(self, runner, test_config, mocker):
        """Test creating repository."""
        mock_manager = mocker.Mock()
        mock_manager.create_repo.return_value = True

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "create-repo",
                "--codename",
                "bookworm",
                "--component",
                "test",
            ],
        )

        assert result.exit_code == 0
        assert "created" in result.output.lower()
        mock_manager.create_repo.assert_called_once()

    def test_create_repo_with_architectures(self, runner, test_config, mocker):
        """Test creating repo with custom architectures."""
        mock_manager = mocker.Mock()
        mock_manager.create_repo.return_value = True

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "create-repo",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--architectures",
                "amd64",
                "--architectures",
                "arm64",
            ],
        )

        assert result.exit_code == 0
        # Check architectures passed
        call_args = mock_manager.create_repo.call_args
        assert call_args[1]["architectures"] == ["amd64", "arm64"]

    def test_create_repo_already_exists(self, runner, test_config, mocker):
        """Test creating repo that already exists fails."""
        mock_manager = mocker.Mock()
        mock_manager.create_repo.side_effect = ValueError("already exists")

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "create-repo",
                "--codename",
                "bookworm",
                "--component",
                "test",
            ],
        )

        assert result.exit_code == 1
        assert "already exists" in result.output
        assert "Use --force" in result.output

    def test_create_repo_dry_run(self, runner, test_config):
        """Test create-repo in dry-run mode."""
        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "--dry-run",
                "create-repo",
                "--codename",
                "bookworm",
                "--component",
                "test",
            ],
        )

        assert result.exit_code == 0
        assert "Dry-run mode" in result.output
        assert "Would create" in result.output


class TestDeleteRepoCommand:
    """Tests for delete-repo command."""

    def test_delete_repo_help(self, runner):
        """Test delete-repo help."""
        result = runner.invoke(cli, ["delete-repo", "--help"])

        assert result.exit_code == 0
        assert "--confirm" in result.output

    def test_delete_repo_without_confirm(self, runner, test_config):
        """Test delete without --confirm fails."""
        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "delete-repo",
                "--codename",
                "bookworm",
                "--component",
                "test",
            ],
        )

        assert result.exit_code == 1
        assert "requires --confirm" in result.output

    def test_delete_repo_with_confirm_cancelled(self, runner, test_config, mocker):
        """Test delete with confirm but cancelled at prompt."""
        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = True

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "delete-repo",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--confirm",
            ],
            input="n\n",  # Answer 'no' to confirmation
        )

        assert result.exit_code == 0
        assert "Cancelled" in result.output
        mock_manager.delete_repo.assert_not_called()

    def test_delete_repo_success(self, runner, test_config, mocker):
        """Test successful repository deletion."""
        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = True
        mock_manager.delete_repo.return_value = True

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "delete-repo",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--confirm",
            ],
            input="y\n",  # Answer 'yes' to confirmation
        )

        assert result.exit_code == 0
        assert "deleted" in result.output.lower()
        mock_manager.delete_repo.assert_called_once()

    def test_delete_repo_not_exists(self, runner, test_config, mocker):
        """Test deleting non-existent repo fails."""
        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = False

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "delete-repo",
                "--codename",
                "bookworm",
                "--component",
                "nonexistent",
                "--confirm",
            ],
        )

        assert result.exit_code == 1
        assert "doesn't exist" in result.output


class TestListCommand:
    """Tests for list command."""

    def test_list_help(self, runner):
        """Test list help."""
        result = runner.invoke(cli, ["list", "--help"])

        assert result.exit_code == 0
        assert "--codename" in result.output
        assert "--component" in result.output

    def test_list_all_repos(self, runner, test_config, mocker):
        """Test listing all repositories."""
        mock_manager = mocker.Mock()
        mock_manager.list_repos.return_value = ["repo1-bookworm", "repo2-noble"]

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(cli, ["--config", test_config, "list"])

        assert result.exit_code == 0
        assert "repo1-bookworm" in result.output
        assert "repo2-noble" in result.output
        assert "Total: 2" in result.output

    def test_list_repos_for_codename(self, runner, test_config, mocker):
        """Test listing repos for specific codename."""
        mock_manager = mocker.Mock()
        mock_manager.list_repos.return_value = ["repo1-bookworm"]

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli, ["--config", test_config, "list", "--codename", "bookworm"]
        )

        assert result.exit_code == 0
        assert "bookworm" in result.output
        assert "repo1-bookworm" in result.output

    def test_list_packages_in_component(self, runner, test_config, mocker):
        """Test listing packages in specific component."""
        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = True
        mock_manager.list_packages.return_value = ["pkg1_1.0_amd64", "pkg2_2.0_amd64"]

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "list",
                "--codename",
                "bookworm",
                "--component",
                "jethome-tools",
            ],
        )

        assert result.exit_code == 0
        assert "pkg1_1.0_amd64" in result.output
        assert "pkg2_2.0_amd64" in result.output
        assert "Packages: 2" in result.output

    def test_list_empty(self, runner, test_config, mocker):
        """Test listing when no repos exist."""
        mock_manager = mocker.Mock()
        mock_manager.list_repos.return_value = []

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(cli, ["--config", test_config, "list"])

        assert result.exit_code == 0
        assert "(none)" in result.output or "Total: 0" in result.output


class TestCLIErrorHandling:
    """Tests for CLI error handling."""

    def test_add_config_error(self, runner, tmp_path):
        """Test add handles config error."""
        # Invalid config file
        bad_config = tmp_path / "bad.yaml"
        bad_config.write_text("invalid: yaml: syntax:")

        result = runner.invoke(
            cli,
            [
                "--config",
                str(bad_config),
                "add",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--packages",
                "test.deb",
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_add_package_dir_not_found(self, runner, test_config):
        """Test add with non-existent package-dir."""
        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "add",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--package-dir",
                "/nonexistent/dir",
            ],
        )

        assert result.exit_code != 0
        assert "Error" in result.output or "not found" in result.output.lower()

    def test_add_unexpected_error(self, runner, test_config, tmp_path, mocker):
        """Test add handles unexpected errors."""
        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        # Mock to raise unexpected exception
        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = True
        mock_manager.add_packages.side_effect = RuntimeError("Unexpected!")

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "add",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--packages",
                str(pkg_file),
            ],
        )

        assert result.exit_code == 99  # Unexpected error code
        assert "Unexpected error" in result.output

    def test_create_repo_aptly_error(self, runner, test_config, mocker):
        """Test create-repo handles AptlyError."""
        mock_manager = mocker.Mock()
        mock_manager.create_repo.side_effect = AptlyError("aptly failed")

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "create-repo",
                "--codename",
                "bookworm",
                "--component",
                "test",
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_delete_repo_aptly_error(self, runner, test_config, mocker):
        """Test delete-repo handles AptlyError."""
        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = True
        mock_manager.delete_repo.side_effect = AptlyError("delete failed")

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "delete-repo",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--confirm",
            ],
            input="y\n",
        )

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_list_aptly_error(self, runner, test_config, mocker):
        """Test list handles AptlyError."""
        mock_manager = mocker.Mock()
        mock_manager.list_repos.side_effect = AptlyError("list failed")

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(cli, ["--config", test_config, "list"])

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_add_repo_not_exists_no_auto_create(
        self, runner, test_config, tmp_path, mocker
    ):
        """Test add fails when repo doesn't exist and no auto_create/force."""
        pkg_file = tmp_path / "test.deb"
        pkg_file.touch()

        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = False
        # Disable auto_create
        mock_config = mocker.Mock()
        mock_config.auto_create_repos = False

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)
        mocker.patch("debrepomanager.cli.Config", return_value=mock_config)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "add",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--packages",
                str(pkg_file),
            ],
        )

        # Should fail without --force and auto_create disabled
        assert result.exit_code != 0

    def test_create_repo_config_error(self, runner, test_config, mocker):
        """Test create-repo handles ConfigError."""
        from debrepomanager.config import ConfigError

        mock_manager = mocker.Mock()
        mock_manager.create_repo.side_effect = ConfigError("config error")

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "create-repo",
                "--codename",
                "bookworm",
                "--component",
                "test",
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_delete_repo_config_error(self, runner, test_config, mocker):
        """Test delete-repo handles ConfigError."""
        from debrepomanager.config import ConfigError

        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = True
        mock_manager.delete_repo.side_effect = ConfigError("config error")

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "delete-repo",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--confirm",
            ],
            input="y\n",
        )

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_list_config_error(self, runner, test_config, mocker):
        """Test list handles ConfigError."""
        from debrepomanager.config import ConfigError

        mock_manager = mocker.Mock()
        mock_manager.list_repos.side_effect = ConfigError("config error")

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(cli, ["--config", test_config, "list"])

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_list_packages_repo_not_exists(self, runner, test_config, mocker):
        """Test list packages for non-existent repo."""
        mock_manager = mocker.Mock()
        mock_manager.repo_exists.return_value = False

        mocker.patch("debrepomanager.cli.AptlyManager", return_value=mock_manager)

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "list",
                "--codename",
                "bookworm",
                "--component",
                "nonexistent",
            ],
        )

        assert result.exit_code == 1
        assert "doesn't exist" in result.output

    def test_add_verbose_with_package_dir_error(self, runner, test_config, mocker):
        """Test add verbose mode with package-dir error."""
        # Mock find_deb_files to raise exception
        mocker.patch(
            "debrepomanager.cli.find_deb_files",
            side_effect=ValueError("Invalid directory"),
        )

        result = runner.invoke(
            cli,
            [
                "--config",
                test_config,
                "--verbose",
                "add",
                "--codename",
                "bookworm",
                "--component",
                "test",
                "--package-dir",
                "/some/dir",
            ],
        )

        assert result.exit_code != 0
        assert "Error" in result.output
