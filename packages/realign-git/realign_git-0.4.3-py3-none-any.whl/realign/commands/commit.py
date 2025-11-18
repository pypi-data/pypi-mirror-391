"""ReAlign commit command - Smart commit with session tracking."""

import os
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
import typer
from rich.console import Console

from ..config import ReAlignConfig
from ..hooks import find_all_active_sessions

console = Console()


def has_file_changes() -> bool:
    """
    Check if there are any staged or unstaged file changes (excluding .realign/sessions/).

    Returns:
        True if there are file changes, False otherwise
    """
    try:
        # Check for unstaged changes (excluding .realign/sessions/)
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        unstaged = [
            line.strip()
            for line in result.stdout.strip().split('\n')
            if line.strip() and not line.strip().startswith('.realign/sessions/')
        ]

        # Check for staged changes (excluding .realign/sessions/)
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        staged = [
            line.strip()
            for line in result.stdout.strip().split('\n')
            if line.strip() and not line.strip().startswith('.realign/sessions/')
        ]

        # Check for untracked files (excluding .realign/sessions/)
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            check=True,
        )
        untracked = [
            line.strip()
            for line in result.stdout.strip().split('\n')
            if line.strip() and not line.strip().startswith('.realign/sessions/')
        ]

        return bool(unstaged or staged or untracked)

    except subprocess.CalledProcessError:
        return False


def has_session_changes(repo_root: Path) -> Tuple[bool, List[Path]]:
    """
    Check if there are new AI session changes.

    Returns:
        Tuple of (has_changes, session_files)
    """
    config = ReAlignConfig.load()

    # Find all active session files
    session_files = find_all_active_sessions(config, repo_root)

    if not session_files:
        return False, []

    # Check if any session file has been modified recently (within last 5 minutes)
    import time
    current_time = time.time()
    recent_sessions = []

    for session_file in session_files:
        if session_file.exists():
            mtime = session_file.stat().st_mtime
            # Consider sessions modified in the last 5 minutes as "new"
            if current_time - mtime < 300:  # 5 minutes
                recent_sessions.append(session_file)

    return bool(recent_sessions), recent_sessions


def stage_all_changes():
    """Stage all changes including untracked files."""
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        console.print("[green]✓[/green] Staged all changes")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error staging changes:[/red] {e}")
        raise typer.Exit(1)


def commit_command(
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Commit message"),
    all_files: bool = typer.Option(False, "--all", "-a", help="Stage all changes before commit"),
    amend: bool = typer.Option(False, "--amend", help="Amend the previous commit"),
    no_edit: bool = typer.Option(False, "--no-edit", help="Use previous commit message (with --amend)"),
):
    """
    Smart commit command with AI session tracking.

    - If there are file changes: acts like `git commit`
    - If there are only session changes: creates an empty commit with session tracking
    - If there are no changes: shows an error
    """
    # Check if we're in a git repository
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
        repo_root = Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        console.print("[red]Error: Not in a git repository[/red]")
        raise typer.Exit(1)

    # Stage all changes if --all flag is set
    if all_files:
        stage_all_changes()

    # Check for file changes and session changes
    has_files = has_file_changes()
    has_sessions, session_files = has_session_changes(repo_root)

    # Determine commit type
    if not has_files and not has_sessions:
        console.print("[yellow]⚠ No changes detected[/yellow]")
        console.print("  • No file changes")
        console.print("  • No recent AI session updates")
        console.print("\n[dim]Tip: Use `git status` to see your repository status[/dim]")
        raise typer.Exit(1)

    # Build git commit command
    commit_cmd = ["git", "commit"]

    # Add message if provided
    if message:
        commit_cmd.extend(["-m", message])

    # Add amend flag if set
    if amend:
        commit_cmd.append("--amend")
        if no_edit:
            commit_cmd.append("--no-edit")

    # If only session changes, use --allow-empty
    if has_sessions and not has_files:
        commit_cmd.append("--allow-empty")
        console.print("[cyan]💬 Detected AI session changes without file changes[/cyan]")
        console.print(f"[dim]   Found {len(session_files)} recent session(s)[/dim]")
        console.print("[cyan]   Creating discussion commit...[/cyan]")
    elif has_files and has_sessions:
        console.print("[green]📝 Detected both file changes and AI session updates[/green]")
    elif has_files:
        console.print("[green]📝 Committing file changes[/green]")

    # Execute git commit
    try:
        # If no message provided and not amending, git will open editor
        result = subprocess.run(
            commit_cmd,
            check=True,
            capture_output=False,  # Let git output go to terminal
        )
        console.print("[green]✓[/green] Commit created successfully")

        # Show commit hash
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        commit_hash = result.stdout.strip()
        console.print(f"[dim]   Commit: {commit_hash}[/dim]")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error creating commit:[/red] {e}")
        raise typer.Exit(1)
