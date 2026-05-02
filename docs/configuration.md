# Configuration

## Configuration File

Create a `.mdconvert.yaml` file in your project root or specify with `--config`:

```bash
md-convert input.md --config custom-config.yaml
```

## Initialize Default Config

```bash
md-convert init
```

This creates a `.mdconvert.yaml` with all default options.

## Configuration Options

### Input

```yaml
input:
  encoding: utf-8
  frontmatter: true
```

- `encoding`: File encoding (default: utf-8)
- `frontmatter`: Parse YAML frontmatter (default: true)

### Output

```yaml
output:
  format: pdf
  filename_pattern: "{name}.{ext}"
```

- `format`: Output format - `pdf` or `docx`
- `filename_pattern`: Pattern for batch output names

### PDF Settings

```yaml
pdf:
  page_size: A4
  margins:
    top: 25mm
    right: 20mm
    bottom: 25mm
    left: 20mm
  dpi: 300
```

- `page_size`: Page size (A4, Letter, Legal, etc.)
- `margins`: Page margins in mm
- `dpi`: Image DPI for PDF

### DOCX Settings

```yaml
docx:
  page_size: A4
  default_font: Calibri
  font_size: 11pt
```

- `page_size`: Page size
- `default_font`: Default font family
- `font_size`: Default font size in points

### Table of Contents

```yaml
toc:
  enabled: true
  depth: 3
  title: "Tabla de Contenidos"
```

- `enabled`: Enable TOC generation
- `depth`: Maximum heading level for TOC
- `title`: TOC title text

### Code Highlighting

```yaml
code:
  highlight_style: github-dark
  line_numbers: false
  background: true
```

- `highlight_style`: Pygments style (github-dark, monokai, dracula, etc.)
- `line_numbers`: Show line numbers
- `background`: Enable code block background

### Mermaid Diagrams

```yaml
diagrams:
  mermaid:
    enabled: true
    theme: default
    format: svg
    scale: 1
```

- `enabled`: Enable Mermaid processing
- `theme`: Mermaid theme (default, dark, forest, etc.)
- `format`: Image format (svg, png)
- `scale`: Diagram scale factor

### Math Rendering

```yaml
math:
  enabled: true
  renderer: matplotlib
```

- `enabled`: Enable math rendering
- `renderer`: Math renderer backend

### Styles

```yaml
styles:
  css: null
  template: default
```

- `css`: Custom CSS file path (null = default)
- `template`: HTML template to use

## Full Example Configuration

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
  dpi: 300

docx:
  page_size: A4
  default_font: Calibri
  font_size: 11pt

toc:
  enabled: true
  depth: 3
  title: "Tabla de Contenidos"

code:
  highlight_style: github-dark
  line_numbers: false
  background: true

diagrams:
  mermaid:
    enabled: true
    theme: default
    format: svg
    scale: 1

math:
  enabled: true
  renderer: matplotlib

styles:
  css: null
  template: default
```
