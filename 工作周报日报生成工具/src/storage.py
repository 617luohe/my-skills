"""本地拉取时间记录与工作 CSV。"""
from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path
from typing import Iterable

CSV_FIELDS = ("date", "project", "module", "summary", "sha", "author")


def today_midnight_local() -> dt.datetime:
    now = dt.datetime.now().astimezone()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def read_last_pull(path: Path) -> dt.datetime | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        raw = data.get("pulled_at") or data.get("iso_datetime")
        if not raw:
            return None
        parsed = dt.datetime.fromisoformat(raw)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.datetime.now().astimezone().tzinfo)
        return parsed.astimezone()
    except (json.JSONDecodeError, OSError, ValueError):
        return None


def write_last_pull(path: Path, when: dt.datetime | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    t = when or dt.datetime.now().astimezone()
    path.write_text(
        json.dumps({"pulled_at": t.isoformat()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_existing_shas(csv_path: Path) -> set[str]:
    if not csv_path.exists():
        return set()
    shas: set[str] = set()
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            s = (row.get("sha") or "").strip()
            if s:
                shas.add(s)
    return shas


def append_rows(csv_path: Path, rows: Iterable[dict[str, str]]) -> int:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if not rows:
        return 0
    new_file = not csv_path.exists()
    with csv_path.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if new_file:
            writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in CSV_FIELDS})
    return len(rows)


def previous_iso_week_monday(day: dt.date | None = None) -> dt.date:
    """当前 ISO 周上一个自然周的周一（本地日历）。"""
    d = day or dt.date.today()
    monday_this = d - dt.timedelta(days=d.weekday())
    return monday_this - dt.timedelta(days=7)


def pull_since_datetime(since_days: int | None = None) -> dt.datetime:
    """Gitee ``since``：在「上一 ISO 周周一」与「近 30 天」中取更早起点，避免遗漏跨周提交。"""
    local = dt.datetime.now().astimezone()
    tzinfo = local.tzinfo or dt.timezone.utc
    if since_days is not None:
        day = (local - dt.timedelta(days=since_days)).date()
        return dt.datetime.combine(day, dt.time.min, tzinfo=tzinfo)
    day_prev_iso = previous_iso_week_monday(local.date())
    day_roll = local.date() - dt.timedelta(days=30)
    day0 = min(day_prev_iso, day_roll)
    return dt.datetime.combine(day0, dt.time.min, tzinfo=tzinfo)


def iso_week_bounds(
    day: dt.date | None = None,
) -> tuple[dt.date, dt.date, int, int]:
    d = day or dt.date.today()
    year, week, _ = d.isocalendar()
    monday = dt.date.fromisocalendar(year, week, 1)
    sunday = monday + dt.timedelta(days=6)
    return monday, sunday, year, week
