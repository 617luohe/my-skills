#!/usr/bin/env python3
"""Black-box smoke tests for keep_claude_fast.py against a temporary CLAUDE_HOME.

Run: python tests/smoke_test.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "keep_claude_fast.py"

OLD_ID = "11111111-1111-1111-1111-111111111111"
NEW_ID = "22222222-2222-2222-2222-222222222222"
CURRENT_ID = "33333333-3333-3333-3333-333333333333"

FAILED = []


def check(name: str, condition: bool, detail: str = "") -> None:
    status = "ok" if condition else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not condition else ""))
    if not condition:
        FAILED.append(name)


def run_cli(home: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--claude-home", str(home), *args],
        capture_output=True,
        text=True,
        errors="replace",
        timeout=120,
    )


def make_home(home: Path) -> None:
    p1 = home / "projects" / "p1"
    p1.mkdir(parents=True)
    old = time.time() - 30 * 86400
    (p1 / f"{OLD_ID}.jsonl").write_text("x" * 1000)
    sdir = p1 / OLD_ID
    (sdir / "tool-results").mkdir(parents=True)
    (sdir / "tool-results" / "a.txt").write_text("y")
    (p1 / f"{NEW_ID}.jsonl").write_text("z" * 500)
    # 当前会话：本测试进程即"调用方"（pid + cwd 双匹配），jsonl 设为超期但必须被跳过
    (p1 / f"{CURRENT_ID}.jsonl").write_text("c" * 300)
    os.utime(p1 / f"{CURRENT_ID}.jsonl", (old, old))
    (p1 / "memory").mkdir()
    (p1 / "memory" / "MEMORY.md").write_text("keep")
    (p1 / "CLAUDE.md").write_text("keep")
    (p1 / "notes.txt").write_text("keep")

    os.utime(p1 / f"{OLD_ID}.jsonl", (old, old))
    for f in (p1 / OLD_ID).rglob("*"):
        os.utime(f, (old, old))

    (home / "sessions").mkdir()
    (home / "sessions" / "99999999.json").write_text(
        json.dumps({"pid": 99999999, "sessionId": OLD_ID, "entrypoint": "cli"})
    )
    # 当前调用方会话：pid 为本测试进程，cwd 为测试运行目录
    (home / "sessions" / f"{os.getpid()}.json").write_text(
        json.dumps(
            {
                "pid": os.getpid(),
                "sessionId": CURRENT_ID,
                "cwd": os.getcwd(),
                "entrypoint": "claude-vscode",
            }
        )
    )
    lines = [
        json.dumps(
            {"display": "m", "timestamp": i, "sessionId": OLD_ID if i % 2 else NEW_ID}
        )
        for i in range(20)
    ]
    (home / "history.jsonl").write_text("\n".join(lines) + "\n")
    (home / "telemetry").mkdir()
    (home / "telemetry" / "t.json").write_text("{}")
    (home / "cache").mkdir()
    (home / "cache" / "c.json").write_text("{}")


def main() -> int:
    home = Path(tempfile.mkdtemp(prefix="kcf-test-"))
    backup = Path(tempfile.mkdtemp(prefix="kcf-backup-")) / "bk"
    try:
        make_home(home)

        # 1. report: read-only, no writes
        r = run_cli(home)
        check("report exits 0", r.returncode == 0, r.stdout[-300:])
        check("report lists project", "projects 1" in r.stdout, r.stdout)
        check(
            "report flags old candidates",
            "old_session_candidates 2" in r.stdout,
            r.stdout,
        )
        check("report created nothing", not (home / "archived").exists())
        check("report created no backup", not (home / "history.jsonl.bak").exists())

        # 2. backup-only
        r = run_cli(home, "--backup-only", "--backup-root", str(backup))
        check("backup-only exits 0", r.returncode == 0, r.stdout[-300:])
        check("backup has history copy", (backup / "history.jsonl").exists())
        check("backup-only archived nothing", not (home / "archived").exists())

        # 3. apply from inside a Claude Code session (current session identified
        #    by pid/cwd in the registry, so apply runs without --force)
        r = run_cli(home, "--apply", "--backup-root", str(backup))
        check("apply exits 0", r.returncode == 0, r.stdout[-300:])
        check(
            "apply auto-excluded current session",
            "auto_excluded_current_session 1" in r.stdout,
            r.stdout,
        )
        archived = (
            sorted((home / "archived" / "p1").glob("*"))
            if (home / "archived" / "p1").exists()
            else []
        )
        check("apply archived old session", len(archived) == 1, str(archived))
        if archived:
            stamp_dir = archived[0]
            check("apply moved jsonl", (stamp_dir / f"{OLD_ID}.jsonl").exists())
            check(
                "apply moved session dir",
                (stamp_dir / OLD_ID / "tool-results" / "a.txt").exists(),
            )
        check(
            "apply kept new session",
            (home / "projects" / "p1" / f"{NEW_ID}.jsonl").exists(),
        )
        check(
            "apply kept current session",
            (home / "projects" / "p1" / f"{CURRENT_ID}.jsonl").exists(),
        )
        check(
            "apply kept memory",
            (home / "projects" / "p1" / "memory" / "MEMORY.md").read_text() == "keep",
        )
        check(
            "apply kept CLAUDE.md",
            (home / "projects" / "p1" / "CLAUDE.md").read_text() == "keep",
        )
        check(
            "apply kept non-uuid file",
            (home / "projects" / "p1" / "notes.txt").exists(),
        )
        check(
            "apply pruned archived history ids",
            OLD_ID not in (home / "history.jsonl").read_text(),
        )
        check(
            "apply kept new history ids", NEW_ID in (home / "history.jsonl").read_text()
        )
        check("apply archived telemetry", not (home / "telemetry").exists())
        check("apply archived cache", not (home / "cache").exists())
        check("apply wrote manifest", (backup / "moved-items.jsonl").exists())
        check(
            "apply wrote restore script", (backup / "restore-claude-fast.py").exists()
        )
        reports = list(backup.glob("cleanup-report-*.md"))
        check("apply wrote cleanup report", len(reports) == 1, str(reports))
        if reports:
            report_text = reports[0].read_text(encoding="utf-8")
            check(
                "report has summary + detail",
                "处理摘要" in report_text
                and "归档会话" in report_text
                and "恢复方法" in report_text,
                report_text[:200],
            )

        # 4. history keep-last limit
        kept_rows = len((home / "history.jsonl").read_text().splitlines())
        check("history within keep-last", kept_rows <= 10, f"rows={kept_rows}")

        # 5. restore is reversible
        r = subprocess.run(
            [sys.executable, str(backup / "restore-claude-fast.py")],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=60,
        )
        check("restore script runs", r.returncode == 0, r.stdout + r.stderr)
        check(
            "restore put jsonl back",
            (home / "projects" / "p1" / f"{OLD_ID}.jsonl").exists(),
        )
        check(
            "restore put session dir back",
            (home / "projects" / "p1" / OLD_ID / "tool-results" / "a.txt").exists(),
        )
        leftover = (
            list((home / "archived" / "p1").rglob("*"))
            if (home / "archived" / "p1").exists()
            else []
        )
        check(
            "restore removed archive files",
            all(p.is_dir() for p in leftover),
            str(leftover),
        )

        # 6. keep-last flag honored on a fresh run
        (home / "projects" / "p1" / f"{OLD_ID}.jsonl").write_text("r" * 1000)
        os.utime(
            home / "projects" / "p1" / f"{OLD_ID}.jsonl",
            (time.time() - 30 * 86400,) * 2,
        )
        r = run_cli(
            home,
            "--apply",
            "--history-keep-last",
            "3",
            "--backup-root",
            str(backup),
        )
        check("apply with keep-last exits 0", r.returncode == 0, r.stdout[-300:])
        kept_rows = len((home / "history.jsonl").read_text().splitlines())
        check("keep-last=3 honored", kept_rows <= 3, f"rows={kept_rows}")

        # 7. missing claude-home is reported, not crashed
        r = run_cli(home / "does-not-exist")
        check(
            "missing home handled",
            r.returncode == 0 and "claude_home_missing" in r.stdout,
            r.stdout[-300:],
        )
    finally:
        shutil.rmtree(home, ignore_errors=True)
        shutil.rmtree(Path(backup).parent, ignore_errors=True)

    print()
    if FAILED:
        print(f"{len(FAILED)} FAILED: {', '.join(FAILED)}")
        return 1
    print("all smoke tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
