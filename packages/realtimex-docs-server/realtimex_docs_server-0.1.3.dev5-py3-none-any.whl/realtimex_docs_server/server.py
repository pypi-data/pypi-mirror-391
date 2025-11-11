"""RealTimeX Local Documentation MCP server."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from fastmcp import FastMCP
from pydantic import Field

DOCS_ENV_VAR = "REALTIMEX_DOCS_ROOT"
DEFAULT_DOCS_PATH = Path(__file__).resolve().parent / "docs"

mcp = FastMCP("RealTimeX Local Documentation Server")

_docs_root: Optional[Path] = None


def _set_docs_root(path: Path) -> None:
    global _docs_root
    _docs_root = path


def _require_docs_root() -> Path:
    if _docs_root is None:
        raise RuntimeError("Documentation root not configured.")
    return _docs_root


def _is_hidden(relative_path: Path) -> bool:
    return any(part.startswith(".") for part in relative_path.parts)


@mcp.tool(
    description="List documentation files inside the configured documentation directory."
)
def list_documents() -> Dict[str, object]:
    """List documentation files under the configured root."""
    root = _require_docs_root()
    files: List[str] = []
    for candidate in root.rglob("*"):
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(root)
        if _is_hidden(relative):
            continue
        files.append(relative.as_posix())
    sorted_files = sorted(files)
    return {
        "status": "success",
        "count": len(sorted_files),
        "files": sorted_files,
    }


@mcp.tool(description="Read UTF-8 documentation content with optional line windowing.")
def read_document(
    path: str = Field(
        description="Relative path to the document inside the documentation root."
    ),
    offset: int = Field(
        default=0, ge=0, description="Zero-based line offset to start reading from."
    ),
    limit: int = Field(
        default=2000, ge=1, le=5000, description="Maximum number of lines to return."
    ),
) -> Dict[str, object]:
    """Read a document from the configured documentation directory."""
    root = _require_docs_root()
    if not path or not path.strip():
        return {"status": "error", "message": "Parameter 'path' must not be empty."}

    target = (root / path).expanduser()
    try:
        target = target.resolve(strict=True)
    except FileNotFoundError:
        return {"status": "error", "message": f"Document '{path}' not found."}
    except OSError as exc:
        return {"status": "error", "message": f"Failed to resolve '{path}': {exc}"}

    try:
        target.relative_to(root)
    except ValueError:
        return {
            "status": "error",
            "message": "Access outside documentation root is not permitted.",
        }

    if not target.is_file():
        return {"status": "error", "message": f"Document '{path}' is not a file."}

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return {
            "status": "error",
            "message": f"Failed to decode '{path}' as UTF-8: {exc}",
        }
    except OSError as exc:
        return {"status": "error", "message": f"Failed to read '{path}': {exc}"}

    lines = content.splitlines(keepends=True)
    if lines and offset >= len(lines):
        return {
            "status": "error",
            "message": f"Line offset {offset} exceeds document length ({len(lines)} lines).",
        }

    window = lines[offset : offset + limit] if lines else []

    return {
        "status": "success",
        "content": "".join(window),
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="realtimex-docs-server",
        description="Expose local documentation through an MCP server using FastMCP.",
    )
    parser.add_argument(
        "--docs-path",
        help=f"Path to the documentation directory. Overrides ${DOCS_ENV_VAR} if provided.",
    )
    return parser.parse_args(argv)


def resolve_docs_root(args: argparse.Namespace) -> Path:
    explicit = args.docs_path
    fallback = os.getenv(DOCS_ENV_VAR)
    raw = explicit or fallback
    if raw:
        root = Path(raw).expanduser()
        if not root.exists():
            raise RuntimeError(f"Documentation path '{root}' does not exist.")
        if not root.is_dir():
            raise RuntimeError(f"Documentation path '{root}' is not a directory.")
        return root.resolve()

    if DEFAULT_DOCS_PATH.exists():
        return DEFAULT_DOCS_PATH

    raise RuntimeError(
        "Documentation path not provided and no bundled docs directory was found. "
        f"Provide --docs-path or set {DOCS_ENV_VAR}."
    )


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    try:
        docs_root = resolve_docs_root(args)
    except RuntimeError as exc:
        sys.stderr.write(f"realtimex-docs-server: {exc}\n")
        raise SystemExit(2) from exc

    _set_docs_root(docs_root)
    mcp.run()
