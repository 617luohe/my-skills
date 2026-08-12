"""Regression tests for scripts/validate_skills.py governance rules."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_skills import validate_repository

MANIFEST = """schema_version: 1
repository_version: 1.0.0
skills:
  - name: good
    path: good
    category: standalone
    version: 1.0.0
    status: stable
    invocation: model
    hosts: [claude, cursor, codex]
    distribution: synchronized
    sync: true
    dependencies: []
  - name: bad
    path: bad
    category: standalone
    version: 1.0.0
    status: stable
    invocation: model
    hosts: [claude, cursor, codex]
    distribution: synchronized
    sync: true
    dependencies: []
"""

GOOD_SKILL = """---
name: good
disable-model-invocation: false
description: >
  多行块标量
  描述内容
---

# good

正文若干行。

- /Library/Caches 是 macOS 缓存目录，不应被当作技能引用
"""

GOOD_AGENTS = """interface:
  display_name: "Good"
policy:
  allow_implicit_invocation: true
"""

BAD_SKILL = """---
name: bad
disable-model-invocation: false
---

# bad

正文。
"""

BAD_AGENTS = """interface:
  display_name: "Bad"
policy:
  allow_implicit_invocation: false
"""


@pytest.fixture
def repo(tmp_path: Path):
    (tmp_path / "skills-manifest.yaml").write_text(MANIFEST, encoding="utf-8")
    (tmp_path / "good").mkdir()
    (tmp_path / "good" / "SKILL.md").write_text(GOOD_SKILL, encoding="utf-8")
    (tmp_path / "good" / "agents").mkdir()
    (tmp_path / "good" / "agents" / "openai.yaml").write_text(
        GOOD_AGENTS, encoding="utf-8"
    )
    (tmp_path / "bad").mkdir()
    (tmp_path / "bad" / "SKILL.md").write_text(BAD_SKILL, encoding="utf-8")
    (tmp_path / "bad" / "agents").mkdir()
    (tmp_path / "bad" / "agents" / "openai.yaml").write_text(
        BAD_AGENTS, encoding="utf-8"
    )
    return tmp_path


def test_good_skill_passes_block_scalar_and_path_exclusion(repo: Path):
    report = validate_repository(repo)
    good_errors = [e for e in report["errors"] if e["path"].endswith("good")]
    assert good_errors == [], good_errors


def test_implicit_false_against_disable_false_reports_parity(repo: Path):
    report = validate_repository(repo)
    parity = [e for e in report["errors"] if e["code"] == "invocation-parity"]
    assert len(parity) == 1, report["errors"]
    assert parity[0]["path"].endswith("bad/SKILL.md")


def test_manifest_user_against_disable_false_reports_parity(repo: Path):
    manifest = (repo / "skills-manifest.yaml").read_text(encoding="utf-8")
    manifest = manifest.replace(
        """    path: good
    category: standalone
    version: 1.0.0
    status: stable
    invocation: model""",
        """    path: good
    category: standalone
    version: 1.0.0
    status: stable
    invocation: user""",
    )
    (repo / "skills-manifest.yaml").write_text(manifest, encoding="utf-8")
    report = validate_repository(repo)
    parity = [e for e in report["errors"] if e["code"] == "invocation-parity"]
    assert any(e["path"].endswith("good/SKILL.md") for e in parity), report["errors"]


def test_deprecated_without_note_reports_manifest_error(repo: Path):
    manifest = (repo / "skills-manifest.yaml").read_text(encoding="utf-8")
    manifest = manifest.replace(
        """    path: good
    category: standalone
    version: 1.0.0
    status: stable""",
        """    path: good
    category: standalone
    version: 1.0.0
    status: deprecated""",
    )
    (repo / "skills-manifest.yaml").write_text(manifest, encoding="utf-8")
    report = validate_repository(repo)
    missing_note = [
        e
        for e in report["errors"]
        if e["code"] == "manifest" and "deprecated_note" in e["message"]
    ]
    assert len(missing_note) == 1, report["errors"]


def test_deprecated_with_note_requires_user_invocation(repo: Path):
    manifest = (repo / "skills-manifest.yaml").read_text(encoding="utf-8")
    manifest = manifest.replace(
        """    path: good
    category: standalone
    version: 1.0.0
    status: stable
    invocation: model""",
        """    path: good
    category: standalone
    version: 1.0.0
    status: deprecated
    deprecated_note: 迁移至 noteall 三阶段流水线
    invocation: model""",
    )
    (repo / "skills-manifest.yaml").write_text(manifest, encoding="utf-8")
    report = validate_repository(repo)
    assert any(
        e["code"] == "manifest" and "invocation user" in e["message"]
        for e in report["errors"]
    ), report["errors"]


def test_deprecated_with_note_passes(repo: Path):
    manifest = (repo / "skills-manifest.yaml").read_text(encoding="utf-8")
    manifest = manifest.replace(
        """    path: good
    version: 1.0.0
    status: stable
    invocation: model""",
        """    path: good
    version: 1.0.0
    status: deprecated
    deprecated_note: 迁移至 noteall 三阶段流水线
    invocation: user""",
    )
    (repo / "skills-manifest.yaml").write_text(manifest, encoding="utf-8")
    report = validate_repository(repo)
    good_errors = [e for e in report["errors"] if e["path"].endswith("good")]
    assert good_errors == [], good_errors


def test_declared_dependency_must_be_referenced(tmp_path: Path):
    manifest = """schema_version: 1
repository_version: 1.0.0
skills:
  - name: main
    path: main
    category: standalone
    version: 1.0.0
    status: stable
    invocation: model
    hosts: [claude, cursor, codex]
    distribution: synchronized
    sync: true
    dependencies: [vocabulary/dep]
  - name: vocabulary/dep
    path: vocabulary/dep
    category: vocabulary
    version: 1.0.0
    status: stable
    invocation: model
    hosts: [claude, cursor, codex]
    distribution: synchronized
    sync: true
    dependencies: []
"""
    (tmp_path / "skills-manifest.yaml").write_text(manifest, encoding="utf-8")
    (tmp_path / "main").mkdir()
    (tmp_path / "main" / "SKILL.md").write_text(
        "---\nname: main\ndisable-model-invocation: false\n---\n\n# main\n\n正文。\n",
        encoding="utf-8",
    )
    (tmp_path / "vocabulary").mkdir()
    (tmp_path / "vocabulary" / "dep").mkdir()
    (tmp_path / "vocabulary" / "dep" / "SKILL.md").write_text(
        "---\nname: dep\ndisable-model-invocation: false\n---\n\n# dep\n\n正文。\n",
        encoding="utf-8",
    )
    report = validate_repository(tmp_path)
    ref_errors = [e for e in report["errors"] if e["code"] == "dependency-reference"]
    assert len(ref_errors) == 1, report["errors"]
    assert "vocabulary/dep" in ref_errors[0]["message"]


def test_missing_description_reports_error(repo: Path):
    report = validate_repository(repo)
    desc_errors = [e for e in report["errors"] if e["code"] == "description"]
    assert len(desc_errors) == 1, report["errors"]
    assert desc_errors[0]["path"].endswith("bad/SKILL.md")


def test_short_description_reports_warning(tmp_path: Path):
    manifest = """schema_version: 1
repository_version: 1.0.0
skills:
  - name: terse
    path: terse
    category: standalone
    version: 1.0.0
    status: stable
    invocation: model
    hosts: [claude, cursor, codex]
    distribution: synchronized
    sync: true
    dependencies: []
"""
    (tmp_path / "skills-manifest.yaml").write_text(manifest, encoding="utf-8")
    (tmp_path / "terse").mkdir()
    (tmp_path / "terse" / "SKILL.md").write_text(
        "---\nname: terse\ndescription: 极简\ndisable-model-invocation: false\n---\n\n# terse\n\n正文。\n",
        encoding="utf-8",
    )
    report = validate_repository(tmp_path)
    short = [e for e in report["warnings"] if e["code"] == "description-short"]
    assert len(short) == 1, report["warnings"]
    assert short[0]["path"].endswith("terse/SKILL.md")


def test_deprecated_publication_is_user_only_with_note(tmp_path: Path):
    from skill_manifest import load_manifest, publication

    manifest = MANIFEST.replace(
        "    status: stable\n    invocation: model",
        "    status: deprecated\n    deprecated_note: use /good\n    invocation: model",
        1,
    )
    (tmp_path / "skills-manifest.yaml").write_text(manifest, encoding="utf-8")
    (tmp_path / "good").mkdir()
    (tmp_path / "good" / "SKILL.md").write_text("content", encoding="utf-8")
    (tmp_path / "bad").mkdir()
    (tmp_path / "bad" / "SKILL.md").write_text("content", encoding="utf-8")

    with pytest.raises(ValueError, match="deprecated.*invocation.*user"):
        publication(load_manifest(tmp_path / "skills-manifest.yaml"), tmp_path)

    manifest = manifest.replace("    invocation: model", "    invocation: user", 1)
    (tmp_path / "skills-manifest.yaml").write_text(manifest, encoding="utf-8")
    published = publication(load_manifest(tmp_path / "skills-manifest.yaml"), tmp_path)
    assert published["skills"][0]["status"] == "deprecated"
    assert published["skills"][0]["deprecated_note"] == "use /good"


def test_publication_flattens_nested_names_and_rejects_collisions(tmp_path: Path):
    from skill_manifest import load_manifest, publication

    def write_manifest(names: str) -> None:
        (tmp_path / "skills-manifest.yaml").write_text(
            "schema_version: 1\nrepository_version: 1.0.0\nskills:\n" + names,
            encoding="utf-8",
        )

    def entry(name: str) -> str:
        path = tmp_path / name
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text("content", encoding="utf-8")
        if name.startswith("vocabulary/"):
            category = "vocabulary"
        elif name.startswith("my-note/"):
            category = "my-note"
        else:
            category = "standalone"
        return (
            f"  - name: {name}\n    path: {name}\n    category: {category}\n"
            f"    version: 1.0.0\n    status: stable\n    invocation: model\n"
            f"    hosts: [claude, cursor, codex]\n    distribution: synchronized\n"
            f"    sync: true\n    dependencies: []\n"
        )

    write_manifest(entry("vocabulary/code-review") + entry("my-note/noteall"))
    result = publication(load_manifest(tmp_path / "skills-manifest.yaml"), tmp_path)
    assert [skill["deployment_name"] for skill in result["skills"]] == [
        "code-review",
        "noteall",
    ]

    write_manifest(entry("vocabulary/code-review") + entry("other/code-review"))
    with pytest.raises(ValueError, match="deployment name collision"):
        publication(load_manifest(tmp_path / "skills-manifest.yaml"), tmp_path)


def test_user_only_body_requires_user_invocation(tmp_path: Path):
    manifest = """schema_version: 1
repository_version: 1.0.0
skills:
  - name: user-skill
    path: user-skill
    category: standalone
    version: 1.0.0
    status: stable
    invocation: model
    hosts: [claude, cursor, codex]
    distribution: synchronized
    sync: true
    dependencies: []
"""
    (tmp_path / "skills-manifest.yaml").write_text(manifest, encoding="utf-8")
    (tmp_path / "user-skill").mkdir()
    (tmp_path / "user-skill" / "SKILL.md").write_text(
        "---\nname: user-skill\ndescription: test user only skill\ndisable-model-invocation: false\n---\n\n仅可由用户显式调用。\n",
        encoding="utf-8",
    )
    (tmp_path / "user-skill" / "agents").mkdir()
    (tmp_path / "user-skill" / "agents" / "openai.yaml").write_text(
        "interface:\n  display_name: test\npolicy:\n  allow_implicit_invocation: true\n",
        encoding="utf-8",
    )
    report = validate_repository(tmp_path)
    semantic = [e for e in report["errors"] if e["code"] == "invocation-semantic"]
    assert len(semantic) == 1, report["errors"]


def test_claude_mirror_detects_missing_support_skill(tmp_path: Path):
    manifest = """schema_version: 1
repository_version: 1.0.0
skills:
  - name: 0-询问luohe
    path: 0-询问luohe
    category: router
    version: 1.0.0
    status: stable
    invocation: model
    hosts: [claude, cursor, codex]
    distribution: synchronized
    sync: true
    dependencies: []
"""
    (tmp_path / "skills-manifest.yaml").write_text(manifest, encoding="utf-8")
    router = tmp_path / "0-询问luohe"
    router.mkdir()
    (router / "SKILL.md").write_text(
        "---\nname: 0-询问luohe\ndescription: router test\ndisable-model-invocation: false\n---\n\n| x | `/1-规划` |\n",
        encoding="utf-8",
    )
    claude = tmp_path / "CLAUDE.md"
    claude.write_text(
        "## 支撑层\n\n| 信号 | 技能 |\n| --- | --- |\n| 探索 | `/0--explore` |\n",
        encoding="utf-8",
    )
    report = validate_repository(
        tmp_path, check_claude_mirror=True, claude_path=claude
    )
    mirror = [e for e in report["errors"] if e["code"] == "claude-mirror"]
    assert len(mirror) == 1
    assert "0--explore" in mirror[0]["message"]
