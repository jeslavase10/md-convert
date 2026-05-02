"""Dependency checker for external tools required by md-convert."""

import shutil
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from rich.console import Console

console = Console()


@dataclass
class Dependency:
    """Represents an external dependency."""

    name: str
    command: str
    package_hint: str  # How to install this dependency
    required: bool = True


AVAILABLE_DEPENDENCIES: List[Dependency] = [
    Dependency(
        name="mermaid-cli",
        command="mmdc",
        package_hint="npm install -g @mermaid-js/mermaid-cli",
        required=False,
    ),
]


class DependencyChecker:
    """Check for required external dependencies."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def check_all(self) -> List[str]:
        """Check all dependencies and return list of missing ones."""
        missing = []
        for dep in AVAILABLE_DEPENDENCIES:
            if not self._check_command(dep.command):
                if self.verbose:
                    console.print(f"[yellow]Warning: {dep.name} not found[/yellow]")
                missing.append(dep.name)
        return missing

    def _check_command(self, command: str) -> bool:
        """Check if a command is available."""
        try:
            result = shutil.which(command)
            return result is not None
        except Exception:
            return False

    def check_and_warn(self) -> None:
        """Check dependencies and print warnings for missing optional ones."""
        for dep in AVAILABLE_DEPENDENCIES:
            if not self._check_command(dep.command):
                console.print(
                    f"[yellow]⚠️  {dep.name} not installed. "
                    f"Install with: {dep.package_hint}[/yellow]"
                )

    def require(self, command: str) -> None:
        """Raise error if command is not available."""
        if not self._check_command(command):
            raise RuntimeError(
                f"Required command '{command}' not found. "
                f"Please ensure it is installed and in PATH."
            )

    def get_version(self, command: str) -> Optional[str]:
        """Get version of a command if available."""
        try:
            result = subprocess.run(
                [command, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip().split("\n")[0]
        except Exception:
            pass
        return None


# Global checker instance
_checker = DependencyChecker()


def check_dependencies() -> List[str]:
    """Quick check for missing dependencies."""
    return _checker.check_all()


def warn_missing_dependencies() -> None:
    """Print warnings for missing optional dependencies."""
    _checker.check_and_warn()
