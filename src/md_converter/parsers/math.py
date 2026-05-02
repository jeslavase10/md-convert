"""Math expression parser using matplotlib for rendering."""

import re
import tempfile
import base64
from pathlib import Path
from rich.console import Console

console = Console()


class MathParser:
    """Process Math/LaTeX blocks in content."""

    MATH_BLOCK_PATTERN = re.compile(r'\$\$([^\$]+)\$\$', re.DOTALL)
    MATH_INLINE_PATTERN = re.compile(r'\$([^\$]+)\$', re.DOTALL)

    def __init__(self, config=None):
        self.config = config or {}
        math_config = self.config.get("math", {})
        self.enabled = math_config.get("enabled", True)
        self.renderer = math_config.get("renderer", "matplotlib")

    def process(self, content: str) -> str:
        """Process math expressions."""
        if not self.enabled:
            return content

        def replace_block(match):
            math_code = match.group(1)
            return self._render_math(math_code)

        content = self.MATH_BLOCK_PATTERN.sub(replace_block, content)
        content = self.MATH_INLINE_PATTERN.sub(
            lambda m: f'<span class="math-inline">{m.group(1)}</span>',
            content
        )
        return content

    def _render_math(self, code: str) -> str:
        """Render LaTeX math to image using matplotlib."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.mathtext as mathtext
        except ImportError:
            return f'<code class="math">{code}</code>'

        try:
            buffer = tempfile.SpooledTemporaryFile()
            fig = plt.figure(figsize=(6, 1))
            fig.text(0.5, 0.5, f'${code}$', fontsize=12, ha='center', va='center')
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            plt.close(fig)
            buffer.seek(0)
            b64 = base64.b64encode(buffer.read()).decode()
            buffer.close()
            return f'<img src="data:image/png;base64,{b64}" class="math-block">'
        except Exception as e:
            console.print(f"[yellow]Math render error: {e}[/yellow]")
            return f'<code class="math">{code}</code>'
