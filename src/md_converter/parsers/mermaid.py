"""Mermaid diagram parser/processor."""

import subprocess
import tempfile
import re
import base64
from pathlib import Path
from rich.console import Console

console = Console()


class MermaidParser:
    """Process Mermaid diagram blocks in HTML content."""

    MERMAID_BLOCK_PATTERN = re.compile(
        r'<pre class="mermaid">([^<]+)</pre>',
        re.DOTALL
    )

    def __init__(self, config=None):
        self.config = config or {}
        mermaid_config = self.config.get("diagrams", {}).get("mermaid", {})
        self.theme = mermaid_config.get("theme", "default")
        self.format = mermaid_config.get("format", "svg")
        self.scale = mermaid_config.get("scale", 1)
        self.temp_dir = tempfile.mkdtemp()
        self.enabled = mermaid_config.get("enabled", True)

    def process(self, html_content: str) -> str:
        """Replace Mermaid blocks with rendered images."""
        if not self.enabled:
            return html_content

        if not self._check_mermaid_available():
            console.print(
                "[yellow]Warning: mermaid-cli not found. "
                "Install with: npm install -g @mermaid-js/mermaid-cli[/yellow]"
            )
            return html_content

        def replace_block(match):
            mermaid_code = match.group(1)
            return self._render_mermaid(mermaid_code)

        return self.MERMAID_BLOCK_PATTERN.sub(replace_block, html_content)

    def _render_mermaid(self, code: str) -> str:
        """Generate image from Mermaid code."""
        mmd_file = Path(self.temp_dir) / f"diagram_{abs(hash(code))}.mmd"
        mmd_file.write_text(code.strip(), encoding="utf-8")

        output_file = mmd_file.with_suffix(f".{self.format}")

        try:
            subprocess.run(
                [
                    "mmdc",
                    "-i", str(mmd_file),
                    "-o", str(output_file),
                    "-t", self.theme,
                    "-w", "1200",
                    "-H", "800",
                    "-s", str(self.scale),
                    "--quiet"
                ],
                check=True,
                capture_output=True,
            )

            if self.format == "svg":
                svg_content = output_file.read_text(encoding="utf-8")
                return f'<div class="mermaid-diagram">{svg_content}</div>'
            else:
                b64 = base64.b64encode(output_file.read_bytes()).decode()
                return f'<img src="data:image/png;base64,{b64}" class="mermaid-diagram">'

        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error rendering mermaid: {e.stderr}[/red]")
            return f'<div class="mermaid-error">Error rendering diagram</div>'
        except FileNotFoundError:
            return f'<pre class="mermaid-raw">{code}</pre>'

    def _check_mermaid_available(self) -> bool:
        """Check if mermaid-cli is available."""
        try:
            subprocess.run(["mmdc", "--version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
