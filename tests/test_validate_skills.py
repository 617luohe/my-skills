from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_skills.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_skills", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RepositoryValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = load_validator()

    def test_source_repository_is_valid_with_only_size_warnings(self) -> None:
        report = self.validator.validate_repository(ROOT)
        self.assertEqual([], report["errors"])
        self.assertTrue(all(item["code"] == "skill-size" for item in report["warnings"]))

    def test_cli_json_is_deterministic_and_successful(self) -> None:
        command = [sys.executable, str(MODULE_PATH), "--json"]
        first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
        second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        payload = json.loads(first.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(str(ROOT.resolve()), payload["root"])

    def test_frontmatter_name_and_invocation_parity_are_checked(self) -> None:
        with self.fixture() as root:
            skill = root / "alpha"
            self.write_skill(skill, "wrong", model_disabled=True)
            self.write_openai(skill, implicit=True)
            report = self.validator.validate_repository(root)
        codes = {item["code"] for item in report["errors"]}
        self.assertIn("frontmatter-name", codes)
        self.assertIn("invocation-parity", codes)

    def test_dependency_target_and_direction_are_checked(self) -> None:
        with self.fixture(
            [("alpha", "synchronized", ["missing", "beta"]), ("beta", "host-provided", [])]
        ) as root:
            self.write_skill(root / "alpha", "alpha")
            self.write_openai(root / "alpha", implicit=True)
            self.write_skill(root / "beta", "beta")
            report = self.validator.validate_repository(root)
        codes = [item["code"] for item in report["errors"]]
        self.assertIn("dependency-target", codes)
        self.assertIn("dependency-direction", codes)

    def test_links_routes_evals_and_banned_references_are_checked(self) -> None:
        with self.fixture() as root:
            skill = root / "alpha"
            self.write_skill(
                skill,
                "alpha",
                body="[missing](references/nope.md) ![missing](references/image.png) /0--unknown 0--auto-iteration\n",
            )
            self.write_openai(skill, implicit=True)
            (skill / "evals").mkdir()
            (skill / "evals" / "evals.json").write_text('{"skill_name":"wrong","evals":{}}', encoding="utf-8")
            report = self.validator.validate_repository(root)
        codes = {item["code"] for item in report["errors"]}
        self.assertTrue(
            {"markdown-link", "skill-reference", "eval-shape", "banned-skill-reference"}.issubset(codes)
        )

    def test_skill_size_thresholds(self) -> None:
        with self.fixture() as root:
            skill = root / "alpha"
            self.write_skill(skill, "alpha", body="\n".join(["line"] * 501))
            self.write_openai(skill, implicit=True)
            report = self.validator.validate_repository(root)
        self.assertIn("skill-size", {item["code"] for item in report["errors"]})

    def test_deployment_check_requires_exact_names_and_hashes(self) -> None:
        with self.fixture() as root:
            skill = root / "alpha"
            self.write_skill(skill, "alpha")
            self.write_openai(skill, implicit=True)
            parent = root.parent
            for host in (".claude", ".cursor", ".codex"):
                target = parent / host / "skills" / "alpha"
                shutil.copytree(skill, target)
            self.assertEqual([], self.validator.validate_repository(root, check_deployments=True)["errors"])
            (parent / ".codex" / "skills" / "alpha" / "SKILL.md").write_text("changed\n", encoding="utf-8")
            report = self.validator.validate_repository(root, check_deployments=True)
        self.assertIn("deployment-hash", {item["code"] for item in report["errors"]})

    def fixture(self, entries=None):
        return ValidationFixture(entries or [("alpha", "synchronized", [])])

    @staticmethod
    def write_skill(path: Path, name: str, model_disabled: bool = False, body: str = "") -> None:
        path.mkdir(parents=True, exist_ok=True)
        disabled = "disable-model-invocation: true\n" if model_disabled else ""
        text = f"---\nname: {name}\ndescription: Test skill.\n{disabled}---\n\n# Test\n{body}"
        (path / "SKILL.md").write_text(text, encoding="utf-8")

    @staticmethod
    def write_openai(path: Path, implicit: bool) -> None:
        agents = path / "agents"
        agents.mkdir(parents=True, exist_ok=True)
        policy = "\npolicy:\n  allow_implicit_invocation: false" if not implicit else ""
        (agents / "openai.yaml").write_text(
            f'interface:\n  display_name: "Test"\n  short_description: "Test skill"{policy}\n',
            encoding="utf-8",
        )


class ValidationFixture:
    def __init__(self, entries):
        self.entries = entries
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "my-skills"

    def __enter__(self) -> Path:
        self.root.mkdir()
        manifest = ["schema_version: 1", "repository_version: 1.0.0", "skills:"]
        for name, distribution, dependencies in self.entries:
            invocation = "model"
            sync = "true" if distribution == "synchronized" else "false"
            deps = "[" + ", ".join(dependencies) + "]"
            manifest.extend(
                [
                    f"  - name: {name}",
                    f"    path: {name}",
                    "    version: 1.0.0",
                    "    status: stable",
                    f"    invocation: {invocation}",
                    "    hosts: [claude, cursor, codex]",
                    f"    distribution: {distribution}",
                    f"    sync: {sync}",
                    f"    dependencies: {deps}",
                ]
            )
        (self.root / "skills-manifest.yaml").write_text("\n".join(manifest) + "\n", encoding="utf-8")
        return self.root

    def __exit__(self, exc_type, exc, tb) -> None:
        self.temp.cleanup()


if __name__ == "__main__":
    unittest.main()
