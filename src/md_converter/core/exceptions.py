"""Custom exceptions and exit codes for md-convert."""

from enum import IntEnum


class ExitCode(IntEnum):
    """Standard exit codes for md-convert CLI."""

    SUCCESS = 0
    GENERIC_ERROR = 1
    VALIDATION_ERROR = 2
    MISSING_DEPENDENCY = 3
    RENDER_ERROR = 4
    FILE_NOT_FOUND = 5


class MDConvertError(Exception):
    """Base exception for all md-convert errors."""

    exit_code = ExitCode.GENERIC_ERROR

    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class ValidationError(MDConvertError):
    """Raised when input validation fails."""

    exit_code = ExitCode.VALIDATION_ERROR


class FileNotFoundError(MDConvertError):
    """Raised when an input file doesn't exist."""

    exit_code = ExitCode.FILE_NOT_FOUND


class DependencyError(MDConvertError):
    """Raised when a required external dependency is missing."""

    exit_code = ExitCode.MISSING_DEPENDENCY


class RenderError(MDConvertError):
    """Raised when rendering/conversion fails."""

    exit_code = ExitCode.RENDER_ERROR


class ConfigError(MDConvertError):
    """Raised when configuration is invalid."""

    exit_code = ExitCode.VALIDATION_ERROR


def format_error(error: Exception, verbose: bool = False) -> str:
    """Format an exception for display to user.

    Args:
        error: The exception to format
        verbose: If True, include traceback

    Returns:
        Formatted error message string
    """
    if isinstance(error, MDConvertError):
        msg = error.message
        if error.details and verbose:
            msg += f"\n  Details: {error.details}"
        return msg
    elif verbose:
        return str(error)
    else:
        return f"Error: {error}"


def handle_exception(error: Exception, verbose: bool = False) -> int:
    """Handle an exception and return the appropriate exit code.

    Args:
        error: The exception to handle
        verbose: If True, print traceback

    Returns:
        Exit code integer
    """
    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    if isinstance(error, MDConvertError):
        exit_code = error.exit_code
    else:
        exit_code = ExitCode.GENERIC_ERROR

    error_msg = format_error(error, verbose)

    console.print(Panel(
        f"[red]{error_msg}[/red]",
        title="[bold red]Error[/bold red]",
        border_style="red",
    ))

    if verbose and not isinstance(error, MDConvertError):
        import traceback
        console.print(f"\n[dim]{traceback.format_exc()}[/dim]")

    return exit_code
