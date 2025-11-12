"""Tests for retention policy engine."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from debian.debian_support import Version

from debrepomanager.aptly import AptlyManager
from debrepomanager.config import Config
from debrepomanager.retention import PackageInfo, RetentionPolicy


@pytest.fixture
def config_with_retention(tmp_path):
    """Create test config with retention policy."""
    config_file = tmp_path / "config.yaml"
    config_content = """
gpg:
  key_id: "TEST_KEY"

aptly:
  root_base: "{root_base}"
  publish_base: "{publish_base}"

retention:
  default:
    min_versions: 5
    max_age_days: 90
  overrides:
    jethome-debug:
      min_versions: 2
      max_age_days: 30
    jethome-testing:
      min_versions: 3
      max_age_days: 14

repositories:
  architectures:
    - amd64
    - arm64
"""
    root_base = tmp_path / "aptly"
    publish_base = tmp_path / "public"
    root_base.mkdir()
    publish_base.mkdir()

    config_file.write_text(
        config_content.format(root_base=str(root_base), publish_base=str(publish_base))
    )

    return Config(str(config_file))


@pytest.fixture
def mock_aptly():
    """Create mock AptlyManager."""
    aptly = MagicMock(spec=AptlyManager)
    return aptly


@pytest.fixture
def retention_policy(config_with_retention, mock_aptly):
    """Create RetentionPolicy instance with mocked aptly."""
    return RetentionPolicy(config_with_retention, mock_aptly)


class TestRetentionPolicy:
    """Test RetentionPolicy class."""

    def test_get_policy_default(self, retention_policy):
        """Test getting default retention policy."""
        policy = retention_policy.get_policy("jethome-tools")

        assert policy["min_versions"] == 5
        assert policy["max_age_days"] == 90

    def test_get_policy_override(self, retention_policy):
        """Test getting component-specific override policy."""
        policy = retention_policy.get_policy("jethome-debug")

        assert policy["min_versions"] == 2
        assert policy["max_age_days"] == 30

    def test_get_policy_another_override(self, retention_policy):
        """Test another component override."""
        policy = retention_policy.get_policy("jethome-testing")

        assert policy["min_versions"] == 3
        assert policy["max_age_days"] == 14

    def test_parse_package_ref_success(self, retention_policy):
        """Test parsing valid package reference."""
        result = retention_policy._parse_package_ref("jethome-tool_1.2.3_amd64")

        assert result == ("jethome-tool", "1.2.3", "amd64")

    def test_parse_package_ref_with_complex_version(self, retention_policy):
        """Test parsing package ref with complex version."""
        result = retention_policy._parse_package_ref("my-package_1.2.3-4ubuntu5_arm64")

        assert result == ("my-package", "1.2.3-4ubuntu5", "arm64")

    def test_parse_package_ref_invalid(self, retention_policy):
        """Test parsing invalid package reference."""
        result = retention_policy._parse_package_ref("invalid_ref")

        assert result is None

    def test_analyze_repository(self, retention_policy, mock_aptly):
        """Test repository analysis and package grouping."""
        # Mock package list
        mock_aptly.list_packages.return_value = [
            "pkg1_1.0_amd64",
            "pkg1_1.1_amd64",
            "pkg1_2.0_amd64",
            "pkg2_1.0_arm64",
            "pkg2_2.0_arm64",
        ]

        grouped = retention_policy.analyze_repository("bookworm", "jethome-tools")

        assert len(grouped) == 2
        assert "pkg1" in grouped
        assert "pkg2" in grouped
        assert len(grouped["pkg1"]) == 3
        assert len(grouped["pkg2"]) == 2

        # Verify package info
        pkg1_versions = [p.version for p in grouped["pkg1"]]
        assert "1.0" in pkg1_versions
        assert "1.1" in pkg1_versions
        assert "2.0" in pkg1_versions

    def test_get_packages_to_remove_keep_min_versions(
        self, retention_policy, mock_aptly
    ):
        """Test that minimum versions are always kept."""
        # Create 10 old packages (all older than max_age_days)
        old_date = datetime.now() - timedelta(days=100)
        packages = [
            f"test-pkg_{i}.0_amd64" for i in range(1, 11)
        ]  # Versions 1.0 to 10.0

        mock_aptly.list_packages.return_value = packages

        # Mock _get_package_upload_date to return old dates
        with patch.object(
            retention_policy, "_get_package_upload_date", return_value=old_date
        ):
            to_remove = retention_policy.get_packages_to_remove(
                "bookworm", "jethome-tools"
            )

        # Should keep newest 5 versions (min_versions=5)
        # Should remove 5 oldest versions
        assert len(to_remove) == 5

        # Verify we're keeping the newest versions
        removed_versions = [pkg.version for pkg in to_remove]
        assert "1.0" in removed_versions  # Oldest
        assert "2.0" in removed_versions
        assert "10.0" not in removed_versions  # Newest, should be kept

    def test_get_packages_to_remove_age_based(self, retention_policy, mock_aptly):
        """Test age-based cleanup (older than max_age_days)."""
        # Create 7 packages with different ages
        now = datetime.now()
        packages_with_dates = [
            ("test-pkg_1.0_amd64", now - timedelta(days=150)),  # Very old
            ("test-pkg_2.0_amd64", now - timedelta(days=100)),  # Old
            ("test-pkg_3.0_amd64", now - timedelta(days=80)),  # Recent
            ("test-pkg_4.0_amd64", now - timedelta(days=60)),  # Recent
            ("test-pkg_5.0_amd64", now - timedelta(days=40)),  # Recent
            ("test-pkg_6.0_amd64", now - timedelta(days=20)),  # Very recent
            ("test-pkg_7.0_amd64", now - timedelta(days=1)),  # Brand new
        ]

        mock_aptly.list_packages.return_value = [pkg for pkg, _ in packages_with_dates]

        # Mock upload dates
        def mock_get_date(codename, component, ref):
            for pkg, date in packages_with_dates:
                if pkg == ref:
                    return date
            return now

        with patch.object(
            retention_policy, "_get_package_upload_date", side_effect=mock_get_date
        ):
            to_remove = retention_policy.get_packages_to_remove(
                "bookworm", "jethome-tools"
            )

        # min_versions=5, max_age_days=90
        # Keep newest 5: 7.0, 6.0, 5.0, 4.0, 3.0
        # From remaining (2.0, 1.0): remove those older than 90 days
        # Should remove: 1.0 (150 days), 2.0 (100 days)
        assert len(to_remove) == 2

        removed_versions = {pkg.version for pkg in to_remove}
        assert "1.0" in removed_versions
        assert "2.0" in removed_versions

    def test_cleanup_dry_run(self, retention_policy, mock_aptly):
        """Test cleanup in dry-run mode."""
        mock_aptly.list_packages.return_value = [
            "pkg_1.0_amd64",
            "pkg_2.0_amd64",
        ]

        old_date = datetime.now() - timedelta(days=100)
        with patch.object(
            retention_policy, "_get_package_upload_date", return_value=old_date
        ):
            result = retention_policy.cleanup("bookworm", "jethome-tools", dry_run=True)

        assert result["analyzed"] == 2
        assert result["to_remove"] == 0  # Both kept due to min_versions=5
        assert result["removed"] == 0
        assert "packages" in result

        # Verify aptly.remove_packages was not called
        mock_aptly.remove_packages.assert_not_called()

    def test_cleanup_apply(self, retention_policy, mock_aptly):
        """Test cleanup with --apply (actual removal)."""
        # Create more packages than min_versions
        packages = [f"pkg_{i}.0_amd64" for i in range(1, 8)]  # 7 packages
        mock_aptly.list_packages.return_value = packages

        old_date = datetime.now() - timedelta(days=100)
        with patch.object(
            retention_policy, "_get_package_upload_date", return_value=old_date
        ):
            result = retention_policy.cleanup(
                "bookworm", "jethome-tools", dry_run=False
            )

        assert result["analyzed"] == 7
        assert result["to_remove"] == 2  # 7 - 5 (min_versions)
        assert result["removed"] == 2

        # Verify aptly.remove_packages was called
        mock_aptly.remove_packages.assert_called_once()
        call_args = mock_aptly.remove_packages.call_args
        assert call_args[0][0] == "bookworm"
        assert call_args[0][1] == "jethome-tools"
        assert len(call_args[0][2]) == 2  # 2 packages to remove
        assert call_args[1]["dry_run"] is False


class TestPackageInfo:
    """Test PackageInfo dataclass."""

    def test_package_info_creation(self):
        """Test creating PackageInfo instance."""
        now = datetime.now()
        pkg = PackageInfo(
            name="test-pkg",
            version="1.2.3",
            architecture="amd64",
            upload_date=now,
            full_ref="test-pkg_1.2.3_amd64",
            size_bytes=1024,
        )

        assert pkg.name == "test-pkg"
        assert pkg.version == "1.2.3"
        assert pkg.architecture == "amd64"
        assert pkg.full_ref == "test-pkg_1.2.3_amd64"
        assert pkg.size_bytes == 1024

    def test_package_info_version_obj(self):
        """Test version_obj property returns Version object."""
        pkg = PackageInfo(
            name="pkg",
            version="1.2.3",
            architecture="amd64",
            upload_date=datetime.now(),
            full_ref="pkg_1.2.3_amd64",
        )

        version_obj = pkg.version_obj
        assert isinstance(version_obj, Version)
        assert str(version_obj) == "1.2.3"

    def test_package_info_age_days(self):
        """Test age_days property calculation."""
        old_date = datetime.now() - timedelta(days=30)
        pkg = PackageInfo(
            name="pkg",
            version="1.0",
            architecture="amd64",
            upload_date=old_date,
            full_ref="pkg_1.0_amd64",
        )

        # Age should be approximately 30 days (allow small delta for test execution time)
        assert 29 <= pkg.age_days <= 31


class TestVersionSorting:
    """Test debian version comparison and sorting."""

    def test_version_comparison_simple(self):
        """Test simple version comparison."""
        v1 = Version("1.0")
        v2 = Version("2.0")

        assert v1 < v2
        assert v2 > v1

    def test_version_comparison_complex(self):
        """Test complex debian version comparison."""
        versions = [
            Version("1.0"),
            Version("1.0.1"),
            Version("1.1"),
            Version("2.0"),
            Version("1.0-1"),
            Version("1.0-2"),
        ]

        sorted_versions = sorted(versions)

        # Verify order
        assert str(sorted_versions[0]) == "1.0"
        assert str(sorted_versions[-1]) == "2.0"

    def test_version_sorting_with_epoch(self):
        """Test version sorting with epoch."""
        v1 = Version("1:1.0")  # Epoch 1
        v2 = Version("2.0")  # No epoch (epoch 0)

        assert v1 > v2  # Epoch takes precedence

    def test_package_sorting_by_version(self):
        """Test sorting PackageInfo objects by version."""
        now = datetime.now()
        packages = [
            PackageInfo("pkg", "1.0", "amd64", now, "pkg_1.0_amd64"),
            PackageInfo("pkg", "2.0", "amd64", now, "pkg_2.0_amd64"),
            PackageInfo("pkg", "1.5", "amd64", now, "pkg_1.5_amd64"),
            PackageInfo("pkg", "1.0.1", "amd64", now, "pkg_1.0.1_amd64"),
        ]

        sorted_packages = sorted(packages, key=lambda p: p.version_obj)

        versions = [p.version for p in sorted_packages]
        assert versions == ["1.0", "1.0.1", "1.5", "2.0"]

    def test_package_sorting_descending(self):
        """Test sorting packages by version (newest first)."""
        now = datetime.now()
        packages = [
            PackageInfo("pkg", "1.0", "amd64", now, "pkg_1.0_amd64"),
            PackageInfo("pkg", "2.0", "amd64", now, "pkg_2.0_amd64"),
            PackageInfo("pkg", "1.5", "amd64", now, "pkg_1.5_amd64"),
        ]

        sorted_packages = sorted(packages, key=lambda p: p.version_obj, reverse=True)

        versions = [p.version for p in sorted_packages]
        assert versions == ["2.0", "1.5", "1.0"]


class TestRetentionPolicyIntegration:
    """Integration tests for retention policy."""

    def test_full_cleanup_workflow(self, retention_policy, mock_aptly):
        """Test complete cleanup workflow."""
        # Setup: 10 packages, varying ages
        now = datetime.now()
        packages = []
        dates = {}

        for i in range(1, 11):
            ref = f"app_{i}.0_amd64"
            packages.append(ref)
            # Age increases with version number (newest = highest version)
            age_days = (11 - i) * 15  # 150, 135, 120, ..., 15 days
            dates[ref] = now - timedelta(days=age_days)

        mock_aptly.list_packages.return_value = packages

        def mock_get_date(codename, component, ref):
            return dates.get(ref, now)

        with patch.object(
            retention_policy, "_get_package_upload_date", side_effect=mock_get_date
        ):
            # Get packages to remove
            to_remove = retention_policy.get_packages_to_remove(
                "bookworm", "jethome-tools"
            )

            # Execute cleanup
            result = retention_policy.cleanup(
                "bookworm", "jethome-tools", dry_run=False
            )

        # min_versions=5, max_age_days=90
        # Keep: 10.0, 9.0, 8.0, 7.0, 6.0 (newest 5)
        # From remaining: 5.0, 4.0, 3.0, 2.0, 1.0
        # Ages: 90, 105, 120, 135, 150 days
        # Remove those > 90 days: 4.0 (105), 3.0 (120), 2.0 (135), 1.0 (150)

        assert result["to_remove"] == 4
        assert result["removed"] == 4

        removed_versions = {pkg.version for pkg in to_remove}
        assert "1.0" in removed_versions
        assert "2.0" in removed_versions
        assert "3.0" in removed_versions
        assert "4.0" in removed_versions
        assert "5.0" not in removed_versions  # Exactly 90 days, kept
        assert "10.0" not in removed_versions  # Newest, kept


class TestKeepLatestOption:
    """Tests for keep_latest retention option."""

    def test_keep_latest_default(self, retention_policy, mocker):
        """Test keep_latest defaults to 1 (keep newest version)."""
        mocker.patch.object(
            retention_policy,
            "analyze_repository",
            return_value={
                "test-pkg": [
                    PackageInfo(
                        name="test-pkg",
                        version="1.0",
                        architecture="amd64",
                        upload_date=datetime.now() - timedelta(days=100),
                        full_ref="test-pkg_1.0_amd64",
                    ),
                ]
            },
        )

        # Policy: min_versions=0, max_age_days=90, keep_latest not set (defaults to 1)
        mocker.patch.object(
            retention_policy,
            "get_policy",
            return_value={"min_versions": 0, "max_age_days": 90},
        )

        to_remove = retention_policy.get_packages_to_remove("bookworm", "test")

        # Should keep the package (keep_latest=1 by default)
        assert len(to_remove) == 0

    def test_keep_latest_multiple_versions(self, retention_policy, mocker):
        """Test keep_latest preserves N newest versions regardless of age."""
        mocker.patch.object(
            retention_policy,
            "analyze_repository",
            return_value={
                "test-pkg": [
                    PackageInfo(
                        name="test-pkg",
                        version="3.0",
                        architecture="amd64",
                        upload_date=datetime.now() - timedelta(days=100),
                        full_ref="test-pkg_3.0_amd64",
                    ),
                    PackageInfo(
                        name="test-pkg",
                        version="2.0",
                        architecture="amd64",
                        upload_date=datetime.now() - timedelta(days=120),
                        full_ref="test-pkg_2.0_amd64",
                    ),
                    PackageInfo(
                        name="test-pkg",
                        version="1.0",
                        architecture="amd64",
                        upload_date=datetime.now() - timedelta(days=150),
                        full_ref="test-pkg_1.0_amd64",
                    ),
                ]
            },
        )

        # Policy: min_versions=1, max_age_days=90, keep_latest=2
        mocker.patch.object(
            retention_policy,
            "get_policy",
            return_value={
                "min_versions": 1,
                "max_age_days": 90,
                "keep_latest": 2,
            },
        )

        to_remove = retention_policy.get_packages_to_remove("bookworm", "test")

        # Should keep 2 latest (v3.0 and v2.0) even though aged, remove v1.0
        assert len(to_remove) == 1
        assert to_remove[0].version == "1.0"

    def test_keep_latest_overrides_min_versions(self, retention_policy, mocker):
        """Test keep_latest takes precedence if higher than min_versions."""
        mocker.patch.object(
            retention_policy,
            "analyze_repository",
            return_value={
                "test-pkg": [
                    PackageInfo(
                        name="test-pkg",
                        version=f"{i}.0",
                        architecture="amd64",
                        upload_date=datetime.now() - timedelta(days=100 + i * 10),
                        full_ref=f"test-pkg_{i}.0_amd64",
                    )
                    for i in range(10, 0, -1)  # 10 versions
                ]
            },
        )

        # keep_latest=7 > min_versions=3
        mocker.patch.object(
            retention_policy,
            "get_policy",
            return_value={
                "min_versions": 3,
                "max_age_days": 90,
                "keep_latest": 7,
            },
        )

        to_remove = retention_policy.get_packages_to_remove("bookworm", "test")

        # Should keep 7 latest, remove 3
        assert len(to_remove) == 3


class TestDeleteLastAgedVersion:
    """Tests for delete_last_aged_version option."""

    def test_delete_last_aged_version_false_default(self, retention_policy, mocker):
        """Test delete_last_aged_version=false (default) keeps last version."""
        mocker.patch.object(
            retention_policy,
            "analyze_repository",
            return_value={
                "test-pkg": [
                    PackageInfo(
                        name="test-pkg",
                        version="1.0",
                        architecture="amd64",
                        upload_date=datetime.now() - timedelta(days=365),
                        full_ref="test-pkg_1.0_amd64",
                    ),
                ]
            },
        )

        # Policy: min_versions=0, max_age_days=90, no delete_last_aged_version
        mocker.patch.object(
            retention_policy,
            "get_policy",
            return_value={"min_versions": 0, "max_age_days": 90, "keep_latest": 0},
        )

        to_remove = retention_policy.get_packages_to_remove("bookworm", "test")

        # Should keep the package (safety - last version)
        assert len(to_remove) == 0

    def test_delete_last_aged_version_true_allows_deletion(
        self, retention_policy, mocker
    ):
        """Test delete_last_aged_version=true allows deleting last version."""
        mocker.patch.object(
            retention_policy,
            "analyze_repository",
            return_value={
                "test-pkg": [
                    PackageInfo(
                        name="test-pkg",
                        version="1.0",
                        architecture="amd64",
                        upload_date=datetime.now() - timedelta(days=365),
                        full_ref="test-pkg_1.0_amd64",
                    ),
                ]
            },
        )

        # Policy: delete_last_aged_version=true allows deletion
        mocker.patch.object(
            retention_policy,
            "get_policy",
            return_value={
                "min_versions": 0,
                "max_age_days": 90,
                "keep_latest": 0,
                "delete_last_aged_version": True,
            },
        )

        to_remove = retention_policy.get_packages_to_remove("bookworm", "test")

        # Should mark for removal (explicitly allowed)
        assert len(to_remove) == 1
        assert to_remove[0].version == "1.0"

    def test_keep_latest_protects_from_deletion(self, retention_policy, mocker):
        """Test keep_latest protects packages even with delete_last_aged_version=true."""
        mocker.patch.object(
            retention_policy,
            "analyze_repository",
            return_value={
                "test-pkg": [
                    PackageInfo(
                        name="test-pkg",
                        version="2.0",
                        architecture="amd64",
                        upload_date=datetime.now() - timedelta(days=200),
                        full_ref="test-pkg_2.0_amd64",
                    ),
                    PackageInfo(
                        name="test-pkg",
                        version="1.0",
                        architecture="amd64",
                        upload_date=datetime.now() - timedelta(days=365),
                        full_ref="test-pkg_1.0_amd64",
                    ),
                ]
            },
        )

        # Policy: keep_latest=1, delete_last_aged_version=true
        mocker.patch.object(
            retention_policy,
            "get_policy",
            return_value={
                "min_versions": 0,
                "max_age_days": 90,
                "keep_latest": 1,
                "delete_last_aged_version": True,
            },
        )

        to_remove = retention_policy.get_packages_to_remove("bookworm", "test")

        # keep_latest=1 protects v2.0, v1.0 can be deleted
        assert len(to_remove) == 1
        assert to_remove[0].version == "1.0"
