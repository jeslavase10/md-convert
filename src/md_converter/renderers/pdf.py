"""PDF renderer using WeasyPrint."""

from weasyprint import HTML, CSS
from pathlib import Path


class PDFRenderer:
    """Render HTML content to PDF using WeasyPrint."""

    def __init__(self, config=None):
        self.config = config or {}
        self.pdf_config = self.config.get("pdf", {})

    def render(self, html_content: str, output_path: Path) -> None:
        """Convert HTML to PDF."""
        page_config = self.pdf_config
        margins = page_config.get("margins", {})

        css = CSS(string=f"""
            @page {{
                size: {page_config.get("page_size", "A4")};
                margin: {margins.get("top", "25mm")}
                       {margins.get("right", "20mm")}
                       {margins.get("bottom", "25mm")}
                       {margins.get("left", "20mm")};
            }}
            @page :first {{
                @top-center {{
                    content: none;
                }}
            }}
        """)

        html = HTML(string=html_content)
        html.write_pdf(
            output_path,
            stylesheets=[css],
            presentational_hints=True
        )
