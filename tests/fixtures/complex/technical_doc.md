# Technical Documentation Template

## Overview

Brief description of the system.

## Requirements

- Python 3.10+
- Dependencies listed in pyproject.toml

## Installation

```bash
pip install md-convert
```

## Usage

```bash
md-convert input.md -o output.pdf
```

## API Reference

### convert(input, output, format)

| Parameter | Type | Description |
|----------|------|-------------|
| input | Path | Input markdown file |
| output | Path | Output file path |
| format | str | Output format (pdf/docx) |

## Configuration

See [configuration.md](../docs/configuration.md) for details.

## License

MIT
