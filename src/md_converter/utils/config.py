"""Configuration loader for md-convert."""

import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager for md-convert."""

    DEFAULT_CONFIG = {
        "input": {
            "encoding": "utf-8",
            "frontmatter": True,
        },
        "output": {
            "format": "pdf",
            "filename_pattern": "{name}.{ext}",
        },
        "pdf": {
            "page_size": "A4",
            "margins": {
                "top": "25mm",
                "right": "20mm",
                "bottom": "25mm",
                "left": "20mm",
            },
            "dpi": 300,
        },
        "docx": {
            "page_size": "A4",
            "default_font": "Calibri",
            "font_size": 11,
        },
        "toc": {
            "enabled": False,
            "depth": 3,
            "title": "Tabla de Contenidos",
        },
        "code": {
            "highlight_style": "github-dark",
            "line_numbers": False,
            "background": True,
        },
        "diagrams": {
            "mermaid": {
                "enabled": True,
                "theme": "default",
                "format": "svg",
                "scale": 1,
            }
        },
        "math": {
            "enabled": True,
            "renderer": "matplotlib",
        },
        "styles": {
            "css": None,
            "template": "default",
        },
    }

    def __init__(self, config_dict: Dict[str, Any]):
        self._config = config_dict

    @classmethod
    def load(cls, config_path: Path = None) -> "Config":
        """Load configuration from file or use defaults."""
        if config_path is None:
            return cls(cls.DEFAULT_CONFIG.copy())

        if not config_path.exists():
            return cls(cls.DEFAULT_CONFIG.copy())

        with open(config_path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}

        merged = cls._deep_merge(cls.DEFAULT_CONFIG.copy(), user_config)
        return cls(merged)

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """Deep merge override into base."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Config._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key: str, default=None):
        """Get config value by dot-notation key."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
