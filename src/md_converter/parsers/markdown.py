"""Markdown parser with extensions support."""

import markdown
from markdown.extensions import extra, tables, codehilite, toc, sane_lists
from pymdownx import superfences, tabbed, details, tasklist, highlight


class MarkdownParser:
    """Parse Markdown to HTML with full extension support."""

    def __init__(self, config=None):
        self.config = config or {}
        self.extensions = self._setup_extensions()

    def _setup_extensions(self):
        return [
            extra,
            tables,
            codehilite,
            toc,
            sane_lists,
            superfences,
            tabbed,
            details,
            tasklist,
            highlight,
        ]

    def _get_configs(self):
        code_config = self.config.get("code", {})
        return {
            "codehilite": {
                "css_class": "highlight",
                "guess_lang": False,
            },
            "toc": {
                "title": "Tabla de Contenidos",
            },
        }

    def parse(self, md_content: str) -> str:
        """Convert Markdown string to HTML."""
        md = markdown.Markdown(
            extensions=self.extensions,
            extension_configs=self._get_configs(),
        )
        return md.convert(md_content)
