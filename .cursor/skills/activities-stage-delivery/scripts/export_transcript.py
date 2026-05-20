#!/usr/bin/env python3
"""Export Cursor agent transcript (jsonl) to Markdown."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def find_project_transcript_dir(repo_root: Path) -> Path | None:
    """Resolve Cursor agent-transcripts folder for this workspace."""
    env_dir = os.environ.get("CURSOR_AGENT_TRANSCRIPTS_DIR")
    if env_dir:
        p = Path(env_dir)
        if p.is_dir():
            return p

    home = Path.home()
    projects = home / ".cursor" / "projects"
    if not projects.is_dir():
        return None

    repo = repo_root.resolve()
    candidates: list[tuple[float, Path]] = []
    for child in projects.iterdir():
        if not child.is_dir():
            continue
        transcripts = child / "agent-transcripts"
        if not transcripts.is_dir():
            continue
        for jsonl in transcripts.rglob("*.jsonl"):
            try:
                if repo in jsonl.resolve().parents:
                    pass
            except OSError:
                continue
            candidates.append((jsonl.stat().st_mtime, jsonl))

    if not candidates:
        for child in projects.iterdir():
            transcripts = child / "agent-transcripts"
            if not transcripts.is_dir():
                continue
            for jsonl in transcripts.rglob("*.jsonl"):
                candidates.append((jsonl.stat().st_mtime, jsonl))

    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def pick_transcript(repo_root: Path, explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            raise FileNotFoundError(f"Transcript not found: {p}")
        return p

    found = find_project_transcript_dir(repo_root)
    if found is None:
        raise FileNotFoundError(
            "No agent transcript jsonl found. Pass --transcript or set "
            "CURSOR_AGENT_TRANSCRIPTS_DIR to the session's .jsonl file."
        )
    return found


def _strip_user_query(text: str) -> str:
    text = re.sub(r"^<user_query>\s*", "", text.strip())
    text = re.sub(r"\s*</user_query>\s*$", "", text)
    return text.strip()


def _content_blocks(message: dict[str, Any]) -> Iterable[tuple[str, str]]:
    for block in message.get("content", []):
        btype = block.get("type")
        if btype == "text":
            yield "text", block.get("text", "")
        elif btype == "tool_use":
            name = block.get("name", "tool")
            inp = block.get("input", {})
            yield "tool", f"**{name}**\n```json\n{json.dumps(inp, ensure_ascii=False, indent=2)}\n```"


def jsonl_to_markdown(
    jsonl_path: Path,
    stage: int,
    stage_title: str,
    base_name: str,
) -> str:
    lines: list[str] = [
        f"# Stage {stage:02d} — Conversation Transcript",
        "",
        f"- **Activity**: {stage_title}",
        f"- **Source**: `{jsonl_path.name}`",
        f"- **Exported**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"- **Pair report**: `Report/{base_name}.md`",
        "",
        "---",
        "",
    ]

    turn = 0
    with jsonl_path.open(encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError:
                continue

            role = row.get("role", "unknown")
            message = row.get("message") or {}
            parts: list[str] = []

            for kind, body in _content_blocks(message):
                if kind == "text" and body:
                    if role == "user":
                        body = _strip_user_query(body)
                    if body and body != "[REDACTED]":
                        parts.append(body)
                elif kind == "tool":
                    parts.append(body)

            if not parts:
                continue

            turn += 1
            heading = "User" if role == "user" else "Assistant" if role == "assistant" else role.title()
            lines.append(f"## Turn {turn} — {heading}")
            lines.append("")
            lines.append("\n\n".join(parts))
            lines.append("")
            lines.append("---")
            lines.append("")

    if turn == 0:
        lines.append("_No exportable messages in transcript (content may be redacted)._")
        lines.append("")

    lines.append(
        "> Export via `activities-stage-delivery` skill. "
        "For a fuller log, use Cursor **Export Transcript** and replace this file."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export agent transcript jsonl to Markdown.")
    parser.add_argument("--stage", type=int, required=True, choices=range(1, 7))
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--transcript", type=str, default=None)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stage-title", type=str, required=True)
    parser.add_argument("--base-name", type=str, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    jsonl_path = pick_transcript(repo_root, args.transcript)
    md = jsonl_to_markdown(jsonl_path, args.stage, args.stage_title, args.base_name)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(md, encoding="utf-8")
    print(f"Wrote transcript: {args.output}")
    print(f"Source jsonl: {jsonl_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
