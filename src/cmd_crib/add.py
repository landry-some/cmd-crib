"""Append a new entry to a topic file."""

from __future__ import annotations

import re
from pathlib import Path

TOPIC_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def render_entry(title: str, command: str, note: str | None = None) -> str:
    """Markdown for one entry, in the same shape the parser reads back."""
    lines = [f"## {title}"]
    if note:
        lines.append(note)
    if "`" in command or "\n" in command:
        lines += ["```", command, "```"]
    else:
        lines.append(f"`{command}`")
    return "\n".join(lines) + "\n"


def add_entry(notes_dir: Path, topic: str, title: str, command: str,
              note: str | None = None) -> tuple[Path, int]:
    """Append an entry to ``<notes_dir>/<topic>.md`` and return (path, heading line).

    The folder and file are created if needed. A new file starts with ``# topic``.
    A file with CRLF line endings keeps them.
    """
    if not TOPIC_NAME.match(topic) or topic.endswith(".md"):
        raise ValueError(f"topic must be a plain name like 'git' or 'docker', got {topic!r}")
    title = title.strip()
    if not title or "\n" in title:
        raise ValueError("title must be a single non-empty line")
    command = command.strip()
    if not command:
        raise ValueError("command must not be empty")
    if note is not None:
        note = " ".join(note.split()) or None

    notes_dir.mkdir(parents=True, exist_ok=True)
    path = notes_dir / f"{topic}.md"
    existing = path.read_text(encoding="utf-8", newline="") if path.exists() else f"# {topic}\n"
    newline = "\r\n" if "\r\n" in existing else "\n"
    existing = existing.replace("\r\n", "\n")

    prefix = existing
    if prefix and not prefix.endswith("\n"):
        prefix += "\n"
    if prefix.strip():
        prefix += "\n"
    heading_line = prefix.count("\n") + 1

    path.write_text(prefix + render_entry(title, command, note), encoding="utf-8",
                    newline=newline)
    return path, heading_line
