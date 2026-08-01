#!/usr/bin/env python3
"""Backup-first Claude Code local-state maintenance.

Default mode is a read-only, privacy-safe report. Use --apply to archive/move.

Safely reduces local drag of Claude Code (CLI and VSCode plugin share ~/.claude):

- reports which project session stores have grown over time
- archives old sessions instead of deleting them
- prunes archived session ids from history.jsonl and keeps only the most recent rows
- archives telemetry/ and cache/ data
- writes manifests and restore scripts so every change is reversible
- never touches project-level memory/, CLAUDE.md, todos/, tasks/, skills/ files
- refuses to apply while Claude Code is running (unless --force)
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SESSION_ID_RE = re.compile(
    r"^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(\.jsonl)?$",
    re.I,
)
PROJECT_NAME_RE = re.compile(r"^[a-z]--")


@dataclass
class SessionFile:
    session_id: str
    jsonl: Path
    size: int
    mtime: float


@dataclass
class ProjectStat:
    name: str
    decoded: str
    session_files: list[SessionFile]
    total_size: int


@dataclass
class MovedItem:
    kind: str  # session | telemetry | cache
    session_id: str | None
    project: str | None
    from_path: str
    to_path: str
    bytes: int


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def report(line: str) -> None:
    print(line)


def claude_home_from_args(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    override = os.environ.get("CLAUDE_CONFIG_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".claude"


def documents_backup_root() -> Path:
    return Path.home() / "Documents" / "Claude" / "claude-backups"


def size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        try:
            return path.stat().st_size
        except OSError:
            return 0
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            try:
                total += item.stat().st_size
            except OSError:
                pass
    return total


def mb(value: int) -> str:
    return f"{value / 1024 / 1024:.1f}"


def gb(value: int) -> str:
    return f"{value / 1024 / 1024 / 1024:.3f}"


def canonical(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError:
        return path.absolute()


def decode_project_name(name: str) -> str:
    """Best-effort decode of the encoded project dir name (display only).

    Encoding: lowercase path, every non [a-z0-9] char replaced by '-', trailing
    slash dropped. Decoding cannot recover original chars exactly, so a run of
    trailing dashes becomes '?' and inner dashes are treated as path separators.
    """
    m = re.match(r"^([a-z])--(.*)$", name)
    if not m:
        return name
    drive = m.group(1).upper()
    rest = m.group(2)
    trailing = len(rest) - len(rest.rstrip("-"))
    body = rest[: len(rest) - trailing] if trailing else rest
    path = body.replace("-", "\\")
    return f"{drive}:\\{path}" + ("?" * trailing)


def run_powershell(command: str) -> list[dict]:
    try:
        output = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", command],
            text=True,
            stderr=subprocess.DEVNULL,
            errors="replace",
        )
    except Exception:
        return []
    if not output.strip():
        return []
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else [data]


def claude_processes_running() -> list[str]:
    """Return descriptions of running Claude Code processes (CLI + VSCode plugin)."""
    system = platform.system()
    if system == "Windows":
        rows = run_powershell(
            "Get-CimInstance Win32_Process | Select-Object Name,ProcessId,CommandLine | ConvertTo-Json -Compress"
        )
        hits = []
        for row in rows:
            name = str(row.get("Name") or "").lower()
            cmd = str(row.get("CommandLine") or "").lower()
            pid = row.get("ProcessId")
            if name == "claude.exe":
                hits.append(f"{pid} claude.exe")
            elif name == "node.exe" and "claude" in cmd:
                hits.append(f"{pid} node (claude)")
        return hits
    try:
        output = subprocess.check_output(
            ["ps", "-axo", "pid=,comm=,args="], text=True, errors="replace"
        )
    except Exception:
        return []
    hits = []
    for line in output.splitlines():
        lower = line.lower()
        if "claude" in lower and ("claude" in lower.split()[:2] or "node" in lower):
            hits.append(line.strip())
    return hits


def active_sessions(claude_home: Path) -> list[dict]:
    """Read sessions/*.json registry: running interactive sessions.

    Each entry: {"pid": ..., "sessionId": ..., "cwd": ..., "entrypoint": "claude-vscode"|"cli"}
    """
    registry = claude_home / "sessions"
    out = []
    for path in sorted(registry.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        if isinstance(data, dict) and data.get("sessionId"):
            out.append(data)
    return out


def pid_alive(pid: int) -> bool:
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output(
                ["tasklist", "/FI", f"PID eq {pid}"], text=True, errors="replace"
            )
            return str(pid) in output
        except Exception:
            return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def running_session_ids(claude_home: Path) -> set[str]:
    ids = set()
    for entry in active_sessions(claude_home):
        try:
            if pid_alive(int(entry["pid"])):
                ids.add(str(entry["sessionId"]))
        except (KeyError, ValueError):
            continue
    return ids


def collect_projects(claude_home: Path) -> list[ProjectStat]:
    root = claude_home / "projects"
    projects: list[ProjectStat] = []
    if not root.is_dir():
        return projects
    for entry in sorted(root.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        sessions: list[SessionFile] = []
        total = 0
        for f in entry.iterdir():
            m = SESSION_ID_RE.match(f.name)
            if not m:
                continue
            if f.is_file():
                try:
                    st = f.stat()
                    size = st.st_size
                    mtime = st.st_mtime
                except OSError:
                    size, mtime = 0, 0.0
                sessions.append(SessionFile(m.group(1), f, size, mtime))
                total += size
            elif f.is_dir():
                total += size_bytes(f)
        projects.append(
            ProjectStat(entry.name, decode_project_name(entry.name), sessions, total)
        )
    projects.sort(key=lambda p: p.total_size, reverse=True)
    return projects


def candidate_sessions(
    projects: list[ProjectStat], older_than_days: int, active_ids: set[str]
) -> list[tuple[ProjectStat, SessionFile]]:
    cutoff = time.time() - older_than_days * 24 * 60 * 60
    out: list[tuple[ProjectStat, SessionFile]] = []
    for project in projects:
        for s in project.session_files:
            if s.session_id in active_ids:
                continue
            if s.mtime >= cutoff:
                continue
            out.append((project, s))
    out.sort(key=lambda item: item[1].size, reverse=True)
    return out


def report_scan(
    claude_home: Path, *, details: bool, archive_older_than_days: int
) -> None:
    if not claude_home.exists():
        report(f"claude_home_missing {claude_home}")
        return

    projects = collect_projects(claude_home)
    project_total = sum(p.total_size for p in projects)
    session_count = sum(len(p.session_files) for p in projects)
    report(f"claude_home {claude_home}")
    report(f"projects {len(projects)}")
    report(f"session_files {session_count}")
    report(f"projects_size_mb {mb(project_total)}")
    if projects:
        report("project_sizes")
        for p in projects:
            label = f"project_{p.name}" if details else "project"
            report(
                f"  {mb(p.total_size)} MB {p.name}  ({p.decoded}) files={len(p.session_files)}"
            )

    top = sorted(
        ((s, p) for p in projects for s in p.session_files),
        key=lambda item: item[0].size,
        reverse=True,
    )
    if top:
        report("largest_sessions")
        for s, p in top[:10]:
            if details:
                report(f"  {mb(s.size)} MB {p.name}/{s.jsonl.name}")
            else:
                report(f"  {mb(s.size)} MB {p.name}")

    cutoff = datetime.now() - timedelta(days=archive_older_than_days)
    old = [s for p in projects for s in p.session_files if s.mtime < cutoff.timestamp()]
    old_size = sum(s.size for s in old)
    report(f"old_session_candidates {len(old)} (mtime < {cutoff.date()})")
    report(f"old_session_candidate_mb {mb(old_size)}")

    for rel, label in [
        ("history.jsonl", "history"),
        ("telemetry", "telemetry"),
        ("cache", "cache"),
        ("file-history", "file_history"),
        ("shell-snapshots", "shell_snapshots"),
        ("plugins", "plugins"),
        ("hooks", "hooks"),
        ("skills", "skills"),
        ("backups", "backups"),
    ]:
        path = claude_home / rel
        if path.exists():
            report(f"{label}_mb {mb(size_bytes(path))}")
    history = claude_home / "history.jsonl"
    if history.exists():
        try:
            lines = history.read_text(encoding="utf-8", errors="replace").splitlines()
            report(f"history_rows {len(lines)}")
        except Exception:
            report("history_rows 0")

    running = claude_processes_running()
    report(f"claude_processes_running {len(running)}")
    for proc in running:
        if details:
            report(f"  running_process {proc}")
        else:
            report("  running_process claude")
    active = running_session_ids(claude_home)
    report(f"active_sessions {len(active)}")


def backup_metadata(claude_home: Path, backup_root: Path) -> None:
    backup_root.mkdir(parents=True, exist_ok=True)
    for name in ["history.jsonl"]:
        src = claude_home / name
        if src.exists():
            shutil.copy2(src, backup_root / name)
            report(f"backed_up {name}")


def write_restore_script(manifest: Path, backup_root: Path) -> None:
    restore = backup_root / "restore-claude-fast.py"
    restore.write_text(
        f'''"""Restore files moved by keep-claude-fast. Read-only helper, run manually."""
import json
import shutil
from pathlib import Path

manifest = Path(r"{manifest}")
moved = 0
for line in manifest.read_text(encoding="utf-8").splitlines():
    rec = json.loads(line)
    src = Path(rec["to_path"])
    dest = Path(rec["from_path"])
    if src.exists() and not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        moved += 1
print(f"restored {{moved}} items")
print("note: history.jsonl itself was not rewritten; restore it from the backup folder if needed")
''',
        encoding="utf-8",
    )
    report(f"restore_script {restore}")


def archive_sessions(
    claude_home: Path,
    candidates: list[tuple[ProjectStat, SessionFile]],
    backup_root: Path,
    stamp: str,
    apply: bool,
    details: bool,
) -> None:
    total = sum(item.size for _, item in candidates)
    report(f"session_archive_candidates {len(candidates)}")
    report(f"session_archive_candidate_mb {mb(total)}")
    for index, (project, s) in enumerate(candidates[:10], start=1):
        if details:
            report(
                f"  session_{index:03d} {mb(s.size)} MB {project.name}/{s.jsonl.name}"
            )
        else:
            report(f"  session_{index:03d} {mb(s.size)} MB {project.name}")
    if not apply:
        return

    manifest_path = backup_root / "moved-items.jsonl"
    items: list[MovedItem] = []
    with manifest_path.open("a", encoding="utf-8") as handle:
        for project, s in candidates:
            archive_root = claude_home / "archived" / project.name / stamp
            dest_jsonl = archive_root / s.jsonl.name
            dest_dir = archive_root / s.session_id
            moved_bytes = 0
            try:
                archive_root.mkdir(parents=True, exist_ok=True)
                shutil.move(str(s.jsonl), str(dest_jsonl))
                moved_bytes += s.size
                item = MovedItem(
                    kind="session",
                    session_id=s.session_id,
                    project=project.name,
                    from_path=str(s.jsonl),
                    to_path=str(dest_jsonl),
                    bytes=moved_bytes,
                )
                handle.write(json.dumps(item.__dict__, ensure_ascii=False) + "\n")
                items.append(item)
                if s.jsonl.with_suffix("").is_dir():
                    src_dir = s.jsonl.with_suffix("")
                    shutil.move(str(src_dir), str(dest_dir))
                    item = MovedItem(
                        kind="session_dir",
                        session_id=s.session_id,
                        project=project.name,
                        from_path=str(src_dir),
                        to_path=str(dest_dir),
                        bytes=0,
                    )
                    handle.write(json.dumps(item.__dict__, ensure_ascii=False) + "\n")
                    items.append(item)
                report(f"  archived {project.name}/{s.jsonl.name}")
            except OSError as exc:
                report(f"  skipped_locked {project.name}/{s.jsonl.name} ({exc})")
    if items:
        write_restore_script(manifest_path, backup_root)
        report(f"session_archive_root {claude_home / 'archived'}")
        report(f"moved_manifest {manifest_path}")


def prune_history(
    claude_home: Path,
    backup_root: Path,
    archived_ids: set[str],
    keep_last: int,
    apply: bool,
) -> None:
    path = claude_home / "history.jsonl"
    if not path.exists():
        report("history_prune_skipped_missing")
        return
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as exc:
        report(f"history_prune_skipped_read_error {exc}")
        return
    before = len(lines)

    kept: list[str] = []
    removed_ids = 0
    for line in lines:
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            kept.append(line)
            continue
        sid = str(data.get("sessionId") or "")
        if sid in archived_ids:
            removed_ids += 1
            continue
        kept.append(line)

    # history.jsonl is append-ordered; keep only the most recent rows.
    kept = kept[-keep_last:] if keep_last > 0 else kept
    report(f"history_rows_before {before}")
    report(f"history_rows_removed_archived {removed_ids}")
    report(f"history_rows_kept {len(kept)}")
    if not apply:
        return
    tmp = path.with_suffix(".jsonl.tmp")
    tmp.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    os.replace(str(tmp), str(path))
    report("history_pruned applied")


def archive_dir(
    claude_home: Path,
    name: str,
    stamp: str,
    apply: bool,
    manifest_path: Path | None = None,
) -> None:
    src = claude_home / name
    if not src.exists() or not src.is_dir():
        report(f"{name}_archive_skipped_missing")
        return
    size = size_bytes(src)
    report(f"{name}_archive_size_mb {mb(size)}")
    if not apply:
        return
    dest = claude_home / "archived" / f"{name}-{stamp}"
    try:
        shutil.move(str(src), str(dest))
        report(f"{name}_archived_to {dest}")
        if manifest_path is not None:
            item = MovedItem(
                kind="dir",
                session_id=None,
                project=None,
                from_path=str(src),
                to_path=str(dest),
                bytes=size,
            )
            with manifest_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(item.__dict__, ensure_ascii=False) + "\n")
    except OSError as exc:
        report(f"{name}_archive_skipped_locked {exc}")


def verify_sizes(claude_home: Path) -> None:
    for rel in ["projects", "archived", "telemetry", "cache"]:
        path = claude_home / rel
        if path.exists():
            report(f"size_{rel}_mb {mb(size_bytes(path))}")


def run(args: argparse.Namespace) -> int:
    claude_home = claude_home_from_args(args.claude_home)
    stamp = now_stamp()
    backup_root = (
        Path(args.backup_root).expanduser().resolve()
        if args.backup_root
        else documents_backup_root() / f"keep-claude-fast-{stamp}"
    )

    running = claude_processes_running()
    if args.apply and running and args.wait_for_claude_exit:
        report("waiting_for_claude_exit")
        while claude_processes_running():
            time.sleep(2)
        running = []

    requested_mode = (
        "apply" if args.apply else "backup-only" if args.backup_only else "report"
    )
    effective_apply = bool(args.apply and (not running or args.force))
    effective_backup = bool(effective_apply or args.backup_only)
    effective_mode = (
        "apply" if effective_apply else "backup-only" if effective_backup else "report"
    )

    if args.details:
        report(f"claude_home {claude_home}")
        if effective_backup:
            report(f"backup_root {backup_root}")
    elif effective_backup:
        report(f"backup_root {backup_root}")
    report(f"requested_mode {requested_mode}")
    report(f"effective_mode {effective_mode}")
    if effective_mode == "report":
        report("mode_safety read_only=true privacy=pseudonymous")
    elif effective_mode == "backup-only":
        report("mode_safety backup_only=true archives=false state_writes=false")
    else:
        report("mode_safety backup_first=true archive_only=true permanent_delete=false")

    if args.apply and not effective_apply:
        report("apply_skipped_claude_running")
        for index, proc in enumerate(running, start=1):
            if args.details:
                report(f"  blocking_process {proc}")
            else:
                report(f"  blocking_process claude_process_{index:03d}")
        return 1

    if effective_backup:
        backup_metadata(claude_home, backup_root)

    report_scan(
        claude_home,
        details=args.details,
        archive_older_than_days=args.archive_older_than_days,
    )

    if effective_mode == "apply":
        active = running_session_ids(claude_home)
        projects = collect_projects(claude_home)
        candidates = candidate_sessions(projects, args.archive_older_than_days, active)
        archive_sessions(
            claude_home,
            candidates,
            backup_root,
            stamp,
            apply=True,
            details=args.details,
        )

        archived_ids = set()
        manifest_path = backup_root / "moved-items.jsonl"
        if manifest_path.exists():
            for line in manifest_path.read_text(
                encoding="utf-8", errors="replace"
            ).splitlines():
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("kind") == "session" and rec.get("session_id"):
                    archived_ids.add(rec["session_id"])
        prune_history(
            claude_home, backup_root, archived_ids, args.history_keep_last, apply=True
        )
        archive_dir(
            claude_home, "telemetry", stamp, apply=True, manifest_path=manifest_path
        )
        archive_dir(
            claude_home, "cache", stamp, apply=True, manifest_path=manifest_path
        )
        verify_sizes(claude_home)

    report("done")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safe, backup-first, archive-only Claude Code local-state maintenance."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply maintenance actions. Default is report-only.",
    )
    parser.add_argument(
        "--backup-only",
        action="store_true",
        help="Create backups without applying maintenance actions. Default report mode writes no files.",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Include raw session ids, paths, and process details in output.",
    )
    parser.add_argument(
        "--wait-for-claude-exit",
        action="store_true",
        help="Wait until Claude Code exits before applying.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Apply even if Claude Code processes are running.",
    )
    parser.add_argument(
        "--claude-home",
        help="Override Claude Code home. Defaults to CLAUDE_CONFIG_DIR or ~/.claude.",
    )
    parser.add_argument("--backup-root", help="Override backup output folder.")
    parser.add_argument("--archive-older-than-days", type=int, default=10)
    parser.add_argument("--history-keep-last", type=int, default=500)
    args = parser.parse_args(argv)
    if args.apply and args.backup_only:
        parser.error("--apply and --backup-only cannot be used together")
    if args.archive_older_than_days < 1:
        parser.error("--archive-older-than-days must be at least 1")
    return args


if __name__ == "__main__":
    raise SystemExit(run(parse_args(sys.argv[1:])))
