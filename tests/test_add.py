import pytest

from cmd_crib.add import add_entry, render_entry
from cmd_crib.cli import main
from cmd_crib.notes import load_dir


def test_new_topic_file_gets_header(tmp_path):
    path, line = add_entry(tmp_path / "notes", "docker", "Remove stopped containers",
                           "docker container prune")
    assert path == tmp_path / "notes" / "docker.md"
    assert path.read_text(encoding="utf-8") == (
        "# docker\n\n## Remove stopped containers\n`docker container prune`\n"
    )
    assert line == 3


def test_append_to_existing_file_without_trailing_newline(tmp_path):
    (tmp_path / "git.md").write_text("## Status\n`git status`", encoding="utf-8")
    path, line = add_entry(tmp_path, "git", "Short log", "git log --oneline")
    assert path.read_text(encoding="utf-8") == (
        "## Status\n`git status`\n\n## Short log\n`git log --oneline`\n"
    )
    assert line == 4


def test_added_entry_round_trips_through_parser(tmp_path):
    add_entry(tmp_path, "git", "Status", "git status")
    _, line = add_entry(tmp_path, "git", "Find removed line", 'git log -S "x`y" --oneline',
                        note="searches   every diff")
    entries = load_dir(tmp_path)
    assert [(e.title, e.commands, e.notes) for e in entries] == [
        ("Status", ["git status"], ""),
        ("Find removed line", ['git log -S "x`y" --oneline'], "searches every diff"),
    ]
    assert entries[1].line == line == 6


def test_backtick_command_uses_fence():
    assert render_entry("T", "echo `date`") == "## T\n```\necho `date`\n```\n"


@pytest.mark.parametrize("topic", ["../evil", "a/b", "", ".hidden", "git.md"])
def test_bad_topic_names_rejected(tmp_path, topic):
    with pytest.raises(ValueError):
        add_entry(tmp_path, topic, "Title", "cmd")


def test_empty_title_or_command_rejected(tmp_path):
    with pytest.raises(ValueError):
        add_entry(tmp_path, "git", "  ", "cmd")
    with pytest.raises(ValueError):
        add_entry(tmp_path, "git", "Title", "   ")


def test_cli_add_then_lookup(tmp_path, capsys):
    code = main(["add", "--dir", str(tmp_path), "-m", "careful", "git", "Hard reset",
                 "--", "git", "reset", "--hard", "HEAD"])
    out, _ = capsys.readouterr()
    assert code == 0
    assert out == f"added to {tmp_path / 'git.md'}:3\n"

    assert main(["--dir", str(tmp_path), "-c", "hard", "reset"]) == 0
    out, _ = capsys.readouterr()
    assert out == "git reset --hard HEAD\n"


def test_cli_add_bad_topic_exits_2(tmp_path, capsys):
    assert main(["add", "--dir", str(tmp_path), "../x", "Title", "cmd"]) == 2
    assert "topic must be" in capsys.readouterr().err


def test_append_to_crlf_file_with_bom_keeps_crlf(tmp_path):
    path = tmp_path / "win.md"
    path.write_bytes(b"\xef\xbb\xbf## Status\r\n`git status`\r\n")
    _, line = add_entry(tmp_path, "win", "Short log", "git log --oneline")
    assert path.read_bytes() == (
        b"\xef\xbb\xbf## Status\r\n`git status`\r\n\r\n## Short log\r\n`git log --oneline`\r\n"
    )
    assert line == 4
    assert [e.title for e in load_dir(tmp_path)] == ["Status", "Short log"]
