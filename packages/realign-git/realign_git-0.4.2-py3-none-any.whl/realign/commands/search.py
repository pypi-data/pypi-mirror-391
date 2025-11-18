"""ReAlign search command - Search through agent sessions and commit history."""

import subprocess
import re
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import typer
from rich.console import Console
from rich.table import Table

console = Console()


def search_command(
    keyword: str = typer.Argument(..., help="Keyword to search for"),
    show_session: bool = typer.Option(False, "--show-session", help="Show session content for matches"),
    max_results: int = typer.Option(20, "--max", "-n", help="Maximum number of results to show"),
    session_only: bool = typer.Option(False, "--session-only", help="Search only in session files, not commits"),
    commits_only: bool = typer.Option(False, "--commits-only", help="Search only in commits, not session files"),
):
    """Search through agent sessions and commit history."""
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

    console.print(f"[blue]Searching for:[/blue] '{keyword}'")

    # Determine what to search based on flags
    search_commits = not session_only
    search_sessions = not commits_only

    # Search in commit messages (including Agent-Summary footers)
    if search_commits:
        console.print("\n[bold]Commits with matching summaries:[/bold]")

        try:
            # Use a unique separator to split commits
            # Format: hash|author|subject|body
            result = subprocess.run(
                ["git", "log", f"--grep={keyword}", "-i", "--pretty=format:%H|%an|%s|%b%x00", f"-n{max_results}"],
                capture_output=True,
                text=True,
                check=True,
                cwd=repo_root,
            )

            if result.stdout:
                commits = []
                # Split by null byte to separate commits
                commit_entries = result.stdout.split("\x00")

                for entry in commit_entries:
                    entry = entry.strip()
                    if not entry:
                        continue

                    # Split only at the first three pipes to preserve body content
                    parts = entry.split("|", 3)
                    if len(parts) >= 3:
                        commit_hash = parts[0][:8]
                        author = parts[1]
                        subject = parts[2]
                        body = parts[3] if len(parts) > 3 else ""

                        # Extract Agent-Summary and Agent-Session-Paths from body
                        summary_match = re.search(r"Agent-Summary:\s*(.+?)(?=\nAgent-|\n\n|\Z)", body, re.DOTALL)
                        session_match = re.search(r"Agent-Session-Paths?:\s*(.+?)(?:\n|$)", body)

                        summary = summary_match.group(1).strip() if summary_match else ""
                        session_path = session_match.group(1) if session_match else ""

                        commits.append({
                            "hash": commit_hash,
                            "author": author,
                            "subject": subject,
                            "body": body,
                            "summary": summary,
                            "session_path": session_path,
                        })

                if commits:
                    def highlight_text(text: str, keyword: str) -> str:
                        """Highlight keyword in text (case-insensitive)."""
                        if not keyword or not text:
                            return text
                        # Use regex to find and replace keyword (case-insensitive)
                        pattern = re.compile(f'({re.escape(keyword)})', re.IGNORECASE)
                        return pattern.sub(r'[black on yellow]\1[/black on yellow]', text)

                    for i, commit in enumerate(commits, 1):
                        console.print(f"\n[bold cyan]{i}. Commit {commit['hash']}[/bold cyan] by [green]{commit['author']}[/green]")
                        console.print(f"   [bold]{highlight_text(commit['subject'], keyword)}[/bold]")

                        # Show body if it exists (excluding agent metadata)
                        if commit["body"]:
                            # Remove Agent-* metadata from body for display
                            display_body = re.sub(r'\n*Agent-Summary:.*', '', commit["body"], flags=re.DOTALL)
                            display_body = re.sub(r'\n*Agent-Session-Paths?:.*', '', display_body, flags=re.DOTALL)
                            display_body = display_body.strip()
                            if display_body:
                                # Indent body lines
                                for line in display_body.split('\n'):
                                    console.print(f"   {highlight_text(line, keyword)}")

                        # Show Agent-Summary if it exists
                        if commit["summary"]:
                            console.print(f"   [yellow]Agent-Summary: {highlight_text(commit['summary'], keyword)}[/yellow]")

                        if commit["session_path"]:
                            console.print(f"   [dim]Session: {commit['session_path']}[/dim]")

                    # Show session content if requested
                    if show_session and commits:
                        console.print("\n[bold]Session content:[/bold]")
                        for commit in commits[:5]:  # Limit to first 5 for session display
                            if commit["session_path"]:
                                show_session_content(repo_root, commit["hash"], commit["session_path"])
                else:
                    console.print("[yellow]No commits found matching the keyword.[/yellow]")
            else:
                console.print("[yellow]No commits found matching the keyword.[/yellow]")

        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error searching commits:[/red] {e}")

    # Search in session files
    if search_sessions:
        sessions_dir = repo_root / ".realign" / "sessions"
        if sessions_dir.exists():
            console.print("\n[bold]Session file matches:[/bold]")

            try:
                result = subprocess.run(
                    ["grep", "-r", "-i", "-l", keyword, str(sessions_dir)],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.stdout:
                    matching_files = result.stdout.strip().split("\n")
                    for file_path in matching_files[:max_results]:
                        rel_path = Path(file_path).relative_to(repo_root)
                        console.print(f"\n[bold cyan]• {rel_path}[/bold cyan]")

                        # Show parsed session content with context
                        display_session_matches(Path(file_path), keyword, max_matches=5)
                else:
                    console.print("[yellow]No session files found matching the keyword.[/yellow]")

            except subprocess.CalledProcessError:
                console.print("[yellow]Could not search session files.[/yellow]")


def show_session_content(repo_root: Path, commit_hash: str, session_path: str):
    """Show content of a session file from a commit."""
    console.print(f"\n[bold cyan]Session for commit {commit_hash}:[/bold cyan]")

    session_file = repo_root / session_path
    if session_file.exists():
        show_file_content(session_file)
    else:
        console.print(f"[yellow]Session file not found:[/yellow] {session_path}")


def show_file_content(file_path: Path, highlight: Optional[str] = None, max_lines: int = 20):
    """Show content of a file with optional highlighting."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        console.print(f"[dim]Showing first {min(len(lines), max_lines)} lines...[/dim]")

        for i, line in enumerate(lines[:max_lines], 1):
            if highlight and highlight.lower() in line.lower():
                console.print(f"{i:4d}: [yellow]{line.rstrip()}[/yellow]")
            else:
                console.print(f"{i:4d}: {line.rstrip()}")

        if len(lines) > max_lines:
            console.print(f"[dim]... ({len(lines) - max_lines} more lines)[/dim]")

    except Exception as e:
        console.print(f"[red]Error reading file:[/red] {e}")


def extract_text_from_content(content: Any) -> str:
    """Extract plain text from various content formats."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text" and "text" in item:
                    texts.append(item["text"])
            elif isinstance(item, str):
                texts.append(item)
        return " ".join(texts)
    elif isinstance(content, dict):
        if "text" in content:
            return content["text"]
        elif "content" in content:
            return extract_text_from_content(content["content"])
    return ""


def extract_username_from_filename(file_path: Path) -> Optional[str]:
    """
    Extract username from session filename.
    Supports two formats:
    - New: username_agent_shortid.jsonl (e.g., alice_claude_a1b2c3d4.jsonl)
    - Old: timestamp_username_agent_shortid.jsonl (e.g., 1234567890_alice_claude_a1b2c3d4.jsonl)
    """
    try:
        filename = file_path.stem  # Get filename without extension
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


def extract_agent_from_filename(file_path: Path) -> Optional[str]:
    """
    Extract agent type from session filename.
    Supports two formats:
    - New: username_agent_shortid.jsonl (e.g., alice_claude_a1b2c3d4.jsonl)
    - Old: timestamp_username_agent_shortid.jsonl (e.g., 1234567890_alice_claude_a1b2c3d4.jsonl)
    Returns 'claude', 'codex', or None if not extractable.
    """
    try:
        filename = file_path.stem  # Get filename without extension
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


def search_in_session_file(file_path: Path, keyword: str, max_matches: int = 5) -> List[Dict[str, Any]]:
    """
    Search for keyword in a session file and return matching messages with context.

    Returns a list of dicts with: role, text, timestamp, line_number, username (optional), model (optional)
    """
    matches = []
    # Extract username and agent type from filename
    username = extract_username_from_filename(file_path)
    agent_from_filename = extract_agent_from_filename(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)

                    # Extract role and message content
                    role = None
                    text = ""
                    timestamp = data.get("timestamp", "")
                    model = None

                    # Handle different message formats
                    # Format 1: Claude Code format
                    if data.get("type") in ("user", "assistant"):
                        role = data.get("type")
                        message = data.get("message", {})
                        if isinstance(message, dict):
                            content = message.get("content", "")
                            text = extract_text_from_content(content)
                            # Extract model name for assistant messages
                            if role == "assistant":
                                model = message.get("model", "")
                    # Format 2: Codex format
                    elif data.get("type") == "response_item":
                        payload = data.get("payload", {})
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
                            text = "\n".join(texts)
                            # Codex doesn't store model info in session files
                            model = None
                    # Format 3: Simple JSONL format
                    elif "role" in data and "content" in data:
                        role = data.get("role")
                        text = extract_text_from_content(data.get("content"))
                        # Extract model name for assistant messages
                        if role == "assistant":
                            model = data.get("model", "")

                    # Check if keyword is in the text (case-insensitive)
                    if role and text and keyword.lower() in text.lower():
                        # If no model from content, use agent from filename (for Codex)
                        if not model and agent_from_filename:
                            model = agent_from_filename

                        matches.append({
                            "role": role,
                            "text": text,
                            "timestamp": timestamp,
                            "line_number": line_num,
                            "username": username,
                            "model": model,
                        })

                        if len(matches) >= max_matches:
                            break

                except json.JSONDecodeError:
                    continue

    except Exception as e:
        console.print(f"[red]Error reading session file:[/red] {e}")

    return matches


def display_session_matches(file_path: Path, keyword: str, max_matches: int = 5):
    """Display matching messages from a session file with context and highlighting."""
    matches = search_in_session_file(file_path, keyword, max_matches)

    if not matches:
        return

    def highlight_text(text: str, keyword: str) -> str:
        """Highlight keyword in text (case-insensitive)."""
        if not keyword or not text:
            return text
        pattern = re.compile(f'({re.escape(keyword)})', re.IGNORECASE)
        return pattern.sub(r'[black on yellow]\1[/black on yellow]', text)

    for i, match in enumerate(matches, 1):
        role_color = "blue" if match["role"] == "user" else "green"

        # Build role label with optional username/model
        role_label = match['role'].upper()
        if match['role'] == 'user':
            username = match.get('username') or 'unknown'
            role_label = f"USER ({username})"
        elif match['role'] == 'assistant':
            model_name = match.get('model')
            if model_name:
                # Check if it's just an agent name (codex, claude, unknown) or full model name
                if model_name.lower() in ('codex', 'claude', 'unknown'):
                    # Agent name from filename
                    role_label = f"ASSISTANT ({model_name})"
                else:
                    # Full model name from session content - extract short version
                    model_short = model_name.split('-2024')[0].split('-2025')[0]  # Remove date suffix
                    role_label = f"ASSISTANT ({model_short})"
            else:
                role_label = "ASSISTANT (unknown)"

        console.print(f"\n  [bold {role_color}]{role_label}[/bold {role_color}] (line {match['line_number']})")

        # Truncate and highlight text
        text = match["text"]
        if len(text) > 500:
            # Find keyword position and show context around it
            keyword_pos = text.lower().find(keyword.lower())
            if keyword_pos != -1:
                start = max(0, keyword_pos - 200)
                end = min(len(text), keyword_pos + 300)
                text = ("..." if start > 0 else "") + text[start:end] + ("..." if end < len(text) else "")

        # Display with highlighting and indentation
        for line in text.split('\n'):
            if line.strip():
                console.print(f"    {highlight_text(line, keyword)}")


if __name__ == "__main__":
    typer.run(search_command)
