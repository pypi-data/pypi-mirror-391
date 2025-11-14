"""Tests for debrepomanager.metadata module."""

import json
from pathlib import Path

import pytest

from debrepomanager.metadata import MetadataError, MetadataManager


@pytest.fixture
def temp_aptly_root(tmp_path):
    """Create temporary aptly root directory."""
    return tmp_path / "aptly"


@pytest.fixture
def metadata_manager(temp_aptly_root):
    """Create MetadataManager instance with temp directory."""
    return MetadataManager(str(temp_aptly_root))


class TestMetadataManagerInit:
    """Tests for MetadataManager initialization."""

    def test_init_creates_paths(self, temp_aptly_root):
        """Test MetadataManager initialization creates correct paths."""
        manager = MetadataManager(str(temp_aptly_root))

        assert manager.aptly_root_base == temp_aptly_root
        assert manager.metadata_dir == temp_aptly_root / ".repomanager"
        assert (
            manager.metadata_path == temp_aptly_root / ".repomanager" / "metadata.json"
        )
        assert manager._metadata is None


class TestMetadataLoad:
    """Tests for metadata loading."""

    def test_load_creates_default_when_no_file(self, metadata_manager):
        """Test load() creates default metadata when file doesn't exist."""
        metadata = metadata_manager.load()

        assert "repositories" in metadata
        assert "last_updated" in metadata
        assert metadata["repositories"] == []
        assert isinstance(metadata["last_updated"], str)

    def test_load_reads_existing_file(self, metadata_manager, temp_aptly_root):
        """Test load() reads existing metadata file."""
        # Create metadata file
        metadata_dir = temp_aptly_root / ".repomanager"
        metadata_dir.mkdir(parents=True)
        metadata_file = metadata_dir / "metadata.json"

        test_data = {
            "repositories": [
                {
                    "codename": "bookworm",
                    "component": "tools",
                    "created": "2025-11-07T10:00:00",
                }
            ],
            "last_updated": "2025-11-07T12:00:00",
        }

        with metadata_file.open("w") as f:
            json.dump(test_data, f)

        # Load metadata
        metadata = metadata_manager.load()

        assert len(metadata["repositories"]) == 1
        assert metadata["repositories"][0]["codename"] == "bookworm"
        assert metadata["repositories"][0]["component"] == "tools"

    def test_load_corrupted_file_raises_error(self, metadata_manager, temp_aptly_root):
        """Test load() raises MetadataError for corrupted file."""
        # Create corrupted metadata file
        metadata_dir = temp_aptly_root / ".repomanager"
        metadata_dir.mkdir(parents=True)
        metadata_file = metadata_dir / "metadata.json"

        with metadata_file.open("w") as f:
            f.write("{ invalid json }")

        with pytest.raises(MetadataError, match="Corrupted metadata"):
            metadata_manager.load()

    def test_load_caches_metadata(self, metadata_manager):
        """Test load() caches metadata in memory."""
        metadata1 = metadata_manager.load()
        metadata2 = metadata_manager.load()

        # Should return same object (cached)
        assert metadata1 is metadata2


class TestMetadataSave:
    """Tests for metadata saving."""

    def test_save_creates_directory(self, metadata_manager, temp_aptly_root):
        """Test save() creates metadata directory if it doesn't exist."""
        metadata = {"repositories": [], "last_updated": "2025-11-07"}

        metadata_manager.save(metadata)

        assert (temp_aptly_root / ".repomanager").exists()
        assert (temp_aptly_root / ".repomanager" / "metadata.json").exists()

    def test_save_writes_json(self, metadata_manager):
        """Test save() writes valid JSON."""
        test_metadata = {
            "repositories": [
                {"codename": "bookworm", "component": "tools", "created": "2025-11-07"}
            ],
            "last_updated": "2025-11-07T10:00:00",
        }

        metadata_manager.save(test_metadata)

        # Read back and verify
        with metadata_manager.metadata_path.open("r") as f:
            saved_data = json.load(f)

        assert len(saved_data["repositories"]) == 1
        assert saved_data["repositories"][0]["codename"] == "bookworm"

    def test_save_updates_timestamp(self, metadata_manager):
        """Test save() updates last_updated timestamp."""
        metadata = {"repositories": [], "last_updated": "old_timestamp"}

        metadata_manager.save(metadata)

        # Read back
        with metadata_manager.metadata_path.open("r") as f:
            saved_data = json.load(f)

        # Timestamp should be updated
        assert saved_data["last_updated"] != "old_timestamp"

    def test_save_uses_cached_metadata_if_none(self, metadata_manager):
        """Test save() uses cached metadata if argument is None."""
        # Load to populate cache
        metadata_manager.load()
        metadata_manager._metadata["repositories"].append(
            {"codename": "test", "component": "test", "created": "2025-11-07"}
        )

        # Save without argument
        metadata_manager.save()

        # Verify saved
        with metadata_manager.metadata_path.open("r") as f:
            saved_data = json.load(f)

        assert len(saved_data["repositories"]) == 1

    def test_save_raises_error_if_no_metadata(self, metadata_manager):
        """Test save() raises error if no metadata to save."""
        with pytest.raises(MetadataError, match="No metadata to save"):
            metadata_manager.save(None)

    def test_save_permission_error(self, metadata_manager, temp_aptly_root, mocker):
        """Test save() raises MetadataError on permission error."""
        metadata = {"repositories": [], "last_updated": "2025-11-07"}

        # Mock Path.open to raise PermissionError
        mock_path_open = mocker.patch.object(Path, "open")
        mock_path_open.side_effect = PermissionError("Access denied")

        with pytest.raises(MetadataError, match="Failed to write metadata"):
            metadata_manager.save(metadata)


class TestAddRepository:
    """Tests for adding repositories to metadata."""

    def test_add_repository_new(self, metadata_manager):
        """Test adding new repository to metadata."""
        metadata_manager.add_repository("bookworm", "tools")

        metadata = metadata_manager.load()
        repos = metadata["repositories"]

        assert len(repos) == 1
        assert repos[0]["codename"] == "bookworm"
        assert repos[0]["component"] == "tools"
        assert "created" in repos[0]

    def test_add_repository_duplicate_skipped(self, metadata_manager):
        """Test adding duplicate repository is skipped."""
        metadata_manager.add_repository("bookworm", "tools")
        metadata_manager.add_repository("bookworm", "tools")  # Duplicate

        metadata = metadata_manager.load()
        repos = metadata["repositories"]

        # Should only have one entry
        assert len(repos) == 1

    def test_add_multiple_repositories(self, metadata_manager):
        """Test adding multiple different repositories."""
        metadata_manager.add_repository("bookworm", "tools")
        metadata_manager.add_repository("noble", "armbian")
        metadata_manager.add_repository("bookworm", "bsp")

        metadata = metadata_manager.load()
        repos = metadata["repositories"]

        assert len(repos) == 3


class TestRemoveRepository:
    """Tests for removing repositories from metadata."""

    def test_remove_repository_exists(self, metadata_manager):
        """Test removing existing repository."""
        metadata_manager.add_repository("bookworm", "tools")
        metadata_manager.add_repository("noble", "armbian")

        metadata_manager.remove_repository("bookworm", "tools")

        metadata = metadata_manager.load()
        repos = metadata["repositories"]

        assert len(repos) == 1
        assert repos[0]["codename"] == "noble"

    def test_remove_repository_not_exists(self, metadata_manager):
        """Test removing non-existent repository doesn't error."""
        metadata_manager.add_repository("bookworm", "tools")

        # Remove non-existent - should not raise
        metadata_manager.remove_repository("noble", "armbian")

        metadata = metadata_manager.load()
        repos = metadata["repositories"]

        assert len(repos) == 1  # Original still there


class TestListRepositories:
    """Tests for listing repositories."""

    def test_list_all_repositories(self, metadata_manager):
        """Test listing all repositories."""
        metadata_manager.add_repository("bookworm", "tools")
        metadata_manager.add_repository("noble", "armbian")

        repos = metadata_manager.list_repositories()

        assert len(repos) == 2

    def test_list_repositories_by_codename(self, metadata_manager):
        """Test filtering repositories by codename."""
        metadata_manager.add_repository("bookworm", "tools")
        metadata_manager.add_repository("bookworm", "armbian")
        metadata_manager.add_repository("noble", "tools")

        repos = metadata_manager.list_repositories("bookworm")

        assert len(repos) == 2
        assert all(r["codename"] == "bookworm" for r in repos)

    def test_list_repositories_empty(self, metadata_manager):
        """Test listing when no repositories exist."""
        repos = metadata_manager.list_repositories()

        assert repos == []


class TestSyncFromAptly:
    """Tests for syncing metadata from aptly state."""

    def test_sync_no_aptly_root(self, metadata_manager, temp_aptly_root, mocker):
        """Test sync when aptly_root_base doesn't exist."""
        # Don't create the directory
        mock_manager = mocker.Mock()

        count = metadata_manager.sync_from_aptly(mock_manager)

        assert count == 0

        # Metadata should be saved (empty)
        metadata = metadata_manager.load()
        assert metadata["repositories"] == []

    def test_sync_finds_repositories(self, metadata_manager, temp_aptly_root, mocker):
        """Test sync finds and adds repositories from aptly."""
        # Create aptly structure
        bookworm_dir = temp_aptly_root / "bookworm"
        bookworm_dir.mkdir(parents=True)
        (bookworm_dir / "aptly.conf").touch()

        noble_dir = temp_aptly_root / "noble"
        noble_dir.mkdir(parents=True)
        (noble_dir / "aptly.conf").touch()

        # Mock aptly_manager.list_repos
        mock_manager = mocker.Mock()
        mock_manager.list_repos.side_effect = lambda codename: (
            ["tools-bookworm", "armbian-bookworm"]
            if codename == "bookworm"
            else ["tools-noble"] if codename == "noble" else []
        )

        count = metadata_manager.sync_from_aptly(mock_manager)

        assert count == 3

        # Verify metadata
        repos = metadata_manager.list_repositories()
        assert len(repos) == 3

    def test_sync_skips_metadata_directory(
        self, metadata_manager, temp_aptly_root, mocker
    ):
        """Test sync skips .repomanager directory."""
        # Create .repomanager directory
        (temp_aptly_root / ".repomanager").mkdir(parents=True)
        (temp_aptly_root / ".repomanager" / "aptly.conf").touch()

        # Create valid codename directory
        bookworm_dir = temp_aptly_root / "bookworm"
        bookworm_dir.mkdir(parents=True)
        (bookworm_dir / "aptly.conf").touch()

        mock_manager = mocker.Mock()
        mock_manager.list_repos.return_value = ["tools-bookworm"]

        count = metadata_manager.sync_from_aptly(mock_manager)

        # Should only find bookworm, not .repomanager
        assert count == 1

    def test_sync_skips_non_aptly_directories(
        self, metadata_manager, temp_aptly_root, mocker
    ):
        """Test sync skips directories without aptly.conf."""
        # Create directory without aptly.conf
        (temp_aptly_root / "not-aptly").mkdir(parents=True)

        # Create valid directory
        bookworm_dir = temp_aptly_root / "bookworm"
        bookworm_dir.mkdir(parents=True)
        (bookworm_dir / "aptly.conf").touch()

        mock_manager = mocker.Mock()
        mock_manager.list_repos.return_value = ["tools-bookworm"]

        count = metadata_manager.sync_from_aptly(mock_manager)

        assert count == 1

    def test_sync_handles_list_repos_error(
        self, metadata_manager, temp_aptly_root, mocker
    ):
        """Test sync handles errors when listing repos."""
        # Create valid directory
        bookworm_dir = temp_aptly_root / "bookworm"
        bookworm_dir.mkdir(parents=True)
        (bookworm_dir / "aptly.conf").touch()

        # Mock to raise exception
        mock_manager = mocker.Mock()
        mock_manager.list_repos.side_effect = Exception("Aptly error")

        # Should not crash, just log warning
        count = metadata_manager.sync_from_aptly(mock_manager)

        assert count == 0

    def test_sync_parses_repo_names_correctly(
        self, metadata_manager, temp_aptly_root, mocker
    ):
        """Test sync correctly parses component from repo name."""
        bookworm_dir = temp_aptly_root / "bookworm"
        bookworm_dir.mkdir(parents=True)
        (bookworm_dir / "aptly.conf").touch()

        mock_manager = mocker.Mock()
        mock_manager.list_repos.return_value = [
            "jethome-tools-bookworm",
            "my-custom-repo-bookworm",
        ]

        count = metadata_manager.sync_from_aptly(mock_manager)

        assert count == 2

        repos = metadata_manager.list_repositories()
        components = [r["component"] for r in repos]
        assert "jethome-tools" in components
        assert "my-custom-repo" in components


class TestMetadataDirectory:
    """Tests for metadata directory management."""

    def test_ensure_metadata_dir_creates(self, metadata_manager, temp_aptly_root):
        """Test _ensure_metadata_dir creates directory."""
        assert not metadata_manager.metadata_dir.exists()

        metadata_manager._ensure_metadata_dir()

        assert metadata_manager.metadata_dir.exists()
        assert metadata_manager.metadata_dir.is_dir()

    def test_ensure_metadata_dir_idempotent(self, metadata_manager):
        """Test _ensure_metadata_dir can be called multiple times."""
        metadata_manager._ensure_metadata_dir()
        metadata_manager._ensure_metadata_dir()  # Should not error

        assert metadata_manager.metadata_dir.exists()

    def test_ensure_metadata_dir_permission_error(self, metadata_manager, mocker):
        """Test _ensure_metadata_dir handles permission errors."""
        mocker.patch.object(Path, "mkdir", side_effect=PermissionError("Access denied"))

        with pytest.raises(MetadataError, match="Failed to create metadata directory"):
            metadata_manager._ensure_metadata_dir()


class TestMetadataEdgeCases:
    """Edge case tests for metadata management."""

    def test_load_file_read_error(self, metadata_manager, temp_aptly_root):
        """Test load() handles file read errors with corrupted JSON."""
        # Create corrupted file (empty file causes JSONDecodeError)
        metadata_dir = temp_aptly_root / ".repomanager"
        metadata_dir.mkdir(parents=True)
        metadata_file = metadata_dir / "metadata.json"
        metadata_file.write_text("")  # Empty file = corrupted

        # Reset cache
        metadata_manager._metadata = None

        with pytest.raises(MetadataError, match="Corrupted metadata"):
            metadata_manager.load()

    def test_load_os_error(self, metadata_manager, temp_aptly_root, mocker):
        """Test load() handles OS errors when reading file."""
        # Create metadata file
        metadata_dir = temp_aptly_root / ".repomanager"
        metadata_dir.mkdir(parents=True)
        metadata_file = metadata_dir / "metadata.json"
        metadata_file.write_text('{"repositories": []}')

        # Reset cache
        metadata_manager._metadata = None

        # Mock Path.open to raise OSError
        original_open = Path.open

        def mock_open(self, *args, **kwargs):
            if self.name == "metadata.json" and "r" in args:
                raise OSError("I/O error")
            return original_open(self, *args, **kwargs)

        mocker.patch.object(Path, "open", mock_open)

        with pytest.raises(MetadataError, match="Failed to read metadata"):
            metadata_manager.load()

    def test_sync_skips_file_not_directory(
        self, metadata_manager, temp_aptly_root, mocker
    ):
        """Test sync skips files (not directories) in aptly_root_base."""
        # Create aptly root base first
        temp_aptly_root.mkdir(parents=True, exist_ok=True)

        # Create a file instead of directory
        (temp_aptly_root / "somefile.txt").touch()

        # Create valid directory
        bookworm_dir = temp_aptly_root / "bookworm"
        bookworm_dir.mkdir(parents=True)
        (bookworm_dir / "aptly.conf").touch()

        mock_manager = mocker.Mock()
        mock_manager.list_repos.return_value = ["tools-bookworm"]

        count = metadata_manager.sync_from_aptly(mock_manager)

        # Should only find bookworm (skip the file)
        assert count == 1
