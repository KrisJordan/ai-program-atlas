#!/usr/bin/env python3
"""Serialize owned staging and commit in a shared worktree.

Use --path for owned files and --ledger-row FILE:PROGRAM_ID for a shared
program ledger. Refuse pre-existing staged work instead of committing it.
"""
import argparse
import fcntl
import json
import subprocess
from pathlib import Path


def commit_owned(root, message, paths, ledger_rows):
    def git(*args, input=None):
        return subprocess.run(['git', *args], cwd=root, input=input,
                              text=True, capture_output=True, check=True).stdout
    lock_path = Path(git('rev-parse', '--git-path', 'atlas-commit.lock').strip())
    if not lock_path.is_absolute():
        lock_path = root / lock_path
    with lock_path.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if git('diff', '--cached', '--name-only').strip():
            raise ValueError('Index already contains staged work; inspect it before using this helper')
        grouped = {}
        for value in ledger_rows:
            filename, pid = value.rsplit(':', 1)
            grouped.setdefault(filename, set()).add(pid)
        if set(paths) & set(grouped):
            raise ValueError('A shared ledger must use --ledger-row, not also --path')
        prepared = {}
        for filename, ids in grouped.items():
            before = json.loads(git('show', 'HEAD:'+filename))
            current = json.loads((root / filename).read_text())
            selected = {r['program_id']: r for r in current['programs'] if r['program_id'] in ids}
            if set(selected) != ids or not ids <= {r['program_id'] for r in before['programs']}:
                raise ValueError('Owned ledger row missing or not unique in expected ledger')
            before['programs'] = [selected.get(r['program_id'], r) for r in before['programs']]
            prepared[filename] = json.dumps(before, indent=2, ensure_ascii=False)+'\n'
        for filename, value in prepared.items():
            blob = git('hash-object', '-w', '--stdin', input=value).strip()
            git('update-index', '--cacheinfo', '100644', blob, filename)
        if paths:
            git('add', '--', *paths)
        return git('commit', '-m', message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-m', '--message', required=True)
    parser.add_argument('--path', action='append', default=[])
    parser.add_argument('--ledger-row', action='append', default=[])
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    print(commit_owned(root, args.message, args.path, args.ledger_row), end='')


if __name__ == '__main__':
    main()
