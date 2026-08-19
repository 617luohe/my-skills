#!/usr/bin/env python3
"""Validate skill repository governance without changing the repository."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
MANIFEST_MODULE_PATH = SCRIPT_DIR / "skill_manifest.py"
BANNED_SKILLS = ("0--Agent统筹", "0--auto-iteration", "0--graphify")
USER_ONLY_BODY_RE = re.compile(
    r"^仅(?:可由|由)?用户(?:显式)?(?:调用|触发|输入)",
    re.MULTILINE,
)
WORKER_ONLY_BODY_RE = re.compile(
    r"仅由\s+\S+\s+调度|严禁(?:直调|直接调用)"
)
LINK_RE = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")
STRUCTURED_SLASH_SKILL_RE = re.compile(
    r"(?<![\w.])/(?!/)([\w-]+/[\w-]+(?:--?[\w-]+)*|[\w-]+(?:--?[\w-]+)+)",
    re.UNICODE,
)
BACKTICKED_SINGLE_SLASH_RE = re.compile(r"`/([A-Za-z0-9][A-Za-z0-9_-]*)`")
# Vault / system path references that look like structured slash skill names
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
        "Documents",
        "scripts",
        "tests",
        "Cleanup-Image",
    }
)
HOST_COMMAND_ALLOWLIST = frozenset({"loop", "changelog"})
FAT_ROUTE_HEADING_RE = re.compile(
    r"^##\s+(?:工作流路由|支撑层)(?:\s|[（(]|$)", re.MULTILINE
)
CHANGELOG_RELEASE_RE = re.compile(
    r"^##\s+\[?([0-9]+\.[0-9]+\.[0-9]+)\]?(?:\s+-[^\n]*)?\s*$",
    re.MULTILINE,
)
MANIFEST_DEPENDENCY_BLOCK_RE = re.compile(
    r"^[^\n]*manifest[^\n]*(?:dependenc(?:y|ies)|依赖)[^\n]*\n"
    r"\s*```[^\n]*\n(.*?)^```",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)

# Naming convention patterns
STAGE_SKILL_RE = re.compile(r"^[0-6]-[a-z][a-z0-9-]*$")  # N-english-slug
EXTENSION_SKILL_RE = re.compile(r"^0--[a-z][a-z0-9-]*$")  # 0--lowercase
VOCABULARY_SKILL_RE = re.compile(
    r"^vocabulary/[a-z][a-z0-9-]*$"
)  # vocabulary/lowercase
MY_NOTE_SKILL_RE = re.compile(
    r"^my-note/[a-z][a-z0-9-]*(-[a-z][a-z0-9-]*)*$"
)  # my-note/lowercase-hyphenated
ROUTER_SKILL = "0-router"


def _slash_skill_references(text: str, runtime_names: set[str]) -> set[str]:
    """Find structured, known flat, and backticked single-segment references."""
    references = set(STRUCTURED_SLASH_SKILL_RE.findall(text))
    references.update(BACKTICKED_SINGLE_SLASH_RE.findall(text))
    plain_names = sorted(
        (name for name in runtime_names if "/" not in name and "-" not in name),
        key=len,
        reverse=True,
    )
    if plain_names:
        exact_runtime = re.compile(
            r"(?<![\w./-])/(" + "|".join(map(re.escape, plain_names)) + r")(?![\w/-])"
        )
        references.update(exact_runtime.findall(text))
    return references


def _expected_category(name: str) -> str:
    if name == ROUTER_SKILL:
        return "router"
    if name.startswith("0--"):
        return "extension"
    if STAGE_SKILL_RE.match(name):
        return "main-flow"
    if name.startswith("vocabulary/"):
        return "vocabulary"
    if name.startswith("my-note/"):
        return "my-note"
    return "standalone"


def _validate_claude_pointer(
    root: Path,
    errors: list[dict[str, str]],
    claude_path: Path | None = None,
) -> None:
    if claude_path is None:
        claude_path = root.parent / "CLAUDE.md"
    if not claude_path.is_file():
        errors.append(
            _finding(
                "claude-pointer",
                claude_path,
                "CLAUDE.md does not exist",
                root,
            )
        )
        return
    claude_text = claude_path.read_text(encoding="utf-8")
    if FAT_ROUTE_HEADING_RE.search(claude_text):
        errors.append(
            _finding(
                "claude-pointer",
                claude_path,
                "CLAUDE.md contains Fat route headings; keep only ## 路由入口",
                root,
            )
        )
    route_heading = re.search(r"^## 路由入口\s*$", claude_text, re.MULTILINE)
    if route_heading is None:
        # 路由入口非强制块：最小内核 CLAUDE.md 只含工作哲学 + 记忆约定，路由由 /0-router 独占
        return
    next_heading = re.search(r"^## ", claude_text[route_heading.end() :], re.MULTILINE)
    section_end = (
        route_heading.end() + next_heading.start()
        if next_heading is not None
        else len(claude_text)
    )
    section = claude_text[route_heading.start() : section_end]
    if f"/{ROUTER_SKILL}" not in section:
        errors.append(
            _finding(
                "claude-pointer",
                claude_path,
                f"## 路由入口 must point to /{ROUTER_SKILL}",
                root,
            )
        )
        return
    body_lines = [
        line.strip()
        for line in section.splitlines()[1:]
        if line.strip()
    ]
    pointer_line = re.compile(
        rf"^完整路由(?:只)?见\s+`/{re.escape(ROUTER_SKILL)}`[。.]?$"
    )
    if len(body_lines) != 1 or pointer_line.fullmatch(body_lines[0]) is None:
        errors.append(
            _finding(
                "claude-pointer",
                claude_path,
                "## 路由入口 must contain only the /0-router pointer",
                root,
            )
        )


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


def _full_description(lines: list[str]) -> str:
    """Extract description value including block-scalar continuation lines."""
    in_desc = False
    parts: list[str] = []
    for line in lines:
        stripped = line.rstrip()
        if not stripped or stripped[0] in " \t":
            if in_desc:
                parts.append(stripped.strip())
            continue
        key, separator, value = stripped.partition(":")
        if separator and key.strip() == "description":
            if value.strip() == ">":
                in_desc = True
            else:
                return value.strip().strip("\"'")
        else:
            in_desc = False
    return " ".join(part for part in parts if part).strip()


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
    # Allow standalone methodology skills (e.g., writing-for-agents, 0--dialectic with uppercase)
    if "/" not in name and not name[0].isdigit():
        return None
    # Check for common naming violations
    if re.match(r"^[0-6]-", name) and not STAGE_SKILL_RE.match(name):
        return f"stage skill must follow 'N-english-slug' format (e.g. 1-plan), got '{name}'"
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
        if skill["version"] != version:
            errors.append(
                _finding(
                    "manifest",
                    root / "skills-manifest.yaml",
                    f"{name}: invalid version",
                    root,
                )
            )
        if skill["status"] not in ("stable", "deprecated", "experimental"):
            errors.append(
                _finding(
                    "manifest",
                    root / "skills-manifest.yaml",
                    f"{name}: invalid status {skill['status']}",
                    root,
                )
            )
        elif skill["status"] == "deprecated":
            if not skill.get("deprecated_note"):
                errors.append(
                    _finding(
                        "manifest",
                        root / "skills-manifest.yaml",
                        f"{name}: deprecated status requires deprecated_note",
                        root,
                    )
                )
            if skill.get("invocation") != "user":
                errors.append(
                    _finding(
                        "manifest",
                        root / "skills-manifest.yaml",
                        f"{name}: deprecated status requires invocation user",
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
        category = skill.get("category")
        expected = _expected_category(name)
        if not isinstance(category, str) or category not in skill_manifest.ALLOWED_CATEGORIES:
            errors.append(
                _finding(
                    "manifest-category",
                    root / "skills-manifest.yaml",
                    f"{name}: category must be one of {sorted(skill_manifest.ALLOWED_CATEGORIES)}",
                    root,
                )
            )
        elif category != expected:
            errors.append(
                _finding(
                    "manifest-category",
                    root / "skills-manifest.yaml",
                    f"{name}: category {category!r} != expected {expected!r}",
                    root,
                )
            )
    return skills


def _pyproject_version(path: Path) -> str | None:
    in_project = False
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if re.fullmatch(r"\[[^]]+\]", stripped):
            in_project = stripped == "[project]"
            continue
        if not in_project:
            continue
        match = re.fullmatch(
            r"""version\s*=\s*(["'])([^"']+)\1(?:\s*#.*)?""", stripped
        )
        if match:
            return match.group(2)
    return None


def _validate_release_versions(
    manifest: dict[str, Any], root: Path, errors: list[dict[str, str]]
) -> None:
    expected = manifest.get("repository_version")
    if not isinstance(expected, str) or not skill_manifest.SEMVER.fullmatch(expected):
        return

    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        actual = _pyproject_version(pyproject)
        if actual != expected:
            message = (
                f"repository_version {expected} != [project].version {actual}"
                if actual is not None
                else "[project].version is missing"
            )
            errors.append(_finding("release-version", pyproject, message, root))

    changelog = root / "CHANGELOG.md"
    if changelog.is_file():
        match = CHANGELOG_RELEASE_RE.search(
            changelog.read_text(encoding="utf-8-sig")
        )
        actual = match.group(1) if match else None
        if actual != expected:
            message = (
                f"repository_version {expected} != first published CHANGELOG version {actual}"
                if actual is not None
                else "CHANGELOG has no published semantic version"
            )
            errors.append(_finding("release-version", changelog, message, root))


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
            if (
                isinstance(target, str)
                and target in by_name
                and skill.get("status") in ("stable", "experimental")
                and by_name[target].get("status") == "deprecated"
            ):
                errors.append(
                    _finding(
                        "dependency-status",
                        root / "skills-manifest.yaml",
                        f"{name}: {skill['status']} skill cannot depend on deprecated {target}",
                        root,
                    )
                )

    graph = {
        name: sorted(
            target
            for target in skill.get("dependencies", [])
            if isinstance(target, str) and target in by_name
        )
        for name, skill in by_name.items()
        if isinstance(skill.get("dependencies"), list)
    }
    state: dict[str, int] = {}
    stack: list[str] = []
    positions: dict[str, int] = {}

    def visit(name: str) -> None:
        state[name] = 1
        positions[name] = len(stack)
        stack.append(name)
        for target in graph.get(name, []):
            if state.get(target, 0) == 0:
                visit(target)
            elif state[target] == 1:
                cycle = stack[positions[target] :] + [target]
                errors.append(
                    _finding(
                        "dependency-cycle",
                        root / "skills-manifest.yaml",
                        f"dependency cycle: {' -> '.join(cycle)}",
                        root,
                    )
                )
        stack.pop()
        positions.pop(name)
        state[name] = 2

    for name in sorted(graph):
        if state.get(name, 0) == 0:
            visit(name)


def _validate_dependency_references(
    skills: list[dict[str, Any]], root: Path, errors: list[dict[str, str]]
) -> None:
    """A declared dependency should be referenced by the skill's own docs."""
    for skill in skills:
        name = skill.get("name")
        deps = skill.get("dependencies")
        if not isinstance(name, str) or not isinstance(deps, list):
            continue
        skill_dir = root / name
        if not skill_dir.is_dir():
            continue
        texts = [
            path.read_text(encoding="utf-8-sig")
            for path in sorted(skill_dir.rglob("*.md"))
        ]
        blob = "\n".join(texts)
        for dep in deps:
            if not isinstance(dep, str) or not dep:
                continue
            if dep not in blob:
                errors.append(
                    _finding(
                        "dependency-reference",
                        skill_dir / "SKILL.md",
                        f"{name}: declared dependency {dep!r} is not referenced in its docs",
                        root,
                    )
                )


def _validate_usage_index(
    skills: list[dict[str, Any]], root: Path, errors: list[dict[str, str]]
) -> None:
    usage = root / "USAGE.md"
    if not usage.is_file():
        return

    targets: set[str] = set()
    text = usage.read_text(encoding="utf-8-sig")
    for raw_target in LINK_RE.findall(text):
        target = raw_target.strip().strip("<>")
        if " " in target and not raw_target.strip().startswith("<"):
            target = target.split(maxsplit=1)[0].strip('"')
        else:
            target = target.strip('"')
        local = target.split("#", 1)[0]
        if local.startswith("./"):
            local = local[2:]
        targets.add(local)

    for skill in skills:
        path = skill.get("path")
        if (
            not isinstance(path, str)
            or skill.get("status") == "deprecated"
            or skill.get("distribution") != "synchronized"
        ):
            continue
        expected = f"{path}/SKILL.md"
        if expected not in targets:
            errors.append(
                _finding(
                    "usage-index",
                    usage,
                    f"{skill.get('name')}: missing Markdown link target {expected}",
                    root,
                )
            )


def _manifest_dependency_edges(text: str) -> set[tuple[str, str]]:
    block = MANIFEST_DEPENDENCY_BLOCK_RE.search(text)
    if block is None:
        return set()

    edges: set[tuple[str, str]] = set()
    for line in block.group(1).splitlines():
        match = re.fullmatch(
            r"\s*`?([^`\s]+)`?\s*(?:-+>|─+>|→)\s*(.*?)\s*", line
        )
        if match is None:
            continue
        source = match.group(1)
        for raw_target in match.group(2).split("+"):
            target = raw_target.strip().strip("`")
            if target:
                edges.add((source, target))
    return edges


def _validate_invocation_graph(
    skills: list[dict[str, Any]], root: Path, errors: list[dict[str, str]]
) -> None:
    graph_path = root / "docs" / "governance" / "invocation-graph.md"
    if not graph_path.is_file():
        return

    documented = _manifest_dependency_edges(
        graph_path.read_text(encoding="utf-8-sig")
    )
    expected: set[tuple[str, str]] = set()
    for skill in skills:
        source = skill.get("name")
        dependencies = skill.get("dependencies")
        if not isinstance(source, str) or not isinstance(dependencies, list):
            continue
        for target in dependencies:
            if isinstance(target, str):
                expected.add((source, target))

    for source, target in sorted(expected - documented):
        errors.append(
            _finding(
                "invocation-graph",
                graph_path,
                f"{source} -> {target} missing from manifest dependency code block",
                root,
            )
        )
    for source, target in sorted(documented - expected):
        errors.append(
            _finding(
                "invocation-graph",
                graph_path,
                f"{source} -> {target} is not declared in manifest",
                root,
            )
        )


def _validate_skill(
    skill: dict[str, Any],
    root: Path,
    runtime_names: set[str],
    canonical_to_deployment: dict[str, str],
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
    lines = document.read_text(encoding="utf-8-sig").splitlines()
    description = _full_description(lines)
    if not description:
        errors.append(
            _finding(
                "description",
                document,
                f"{name}: description is missing or empty",
                root,
            )
        )
    elif len(description) < 12:
        warnings.append(
            _finding(
                "description-short",
                document,
                f"{name}: description only {len(description)} chars; add trigger terms for reliable routing",
                root,
            )
        )
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
    manifest_invocation = skill.get("invocation")
    if (manifest_invocation == "user") != disabled:
        errors.append(
            _finding(
                "invocation-parity",
                document,
                f"manifest says {manifest_invocation!r} but frontmatter disable-model-invocation is {str(disabled).lower()}",
                root,
            )
        )
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

    body = document.read_text(encoding="utf-8-sig")
    if USER_ONLY_BODY_RE.search(body):
        if manifest_invocation != "user" or not disabled:
            errors.append(
                _finding(
                    "invocation-semantic",
                    document,
                    "body declares user-only invocation but manifest/frontmatter allow model invocation",
                    root,
                )
            )
    if (
        WORKER_ONLY_BODY_RE.search(body)
        and manifest_invocation == "model"
        and name.startswith("my-note/")
    ):
        warnings.append(
            _finding(
                "invocation-semantic",
                document,
                f"{name}: body restricts direct invocation; consider invocation user if truly worker-only",
                root,
            )
        )

    line_count = len(body.splitlines())
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
        _validate_markdown(
            markdown, root, runtime_names, canonical_to_deployment, errors
        )


def _validate_document_authority(
    path: Path, text: str, root: Path, errors: list[dict[str, str]]
) -> None:
    """Enforce the repository's CONTEXT, ADR, and task-status boundaries."""
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    normalized = text.lower()

    if relative == "1-plan/references/context-format.md":
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
                "ADR template must be owned by 1-plan/references/adr-format.md",
                root,
            )
        )


def _validate_markdown(
    path: Path,
    root: Path,
    runtime_names: set[str],
    canonical_to_deployment: dict[str, str],
    errors: list[dict[str, str]],
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
    for reference in _slash_skill_references(text, runtime_names):
        if reference in HOST_COMMAND_ALLOWLIST:
            continue
        if reference.split("/", 1)[0] in SKILL_REF_EXCLUSIONS:
            continue
        if reference.endswith("-"):
            continue  # incomplete template token (e.g. <root>/report-<stamp>.md)
        if reference not in runtime_names:
            expected = canonical_to_deployment.get(reference)
            message = (
                f"canonical skill reference /{reference} is not deployed; use /{expected}"
                if expected is not None
                else f"unknown runtime skill reference /{reference}"
            )
            errors.append(
                _finding(
                    "skill-reference",
                    path,
                    message,
                    root,
                )
            )


def validate_repository(
    root: Path,
    *,
    check_claude_pointer: bool = False,
    check_claude_mirror: bool = False,
    claude_path: Path | None = None,
) -> dict[str, Any]:
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
    _validate_release_versions(manifest, root, errors)
    canonical = {
        skill["name"] for skill in skills if isinstance(skill.get("name"), str)
    }
    canonical_to_deployment = {
        skill["name"]: skill_manifest.deployment_name(skill["name"])
        for skill in skills
        if isinstance(skill.get("name"), str) and skill.get("status") != "deprecated"
    }
    runtime_names = set(canonical_to_deployment.values())
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
    _validate_dependency_references(skills, root, errors)
    _validate_usage_index(skills, root, errors)
    _validate_invocation_graph(skills, root, errors)
    for skill in sorted(skills, key=lambda item: str(item.get("name", ""))):
        _validate_skill(
            skill,
            root,
            runtime_names,
            canonical_to_deployment,
            errors,
            warnings,
        )
    navigation_docs = [root / "README.md", root / "USAGE.md", root / "CONTEXT.md"]
    governance_root = root / "docs" / "governance"
    if governance_root.is_dir():
        navigation_docs.extend(sorted(governance_root.rglob("*.md")))
    for markdown in navigation_docs:
        if markdown.is_file():
            _validate_markdown(
                markdown, root, runtime_names, canonical_to_deployment, errors
            )
    if check_claude_pointer or check_claude_mirror:
        _validate_claude_pointer(root, errors, claude_path)
    errors.sort(key=lambda item: (item["path"], item["code"], item["message"]))
    warnings.sort(key=lambda item: (item["path"], item["code"], item["message"]))
    return {"ok": not errors, "root": str(root), "errors": errors, "warnings": warnings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="emit a deterministic JSON report"
    )
    parser.add_argument(
        "--root", type=Path, default=SCRIPT_DIR.parent, help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--check-claude-pointer",
        action="store_true",
        help="require CLAUDE.md small-kernel route pointer",
    )
    parser.add_argument(
        "--check-claude-mirror",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--claude-md",
        type=Path,
        default=None,
        help="CLAUDE.md path (default: <root>/../CLAUDE.md)",
    )
    args = parser.parse_args(argv)
    report = validate_repository(
        args.root,
        check_claude_pointer=args.check_claude_pointer,
        check_claude_mirror=args.check_claude_mirror,
        claude_path=args.claude_md,
    )
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
