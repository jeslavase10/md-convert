# md-convert

Convert Markdown to PDF/DOCX with support for tables, code blocks, and diagrams.

## Features

- **Markdown parsing** with syntax highlighting
- **Tables** with alignment support
- **Code blocks** with 20+ language themes
- **Mermaid diagrams** (flowcharts, sequence, class diagrams)
- **Math/LaTeX** equations
- **Table of contents** generation

## Installation

```bash
pip install md-convert
```

Or install from source:

```bash
cd md-convert
pip install -e .
```

### Dependencies

- **Mermaid CLI** (optional, for diagrams):
  ```bash
  npm install -g @mermaid-js/mermaid-cli
  ```

- **WeasyPrint** (optional, for PDF on Windows):
  WeasyPrint works best on Linux/macOS. On Windows, consider using Docker.

## Usage

```bash
# Convert to PDF (default)
md-convert input.md

# Convert to DOCX
md-convert input.md -f docx

# Specify output file
md-convert input.md -o output.pdf

# With table of contents
md-convert input.md --toc

# Custom code theme
md-convert input.md --highlight-style monokai

# Using config file
md-convert input.md --config .mdconvert.yaml

# Initialize default config
md-convert --init
```

## Configuration

Create a `.mdconvert.yaml` file:

```yaml
input:
  encoding: utf-8
  frontmatter: true

output:
  format: pdf

pdf:
  page_size: A4
  margins:
    top: 25mm
    right: 20mm
    bottom: 25mm
    left: 20mm

code:
  highlight_style: github-dark
  line_numbers: false

diagrams:
  mermaid:
    enabled: true
    theme: default
    format: svg

math:
  enabled: true
```

## Supported Markdown

### Basic
- Headings (h1-h6)
- Paragraphs and line breaks
- Bold, italic, strikethrough
- Ordered and unordered lists
- Links and images

### Extended
- Tables with alignment
- Code blocks with syntax highlighting
- Blockquotes
- Horizontal rules
- Task lists/checkboxes

### Advanced
- Mermaid diagrams
- Math/LaTeX equations
- Footnotes

## License

MIT
