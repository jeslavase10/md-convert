"""Core converter module - exposes API for programmatic usage."""

from pathlib import Path
from typing import Union, Optional

from md_converter.parsers.markdown import MarkdownParser
from md_converter.parsers.frontmatter import FrontmatterParser, DocumentMetadata
from md_converter.renderers.pdf import PDFRenderer
from md_converter.renderers.docx import DOCXRenderer
from md_converter.renderers.html import HTMLRenderer
from md_converter.utils.config import Config
from md_converter.utils.hooks import HookManager, HookPhase, get_hooks


class ConversionError(Exception):
    """Raised when conversion fails."""

    pass


class Converter:
    """Main converter class - can be used programmatically via import.

    Usage:
        from md_converter import Converter

        converter = Converter()
        converter.convert("input.md", "output.pdf")

        # Or with custom config
        from md_converter.utils.config import Config
        cfg = Config.load(Path("custom.yaml"))
        converter = Converter(cfg)
        converter.convert("input.md", "output.pdf", format="docx")

        # With hooks
        from md_converter.utils.hooks import HookPhase
        converter.hooks.register("my_hook", HookPhase.POST_CONVERT, lambda ctx: print("Done!"))
        converter.convert("input.md", "output.pdf")
    """

    SUPPORTED_FORMATS = ["pdf", "docx", "html"]

    def __init__(self, config: Config = None, hooks: HookManager = None):
        """Initialize converter with optional config and hooks.

        Args:
            config: Optional Config instance
            hooks: Optional HookManager instance. If None, uses global hooks.
        """
        self.config = config or Config()
        self.frontmatter_parser = FrontmatterParser()
        self.markdown_parser = MarkdownParser(self.config)
        self.html_renderer = HTMLRenderer(self.config)
        self.hooks = hooks or get_hooks()

    def convert(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        format: str = "pdf",
        metadata: Optional[DocumentMetadata] = None,
    ) -> Path:
        """Convert Markdown file to specified format.

        Args:
            input_path: Path to input Markdown file
            output_path: Path to output file (format determined by extension or format arg)
            format: Output format (pdf, docx, html). Overrides output_path extension.
            metadata: Optional metadata to pass to renderer

        Returns:
            Path to output file

        Raises:
            ConversionError: If conversion fails
            FileNotFoundError: If input file doesn't exist
            ValueError: If format is not supported
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        format = format.lower()
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}. Use: {self.SUPPORTED_FORMATS}")

        # Build context for hooks
        context = {
            "input_path": input_path,
            "output_path": output_path,
            "format": format,
            "config": self.config,
        }

        try:
            # PRE_CONVERT hooks
            self.hooks.trigger(HookPhase.PRE_CONVERT, context)

            # Read and parse markdown
            md_content = input_path.read_text(encoding="utf-8")

            # Extract frontmatter if present
            fm_metadata, md_content = self.frontmatter_parser.parse(md_content)
            if metadata is None:
                metadata = fm_metadata

            # Apply frontmatter variables
            if fm_metadata.variables:
                md_content = self.frontmatter_parser.apply_variables(
                    md_content, fm_metadata.variables
                )

            # Parse markdown to HTML
            html_content = self.markdown_parser.parse(md_content)

            # For DOCX: process special elements (math, mermaid)
            if format == "docx":
                html_content = self._process_for_docx(html_content)

            # PRE_RENDER hooks
            self.hooks.trigger(HookPhase.PRE_RENDER, context | {"html_content": html_content})

            # Render output
            if format == "html":
                full_html = self.html_renderer.render(html_content)
                output_path.write_text(full_html, encoding="utf-8")
            elif format == "pdf":
                renderer = PDFRenderer(self.config)
                renderer.render(html_content, output_path)
            elif format == "docx":
                renderer = DOCXRenderer(self.config)
                renderer.render(html_content, output_path)

            # POST_RENDER hooks
            self.hooks.trigger(HookPhase.POST_RENDER, context | {"output_path": output_path})

            # POST_CONVERT hooks
            self.hooks.trigger(HookPhase.POST_CONVERT, context | {"output_path": output_path})

            return output_path

        except Exception as e:
            # ON_ERROR hooks
            error_context = context | {"error": str(e), "exception": e}
            self.hooks.trigger(HookPhase.ON_ERROR, error_context)
            raise ConversionError(f"Failed to convert {input_path}: {e}") from e

    def _process_for_docx(self, html_content: str) -> str:
        """Process HTML content for DOCX output - render math to images."""
        from md_converter.parsers.math import MathParser

        math_parser = MathParser(self.config)
        return math_parser.process(html_content)

    def convert_to_html(self, md_content: str) -> str:
        """Convert Markdown string directly to HTML.

        Args:
            md_content: Markdown content as string

        Returns:
            HTML string
        """
        # Parse frontmatter
        fm_metadata, md_content = self.frontmatter_parser.parse(md_content)

        # Apply variables
        if fm_metadata.variables:
            md_content = self.frontmatter_parser.apply_variables(
                md_content, fm_metadata.variables
            )

        # Parse markdown
        return self.markdown_parser.parse(md_content)

    def convert_streaming(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        format: str = "pdf",
        chunk_size: int = 1000,  # Lines per chunk
    ) -> Path:
        """Convert large Markdown file using streaming mode.

        Processes file in chunks to avoid memory issues with large documents.
        Falls back to standard conversion if file is small enough.

        Args:
            input_path: Path to input Markdown file
            output_path: Path to output file
            format: Output format (pdf, docx, html)
            chunk_size: Number of lines to process per chunk

        Returns:
            Path to output file
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        format = format.lower()
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}. Use: {self.SUPPORTED_FORMATS}")

        file_size = input_path.stat().st_size
        STREAMING_THRESHOLD = 10 * 1024 * 1024  # 10MB

        if file_size <= STREAMING_THRESHOLD:
            # Small file - use regular conversion
            return self.convert(input_path, output_path, format)

        # Large file - use streaming mode
        logger = self._get_logger()
        logger.info(f"Streaming large file ({file_size // (1024*1024)}MB)")

        try:
            # Read entire file but parse in chunks
            md_content = input_path.read_text(encoding="utf-8")

            # Extract frontmatter first (must be done on full content)
            fm_metadata, md_content = self.frontmatter_parser.parse(md_content)

            # Apply variables
            if fm_metadata.variables:
                md_content = self.frontmatter_parser.apply_variables(
                    md_content, fm_metadata.variables
                )

            # Process in chunks
            lines = md_content.split("\n")
            chunks = []
            current_chunk = []

            for i, line in enumerate(lines):
                current_chunk.append(line)
                if len(current_chunk) >= chunk_size:
                    # Process this chunk
                    chunk_text = "\n".join(current_chunk)
                    chunk_html = self.markdown_parser.parse(chunk_text)
                    chunks.append(chunk_html)
                    current_chunk = []

            # Process remaining lines
            if current_chunk:
                chunk_text = "\n".join(current_chunk)
                chunk_html = self.markdown_parser.parse(chunk_text)
                chunks.append(chunk_html)

            # Combine chunks
            html_content = "\n".join(chunks)

            # For DOCX: process special elements
            if format == "docx":
                html_content = self._process_for_docx(html_content)

            # Render output
            if format == "html":
                full_html = self.html_renderer.render(html_content)
                output_path.write_text(full_html, encoding="utf-8")
            elif format == "pdf":
                renderer = PDFRenderer(self.config)
                renderer.render(html_content, output_path)
            elif format == "docx":
                renderer = DOCXRenderer(self.config)
                renderer.render(html_content, output_path)

            return output_path

        except Exception as e:
            raise ConversionError(f"Failed to convert {input_path}: {e}") from e

    def _get_logger(self):
        """Get logger instance (lazy import to avoid circular deps)."""
        from md_converter.utils.logging import get_logger
        return get_logger(__name__)


# Module-level convenience function
def convert(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    format: str = "pdf",
) -> Path:
    """Convenience function for quick conversions.

    Usage:
        from md_converter import convert
        convert("input.md", "output.pdf")
    """
    converter = Converter()
    return converter.convert(input_path, output_path, format)
