# Changelog

All notable changes to this project will be documented in this file.

## [1.0.2] - 2026-05-01

### Added
- **Kroki Offline Mode**: `KrokiRenderer` with connectivity check, falls back to raw diagram code when offline
- **File Logging with Rotation**: `RotatingFileHandler` with `max_bytes` and `backup_count`, configured via `log_file` in config
- **Hook System**: `HookManager` with phases (PRE_CONVERT, POST_CONVERT, PRE_RENDER, POST_RENDER, ON_ERROR) for extensibility
- **Plugin System**: `PluginRegistry` with entry point discovery for custom parsers/renderers
- **Streaming Mode**: `Converter.convert_streaming()` for chunk-based processing of large files (>10MB)
- **Watch Mode**: `md-convert watch start` command using watchdog for auto-reconvert on file changes

## [1.0.1] - 2026-05-01

### Added
- **FrontmatterParser**: YAML frontmatter extraction with `DocumentMetadata` dataclass
- **Converter API**: Programmatic usage via `from md_converter import Converter, convert`
- **Dependency Checker**: `utils/deps.py` for validating external tools (mmdc, etc.)
- **Shell Completion**: Typer built-in completion support (`add_completion=True`)
- **DOCX Table Alignment**: Left/center/right alignment support in tables
- **DOCX Image Support**: Base64 embedded images and local files
- **Math → Image for DOCX**: LaTeX math rendered as PNG via matplotlib in DOCX output
- **Structured Logging**: Rich-based logging with `MDConvertLogger` and configurable levels
- **Exception Hierarchy**: Typed exceptions (`ValidationError`, `RenderError`, etc.) with exit codes
- **Templates CLI**: `templates list` and `templates create` commands

### Changed
- `pyproject.toml`: Added `jinja2>=3.1.0` and `watchdog>=3.0.0` to dependencies
- Exit codes standardized: 0=success, 1=generic, 2=validation, 3=dependency, 4=render, 5=not found
- CLI now parses frontmatter and applies variables automatically

### Fixed
- DOCX table cell alignment not being applied
- Image rendering in DOCX (was a no-op `pass`)

## [1.0.0] - 2024-05-01

### Added
- CLI tool with Typer for converting Markdown to PDF/DOCX
- Markdown parser with pymdown-extensions (tables, code blocks, task lists)
- PDF renderer using WeasyPrint
- DOCX renderer using python-docx
- HTML intermediate renderer with styling
- Mermaid diagram support via mermaid-cli
- Math/LaTeX rendering support via matplotlib
- Config file support (YAML .mdconvert.yaml)
- Directory batch conversion with `-r` recursive flag
- Custom CSS support via `--css` flag
- Custom highlight style via `--highlight-style` flag
- Mermaid theme customization via `--mermaid-theme` flag
- Diagram format selection via `--diagram-format` flag
- `--init` command to create default config file
- `--verbose`, `--dry-run` debugging options
- README.md with documentation

### Features
- Headings (h1-h6) with styling
- Tables with alignment support
- Code blocks with 20+ language syntax highlighting
- Blockquotes, lists (ordered/unordered/nested)
- Task lists/checkboxes
- Mermaid diagrams (flowcharts, sequence, class)
- Math equations (inline and block)
