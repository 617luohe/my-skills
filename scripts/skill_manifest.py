#!/usr/bin/env python3
"""Read the repository's deliberately restricted skills manifest.

This is not a general YAML implementation. It accepts only the manifest shape used
by this repository: top-level scalars and a ``skills`` sequence of flat mappings
whose values are scalars or inline scalar lists.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
REQUIRED_FIELDS = {
    "name",
    "path",
    "version",
    "status",
    "invocation",
    "hosts",
    "distribution",
    "sync",
    "dependencies",
}
OPTIONAL_FIELDS = {"layer", "deprecated_note", "category"}
ALLOWED_CATEGORIES = frozenset(
    {"router", "main-flow", "extension", "standalone", "vocabulary", "my-note"}
)


def _scalar(text: str, line_number: int) -> Any:
    value = text.strip()
    if not value:
        raise ValueError(f"line {line_number}: empty values are not supported")
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        if not body:
            return []
        items = [item.strip() for item in body.split(",")]
        if any(not item or "[" in item or "]" in item for item in items):
            raise ValueError(f"line {line_number}: invalid inline list")
        return items
    if value.isdigit():
        return int(value)
    if value[0] in "'\"" or value[-1] in "'\"":
        raise ValueError(f"line {line_number}: quoted scalars are not supported")
    return value


def load_manifest(path: Path) -> dict[str, Any]:
    document: dict[str, Any] = {}
    skills: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()

        if indent == 0:
            current = None
            if stripped == "skills:":
                document["skills"] = skills
                continue
            key, separator, value = stripped.partition(":")
            if not separator or not key or key in document:
                raise ValueError(
                    f"line {line_number}: invalid or duplicate top-level key"
                )
            document[key] = _scalar(value, line_number)
            continue

        if indent == 2 and stripped.startswith("- "):
            key, separator, value = stripped[2:].partition(":")
            if not separator or not key:
                raise ValueError(f"line {line_number}: invalid skill entry")
            current = {key: _scalar(value, line_number)}
            skills.append(current)
            continue

        if indent == 4 and current is not None:
            key, separator, value = stripped.partition(":")
            if not separator or not key or key in current:
                raise ValueError(
                    f"line {line_number}: invalid or duplicate skill field"
                )
            current[key] = _scalar(value, line_number)
            continue

        raise ValueError(f"line {line_number}: unsupported YAML structure")

    if "skills" not in document:
        raise ValueError("manifest must contain a skills sequence")
    return document


def safe_skill_path(value: Any) -> bool:
    """Return whether value is a relative, traversal-free skill path."""
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    if value.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", value):
        return False
    parts = value.split("/")
    return all(part and part not in {".", ".."} for part in parts)


def deployment_name(name: str) -> str:
    """Map a canonical nested name to its deterministic flat deployment name."""
    return name.rsplit("/", 1)[-1]


def publication(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    if manifest.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    repository_version = manifest.get("repository_version")
    if not isinstance(repository_version, str) or not SEMVER.fullmatch(
        repository_version
    ):
        raise ValueError("repository_version must be a semantic version")

    seen_names: set[str] = set()
    seen_deployment_names: dict[str, str] = {}
    published: list[dict[str, str]] = []
    host_provided = 0
    for index, skill in enumerate(manifest["skills"], 1):
        missing = REQUIRED_FIELDS - skill.keys()
        extra = skill.keys() - REQUIRED_FIELDS - OPTIONAL_FIELDS
        if missing or extra:
            raise ValueError(
                f"skill {index}: fields mismatch; missing={sorted(missing)}, extra={sorted(extra)}"
            )
        name = skill["name"]
        if not isinstance(name, str) or name in seen_names or not safe_skill_path(name):
            raise ValueError(f"skill {index}: name must be a unique safe relative path")
        seen_names.add(name)
        if skill["path"] != name or not safe_skill_path(skill["path"]):
            raise ValueError(f"skill {name}: path must equal a safe name")
        if skill["version"] != repository_version:
            raise ValueError(f"skill {name}: version must equal repository_version")
        if skill["status"] not in ("stable", "deprecated", "experimental"):
            raise ValueError(f"skill {name}: status must be stable, deprecated, or experimental")
        if skill["status"] == "deprecated":
            if (
                not isinstance(skill.get("deprecated_note"), str)
                or not skill["deprecated_note"]
            ):
                raise ValueError(f"skill {name}: deprecated requires deprecated_note")
            if skill["invocation"] != "user":
                raise ValueError(f"skill {name}: deprecated invocation must be user")
        if skill["invocation"] not in ("user", "model"):
            raise ValueError(f"skill {name}: invocation must be user or model")
        if skill["hosts"] != ["claude", "cursor", "codex"]:
            raise ValueError(f"skill {name}: hosts must be [claude, cursor, codex]")
        if not isinstance(skill["dependencies"], list):
            raise ValueError(f"skill {name}: dependencies must be a list")

        source = root / skill["path"]
        if not source.is_dir() or not (source / "SKILL.md").is_file():
            raise ValueError(f"skill {name}: source directory or SKILL.md is missing")

        if skill["distribution"] == "synchronized":
            if skill["sync"] is not True:
                raise ValueError(
                    f"skill {name}: synchronized skills must set sync true"
                )
            flat_name = deployment_name(name)
            previous = seen_deployment_names.get(flat_name)
            if previous is not None:
                raise ValueError(
                    f"deployment name collision: {name} and {previous} both map to {flat_name}"
                )
            seen_deployment_names[flat_name] = name
            published.append(
                {
                    "name": name,
                    "path": skill["path"],
                    "deployment_name": flat_name,
                    **(
                        {
                            "status": "deprecated",
                            "deprecated_note": skill["deprecated_note"],
                        }
                        if skill["status"] == "deprecated"
                        else {}
                    ),
                }
            )
        elif skill["distribution"] == "host-provided":
            host_provided += 1
            if skill["sync"] is not False or skill["invocation"] != "model":
                raise ValueError(
                    f"skill {name}: host-provided skills must set sync false and invocation model"
                )
        else:
            raise ValueError(f"skill {name}: unsupported distribution")

    return {
        "generated_by": "scripts/skill_manifest.py from skills-manifest.yaml",
        "schema_version": manifest["schema_version"],
        "repository_version": repository_version,
        "synchronized_count": len(published),
        "host_provided_count": host_provided,
        "skills": published,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("publication",))
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "skills-manifest.yaml",
    )
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    result = publication(load_manifest(manifest_path), manifest_path.parent)
    json.dump(result, fp=__import__("sys").stdout, ensure_ascii=True, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
