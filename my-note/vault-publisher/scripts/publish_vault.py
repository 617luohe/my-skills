#!/usr/bin/env python3
"""Deterministic Git publish for the fixed vault.

Only stages the paths this pipeline owns; never runs `git add .`, never
creates empty commits, never auto-resolves conflicts, and never rolls back a
successful local commit when push fails.

A structural quality gate runs before remote sync: frontmatter/broken-link
violations in the owned paths block the publish (exit 5) unless
``--allow-issues`` explicitly overrides it. Orphan/duplicate/index findings are
reported but never block.

Exit codes:
    0  published (or nothing to commit)
    2  precondition failed (invalid vault / unowned changes present)
    3  merge conflict (stopped)
    4  push failed (local commit kept)
    5  quality gate failed (structural violations in owned paths)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import vault_check  # same-directory module (stdlib-only, zero subprocess cost)

EXIT_OK = 0
EXIT_PRECONDITION = 2
EXIT_CONFLICT = 3
EXIT_PUSH_FAILED = 4
EXIT_QUALITY = 5


def die(msg: str, code: int) -> None:
    sys.stderr.write(f"publish_vault: {msg}\n")
    raise SystemExit(code)


def run_git(vault: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    return subprocess.run(
        ["git", "-C", str(vault), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


def _norm(vault: Path, p: str) -> str:
    full = Path(p) if Path(p).is_absolute() else Path(vault) / p
    return os.path.normcase(str(full.resolve()))


def _rev(vault: Path, *ref: str) -> str | None:
    r = run_git(vault, "rev-parse", "--verify", *ref)
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def validate_vault(vault: Path) -> None:
    if not vault.is_dir():
        die(f"vault not found: {vault}", EXIT_PRECONDITION)
    if not (vault / ".obsidian").is_dir():
        die(f"not an obsidian vault (missing .obsidian): {vault}", EXIT_PRECONDITION)
    r = run_git(vault, "rev-parse", "--is-inside-work-tree")
    if r.returncode != 0 or r.stdout.strip() != "true":
        die(f"not a git repository: {vault}", EXIT_PRECONDITION)


def require_clean_worktree(vault: Path, owned_paths: list[str]) -> None:
    owned_abs = {_norm(vault, p) for p in owned_paths}
    # core.quotepath=false: porcelain must emit raw UTF-8 paths, not C-escaped
    # ones ("\xe5..." octal sequences), or Chinese paths fail owned-path matching.
    r = run_git(
        vault,
        "-c",
        "core.quotepath=false",
        "status",
        "--porcelain",
        "--untracked-files=all",
    )
    if r.returncode != 0:
        die("git status failed", EXIT_PRECONDITION)
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        path_part = line[3:].strip().strip('"')
        if " -> " in path_part:
            path_part = path_part.split(" -> ", 1)[1].strip('"')
        if _norm(vault, path_part) not in owned_abs:
            die(f"unowned changes present, stopping: {line.strip()}", EXIT_PRECONDITION)


def _vault_rel(vault: Path, p: str) -> str:
    """Normalize an owned path to a vault-relative forward-slash path."""
    full = Path(p) if Path(p).is_absolute() else Path(vault) / p
    return os.path.relpath(str(full.resolve()), str(vault.resolve())).replace("\\", "/")


def _structural_findings(vault: Path, owned_paths: list[str]) -> list[str]:
    """Run vault_check on the owned paths and return structural violations.

    Structural = frontmatter enum/format violations + missing required fields
    + broken links. A file with no frontmatter block at all is reported but
    never blocks the gate (it carries no owned-structure to violate).
    """
    if not owned_paths:
        return []
    paths_filter = {_vault_rel(vault, p) for p in owned_paths}
    findings = vault_check.run_checks(vault, paths_filter=paths_filter)
    structural = [
        f for f in findings.frontmatter if vault_check.is_structural_finding(f)
    ]
    return structural + findings.broken_links


def quality_gate(vault: Path, owned_paths: list[str]) -> None:
    """Block publish when owned paths carry frontmatter/broken-link violations."""
    structural = _structural_findings(vault, owned_paths)
    if not structural:
        return
    sys.stderr.write("publish_vault: quality gate failed (structural violations):\n")
    for item in structural:
        sys.stderr.write(f"  {item}\n")
    die(
        "owned paths have frontmatter/broken-link violations; "
        "use --allow-issues to override",
        EXIT_QUALITY,
    )


def warn_quality_issues(vault: Path, owned_paths: list[str]) -> None:
    """--allow-issues escape hatch: report what the gate would have blocked."""
    structural = _structural_findings(vault, owned_paths)
    if structural:
        sys.stderr.write(
            f"publish_vault: warning: --allow-issues bypassed quality gate "
            f"({len(structural)} structural finding(s) in owned paths)\n"
        )


def sync_remote(vault: Path) -> None:
    fetch = run_git(vault, "fetch", "origin")
    if fetch.returncode != 0:
        sys.stderr.write("publish_vault: warning: fetch failed, skipping remote sync\n")
        return
    origin = _rev(vault, "origin/master")
    head = _rev(vault, "HEAD")
    if origin is None or origin == head:
        return
    base = run_git(vault, "merge-base", "HEAD", "origin/master")
    if base.returncode != 0:
        return
    base = base.stdout.strip()
    if base == origin:
        # Local is ahead: retry the pending push first.
        push = run_git(vault, "push")
        if push.returncode != 0:
            sys.stderr.write(push.stdout + push.stderr)
            die("push failed; pending commits kept locally", EXIT_PUSH_FAILED)
        return
    merge = run_git(vault, "merge", "origin/master", "--no-edit")
    if merge.returncode != 0:
        sys.stderr.write(merge.stdout + merge.stderr)
        die("merge conflict; stopped without auto-resolving", EXIT_CONFLICT)
    # Merge produced a local commit; sync it upstream so it is never left unpushed.
    push = run_git(vault, "push")
    if push.returncode != 0:
        sys.stderr.write(push.stdout + push.stderr)
        die("push failed; merge commit kept locally", EXIT_PUSH_FAILED)


def publish(vault: Path, owned_paths: list[str], message: str) -> int:
    if owned_paths:
        add = run_git(vault, "add", "--", *owned_paths)
        if add.returncode != 0:
            sys.stderr.write(add.stdout + add.stderr)
            die("failed to stage owned paths", EXIT_PRECONDITION)
    staged = run_git(vault, "diff", "--cached", "--quiet")
    if staged.returncode == 0:
        print("no changes to commit")
        return EXIT_OK
    commit = run_git(vault, "commit", "-m", message)
    if commit.returncode != 0:
        sys.stderr.write(commit.stdout + commit.stderr)
        die("commit failed", EXIT_PRECONDITION)
    push = run_git(vault, "push")
    if push.returncode != 0:
        sys.stderr.write(push.stdout + push.stderr)
        die("push failed; local commit kept (see git log)", EXIT_PUSH_FAILED)
    print("pushed")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    # Windows GBK console cannot encode Chinese/emoji in gate diagnostics; force
    # UTF-8 for this process's own streams (not on import, see vault_check).
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vault", required=True, help="fixed vault path (from noteall config.yaml)"
    )
    parser.add_argument(
        "--paths", nargs="*", default=[], help="owned paths relative to the vault"
    )
    parser.add_argument("--message", required=True, help="commit message")
    parser.add_argument(
        "--allow-issues",
        action="store_true",
        help="bypass the structural quality gate (warn and continue)",
    )
    args = parser.parse_args(argv)

    vault = Path(args.vault)
    validate_vault(vault)
    require_clean_worktree(vault, args.paths)
    if args.allow_issues:
        warn_quality_issues(vault, args.paths)
    else:
        quality_gate(vault, args.paths)
    sync_remote(vault)
    return publish(vault, args.paths, args.message)


if __name__ == "__main__":
    raise SystemExit(main())
