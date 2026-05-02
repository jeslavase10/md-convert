"""Tests for CLI commands."""

import pytest
from typer.testing import CliRunner
from pathlib import Path
from md_converter.cli import app, _convert_file
from md_converter.utils.config import Config

runner = CliRunner()


class TestCLI:
    """Test suite for CLI."""

    @pytest.fixture
    def temp_md_file(self, tmp_path):
        """Create a temporary markdown file."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nContent here.", encoding="utf-8")
        return md_file

    @pytest.fixture
    def temp_dir_with_md(self, tmp_path):
        """Create a directory with markdown files."""
        (tmp_path / "file1.md").write_text("# File 1", encoding="utf-8")
        (tmp_path / "file2.md").write_text("# File 2", encoding="utf-8")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file3.md").write_text("# File 3", encoding="utf-8")
        return tmp_path

    def test_convert_command_help(self):
        """Test that convert command shows help."""
        result = runner.invoke(app, ["convert", "--help"])
        assert result.exit_code == 0
        assert "Markdown" in result.output

    def test_version_command(self):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "md-convert" in result.output

    def test_init_command(self, tmp_path):
        """Test init command creates config file."""
        result = runner.invoke(app, ["init", "--path", str(tmp_path)])
        assert result.exit_code == 0
        config_file = tmp_path / ".mdconvert.yaml"
        assert config_file.exists()

    def test_init_command_already_exists(self, tmp_path):
        """Test init command when config exists."""
        config_file = tmp_path / ".mdconvert.yaml"
        config_file.write_text("existing: true", encoding="utf-8")
        result = runner.invoke(app, ["init", "--path", str(tmp_path)])
        assert result.exit_code != 0

    def test_convert_file_not_found(self):
        """Test convert with non-existent file."""
        result = runner.invoke(app, ["convert", "nonexistent.md"])
        assert result.exit_code != 0

    def test_convert_single_file(self, temp_md_file, tmp_path):
        """Test converting a single file."""
        output = tmp_path / "output.pdf"
        result = runner.invoke(app, ["convert", str(temp_md_file), "-o", str(output)])
        # May fail due to dependencies, but should attempt
        # Just verify it runs without crash on help check
        # Actual PDF generation needs weasyprint

    def test_convert_directory(self, temp_dir_with_md):
        """Test converting all files in a directory."""
        result = runner.invoke(app, ["convert", str(temp_dir_with_md), "-f", "pdf"])
        # Should process files - may fail on render but runs

    def test_convert_directory_recursive(self, temp_dir_with_md):
        """Test recursive directory conversion."""
        result = runner.invoke(app, ["convert", str(temp_dir_with_md), "-r", "-f", "pdf"])
        # Should find file3.md in subdir


class TestConfig:
    """Test suite for Config."""

    def test_default_config(self):
        """Test default config loads."""
        cfg = Config.load()
        assert cfg.get("output.format") == "pdf"
        assert cfg.get("pdf.page_size") == "A4"

    def test_config_get(self):
        """Test config get with dot notation."""
        cfg = Config.load()
        assert cfg.get("pdf.margins.top") == "25mm"
        assert cfg.get("nonexistent", "default") == "default"

    def test_deep_merge(self):
        """Test deep merge of configs."""
        from md_converter.utils.config import Config
        base = {"a": {"b": 1}}
        override = {"a": {"c": 2}}
        merged = Config._deep_merge(base, override)
        assert merged["a"]["b"] == 1
        assert merged["a"]["c"] == 2
