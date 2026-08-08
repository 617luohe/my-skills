"""Black-box tests for vault-publisher/publish_vault.py using temp git repos.

Exit codes:
    0 = published (or no changes to commit)
    2 = precondition failed (invalid vault / unowned dirty worktree)
    3 = merge conflict (stopped, not auto-resolved)
    4 = push failed (local commit kept)
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "my-note"
    / "vault-publisher"
    / "scripts"
    / "publish_vault.py"
)

EXIT_OK = 0
EXIT_PRECONDITION = 2
EXIT_CONFLICT = 3
EXIT_PUSH_FAILED = 4
EXIT_QUALITY = 5


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )


def run_script(
    vault: Path, paths: list[str], message: str, *extra: str
) -> subprocess.CompletedProcess[str]:
    # Script forces UTF-8 on its own streams in main(); decode with UTF-8 even
    # when the parent process locale is GBK.
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--vault",
            str(vault),
            "--paths",
            *paths,
            "--message",
            message,
            *extra,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def origin_has(origin: Path, path: str) -> bool:
    r = subprocess.run(
        ["git", "--git-dir", str(origin), "cat-file", "-e", f"master:{path}"],
        capture_output=True,
    )
    return r.returncode == 0


@pytest.fixture
def vault_pair(tmp_path: Path):
    origin = tmp_path / "origin.git"
    vault = tmp_path / "vault"
    subprocess.run(
        ["git", "init", "--bare", str(origin)], check=True, capture_output=True
    )
    subprocess.run(["git", "init", str(vault)], check=True, capture_output=True)
    git(vault, "config", "user.email", "t@t.io")
    git(vault, "config", "user.name", "t")
    (vault / ".obsidian").mkdir()
    (vault / "a.md").write_text("a", encoding="utf-8")
    git(vault, "add", ".")
    assert git(vault, "commit", "-m", "init").returncode == 0
    git(vault, "remote", "add", "origin", str(origin))
    assert git(vault, "push", "-u", "origin", "master").returncode == 0
    return vault, origin


def test_publish_success_pushes(vault_pair):
    vault, origin = vault_pair
    (vault / "new.md").write_text("hello", encoding="utf-8")
    res = run_script(vault, ["new.md"], "notes(resource): ingest new")
    assert res.returncode == EXIT_OK, res.stdout + res.stderr
    assert origin_has(origin, "new.md")


def test_chinese_path_owned_and_deleted(vault_pair):
    # git porcelain escapes non-ASCII paths by default (core.quotepath=true);
    # a Chinese owned path must still be accepted, and a Chinese deletion
    # (raw -> 7-Sources archive move) must be stageable via owned paths.
    vault, origin = vault_pair
    (vault / "raw").mkdir()
    (vault / "raw" / "2026年工作总结.pptx").write_text("ppt", encoding="utf-8")
    git(vault, "add", ".")
    assert git(vault, "commit", "-m", "add raw").returncode == 0
    os.replace(vault / "raw" / "2026年工作总结.pptx", vault / "7-Sources.md")
    res = run_script(
        vault,
        ["raw/2026年工作总结.pptx", "7-Sources.md"],
        "notes(source): ingest 工作总结（归档）",
    )
    assert res.returncode == EXIT_OK, res.stdout + res.stderr
    assert not origin_has(origin, "raw/2026年工作总结.pptx")
    assert origin_has(origin, "7-Sources.md")


def test_dirty_worktree_stops(vault_pair):
    vault, origin = vault_pair
    (vault / "new.md").write_text("hello", encoding="utf-8")
    (vault / "outside.md").write_text("unowned", encoding="utf-8")  # not an owned path
    res = run_script(vault, ["new.md"], "notes(resource): ingest new")
    assert res.returncode == EXIT_PRECONDITION, res.stdout + res.stderr
    assert not origin_has(origin, "new.md")


def test_remote_ahead_fast_forwards(vault_pair):
    vault, origin = vault_pair
    git(vault, "checkout", "-b", "temp")
    (vault / "remote.md").write_text("remote", encoding="utf-8")
    git(vault, "add", ".")
    assert git(vault, "commit", "-m", "remote add").returncode == 0
    assert git(vault, "push", "origin", "temp:master").returncode == 0
    git(vault, "checkout", "master")
    (vault / "new.md").write_text("hello", encoding="utf-8")
    res = run_script(vault, ["new.md"], "notes(resource): ingest new")
    assert res.returncode == EXIT_OK, res.stdout + res.stderr
    assert origin_has(origin, "remote.md")
    assert origin_has(origin, "new.md")


def test_remote_conflict_stops(vault_pair):
    vault, origin = vault_pair
    git(vault, "checkout", "-b", "temp")
    (vault / "a.md").write_text("remote change", encoding="utf-8")
    git(vault, "add", ".")
    assert git(vault, "commit", "-m", "remote").returncode == 0
    assert git(vault, "push", "origin", "temp:master").returncode == 0
    git(vault, "checkout", "master")
    (vault / "a.md").write_text("local change", encoding="utf-8")
    git(vault, "add", ".")
    assert (
        git(vault, "commit", "-m", "local").returncode == 0
    )  # local diverge, not pushed
    (vault / "new.md").write_text("hello", encoding="utf-8")
    res = run_script(vault, ["new.md"], "notes(resource): ingest new")
    assert res.returncode == EXIT_CONFLICT, res.stdout + res.stderr


def test_push_failure_keeps_local_commit(vault_pair):
    vault, origin = vault_pair
    git(vault, "remote", "set-url", "origin", "file:///nonexistent/origin.git")
    (vault / "new.md").write_text("hello", encoding="utf-8")
    res = run_script(vault, ["new.md"], "notes(resource): ingest new")
    assert res.returncode == EXIT_PUSH_FAILED, res.stdout + res.stderr
    r = git(vault, "log", "-1", "--format=%s")
    assert "ingest new" in r.stdout


def test_no_changes_creates_no_commit(vault_pair):
    vault, origin = vault_pair
    before = git(vault, "rev-parse", "HEAD").stdout.strip()
    res = run_script(
        vault, ["a.md"], "notes(resource): ingest nothing"
    )  # a.md unchanged
    assert res.returncode == EXIT_OK, res.stdout + res.stderr
    assert git(vault, "rev-parse", "HEAD").stdout.strip() == before


def test_pending_push_retried_first(vault_pair):
    vault, origin = vault_pair
    (vault / "legacy.md").write_text("legacy", encoding="utf-8")
    git(vault, "add", ".")
    assert git(vault, "commit", "-m", "legacy pending").returncode == 0  # not pushed
    (vault / "new.md").write_text("hello", encoding="utf-8")
    res = run_script(vault, ["new.md"], "notes(resource): ingest new")
    assert res.returncode == EXIT_OK, res.stdout + res.stderr
    assert origin_has(origin, "legacy.md")
    assert origin_has(origin, "new.md")


def test_merge_without_owned_changes_still_pushes(vault_pair):
    vault, origin = vault_pair
    git(vault, "checkout", "-b", "temp")
    (vault / "remote.md").write_text("remote", encoding="utf-8")
    git(vault, "add", ".")
    assert git(vault, "commit", "-m", "remote add").returncode == 0
    assert git(vault, "push", "origin", "temp:master").returncode == 0
    git(vault, "checkout", "master")
    (vault / "local.md").write_text("local", encoding="utf-8")
    git(vault, "add", ".")
    assert git(vault, "commit", "-m", "local").returncode == 0
    res = run_script(vault, [], "notes(resource): ingest nothing")  # no owned changes
    assert res.returncode == EXIT_OK, res.stdout + res.stderr
    assert origin_has(origin, "remote.md")
    assert origin_has(origin, "local.md")


# ---------------------------------------------------------------------------
# T006: quality gate
# ---------------------------------------------------------------------------

# 7-Sources note with an illegal confidence enum value.
_BAD_7S = (
    "---\ntitle: 坏笔记\ntags:\n  - type/source\nstatus: draft\nconfidence: sprout\n---\n"
    "\n# 坏笔记\n"
)
# Fully compliant 7-Sources note (self-linked so it is not an orphan).
_GOOD_7S = (
    "---\ntitle: 好笔记\ntags:\n  - type/source\nstatus: draft\nconfidence: seed\n---\n"
    "\n# 好笔记\n\n[[好笔记]]\n"
)
# Valid frontmatter but a link to a non-existent note.
_BROKEN_7S = (
    "---\ntitle: 断链\ntags:\n  - type/source\nstatus: draft\nconfidence: seed\n---\n"
    "\n# 断链\n\n[[不存在的概念]]\n"
)


def test_gate_blocks_frontmatter_violation(vault_pair):
    vault, origin = vault_pair
    (vault / "7-Sources").mkdir(exist_ok=True)
    (vault / "7-Sources" / "坏笔记.md").write_text(_BAD_7S, encoding="utf-8")
    res = run_script(vault, ["7-Sources/坏笔记.md"], "notes(source): ingest bad")
    assert res.returncode == EXIT_QUALITY, res.stdout + res.stderr
    assert "confidence illegal value 'sprout'" in res.stderr
    assert not origin_has(origin, "7-Sources/坏笔记.md")


def test_gate_blocks_broken_link(vault_pair):
    vault, origin = vault_pair
    (vault / "7-Sources").mkdir(exist_ok=True)
    (vault / "7-Sources" / "断链.md").write_text(_BROKEN_7S, encoding="utf-8")
    res = run_script(vault, ["7-Sources/断链.md"], "notes(source): ingest bad")
    assert res.returncode == EXIT_QUALITY, res.stdout + res.stderr
    assert "broken link [[不存在的概念]]" in res.stderr
    assert not origin_has(origin, "7-Sources/断链.md")


def test_gate_allow_issues_passes(vault_pair):
    vault, origin = vault_pair
    (vault / "7-Sources").mkdir(exist_ok=True)
    (vault / "7-Sources" / "坏笔记.md").write_text(_BAD_7S, encoding="utf-8")
    res = run_script(
        vault,
        ["7-Sources/坏笔记.md"],
        "notes(source): ingest bad (override)",
        "--allow-issues",
    )
    assert res.returncode == EXIT_OK, res.stdout + res.stderr
    assert "bypassed quality gate" in res.stderr
    assert origin_has(origin, "7-Sources/坏笔记.md")


def test_gate_only_checks_owned_paths(vault_pair):
    # Historical violations (committed, not owned) must not block the publish.
    vault, origin = vault_pair
    (vault / "7-Sources").mkdir(exist_ok=True)
    (vault / "7-Sources" / "旧坏笔记.md").write_text(_BAD_7S, encoding="utf-8")
    git(vault, "add", ".")
    assert git(vault, "commit", "-m", "historical bad note").returncode == 0
    (vault / "7-Sources" / "好笔记.md").write_text(_GOOD_7S, encoding="utf-8")
    res = run_script(vault, ["7-Sources/好笔记.md"], "notes(source): ingest good")
    assert res.returncode == EXIT_OK, res.stdout + res.stderr
    assert origin_has(origin, "7-Sources/好笔记.md")


def test_gate_skipped_when_no_owned_paths(vault_pair):
    # No owned paths -> gate is skipped, even if the vault carries bad notes.
    vault, origin = vault_pair
    (vault / "7-Sources").mkdir(exist_ok=True)
    (vault / "7-Sources" / "坏笔记.md").write_text(_BAD_7S, encoding="utf-8")
    git(vault, "add", ".")
    assert git(vault, "commit", "-m", "bad note").returncode == 0
    res = run_script(vault, [], "notes(source): ingest nothing")
    assert res.returncode == EXIT_OK, res.stdout + res.stderr


def test_gate_blocks_missing_required_field(vault_pair):
    # A new 7-Sources note missing the required `confidence` field is a
    # structural violation (missing required fields block the gate).
    vault, origin = vault_pair
    (vault / "7-Sources").mkdir(exist_ok=True)
    (vault / "7-Sources" / "缺字段.md").write_text(
        "---\ntitle: 缺字段\ntags:\n  - type/source\nstatus: draft\n---\n\n# 缺字段\n",
        encoding="utf-8",
    )
    res = run_script(vault, ["7-Sources/缺字段.md"], "notes(source): ingest missing")
    assert res.returncode == EXIT_QUALITY, res.stdout + res.stderr
    assert "missing field(s) confidence" in res.stderr
    assert not origin_has(origin, "7-Sources/缺字段.md")
