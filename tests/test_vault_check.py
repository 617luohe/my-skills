"""Black-box tests for vault-publisher/vault_check.py using temp vaults."""

from __future__ import annotations

import json
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
    / "vault_check.py"
)

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_PRECONDITION = 2


def run_script(vault: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--vault", str(vault), *extra],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    (tmp_path / ".obsidian").mkdir()
    return tmp_path


def write(vault: Path, rel: str, content: str) -> Path:
    p = vault / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def test_invalid_vault_exits_precondition(tmp_path: Path) -> None:
    result = run_script(tmp_path)
    assert result.returncode == EXIT_PRECONDITION


def test_clean_vault_exits_ok(vault: Path) -> None:
    # Use 7-Sources (no orphan check there) for a clean, self-contained note.
    write(
        vault,
        "7-Sources/技术工具/原子笔记.md",
        "---\ntitle: 原子笔记\ntags:\n  - type/source\n  - domain/tech\nstatus: draft\nconfidence: seed\n---\n\n# 原子笔记\n\n> 定义。\n",
    )
    result = run_script(vault)
    assert result.returncode == EXIT_OK, result.stdout


def test_missing_frontmatter_is_found(vault: Path) -> None:
    write(vault, "7-Sources/生活/无元数据.md", "# 无元数据\n\n内容。\n")
    result = run_script(vault)
    assert result.returncode == EXIT_FINDINGS
    assert "missing frontmatter" in result.stdout


def test_missing_confidence_is_found(vault: Path) -> None:
    write(
        vault,
        "4-Resources/tech/缺置信度.md",
        "---\ntitle: 缺置信度\ntags:\n  - type/resource\n  - domain/tech\nstatus: draft\n---\n\n# 缺置信度\n",
    )
    result = run_script(vault)
    assert "missing field(s) confidence" in result.stdout


def test_broken_link_is_found(vault: Path) -> None:
    write(
        vault,
        "4-Resources/tech/来源.md",
        "---\ntags:\n  - type/resource\n  - domain/tech\nstatus: draft\nconfidence: seed\n---\n\n[[不存在的概念]]\n",
    )
    result = run_script(vault)
    assert "broken link [[不存在的概念]]" in result.stdout


def test_attachment_link_not_broken(vault: Path) -> None:
    write(
        vault,
        "7-Sources/生活/带附件.md",
        "---\ntitle: 带附件\ntags:\n  - type/source\n  - domain/life\nstatus: draft\nconfidence: seed\n---\n\n[[截图.jpg]]\n",
    )
    (vault / "assets").mkdir()
    (vault / "assets" / "截图.jpg").write_bytes(b"\x89PNG")
    result = run_script(vault)
    assert result.returncode == EXIT_OK, result.stdout


def test_orphan_is_found(vault: Path) -> None:
    write(
        vault,
        "4-Resources/tech/孤儿笔记.md",
        "---\ntags:\n  - type/resource\n  - domain/tech\nstatus: draft\nconfidence: seed\n---\n\n# 孤儿\n",
    )
    result = run_script(vault)
    assert "no inbound wikilink" in result.stdout


def test_json_report(vault: Path) -> None:
    write(
        vault,
        "7-Sources/技术工具/合规笔记.md",
        "---\ntitle: 合规笔记\ntags:\n  - type/source\n  - domain/tech\nstatus: draft\nconfidence: seed\n---\n\n# 合规\n",
    )
    result = run_script(vault, "--json")
    report = json.loads(result.stdout)
    assert report["clean"] is True
    assert "vault" in report
