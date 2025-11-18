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


def calculate_line_range(
    from_line: Optional[int],
    to_line: Optional[int],
    around_line: Optional[int],
    context: int,
    first: Optional[int],
    last: Optional[int],
    total_lines: int,
) -> Optional[tuple[int, int]]:
    """
    Calculate the line range to display based on various parameters.

    Returns (start_line, end_line) tuple (1-indexed, inclusive) or None for all lines.
    """
    # Priority: around > from/to > first/last

    if around_line is not None:
        # Show lines around a specific line
        start = max(1, around_line - context)
        end = min(total_lines, around_line + context)
        return (start, end)

    if from_line is not None or to_line is not None:
        # Show range from start to end
        start = from_line if from_line is not None else 1
        end = to_line if to_line is not None else total_lines
        return (start, end)

    if first is not None:
        # Show first N lines
        return (1, min(first, total_lines))

    if last is not None:
        # Show last N lines
        return (max(1, total_lines - last + 1), total_lines)

    # No range specified, show all
    return None


def show_command(
    commit: Optional[str] = typer.Argument(None, help="Commit hash to show session from"),
    session: Optional[str] = typer.Option(None, "--session", "-s", help="Direct path to session file"),
    format_output: str = typer.Option("pretty", "--format", "-f", help="Output format: pretty, json, raw"),
    pager: bool = typer.Option(False, "--pager", "-p", help="Use pager (less) for output"),
    from_line: Optional[int] = typer.Option(None, "--from", help="Start from line number (inclusive)"),
    to_line: Optional[int] = typer.Option(None, "--to", help="End at line number (inclusive)"),
    around_line: Optional[int] = typer.Option(None, "--around", help="Show lines around this line number"),
    context: int = typer.Option(5, "--context", "-C", help="Number of lines before/after when using --around (default: 5)"),
    first: Optional[int] = typer.Option(None, "--first", help="Show only first N lines"),
    last: Optional[int] = typer.Option(None, "--last", help="Show only last N lines"),
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

    # Calculate line range
    line_range = calculate_line_range(
        from_line=from_line,
        to_line=to_line,
        around_line=around_line,
        context=context,
        first=first,
        last=last,
        total_lines=len(session_content.strip().split("\n")) if session_content else 0,
    )

    # Display session content
    if session_content:
        display_session(session_content, format_output, pager, session_path, line_range)


def display_session(content: str, format_type: str, use_pager: bool, session_path: Optional[str], line_range: Optional[tuple[int, int]] = None):
    """Display session content in specified format."""
    # Filter content by line range if specified
    if line_range is not None:
        start_line, end_line = line_range
        all_lines = content.strip().split("\n")
        filtered_lines = all_lines[start_line - 1:end_line]  # Convert to 0-indexed
        content = "\n".join(filtered_lines)

        # Show range info
        total_lines = len(all_lines)
        console.print(f"[dim]Showing lines {start_line}-{end_line} of {total_lines}[/dim]\n")

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
        format_session_pretty_direct(content, session_path, line_range)


def extract_username_from_filename(file_path: str) -> Optional[str]:
    """
    Extract username from session filename.
    Supports two formats:
    - New: username_agent_shortid.jsonl (e.g., alice_claude_a1b2c3d4.jsonl)
    - Old: timestamp_username_agent_shortid.jsonl (e.g., 1234567890_alice_claude_a1b2c3d4.jsonl)
    """
    try:
        from pathlib import Path
        filename = Path(file_path).stem  # Get filename without extension
        parts = filename.split('_')

        if len(parts) >= 3:
            if parts[0].isdigit():
                # Old format: timestamp_username_agent_shortid
                return parts[1]
            else:
                # New format: username_agent_shortid
                return parts[0]
    except Exception:
        pass
    # Return None if username cannot be extracted (e.g., UUID format)
    return None


def extract_agent_from_filename(file_path: str) -> Optional[str]:
    """
    Extract agent type from session filename.
    Supports two formats:
    - New: username_agent_shortid.jsonl (e.g., alice_claude_a1b2c3d4.jsonl)
    - Old: timestamp_username_agent_shortid.jsonl (e.g., 1234567890_alice_claude_a1b2c3d4.jsonl)
    Returns 'claude', 'codex', or None if not extractable.
    """
    try:
        from pathlib import Path
        filename = Path(file_path).stem  # Get filename without extension
        parts = filename.split('_')

        if len(parts) >= 3:
            if parts[0].isdigit():
                # Old format: timestamp_username_agent_shortid
                agent = parts[2]
            else:
                # New format: username_agent_shortid
                agent = parts[1]

            # Normalize agent name
            agent_lower = agent.lower()
            if agent_lower in ('claude', 'codex', 'unknown'):
                return agent_lower
    except Exception:
        pass
    return None


def extract_text_from_content(content):
    """Extract text from various content formats."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    texts.append(item.get("text", ""))
                elif "text" in item:
                    texts.append(item.get("text", ""))
            elif isinstance(item, str):
                texts.append(item)
        return "\n".join(texts) if texts else ""
    if isinstance(content, dict):
        # Handle nested content structure
        if "content" in content:
            return extract_text_from_content(content["content"])
        elif "text" in content:
            return content["text"]
    return str(content)


def format_session_pretty_direct(content: str, session_path: Optional[str], line_range: Optional[tuple[int, int]] = None):
    """Format and display session content in a pretty, readable way."""
    lines = content.strip().split("\n")

    # Extract username and agent from filename if available
    username = None
    agent_from_filename = None
    if session_path:
        username = extract_username_from_filename(session_path)
        agent_from_filename = extract_agent_from_filename(session_path)
        console.print(f"\n[bold cyan]Session: {session_path}[/bold cyan]\n")

    # Calculate starting line number for display
    start_line_num = line_range[0] if line_range else 1

    for i, line in enumerate(lines, start_line_num):
        try:
            # Try to parse as JSON (for JSONL format)
            obj = json.loads(line)

            role = None
            content_text = ""
            timestamp = obj.get("timestamp", "")
            model = None

            # Handle different message formats
            # Format 1: Claude Code format with type and message
            if obj.get("type") in ("user", "assistant"):
                role = obj.get("type")
                message = obj.get("message", {})
                if isinstance(message, dict):
                    content_text = extract_text_from_content(message.get("content", ""))
                    if role == "assistant":
                        model = message.get("model", "")
            # Format 2: Codex format
            elif obj.get("type") == "response_item":
                payload = obj.get("payload", {})
                if payload.get("type") == "message":
                    role = payload.get("role")
                    content = payload.get("content", [])
                    # Extract text from Codex content format
                    texts = []
                    for item in content if isinstance(content, list) else []:
                        if isinstance(item, dict):
                            # Codex uses "input_text" and "output_text" types
                            if item.get("type") in ("input_text", "output_text"):
                                texts.append(item.get("text", ""))
                    content_text = "\n".join(texts)
                    # Codex doesn't store model info in session files
                    model = None
                else:
                    # Skip non-message response_items (reasoning, session_meta, etc.)
                    continue
            # Format 3: Simple format with role and content
            elif "role" in obj and "content" in obj:
                role = obj.get("role")
                content_text = extract_text_from_content(obj.get("content"))
                if role == "assistant":
                    model = obj.get("model", "")
            else:
                # Skip non-message types (session_meta, etc.)
                obj_type = obj.get("type")
                if obj_type in ("session_meta", "reasoning", "session_start", "session_end"):
                    continue
                role = obj.get("role", "unknown")
                content_text = extract_text_from_content(obj.get("content", ""))

            # Skip if no role extracted or no content
            if not role or not content_text or not content_text.strip():
                continue

            # Build title with username/model info and line number
            if role == "user":
                display_username = username or "unknown"
                title = f"[bold blue]User ({display_username})[/bold blue] [dim]line {i}[/dim] {timestamp}"
                console.print(
                    Panel(
                        content_text,
                        title=title,
                        border_style="blue",
                        padding=(1, 2),
                    )
                )
            elif role == "assistant":
                # Try to get model from content first, fallback to agent from filename
                if model:
                    # Check if it's just an agent name or full model name
                    if model.lower() in ('codex', 'claude', 'unknown'):
                        display_model = model
                    else:
                        # Full model name - extract short version
                        display_model = model.split('-2024')[0].split('-2025')[0]
                elif agent_from_filename:
                    # Use agent type from filename
                    display_model = agent_from_filename
                else:
                    display_model = "unknown"
                title = f"[bold green]Assistant ({display_model})[/bold green] [dim]line {i}[/dim] {timestamp}"
                console.print(
                    Panel(
                        content_text,
                        title=title,
                        border_style="green",
                        padding=(1, 2),
                    )
                )
            else:
                console.print(
                    Panel(
                        content_text,
                        title=f"[bold yellow]{role.title()}[/bold yellow] [dim]line {i}[/dim] {timestamp}",
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
