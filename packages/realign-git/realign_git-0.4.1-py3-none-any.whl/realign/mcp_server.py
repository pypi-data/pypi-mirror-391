#!/usr/bin/env python3
"""ReAlign MCP Server - Expose ReAlign functionality via Model Context Protocol."""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import ReAlignConfig
from .commands import init, search, show


# Initialize MCP server
app = Server("realign")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available ReAlign tools."""
    return [
        Tool(
            name="realign_init",
            description=(
                "Initialize ReAlign in a directory to enable AI conversation tracking with git commits. "
                "This command AUTOMATICALLY initializes a git repository if one doesn't exist yet, "
                "then sets up git hooks and configures session tracking. "
                "IMPORTANT: Use this instead of 'git init' when you want to track AI conversations. "
                "It will handle both git initialization AND ReAlign setup in one step."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to directory to initialize (default: current directory)",
                    },
                },
            },
        ),
        Tool(
            name="realign_search",
            description=(
                "Search through git commits and AI agent chat sessions. "
                "Finds commits with matching keywords in commit messages or session content. "
                "Returns commit hashes, messages, dates, and optionally session content. "
                "Can search in commits only, sessions only, or both (default)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Keyword to search for in commits and sessions",
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository (default: current directory)",
                    },
                    "show_session": {
                        "type": "boolean",
                        "description": "Include full session content in results",
                        "default": False,
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 20,
                    },
                    "session_only": {
                        "type": "boolean",
                        "description": "Search only in session files, not commits. Useful for finding topics discussed in historical conversations.",
                        "default": False,
                    },
                    "commits_only": {
                        "type": "boolean",
                        "description": "Search only in commits, not session files. Useful for quick commit message searches.",
                        "default": False,
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="realign_show",
            description=(
                "Display the AI agent chat session associated with a specific git commit. "
                "Shows the full conversation that led to the code changes in that commit. "
                "Use this to understand the context and reasoning behind code changes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "commit_hash": {
                        "type": "string",
                        "description": "Git commit hash (full or short)",
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository (default: current directory)",
                    },
                    "session_path": {
                        "type": "string",
                        "description": "Direct path to session file (alternative to commit_hash)",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["pretty", "json", "raw"],
                        "description": "Output format",
                        "default": "pretty",
                    },
                },
            },
        ),
        Tool(
            name="realign_get_latest_session",
            description=(
                "Get the path to the most recent AI agent chat session. "
                "Automatically detects Claude Code sessions or uses configured history path. "
                "Useful for retrieving the current conversation context."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to git repository (for Claude auto-detection)",
                    },
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution."""

    try:
        if name == "realign_init":
            return await handle_init(arguments)
        elif name == "realign_search":
            return await handle_search(arguments)
        elif name == "realign_show":
            return await handle_show(arguments)
        elif name == "realign_get_latest_session":
            return await handle_get_latest_session(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_init(args: dict) -> list[TextContent]:
    """Handle realign_init tool."""
    repo_path = args.get("repo_path", ".")

    # In MCP context, always use --yes to avoid interactive prompts
    # This ensures git repo initialization happens automatically
    cmd = ["realign", "init", "--yes"]

    # Run command
    result = subprocess.run(
        cmd,
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    if result.returncode == 0:
        return [TextContent(
            type="text",
            text=f"✅ ReAlign initialized successfully\n\n{output}"
        )]
    else:
        return [TextContent(
            type="text",
            text=f"❌ Failed to initialize ReAlign\n\n{output}"
        )]


async def handle_search(args: dict) -> list[TextContent]:
    """Handle realign_search tool."""
    keyword = args["keyword"]
    repo_path = args.get("repo_path", ".")
    show_session = args.get("show_session", False)
    max_results = args.get("max_results", 20)
    session_only = args.get("session_only", False)
    commits_only = args.get("commits_only", False)

    # Build command
    cmd = ["realign", "search", keyword, "--max", str(max_results)]
    if show_session:
        cmd.append("--show-session")
    if session_only:
        cmd.append("--session-only")
    if commits_only:
        cmd.append("--commits-only")

    # Run command
    result = subprocess.run(
        cmd,
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    output = result.stdout
    if result.returncode == 0:
        return [TextContent(type="text", text=output or "No results found")]
    else:
        return [TextContent(
            type="text",
            text=f"Error searching: {result.stderr}"
        )]


async def handle_show(args: dict) -> list[TextContent]:
    """Handle realign_show tool."""
    commit_hash = args.get("commit_hash")
    repo_path = args.get("repo_path", ".")
    session_path = args.get("session_path")
    format_type = args.get("format", "pretty")

    # Build command
    cmd = ["realign", "show"]
    if session_path:
        cmd.extend(["--session", session_path])
    elif commit_hash:
        cmd.append(commit_hash)
    else:
        return [TextContent(
            type="text",
            text="Error: Must provide either commit_hash or session_path"
        )]

    cmd.extend(["--format", format_type])

    # Run command
    result = subprocess.run(
        cmd,
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return [TextContent(type="text", text=result.stdout)]
    else:
        return [TextContent(
            type="text",
            text=f"Error showing session: {result.stderr}"
        )]


async def handle_get_latest_session(args: dict) -> list[TextContent]:
    """Handle realign_get_latest_session tool."""
    from .claude_detector import find_claude_sessions_dir

    repo_path = args.get("repo_path", ".")
    config = ReAlignConfig.load()

    # Try Claude auto-detection first
    if config.auto_detect_claude:
        claude_dir = find_claude_sessions_dir(Path(repo_path))
        if claude_dir:
            # Find latest session in Claude directory
            session_files = sorted(
                claude_dir.glob("*.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if session_files:
                return [TextContent(
                    type="text",
                    text=f"Latest Claude Code session: {session_files[0]}"
                )]

    # Fallback to configured history path
    history_path = config.expanded_local_history_path

    if not history_path.exists():
        return [TextContent(
            type="text",
            text=f"No sessions found. History path does not exist: {history_path}"
        )]

    # Find latest session file
    session_files = sorted(
        history_path.glob("*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if session_files:
        return [TextContent(
            type="text",
            text=f"Latest session: {session_files[0]}"
        )]
    else:
        return [TextContent(
            type="text",
            text=f"No session files found in {history_path}"
        )]


async def async_main():
    """Run the MCP server (async)."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Entry point for the MCP server command."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
