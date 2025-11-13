"""ReAlign search command - Search through agent sessions and commit history."""

import subprocess
import re
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

console = Console()


def search_command(
    keyword: str = typer.Argument(..., help="Keyword to search for"),
    show_session: bool = typer.Option(False, "--show-session", help="Show session content for matches"),
    max_results: int = typer.Option(20, "--max", "-n", help="Maximum number of results to show"),
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

    # Search in commit messages (including Agent-Summary footers)
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
    sessions_dir = repo_root / ".realign" / "sessions"
    if sessions_dir.exists():
        console.print("\n[bold]Direct session file matches:[/bold]")

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
                    console.print(f"  [cyan]•[/cyan] {rel_path}")

                    if show_session:
                        show_file_content(Path(file_path), keyword)
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


if __name__ == "__main__":
    typer.run(search_command)
