#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "typer>=0.9.0",
#   "rich>=13.0.0",
# ]
# ///
"""Test script with PEP 723 dependencies and standard Python shebang."""

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def greet(name: str) -> None:
    """Greet a user by name."""
    console.print(f"[bold green]Hello {name}![/bold green]")


if __name__ == "__main__":
    app()
