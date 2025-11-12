"""Fuzz tests for utils module using Hypothesis.

These tests use property-based testing to verify that utility functions
handle random inputs correctly without crashes.
"""

import tempfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from debrepomanager.utils import (
    compare_versions,
    find_deb_files,
    get_package_age,
    parse_deb_metadata,
    setup_logging,
)


class TestVersionCompareFuzzing:
    """Fuzz tests for version comparison."""

    @given(
        version1=st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("Nd", "Pd")),
        ),
        version2=st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("Nd", "Pd")),
        ),
    )
    @settings(max_examples=100, deadline=500)
    def test_compare_versions_no_crash(self, version1: str, version2: str) -> None:
        """Test that version comparison doesn't crash with random version strings."""
        try:
            result = compare_versions(version1, version2)
            # Result should be an integer (apt_pkg returns any int, not just -1/0/1)
            assert isinstance(result, int)
            # Sign should be consistent: negative, zero, or positive
            if result < 0:
                assert compare_versions(version2, version1) > 0
            elif result > 0:
                assert compare_versions(version2, version1) < 0
            else:
                assert compare_versions(version2, version1) == 0
        except (ValueError, TypeError, AttributeError):
            # May fail on invalid version strings, but shouldn't crash
            pass

    @given(version=st.text(min_size=1, max_size=100))
    @settings(max_examples=100, deadline=500)
    def test_compare_version_with_itself(self, version: str) -> None:
        """Test that comparing version with itself returns 0."""
        try:
            result = compare_versions(version, version)
            # Same version should return 0
            assert result == 0
        except (ValueError, TypeError, AttributeError):
            # May fail on invalid version strings
            pass

    @given(
        version1=st.from_regex(r"\d+\.\d+(\.\d+)?", fullmatch=True),
        version2=st.from_regex(r"\d+\.\d+(\.\d+)?", fullmatch=True),
    )
    @settings(max_examples=50, deadline=500)
    def test_compare_semver_versions(self, version1: str, version2: str) -> None:
        """Test comparing semantic version strings."""
        result = compare_versions(version1, version2)
        assert isinstance(result, int)

        # For same version, result should be 0
        if version1 == version2:
            assert result == 0

        # Test symmetry: if v1 < v2, then v2 > v1
        reverse_result = compare_versions(version2, version1)
        if result < 0:
            assert reverse_result > 0
        elif result > 0:
            assert reverse_result < 0


class TestFindDebFilesFuzzing:
    """Fuzz tests for finding .deb files."""

    @given(
        subdirs=st.lists(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(whitelist_categories=("Ll", "Nd")),
            ),
            min_size=0,
            max_size=5,
        ),
        file_names=st.lists(
            st.text(
                min_size=1,
                max_size=30,
                alphabet=st.characters(whitelist_categories=("Ll", "Nd")),
            ),
            min_size=0,
            max_size=10,
        ),
    )
    @settings(max_examples=50, deadline=2000)
    def test_find_deb_files_with_random_structure(
        self, subdirs: list, file_names: list
    ) -> None:
        """Test finding .deb files in random directory structures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create random subdirectories
            for subdir in subdirs:
                try:
                    (tmppath / subdir).mkdir(parents=True, exist_ok=True)
                except (OSError, ValueError):
                    # Invalid directory name
                    continue

            # Create random files (some with .deb extension)
            deb_count = 0
            for i, name in enumerate(file_names):
                try:
                    # Every third file gets .deb extension
                    if i % 3 == 0:
                        filepath = tmppath / f"{name}.deb"
                        deb_count += 1
                    else:
                        filepath = tmppath / f"{name}.txt"

                    filepath.touch()
                except (OSError, ValueError):
                    # Invalid file name
                    continue

            # Should not crash
            try:
                result = find_deb_files(str(tmppath), recursive=True)
                assert isinstance(result, list)
                # Should find at most deb_count files
                assert len(result) <= deb_count
            except (FileNotFoundError, ValueError, OSError):
                # Expected for some edge cases
                pass

    @given(
        path_str=st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(
                min_codepoint=32, max_codepoint=126, blacklist_characters="/"
            ),
        )
    )
    @settings(max_examples=20, deadline=500)
    def test_find_deb_files_invalid_paths(self, path_str: str) -> None:
        """Test find_deb_files with simple invalid paths (limited to avoid hangs)."""
        try:
            result = find_deb_files(path_str, recursive=True)
            # If it succeeds, should return a list
            assert isinstance(result, list)
        except (FileNotFoundError, ValueError, OSError, TypeError, PermissionError):
            # Expected for invalid paths
            pass


class TestSetupLoggingFuzzing:
    """Fuzz tests for logging setup."""

    @given(
        level=st.sampled_from(
            [
                "DEBUG",
                "INFO",
                "WARNING",
                "ERROR",
                "CRITICAL",
                "debug",
                "info",
                "invalid",
            ]
        ),
        log_format=st.one_of(st.none(), st.text(max_size=200)),
    )
    @settings(max_examples=50, deadline=500)
    def test_setup_logging_no_crash(self, level: str, log_format: str) -> None:
        """Test that setup_logging doesn't crash with various inputs."""
        try:
            logger = setup_logging(level=level, log_format=log_format)
            # Should return a logger
            assert logger is not None
            # Should be able to log
            logger.info("Test message")
        except (ValueError, KeyError, AttributeError):
            # Expected for invalid log levels or formats
            pass

    @given(
        level=st.text(min_size=1, max_size=50),
    )
    @settings(max_examples=100, deadline=500)
    def test_setup_logging_random_levels(self, level: str) -> None:
        """Test setup_logging with random level strings."""
        try:
            logger = setup_logging(level=level)
            assert logger is not None
        except (ValueError, KeyError, AttributeError, TypeError):
            # Expected for invalid log levels
            pass


class TestPackageAgeFuzzing:
    """Fuzz tests for package age calculation."""

    @given(
        filename=st.text(
            min_size=1,
            max_size=100,
            alphabet=st.characters(whitelist_categories=("Ll", "Nd")),
        )
    )
    @settings(max_examples=50, deadline=1000)
    def test_get_package_age_with_temp_file(self, filename: str) -> None:
        """Test get_package_age with temporary files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            try:
                # Create a file
                filepath = tmppath / f"{filename}.deb"
                filepath.touch()

                # Should calculate age without crash
                age = get_package_age(str(filepath))
                assert isinstance(age, int)
                assert age >= 0

            except (OSError, ValueError):
                # Invalid filename
                pass

    @given(path_str=st.text(min_size=0, max_size=200))
    @settings(max_examples=100, deadline=500)
    def test_get_package_age_invalid_paths(self, path_str: str) -> None:
        """Test get_package_age with random path strings."""
        try:
            age = get_package_age(path_str)
            # If it succeeds, should return non-negative int
            assert isinstance(age, int)
            assert age >= 0
        except (FileNotFoundError, ValueError, OSError, TypeError):
            # Expected for invalid paths
            pass


class TestParseDebMetadataFuzzing:
    """Fuzz tests for .deb metadata parsing."""

    @given(path_str=st.text(min_size=0, max_size=200))
    @settings(max_examples=50, deadline=500)
    def test_parse_deb_metadata_random_paths(self, path_str: str) -> None:
        """Test parse_deb_metadata with random path strings."""
        try:
            result = parse_deb_metadata(path_str)
            # If it succeeds, should return PackageInfo
            assert hasattr(result, "name")
            assert hasattr(result, "version")
            assert hasattr(result, "architecture")
        except (FileNotFoundError, ValueError, OSError, TypeError, AttributeError):
            # Expected - not a valid .deb file
            pass

    @given(
        filename=st.text(
            min_size=1,
            max_size=100,
            alphabet=st.characters(whitelist_categories=("Ll", "Nd")),
        ),
        content=st.binary(min_size=0, max_size=1024),
    )
    @settings(max_examples=50, deadline=1000)
    def test_parse_deb_metadata_random_files(
        self, filename: str, content: bytes
    ) -> None:
        """Test parse_deb_metadata with random file content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            try:
                filepath = tmppath / f"{filename}.deb"
                filepath.write_bytes(content)

                # Should handle gracefully (not a valid .deb)
                try:
                    result = parse_deb_metadata(str(filepath))
                    # If it somehow parses, should have required fields
                    assert hasattr(result, "name")
                except (ValueError, OSError, AttributeError):
                    # Expected - not a valid .deb file
                    pass

            except (OSError, ValueError):
                # Invalid filename or write error
                pass


class TestPathHandlingEdgeCases:
    """Edge case tests for path handling."""

    def test_find_deb_files_empty_directory(self) -> None:
        """Test finding .deb files in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = find_deb_files(tmpdir, recursive=True)
            assert result == []

    def test_find_deb_files_nested_empty_dirs(self) -> None:
        """Test finding .deb files in nested empty directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "a" / "b" / "c").mkdir(parents=True)

            result = find_deb_files(tmpdir, recursive=True)
            assert result == []

    def test_find_deb_files_mixed_extensions(self) -> None:
        """Test finding .deb files among other file types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create various files
            (tmppath / "package1.deb").touch()
            (tmppath / "package2.DEB").touch()  # Different case
            (tmppath / "readme.txt").touch()
            (tmppath / "script.sh").touch()
            (tmppath / "package.deb.bak").touch()

            result = find_deb_files(tmpdir, recursive=False)
            # Should find only .deb files (case-sensitive)
            assert len(result) >= 1
            assert all(str(f).endswith(".deb") for f in result)

    def test_compare_versions_edge_cases(self) -> None:
        """Test version comparison with edge cases."""
        # Empty strings
        try:
            result = compare_versions("", "")
            assert result == 0
        except (ValueError, AttributeError):
            pass

        # Very long versions
        long_version = "1." + ".".join(["0"] * 100)
        try:
            result = compare_versions(long_version, long_version)
            assert result == 0
        except (ValueError, AttributeError):
            pass

        # Special characters
        try:
            result = compare_versions("1.0-rc1", "1.0-rc1")
            assert result == 0
        except (ValueError, AttributeError):
            pass
