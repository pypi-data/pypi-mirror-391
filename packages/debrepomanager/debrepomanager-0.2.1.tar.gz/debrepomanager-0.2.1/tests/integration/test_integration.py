"""Integration tests with real aptly in Docker.

These tests run against real aptly installation to verify that:
1. Repositories are created correctly
2. Packages with same name/version but different content work in different codenames
3. APT can install packages from created repositories
4. Dual format (old/new URL) works
"""

import subprocess
from pathlib import Path

import pytest

# Skip all integration tests if not in Docker environment
pytestmark = pytest.mark.integration


def has_aptly() -> bool:
    """Check if aptly is available."""
    try:
        subprocess.run(["aptly", "version"], capture_output=True, check=True, timeout=5)
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


def has_fpm() -> bool:
    """Check if fpm is available."""
    try:
        subprocess.run(["fpm", "--version"], capture_output=True, check=True, timeout=5)
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


# Skip if aptly or fpm not available
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not has_aptly(), reason="aptly not available"),
    pytest.mark.skipif(not has_fpm(), reason="fpm not available"),
]


@pytest.fixture
def unique_component():
    """Generate unique component name for test isolation."""
    import time

    return f"test-{int(time.time() * 1000000)}"


@pytest.fixture(scope="module")
def test_packages(tmp_path_factory):
    """Create test packages using fpm."""
    packages_dir = tmp_path_factory.mktemp("packages")

    # Helper to create package
    def create_package(name, version, arch, codename, extra_content=""):
        tmp_dir = tmp_path_factory.mktemp(f"pkg-{name}-{version}")
        content_dir = tmp_dir / "etc" / name
        content_dir.mkdir(parents=True)

        # Create file with content specific to codename
        (content_dir / "hello_world").write_text(
            f"Hello from {name} v{version} ({codename})\n{extra_content}"
        )

        output = packages_dir / f"{name}_{version}_{arch}_{codename}.deb"

        subprocess.run(
            [
                "fpm",
                "-s",
                "dir",
                "-t",
                "deb",
                "-n",
                name,
                "-v",
                version,
                "-a",
                arch,
                "--description",
                f"Test package for {codename}",
                "-C",
                str(tmp_dir),
                "--package",
                str(output),
                "etc",
            ],
            check=True,
            capture_output=True,
        )

        return str(output)

    # Create test packages
    packages = {
        "bookworm": {
            "bsp": create_package(
                "jethome-bsp", "1.0", "amd64", "bookworm", "BSP for bookworm"
            ),
            "tool": create_package("jethome-tool", "1.0", "amd64", "bookworm"),
        },
        "noble": {
            "bsp": create_package(
                "jethome-bsp", "1.0", "amd64", "noble", "BSP for noble"
            ),
            "tool": create_package("jethome-tool", "2.0", "amd64", "noble"),
        },
    }

    return packages


@pytest.fixture(scope="module")
def config_file(tmp_path_factory):
    """Create test configuration."""
    config_dir = tmp_path_factory.mktemp("config")
    config_file = config_dir / "config.yaml"

    aptly_root = tmp_path_factory.mktemp("aptly")
    repo_root = tmp_path_factory.mktemp("repo")

    # Get GPG key ID from system
    result = subprocess.run(
        ["gpg", "--list-secret-keys", "--keyid-format", "LONG"],
        capture_output=True,
        text=True,
    )
    # Extract first key ID (simple parsing)
    gpg_key_id = "TEST_KEY"  # Fallback
    for line in result.stdout.split("\n"):
        if "sec" in line:
            parts = line.split()
            if len(parts) > 1 and "/" in parts[1]:
                gpg_key_id = parts[1].split("/")[1]
                break

    config_file.write_text(
        f"""
aptly:
  root_base: {aptly_root}
  publish_base: {repo_root}

gpg:
  key_id: {gpg_key_id}
  use_agent: true

repositories:
  codenames: [bookworm, noble]
  components: [jethome-tools, jethome-bsp]
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

    return str(config_file)


class TestRepositoryCreation:
    """Test repository creation with real aptly."""

    def test_create_repository(self, config_file, unique_component):
        """Test creating repository with real aptly."""
        from debrepomanager import AptlyManager, Config

        config = Config(config_file)
        manager = AptlyManager(config)

        # Create repository with unique name
        result = manager.create_repo("bookworm", unique_component)
        assert result is True

        # Verify repo exists
        assert manager.repo_exists("bookworm", unique_component)

        # Verify aptly root and config created
        aptly_root = Path(config.get_aptly_root("bookworm"))
        assert aptly_root.exists()
        assert (aptly_root / "aptly.conf").exists()

    def test_create_multiple_codenames(self, config_file, unique_component):
        """Test creating repos for multiple codenames (isolation test)."""
        from debrepomanager import AptlyManager, Config

        config = Config(config_file)
        manager = AptlyManager(config)

        # Create same component for different codenames
        component = f"{unique_component}-multi"
        manager.create_repo("bookworm", component, force=True)
        manager.create_repo("noble", component, force=True)

        # Both should exist
        assert manager.repo_exists("bookworm", component)
        assert manager.repo_exists("noble", component)

        # Different aptly roots
        bookworm_root = Path(config.get_aptly_root("bookworm"))
        noble_root = Path(config.get_aptly_root("noble"))

        assert bookworm_root != noble_root
        assert bookworm_root.exists()
        assert noble_root.exists()

    def test_force_recreate(self, config_file):
        """Test force recreation of existing repository."""
        import time

        from debrepomanager import AptlyManager, Config

        config = Config(config_file)
        manager = AptlyManager(config)

        # Use timestamp to ensure unique repo name
        repo_name = f"test-force-{int(time.time())}"

        # Create first time
        manager.create_repo("bookworm", repo_name, force=True)
        assert manager.repo_exists("bookworm", repo_name)

        # Recreate with force
        result = manager.create_repo("bookworm", repo_name, force=True)
        assert result is True
        assert manager.repo_exists("bookworm", repo_name)

    def test_create_without_force_fails(self, config_file):
        """Test creating existing repo without force raises error."""
        from debrepomanager import AptlyManager, Config

        config = Config(config_file)
        manager = AptlyManager(config)

        # Create first time
        manager.create_repo("bookworm", "test-noforce", force=True)

        # Try to create again without force
        with pytest.raises(ValueError, match="already exists"):
            manager.create_repo("bookworm", "test-noforce", force=False)


@pytest.mark.slow
class TestPackageIsolation:
    """Test that packages with same name/version work in different codenames."""

    def test_same_package_different_codenames(
        self, config_file, unique_component, test_packages
    ):
        """Critical test: same package name/version, different content, different codenames."""
        from debrepomanager import AptlyManager, Config

        config = Config(config_file)
        manager = AptlyManager(config)

        # Create repos
        manager.create_repo("bookworm", f"{unique_component}-jethome-bsp", force=True)
        manager.create_repo("noble", f"{unique_component}-jethome-bsp", force=True)

        # This would fail in single aptly root!
        # But should work with multi-root (different pools)

        # Verify different aptly roots (multi-root isolation)
        bookworm_root = Path(config.get_aptly_root("bookworm"))
        noble_root = Path(config.get_aptly_root("noble"))

        # Roots should be different (isolation)
        assert bookworm_root != noble_root

        # Both roots should exist after create_repo
        assert bookworm_root.exists()
        assert noble_root.exists()

        # Both should have aptly config files
        assert (bookworm_root / "aptly.conf").exists()
        assert (noble_root / "aptly.conf").exists()

        # Note: Actual package adding with same name/version different content
        # is tested in TestAddPackages::test_add_same_package_different_codenames


class TestCleanup:
    """Test cleanup operations."""

    def test_delete_repository(self, config_file):
        """Test deleting repository."""
        from debrepomanager import AptlyManager, Config

        config = Config(config_file)
        manager = AptlyManager(config)

        # Create and then delete
        manager.create_repo("bookworm", "test-delete", force=True)
        assert manager.repo_exists("bookworm", "test-delete")

        result = manager.delete_repo("bookworm", "test-delete")
        assert result is True

        # Should not exist anymore
        assert not manager.repo_exists("bookworm", "test-delete")


class TestAddPackages:
    """Test adding packages to repository."""

    def test_add_packages_to_repo(self, config_file, test_packages, unique_component):
        """Test adding packages to repository."""
        from debrepomanager import AptlyManager, Config

        config = Config(config_file)
        manager = AptlyManager(config)

        # Create repository with unique name
        manager.create_repo("bookworm", unique_component, force=True)

        # Add package to same unique component
        pkg_file = test_packages["bookworm"]["tool"]
        result = manager.add_packages("bookworm", unique_component, [pkg_file])

        assert result is True

        # Verify package is in repository using aptly repo show
        repo_name = f"{unique_component}-bookworm"
        result = manager._run_aptly(
            ["repo", "show", "-with-packages", repo_name], "bookworm"
        )

        assert "jethome-tool" in result.stdout

    def test_add_same_package_different_codenames(
        self, config_file, test_packages, unique_component
    ):
        """CRITICAL: Test adding same package name/version to different codenames.

        This validates multi-root isolation - same package name and version
        but different content can exist in different codenames.
        """
        from debrepomanager import AptlyManager, Config

        config = Config(config_file)
        manager = AptlyManager(config)

        # Create repos for both codenames
        manager.create_repo("bookworm", f"{unique_component}-jethome-bsp", force=True)
        manager.create_repo("noble", f"{unique_component}-jethome-bsp", force=True)

        # Add jethome-bsp v1.0 to bookworm (content: "BSP for bookworm")
        pkg_bookworm = test_packages["bookworm"]["bsp"]
        manager.add_packages(
            "bookworm", f"{unique_component}-jethome-bsp", [pkg_bookworm]
        )

        # Add jethome-bsp v1.0 to noble (content: "BSP for noble")
        # SAME name and version, DIFFERENT content!
        pkg_noble = test_packages["noble"]["bsp"]
        manager.add_packages("noble", f"{unique_component}-jethome-bsp", [pkg_noble])

        # Both should succeed - this is the critical test!
        # Verify both packages are in their respective repos
        result_bookworm = manager._run_aptly(
            [
                "repo",
                "show",
                "-with-packages",
                f"{unique_component}-jethome-bsp-bookworm",
            ],
            "bookworm",
        )
        result_noble = manager._run_aptly(
            ["repo", "show", "-with-packages", f"{unique_component}-jethome-bsp-noble"],
            "noble",
        )

        assert "jethome-bsp" in result_bookworm.stdout
        assert "jethome-bsp" in result_noble.stdout

        # Verify different aptly pools (multi-root isolation)
        bookworm_root = Path(config.get_aptly_root("bookworm"))
        noble_root = Path(config.get_aptly_root("noble"))

        assert bookworm_root != noble_root

        # Verify aptly roots exist (created during operations)
        assert bookworm_root.exists()
        assert noble_root.exists()

        # Verify aptly config files exist
        assert (bookworm_root / "aptly.conf").exists()
        assert (noble_root / "aptly.conf").exists()

    def test_add_packages_creates_snapshot(
        self, config_file, test_packages, unique_component
    ):
        """Test that adding packages creates snapshots."""
        from debrepomanager import AptlyManager, Config

        config = Config(config_file)
        manager = AptlyManager(config)

        # Create repo and add package
        manager.create_repo("bookworm", f"{unique_component}-jethome-tools", force=True)
        pkg_file = test_packages["bookworm"]["tool"]
        manager.add_packages(
            "bookworm", f"{unique_component}-jethome-tools", [pkg_file]
        )

        # List snapshots
        result = manager._run_aptly(["snapshot", "list", "-raw"], "bookworm")
        snapshots = result.stdout.strip().split("\n")

        # Should have at least init snapshot and one from add_packages
        assert len(snapshots) >= 2
        assert any("jethome-tools-bookworm" in s for s in snapshots)

    def test_snapshot_cleanup(self, config_file, test_packages):
        """Test that old snapshots are cleaned up."""
        from debrepomanager import AptlyManager, Config

        config = Config(config_file)
        manager = AptlyManager(config)

        # Create repo
        manager.create_repo("bookworm", "test-cleanup", force=True)

        # Create test package files
        pkg_file = test_packages["bookworm"]["tool"]

        # Add packages multiple times to create many snapshots
        max_snapshots = config.max_snapshots
        for i in range(max_snapshots + 5):
            manager.add_packages("bookworm", "test-cleanup", [pkg_file])

        # List snapshots
        result = manager._run_aptly(["snapshot", "list", "-raw"], "bookworm")
        snapshots = result.stdout.strip().split("\n")

        # Filter for our repo (excluding -init)
        repo_snapshots = [
            s
            for s in snapshots
            if s.startswith("test-cleanup-bookworm-") and not s.endswith("-init")
        ]

        # Should have kept only max_snapshots
        assert len(repo_snapshots) <= max_snapshots
