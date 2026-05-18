"""从 CSV 生成精简周报 Markdown。"""
from __future__ import annotations

import csv
import datetime as dt
from collections import defaultdict
from pathlib import Path

from .storage import iso_week_bounds


def _truncate(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"


def load_recent_rows(csv_path: Path, end: dt.date, days: int = 14) -> list[dict[str, str]]:
    """读取 ``days`` 个自然日（含 ``end`` 当日）内的记录。"""
    if not csv_path.exists():
        return []
    start = end - dt.timedelta(days=days - 1)
    rows: list[dict[str, str]] = []
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ds = (row.get("date") or "").strip()
            try:
                d = dt.date.fromisoformat(ds)
            except ValueError:
                continue
            if start <= d <= end:
                rows.append(row)
    return rows


def build_weekly_markdown(
    csv_path: Path,
    max_chars_per_project: int = 300,
    reference_day: dt.date | None = None,
    report_days: int = 14,
) -> tuple[str, str]:
    _, _, year, week = iso_week_bounds(reference_day)
    filename = f"{year}年第{week}周周报.md"
    title = f"{year}年第{week}周工作周报"

    end = reference_day or dt.date.today()
    rows = load_recent_rows(csv_path, end, days=report_days)
    start = end - dt.timedelta(days=report_days - 1)
    by_project: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for r in rows:
        proj = (r.get("project") or "未命名项目").strip()
        mod = (r.get("module") or "综合").strip()
        summary = (r.get("summary") or "").strip()
        if summary:
            by_project[proj][mod].append(summary)

    lines: list[str] = [
        f"# {title}",
        "",
        f"- 文件名按 ISO 周次命名；正文汇总区间为最近 {report_days} 个自然日（含当日）："
        f"{start.isoformat()} 至 {end.isoformat()}。",
        "- 说明：侧重功能与逻辑变更相关提交摘要，不做量化统计。",
        "",
    ]

    if not rows:
        lines.append(
            "上述区间内暂无已同步的提交记录；可先执行同步或扩大拉取范围（如 `--since-days`）。\n"
        )
        return filename, "\n".join(lines)

    for project in sorted(by_project.keys()):
        module_chunks: list[str] = []
        for module in sorted(by_project[project].keys()):
            msgs = by_project[project][module]
            merged = "；".join(dict.fromkeys(msgs))
            module_chunks.append(f"{module}：{merged}")
        body_raw = " ".join(module_chunks)
        suffix = "\n\n**下周预期：** 各模块按迭代计划推进功能完善与联调验证。\n"
        prefix = f"## {project}\n\n**模块进展：** "
        budget = max_chars_per_project - len(prefix) - len(suffix)
        body = _truncate(body_raw, max(budget, 0))
        section = prefix + body + suffix
        lines.append(section.rstrip())
        lines.append("")

    return filename, "\n".join(lines).rstrip() + "\n"


def write_weekly_doc(
    docs_dir: Path,
    csv_path: Path,
    report_days: int = 14,
) -> Path:
    docs_dir.mkdir(parents=True, exist_ok=True)
    filename, body = build_weekly_markdown(csv_path, report_days=report_days)
    path = docs_dir / filename
    path.write_text(body, encoding="utf-8")
    return path


def build_daily_markdown(
    csv_path: Path,
    max_chars_per_project: int = 300,
    day: dt.date | None = None,
) -> tuple[str, str]:
    """单日汇总：文件名 ``YYYY-MM-DD日报.md``。"""
    d = day or dt.date.today()
    filename = f"{d.isoformat()}日报.md"
    title = f"{d.year}年{d.month}月{d.day}日工作日报"

    rows = load_recent_rows(csv_path, d, days=1)
    by_project: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for r in rows:
        proj = (r.get("project") or "未命名项目").strip()
        mod = (r.get("module") or "综合").strip()
        summary = (r.get("summary") or "").strip()
        if summary:
            by_project[proj][mod].append(summary)

    lines: list[str] = [
        f"# {title}",
        "",
        f"- 统计日：{d.isoformat()}（本地日历单日）。",
        "- 说明：侧重功能与逻辑变更相关提交摘要，不做量化统计。",
        "",
    ]

    if not rows:
        lines.append(
            "当日暂无已同步的提交记录；可先执行同步或调整 `--since-days`。\n"
        )
        return filename, "\n".join(lines)

    for project in sorted(by_project.keys()):
        module_chunks: list[str] = []
        for module in sorted(by_project[project].keys()):
            msgs = by_project[project][module]
            merged = "；".join(dict.fromkeys(msgs))
            module_chunks.append(f"{module}：{merged}")
        body_raw = " ".join(module_chunks)
        suffix = "\n\n**明日预期：** 各模块按迭代计划继续推进开发与联调验证。\n"
        prefix = f"## {project}\n\n**模块进展：** "
        budget = max_chars_per_project - len(prefix) - len(suffix)
        body = _truncate(body_raw, max(budget, 0))
        section = prefix + body + suffix
        lines.append(section.rstrip())
        lines.append("")

    return filename, "\n".join(lines).rstrip() + "\n"


def write_daily_doc(
    docs_dir: Path,
    csv_path: Path,
    day: dt.date | None = None,
) -> Path:
    docs_dir.mkdir(parents=True, exist_ok=True)
    filename, body = build_daily_markdown(csv_path, day=day)
    path = docs_dir / filename
    path.write_text(body, encoding="utf-8")
    return path
