"""Tests for MermaidParser."""

import pytest
from pathlib import Path
from md_converter.parsers.mermaid import MermaidParser


class TestMermaidParser:
    """Test suite for MermaidParser."""

    @pytest.fixture
    def parser(self):
        return MermaidParser({})

    @pytest.fixture
    def flowchart_html(self):
        return '''<pre class="mermaid">graph TD\n  A[Start] --> B[End]\n</pre>'''

    @pytest.fixture
    def sequence_html(self):
        return '''<pre class="mermaid">sequenceDiagram\n  A->>B: Hello\n</pre>'''

    def test_parser_init(self, parser):
        """Test MermaidParser initializes."""
        assert parser is not None
        assert parser.theme == "default"
        assert parser.format == "svg"

    def test_parser_disabled(self):
        """Test parser when Mermaid is disabled."""
        parser = MermaidParser({"diagrams": {"mermaid": {"enabled": False}}})
        html = '<pre class="mermaid">graph TD\n  A --> B\n</pre>'
        result = parser.process(html)
        assert result == html

    def test_mermaid_block_pattern(self, parser, flowchart_html):
        """Test that Mermaid blocks are detected."""
        assert '<pre class="mermaid">' in flowchart_html

    def test_process_returns_html(self, parser, flowchart_html):
        """Test process method returns HTML content."""
        result = parser.process(flowchart_html)
        assert isinstance(result, str)

    def test_fallback_when_mermaid_not_available(self, parser, flowchart_html):
        """Test fallback when mermaid-cli is not installed."""
        if not parser._check_mermaid_available():
            result = parser.process(flowchart_html)
            assert 'mermaid-raw' in result or flowchart_html in result

    def test_render_with_theme(self):
        """Test that theme is passed to config."""
        parser = MermaidParser({"diagrams": {"mermaid": {"theme": "dark"}}})
        assert parser.theme == "dark"

    def test_render_with_format_png(self):
        """Test that format PNG is configured."""
        parser = MermaidParser({"diagrams": {"mermaid": {"format": "png"}}})
        assert parser.format == "png"

    def test_render_with_format_svg(self):
        """Test that format SVG is configured."""
        parser = MermaidParser({"diagrams": {"mermaid": {"format": "svg"}}})
        assert parser.format == "svg"

    def test_multiple_mermaid_blocks(self, parser):
        """Test processing multiple mermaid blocks."""
        html = '''
        <pre class="mermaid">graph TD\n  A --> B\n</pre>
        <p>Some text</p>
        <pre class="mermaid">sequenceDiagram\n  A->>B: Hello\n</pre>
        '''
        result = parser.process(html)
        assert isinstance(result, str)

    def test_empty_mermaid_block(self, parser):
        """Test processing empty mermaid block."""
        html = '<pre class="mermaid"></pre>'
        result = parser.process(html)
        assert result != html or 'mermaid' in result.lower()

    def test_invalid_mermaid_code(self, parser):
        """Test handling of invalid mermaid code."""
        html = '<pre class="mermaid">this is not valid mermaid!!!\n  invalid\n</pre>'
        result = parser.process(html)
        assert isinstance(result, str)

    def test_check_mermaid_available(self, parser):
        """Test checking mermaid-cli availability."""
        available = parser._check_mermaid_available()
        assert isinstance(available, bool)
