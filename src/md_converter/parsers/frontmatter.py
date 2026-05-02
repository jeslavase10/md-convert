"""Frontmatter parser for Markdown documents."""

import re
import yaml
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class DocumentMetadata:
    """Metadata extracted from document frontmatter."""

    title: str = ""
    subtitle: str = ""
    authors: list = field(default_factory=list)
    date: Optional[datetime] = None
    version: str = "1.0.0"
    status: str = "Draft"
    classification: str = "Internal"
    company: Dict[str, str] = field(default_factory=dict)
    document_id: str = ""
    output_config: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, str] = field(default_factory=dict)
    lang: str = "es"
    raw: Dict[str, Any] = field(default_factory=dict)


class FrontmatterParser:
    """Parse YAML frontmatter from Markdown documents."""

    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    def parse(self, content: str) -> Tuple[DocumentMetadata, str]:
        """Extract frontmatter and return (metadata, content_without_frontmatter)."""
        match = self.FRONTMATTER_PATTERN.match(content)

        if not match:
            return DocumentMetadata(), content

        yaml_content = match.group(1)
        remaining_content = content[match.end() :]

        try:
            raw_data = yaml.safe_load(yaml_content) or {}
        except yaml.YAMLError:
            return DocumentMetadata(), content

        metadata = self._process_metadata(raw_data)

        return metadata, remaining_content

    def _process_metadata(self, raw: Dict) -> DocumentMetadata:
        """Process and validate metadata from raw YAML dict."""
        # Process date
        date = None
        if "date" in raw:
            raw_date = raw["date"]
            if isinstance(raw_date, str):
                try:
                    date = datetime.fromisoformat(raw_date)
                except ValueError:
                    try:
                        date = datetime.strptime(raw_date, "%Y-%m-%d")
                    except ValueError:
                        date = None
            elif isinstance(raw_date, datetime):
                date = raw_date

        # Process authors
        authors = raw.get("author", [])
        if isinstance(authors, str):
            authors = [{"name": authors}]
        elif isinstance(authors, dict):
            authors = [authors]
        elif isinstance(authors, list):
            processed = []
            for a in authors:
                if isinstance(a, str):
                    processed.append({"name": a})
                else:
                    processed.append(a)
            authors = processed

        return DocumentMetadata(
            title=raw.get("title", ""),
            subtitle=raw.get("subtitle", ""),
            authors=authors,
            date=date,
            version=raw.get("version", "1.0.0"),
            status=raw.get("status", "Draft"),
            classification=raw.get("classification", "Internal"),
            company=raw.get("company", {}),
            document_id=raw.get("document_id", ""),
            output_config=raw.get("output", {}),
            variables=raw.get("variables", {}),
            lang=raw.get("lang", "es"),
            raw=raw,
        )

    def apply_variables(self, content: str, variables: Dict[str, str]) -> str:
        """Replace {{variable}} placeholders in content."""
        for key, value in variables.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        return content
