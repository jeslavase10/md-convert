"""CLI module for md-convert."""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from md_converter.parsers.markdown import MarkdownParser
from md_converter.renderers.pdf import PDFRenderer
from md_converter.renderers.docx import DOCXRenderer
from md_converter.utils.config import Config
from md_converter.utils.deps import warn_missing_dependencies
from md_converter.utils.templates import TemplateManager, BUILTIN_TEMPLATES

app = typer.Typer(
    name="md-convert",
    help="Convierte Markdown a PDF/DOCX con soporte para tablas, código y diagramas",
    add_completion=True,
    rich_markup_mode="rich",
)
console = Console()


@app.command()
def convert(
    input: Path = typer.Argument(..., help="Archivo o directorio Markdown de entrada"),
    output: Path = typer.Option(None, "-o", "--output", help="Archivo o directorio de salida"),
    format: str = typer.Option("pdf", "-f", "--format", help="Formato de salida: pdf o docx"),
    recursive: bool = typer.Option(False, "-r", "--recursive", help="Convertir recursively archivos .md en subdirectorios"),
    toc: bool = typer.Option(False, "--toc", help="Incluir tabla de contenidos"),
    toc_depth: int = typer.Option(3, "--toc-depth", help="Nivel máximo de encabezados para TOC"),
    config: Path = typer.Option(None, "--config", help="Archivo de configuración YAML"),
    highlight_style: str = typer.Option("github-dark", "--highlight-style", help="Tema de código"),
    css: Path = typer.Option(None, "--css", help="Archivo CSS personalizado"),
    template: str = typer.Option("default", "--template", help="Template HTML a usar"),
    mermaid_theme: str = typer.Option("default", "--mermaid-theme", help="Tema para diagramas Mermaid"),
    diagram_format: str = typer.Option("svg", "--diagram-format", help="Formato de diagramas: svg o png"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Modo verbose"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Solo validar sin generar salida"),
    keep_html: bool = typer.Option(False, "--keep-html", help="No borrar HTML temporal"),
):
    """Convierte archivos Markdown a PDF o DOCX."""
    # Build config from CLI options (override file config)
    cfg = _build_config(config, highlight_style, css, template, mermaid_theme, diagram_format)

    # Es directorio: convertir todos los .md
    if input.is_dir():
        _convert_directory(
            input, output, format, recursive, cfg, verbose
        )
        return

    # Es archivo individual
    _convert_file(input, output, format, cfg, verbose, dry_run, keep_html)


def _build_config(config_path: Path, highlight_style: str, css: Path, template: str, mermaid_theme: str, diagram_format: str):
    """Build config dict from defaults + CLI overrides."""
    from md_converter.utils.config import Config
    base_cfg = Config.load(config_path)

    # Override with CLI flags
    if highlight_style:
        base_cfg._config.setdefault("code", {})["highlight_style"] = highlight_style
    if template:
        base_cfg._config.setdefault("styles", {})["template"] = template
    if mermaid_theme:
        base_cfg._config.setdefault("diagrams", {}).setdefault("mermaid", {})["theme"] = mermaid_theme
    if diagram_format:
        base_cfg._config.setdefault("diagrams", {}).setdefault("mermaid", {})["format"] = diagram_format
    if css and css.exists():
        base_cfg._config.setdefault("styles", {})["css"] = str(css)

    return base_cfg


def _convert_file(input_path: Path, output_path: Path, format: str, cfg, verbose: bool, dry_run: bool, keep_html: bool):
    """Convert a single Markdown file."""
    if not input_path.exists():
        console.print(f"[red]Error: Archivo no encontrado: {input_path}[/red]")
        raise typer.Exit(2)

    if output_path is None:
        output_path = input_path.with_suffix(f".{format}")

    if verbose:
        console.print(f"[cyan]Input:[/cyan] {input_path}")
        console.print(f"[cyan]Output:[/cyan] {output_path}")
        console.print(f"[cyan]Format:[/cyan] {format}")
        warn_missing_dependencies()

    if dry_run:
        console.print("[green]✓ Dry run - validación exitosa[/green]")
        return

    from md_converter.parsers.frontmatter import FrontmatterParser
    from md_converter.core.converter import Converter

    # Use frontmatter-aware conversion
    fm_parser = FrontmatterParser()
    md_content = input_path.read_text(encoding="utf-8")
    metadata, md_content = fm_parser.parse(md_content)

    if verbose and metadata.title:
        console.print(f"[cyan]Title:[/cyan] {metadata.title}")

    # Apply frontmatter variables
    if metadata.variables:
        md_content = fm_parser.apply_variables(md_content, metadata.variables)

    parser = MarkdownParser(cfg)
    html_content = parser.parse(md_content)

    if format == "pdf":
        renderer = PDFRenderer(cfg)
        renderer.render(html_content, output_path)
    elif format == "docx":
        renderer = DOCXRenderer(cfg)
        renderer.render(html_content, output_path)
    else:
        console.print(f"[red]Error: Formato no soportado: {format}[/red]")
        raise typer.Exit(2)

    console.print(f"[green]✓ Generado: {output_path}[/green]")


def _convert_directory(input_dir: Path, output_dir: Path, format: str, recursive: bool, cfg, verbose: bool):
    """Convert all Markdown files in a directory."""
    pattern = "**/*.md" if recursive else "*.md"
    md_files = list(input_dir.glob(pattern))

    if not md_files:
        console.print(f"[yellow]No se encontraron archivos .md en {input_dir}[/yellow]")
        return

    if output_dir is None:
        output_dir = input_dir
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    if verbose:
        console.print(f"[cyan]Directorio:[/cyan] {input_dir}")
        console.print(f"[cyan]Archivos a convertir:[/cyan] {len(md_files)}")
        console.print(f"[cyan]Directorio salida:[/cyan] {output_dir}")

    success = 0
    errors = 0
    for md_file in md_files:
        try:
            relative_path = md_file.relative_to(input_dir)
            output_path = output_dir / relative_path.with_suffix(f".{format}")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            _convert_file(md_file, output_path, format, cfg, False, False, False)
            success += 1
        except Exception as e:
            console.print(f"[red]✗ Error en {md_file}: {e}[/red]")
            errors += 1

    console.print(f"\n[green]✓ Convertidos: {success}[/green] [red]✗ Errores: {errors}[/red]")


@app.command()
def init(
    path: Path = typer.Option(Path.cwd(), "--path", help="Directorio donde crear configuración"),
):
    """Crea archivo de configuración por defecto."""
    config_path = path / ".mdconvert.yaml"
    if config_path.exists():
        console.print(f"[yellow]Advertencia: {config_path} ya existe[/yellow]")
        raise typer.Exit(1)

    default_config = """\
input:
  encoding: utf-8
  frontmatter: true

output:
  format: pdf
  filename_pattern: "{name}.{ext}"

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
  enabled: false
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
"""
    config_path.write_text(default_config, encoding="utf-8")
    console.print(f"[green]✓ Configuración creada: {config_path}[/green]")


@app.command()
def version():
    """Muestra la versión de md-convert."""
    from md_converter import __version__
    console.print(f"[cyan]md-convert {__version__}[/cyan]")


templates_app = typer.Typer(help="Manage HTML templates")


@templates_app.command("list")
def templates_list():
    """List all available templates."""
    manager = TemplateManager()

    table = Table(title="Available Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Type", style="magenta")

    for tmpl in manager.list_templates():
        table.add_row(
            tmpl.name,
            tmpl.description,
            "builtin" if tmpl.is_builtin else "custom",
        )

    console.print(table)


@templates_app.command("create")
def templates_create(
    name: str = typer.Argument(..., help="Name for the new template"),
    path: Path = typer.Option(Path.cwd(), "--path", help="Directory to create template in"),
):
    """Create a new custom template."""
    manager = TemplateManager()

    if manager.template_exists(name):
        console.print(f"[yellow]Template '{name}' already exists[/yellow]")
        raise typer.Exit(1)

    try:
        template_dir = manager.create_template(name, path)
        console.print(f"[green]✓ Template created at: {template_dir}[/green]")
    except Exception as e:
        console.print(f"[red]Error creating template: {e}[/red]")
        raise typer.Exit(1)


app.add_typer(templates_app, name="templates")


if __name__ == "__main__":
    app()
