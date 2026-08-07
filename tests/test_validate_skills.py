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
    version: 1.0.0
    status: stable
    invocation: model
    hosts: [claude]
    distribution: synchronized
    sync: true
    dependencies: []
  - name: bad
    path: bad
    version: 1.0.0
    status: stable
    invocation: model
    hosts: [claude]
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
    version: 1.0.0
    status: stable
    invocation: model""",
        """    path: good
    version: 1.0.0
    status: stable
    invocation: user""",
    )
    (repo / "skills-manifest.yaml").write_text(manifest, encoding="utf-8")
    report = validate_repository(repo)
    parity = [e for e in report["errors"] if e["code"] == "invocation-parity"]
    assert any(e["path"].endswith("good/SKILL.md") for e in parity), report["errors"]
