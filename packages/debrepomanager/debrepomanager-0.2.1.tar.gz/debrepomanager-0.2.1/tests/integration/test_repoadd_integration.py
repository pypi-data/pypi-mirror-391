"""Integration tests for repoadd script."""

import os
import subprocess
from pathlib import Path

import pytest


class TestRepoaddIntegration:
    """Integration tests for repoadd script with real packages."""

    @pytest.fixture
    def scripts_dir(self):
        """Get scripts directory."""
        return Path(__file__).parent.parent.parent / "scripts"

    @pytest.fixture
    def repoadd_script(self, scripts_dir):
        """Get repoadd script path."""
        script = scripts_dir / "repoadd"
        assert script.exists(), f"repoadd script not found: {script}"
        assert os.access(script, os.X_OK), f"repoadd script not executable: {script}"
        return script

    @pytest.fixture
    def test_packages_dir(self, tmp_path):
        """Create directory with test .deb packages."""
        pkg_dir = tmp_path / "test-packages"
        pkg_dir.mkdir()

        # Create fake .deb files
        (pkg_dir / "test-package1_1.0_amd64.deb").touch()
        (pkg_dir / "test-package2_1.0_amd64.deb").touch()

        # Create subdirectory with more packages
        subdir = pkg_dir / "subdir"
        subdir.mkdir()
        (subdir / "test-package3_1.0_amd64.deb").touch()

        return pkg_dir

    def test_repoadd_help(self, repoadd_script):
        """Test repoadd shows help message."""
        result = subprocess.run(
            [str(repoadd_script)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "Usage:" in result.stdout
        assert "stable|beta|test" in result.stdout
        assert "component" in result.stdout

    def test_repoadd_invalid_environment(self, repoadd_script, test_packages_dir):
        """Test repoadd rejects invalid environment."""
        result = subprocess.run(
            [str(repoadd_script), "invalid", "bookworm", str(test_packages_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert (
            "Invalid environment" in result.stderr
            or "Invalid environment" in result.stdout
        )

    def test_repoadd_invalid_codename(self, repoadd_script, test_packages_dir):
        """Test repoadd rejects invalid codename."""
        result = subprocess.run(
            [str(repoadd_script), "stable", "INVALID@#$", str(test_packages_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert (
            "Invalid codename" in result.stderr or "Invalid codename" in result.stdout
        )

    def test_repoadd_nonexistent_directory(self, repoadd_script):
        """Test repoadd rejects non-existent directory."""
        result = subprocess.run(
            [str(repoadd_script), "stable", "bookworm", "/nonexistent/path"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "not found" in result.stderr or "not found" in result.stdout

    def test_repoadd_empty_directory(self, repoadd_script, tmp_path):
        """Test repoadd rejects empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = subprocess.run(
            [str(repoadd_script), "stable", "bookworm", str(empty_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert (
            "No .deb files found" in result.stderr
            or "No .deb files found" in result.stdout
        )

    def test_repoadd_dry_run_auto_component(self, repoadd_script, test_packages_dir):
        """Test repoadd dry-run with auto-generated component."""
        env = os.environ.copy()
        env["DRY_RUN"] = "1"

        result = subprocess.run(
            [str(repoadd_script), "stable", "bookworm", str(test_packages_dir)],
            capture_output=True,
            text=True,
            env=env,
        )

        # Should succeed in dry-run mode
        assert result.returncode == 0
        assert "DRY RUN" in result.stdout
        assert "Found 3 .deb package(s)" in result.stdout
        # Component should be auto-generated: jethome-test-packages
        assert (
            "jethome-test-packages" in result.stdout or "test-packages" in result.stdout
        )

    def test_repoadd_dry_run_explicit_component(
        self, repoadd_script, test_packages_dir
    ):
        """Test repoadd dry-run with explicit component."""
        env = os.environ.copy()
        env["DRY_RUN"] = "1"

        result = subprocess.run(
            [
                str(repoadd_script),
                "stable",
                "bookworm",
                str(test_packages_dir),
                "jethome-custom",
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        # Should succeed in dry-run mode
        assert result.returncode == 0
        assert "DRY RUN" in result.stdout
        assert "Found 3 .deb package(s)" in result.stdout
        assert "jethome-custom" in result.stdout
        assert "Using explicit component: jethome-custom" in result.stdout

    def test_repoadd_dry_run_beta_environment(self, repoadd_script, test_packages_dir):
        """Test repoadd dry-run with beta environment."""
        env = os.environ.copy()
        env["DRY_RUN"] = "1"

        result = subprocess.run(
            [
                str(repoadd_script),
                "beta",
                "noble",
                str(test_packages_dir),
                "jethome-tools",
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        # Should succeed in dry-run mode
        assert result.returncode == 0
        assert "DRY RUN" in result.stdout
        assert "Environment: beta" in result.stdout
        assert "Codename: noble" in result.stdout
        assert "jethome-tools" in result.stdout
        assert "http://deb.repo.com/beta/" in result.stdout

    def test_repoadd_dry_run_test_environment(self, repoadd_script, test_packages_dir):
        """Test repoadd dry-run with test environment."""
        env = os.environ.copy()
        env["DRY_RUN"] = "1"

        result = subprocess.run(
            [
                str(repoadd_script),
                "test",
                "bookworm",
                str(test_packages_dir),
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        # Should succeed in dry-run mode
        assert result.returncode == 0
        assert "DRY RUN" in result.stdout
        assert "Environment: test" in result.stdout
        assert "http://deb.repo.com/test/" in result.stdout

    def test_repoadd_component_with_jethome_prefix(self, repoadd_script, tmp_path):
        """Test that jethome- prefix is not duplicated."""
        env = os.environ.copy()
        env["DRY_RUN"] = "1"

        # Create directory with jethome- prefix
        pkg_dir = tmp_path / "jethome-tools"
        pkg_dir.mkdir()
        (pkg_dir / "test.deb").touch()

        result = subprocess.run(
            [str(repoadd_script), "stable", "bookworm", str(pkg_dir)],
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 0
        # Should not duplicate prefix
        assert "Component: jethome-tools" in result.stdout
        # Should not be jethome-jethome-tools
        assert "jethome-jethome-tools" not in result.stdout

    @pytest.mark.skip(reason="repoadd script not available in Docker integration tests")
    @pytest.mark.integration
    def test_repoadd_full_workflow_dry_run(self, repoadd_script, test_packages_dir):
        """Test complete repoadd workflow in dry-run mode."""
        env = os.environ.copy()
        env["DRY_RUN"] = "1"
        env["DEBUG"] = "1"

        result = subprocess.run(
            [
                str(repoadd_script),
                "stable",
                "bookworm",
                str(test_packages_dir),
                "jethome-integration-test",
            ],
            capture_output=True,
            text=True,
            env=env,
        )

        # Verify success
        assert result.returncode == 0

        # Verify output contains key information
        assert "DRY RUN MODE" in result.stdout
        assert "Found 3 .deb package(s)" in result.stdout
        assert "Environment: stable" in result.stdout
        assert "Codename: bookworm" in result.stdout
        assert "Component: jethome-integration-test" in result.stdout
        assert "Package directory:" in result.stdout

        # Verify summary
        assert "SUCCESS" in result.stdout
        assert "APT Configuration:" in result.stdout
        assert (
            "deb http://deb.repo.com/ bookworm jethome-integration-test"
            in result.stdout
        )
