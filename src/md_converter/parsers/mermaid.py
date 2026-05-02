"""Mermaid diagram parser/processor."""

import subprocess
import tempfile
import re
import base64
import urllib.request
from pathlib import Path
from rich.console import Console

console = Console()


class KrokiRenderer:
    """Render diagrams via Kroki API with offline fallback.

    Supports: mermaid, plantuml, chartjs, and other Kroki-supported diagrams.
    """

    KROKI_URL = "https://kroki.io"

    def __init__(self, config=None):
        self.config = config or {}
        diagram_config = self.config.get("diagrams", {})
        self.enabled = diagram_config.get("enabled", True)
        self.format = diagram_config.get("format", "svg")
        self.timeout = diagram_config.get("timeout", 10)

    def render(self, code: str, diagram_type: str = "mermaid") -> str:
        """Render diagram via Kroki API.

        Args:
            code: Diagram source code
            diagram_type: Type of diagram (mermaid, plantuml, etc.)

        Returns:
            HTML img/svg tag or fallback raw code
        """
        if not self.enabled:
            return f'<pre class="diagram-{diagram_type}">{code}</pre>'

        # Check connectivity first
        if not self._check_connectivity():
            console.print(
                "[yellow]Warning: Kroki.io unreachable. "
                "Diagram rendered as raw code.[/yellow]"
            )
            return f'<pre class="diagram-{diagram_type}-offline">{code}</pre>'

        try:
            encoded = base64.urlsafe_b64encode(code.encode()).decode()
            url = f"{self.KROKI_URL}/{diagram_type}/{self.format}/{encoded}"

            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                content = response.read()

            if self.format == "svg":
                svg = content.decode("utf-8")
                return f'<div class="diagram-{diagram_type}">{svg}</div>'
            else:
                b64 = base64.b64encode(content).decode()
                return f'<img src="data:image/{self.format};base64,{b64}" class="diagram-{diagram_type}">'

        except urllib.error.URLError as e:
            console.print(f"[yellow]Kroki error: {e}. Showing raw diagram.[/yellow]")
            return f'<pre class="diagram-{diagram_type}-error">{code}</pre>'
        except Exception as e:
            console.print(f"[yellow]Diagram render failed: {e}[/yellow]")
            return f'<pre class="diagram-{diagram_type}">{code}</pre>'

    def _check_connectivity(self) -> bool:
        """Check if Kroki.io is reachable."""
        try:
            req = urllib.request.Request(
                f"{self.KROKI_URL}/ping",
                method="HEAD",
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception:
            return False


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
        self.use_kroki = mermaid_config.get("use_kroki", False)
        self._kroki = KrokiRenderer(config)

    def process(self, html_content: str) -> str:
        """Replace Mermaid blocks with rendered images."""
        if not self.enabled:
            return html_content

        def replace_block(match):
            mermaid_code = match.group(1)
            return self._render_mermaid(mermaid_code)

        return self.MERMAID_BLOCK_PATTERN.sub(replace_block, html_content)

    def _render_mermaid(self, code: str) -> str:
        """Generate image from Mermaid code.

        Tries local mmdc first if available, falls back to Kroki API.
        """
        # Try local mermaid-cli first
        if self._check_mermaid_available():
            return self._render_via_mmdc(code)

        # Fall back to Kroki API
        if self.use_kroki:
            return self._kroki.render(code, "mermaid")

        # No renderer available - show raw code
        console.print(
            "[yellow]Warning: mermaid-cli not found. "
            "Install with: npm install -g @mermaid-js/mermaid-cli[/yellow]"
        )
        return f'<pre class="mermaid-raw">{code}</pre>'

    def _render_via_mmdc(self, code: str) -> str:
        """Render using local mermaid-cli (mmdc)."""
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
