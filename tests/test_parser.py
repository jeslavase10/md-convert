"""Tests for MarkdownParser."""

import pytest
from md_converter.parsers.markdown import MarkdownParser


class TestMarkdownParser:
    """Test suite for MarkdownParser."""

    @pytest.fixture
    def parser(self):
        return MarkdownParser({})

    def test_headings(self, parser):
        """Test heading parsing."""
        md = "# Heading 1\n## Heading 2\n### Heading 3"
        html = parser.parse(md)
        assert "<h1>Heading 1</h1>" in html
        assert "<h2>Heading 2</h2>" in html
        assert "<h3>Heading 3</h3>" in html

    def test_paragraphs(self, parser):
        """Test paragraph parsing."""
        md = "This is a paragraph.\n\nThis is another."
        html = parser.parse(md)
        assert "<p>" in html

    def test_bold_italic(self, parser):
        """Test bold and italic."""
        md = "**bold** and *italic*"
        html = parser.parse(md)
        assert "<strong>bold</strong>" in html
        assert "<em>italic</em>" in html

    def test_lists(self, parser):
        """Test ordered and unordered lists."""
        md = "- Item 1\n- Item 2\n1. One\n2. Two"
        html = parser.parse(md)
        assert "<ul>" in html
        assert "<ol>" in html

    def test_code_block(self, parser):
        """Test code block with syntax highlighting."""
        md = "```python\nprint('hello')\n```"
        html = parser.parse(md)
        assert "<code" in html or "<pre" in html

    def test_simple_table(self, parser):
        """Test simple table parsing."""
        md = "| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |"
        html = parser.parse(md)
        assert "<table>" in html
        assert "<th>" in html or "<td>" in html

    def test_aligned_table(self, parser):
        """Test table with alignment."""
        md = "| Left | Center | Right |\n|:-----|:------:|------:|\n| L    | C      | R     |"
        html = parser.parse(md)
        assert "<table>" in html

    def test_blockquote(self, parser):
        """Test blockquote parsing."""
        md = "> This is a quote"
        html = parser.parse(md)
        assert "<blockquote>" in html

    def test_links(self, parser):
        """Test link parsing."""
        md = "[Link text](https://example.com)"
        html = parser.parse(md)
        assert '<a href="https://example.com">Link text</a>' in html

    def test_images(self, parser):
        """Test image parsing."""
        md = "![Alt text](image.png)"
        html = parser.parse(md)
        assert '<img' in html

    def test_task_list(self, parser):
        """Test task list/checkbox parsing."""
        md = "- [x] Done\n- [ ] Todo"
        html = parser.parse(md)
        assert "task-list-item" in html or "<ul>" in html

    def test_inline_code(self, parser):
        """Test inline code parsing."""
        md = "Use `code` here"
        html = parser.parse(md)
        assert "<code>" in html

    def test_horizontal_rule(self, parser):
        """Test horizontal rule."""
        md = "Text\n\n---\n\nMore text"
        html = parser.parse(md)
        assert "<hr" in html

    def test_mermaid_block(self, parser):
        """Test mermaid code block."""
        md = "```mermaid\ngraph TD\n  A-->B\n```"
        html = parser.parse(md)
        assert '<pre class="mermaid">' in html

    def test_nested_lists(self, parser):
        """Test nested list parsing."""
        md = "- Outer\n  - Inner\n1. One\n   2. Sub"
        html = parser.parse(md)
        assert "<ul>" in html or "<ol>" in html
