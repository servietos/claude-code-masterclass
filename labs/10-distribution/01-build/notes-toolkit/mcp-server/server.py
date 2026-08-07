"""Notes toolkit MCP server: counts TODO/FIXME/NOTE markers in a project."""

import os
import re
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("notes-mcp")

MARKERS = ("TODO", "FIXME", "NOTE")
MARKER_RE = re.compile(r"\b(TODO|FIXME|NOTE)\b")
SKIP_DIRS = {".git", ".claude", "node_modules", ".venv", "__pycache__", ".notes", "dist", "build"}
TEXT_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".c", ".h", ".sh", ".rb", ".md"}


def _project_root() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


@mcp.tool()
def count_todos(path: str = "") -> dict:
    """Count TODO, FIXME and NOTE comments in the project and return the totals per marker."""
    root = Path(path) if path else _project_root()
    counts = {marker: 0 for marker in MARKERS}
    files_scanned = 0

    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            candidate = Path(current) / name
            if candidate.suffix not in TEXT_SUFFIXES:
                continue
            files_scanned += 1
            for line in candidate.read_text(encoding="utf-8", errors="replace").splitlines():
                match = MARKER_RE.search(line)
                if match:
                    counts[match.group(1)] += 1

    return {
        "root": str(root),
        "files_scanned": files_scanned,
        "counts": counts,
        "total": sum(counts.values()),
    }


if __name__ == "__main__":
    # stdout carries the MCP protocol on stdio transport, so every log line goes to stderr
    print(f"notes-mcp server starting on stdio, root {_project_root()}", file=sys.stderr, flush=True)
    mcp.run(transport="stdio")
    print("notes-mcp server stopped", file=sys.stderr, flush=True)
