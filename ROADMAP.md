# Roadmap

v0.1 covers the notes parser, keyword search, the `crib` lookup command and
`crib add`. Everything below is planned follow-up work, with rough hour estimates.

Total: **28 h**

## Features (15 h)

- [ ] Fuzzy matching so `crib dckr prune` still finds "docker system prune" (3 h)
- [ ] Tags on entries (`tags: net, debug` line) and `-T TAG` filter (2 h)
- [ ] `crib edit QUERY` opens `$EDITOR` at the matching entry's line (1.5 h)
- [ ] `--copy` puts the top command on the clipboard (wl-copy / xclip / pbcopy) (1.5 h)
- [ ] `{{placeholder}}` fields in commands, prompted for and filled before printing (2.5 h)
- [ ] Interactive picker (curses) to browse results and choose one (3 h)
- [ ] Colour output with highlighted match words, off when not a TTY or `NO_COLOR` set (1.5 h)

## Bugs and edge cases (5 h)

- [x] Files with CRLF line endings and a UTF-8 BOM (1 h)
- [x] Unclosed code fence at the end of a file: warn instead of swallowing the rest (1 h)
- [x] Non-UTF-8 files: skip with a warning naming the file (0.5 h)
- [ ] Duplicate titles in one topic: show both, flag in `--check` (1 h)
- [ ] `crib add` into a file without a trailing newline or with a `~~~` fence style (1.5 h)

## Refactors (3 h)

- [ ] Cache parsed notes keyed by file mtime so large note folders stay fast (2 h)
- [ ] Move output formatting out of `cli.py` into its own module (1 h)

## Tests (3 h)

- [ ] Property-style tests for the parser over generated Markdown (1.5 h)
- [ ] End-to-end tests running the installed `crib` script in a temp notes folder (1.5 h)

## Docs (2 h)

- [ ] Notes format reference with more examples, including nested lists (1 h)
- [ ] Short guide for importing an existing pile of notes (1 h)
