"""md-convert: Markdown to PDF/DOCX converter."""

from md_converter.core import Converter, convert, ConversionError

__version__ = "1.0.0"
__all__ = ["Converter", "convert", "ConversionError", "__version__"]
