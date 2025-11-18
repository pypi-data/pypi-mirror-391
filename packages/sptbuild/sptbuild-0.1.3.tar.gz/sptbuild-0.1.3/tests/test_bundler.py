"""Tests for plugin bundling functionality."""

import os
import shutil
import tempfile
import pytest
from pathlib import Path

from sptbuild.plugin_config import PluginConfig
from sptbuild.bundler import FileBundler


class TestPluginConfig:
    """Test PluginConfig class."""

    def test_no_config_file(self, tmp_path):
        """Test when plugin.toml doesn't exist."""
        os.chdir(tmp_path)
        config = PluginConfig()
        assert not config.has_config()
        assert config.get_files() == []
        assert config.get_directories() == []
        assert config.get_custom_mappings() == []
        assert config.get_package_name_override() is None

    def test_basic_files_config(self):
        """Test loading plugin.toml with basic files."""
        fixture_dir = Path(__file__).parent / "fixtures" / "basic_files"
        os.chdir(fixture_dir)

        config = PluginConfig()
        assert config.has_config()

        files = config.get_files()
        assert "README.md" in files
        assert "LICENSE.txt" in files
        assert "config/settings.json" in files
        assert len(files) == 3

    def test_directories_config(self):
        """Test loading plugin.toml with directories."""
        fixture_dir = Path(__file__).parent / "fixtures" / "with_directories"
        os.chdir(fixture_dir)

        config = PluginConfig()
        assert config.has_config()

        dirs = config.get_directories()
        assert "assets" in dirs
        assert "data/localization" in dirs
        assert len(dirs) == 2

    def test_custom_mappings_config(self):
        """Test loading plugin.toml with custom mappings."""
        fixture_dir = Path(__file__).parent / "fixtures" / "custom_mappings"
        os.chdir(fixture_dir)

        config = PluginConfig()
        assert config.has_config()

        custom = config.get_custom_mappings()
        assert len(custom) == 2

        assert custom[0]["source"] == "docs/UserGuide.md"
        assert custom[0]["destination"] == "GUIDE.md"

        assert custom[1]["source"] == "configs/default.json"
        assert custom[1]["destination"] == "config/default.json"

    def test_invalid_toml_syntax(self, tmp_path):
        """Test that invalid TOML syntax causes an error."""
        os.chdir(tmp_path)

        # Create invalid TOML file
        with open("plugin.toml", "w") as f:
            f.write("[bundle\n")  # Missing closing bracket
            f.write("files = []\n")

        with pytest.raises(SystemExit) as exc_info:
            PluginConfig()

        assert exc_info.value.code == 1

    def test_files_not_a_list(self, tmp_path):
        """Test that non-list files value causes an error."""
        os.chdir(tmp_path)

        with open("plugin.toml", "w") as f:
            f.write('[bundle]\nfiles = "not a list"\n')

        config = PluginConfig()
        with pytest.raises(SystemExit) as exc_info:
            config.get_files()

        assert exc_info.value.code == 1

    def test_directories_not_a_list(self, tmp_path):
        """Test that non-list directories value causes an error."""
        os.chdir(tmp_path)

        with open("plugin.toml", "w") as f:
            f.write('[bundle]\ndirectories = "not a list"\n')

        config = PluginConfig()
        with pytest.raises(SystemExit) as exc_info:
            config.get_directories()

        assert exc_info.value.code == 1

    def test_custom_not_a_list(self, tmp_path):
        """Test that non-list custom value causes an error."""
        os.chdir(tmp_path)

        with open("plugin.toml", "w") as f:
            f.write('[bundle]\ncustom = "not a list"\n')

        config = PluginConfig()
        with pytest.raises(SystemExit) as exc_info:
            config.get_custom_mappings()

        assert exc_info.value.code == 1

    def test_custom_mapping_not_a_dict(self, tmp_path):
        """Test that non-dict custom mapping causes an error."""
        os.chdir(tmp_path)

        with open("plugin.toml", "w") as f:
            f.write('[bundle]\ncustom = ["not a dict"]\n')

        config = PluginConfig()
        with pytest.raises(SystemExit) as exc_info:
            config.get_custom_mappings()

        assert exc_info.value.code == 1

    def test_custom_mapping_missing_source(self, tmp_path):
        """Test that custom mapping without source causes an error."""
        os.chdir(tmp_path)

        with open("plugin.toml", "w") as f:
            f.write('[[bundle.custom]]\ndestination = "dest.txt"\n')

        config = PluginConfig()
        with pytest.raises(SystemExit) as exc_info:
            config.get_custom_mappings()

        assert exc_info.value.code == 1

    def test_custom_mapping_missing_destination(self, tmp_path):
        """Test that custom mapping without destination causes an error."""
        os.chdir(tmp_path)

        with open("plugin.toml", "w") as f:
            f.write('[[bundle.custom]]\nsource = "src.txt"\n')

        config = PluginConfig()
        with pytest.raises(SystemExit) as exc_info:
            config.get_custom_mappings()

        assert exc_info.value.code == 1

    def test_package_name_override(self, tmp_path):
        """Test package name override."""
        os.chdir(tmp_path)

        with open("plugin.toml", "w") as f:
            f.write('[package]\nname = "OverriddenName"\n')

        config = PluginConfig()
        assert config.get_package_name_override() == "OverriddenName"


class TestFileBundler:
    """Test FileBundler class."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Store original directory
        self.original_dir = os.getcwd()

        yield

        # Cleanup: restore original directory
        os.chdir(self.original_dir)

    def _create_dest_dir(self, tmp_path):
        """Create a destination directory for bundling."""
        dest_dir = tmp_path / "zipdir" / "BepInEx" / "plugins" / "TestPlugin"
        dest_dir.mkdir(parents=True, exist_ok=True)
        return str(dest_dir)

    def _cleanup_dest_dir(self, dest_dir):
        """Remove destination directory."""
        zipdir = Path(dest_dir).parent.parent.parent
        if zipdir.exists():
            shutil.rmtree(zipdir)

    def test_bundle_basic_files(self, tmp_path):
        """Test bundling basic files."""
        fixture_dir = Path(__file__).parent / "fixtures" / "basic_files"
        os.chdir(fixture_dir)

        dest_dir = self._create_dest_dir(tmp_path)
        config = PluginConfig()
        bundler = FileBundler(dest_dir)

        bundler.bundle_from_config(config)

        # Check that specified files were copied
        assert os.path.exists(os.path.join(dest_dir, "README.md"))
        assert os.path.exists(os.path.join(dest_dir, "LICENSE.txt"))
        assert os.path.exists(os.path.join(dest_dir, "config", "settings.json"))

        # Check that unspecified files were NOT copied
        assert not os.path.exists(os.path.join(dest_dir, "SHOULD_NOT_COPY.txt"))

        # Verify file contents
        with open(os.path.join(dest_dir, "README.md")) as f:
            assert "Test Plugin" in f.read()

        self._cleanup_dest_dir(dest_dir)

    def test_bundle_directories(self, tmp_path):
        """Test bundling entire directories."""
        fixture_dir = Path(__file__).parent / "fixtures" / "with_directories"
        os.chdir(fixture_dir)

        dest_dir = self._create_dest_dir(tmp_path)
        config = PluginConfig()
        bundler = FileBundler(dest_dir)

        bundler.bundle_from_config(config)

        # Check that files were copied
        assert os.path.exists(os.path.join(dest_dir, "README.md"))

        # Check that directories were copied
        assert os.path.exists(os.path.join(dest_dir, "assets", "icon.png"))
        assert os.path.exists(os.path.join(dest_dir, "assets", "banner.jpg"))
        assert os.path.exists(os.path.join(dest_dir, "data", "localization", "en.json"))
        assert os.path.exists(os.path.join(dest_dir, "data", "localization", "fr.json"))

        # Check that other directories were NOT copied
        assert not os.path.exists(os.path.join(dest_dir, "data", "other"))
        assert not os.path.exists(os.path.join(dest_dir, "data", "other", "should_not_copy.txt"))

        self._cleanup_dest_dir(dest_dir)

    def test_bundle_custom_mappings(self, tmp_path):
        """Test bundling with custom source->destination mappings."""
        fixture_dir = Path(__file__).parent / "fixtures" / "custom_mappings"
        os.chdir(fixture_dir)

        dest_dir = self._create_dest_dir(tmp_path)
        config = PluginConfig()
        bundler = FileBundler(dest_dir)

        bundler.bundle_from_config(config)

        # Check that regular files were copied
        assert os.path.exists(os.path.join(dest_dir, "README.md"))

        # Check that custom mappings were applied
        # docs/UserGuide.md -> GUIDE.md
        assert os.path.exists(os.path.join(dest_dir, "GUIDE.md"))
        assert not os.path.exists(os.path.join(dest_dir, "docs", "UserGuide.md"))

        # configs/default.json -> config/default.json
        assert os.path.exists(os.path.join(dest_dir, "config", "default.json"))
        assert not os.path.exists(os.path.join(dest_dir, "configs", "default.json"))

        # Verify content
        with open(os.path.join(dest_dir, "GUIDE.md")) as f:
            assert "User Guide" in f.read()

        self._cleanup_dest_dir(dest_dir)

    def test_no_config_bundling(self, tmp_path):
        """Test that bundling works when there's no plugin.toml."""
        fixture_dir = Path(__file__).parent / "fixtures" / "no_config"
        os.chdir(fixture_dir)

        dest_dir = self._create_dest_dir(tmp_path)
        config = PluginConfig()
        bundler = FileBundler(dest_dir)

        # Should not raise an error
        bundler.bundle_from_config(config)

        # No files should be bundled
        files = list(Path(dest_dir).rglob("*"))
        assert len(files) == 0  # Only the directory itself, no files

        self._cleanup_dest_dir(dest_dir)

    def test_missing_file_error(self, tmp_path):
        """Test that missing files cause an error."""
        fixture_dir = Path(__file__).parent / "fixtures" / "missing_files"
        os.chdir(fixture_dir)

        dest_dir = self._create_dest_dir(tmp_path)
        config = PluginConfig()
        bundler = FileBundler(dest_dir)

        # Should exit with error when trying to bundle non-existent file
        with pytest.raises(SystemExit) as exc_info:
            bundler.bundle_from_config(config)

        assert exc_info.value.code == 1

        self._cleanup_dest_dir(dest_dir)

    def test_bundle_file_not_a_file(self, tmp_path):
        """Test that bundling a directory as a file causes an error."""
        os.chdir(tmp_path)
        os.makedirs("somedir")

        dest_dir = self._create_dest_dir(tmp_path)
        bundler = FileBundler(dest_dir)

        with pytest.raises(SystemExit) as exc_info:
            bundler.bundle_file("somedir")

        assert exc_info.value.code == 1
        self._cleanup_dest_dir(dest_dir)

    def test_bundle_directory_not_a_directory(self, tmp_path):
        """Test that bundling a file as a directory causes an error."""
        os.chdir(tmp_path)
        with open("somefile.txt", "w") as f:
            f.write("test")

        dest_dir = self._create_dest_dir(tmp_path)
        bundler = FileBundler(dest_dir)

        with pytest.raises(SystemExit) as exc_info:
            bundler.bundle_directory("somefile.txt")

        assert exc_info.value.code == 1
        self._cleanup_dest_dir(dest_dir)

    def test_custom_mapping_invalid_type(self, tmp_path):
        """Test that custom mapping with invalid source type causes error."""
        os.chdir(tmp_path)

        # Create a test config with custom mapping
        with open("plugin.toml", "w") as f:
            f.write('[[bundle.custom]]\n')
            f.write('source = "nonexistent"\n')
            f.write('destination = "dest"\n')

        # Create a device file or something that's neither file nor directory
        # For testing, we'll just use a path that doesn't exist
        dest_dir = self._create_dest_dir(tmp_path)
        config = PluginConfig()
        bundler = FileBundler(dest_dir)

        with pytest.raises(SystemExit) as exc_info:
            bundler.bundle_from_config(config)

        assert exc_info.value.code == 1
        self._cleanup_dest_dir(dest_dir)

    def test_custom_mapping_with_directory(self, tmp_path):
        """Test custom mapping that points to a directory."""
        os.chdir(tmp_path)

        # Create source directory
        os.makedirs("source_dir/subdir")
        with open("source_dir/subdir/file.txt", "w") as f:
            f.write("content")

        # Create config with custom mapping for directory
        with open("plugin.toml", "w") as f:
            f.write('[[bundle.custom]]\n')
            f.write('source = "source_dir"\n')
            f.write('destination = "renamed_dir"\n')

        dest_dir = self._create_dest_dir(tmp_path)
        config = PluginConfig()
        bundler = FileBundler(dest_dir)

        bundler.bundle_from_config(config)

        # Verify directory was copied with custom name
        assert os.path.exists(os.path.join(dest_dir, "renamed_dir", "subdir", "file.txt"))
        with open(os.path.join(dest_dir, "renamed_dir", "subdir", "file.txt")) as f:
            assert f.read() == "content"

        self._cleanup_dest_dir(dest_dir)

    def test_bundle_file_with_custom_destination(self, tmp_path):
        """Test bundling a file to a custom destination."""
        os.chdir(tmp_path)

        # Create source file
        with open("source.txt", "w") as f:
            f.write("test content")

        dest_dir = self._create_dest_dir(tmp_path)
        bundler = FileBundler(dest_dir)

        bundler.bundle_file("source.txt", "custom/path/dest.txt")

        # Verify file was copied to custom location
        assert os.path.exists(os.path.join(dest_dir, "custom", "path", "dest.txt"))
        with open(os.path.join(dest_dir, "custom", "path", "dest.txt")) as f:
            assert f.read() == "test content"

        self._cleanup_dest_dir(dest_dir)

    def test_bundle_directory_with_custom_destination(self, tmp_path):
        """Test bundling a directory to a custom destination."""
        os.chdir(tmp_path)

        # Create source directory with files
        os.makedirs("source_dir")
        with open("source_dir/file1.txt", "w") as f:
            f.write("content1")
        with open("source_dir/file2.txt", "w") as f:
            f.write("content2")

        dest_dir = self._create_dest_dir(tmp_path)
        bundler = FileBundler(dest_dir)

        bundler.bundle_directory("source_dir", "custom/location")

        # Verify directory was copied to custom location
        assert os.path.exists(os.path.join(dest_dir, "custom", "location", "file1.txt"))
        assert os.path.exists(os.path.join(dest_dir, "custom", "location", "file2.txt"))

        self._cleanup_dest_dir(dest_dir)

    def test_bundle_nested_directories(self, tmp_path):
        """Test bundling deeply nested directory structures."""
        fixture_dir = Path(__file__).parent / "fixtures" / "nested_dirs"
        os.chdir(fixture_dir)

        dest_dir = self._create_dest_dir(tmp_path)
        config = PluginConfig()
        bundler = FileBundler(dest_dir)

        bundler.bundle_from_config(config)

        # Verify nested structure was preserved
        assert os.path.exists(os.path.join(dest_dir, "nested", "file.txt"))
        assert os.path.exists(os.path.join(dest_dir, "nested", "subdir1", "file.txt"))
        assert os.path.exists(os.path.join(dest_dir, "nested", "subdir1", "subdir2", "file.txt"))

        # Verify content
        with open(os.path.join(dest_dir, "nested", "subdir1", "subdir2", "file.txt")) as f:
            assert "deep file" in f.read()

        self._cleanup_dest_dir(dest_dir)
