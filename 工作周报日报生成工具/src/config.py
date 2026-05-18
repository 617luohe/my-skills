"""路径与仓库配置（不含密钥）。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LOG_DIR = ROOT / "log"
DATA_SOURCE_DIR = ROOT / "data" / "source"
DOCS_DIR = ROOT / "docs"

LAST_PULL_LOG = LOG_DIR / "gitee_last_pull.json"
WORK_CSV = DATA_SOURCE_DIR / "work_content.csv"

DEFAULT_REPOS = (
    {
        "owner": "luohe666",
        "repo": "mark_by_line",
        "project_label": "冷热集批排产-控制程序",
    },
    {
        "owner": "luohe666",
        "repo": "py_src_hot_rolling",
        "project_label": "冷热集批排产-算法程序",
    },
)

REPOS = DEFAULT_REPOS


def resolve_repos(
    repo_specs: list[str] | None,
    repos_file: Path | None,
    root: Path,
) -> tuple[dict[str, str], ...]:
    """CLI / Skill 覆盖仓库列表；均未提供时使用 DEFAULT_REPOS。"""
    if repos_file is not None:
        path = repos_file if repos_file.is_absolute() else (root / repos_file)
        if not path.is_file():
            raise ValueError(f"repos-file 不存在: {path}")
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("repos-file JSON 须为数组")
        out: list[dict[str, str]] = []
        for item in raw:
            if not isinstance(item, dict):
                raise ValueError("repos-file 中每项须为对象")
            owner = str(item.get("owner", "")).strip()
            repo = str(item.get("repo", "")).strip()
            label = str(item.get("project_label", "")).strip()
            if not owner or not repo or not label:
                raise ValueError("每项须含 owner、repo、project_label")
            out.append(
                {"owner": owner, "repo": repo, "project_label": label}
            )
        return tuple(out)

    if repo_specs:
        out = []
        for spec in repo_specs:
            parts = spec.split("::", 2)
            if len(parts) != 3:
                raise ValueError(
                    "--repo 格式须为 owner::repo::项目展示名（双冒号分隔，展示名可含空格）"
                )
            owner, repo, label = (p.strip() for p in parts)
            if not owner or not repo or not label:
                raise ValueError("--repo 三段均不可为空")
            out.append({"owner": owner, "repo": repo, "project_label": label})
        return tuple(out)

    return DEFAULT_REPOS
