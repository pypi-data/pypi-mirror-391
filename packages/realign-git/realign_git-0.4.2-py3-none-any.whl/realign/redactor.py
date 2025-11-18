"""
Redactor module for detecting and redacting sensitive information in sessions.

This module uses detect-secrets to identify potential secrets and provides
functionality to redact them from session files.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class SecretMatch:
    """Represents a detected secret."""

    def __init__(self, secret_type: str, line_number: int, secret_hash: str):
        self.type = secret_type
        self.line = line_number
        self.hash = secret_hash

    def __repr__(self):
        return f"SecretMatch(type={self.type}, line={self.line})"


def detect_secrets(content: str) -> Tuple[List[SecretMatch], bool]:
    """
    Detect secrets in the given content using detect-secrets library.

    Args:
        content: The text content to scan for secrets

    Returns:
        Tuple of (list of SecretMatch objects, whether detect-secrets is available)
    """
    try:
        from detect_secrets import SecretsCollection
        from detect_secrets.settings import default_settings
    except ImportError:
        # detect-secrets not installed, fall back to basic pattern matching
        return [], False

    if not content or not content.strip():
        return [], True

    secrets = []

    # Create a temporary file for scanning
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.jsonl',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(content)
            temp_path = f.name

        # Scan the file
        collection = SecretsCollection()
        with default_settings():
            collection.scan_file(temp_path)

        # Extract detected secrets
        for filename, secret_list in collection.data.items():
            for secret in secret_list:
                secrets.append(
                    SecretMatch(
                        secret_type=secret.type,
                        line_number=secret.line_number,
                        secret_hash=secret.secret_hash
                    )
                )

    except Exception as e:
        print(f"Warning: Error during secret detection: {e}", file=sys.stderr)
    finally:
        # Clean up temp file
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except Exception:
            pass

    return secrets, True


def redact_content(content: str, secrets: List[SecretMatch]) -> str:
    """
    Redact detected secrets from content.

    Args:
        content: Original content
        secrets: List of detected secrets

    Returns:
        Content with secrets redacted
    """
    if not secrets:
        return content

    lines = content.split('\n')

    # Group secrets by line number
    secrets_by_line = {}
    for secret in secrets:
        line_num = secret.line - 1  # Convert to 0-indexed
        if 0 <= line_num < len(lines):
            if line_num not in secrets_by_line:
                secrets_by_line[line_num] = []
            secrets_by_line[line_num].append(secret)

    # Redact secrets (simple approach: replace entire line with redaction notice)
    for line_num, line_secrets in secrets_by_line.items():
        secret_types = [s.type for s in line_secrets]
        # Keep the JSON structure but redact the sensitive value
        # This is a simple approach - we mark the line as redacted
        original_line = lines[line_num]
        # Try to preserve JSON structure by finding quotes and redacting content
        if '"' in original_line:
            # Simple redaction: find the value part and replace it
            lines[line_num] = original_line.replace(
                original_line[original_line.find(':'):] if ':' in original_line else original_line,
                f': "[REDACTED: {", ".join(set(secret_types))}]"'
            )
        else:
            lines[line_num] = f"[REDACTED LINE - {', '.join(set(secret_types))}]"

    return '\n'.join(lines)


def check_and_redact_session(
    session_content: str,
    redact_mode: str = "auto"
) -> Tuple[str, bool, List[SecretMatch]]:
    """
    Check session content for secrets and optionally redact them.

    Args:
        session_content: The session content to check
        redact_mode: Redaction mode - "auto" (redact if found), "detect" (only detect), "off"

    Returns:
        Tuple of (potentially redacted content, whether secrets were found, list of secrets)
    """
    if redact_mode == "off":
        return session_content, False, []

    # Detect secrets
    secrets, detect_secrets_available = detect_secrets(session_content)

    if not secrets:
        return session_content, False, []

    # Print warning about detected secrets
    print(
        f"⚠️  Detected {len(secrets)} potential secret(s) in session:",
        file=sys.stderr
    )
    for secret in secrets:
        print(f"   - {secret.type} at line {secret.line}", file=sys.stderr)

    if redact_mode == "detect":
        # Only detect, don't redact
        return session_content, True, secrets

    # Auto mode: redact the secrets
    redacted_content = redact_content(session_content, secrets)
    print("   ✅ Secrets have been automatically redacted", file=sys.stderr)

    return redacted_content, True, secrets


def save_original_session(
    session_path: Path,
    repo_root: Path
) -> Optional[Path]:
    """
    Save a copy of the original session before redaction.

    Args:
        session_path: Path to the session file in .realign/sessions/
        repo_root: Repository root path

    Returns:
        Path to the backup file, or None if backup failed
    """
    try:
        backup_dir = repo_root / ".realign" / "sessions-original"
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = backup_dir / session_path.name

        # Copy original file to backup
        import shutil
        shutil.copy2(session_path, backup_path)

        return backup_path
    except Exception as e:
        print(f"Warning: Could not backup original session: {e}", file=sys.stderr)
        return None
