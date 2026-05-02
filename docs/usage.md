# Usage

## Basic Usage

```bash
# Convert to PDF (default)
md-convert input.md

# Convert to DOCX
md-convert input.md -f docx

# Specify output file
md-convert input.md -o output.pdf
```

## Directory Batch Conversion

```bash
# Convert all .md files in a directory
md-convert docs/

# Recursive (include subdirectories)
md-convert docs/ -r

# Output to different directory
md-convert docs/ -o output_folder/
```

## Table of Contents

```bash
# Generate with TOC
md-convert input.md --toc

# TOC with custom depth
md-convert input.md --toc --toc-depth 3
```

## Code Highlighting

```bash
# Use a specific theme
md-convert input.md --highlight-style monokai

# Available themes: github-dark, github, monokai, dracula
```

## CSS Customization

```bash
# Use custom CSS file
md-convert input.md --css custom.css
```

## Mermaid Diagrams

```bash
# Use dark theme for diagrams
md-convert input.md --mermaid-theme dark

# Use PNG instead of SVG
md-convert input.md --diagram-format png
```

## Configuration File

```bash
# Use a custom config file
md-convert input.md --config .mdconvert.yaml

# Create default config file
md-convert init
```

## Debug Options

```bash
# Verbose output
md-convert input.md --verbose

# Dry run (validation only)
md-convert input.md --dry-run

# Keep intermediate HTML
md-convert input.md --keep-html
```

## Multiple Files

```bash
# Convert multiple specific files
md-convert file1.md file2.md file3.md

# Use glob pattern
md-convert *.md -f pdf
```

## Examples

### Full Featured

```bash
md-convert documento.md \
  --format pdf \
  --toc \
  --highlight-style dracula \
  --mermaid-theme dark \
  --output reporte.pdf
```

### Batch with DOCX

```bash
md-convert docs/ -r -f docx -o docx_output/
```

## Exit Codes

- `0`: Success
- `1`: Error (file not found, invalid format, etc.)
