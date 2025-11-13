#!/usr/bin/env python3
"""
ReAlign Git Hooks - Entry points for git hook commands.

This module provides the hook functionality as Python commands that can be
invoked directly from git hooks without copying any Python files to the target repository.
"""

import os
import sys
import json
import time
import uuid
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List

from .config import ReAlignConfig
from .claude_detector import find_claude_sessions_dir


def get_new_content_from_git_diff(repo_root: Path, session_relpath: str) -> str:
    """
    Extract new content added in this commit by using git diff.
    Returns the raw text of all added lines, without parsing.

    Args:
        repo_root: Path to git repository root
        session_relpath: Relative path to session file in repo (e.g. ".realign/sessions/xxx.jsonl")

    Returns:
        String containing all new content added in this commit
    """
    try:
        # Try to get diff from HEAD (last commit)
        # This shows lines added since last commit
        result = subprocess.run(
            ["git", "diff", "HEAD", "--", session_relpath],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
        )

        # If file doesn't exist in HEAD (new file), get all content
        if result.returncode != 0 or not result.stdout.strip():
            # File is new or no diff, read entire file
            session_file = repo_root / session_relpath
            if session_file.exists():
                with open(session_file, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                return ""
        else:
            # Parse diff output to extract added lines
            new_lines = []
            for line in result.stdout.split("\n"):
                # Lines starting with '+' (but not '+++') are additions
                if line.startswith("+") and not line.startswith("+++"):
                    # Remove the '+' prefix
                    new_lines.append(line[1:])

            return "\n".join(new_lines)

    except subprocess.TimeoutExpired:
        print("Warning: git diff command timed out", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"Warning: Could not extract new content from git diff: {e}", file=sys.stderr)
        return ""


def get_claude_project_name(project_path: Path) -> str:
    """
    Convert a project path to Claude Code's project directory name format.

    Claude Code transforms project paths by replacing '/' with '-' (excluding root '/').
    For example: /Users/alice/Projects/MyApp -> -Users-alice-Projects-MyApp
    """
    abs_path = project_path.resolve()
    path_str = str(abs_path)
    if path_str.startswith('/'):
        path_str = path_str[1:]
    return '-' + path_str.replace('/', '-')


def find_codex_latest_session(project_path: Path, days_back: int = 7) -> Optional[Path]:
    """
    Find the most recent Codex session for a given project path.

    Codex stores sessions in ~/.codex/sessions/{YYYY}/{MM}/{DD}/
    with all projects mixed together. We need to search by date
    and filter by the 'cwd' field in session metadata.

    Args:
        project_path: The absolute path to the project
        days_back: Number of days to look back (default: 7)

    Returns:
        Path to the most recent session file, or None if not found
    """
    from datetime import datetime, timedelta

    codex_sessions_base = Path.home() / ".codex" / "sessions"

    if not codex_sessions_base.exists():
        return None

    # Normalize project path for comparison
    abs_project_path = str(project_path.resolve())

    matching_sessions = []

    # Search through recent days
    for days_ago in range(days_back + 1):
        target_date = datetime.now() - timedelta(days=days_ago)
        date_path = codex_sessions_base / str(target_date.year) / f"{target_date.month:02d}" / f"{target_date.day:02d}"

        if not date_path.exists():
            continue

        # Check all session files in this date directory
        for session_file in date_path.glob("rollout-*.jsonl"):
            try:
                # Read first line to get session metadata
                with open(session_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    if first_line:
                        data = json.loads(first_line)
                        if data.get('type') == 'session_meta':
                            session_cwd = data.get('payload', {}).get('cwd', '')
                            # Match the project path
                            if session_cwd == abs_project_path:
                                matching_sessions.append(session_file)
            except (json.JSONDecodeError, IOError):
                # Skip malformed or unreadable files
                continue

    # Sort by modification time, newest first
    matching_sessions.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return matching_sessions[0] if matching_sessions else None


def find_all_active_sessions(
    config: ReAlignConfig,
    project_path: Optional[Path] = None
) -> List[Path]:
    """
    Find all active session files based on enabled auto-detection options.

    Returns a list of session file paths from all enabled sources:
    - Codex session (if auto_detect_codex is True)
    - Claude Code latest session (if auto_detect_claude is True)
    - Sessions from local_history_path (if no auto-detection or as fallback)

    Args:
        config: Configuration object
        project_path: Optional path to the current project (git repo root)

    Returns:
        List of session file paths (may be empty if no sessions found)
    """
    sessions = []

    # If REALIGN_LOCAL_HISTORY_PATH is set, only use that path (disables auto-detection)
    if os.getenv("REALIGN_LOCAL_HISTORY_PATH"):
        history_path = config.expanded_local_history_path
        session = find_latest_session(history_path)
        if session:
            sessions.append(session)
        return sessions

    # Try Codex auto-detection if enabled
    if config.auto_detect_codex and project_path:
        codex_session = find_codex_latest_session(project_path)
        if codex_session:
            sessions.append(codex_session)

    # Try Claude auto-detection if enabled
    if config.auto_detect_claude and project_path:
        claude_dir = find_claude_sessions_dir(project_path)
        if claude_dir:
            claude_session = find_latest_session(claude_dir)
            if claude_session:
                sessions.append(claude_session)

    # If no sessions found from auto-detection, try fallback path
    if not sessions:
        history_path = config.expanded_local_history_path
        session = find_latest_session(history_path)
        if session:
            sessions.append(session)

    return sessions


def find_latest_session(history_path: Path, explicit_path: Optional[str] = None) -> Optional[Path]:
    """
    Find the most recent session file.

    Args:
        history_path: Path to history directory or a specific session file (for Codex)
        explicit_path: Explicit path to a session file (overrides history_path)

    Returns:
        Path to the session file, or None if not found
    """
    if explicit_path:
        session_file = Path(explicit_path)
        if session_file.exists():
            return session_file
        return None

    # Expand user path
    history_path = Path(os.path.expanduser(history_path)) if isinstance(history_path, str) else history_path

    if not history_path.exists():
        return None

    # If history_path is already a file (e.g., Codex session), return it directly
    if history_path.is_file():
        return history_path

    # Otherwise, search directory for session files
    session_files = []
    for pattern in ["*.json", "*.jsonl"]:
        session_files.extend(history_path.glob(pattern))

    if not session_files:
        return None

    # Return most recently modified
    return max(session_files, key=lambda p: p.stat().st_mtime)


def simple_summarize(content: str, max_chars: int = 500) -> str:
    """
    Generate a simple summary from new session content.
    Extracts key information without LLM.

    Args:
        content: Raw text content of new session additions
        max_chars: Maximum characters in summary
    """
    if not content or not content.strip():
        return "No new content in this session"

    lines = content.strip().split("\n")

    # Try to extract meaningful content from JSONL format
    summaries = []
    for line in lines[:10]:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            # Extract summary from special summary lines
            if obj.get("type") == "summary" and obj.get("summary"):
                summaries.append(f"Summary: {obj.get('summary')}")
            # Extract message content from user/assistant messages (complex format)
            elif obj.get("type") in ("user", "assistant") and obj.get("message"):
                msg = obj.get("message")
                if isinstance(msg, dict) and msg.get("content"):
                    content_text = msg.get("content")
                    if isinstance(content_text, str):
                        summaries.append(content_text[:100])
                    elif isinstance(content_text, list):
                        for item in content_text:
                            if isinstance(item, dict) and item.get("type") == "text":
                                summaries.append(item.get("text", "")[:100])
                                break
            # Also handle simple role/content format (for compatibility)
            elif obj.get("role") in ("user", "assistant") and obj.get("content"):
                content_text = obj.get("content")
                if isinstance(content_text, str):
                    summaries.append(content_text[:100])
        except (json.JSONDecodeError, KeyError, TypeError):
            # Not JSON or doesn't have expected structure, try raw text
            if len(line) > 20:
                summaries.append(line[:100])

    if summaries:
        summary = " | ".join(summaries[:3])
        return summary[:max_chars]

    return f"Session updated with {len(lines)} new lines"


def generate_summary_with_llm(content: str, max_chars: int = 500) -> Optional[str]:
    """
    Generate summary using LLM (Anthropic Claude or OpenAI) for NEW content only.
    Returns None if LLM is not available or fails.

    Tries providers in order:
    1. Anthropic (Claude) - if ANTHROPIC_API_KEY is set
    2. OpenAI (GPT) - if OPENAI_API_KEY is set

    Args:
        content: Raw text content of new session additions
        max_chars: Maximum characters in summary
    """
    if not content or not content.strip():
        return "No new content in this session"

    # Truncate content for API (to avoid token limits)
    # Approximately 4000 chars = ~1000 tokens
    truncated_content = content[:4000]

    # System prompt for summarization
    system_prompt = (
        "You are a helpful assistant that summarizes NEW content added to AI agent chat sessions. "
        "Provide a concise summary in Chinese (中文) focusing on the main topics and actions in the NEW content."
    )
    user_prompt = f"Summarize this NEW content from an AI chat session in one or two sentences:\n\n{truncated_content}"

    # Try Anthropic (Claude) first
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        print("   → Trying Anthropic (Claude)...", file=sys.stderr)
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)

            response = client.messages.create(
                model="claude-3-5-haiku-20241022",  # Fast and cost-effective
                max_tokens=150,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            summary = response.content[0].text.strip()
            print("   ✅ Anthropic (Claude) summary successful", file=sys.stderr)
            return summary[:max_chars]

        except ImportError:
            print("   ❌ Anthropic package not installed, trying OpenAI...", file=sys.stderr)
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
                print(f"   ❌ Anthropic authentication failed (check API key), trying OpenAI...", file=sys.stderr)
            elif "quota" in error_msg.lower() or "credit" in error_msg.lower():
                print(f"   ❌ Anthropic quota/credit issue, trying OpenAI...", file=sys.stderr)
            else:
                print(f"   ❌ Anthropic API error: {e}, trying OpenAI...", file=sys.stderr)
    else:
        print("   ⓘ ANTHROPIC_API_KEY not set, trying OpenAI...", file=sys.stderr)

    # Fallback to OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("   → Trying OpenAI (GPT)...", file=sys.stderr)
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                max_tokens=150,
                temperature=0.7,
            )

            summary = response.choices[0].message.content.strip()
            print("   ✅ OpenAI (GPT) summary successful", file=sys.stderr)
            return summary[:max_chars]

        except ImportError:
            print("   ❌ OpenAI package not installed", file=sys.stderr)
            return None
        except Exception as e:
            error_msg = str(e)
            if "Incorrect API key" in error_msg or "authentication" in error_msg.lower():
                print(f"   ❌ OpenAI authentication failed (check API key)", file=sys.stderr)
            elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                print(f"   ❌ OpenAI quota/billing issue", file=sys.stderr)
            else:
                print(f"   ❌ OpenAI API error: {e}", file=sys.stderr)
            return None
    else:
        print("   ⓘ OPENAI_API_KEY not set", file=sys.stderr)

    # No API keys available
    print("   ❌ No LLM API keys configured", file=sys.stderr)
    return None


def generate_session_filename(user: str, agent: str = "claude") -> str:
    """Generate a unique session filename."""
    timestamp = int(time.time())
    user_short = user.split()[0].lower() if user else "unknown"
    short_id = uuid.uuid4().hex[:8]
    return f"{timestamp}_{user_short}_{agent}_{short_id}.jsonl"


def get_git_user() -> str:
    """Get git user name."""
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return os.getenv("USER", "unknown")


def copy_session_to_repo(session_file: Path, repo_root: Path, user: str) -> Tuple[Path, str]:
    """
    Copy session file to repository .realign/sessions/ directory.
    Preserves the original filename to track session identity across commits.
    Returns (absolute_path, relative_path).
    """
    sessions_dir = repo_root / ".realign" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Use original filename to maintain session identity
    # This allows the same session to be updated across multiple commits
    original_filename = session_file.name
    dest_path = sessions_dir / original_filename

    # Atomic copy (write to temp then move)
    # If file exists, this will update it with new content
    temp_path = dest_path.with_suffix(".tmp")
    shutil.copy2(session_file, temp_path)
    temp_path.rename(dest_path)

    # Return both absolute and relative paths
    rel_path = dest_path.relative_to(repo_root)
    return dest_path, str(rel_path)


def process_sessions(
    pre_commit_mode: bool = False,
    session_path: Optional[str] = None,
    user: Optional[str] = None
) -> Dict[str, Any]:
    """
    Core logic for processing agent sessions.
    Used by both pre-commit and prepare-commit-msg hooks.

    Args:
        pre_commit_mode: If True, only return session paths without generating summaries
        session_path: Explicit path to a session file (optional)
        user: User name override (optional)

    Returns:
        Dictionary with keys: summary, session_relpaths, redacted
    """
    # Load configuration
    config = ReAlignConfig.load()

    # Find repository root
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        repo_root = Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        print(json.dumps({"error": "Not in a git repository"}), file=sys.stderr)
        sys.exit(1)

    # Find all active session files
    session_path_env = session_path or os.getenv("REALIGN_SESSION_PATH")

    if session_path_env:
        # Explicit session path provided
        session_file = Path(session_path_env)
        session_files = [session_file] if session_file.exists() else []
    else:
        # Auto-detect all enabled sessions
        session_files = find_all_active_sessions(config, repo_root)

    if not session_files:
        # Return empty result (don't block commit)
        return {"summary": "", "session_relpaths": [], "redacted": False}

    # Get user
    user = user or get_git_user()

    # Copy all sessions to repo
    session_relpaths = []
    for session_file in session_files:
        try:
            _, session_relpath = copy_session_to_repo(session_file, repo_root, user)
            session_relpaths.append(session_relpath)
        except Exception as e:
            print(f"Warning: Could not copy session file {session_file}: {e}", file=sys.stderr)
            continue

    if not session_relpaths:
        return {"summary": "", "session_relpaths": [], "redacted": False}

    # If pre-commit mode, just return session paths (summary will be generated later)
    if pre_commit_mode:
        return {
            "summary": "",
            "session_relpaths": session_relpaths,
            "redacted": False,
        }

    # For prepare-commit-msg mode, generate summary from all sessions
    all_summaries = []
    redacted = False

    for session_relpath in session_relpaths:
        # Extract NEW content using git diff
        new_content = get_new_content_from_git_diff(repo_root, session_relpath)

        if not new_content or not new_content.strip():
            continue

        # Generate summary for NEW content only
        summary = None
        if config.use_LLM:
            print("🤖 Attempting to generate LLM summary...", file=sys.stderr)
            summary = generate_summary_with_llm(new_content, config.summary_max_chars)

            if summary:
                print("✅ LLM summary generated successfully", file=sys.stderr)
            else:
                print("⚠️  LLM summary failed - falling back to local summarization", file=sys.stderr)
                print("   Check your API keys: ANTHROPIC_API_KEY or OPENAI_API_KEY", file=sys.stderr)

        if not summary:
            # Fallback to simple summarize
            print("📝 Using local summarization (no LLM)", file=sys.stderr)
            summary = simple_summarize(new_content, config.summary_max_chars)

        # Identify agent type from filename
        agent_name = "Unknown"
        if "rollout-" in session_relpath:
            agent_name = "Codex"
        elif "agent-" in session_relpath or ".jsonl" in session_relpath:
            agent_name = "Claude"

        all_summaries.append(f"[{agent_name}] {summary}")

        # Check for potential secrets in new content (simple pattern matching)
        if config.redact_on_match:
            import re
            patterns = [
                r"api[_-]?key",
                r"password",
                r"secret",
                r"token",
                r"bearer",
            ]
            for pattern in patterns:
                if re.search(pattern, new_content, re.IGNORECASE):
                    print(f"Warning: Potential sensitive data detected in {agent_name} session (pattern: {pattern})", file=sys.stderr)
                    break

    # Combine all summaries
    if all_summaries:
        combined_summary = " | ".join(all_summaries)
    else:
        combined_summary = "No new content in sessions"

    return {
        "summary": combined_summary,
        "session_relpaths": session_relpaths,
        "redacted": redacted,
    }


def pre_commit_hook():
    """
    Entry point for pre-commit hook.
    Finds and stages session files.
    """
    result = process_sessions(pre_commit_mode=True)
    print(json.dumps(result, ensure_ascii=False))

    # Stage the session files
    if result["session_relpaths"]:
        try:
            subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True,
            )
            repo_root_result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True,
            )
            repo_root = repo_root_result.stdout.strip()

            for session_path in result["session_relpaths"]:
                subprocess.run(
                    ["git", "add", session_path],
                    cwd=repo_root,
                    check=True,
                )
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not stage session files: {e}", file=sys.stderr)

    sys.exit(0)


def prepare_commit_msg_hook():
    """
    Entry point for prepare-commit-msg hook.
    Generates session summary and appends to commit message.
    """
    # Get commit message file path from command line arguments
    if len(sys.argv) < 2:
        print("Error: Commit message file path not provided", file=sys.stderr)
        sys.exit(1)

    msg_file = sys.argv[1]

    # Process sessions and generate summary
    result = process_sessions(pre_commit_mode=False)

    # Append summary to commit message
    if result["summary"] and result["session_relpaths"]:
        try:
            with open(msg_file, "a", encoding="utf-8") as f:
                f.write(f"\n\nAgent-Summary: {result['summary']}\n")
                f.write(f"Agent-Session-Paths: {', '.join(result['session_relpaths'])}\n")
                if result["redacted"]:
                    f.write("Agent-Redacted: true\n")
        except Exception as e:
            print(f"Warning: Could not append to commit message: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    # This allows the module to be run directly for testing
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--pre-commit":
            pre_commit_hook()
        elif sys.argv[1] == "--prepare-commit-msg":
            prepare_commit_msg_hook()
        else:
            print("Usage: python -m realign.hooks [--pre-commit|--prepare-commit-msg]")
            sys.exit(1)
    else:
        print("Usage: python -m realign.hooks [--pre-commit|--prepare-commit-msg]")
        sys.exit(1)
