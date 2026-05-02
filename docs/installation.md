# Installation

## Prerequisites

- Python 3.10 or higher
- Node.js (optional, for Mermaid diagrams)
- npm (optional, for Mermaid CLI)

## Install via pip

```bash
pip install md-convert
```

## Install from source

```bash
git clone https://github.com/tuuser/md-convert.git
cd md-convert
pip install -e .
```

## Install editable with dev dependencies

```bash
pip install -e ".[dev]"
```

## Mermaid CLI Installation (Optional)

For diagram support, install the Mermaid CLI:

```bash
npm install -g @mermaid-js/mermaid-cli
```

## Verify Installation

```bash
md-convert --version
md-convert --help
```

## Docker Installation

```bash
docker pull tuuser/md-convert
docker run -v $(pwd):/docs tuuser/md-convert input.md -o output.pdf
```

## Troubleshooting

### WeasyPrint issues on Windows

WeasyPrint works best on Linux/macOS. On Windows:

1. Use Docker: `docker run ... md-convert input.md ...`
2. Or install GTK3 from [gtk.org](https://gtk.org)

### Mermaid CLI not found

If you see the warning "mermaid-cli not found", install it:

```bash
npm install -g @mermaid-js/mermaid-cli
```
