"""ReAlign init command - Initialize ReAlign in a git repository."""

import os
import subprocess
import yaml
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.prompt import Confirm

from ..config import ReAlignConfig, get_default_config_content

console = Console()


def init_command(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts"),
    skip_commit: bool = typer.Option(False, "--skip-commit", help="Skip auto-commit of hooks"),
):
    """Initialize ReAlign in the current git repository."""
    # Check if we're in a git repository
    is_git_repo = True
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        is_git_repo = False

    # If not a git repo, offer to initialize it
    if not is_git_repo:
        console.print("[yellow]⚠ Not in a git repository.[/yellow]")
        if yes or Confirm.ask("Would you like to initialize a git repository here?", default=True):
            try:
                subprocess.run(["git", "init"], check=True)
                console.print("[green]✓[/green] Initialized git repository")
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Error initializing git repository:[/red] {e}")
                raise typer.Exit(1)
        else:
            console.print("[red]Error: Not in a git repository. Please run from a git repo.[/red]")
            raise typer.Exit(1)

    repo_root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )

    console.print(f"[blue]Initializing ReAlign in:[/blue] {repo_root}")

    # Create directory structure
    realign_dir = repo_root / ".realign"
    hooks_dir = realign_dir / "hooks"
    sessions_dir = realign_dir / "sessions"

    for directory in [realign_dir, hooks_dir, sessions_dir]:
        directory.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓[/green] Created directory: {directory.relative_to(repo_root)}")

    # Create prepare-commit-msg hook
    # Install pre-commit hook
    pre_commit_path = hooks_dir / "pre-commit"
    if not pre_commit_path.exists():
        pre_commit_content = get_pre_commit_hook()
        pre_commit_path.write_text(pre_commit_content, encoding="utf-8")
        pre_commit_path.chmod(0o755)
        console.print(
            f"[green]✓[/green] Created hook: {pre_commit_path.relative_to(repo_root)} (executable)"
        )
    else:
        console.print(f"[yellow]⚠[/yellow] Hook already exists: {pre_commit_path.relative_to(repo_root)}")

    # Install prepare-commit-msg hook
    hook_path = hooks_dir / "prepare-commit-msg"
    if not hook_path.exists():
        hook_content = get_prepare_commit_msg_hook()
        hook_path.write_text(hook_content, encoding="utf-8")
        hook_path.chmod(0o755)
        console.print(
            f"[green]✓[/green] Created hook: {hook_path.relative_to(repo_root)} (executable)"
        )
    else:
        console.print(f"[yellow]⚠[/yellow] Hook already exists: {hook_path.relative_to(repo_root)}")


    # Create .gitignore for sessions (optional - commented out for MVP)
    gitignore_path = realign_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text("# Uncomment to ignore session files\n# sessions/\n", encoding="utf-8")

    # Backup and set core.hooksPath
    backup_file = realign_dir / "backup_hook_config.yaml"
    try:
        current_hooks_path = subprocess.run(
            ["git", "config", "--local", "core.hooksPath"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()

        if current_hooks_path and current_hooks_path != ".realign/hooks":
            console.print(f"[yellow]⚠ Current core.hooksPath:[/yellow] {current_hooks_path}")

            if not yes and not Confirm.ask("Overwrite existing core.hooksPath?"):
                console.print("[yellow]Initialization cancelled.[/yellow]")
                raise typer.Exit(0)

            # Backup old configuration
            backup_data = {
                "original_hooks_path": current_hooks_path,
                "backup_timestamp": subprocess.run(
                    ["date", "+%Y-%m-%d %H:%M:%S"],
                    capture_output=True,
                    text=True,
                    check=False,
                ).stdout.strip(),
            }
            with open(backup_file, "w", encoding="utf-8") as f:
                yaml.dump(backup_data, f)
            console.print(f"[green]✓[/green] Backed up old hooks config to {backup_file.name}")

        # Set new hooks path
        subprocess.run(
            ["git", "config", "--local", "core.hooksPath", ".realign/hooks"],
            check=True,
        )
        console.print("[green]✓[/green] Set core.hooksPath to .realign/hooks")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error setting git config:[/red] {e}")
        raise typer.Exit(1)

    # Initialize global config if not exists
    global_config_path = Path.home() / ".config" / "realign" / "config.yaml"
    if not global_config_path.exists():
        global_config_path.parent.mkdir(parents=True, exist_ok=True)
        global_config_path.write_text(get_default_config_content(), encoding="utf-8")
        console.print(f"[green]✓[/green] Created global config: {global_config_path}")
    else:
        console.print(f"[blue]ℹ[/blue] Global config already exists: {global_config_path}")

    # Create local history directory
    config = ReAlignConfig.load()
    history_dir = config.expanded_local_history_path
    history_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]✓[/green] Ensured history directory exists: {history_dir}")

    # Add hooks to git (optional commit)
    if not skip_commit:
        try:
            subprocess.run(["git", "add", ".realign/hooks/prepare-commit-msg"], check=True)
            console.print("[green]✓[/green] Added hook to git staging area")

            # Try to commit (may fail if no changes, which is fine)
            result = subprocess.run(
                ["git", "commit", "-m", "chore(realign): add prepare-commit-msg hook", "--no-verify"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                console.print("[green]✓[/green] Committed hook to repository")
            else:
                console.print("[yellow]ℹ[/yellow] Hook staged but not committed (no changes or already committed)")
        except subprocess.CalledProcessError:
            console.print("[yellow]⚠[/yellow] Could not auto-commit hook (you can commit manually)")

    # Print next steps
    console.print("\n[bold green]✓ ReAlign initialized successfully![/bold green]\n")
    console.print("[bold]Next steps:[/bold]")
    console.print("  1. Ensure your agent saves chat histories to:", style="dim")
    console.print(f"     {history_dir}", style="cyan")
    console.print("  2. Make commits as usual - ReAlign will automatically track sessions", style="dim")
    console.print("  3. Search sessions with: [cyan]realign search <keyword>[/cyan]", style="dim")
    console.print("  4. View sessions with: [cyan]realign show <commit>[/cyan]", style="dim")
    console.print("\n[bold]Optional: Enable Git LFS for sessions[/bold]")
    console.print("  git lfs install", style="dim cyan")
    console.print("  git lfs track '.realign/sessions/*.jsonl'", style="dim cyan")
    console.print("  git add .gitattributes && git commit -m 'chore: track sessions with LFS' --no-verify", style="dim cyan")


def get_pre_commit_hook() -> str:
    """Get the pre-commit hook script content."""
    return '''#!/bin/bash
# ReAlign pre-commit hook
# Finds and stages agent session files before commit

# 1. Try to find realign-hook-pre-commit in PATH first (pipx/pip installations)
if command -v realign-hook-pre-commit >/dev/null 2>&1; then
    VERSION=$(realign version 2>/dev/null | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+' || echo "unknown")
    echo "ReAlign pre-commit hook (dev-$VERSION)" >&2
    exec realign-hook-pre-commit "$@"
fi

# 2. Try using uvx (for MCP installations where command is in uvx cache)
if command -v uvx >/dev/null 2>&1; then
    VERSION=$(uvx --from realign-git realign version 2>/dev/null | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+' || echo "unknown")
    echo "ReAlign pre-commit hook (release-$VERSION)" >&2
    exec uvx --from realign-git realign-hook-pre-commit "$@"
fi

# If all else fails, print an error
echo "Error: Cannot find realign. Please ensure it's installed:" >&2
echo "  - For CLI: pipx install realign-git" >&2
echo "  - For MCP: Ensure uvx is available" >&2
exit 1
'''


def get_prepare_commit_msg_hook() -> str:
    """Get the prepare-commit-msg hook script content."""
    return '''#!/bin/bash
# ReAlign prepare-commit-msg hook
# Adds agent session metadata to commit messages

COMMIT_MSG_FILE="$1"
COMMIT_SOURCE="$2"

# Skip for merge, squash, and commit --amend (but allow message and template)
if [ "$COMMIT_SOURCE" = "merge" ] || [ "$COMMIT_SOURCE" = "squash" ] || [ "$COMMIT_SOURCE" = "commit" ]; then
    exit 0
fi

# 1. Try to find realign-hook-prepare-commit-msg in PATH first (pipx/pip installations)
if command -v realign-hook-prepare-commit-msg >/dev/null 2>&1; then
    VERSION=$(realign version 2>/dev/null | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+' || echo "unknown")
    echo "ReAlign prepare-commit-msg hook (dev-$VERSION)" >&2
    exec realign-hook-prepare-commit-msg "$@"
fi

# 2. Try using uvx (for MCP installations where command is in uvx cache)
if command -v uvx >/dev/null 2>&1; then
    VERSION=$(uvx --from realign-git realign version 2>/dev/null | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+' || echo "unknown")
    echo "ReAlign prepare-commit-msg hook (release-$VERSION)" >&2
    exec uvx --from realign-git realign-hook-prepare-commit-msg "$@"
fi

# If all else fails, print an error
echo "Error: Cannot find realign. Please ensure it's installed:" >&2
echo "  - For CLI: pipx install realign-git" >&2
echo "  - For MCP: Ensure uvx is available" >&2
exit 1
'''


if __name__ == "__main__":
    typer.run(init_command)
