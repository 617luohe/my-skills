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
# Directories excluded from the default "content" orphan scope.
CONTENT_EXCLUDED_DIRS = {"5-Journal", "8-Templates", "9-System"}
# Directories whose notes form the concept subnet for metrics.
CONCEPT_DIRS = {"4-Resources", "7-Sources", "1-Atlas"}

# Legal enum values (single source of truth for frontmatter compliance).
CONFIDENCE_ENUM = {"seed", "sapling", "evergreen"}
STATUS_ENUM = {"draft", "published", "archived"}

ORPHAN_SCOPES = ("all", "content", "4-Resources")

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

# Substrings that mark a frontmatter finding as a structural violation
# (illegal enum/format value, or a required field missing), as opposed to a
# missing-frontmatter report. publish_vault's quality gate blocks structural
# findings only.
STRUCTURAL_MARKERS = (
    "illegal value",
    "type/ prefix",
    "title empty",
    "missing field(s)",
)


def is_structural_finding(item: str) -> bool:
    """True if a frontmatter finding is a structural (enum/format/missing-required) violation."""
    return any(m in item for m in STRUCTURAL_MARKERS)


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


def _strip_quotes(value: str) -> str:
    """Strip a pair of matching single/double quotes around a scalar value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _frontmatter_fields(text: str) -> dict[str, str | list[str]] | None:
    """Parse the top-level frontmatter block into a {key: value} dict.

    Supports the YAML subset used by this vault (stdlib-only, no PyYAML):
    ``key: value`` scalars, ``key: [a, b]`` inline lists, ``key:`` followed by
    ``  - item`` block lists, and single/double-quoted value stripping. Returns
    None if the file has no frontmatter block.
    """
    if not text.lstrip().startswith("---"):
        return None
    lines = text.lstrip().splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None
    fields: dict[str, str | list[str]] = {}
    current: str | None = None  # key awaiting a block list
    for line in lines[1:end]:
        if not line.strip():
            current = None
            continue
        stripped = line.lstrip()
        if stripped.startswith("-") and current is not None:
            item = _strip_quotes(stripped[1:].strip())
            existing = fields[current]
            if isinstance(existing, str):
                fields[current] = [item]
            else:
                existing.append(item)
            continue
        current = None
        if ":" not in line:
            continue  # ignore malformed lines
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        if not key:
            continue
        if rest.startswith("[") and rest.endswith("]"):
            items = [
                _strip_quotes(i.strip())
                for i in rest.strip("[]").split(",")
                if i.strip()
            ]
            fields[key] = items
        elif rest == "":
            fields[key] = ""
            current = key
        else:
            fields[key] = _strip_quotes(rest)
    return fields


def _check_enum_compliance(
    rel: str, first_part: str, fields: dict[str, str | list[str]], findings: Findings
) -> None:
    """Validate enum/format values for fields that are present.

    Missing keys are reported by _check_frontmatter; this only flags values
    that exist but violate the legal enum or expected format.
    """
    required = FM_REQUIRED_BY_DIR.get(first_part, FM_DEFAULT)
    if "confidence" in fields:
        val = fields["confidence"]
        if not (isinstance(val, str) and val in CONFIDENCE_ENUM):
            val_s = val if isinstance(val, str) else repr(val)
            findings.frontmatter.append(
                f"{rel}: confidence illegal value '{val_s}' (expected seed/sapling/evergreen)"
            )
    if "status" in fields:
        val = fields["status"]
        if not (isinstance(val, str) and val in STATUS_ENUM):
            val_s = val if isinstance(val, str) else repr(val)
            findings.frontmatter.append(
                f"{rel}: status illegal value '{val_s}' (expected draft/published/archived)"
            )
    if "source" in fields:
        val = fields["source"]
        if not (isinstance(val, str) and val.startswith("[[") and val.endswith("]]")):
            val_s = val if isinstance(val, str) else repr(val)
            findings.frontmatter.append(
                f"{rel}: source illegal value '{val_s}' (expected [[wikilink]])"
            )
    if "tags" in fields and "tags" in required:
        tags = fields["tags"]
        if isinstance(tags, str):
            tags = [tags]
        if not any(isinstance(t, str) and t.startswith("type/") for t in tags):
            findings.frontmatter.append(f"{rel}: tags missing type/ prefix tag")
    if "title" in fields and "title" in required:
        val = fields["title"]
        if not (isinstance(val, str) and val.strip()):
            findings.frontmatter.append(f"{rel}: title empty (expected non-empty)")


def _check_frontmatter(files: list[tuple[str, Path]], findings: Findings) -> None:
    for rel, path in files:
        first_part = rel.split("/")[0]
        if first_part in PLACEHOLDER_DIRS:
            continue
        if rel.endswith("/_INDEX.md"):
            continue
        fields = _frontmatter_fields(path.read_text(encoding="utf-8-sig"))
        if fields is None:
            findings.frontmatter.append(f"{rel}: missing frontmatter")
            continue
        required = FM_REQUIRED_BY_DIR.get(first_part, FM_DEFAULT)
        missing = [k for k in required if k not in fields]
        if missing:
            findings.frontmatter.append(f"{rel}: missing field(s) {', '.join(missing)}")
        _check_enum_compliance(rel, first_part, fields, findings)


def _check_broken_links(
    vault: Path,
    files: list[tuple[str, Path]],
    findings: Findings,
    files_subset: list[tuple[str, Path]] | None = None,
) -> set[str]:
    # Include _INDEX.md stems (they are valid [[...]] targets).
    all_stems = {p.stem for _, p in files}
    # Attachment targets: basename with extension present anywhere (pptx/jpg/csv).
    attachment_names = {s.name for s in vault.rglob("*") if s.is_file()}
    checked = files if files_subset is None else files_subset
    for rel, path in checked:
        if rel.endswith("/_INDEX.md"):
            continue
        text = path.read_text(encoding="utf-8-sig")
        for m in LINK_RE.finditer(text):
            target = m.group(1).split("#", 1)[0].split("|", 1)[0].strip()
            if not target or target.endswith("/"):
                continue  # empty or directory link
            if "\\" in target:
                # Backslash is not a valid wikilink separator in Obsidian.
                findings.broken_links.append(f"{rel}: backslash link [[{target}]]")
                continue
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


def _wikilink_graph(
    files: list[tuple[str, Path]],
) -> tuple[dict[str, set[str]], set[str]]:
    """Build the undirected wikilink graph over note stems.

    Returns (adj, used): adj maps a stem to its neighbor stems (edges only
    between existing notes, self-loops excluded); used is the set of basenames
    referenced by any [[...]] target (existing or not).
    """
    stems = {p.stem for _, p in files}
    adj: dict[str, set[str]] = defaultdict(set)
    used: set[str] = set()
    for rel, path in files:
        src = Path(rel).stem
        for m in LINK_RE.finditer(path.read_text(encoding="utf-8-sig")):
            t = m.group(1).split("|", 1)[0].strip().split("#", 1)[0]
            if not t or t.endswith("/"):
                continue
            last = t.split("/")[-1]
            used.add(last)
            if last in stems and last != src:
                adj[src].add(last)
                adj[last].add(src)
    return adj, used


def _check_orphans(
    files: list[tuple[str, Path]],
    adj: dict[str, set[str]],
    used: set[str],
    findings: Findings,
    scope: str = "content",
) -> None:
    if not files:
        return
    for rel, _ in files:
        if rel.endswith("/_INDEX.md"):
            continue
        first = rel.split("/")[0]
        if scope == "content" and first in CONTENT_EXCLUDED_DIRS:
            continue
        if scope == "4-Resources" and first != "4-Resources":
            continue
        stem = Path(rel).stem
        if scope == "4-Resources":
            # Legacy 4-Resources scope: only inbound references matter.
            if stem in used:
                continue
            findings.orphans.append(f"{rel}: no inbound wikilink")
            continue
        # all/content: fully isolated = no inbound AND no outbound edge.
        if stem in used or stem in adj:
            continue
        findings.orphans.append(
            f"{rel}: no inbound wikilink and no outbound wikilink (fully isolated)"
        )


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


def _matches_paths(rel: str, paths_filter: set[str]) -> bool:
    for p in paths_filter:
        p = p.replace("\\", "/").strip("/")
        if rel == p or rel.startswith(p + "/"):
            return True
    return False


def run_checks(
    vault: Path,
    orphan_scope: str = "content",
    paths_filter: set[str] | None = None,
) -> Findings:
    findings = Findings()
    all_files = _md_files(vault)
    files = all_files
    if paths_filter is not None:
        files = [f for f in all_files if _matches_paths(f[0], paths_filter)]
    _check_frontmatter(files, findings)
    _check_broken_links(
        vault, all_files, findings, files if paths_filter is not None else None
    )
    adj, used = _wikilink_graph(all_files)
    _check_orphans(files, adj, used, findings, orphan_scope)
    _check_duplicates(files, findings)
    _check_index_staleness(files, findings)
    return findings


def compute_metrics(vault: Path) -> dict:
    """Quantitative graph metrics for the fixed vault.

    Stable metric definitions (do not change without updating tests):
    - notes:     number of scanned .md files (same set as run_checks)
    - edges:     unique undirected wikilink edges between existing note stems
    - orphan_rate:   fully isolated notes / notes; fully isolated = no inbound
      AND no outbound reference (self-links do not count), consistent with the
      orphan check in all/content scope
    - linked_rate:   notes with at least one incident edge / notes
    - components_ge2: connected components with >= 2 nodes (nodes with edges only)
    - lcc_share:     largest component size / notes (denominator is total notes)
    - concept_subnet_density: density 2E/(n(n-1)) of the concept subnet
      (4-Resources/7-Sources/1-Atlas notes, excluding _INDEX)
    - broken_links:  per-link broken/backslash link findings count
    - schema_enums:  observed confidence/status values across notes plus
      illegal_count (notes with a value outside the legal enum)
    """
    files = _md_files(vault)
    notes = len(files)
    adj, used = _wikilink_graph(files)
    isolated = sum(
        1 for _, p in files if Path(p).stem not in adj and Path(p).stem not in used
    )
    linked = notes - isolated
    # Connected components over nodes that have at least one edge.
    seen: set[str] = set()
    sizes: list[int] = []
    for node in list(adj):
        if node in seen:
            continue
        stack = [node]
        size = 0
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            size += 1
            stack.extend(adj[n] - seen)
        sizes.append(size)
    concept_nodes = {
        Path(rel).stem
        for rel, _ in files
        if rel.split("/")[0] in CONCEPT_DIRS and not rel.endswith("/_INDEX.md")
    }
    concept_edges = sum(
        1 for a, b in _edges_from(adj) if a in concept_nodes and b in concept_nodes
    )
    cn = len(concept_nodes)
    density = 0.0
    if cn > 1:
        density = (2 * concept_edges) / (cn * (cn - 1))
    broken = Findings()
    _check_broken_links(vault, files, broken)
    conf_obs: set[str] = set()
    status_obs: set[str] = set()
    illegal = 0
    for rel, path in files:
        if rel.endswith("/_INDEX.md") or rel.split("/")[0] in PLACEHOLDER_DIRS:
            continue
        fields = _frontmatter_fields(path.read_text(encoding="utf-8-sig"))
        if fields is None:
            continue
        bad = False
        if "confidence" in fields and isinstance(fields["confidence"], str):
            conf_obs.add(fields["confidence"])
            if fields["confidence"] not in CONFIDENCE_ENUM:
                bad = True
        if "status" in fields and isinstance(fields["status"], str):
            status_obs.add(fields["status"])
            if fields["status"] not in STATUS_ENUM:
                bad = True
        if bad:
            illegal += 1
    return {
        "notes": notes,
        "edges": len(_edges_from(adj)),
        "orphan_rate": round(isolated / notes, 4) if notes else 0.0,
        "linked_rate": round(linked / notes, 4) if notes else 0.0,
        "components_ge2": sum(1 for s in sizes if s >= 2),
        "lcc_share": round(max(sizes, default=0) / notes, 4) if notes else 0.0,
        "concept_subnet_density": round(density, 6),
        "broken_links": len(broken.broken_links),
        "schema_enums": {
            "confidence": sorted(conf_obs),
            "status": sorted(status_obs),
            "illegal_count": illegal,
        },
    }


def _edges_from(adj: dict[str, set[str]]) -> set[tuple[str, str]]:
    edges: set[tuple[str, str]] = set()
    for a, neighbors in adj.items():
        for b in neighbors:
            edges.add(tuple(sorted((a, b))))
    return edges


def main(argv: list[str] | None = None) -> int:
    # Windows GBK console cannot encode emoji/Chinese paths in JSON output;
    # force UTF-8 for this process's own streams. Done in main() only, not at
    # module import, so importing this module (e.g. publish_vault) has no
    # side effect on the importer's stream encodings.
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="fixed vault path")
    parser.add_argument("--json", action="store_true", help="emit JSON report")
    parser.add_argument(
        "--metrics", action="store_true", help="emit graph metrics JSON"
    )
    parser.add_argument(
        "--orphan-scope",
        choices=ORPHAN_SCOPES,
        default="content",
        help="orphan check scope (default: content)",
    )
    parser.add_argument(
        "--paths", nargs="*", default=None, help="restrict checks to these rel paths"
    )
    args = parser.parse_args(argv)

    vault = Path(args.vault)
    validate_vault(vault)
    paths_filter = set(args.paths) if args.paths else None
    findings = run_checks(
        vault, orphan_scope=args.orphan_scope, paths_filter=paths_filter
    )

    report = {
        "vault": str(vault),
        "clean": findings.count() == 0,
        "frontmatter": findings.frontmatter,
        "broken_links": findings.broken_links,
        "orphans": findings.orphans,
        "duplicates": findings.duplicates,
        "index_stale": findings.index_stale,
    }
    metrics = compute_metrics(vault) if args.metrics else None

    if args.json and args.metrics:
        json.dump(
            {"findings": report, "metrics": metrics},
            sys.stdout,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        print()
    elif args.json:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
        print()
    elif args.metrics:
        json.dump(metrics, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
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
    if args.metrics and not args.json:
        # metrics-only mode: the JSON metrics output is the deliverable; exit
        # code reflects metric production, not findings severity.
        return EXIT_OK
    return EXIT_OK if findings.count() == 0 else EXIT_FINDINGS


if __name__ == "__main__":
    raise SystemExit(main())
