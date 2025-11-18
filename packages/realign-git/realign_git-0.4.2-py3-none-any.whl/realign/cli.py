#!/usr/bin/env python3
"""ReAlign CLI - Main command-line interface."""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.syntax import Syntax

from .commands import init, search, show, config

app = typer.Typer(
    name="realign",
    help="Track and version AI agent chat sessions with git commits",
    add_completion=False,
)
console = Console()

# Register commands
app.command(name="init")(init.init_command)
app.command(name="search")(search.search_command)
app.command(name="show")(show.show_command)
app.command(name="config")(config.config_command)


@app.command()
def version():
    """Show ReAlign version."""
    from . import __version__
    console.print(f"ReAlign version {__version__}")


if __name__ == "__main__":
    app()
