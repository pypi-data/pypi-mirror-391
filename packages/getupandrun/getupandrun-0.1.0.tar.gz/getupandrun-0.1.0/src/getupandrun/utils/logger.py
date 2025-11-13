"""Logging utilities using Rich for colorized output."""

from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

# Define custom theme for consistent styling
CUSTOM_THEME = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red",
        "prompt": "bold blue",
    }
)

# Global console instance
console = Console(theme=CUSTOM_THEME)


def get_logger(name: str = "getupandrun") -> RichHandler:
    """
    Get a Rich logger handler.

    Args:
        name: Logger name

    Returns:
        RichHandler instance
    """
    import logging

    handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
    )
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return handler


def print_info(message: str) -> None:
    """
    Print an info message.

    Args:
        message: Message to print
    """
    console.print(f"[info]ℹ[/info] {message}")


def print_success(message: str) -> None:
    """
    Print a success message.

    Args:
        message: Message to print
    """
    console.print(f"[success]✓[/success] {message}")


def print_warning(message: str) -> None:
    """
    Print a warning message.

    Args:
        message: Message to print
    """
    console.print(f"[warning]⚠[/warning] {message}")


def print_error(message: str) -> None:
    """
    Print an error message.

    Args:
        message: Message to print
    """
    console.print(f"[error]✗[/error] {message}")


def print_prompt(message: str) -> None:
    """
    Print a prompt message.

    Args:
        message: Message to print
    """
    console.print(f"[prompt]→[/prompt] {message}")


def print_header(message: str) -> None:
    """
    Print a header message.

    Args:
        message: Header message to print
    """
    console.print(f"\n[bold cyan]{message}[/bold cyan]\n")


def print_section(message: str) -> None:
    """
    Print a section divider.

    Args:
        message: Section message to print
    """
    console.print(f"\n[bold]{message}[/bold]")


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    """
    Print a table using Rich.

    Args:
        headers: Column headers
        rows: Table rows
    """
    from rich.table import Table

    table = Table(show_header=True, header_style="bold magenta")
    for header in headers:
        table.add_column(header)

    for row in rows:
        table.add_row(*row)

    console.print(table)


def print_progress(message: str) -> None:
    """
    Print a progress message (for future use with progress bars).

    Args:
        message: Progress message to print
    """
    console.print(f"[dim]{message}[/dim]")


def create_progress_bar() -> "Progress":
    """
    Create a Rich Progress instance for progress bars.

    Returns:
        Progress instance
    """
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TextColumn,
        TimeElapsedColumn,
    )

    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )


def get_console() -> Console:
    """
    Get the global console instance.

    Returns:
        Console instance
    """
    return console

