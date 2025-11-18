"""Tests for init-config command."""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from io import StringIO

from sptbuild.commands import init_config


class TestInitConfig:
    """Test init-config command."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Store original directory and stdout
        self.original_dir = os.getcwd()
        self.original_stdout = sys.stdout

        yield

        # Cleanup: restore original directory and stdout
        os.chdir(self.original_dir)
        sys.stdout = self.original_stdout

    def test_create_default_file(self, tmp_path):
        """Test creating plugin.toml in current directory."""
        os.chdir(tmp_path)

        init_config.run([])

        # Check file was created
        assert os.path.exists("plugin.toml")

        # Verify content
        with open("plugin.toml") as f:
            content = f.read()
            assert "[bundle]" in content
            assert "files = [" in content
            assert "directories = [" in content
            assert "BepInEx/plugins/" in content

    def test_create_custom_output_file(self, tmp_path):
        """Test creating file with custom output path."""
        os.chdir(tmp_path)

        custom_file = "my-config.toml"
        init_config.run(['--output', custom_file])

        # Check file was created
        assert os.path.exists(custom_file)

        # Verify content
        with open(custom_file) as f:
            content = f.read()
            assert "[bundle]" in content

    def test_output_to_stdout(self, tmp_path):
        """Test outputting to stdout."""
        os.chdir(tmp_path)

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        init_config.run(['--output', '-'])

        # Restore stdout
        sys.stdout = self.original_stdout

        # Verify output
        content = captured_output.getvalue()
        assert "[bundle]" in content
        assert "files = [" in content
        assert "directories = [" in content

        # Verify no file was created
        assert not os.path.exists("plugin.toml")

    def test_refuse_overwrite_without_force(self, tmp_path):
        """Test that existing file is not overwritten without --force."""
        os.chdir(tmp_path)

        # Create initial file
        with open("plugin.toml", "w") as f:
            f.write("initial content")

        # Try to create again without force
        with pytest.raises(SystemExit) as exc_info:
            init_config.run([])

        assert exc_info.value.code == 1

        # Verify original content is preserved
        with open("plugin.toml") as f:
            assert f.read() == "initial content"

    def test_overwrite_with_force(self, tmp_path):
        """Test that existing file is overwritten with --force."""
        os.chdir(tmp_path)

        # Create initial file
        with open("plugin.toml", "w") as f:
            f.write("initial content")

        # Overwrite with force
        init_config.run(['--force'])

        # Verify new content
        with open("plugin.toml") as f:
            content = f.read()
            assert "initial content" not in content
            assert "[bundle]" in content

    def test_custom_file_with_force(self, tmp_path):
        """Test overwriting custom file with --force."""
        os.chdir(tmp_path)

        custom_file = "custom.toml"

        # Create initial file
        with open(custom_file, "w") as f:
            f.write("old content")

        # Overwrite with force
        init_config.run(['--force', '--output', custom_file])

        # Verify new content
        with open(custom_file) as f:
            content = f.read()
            assert "old content" not in content
            assert "[bundle]" in content

    def test_content_format(self, tmp_path):
        """Test that generated content has expected format."""
        os.chdir(tmp_path)

        init_config.run([])

        with open("plugin.toml") as f:
            content = f.read()

            # Check for all major sections
            assert "# Plugin bundling configuration" in content
            assert "[bundle]" in content
            assert "files = [" in content
            assert "directories = [" in content
            assert "[[bundle.custom]]" in content

            # Check for helpful comments
            assert "README.md" in content
            assert "relative to project root" in content
            assert "Example resulting zip structure:" in content

    def test_create_file_io_error(self, tmp_path):
        """Test that IO errors are handled when creating file."""
        os.chdir(tmp_path)

        # Create a directory with the same name as target file
        os.makedirs("plugin.toml")

        # Try to create file (should fail because it's a directory)
        with pytest.raises(SystemExit) as exc_info:
            init_config.run([])

        assert exc_info.value.code == 1
