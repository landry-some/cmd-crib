# git

## Undo last commit, keep changes
`git reset --soft HEAD~1`

## Show a file as it was at an old commit
```bash
git show abc1234:src/main.py
```

## Find which commit removed a line
Searches every diff for the string.
`git log -S "old_function_name" --oneline`

## Clean untracked files (dry run first)
`git clean -nd`
`git clean -fd`
