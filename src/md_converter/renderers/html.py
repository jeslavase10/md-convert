"""HTML renderer with styles."""

from pathlib import Path

BASE_CSS = """
/* Base styles for Markdown rendering */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: 600;
    line-height: 1.25;
}
h1 { font-size: 2em; border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
h2 { font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
h3 { font-size: 1.25em; }
h4 { font-size: 1em; }

/* Paragraphs */
p { margin: 1em 0; }

/* Lists */
ul, ol { padding-left: 2em; margin: 1em 0; }
li { margin: 0.25em 0; }
li > ul, li > ol { margin: 0.25em 0; }

/* Links */
a { color: #0366d6; text-decoration: none; }
a:hover { text-decoration: underline; }

/* Images */
img { max-width: 100%; height: auto; }

/* Tables */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}
th, td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
}
th {
    background-color: #f8f9fa;
    font-weight: bold;
}
tr:nth-child(even) {
    background-color: #f2f2f2;
}

/* Code */
pre {
    background: #282c34;
    color: #abb2bf;
    padding: 1em;
    border-radius: 8px;
    overflow-x: auto;
    position: relative;
}
code {
    font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
    font-size: 0.9em;
}
:not(pre) > code {
    background: #f0f0f0;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    color: #e05550;
}

/* Blockquotes */
blockquote {
    border-left: 4px solid #ddd;
    margin: 1em 0;
    padding: 0.5em 1em;
    color: #666;
    background: #f9f9f9;
}

/* Horizontal rules */
hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 2em 0;
}

/* Task lists */
.task-list-item {
    list-style-type: none;
    margin-left: -1.5em;
}
.task-list-item input {
    margin-right: 0.5em;
}

/* Mermaid diagrams */
.mermaid-diagram {
    text-align: center;
    margin: 2em 0;
}
.mermaid-error {
    color: #dc3545;
    background: #fff0f0;
    padding: 1em;
    border-radius: 8px;
}
.mermaid-raw {
    background: #f8f8f8;
    padding: 1em;
    border-radius: 8px;
    overflow-x: auto;
}

/* Table of contents */
.toc {
    background: #f8f9fa;
    padding: 1em;
    border-radius: 8px;
    margin: 1em 0;
}
.toc ul {
    margin: 0;
    padding-left: 1.5em;
}
"""


class HTMLRenderer:
    """Render HTML with proper styling."""

    def __init__(self, config=None):
        self.config = config or {}
        self.styles = self.config.get("styles", {})
        self.css = BASE_CSS
        # Load custom CSS if specified
        custom_css = self.styles.get("css")
        if custom_css:
            css_path = Path(custom_css)
            if css_path.exists():
                self.css += "\n" + css_path.read_text()

    def render(self, html_content: str, template: str = "default") -> str:
        """Wrap HTML content with full document structure."""
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
{self.css}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

    def add_custom_css(self, css_path: str) -> None:
        """Load custom CSS from file."""
        path = Path(css_path)
        if path.exists():
            self.css += "\n" + path.read_text()
