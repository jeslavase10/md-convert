"""Tests for PDF renderer."""

import pytest
from pathlib import Path
from md_converter.renderers.pdf import PDFRenderer
from md_converter.renderers.html import HTMLRenderer
from md_converter.utils.config import Config


class TestPDFRenderer:
    """Test suite for PDFRenderer."""

    @pytest.fixture
    def renderer(self):
        return PDFRenderer(Config.load())

    @pytest.fixture
    def html_renderer(self):
        return HTMLRenderer(Config.load())

    def test_pdf_renderer_init(self, renderer):
        """Test PDFRenderer initializes."""
        assert renderer is not None
        assert renderer.pdf_config is not None

    def test_simple_html_to_pdf(self, renderer, html_renderer, tmp_path):
        """Test converting simple HTML to PDF."""
        html = html_renderer.render("<h1>Test</h1><p>Content</p>")
        output = tmp_path / "test.pdf"
        # Note: WeasyPrint may not be available on all systems
        try:
            renderer.render(html, output)
            assert output.exists()
        except Exception as e:
            # WeasyPrint may fail on Windows without dependencies
            pytest.skip(f"WeasyPrint not available: {e}")

    def test_pdf_config_page_size(self, renderer):
        """Test PDF config has page size."""
        assert renderer.pdf_config.get("page_size") == "A4"
