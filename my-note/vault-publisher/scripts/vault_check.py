#!/usr/bin/env python3
"""Deterministic health check for the fixed vault.

Scans frontmatter compliance, broken wikilinks, orphan notes, duplicate
candidates, and _INDEX staleness so noteall's health checks stop depending on
freeform grep and become reproducible, testable output.

Exit codes:
    0  clean (no findings above severity)
    1  findings above severity found
    2  precondition failed (invalid vault)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_PRECONDITION = 2

# System/template directories excluded from content scans.
EXCLUDED_PARTS = {".git", ".obsidian", ".claude", ".codex", ".cursor"}
# Root-level system files that are not content notes.
EXCLUDED_ROOT_FILES = {"CLAUDE.md", "欢迎.md"}
# 8-Templates holds placeholder links; 9-System may hold illustrative examples.
PLACEHOLDER_DIRS = {"8-Templates", "9-System"}

# Wikilink targets that are intentional placeholders or illustrative examples.
PLACEHOLDER_TARGETS = {
    "概念A",
    "概念B",
    "项目A",
    "项目B",
    "笔记名",
    "笔记A",
    "笔记名#章节",
    "相关笔记1",
    "相关笔记2",
    "相关笔记3",
    "相关笔记4",
    "相关MOC-1",
    "相关MOC-2",
    "相关资源1",
    "相关项目1",
    "相关会议1",
    "相关概念A",
    "相关概念B",
    "相关书籍/文章",
    "参考来源1",
    "来源笔记",
    "人名",
    "人名1",
    "wikilink",
    "link",
    "创建链接",
    "{{project-name}}",
    "LLM基础",
    "向量数据库",
    "Transformer架构",
    "迁移学习",
    "模型评估指标",
    "AI智能体",
    "认知偏差",
    "系统1与系统2",
    "前景理论",
    "项目沟通",
}

LINK_RE = re.compile(r"\[\[([^\[\]|]+)(?:\|[^\]]*)?\]\]")
# Required frontmatter fields per top-level directory. title is optional
# (Obsidian defaults it to the filename). Journals/MOCs use tag-based status.
FM_REQUIRED_BY_DIR = {
    "0-Inbox": (),
    "1-Atlas": ("tags",),
    "2-Projects": ("tags", "status"),
    "3-Areas": ("tags", "status"),
    "4-Resources": ("tags", "status", "confidence"),
    "5-Journal": ("title", "tags"),
    "6-People": ("title", "tags"),
    "7-Sources": ("title", "tags", "status", "confidence"),
    "9-System": ("title", "tags", "status"),
}
FM_DEFAULT = ("tags",)


@dataclass
class Findings:
    frontmatter: list[str] = field(default_factory=list)
    broken_links: list[str] = field(default_factory=list)
    orphans: list[str] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    index_stale: list[str] = field(default_factory=list)

    def count(self) -> int:
        return (
            len(self.frontmatter)
            + len(self.broken_links)
            + len(self.orphans)
            + len(self.duplicates)
            + len(self.index_stale)
        )


def die(msg: str, code: int) -> None:
    sys.stderr.write(f"vault_check: {msg}\n")
    raise SystemExit(code)


def validate_vault(vault: Path) -> None:
    if not vault.is_dir():
        die(f"vault not found: {vault}", EXIT_PRECONDITION)
    if not (vault / ".obsidian").is_dir():
        die(f"not an obsidian vault (missing .obsidian): {vault}", EXIT_PRECONDITION)


def _is_excluded(rel: str) -> bool:
    return any(part in EXCLUDED_PARTS for part in rel.split("/"))


def _md_files(vault: Path) -> list[tuple[str, Path]]:
    files = []
    for p in vault.rglob("*.md"):
        rel = p.relative_to(vault).as_posix()
        if _is_excluded(rel):
            continue
        if rel in EXCLUDED_ROOT_FILES:
            continue
        files.append((rel, p))
    return sorted(files)


def _frontmatter_fields(text: str) -> set[str] | None:
    """Return top-level frontmatter keys, or None if the file has no FM block."""
    if not text.lstrip().startswith("---"):
        return None
    lines = text.lstrip().splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None
    keys = set()
    for line in lines[1:end]:
        if not line.strip() or line[0] in " \t":
            continue
        key, _, _ = line.partition(":")
        keys.add(key.strip())
    return keys


def _check_frontmatter(files: list[tuple[str, Path]], findings: Findings) -> None:
    for rel, path in files:
        first_part = rel.split("/")[0]
        if first_part in PLACEHOLDER_DIRS:
            continue
        if rel.endswith("/_INDEX.md"):
            continue
        keys = _frontmatter_fields(path.read_text(encoding="utf-8-sig"))
        if keys is None:
            findings.frontmatter.append(f"{rel}: missing frontmatter")
            continue
        required = FM_REQUIRED_BY_DIR.get(first_part, FM_DEFAULT)
        missing = [k for k in required if k not in keys]
        if missing:
            findings.frontmatter.append(f"{rel}: missing field(s) {', '.join(missing)}")


def _check_broken_links(
    vault: Path, files: list[tuple[str, Path]], findings: Findings
) -> set[str]:
    # Include _INDEX.md stems (they are valid [[...]] targets).
    all_stems = {p.stem for _, p in files}
    # Attachment targets: basename with extension present anywhere (pptx/jpg/csv).
    attachment_names = {s.name for s in vault.rglob("*") if s.is_file()}
    for rel, path in files:
        if rel.endswith("/_INDEX.md"):
            continue
        text = path.read_text(encoding="utf-8-sig")
        for m in LINK_RE.finditer(text):
            target = m.group(1).split("#", 1)[0].split("|", 1)[0].strip().rstrip("\\")
            if not target or target.endswith("/"):
                continue  # empty or directory link
            if target in PLACEHOLDER_TARGETS:
                continue  # placeholder with slash (e.g. 相关书籍/文章)
            last = target.split("/")[-1]
            if last in all_stems:
                continue
            if last in PLACEHOLDER_TARGETS:
                continue
            if "." in last and last in attachment_names:
                continue  # existing attachment (has extension)
            findings.broken_links.append(f"{rel}: broken link [[{target}]]")
    return all_stems


def _check_orphans(
    files: list[tuple[str, Path]], all_stems: set[str], findings: Findings
) -> None:
    if not all_stems:
        return
    link_text = "\n".join(
        p.read_text(encoding="utf-8-sig")
        for _, p in files
        if not _.endswith("/_INDEX.md")
    )
    # Build set of all basename references actually used as [[...]] targets.
    used = set()
    for m in LINK_RE.finditer(link_text):
        t = m.group(1).split("|", 1)[0].strip().rstrip("\\")
        used.add(t.split("#", 1)[0].split("/")[-1])
    for rel, _ in files:
        if not rel.startswith("4-Resources/"):
            continue
        if rel.endswith("/_INDEX.md"):
            continue
        if Path(rel).stem in used:
            continue
        findings.orphans.append(f"{rel}: no inbound wikilink")


def _check_duplicates(files: list[tuple[str, Path]], findings: Findings) -> None:
    seen: dict[str, list[str]] = defaultdict(list)
    for rel, _ in files:
        if rel.endswith("/_INDEX.md"):
            continue
        seen[Path(rel).stem].append(rel)
    for stem, paths in sorted(seen.items()):
        # Only flag basename collisions inside the same folder (genuine
        # duplicates); same-named READMEs across project subfolders are normal.
        by_dir: dict[str, list[str]] = {}
        for rel in paths:
            by_dir.setdefault(str(Path(rel).parent), []).append(rel)
        for rels in by_dir.values():
            if len(rels) > 1:
                findings.duplicates.append(
                    f"duplicate basename '{stem}' in same folder: {', '.join(rels)}"
                )


def _check_index_staleness(files: list[tuple[str, Path]], findings: Findings) -> None:
    by_rel = {rel: p for rel, p in files}
    for rel, path in by_rel.items():
        if not rel.endswith("/_INDEX.md"):
            continue
        folder = rel[: -len("_INDEX.md")]
        actual = sum(1 for r in by_rel if r.startswith(folder) and r != rel)
        # _INDEX files carry counts like "N 篇" / "日记总数 | N". The index is
        # current if any number in it matches the folder's real count (within 1).
        numbers = [
            int(n)
            for n in re.findall(r"(\d{1,5})\s*篇", path.read_text(encoding="utf-8-sig"))
        ]
        if numbers and not any(abs(actual - n) <= 1 for n in numbers):
            findings.index_stale.append(
                f"{rel}: expected ~{actual} notes, index counts {numbers}"
            )


def run_checks(vault: Path) -> Findings:
    findings = Findings()
    files = _md_files(vault)
    _check_frontmatter(files, findings)
    all_stems = _check_broken_links(vault, files, findings)
    _check_orphans(files, all_stems, findings)
    _check_duplicates(files, findings)
    _check_index_staleness(files, findings)
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="fixed vault path")
    parser.add_argument("--json", action="store_true", help="emit JSON report")
    args = parser.parse_args(argv)

    vault = Path(args.vault)
    validate_vault(vault)
    findings = run_checks(vault)

    if args.json:
        json.dump(
            {
                "vault": str(vault),
                "clean": findings.count() == 0,
                "frontmatter": findings.frontmatter,
                "broken_links": findings.broken_links,
                "orphans": findings.orphans,
                "duplicates": findings.duplicates,
                "index_stale": findings.index_stale,
            },
            sys.stdout,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        print()
    else:
        sections = [
            ("Frontmatter", findings.frontmatter),
            ("Broken links", findings.broken_links),
            ("Orphans", findings.orphans),
            ("Duplicates", findings.duplicates),
            ("INDEX stale", findings.index_stale),
        ]
        for title, items in sections:
            for item in items:
                print(f"{title}: {item}")
        print(
            f"Health {'clean' if findings.count() == 0 else 'issues'}: "
            f"{findings.count()} finding(s)"
        )
    return EXIT_OK if findings.count() == 0 else EXIT_FINDINGS


if __name__ == "__main__":
    raise SystemExit(main())
