from pathlib import Path

from cmd_crib.notes import load_dir, parse_text

SAMPLE = """\
# Git

Stuff I forget.

## Undo last commit, keep changes
`git reset --soft HEAD~1`

## Show a file at an old commit
Handy for diffing by eye.

```bash
git show REV:path/to/file
```

## Two commands
`git stash`
`git stash pop`
"""


def test_parse_entries_titles_and_lines():
    entries = parse_text(SAMPLE, "git", Path("git.md"))
    assert [e.title for e in entries] == [
        "Undo last commit, keep changes",
        "Show a file at an old commit",
        "Two commands",
    ]
    assert [e.line for e in entries] == [5, 8, 15]
    assert all(e.topic == "git" for e in entries)


def test_inline_and_fenced_commands():
    undo, show, two = parse_text(SAMPLE, "git", Path("git.md"))
    assert undo.commands == ["git reset --soft HEAD~1"]
    assert show.commands == ["git show REV:path/to/file"]
    assert show.notes == "Handy for diffing by eye."
    assert two.commands == ["git stash", "git stash pop"]


def test_text_before_first_heading_is_ignored():
    entries = parse_text("intro `ls`\n`pwd`\n\n## Real\n`ls -la`\n", "sh", Path("sh.md"))
    assert len(entries) == 1
    assert entries[0].commands == ["ls -la"]


def test_heading_inside_fence_is_not_an_entry():
    text = "## Script\n```\n## not a heading\necho hi\n```\n"
    (entry,) = parse_text(text, "sh", Path("sh.md"))
    assert entry.commands == ["## not a heading\necho hi"]


def test_multiline_block_and_trailing_hashes():
    text = "## Loop ##\n```sh\nfor f in *; do\n  echo $f\ndone\n```\n"
    (entry,) = parse_text(text, "sh", Path("sh.md"))
    assert entry.title == "Loop"
    assert entry.commands == ["for f in *; do\n  echo $f\ndone"]


def test_inline_code_inside_sentence_is_a_note():
    text = "## Note\nUse `-r` for folders.\n`cp -r a b`\n"
    (entry,) = parse_text(text, "sh", Path("sh.md"))
    assert entry.commands == ["cp -r a b"]
    assert entry.notes == "Use `-r` for folders."


def test_unclosed_fence_keeps_rest_as_command():
    text = "## Open\n```\necho one\necho two\n"
    (entry,) = parse_text(text, "sh", Path("sh.md"))
    assert entry.commands == ["echo one\necho two"]


def test_load_dir_uses_file_stem_as_topic(tmp_path):
    (tmp_path / "tar.md").write_text("## Extract\n`tar xf a.tar`\n", encoding="utf-8")
    (tmp_path / "git.md").write_text("## Status\n`git status`\n", encoding="utf-8")
    (tmp_path / "readme.txt").write_text("## Not notes\n`nope`\n", encoding="utf-8")
    entries = load_dir(tmp_path)
    assert [(e.topic, e.title) for e in entries] == [("git", "Status"), ("tar", "Extract")]
    assert entries[0].path == tmp_path / "git.md"
