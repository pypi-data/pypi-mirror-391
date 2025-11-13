"""ReAlign show command - Display agent sessions from commits or files."""

import subprocess
import json
import re
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def show_command(
    commit: Optional[str] = typer.Argument(None, help="Commit hash to show session from"),
    session: Optional[str] = typer.Option(None, "--session", "-s", help="Direct path to session file"),
    format_output: str = typer.Option("pretty", "--format", "-f", help="Output format: pretty, json, raw"),
    pager: bool = typer.Option(False, "--pager", "-p", help="Use pager (less) for output"),
):
    """Display agent sessions from commits or files."""
    if not commit and not session:
        console.print("[red]Error: Must specify either a commit hash or --session path[/red]")
        raise typer.Exit(1)

    # Check if we're in a git repository
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        console.print("[red]Error: Not in a git repository.[/red]")
        raise typer.Exit(1)

    repo_root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )

    session_path = None
    session_content = None

    # Get session from commit
    if commit:
        console.print(f"[blue]Fetching session for commit:[/blue] {commit}")

        try:
            # Get commit message to extract session path
            result = subprocess.run(
                ["git", "show", "--format=%b", "-s", commit],
                capture_output=True,
                text=True,
                check=True,
                cwd=repo_root,
            )

            body = result.stdout
            session_match = re.search(r"Agent-Session-Path:\s*(.+?)(?:\n|$)", body)

            if not session_match:
                console.print("[yellow]No agent session found in this commit.[/yellow]")
                raise typer.Exit(0)

            session_path = session_match.group(1).strip()
            console.print(f"[green]Found session:[/green] {session_path}")

            # Try to read from working tree first
            full_session_path = repo_root / session_path
            if full_session_path.exists():
                with open(full_session_path, "r", encoding="utf-8") as f:
                    session_content = f.read()
            else:
                # Try to get from git
                result = subprocess.run(
                    ["git", "show", f"{commit}:{session_path}"],
                    capture_output=True,
                    text=True,
                    check=False,
                    cwd=repo_root,
                )
                if result.returncode == 0:
                    session_content = result.stdout
                else:
                    console.print(f"[red]Could not find session file:[/red] {session_path}")
                    raise typer.Exit(1)

        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error fetching commit:[/red] {e}")
            raise typer.Exit(1)

    # Get session from direct path
    elif session:
        session_path = session
        full_path = Path(session) if Path(session).is_absolute() else repo_root / session

        if not full_path.exists():
            console.print(f"[red]Session file not found:[/red] {session}")
            raise typer.Exit(1)

        console.print(f"[blue]Reading session:[/blue] {session}")
        with open(full_path, "r", encoding="utf-8") as f:
            session_content = f.read()

    # Display session content
    if session_content:
        display_session(session_content, format_output, pager, session_path)


def display_session(content: str, format_type: str, use_pager: bool, session_path: Optional[str]):
    """Display session content in specified format."""
    if format_type == "raw":
        if use_pager:
            try:
                subprocess.run(["less", "-R"], input=content, text=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                console.print(content)
        else:
            console.print(content)
    elif format_type == "json":
        try:
            # Try to parse and pretty-print as JSON/JSONL
            lines = content.strip().split("\n")
            formatted_lines = []
            for line in lines:
                try:
                    obj = json.loads(line)
                    formatted_lines.append(json.dumps(obj, indent=2, ensure_ascii=False))
                except json.JSONDecodeError:
                    formatted_lines.append(line)
            output = "\n".join(formatted_lines)
            if use_pager:
                try:
                    subprocess.run(["less", "-R"], input=output, text=True, check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    console.print(output)
            else:
                console.print(output)
        except Exception:
            console.print(content)
    else:  # pretty format
        # For pretty format, render directly (can't use pager with rich objects)
        format_session_pretty_direct(content, session_path)


def format_session_pretty_direct(content: str, session_path: Optional[str]):
    """Format and display session content in a pretty, readable way."""
    lines = content.strip().split("\n")

    if session_path:
        console.print(f"\n[bold cyan]Session: {session_path}[/bold cyan]\n")

    for i, line in enumerate(lines, 1):
        try:
            # Try to parse as JSON (for JSONL format)
            obj = json.loads(line)

            role = obj.get("role", "unknown")
            content_text = obj.get("content", "")
            timestamp = obj.get("timestamp", "")

            # Format based on role
            if role == "user":
                console.print(
                    Panel(
                        content_text,
                        title=f"[bold blue]User[/bold blue] {timestamp}",
                        border_style="blue",
                        padding=(1, 2),
                    )
                )
            elif role == "assistant":
                console.print(
                    Panel(
                        content_text,
                        title=f"[bold green]Assistant[/bold green] {timestamp}",
                        border_style="green",
                        padding=(1, 2),
                    )
                )
            else:
                console.print(
                    Panel(
                        content_text,
                        title=f"[bold yellow]{role.title()}[/bold yellow] {timestamp}",
                        border_style="yellow",
                        padding=(1, 2),
                    )
                )

        except json.JSONDecodeError:
            # Not JSON, display as plain text
            console.print(f"[dim]{i:4d}:[/dim] {line}")


def format_session_pretty(content: str, session_path: Optional[str]) -> str:
    """Format session content in a pretty, readable way (deprecated - use format_session_pretty_direct)."""
    # This is kept for compatibility but not used
    return content


if __name__ == "__main__":
    typer.run(show_command)
