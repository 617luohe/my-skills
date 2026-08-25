"""Regression tests for scripts/validate_skills.py governance rules."""

from __future__ import annotations

import json
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


def _write_governance_repo(
    root: Path, skills: list[dict[str, object]], version: str = "1.0.0"
) -> None:
    manifest_lines = [
        "schema_version: 1",
        f"repository_version: {version}",
        "skills:",
    ]
    for skill in skills:
        name = str(skill["name"])
        dependencies = [str(dep) for dep in skill.get("dependencies", [])]
        status = str(skill.get("status", "stable"))
        invocation = str(
            skill.get("invocation", "user" if status == "deprecated" else "model")
        )
        distribution = str(skill.get("distribution", "synchronized"))
        category = (
            "vocabulary"
            if name.startswith("vocabulary/")
            else "my-note"
            if name.startswith("my-note/")
            else "standalone"
        )
        manifest_lines.extend(
            [
                f"  - name: {name}",
                f"    path: {name}",
                f"    category: {category}",
                f"    version: {version}",
                f"    status: {status}",
            ]
        )
        if status == "deprecated":
            manifest_lines.append("    deprecated_note: replaced")
        manifest_lines.extend(
            [
                f"    invocation: {invocation}",
                "    hosts: [claude, cursor, codex]",
                f"    distribution: {distribution}",
                f"    sync: {'true' if distribution == 'synchronized' else 'false'}",
                f"    dependencies: [{', '.join(dependencies)}]",
            ]
        )

        skill_path = root / name
        skill_path.mkdir(parents=True)
        (skill_path / "SKILL.md").write_text(
            f"---\nname: {name.rsplit('/', 1)[-1]}\n"
            "description: sufficiently long test description\n"
            f"disable-model-invocation: {'true' if invocation == 'user' else 'false'}\n"
            "---\n\n"
            f"# {name}\n\nDependencies: {', '.join(dependencies)}.\n",
            encoding="utf-8",
        )
        (skill_path / "agents").mkdir()
        (skill_path / "agents" / "openai.yaml").write_text(
            "policy:\n"
            f"  allow_implicit_invocation: {'false' if invocation == 'user' else 'true'}\n",
            encoding="utf-8",
        )
    (root / "skills-manifest.yaml").write_text(
        "\n".join(manifest_lines) + "\n", encoding="utf-8"
    )


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


def test_slash_references_use_flat_runtime_deployment_name(tmp_path: Path):
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
    main = tmp_path / "main"
    dependency = tmp_path / "vocabulary" / "dep"
    for path, name in ((main, "main"), (dependency, "dep")):
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: sufficiently long description\n"
            "disable-model-invocation: false\n---\n\n正文。\n",
            encoding="utf-8",
        )
        (path / "agents").mkdir()
        (path / "agents" / "openai.yaml").write_text(
            "interface:\n  display_name: test\npolicy:\n"
            "  allow_implicit_invocation: true\n",
            encoding="utf-8",
        )

    main_skill = main / "SKILL.md"
    main_skill.write_text(
        main_skill.read_text(encoding="utf-8")
        + "\nManifest dependency: vocabulary/dep；运行时调用 `/vocabulary/dep`。\n",
        encoding="utf-8",
    )
    report = validate_repository(tmp_path)
    refs = [e for e in report["errors"] if e["code"] == "skill-reference"]
    assert len(refs) == 1, report["errors"]
    assert "use /dep" in refs[0]["message"]

    main_skill.write_text(
        main_skill.read_text(encoding="utf-8").replace("/vocabulary/dep", "/dep"),
        encoding="utf-8",
    )
    report = validate_repository(tmp_path)
    refs = [e for e in report["errors"] if e["code"] == "skill-reference"]
    assert refs == [], refs


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

    write_manifest(entry("vocabulary/review-core") + entry("my-note/noteall"))
    result = publication(load_manifest(tmp_path / "skills-manifest.yaml"), tmp_path)
    assert [skill["deployment_name"] for skill in result["skills"]] == [
        "review-core",
        "noteall",
    ]

    write_manifest(entry("vocabulary/review-core") + entry("other/review-core"))
    with pytest.raises(ValueError, match="deployment name collision"):
        publication(load_manifest(tmp_path / "skills-manifest.yaml"), tmp_path)


def test_contract_cli_emits_active_skill_lock_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    from skill_manifest import main

    manifest = MANIFEST.replace(
        "    status: stable\n    invocation: model",
        "    status: deprecated\n"
        "    deprecated_note: replaced by /bad\n"
        "    invocation: user",
        1,
    )
    manifest = manifest.replace(
        "    status: stable\n    invocation: model",
        "    status: experimental\n    invocation: user",
        1,
    )
    manifest = manifest.replace(
        "  - name: bad\n    path: bad",
        "  - name: vocabulary/bad\n    path: vocabulary/bad",
    )
    manifest_path = tmp_path / "skills-manifest.yaml"
    manifest_path.write_text(manifest, encoding="utf-8")
    for name in ("good", "vocabulary/bad"):
        path = tmp_path / name
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text("content", encoding="utf-8")

    monkeypatch.setattr(
        sys, "argv", ["skill_manifest.py", "contract", "--manifest", str(manifest_path)]
    )
    assert main() == 0
    result = json.loads(capsys.readouterr().out)

    assert result["schema_version"] == 1
    assert result["repository_version"] == "1.0.0"
    assert result["skills"] == [
        {
            "name": "vocabulary/bad",
            "deployment_name": "bad",
            "hosts": ["claude", "cursor", "codex"],
            "invocation": "user",
            "status": "experimental",
        }
    ]


@pytest.mark.parametrize("command", ["publication", "contract"])
def test_manifest_cli_output_writes_utf8_json_without_stdout(
    repo: Path,
    command: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    from skill_manifest import main

    output = repo / f"{command}.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "skill_manifest.py",
            command,
            "--manifest",
            str(repo / "skills-manifest.yaml"),
            "--output",
            str(output),
        ],
    )

    assert main() == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    raw = output.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert raw.endswith(b"\n")
    assert json.loads(raw.decode("utf-8"))["repository_version"] == "1.0.0"


def test_manifest_cli_output_does_not_create_missing_parent(
    repo: Path, monkeypatch: pytest.MonkeyPatch
):
    from skill_manifest import main

    output = repo / "missing" / "contract.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "skill_manifest.py",
            "contract",
            "--manifest",
            str(repo / "skills-manifest.yaml"),
            "--output",
            str(output),
        ],
    )

    with pytest.raises(FileNotFoundError):
        main()
    assert not output.parent.exists()


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


def test_claude_pointer_rejects_fat_routes_and_accepts_small_kernel(tmp_path: Path):
    manifest = """schema_version: 1
repository_version: 1.0.0
skills:
  - name: 0-router
    path: 0-router
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
    router = tmp_path / "0-router"
    router.mkdir()
    (router / "SKILL.md").write_text(
        "---\nname: 0-router\ndescription: router test\ndisable-model-invocation: false\n---\n\n| x | `/1-plan` |\n",
        encoding="utf-8",
    )
    claude = tmp_path / "CLAUDE.md"
    claude.write_text(
        "## 支撑层\n\n| 信号 | 技能 |\n| --- | --- |\n| 视觉 | `/vision-skill` |\n",
        encoding="utf-8",
    )
    report = validate_repository(
        tmp_path, check_claude_pointer=True, claude_path=claude
    )
    pointer = [e for e in report["errors"] if e["code"] == "claude-pointer"]
    assert any("Fat route headings" in e["message"] for e in pointer)

    claude.write_text(
        "## 工作哲学\n\n称呼：始终称呼我luohe。\n\n"
        "## 记忆约定\n\n规则。\n",
        encoding="utf-8",
    )
    report = validate_repository(
        tmp_path, check_claude_pointer=True, claude_path=claude
    )
    pointer = [e for e in report["errors"] if e["code"] == "claude-pointer"]
    assert pointer == [], pointer

    claude.write_text(
        "## 路由入口\n\n"
        "完整路由见 `/0-router`。\n"
        "规模不明时先规划。\n",
        encoding="utf-8",
    )
    report = validate_repository(
        tmp_path, check_claude_pointer=True, claude_path=claude
    )
    pointer = [e for e in report["errors"] if e["code"] == "claude-pointer"]
    assert any("must contain only" in e["message"] for e in pointer)


@pytest.mark.parametrize(
    "flag",
    ["--check-claude-pointer", "--check-claude-mirror"],
)
def test_explicit_claude_pointer_check_requires_existing_file(
    repo: Path, flag: str, capsys: pytest.CaptureFixture[str]
):
    from validate_skills import main

    missing = repo / "missing-CLAUDE.md"
    assert (
        main(
            [
                "--root",
                str(repo),
                flag,
                "--claude-md",
                str(missing),
                "--json",
            ]
        )
        == 1
    )
    report = json.loads(capsys.readouterr().out)
    pointer = [e for e in report["errors"] if e["code"] == "claude-pointer"]
    assert len(pointer) == 1, pointer
    assert pointer[0]["message"] == "CLAUDE.md does not exist"


@pytest.mark.parametrize(
    "relative_path",
    ["README.md", "USAGE.md", "CONTEXT.md", "docs/governance/names.md"],
)
def test_navigation_docs_detect_backticked_single_segment_skill_typos(
    repo: Path, relative_path: str
):
    target = repo / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("未知调用：`/grillin`。\n", encoding="utf-8")

    report = validate_repository(repo)
    refs = [e for e in report["errors"] if e["code"] == "skill-reference"]
    assert any(
        e["path"] == relative_path and "/grillin" in e["message"] for e in refs
    ), refs


def test_navigation_slash_allowlist_ignores_host_commands_and_paths(repo: Path):
    (repo / "README.md").write_text("宿主命令：`/loop`。\n", encoding="utf-8")
    (repo / "USAGE.md").write_text("系统路径：`/tmp`。\n", encoding="utf-8")
    governance = repo / "docs" / "governance"
    governance.mkdir(parents=True)
    (governance / "names.md").write_text(
        "有效运行时技能：`/good`；宿主命令：`/changelog`。\n",
        encoding="utf-8",
    )

    report = validate_repository(repo)
    refs = [e for e in report["errors"] if e["code"] == "skill-reference"]
    assert refs == [], refs


def test_repository_contract_marks_dialectic_user_only():
    from skill_manifest import contract, load_manifest

    root = Path(__file__).resolve().parents[1]
    result = contract(load_manifest(root / "skills-manifest.yaml"), root)
    dialectic = next(
        skill for skill in result["skills"] if skill["name"] == "0-dialectic"
    )
    assert dialectic["deployment_name"] == "0-dialectic"
    assert dialectic["invocation"] == "user"
    assert dialectic["status"] == "stable"


def test_router_fixtures_have_structural_metadata_without_reclassifying():
    from skill_manifest import contract, load_manifest

    root = Path(__file__).resolve().parents[1]
    fixtures = root / "tests" / "fixtures" / "prompts" / "router"
    runtime_names = {
        skill["deployment_name"]
        for skill in contract(
            load_manifest(root / "skills-manifest.yaml"), root
        )["skills"]
    }
    router = (root / "0-router" / "SKILL.md").read_text(encoding="utf-8")
    prompt_files = sorted(
        path for path in fixtures.glob("*.md") if path.name != "README.md"
    )
    assert prompt_files

    for path in prompt_files:
        lines = path.read_text(encoding="utf-8").splitlines()
        assert lines and lines[0] == "---", path
        end = lines.index("---", 1)
        metadata = {}
        for line in lines[1:end]:
            key, separator, value = line.partition(":")
            assert separator and key.strip() and value.strip(), (path, line)
            metadata[key.strip()] = value.strip()
        assert any(line.strip() for line in lines[end + 1 :]), path

        expected = metadata["expected"]
        if expected == "direct":
            marker = metadata["router_marker"]
            assert marker in router, (path, marker)
        else:
            assert expected in runtime_names, (path, expected)
            assert f"/{expected}" in router, (path, expected)


def test_dependency_cycles_report_readable_paths(tmp_path: Path):
    _write_governance_repo(
        tmp_path,
        [
            {"name": "self-cycle", "dependencies": ["self-cycle"]},
            {"name": "alpha", "dependencies": ["beta"]},
            {"name": "beta", "dependencies": ["gamma"]},
            {"name": "gamma", "dependencies": ["alpha"]},
        ],
    )

    report = validate_repository(tmp_path)

    cycles = {
        error["message"]
        for error in report["errors"]
        if error["code"] == "dependency-cycle"
    }
    assert cycles == {
        "dependency cycle: alpha -> beta -> gamma -> alpha",
        "dependency cycle: self-cycle -> self-cycle",
    }


def test_active_skills_cannot_depend_on_deprecated_skills(tmp_path: Path):
    _write_governance_repo(
        tmp_path,
        [
            {"name": "legacy-base", "status": "deprecated"},
            {
                "name": "legacy-client",
                "status": "deprecated",
                "dependencies": ["legacy-base"],
            },
            {"name": "stable-client", "dependencies": ["legacy-base"]},
            {
                "name": "experimental-client",
                "status": "experimental",
                "dependencies": ["legacy-base"],
            },
        ],
    )

    report = validate_repository(tmp_path)

    status_errors = {
        error["message"]
        for error in report["errors"]
        if error["code"] == "dependency-status"
    }
    assert status_errors == {
        "experimental-client: experimental skill cannot depend on deprecated legacy-base",
        "stable-client: stable skill cannot depend on deprecated legacy-base",
    }


def test_release_versions_match_manifest_when_files_exist(tmp_path: Path):
    _write_governance_repo(tmp_path, [{"name": "active"}])
    assert not [
        error
        for error in validate_repository(tmp_path)["errors"]
        if error["code"] == "release-version"
    ]

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "fixture"\nversion = "2.0.0"\n',
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n## [3.0.0] - 2026-08-13\n",
        encoding="utf-8",
    )

    report = validate_repository(tmp_path)

    mismatches = {
        (error["path"], error["message"])
        for error in report["errors"]
        if error["code"] == "release-version"
    }
    assert mismatches == {
        (
            "CHANGELOG.md",
            "repository_version 1.0.0 != first published CHANGELOG version 3.0.0",
        ),
        (
            "pyproject.toml",
            "repository_version 1.0.0 != [project].version 2.0.0",
        ),
    }

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nversion = "1.0.0"\n',
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n## [1.0.0] - 2026-08-13\n",
        encoding="utf-8",
    )
    assert not [
        error
        for error in validate_repository(tmp_path)["errors"]
        if error["code"] == "release-version"
    ]


def test_usage_indexes_active_synchronized_skills_by_link_target(tmp_path: Path):
    _write_governance_repo(
        tmp_path,
        [
            {"name": "active-one"},
            {"name": "active-two"},
            {"name": "retired", "status": "deprecated"},
            {"name": "host-skill", "distribution": "host-provided"},
        ],
    )
    (tmp_path / "USAGE.md").write_text(
        "Plain text is not an index: active-one/SKILL.md\n\n"
        "[Active two](<active-two/SKILL.md>)\n",
        encoding="utf-8",
    )

    report = validate_repository(tmp_path)

    usage_errors = [
        error for error in report["errors"] if error["code"] == "usage-index"
    ]
    assert usage_errors == [
        {
            "code": "usage-index",
            "path": "USAGE.md",
            "message": "active-one: missing Markdown link target active-one/SKILL.md",
        }
    ]


def test_invocation_graph_indexes_each_manifest_dependency_edge(tmp_path: Path):
    _write_governance_repo(
        tmp_path,
        [
            {"name": "main", "dependencies": ["dep-one", "dep-two"]},
            {"name": "dep-one"},
            {"name": "dep-two"},
        ],
    )
    governance = tmp_path / "docs" / "governance"
    governance.mkdir(parents=True)
    graph = governance / "invocation-graph.md"
    graph.write_text(
        "# Invocation graph\n\n"
        "Outside the manifest block does not count: main -> dep-two\n\n"
        "The manifest canonical dependencies are:\n\n"
        "```text\n"
        "main -> dep-one\n"
        "```\n",
        encoding="utf-8",
    )

    report = validate_repository(tmp_path)

    graph_errors = [
        error for error in report["errors"] if error["code"] == "invocation-graph"
    ]
    assert graph_errors == [
        {
            "code": "invocation-graph",
            "path": "docs/governance/invocation-graph.md",
            "message": "main -> dep-two missing from manifest dependency code block",
        }
    ]

    graph.write_text(
        "# Invocation graph\n\n"
        "The manifest canonical dependencies are:\n\n"
        "```text\n"
        "main ──> dep-one + dep-two\n"
        "```\n",
        encoding="utf-8",
    )
    assert not [
        error
        for error in validate_repository(tmp_path)["errors"]
        if error["code"] == "invocation-graph"
    ]

    graph.write_text(
        "# Invocation graph\n\n"
        "The manifest canonical dependencies are:\n\n"
        "```text\n"
        "main ──> dep-one + dep-two\n"
        "dep-one ──> dep-two\n"
        "```\n",
        encoding="utf-8",
    )
    extra_edges = [
        error
        for error in validate_repository(tmp_path)["errors"]
        if error["code"] == "invocation-graph"
    ]
    assert extra_edges == [
        {
            "code": "invocation-graph",
            "path": "docs/governance/invocation-graph.md",
            "message": "dep-one -> dep-two is not declared in manifest",
        }
    ]


def test_router_trigger_eval_set_has_valid_routes_and_near_misses():
    from skill_manifest import contract, load_manifest

    root = Path(__file__).resolve().parents[1]
    dataset = json.loads(
        (
            root
            / "tests"
            / "fixtures"
            / "prompts"
            / "router"
            / "trigger-evals.json"
        ).read_text(encoding="utf-8")
    )
    runtime_names = {
        skill["deployment_name"]
        for skill in contract(
            load_manifest(root / "skills-manifest.yaml"), root
        )["skills"]
    }
    cases = dataset["cases"]

    assert dataset["schema_version"] == 1
    assert len(cases) >= 22
    assert len({case["id"] for case in cases}) == len(cases)
    for case in cases:
        assert case["prompt"].strip()
        assert case["reason"].strip()
        assert case["expected"] == "direct" or case["expected"] in runtime_names
        assert isinstance(case["forbidden"], list)
        assert case["expected"] not in case["forbidden"]
        assert set(case["forbidden"]) <= runtime_names

    assert any(case["forbidden"] for case in cases)
    assert any(
        case["expected"] == "direct" and "noteall" in case["forbidden"]
        for case in cases
    )

    by_id = {case["id"]: case for case in cases}
    required_boundaries = {
        "plan-ambiguous-auth": ("1-plan", {"2-implement"}),
        "review-without-upstream-evidence": ("3-review", {"2-implement"}),
        "issue-only": ("issue-reporting", {"4-debug"}),
        "memory-near-miss": ("direct", {"noteall"}),
        "neat-freak": ("0-neat-freak", {"6-sum"}),
        "dialectic-implicit-negative": ("direct", {"0-dialectic"}),
    }
    for case_id, (expected, forbidden) in required_boundaries.items():
        assert by_id[case_id]["expected"] == expected
        assert forbidden <= set(by_id[case_id]["forbidden"])


def test_noteall_locks_one_selected_vault_across_pipeline_docs():
    root = Path(__file__).resolve().parents[1]
    config = (
        root / "my-note" / "noteall" / "references" / "config.yaml"
    ).read_text(encoding="utf-8")
    runtime_docs = [
        root / "my-note" / "noteall" / "SKILL.md",
        root / "my-note" / "noteall" / "references" / "intake.md",
        root / "my-note" / "noteall" / "references" / "maintain.md",
        root / "my-note" / "noteall" / "references" / "publish.md",
        root / "my-note" / "vault-publisher" / "SKILL.md",
    ]
    texts = [path.read_text(encoding="utf-8") for path in runtime_docs]
    joined = "\n".join(texts)

    assert "prefer_current_vault: true" in config
    assert "vault_path:" in config
    assert all("{selected_vault}" in text for text in texts)
    assert "{vault_path}" not in joined
    assert "{vault}" not in joined


def test_parallel_orchestration_contract_markers():
    root = Path(__file__).resolve().parents[1]
    router = (root / "0-router" / "SKILL.md").read_text(encoding="utf-8")
    plan = (root / "1-plan" / "SKILL.md").read_text(encoding="utf-8")
    implement = (root / "2-implement" / "SKILL.md").read_text(encoding="utf-8")
    review = (root / "3-review" / "references" / "review-rules.md").read_text(
        encoding="utf-8"
    )
    neat_freak = (root / "0-neat-freak" / "SKILL.md").read_text(encoding="utf-8")
    maintain = (
        root / "my-note" / "noteall" / "references" / "maintain.md"
    ).read_text(encoding="utf-8")

    assert "（顺序开发）" not in router
    for marker in ("Write Set", "无相互依赖只表示候选", "唯一 owner", "HITL"):
        assert marker in plan
    for marker in (
        "同一冻结基点",
        "隔离可写上下文",
        "可回传变更包",
        "依赖已验收",
        "Write Set 互斥",
        "唯一 owner",
        "HITL 无未决影响",
        "运行资源可隔离",
        "顺序 fresh context",
        "主上下文顺序执行",
        "唯一合流",
        "冲突即停止",
        "最终合流态",
    ):
        assert marker in implement
    for host_specific in ("后台 subagent", "并行 task", "worktree", "Cursor", "Codex"):
        assert host_specific not in implement
    for marker in ("独立只读上下文", "同一证据包", "主流程唯一汇总"):
        assert marker in review
    assert "docs/ → CLAUDE.md → memory 串行执行" in neat_freak
    for marker in (
        "HITL 确认",
        "共享 INDEX/MOC",
        "移动/重命名",
        "断链修复",
        "Publish 保持串行",
    ):
        assert marker in maintain
