import pytest

from cmd_crib.cli import default_notes_dir, main


@pytest.fixture
def notes(tmp_path):
    (tmp_path / "tar.md").write_text(
        "# tar\n\n"
        "## Extract an archive\n`tar xf archive.tar`\n\n"
        "## Create a gzip archive\nAdd -v to list files.\n`tar czf out.tgz dir/`\n",
        encoding="utf-8",
    )
    (tmp_path / "git.md").write_text(
        "## Undo last commit\n```\ngit reset --soft HEAD~1\n```\n\n## No command here\nJust text.\n",
        encoding="utf-8",
    )
    return tmp_path


def run(capsys, *argv):
    code = main(list(argv))
    out, err = capsys.readouterr()
    return code, out, err


def test_lookup_prints_numbered_results(notes, capsys):
    code, out, _ = run(capsys, "--dir", str(notes), "archive")
    assert code == 0
    assert out.splitlines() == [
        "1. tar / Extract an archive  (tar.md:3)",
        "     tar xf archive.tar",
        "",
        "2. tar / Create a gzip archive  (tar.md:6)",
        "     tar czf out.tgz dir/",
        "     # Add -v to list files.",
    ]


def test_command_flag_prints_bare_command(notes, capsys):
    code, out, _ = run(capsys, "--dir", str(notes), "-c", "undo")
    assert code == 0
    assert out == "git reset --soft HEAD~1\n"


def test_command_flag_with_entry_without_command(notes, capsys):
    code, _, err = run(capsys, "--dir", str(notes), "-c", "no", "command")
    assert code == 1
    assert "has no command" in err


def test_no_matches_exits_1(notes, capsys):
    code, out, err = run(capsys, "--dir", str(notes), "zzz")
    assert code == 1
    assert out == ""
    assert "no matches" in err


def test_topic_filter_and_limit(notes, capsys):
    code, out, _ = run(capsys, "--dir", str(notes), "-t", "tar", "-n", "1")
    assert code == 0
    assert "Extract an archive" in out
    assert "Create a gzip" not in out
    assert "1 more, use -n 0" in out


def test_topics_lists_counts(notes, capsys):
    code, out, _ = run(capsys, "--dir", str(notes), "--topics")
    assert code == 0
    assert out.splitlines() == ["git  2", "tar  2"]


def test_missing_notes_dir(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--dir", str(tmp_path / "nope"), "x"])
    assert "notes folder not found" in str(exc.value.code)


def test_crib_dir_env_is_used(notes, capsys, monkeypatch):
    monkeypatch.setenv("CRIB_DIR", str(notes))
    code, out, _ = run(capsys, "-c", "extract")
    assert code == 0
    assert out == "tar xf archive.tar\n"


def test_default_dir_uses_xdg_config(monkeypatch, tmp_path):
    monkeypatch.delenv("CRIB_DIR", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    assert default_notes_dir() == tmp_path / "crib" / "notes"


def test_lookup_still_works_next_to_non_utf8_file(notes, capsys):
    (notes / "old.md").write_bytes(b"## Extract\n\xff\n")
    code, out, err = run(capsys, "--dir", str(notes), "-c", "extract")
    assert code == 0
    assert out == "tar xf archive.tar\n"
    assert "skipping" in err and "old.md" in err


def test_tag_flag_filters_and_tags_are_shown(tmp_path, capsys):
    (tmp_path / "sh.md").write_text(
        "## Open ports\ntags: net, debug\n`ss -tlnp`\n\n## Disk usage\n`du -sh`\n",
        encoding="utf-8",
    )
    code, out, _ = run(capsys, "--dir", str(tmp_path), "-T", "net")
    assert code == 0
    assert out.splitlines() == ["1. sh / Open ports  (sh.md:1)  [net, debug]", "     ss -tlnp"]
    code, _, err = run(capsys, "--dir", str(tmp_path), "-T", "net", "disk")
    assert code == 1
    assert "no matches" in err
