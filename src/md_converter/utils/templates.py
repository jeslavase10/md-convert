"""Template management for md-convert."""

from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

BUILTIN_TEMPLATES = {
    "default": "Clean, minimal template for general use",
    "report": "Corporate report with cover page and executive summary",
    "academic": "Academic format with citations and bibliography",
}


@dataclass
class TemplateInfo:
    """Information about a template."""

    name: str
    description: str
    path: Path
    is_builtin: bool = True


class TemplateManager:
    """Manage HTML templates for md-convert."""

    def __init__(self, custom_path: Optional[Path] = None):
        """Initialize template manager.

        Args:
            custom_path: Optional path to user-defined templates
        """
        self.custom_path = custom_path
        self._builtin_template_dir = Path(__file__).parent

    def list_templates(self) -> List[TemplateInfo]:
        """List all available templates."""
        templates = []

        # Built-in templates
        for name, description in BUILTIN_TEMPLATES.items():
            template_path = self._builtin_template_dir / f"{name}.html"
            templates.append(TemplateInfo(
                name=name,
                description=description,
                path=template_path,
                is_builtin=True,
            ))

        # Custom templates
        if self.custom_path and self.custom_path.exists():
            for template_dir in self.custom_path.iterdir():
                if template_dir.is_dir() and (template_dir / "template.html").exists():
                    config_file = template_dir / "config.yaml"
                    description = name  # Default to name
                    if config_file.exists():
                        import yaml
                        with open(config_file) as f:
                            config = yaml.safe_load(f)
                            description = config.get("description", name)
                    templates.append(TemplateInfo(
                        name=name,
                        description=description,
                        path=template_dir / "template.html",
                        is_builtin=False,
                    ))

        return templates

    def get_template_path(self, name: str) -> Optional[Path]:
        """Get path to a specific template."""
        if name in BUILTIN_TEMPLATES:
            return self._builtin_template_dir / f"{name}.html"

        if self.custom_path and self.custom_path.exists():
            custom_template = self.custom_path / name / "template.html"
            if custom_template.exists():
                return custom_template

        return None

    def create_template(self, name: str, output_dir: Path) -> Path:
        """Create a new custom template from the default template.

        Args:
            name: Name for the new template
            output_dir: Directory to create template in

        Returns:
            Path to created template directory
        """
        template_dir = output_dir / name
        template_dir.mkdir(parents=True, exist_ok=True)

        # Copy default template
        default_template = self._builtin_template_dir / "default.html"
        target_template = template_dir / "template.html"

        if default_template.exists():
            target_template.write_text(default_template.read_text())

        # Create config.yaml
        config_content = f"""\
name: {name}
description: Custom template - {name}
page_size: A4
margins:
  top: 25mm
  right: 20mm
  bottom: 25mm
  left: 20mm
fonts:
  body: Calibri
  heading: Calibri Light
  code: Consolas
colors:
  primary: "#333333"
  secondary: "#666666"
  accent: "#0066cc"
"""
        (template_dir / "config.yaml").write_text(config_content)

        return template_dir

    def template_exists(self, name: str) -> bool:
        """Check if a template exists."""
        return self.get_template_path(name) is not None
