"""Reusable output formatters for CLI commands."""

import json
from typing import Any, Callable, Protocol, TypeVar

from rich.console import Console
from rich.table import Table

T = TypeVar("T")
console = Console()


def output_json(data: dict[str, Any], success: bool = True) -> None:
    """Output data as JSON to stdout.

    Args:
        data: The data to output as JSON
        success: Whether this is a success response (affects structure)
    """
    output: dict[str, Any]
    if success:
        output = {"success": True, "data": data}
    else:
        output = {"success": False, **data}

    print(json.dumps(output, indent=2))


class Formatter(Protocol[T]):
    """Protocol for output formatters."""

    def format_one(self, item: T) -> None:
        """Format a single item."""
        ...

    def format_list(self, items: list[T], title: str = "") -> None:
        """Format a list of items."""
        ...


class JSONFormatter:
    """JSON output formatter with consistent structure."""

    @staticmethod
    def format_one(item: Any, success: bool = True) -> None:
        """Print single item as JSON.

        Args:
            item: Item to format (Pydantic model or dict)
            success: Whether operation was successful
        """
        data = item.model_dump(mode="json") if hasattr(item, "model_dump") else item
        print(json.dumps({"success": success, "data": data}, indent=2))

    @staticmethod
    def format_list(items: list[Any], title: str = "") -> None:
        """Print list as JSON.

        Args:
            items: List of items to format
            title: Optional title (added to metadata)
        """
        data = [
            item.model_dump(mode="json") if hasattr(item, "model_dump") else item
            for item in items
        ]
        output = {"success": True, "items": data, "count": len(data)}
        if title:
            output["title"] = title
        print(json.dumps(output, indent=2))


class TableFormatter:
    """Table output formatter with Rich.

    Example:
        formatter = TableFormatter()
        formatter.format_list(
            items=labels,
            columns=[("Name", "cyan"), ("Color", "white")],
            title="Labels",
            row_formatter=lambda l: [l.name, l.color or ""],
        )
    """

    def __init__(self, console: Console | None = None):
        self.console = console or Console()

    def format_list(
        self,
        items: list[Any],
        columns: list[tuple[str, str]],  # (name, style) pairs
        title: str = "",
        row_formatter: Callable[[Any], list[str]] | None = None,
        empty_message: str | None = None,
    ) -> None:
        """Format items as a table.

        Args:
            items: Items to display
            columns: List of (column_name, style) tuples
            title: Table title
            row_formatter: Function to convert item to row values
            empty_message: Custom message for empty results
        """
        if not items:
            msg = empty_message or f"No {title.lower() if title else 'items'} found"
            self.console.print(f"[yellow]{msg}[/yellow]")
            return

        table = Table(title=title, show_header=True, header_style="bold")
        for col_name, col_style in columns:
            table.add_column(col_name, style=col_style)

        for item in items:
            row_values = (
                row_formatter(item) if row_formatter else self._default_row(item)
            )
            table.add_row(*row_values)

        self.console.print(table)
        count_text = "1 item" if len(items) == 1 else f"{len(items)} items"
        self.console.print(f"\n{count_text}")

    def _default_row(self, item: Any) -> list[str]:
        """Default row formatter - converts object to strings."""
        if hasattr(item, "model_dump"):
            data = item.model_dump()
            return [str(v) for v in data.values()]
        return [str(item)]
