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


def format_session_pretty_direct(content: str, session_path: Optional[str]):
    """Format and display session content in a pretty, readable way."""
    lines = content.strip().split("\n")

    # Extract username and agent from filename if available
    username = None
    agent_from_filename = None
    if session_path:
        username = extract_username_from_filename(session_path)
        agent_from_filename = extract_agent_from_filename(session_path)
        console.print(f"\n[bold cyan]Session: {session_path}[/bold cyan]\n")

    for i, line in enumerate(lines, 1):
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

            # Build title with username/model info
            if role == "user":
                display_username = username or "unknown"
                title = f"[bold blue]User ({display_username})[/bold blue] {timestamp}"
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
                title = f"[bold green]Assistant ({display_model})[/bold green] {timestamp}"
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
