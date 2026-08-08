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

# Unit tests import the module directly (T001 parser tests); black-box tests
# exercise the CLI via subprocess.
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))
import vault_check as vc  # noqa: E402

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
    # A well-formed note with a self-reference is not an orphan under the
    # default content scope (7-Sources is checked since T004).
    write(
        vault,
        "7-Sources/技术工具/原子笔记.md",
        "---\ntitle: 原子笔记\ntags:\n  - type/source\n  - domain/tech\nstatus: draft\nconfidence: seed\n---\n\n# 原子笔记\n\n> 定义。\n\n[[原子笔记]]\n",
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
        "---\ntitle: 带附件\ntags:\n  - type/source\n  - domain/life\nstatus: draft\nconfidence: seed\n---\n\n[[截图.jpg]]\n\n[[带附件]]\n",
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
        "---\ntitle: 合规笔记\ntags:\n  - type/source\n  - domain/tech\nstatus: draft\nconfidence: seed\n---\n\n# 合规\n\n[[合规笔记]]\n",
    )
    result = run_script(vault, "--json")
    report = json.loads(result.stdout)
    assert report["clean"] is True
    assert "vault" in report


# ---------------------------------------------------------------------------
# T001: structured frontmatter parsing
# ---------------------------------------------------------------------------


def test_fm_parses_block_list() -> None:
    fields = vc._frontmatter_fields(
        "---\ntags:\n  - type/source\n  - domain/tech\nstatus: draft\n---\n"
    )
    assert fields == {"tags": ["type/source", "domain/tech"], "status": "draft"}


def test_fm_parses_inline_list() -> None:
    fields = vc._frontmatter_fields("---\ntags: [type/source, domain/tech]\n---\n")
    assert fields == {"tags": ["type/source", "domain/tech"]}


def test_fm_strips_quotes() -> None:
    fields = vc._frontmatter_fields(
        "---\nsource: \"[[Vegas 交易系统（罗晟）]]\"\ntitle: '原子笔记'\n---\n"
    )
    assert fields["source"] == "[[Vegas 交易系统（罗晟）]]"
    assert fields["title"] == "原子笔记"


def test_fm_none_without_block() -> None:
    assert vc._frontmatter_fields("# 无 frontmatter\n") is None
    assert vc._frontmatter_fields("---\nnever closed\n") is None


# ---------------------------------------------------------------------------
# T002: enum/format compliance
# ---------------------------------------------------------------------------


def _src_fm(tail: str) -> str:
    return (
        "---\ntitle: x\ntags:\n  - type/source\n  - domain/tech\n"
        "status: draft\nconfidence: seed\n---\n\n# x\n" + tail
    )


def test_illegal_confidence_value_is_found(vault: Path) -> None:
    write(
        vault,
        "7-Sources/tech/坏置信度.md",
        "---\ntitle: 坏置信度\ntags:\n  - type/source\nstatus: draft\nconfidence: budding\n---\n\n# x\n",
    )
    result = run_script(vault)
    assert (
        "confidence illegal value 'budding' (expected seed/sapling/evergreen)"
        in result.stdout
    )


def test_legal_confidence_values_not_flagged(vault: Path) -> None:
    for i, val in enumerate(("seed", "sapling", "evergreen")):
        write(
            vault,
            f"7-Sources/tech/合法{i}.md",
            _src_fm(f"\n[[合法{i}]]\n").replace(
                "confidence: seed", f"confidence: {val}"
            ),
        )
    result = run_script(vault)
    assert "confidence illegal value" not in result.stdout


def test_illegal_status_value_is_found(vault: Path) -> None:
    write(
        vault,
        "7-Sources/tech/坏状态.md",
        "---\ntitle: 坏状态\ntags:\n  - type/source\nstatus: active\nconfidence: seed\n---\n\n# x\n",
    )
    result = run_script(vault)
    assert (
        "status illegal value 'active' (expected draft/published/archived)"
        in result.stdout
    )


def test_illegal_source_value_is_found(vault: Path) -> None:
    write(
        vault,
        "7-Sources/tech/坏来源.md",
        "---\ntitle: 坏来源\ntags:\n  - type/source\nstatus: draft\nconfidence: seed\nsource: https://example.com/note\n---\n\n# x\n",
    )
    result = run_script(vault)
    assert (
        "source illegal value 'https://example.com/note' (expected [[wikilink]])"
        in result.stdout
    )


def test_empty_source_is_illegal(vault: Path) -> None:
    write(
        vault,
        "7-Sources/tech/空来源.md",
        "---\ntitle: 空来源\ntags:\n  - type/source\nstatus: draft\nconfidence: seed\nsource:\n---\n\n# x\n",
    )
    result = run_script(vault)
    assert "source illegal value '' (expected [[wikilink]])" in result.stdout


def test_wikilink_source_ok(vault: Path) -> None:
    write(
        vault,
        "7-Sources/tech/好来源.md",
        '---\ntitle: 好来源\ntags:\n  - type/source\nstatus: draft\nconfidence: seed\nsource: "[[被引用]]"\n---\n\n# x\n\n[[被引用]]\n',
    )
    write(vault, "7-Sources/tech/被引用.md", _src_fm("\n[[好来源]]\n"))
    result = run_script(vault)
    assert "source illegal value" not in result.stdout
    assert result.returncode == EXIT_OK, result.stdout


def test_tags_missing_type_prefix_is_found(vault: Path) -> None:
    write(
        vault,
        "7-Sources/tech/无类型标签.md",
        "---\ntitle: 无类型标签\ntags:\n  - domain/tech\nstatus: draft\nconfidence: seed\n---\n\n# x\n",
    )
    result = run_script(vault)
    assert "tags missing type/ prefix tag" in result.stdout


def test_title_empty_is_found(vault: Path) -> None:
    write(
        vault,
        "5-Journal/daily/2025-07-01.md",
        '---\ntitle: ""\ntags:\n  - type/journal\n---\n\n# x\n',
    )
    result = run_script(vault)
    assert "title empty (expected non-empty)" in result.stdout


def test_legal_file_not_misreported(vault: Path) -> None:
    write(vault, "7-Sources/tech/完全合规.md", _src_fm("\n[[完全合规]]\n"))
    result = run_script(vault)
    assert result.returncode == EXIT_OK, result.stdout


# ---------------------------------------------------------------------------
# T003: backslash path detection
# ---------------------------------------------------------------------------


def test_backslash_link_is_found(vault: Path) -> None:
    write(
        vault,
        "4-Resources/tech/来源.md",
        "---\ntags:\n  - type/resource\nstatus: draft\nconfidence: seed\n---\n\n"
        "[[7-Sources/热轧排程项目/01-快速入口/README\\]]\n",
    )
    result = run_script(vault)
    assert (
        "backslash link [[7-Sources/热轧排程项目/01-快速入口/README\\]]"
        in result.stdout
    )


def test_forward_slash_link_not_flagged(vault: Path) -> None:
    write(vault, "7-Sources/tech/A.md", _src_fm("\n[[B]]\n"))
    write(vault, "7-Sources/tech/B.md", _src_fm("\n[[A]]\n"))
    result = run_script(vault)
    assert result.returncode == EXIT_OK, result.stdout
    assert "backslash link" not in result.stdout


# ---------------------------------------------------------------------------
# T004: orphan scope parameterization
# ---------------------------------------------------------------------------


def _write_orphan_notes(vault: Path) -> None:
    write(
        vault,
        "5-Journal/daily/2025-07-01.md",
        "---\ntitle: 日记\ntags:\n  - type/journal\n---\n\n# 日记\n",
    )
    write(
        vault,
        "7-Sources/tech/孤a.md",
        "---\ntitle: 孤a\ntags:\n  - type/source\nstatus: draft\nconfidence: seed\n---\n\n# 孤a\n",
    )
    write(
        vault,
        "4-Resources/tech/孤b.md",
        "---\ntags:\n  - type/resource\nstatus: draft\nconfidence: seed\n---\n\n# 孤b\n",
    )


def test_orphan_scope_all(vault: Path) -> None:
    _write_orphan_notes(vault)
    report = json.loads(run_script(vault, "--orphan-scope", "all", "--json").stdout)
    orphans = {o.split(":")[0] for o in report["orphans"]}
    assert orphans == {
        "5-Journal/daily/2025-07-01.md",
        "7-Sources/tech/孤a.md",
        "4-Resources/tech/孤b.md",
    }


def test_orphan_scope_content_is_default(vault: Path) -> None:
    _write_orphan_notes(vault)
    report = json.loads(run_script(vault, "--json").stdout)
    orphans = {o.split(":")[0] for o in report["orphans"]}
    assert orphans == {"7-Sources/tech/孤a.md", "4-Resources/tech/孤b.md"}


def test_orphan_scope_4_resources(vault: Path) -> None:
    _write_orphan_notes(vault)
    report = json.loads(
        run_script(vault, "--orphan-scope", "4-Resources", "--json").stdout
    )
    orphans = {o.split(":")[0] for o in report["orphans"]}
    assert orphans == {"4-Resources/tech/孤b.md"}


def test_note_with_outbound_link_not_orphan(vault: Path) -> None:
    # A links to existing B: has outbound edge -> not fully isolated.
    write(vault, "7-Sources/tech/A.md", _src_fm("\n[[B]]\n"))
    write(vault, "7-Sources/tech/B.md", _src_fm("\n[[B]]\n"))
    report = json.loads(run_script(vault, "--orphan-scope", "all", "--json").stdout)
    orphans = {o.split(":")[0] for o in report["orphans"]}
    assert "7-Sources/tech/A.md" not in orphans


# ---------------------------------------------------------------------------
# T005: --metrics
# ---------------------------------------------------------------------------


def _write_metric_vault(vault: Path) -> None:
    # a-b-c connected (7-Sources), d-e connected (1-Atlas), f isolated
    # (5-Journal), g links only to a broken target.
    write(vault, "7-Sources/a.md", _src_fm("\n[[b]]\n").replace("seed", "sprout"))
    write(vault, "7-Sources/b.md", _src_fm("\n[[c]]\n"))
    write(vault, "7-Sources/c.md", _src_fm("\n"))
    write(
        vault,
        "1-Atlas/d.md",
        "---\ntags:\n  - type/atlas\n---\n\n# d\n\n[[e]]\n",
    )
    write(vault, "1-Atlas/e.md", "---\ntags:\n  - type/atlas\n---\n\n# e\n")
    write(
        vault,
        "5-Journal/f.md",
        "---\ntitle: f\ntags:\n  - type/journal\n---\n\n# f\n",
    )
    write(vault, "0-Inbox/g.md", "# g\n\n[[不存在]]\n")


def test_metrics_json(vault: Path) -> None:
    _write_metric_vault(vault)
    metrics = json.loads(run_script(vault, "--metrics").stdout)
    assert metrics["notes"] == 7
    assert metrics["edges"] == 3
    assert metrics["orphan_rate"] == 0.2857
    assert metrics["linked_rate"] == 0.7143
    assert metrics["components_ge2"] == 2
    assert metrics["lcc_share"] == 0.4286
    assert metrics["concept_subnet_density"] == 0.3
    assert metrics["broken_links"] == 1
    assert metrics["schema_enums"]["confidence"] == ["seed", "sprout"]
    assert metrics["schema_enums"]["status"] == ["draft"]
    assert metrics["schema_enums"]["illegal_count"] == 1


def test_metrics_with_json_are_composable(vault: Path) -> None:
    _write_metric_vault(vault)
    payload = json.loads(run_script(vault, "--metrics", "--json").stdout)
    assert set(payload) == {"findings", "metrics"}
    assert payload["metrics"]["notes"] == 7
    assert "frontmatter" in payload["findings"]


def test_metrics_only_exits_zero(vault: Path) -> None:
    # metrics-only mode returns 0: the JSON metrics output is the deliverable,
    # regardless of findings severity.
    _write_metric_vault(vault)
    result = run_script(vault, "--metrics")
    assert result.returncode == EXIT_OK, result.stderr
    assert json.loads(result.stdout)["notes"] == 7


def test_json_emoji_filename_no_crash(vault: Path) -> None:
    # Windows GBK console cannot encode emoji filenames (🏠 知识库入口). --json
    # must not crash: stdout is force-reconfigured to UTF-8 in main(). Drop
    # PYTHONIOENCODING to simulate the native console encoding path.
    write(vault, "7-Sources/🏠 知识库入口.md", _src_fm("\n[[emoji]]\n"))
    write(vault, "7-Sources/emoji.md", _src_fm("\n[[🏠 知识库入口]]\n"))
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--vault", str(vault), "--json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    assert result.returncode == EXIT_OK, result.stderr
    report = json.loads(result.stdout)
    assert "vault" in report
