#!/usr/bin/env python3
"""Validate skill repository governance without changing the repository."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
MANIFEST_MODULE_PATH = SCRIPT_DIR / "skill_manifest.py"
BANNED_SKILLS = ("0--Agent统筹", "0--auto-iteration", "0--graphify")
HOSTS = (".claude", ".cursor", ".codex")
LINK_RE = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")
SLASH_SKILL_RE = re.compile(
    r"(?<![\w.])/(?!/)([\w-]+/[\w-]+(?:--?[\w-]+)*|[\w-]+(?:--?[\w-]+)+)",
    re.UNICODE,
)
# Vault / system path references that look like skill names to SLASH_SKILL_RE
# but aren't (matched by first path segment)
SKILL_REF_EXCLUSIONS = frozenset(
    {
        "0-Inbox",
        "1-Atlas",
        "2-Projects",
        "3-Areas",
        "4-Resources",
        "5-Journal",
        "6-People",
        "7-Sources",
        "raw",
        "docs",
        "memory",
        "Library",
        "tmp",
        "Desktop",
        "Data",
        "Music",
        "Cleanup-Image",
    }
)
ROUTE_ROW_RE = re.compile(r"^\|[^\n]*\|\s*([^|`]+?)\s*\|[^\n]*$")

# Naming convention patterns
STAGE_SKILL_RE = re.compile(r"^[0-6]-[一-鿿]+$")  # N-中文
EXTENSION_SKILL_RE = re.compile(r"^0--[a-z][a-z0-9-]*$")  # 0--lowercase
VOCABULARY_SKILL_RE = re.compile(
    r"^vocabulary/[a-z][a-z0-9-]*$"
)  # vocabulary/lowercase
MY_NOTE_SKILL_RE = re.compile(
    r"^my-note/[a-z][a-z0-9-]*(-[a-z][a-z0-9-]*)*$"
)  # my-note/lowercase-hyphenated
ROUTER_SKILL = "0-询问luohe"


def _load_manifest_module():
    spec = importlib.util.spec_from_file_location(
        "skill_manifest", MANIFEST_MODULE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MANIFEST_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    old_dont_write_bytecode = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old_dont_write_bytecode
    return module


skill_manifest = _load_manifest_module()


def _finding(code: str, path: Path, message: str, root: Path) -> dict[str, str]:
    try:
        display_path = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        display_path = path.resolve().as_posix()
    return {"code": code, "path": display_path, "message": message}


def _frontmatter(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening ---")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing ---") from exc
    values: dict[str, Any] = {}
    for line_number, line in enumerate(lines[1:end], 2):
        if not line.strip() or line[0] in " \t":
            continue  # blank or block-scalar continuation line
        key, separator, raw_value = line.partition(":")
        if not separator or not key.strip() or key.strip() in values:
            raise ValueError(f"line {line_number}: invalid or duplicate field")
        value = raw_value.strip()
        if value == "true":
            parsed: Any = True
        elif value == "false":
            parsed = False
        else:
            parsed = value.strip("\"'")
        values[key.strip()] = parsed
    return values


def _implicit_invocation(path: Path) -> bool:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    in_policy = False
    found: bool | None = None
    for line_number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            in_policy = stripped == "policy:"
            continue
        if (
            in_policy
            and indent == 2
            and stripped.startswith("allow_implicit_invocation:")
        ):
            raw_value = stripped.partition(":")[2].split("#", 1)[0].strip()
            if raw_value not in ("true", "false") or found is not None:
                raise ValueError(
                    f"line {line_number}: invalid allow_implicit_invocation"
                )
            found = raw_value == "true"
    return True if found is None else found


def _tree_hash(path: Path) -> str:
    digest = hashlib.sha256()
    for file_path in sorted(item for item in path.rglob("*") if item.is_file()):
        relative = file_path.relative_to(path).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        data = file_path.read_bytes()
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def _validate_naming(name: str) -> str | None:
    """Validate skill name against naming conventions.

    Returns None if valid, or an error message if invalid.
    """
    if name == ROUTER_SKILL:
        return None
    if STAGE_SKILL_RE.match(name):
        return None
    if EXTENSION_SKILL_RE.match(name):
        return None
    if VOCABULARY_SKILL_RE.match(name):
        return None
    if MY_NOTE_SKILL_RE.match(name):
        return None
    # Allow standalone methodology skills (e.g., multi-worker, 0--dialectic with uppercase)
    if "/" not in name and not name[0].isdigit():
        return None
    # Check for common naming violations
    if re.match(r"^[0-6]-", name) and not STAGE_SKILL_RE.match(name):
        return f"stage skill must follow 'N-中文' format, got '{name}'"
    if name.startswith("0--") and not EXTENSION_SKILL_RE.match(name):
        return f"extension skill must follow '0--lowercase' format, got '{name}'"
    if name.startswith("vocabulary/") and not VOCABULARY_SKILL_RE.match(name):
        return (
            f"vocabulary skill must follow 'vocabulary/lowercase' format, got '{name}'"
        )
    if name.startswith("my-note/") and not MY_NOTE_SKILL_RE.match(name):
        return f"my-note skill must follow 'my-note/lowercase' format, got '{name}'"
    return f"skill name '{name}' does not match any naming convention"


def _validate_manifest(
    manifest: dict[str, Any], root: Path, errors: list[dict[str, str]]
) -> list[dict[str, Any]]:
    skills = manifest.get("skills")
    if manifest.get("schema_version") != 1:
        errors.append(
            _finding(
                "manifest",
                root / "skills-manifest.yaml",
                "schema_version must be 1",
                root,
            )
        )
    version = manifest.get("repository_version")
    if not isinstance(version, str) or not skill_manifest.SEMVER.fullmatch(version):
        errors.append(
            _finding(
                "manifest",
                root / "skills-manifest.yaml",
                "repository_version must be semantic",
                root,
            )
        )
    if not isinstance(skills, list):
        errors.append(
            _finding(
                "manifest",
                root / "skills-manifest.yaml",
                "skills must be a sequence",
                root,
            )
        )
        return []

    names: set[str] = set()
    for index, skill in enumerate(skills, 1):
        path = root / str(skill.get("path", ""))
        missing = skill_manifest.REQUIRED_FIELDS - skill.keys()
        extra = (
            skill.keys()
            - skill_manifest.REQUIRED_FIELDS
            - skill_manifest.OPTIONAL_FIELDS
        )
        name = skill.get("name")
        if missing or extra:
            errors.append(
                _finding(
                    "manifest",
                    root / "skills-manifest.yaml",
                    f"skill {index} fields mismatch",
                    root,
                )
            )
            continue
        if not isinstance(name, str) or not name or name in names:
            errors.append(
                _finding(
                    "manifest-name",
                    root / "skills-manifest.yaml",
                    f"skill {index} name must be unique",
                    root,
                )
            )
            continue
        names.add(name)
        # Validate naming convention
        naming_error = _validate_naming(name)
        if naming_error:
            errors.append(
                _finding(
                    "naming-convention",
                    root / "skills-manifest.yaml",
                    f"{name}: {naming_error}",
                    root,
                )
            )
        if skill["path"] != name:
            errors.append(
                _finding(
                    "manifest-path",
                    root / "skills-manifest.yaml",
                    f"{name}: path must equal name",
                    root,
                )
            )
        if skill["version"] != version or skill["status"] != "stable":
            errors.append(
                _finding(
                    "manifest",
                    root / "skills-manifest.yaml",
                    f"{name}: invalid version or status",
                    root,
                )
            )
        if skill["invocation"] not in ("user", "model"):
            errors.append(
                _finding(
                    "manifest",
                    root / "skills-manifest.yaml",
                    f"{name}: invalid invocation",
                    root,
                )
            )
        if skill["hosts"] != ["claude", "cursor", "codex"]:
            errors.append(
                _finding(
                    "manifest",
                    root / "skills-manifest.yaml",
                    f"{name}: invalid hosts",
                    root,
                )
            )
        distribution = skill["distribution"]
        if distribution == "synchronized" and skill["sync"] is not True:
            errors.append(
                _finding(
                    "manifest",
                    root / "skills-manifest.yaml",
                    f"{name}: synchronized requires sync true",
                    root,
                )
            )
        elif distribution == "host-provided" and (
            skill["sync"] is not False or skill["invocation"] != "model"
        ):
            errors.append(
                _finding(
                    "manifest",
                    root / "skills-manifest.yaml",
                    f"{name}: invalid host-provided settings",
                    root,
                )
            )
        elif distribution not in ("synchronized", "host-provided"):
            errors.append(
                _finding(
                    "manifest",
                    root / "skills-manifest.yaml",
                    f"{name}: invalid distribution",
                    root,
                )
            )
        if not isinstance(skill["dependencies"], list):
            errors.append(
                _finding(
                    "manifest",
                    root / "skills-manifest.yaml",
                    f"{name}: dependencies must be a list",
                    root,
                )
            )
        if not path.is_dir() or not (path / "SKILL.md").is_file():
            errors.append(
                _finding(
                    "manifest-path",
                    path,
                    f"{name}: source directory or SKILL.md missing",
                    root,
                )
            )
    return skills


def _validate_dependencies(
    skills: list[dict[str, Any]], root: Path, errors: list[dict[str, str]]
) -> None:
    by_name = {
        skill.get("name"): skill
        for skill in skills
        if isinstance(skill.get("name"), str)
    }
    for skill in skills:
        name = skill.get("name")
        dependencies = skill.get("dependencies")
        if not isinstance(name, str) or not isinstance(dependencies, list):
            continue
        for target in dependencies:
            if not isinstance(target, str) or target not in by_name:
                errors.append(
                    _finding(
                        "dependency-target",
                        root / "skills-manifest.yaml",
                        f"{name}: unknown dependency {target!r}",
                        root,
                    )
                )
            elif (
                skill.get("distribution") == "synchronized"
                and by_name[target].get("distribution") == "host-provided"
            ):
                errors.append(
                    _finding(
                        "dependency-direction",
                        root / "skills-manifest.yaml",
                        f"{name}: synchronized skill cannot depend on host-provided {target}",
                        root,
                    )
                )


def _validate_skill(
    skill: dict[str, Any],
    root: Path,
    canonical: set[str],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    if skill.get("distribution") == "host-provided":
        return
    name = skill.get("name")
    if not isinstance(name, str):
        return
    skill_path = root / name
    document = skill_path / "SKILL.md"
    if not document.is_file():
        return
    try:
        frontmatter = _frontmatter(document)
    except ValueError as exc:
        errors.append(_finding("frontmatter", document, str(exc), root))
        return
    # For nested skills (e.g., vocabulary/cat/skill), frontmatter name should match
    # only the final component (e.g., "skill"), not the full path
    expected_frontmatter_name = name.split("/")[-1] if "/" in name else name
    if frontmatter.get("name") != expected_frontmatter_name:
        errors.append(
            _finding(
                "frontmatter-name",
                document,
                f"frontmatter name must be {expected_frontmatter_name}",
                root,
            )
        )

    disabled = frontmatter.get("disable-model-invocation") is True
    openai = skill_path / "agents" / "openai.yaml"
    try:
        implicit = _implicit_invocation(openai) if openai.is_file() else None
    except ValueError as exc:
        implicit = None
        errors.append(_finding("invocation-parity", openai, str(exc), root))
    # disable-model-invocation is the single source of truth: the agents file
    # must not allow implicit invocation when model invocation is disabled.
    if not openai.is_file() or implicit == disabled:
        errors.append(
            _finding(
                "invocation-parity",
                document,
                "manifest, frontmatter, and agents/openai.yaml invocation controls disagree",
                root,
            )
        )

    line_count = len(document.read_text(encoding="utf-8-sig").splitlines())
    if line_count > 500:
        errors.append(
            _finding(
                "skill-size",
                document,
                f"SKILL.md has {line_count} lines; maximum is 500",
                root,
            )
        )
    elif line_count > 200:
        warnings.append(
            _finding(
                "skill-size",
                document,
                f"SKILL.md has {line_count} lines; recommended maximum is 200",
                root,
            )
        )

    for markdown in sorted(skill_path.rglob("*.md")):
        _validate_markdown(markdown, root, canonical, errors)


def _validate_document_authority(
    path: Path, text: str, root: Path, errors: list[dict[str, str]]
) -> None:
    """Enforce the repository's CONTEXT, ADR, and task-status boundaries."""
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    normalized = text.lower()

    if relative == "1-规划/references/context-format.md":
        forbidden = (
            "技术栈",
            "模块地图",
            "当前任务",
            "历史归档",
            "architecture decision",
            "## adr",
            "### adr",
        )
        if any(term in normalized for term in forbidden):
            errors.append(
                _finding(
                    "context-authority",
                    path,
                    "CONTEXT format may contain only glossary, relationships, ambiguities, and domain scenarios",
                    root,
                )
            )

    if re.search(r"(?<![.\w-])/references/adr-format\.md", text):
        errors.append(
            _finding(
                "adr-template-owner",
                path,
                "ADR template must be owned by vocabulary/domain-modeling/references/adr-format.md",
                root,
            )
        )


def _validate_markdown(
    path: Path, root: Path, canonical: set[str], errors: list[dict[str, str]]
) -> None:
    text = path.read_text(encoding="utf-8-sig")
    _validate_document_authority(path, text, root, errors)
    for banned in BANNED_SKILLS:
        if banned in text:
            errors.append(
                _finding(
                    "banned-skill-reference",
                    path,
                    f"references removed skill {banned}",
                    root,
                )
            )
    for raw_target in LINK_RE.findall(text):
        target = raw_target.strip().strip("<>")
        if " " in target and not raw_target.strip().startswith("<"):
            target = target.split(maxsplit=1)[0].strip('"')
        else:
            target = target.strip('"')
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        local = target.split("#", 1)[0]
        if local and not (path.parent / local).resolve().exists():
            errors.append(
                _finding("markdown-link", path, f"broken local link: {target}", root)
            )
    for reference in SLASH_SKILL_RE.findall(text):
        if reference.split("/", 1)[0] in SKILL_REF_EXCLUSIONS:
            continue
        if reference not in canonical:
            errors.append(
                _finding(
                    "skill-reference",
                    path,
                    f"unknown canonical skill reference /{reference}",
                    root,
                )
            )


def _validate_routes(
    root: Path, canonical: set[str], errors: list[dict[str, str]]
) -> None:
    route_path = root / "use-skills" / "SKILL.md"
    if not route_path.is_file():
        return
    in_table = False
    for line in route_path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip() == "## 技能路由表":
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if (
            not in_table
            or not line.startswith("|")
            or "---" in line
            or "匹配技能" in line
        ):
            continue
        columns = [
            column.strip().strip("`") for column in line.strip().strip("|").split("|")
        ]
        if len(columns) >= 4 and columns[3] not in canonical:
            errors.append(
                _finding(
                    "canonical-route",
                    route_path,
                    f"route uses unknown skill {columns[3]}",
                    root,
                )
            )


def _validate_deployments(
    root: Path, skills: list[dict[str, Any]], errors: list[dict[str, str]]
) -> None:
    published = sorted(
        skill["name"]
        for skill in skills
        if skill.get("distribution") == "synchronized"
        and isinstance(skill.get("name"), str)
    )
    expected_names = set(published)
    for host in HOSTS:
        deployment = root.parent / host / "skills"
        if not deployment.is_dir():
            errors.append(
                _finding(
                    "deployment-state",
                    deployment,
                    f"{host} deployment root is missing",
                    root,
                )
            )
            continue

        state_path = deployment / ".my-skills-managed.json"
        try:
            state = json.loads(state_path.read_text(encoding="utf-8-sig"))
        except FileNotFoundError:
            errors.append(
                _finding(
                    "deployment-state",
                    state_path,
                    "managed state file is missing; cannot infer managed skills from directory entries",
                    root,
                )
            )
            continue
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(
                _finding(
                    "deployment-state",
                    state_path,
                    f"invalid managed state: {exc}",
                    root,
                )
            )
            continue

        managed = state.get("skills") if isinstance(state, dict) else None
        state_valid = (
            isinstance(state, dict)
            and state.get("schema_version") == 1
            and isinstance(managed, list)
            and all(isinstance(name, str) and name for name in managed)
            and len(managed) == len(set(managed))
        )
        if not state_valid:
            errors.append(
                _finding(
                    "deployment-state",
                    state_path,
                    "managed state must contain schema_version 1 and a unique list of non-empty skill names",
                    root,
                )
            )
            continue

        managed_names = set(managed)
        if managed_names != expected_names:
            errors.append(
                _finding(
                    "deployment-state-drift",
                    state_path,
                    f"expected managed skills {published}; found {sorted(managed_names)}",
                    root,
                )
            )

        # Only names in the source publication are managed by this validation.
        # Other deployment entries are explicitly left untouched by synchronization.
        for name in published:
            deployed_skill = deployment / name
            if not deployed_skill.is_dir():
                errors.append(
                    _finding(
                        "deployment-hash",
                        deployed_skill,
                        "managed deployment directory is missing",
                        root,
                    )
                )
            elif _tree_hash(root / name) != _tree_hash(deployed_skill):
                errors.append(
                    _finding(
                        "deployment-hash",
                        deployed_skill,
                        "deployment content hash differs from source",
                        root,
                    )
                )


def validate_repository(root: Path, check_deployments: bool = False) -> dict[str, Any]:
    root = root.resolve()
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    manifest_path = root / "skills-manifest.yaml"
    try:
        manifest = skill_manifest.load_manifest(manifest_path)
    except (OSError, ValueError) as exc:
        errors.append(_finding("manifest", manifest_path, str(exc), root))
        manifest = {"skills": []}
    skills = _validate_manifest(manifest, root, errors)
    canonical = {
        skill["name"] for skill in skills if isinstance(skill.get("name"), str)
    }
    # Discover skills recursively: top-level and any nested under subdirectories
    discovered = set()
    for skill_md in root.rglob("*/SKILL.md"):
        skill_dir = skill_md.parent
        try:
            relative_path = skill_dir.relative_to(root).as_posix()
            discovered.add(relative_path)
        except ValueError:
            pass
    if discovered != canonical:
        errors.append(
            _finding(
                "manifest-path",
                manifest_path,
                f"manifest names differ from skill directories; missing={sorted(discovered - canonical)}, extra={sorted(canonical - discovered)}",
                root,
            )
        )
    _validate_dependencies(skills, root, errors)
    for skill in sorted(skills, key=lambda item: str(item.get("name", ""))):
        _validate_skill(skill, root, canonical, errors, warnings)
    _validate_routes(root, canonical, errors)
    if check_deployments:
        _validate_deployments(root, skills, errors)
    errors.sort(key=lambda item: (item["path"], item["code"], item["message"]))
    warnings.sort(key=lambda item: (item["path"], item["code"], item["message"]))
    return {"ok": not errors, "root": str(root), "errors": errors, "warnings": warnings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="emit a deterministic JSON report"
    )
    parser.add_argument(
        "--check-deployments",
        action="store_true",
        help="compare parent host deployments with source",
    )
    parser.add_argument(
        "--root", type=Path, default=SCRIPT_DIR.parent, help=argparse.SUPPRESS
    )
    args = parser.parse_args(argv)
    report = validate_repository(args.root, args.check_deployments)
    if args.json:
        json.dump(report, sys.stdout, ensure_ascii=True, indent=2, sort_keys=True)
        print()
    else:
        for level in ("errors", "warnings"):
            for item in report[level]:
                print(
                    f"{level[:-1].upper()} [{item['code']}] {item['path']}: {item['message']}"
                )
        print(
            f"Validation {'passed' if report['ok'] else 'failed'}: {len(report['errors'])} error(s), {len(report['warnings'])} warning(s)"
        )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
