"""Tests for DOCX renderer."""

import pytest
from pathlib import Path
from docx import Document
from md_converter.parsers.markdown import MarkdownParser
from md_converter.renderers.docx import DOCXRenderer
from md_converter.utils.config import Config


class TestDOCXRenderer:
    """Test suite for DOCXRenderer."""

    @pytest.fixture
    def renderer(self):
        return DOCXRenderer(Config.load())

    @pytest.fixture
    def parser(self):
        return MarkdownParser(Config.load())

    def test_simple_document(self, renderer, tmp_path):
        """Test creating a simple DOCX document."""
        html = "<html><body><h1>Title</h1><p>Paragraph text.</p></body></html>"
        output = tmp_path / "test.docx"
        renderer.render(html, output)
        assert output.exists()

    def test_document_with_table(self, renderer, tmp_path):
        """Test document with table."""
        html = """
        <html><body>
        <table>
            <tr><th>Header</th></tr>
            <tr><td>Cell</td></tr>
        </table>
        </body></html>
        """
        output = tmp_path / "table.docx"
        renderer.render(html, output)
        assert output.exists()
        doc = Document(output)
        assert len(doc.tables) == 1

    def test_document_with_code(self, renderer, tmp_path):
        """Test document with code block."""
        html = "<html><body><pre><code>print('hello')</code></pre></body></html>"
        output = tmp_path / "code.docx"
        renderer.render(html, output)
        assert output.exists()

    def test_document_with_list(self, renderer, tmp_path):
        """Test document with list."""
        html = "<html><body><ul><li>Item 1</li><li>Item 2</li></ul></body></html>"
        output = tmp_path / "list.docx"
        renderer.render(html, output)
        assert output.exists()
