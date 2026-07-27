#!/usr/bin/env python3
"""Unit tests for validate_skills.py"""

import json
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_skills import (
    BANNED_SKILLS,
    LINK_RE,
    SLASH_SKILL_RE,
    _validate_document_authority,
    _validate_eval,
)


class TestBannedSkills(unittest.TestCase):
    """Test banned skills constant."""

    def test_banned_skills_tuple(self):
        self.assertIsInstance(BANNED_SKILLS, tuple)
        self.assertGreater(len(BANNED_SKILLS), 0)

    def test_banned_skills_content(self):
        expected = ("0--Agent统筹", "0--auto-iteration", "0--graphify")
        self.assertEqual(BANNED_SKILLS, expected)


class TestHighRiskEvalCoverage(unittest.TestCase):
    """Verify the bundled eval contract covers its high-risk branches."""

    EVAL_PATHS = {
        "2-开发": "2-开发/evals/evals.json",
        "3-检查": "3-检查/evals/evals.json",
        "4-调试": "4-调试/evals/evals.json",
        "diagnosing-bugs": "vocabulary/diagnosing-bugs/evals/evals.json",
        "5-版本管理": "5-版本管理/evals/evals.json",
        "multi-worker": "multi-worker/evals/evals.json",
        "0-询问luohe": "0-询问luohe/evals/evals.json",
    }

    def _cases(self, skill_name):
        path = REPO_ROOT / self.EVAL_PATHS[skill_name]
        self.assertTrue(path.is_file(), path)
        return json.loads(path.read_text(encoding="utf-8"))["evals"]

    def test_high_risk_eval_files_are_bundled_per_owner(self):
        for skill_name, relative_path in self.EVAL_PATHS.items():
            self.assertIn(skill_name, Path(relative_path).parts)

    def test_key_scenarios_are_covered(self):
        required_terms = {
            "2-开发": ("git commit", "/3-"),
            "3-检查": ("base", "issue", "Jira", "tracker"),
            "4-调试": ("trace", "metrics"),
            "diagnosing-bugs": ("不伪造", "根因证据"),
            "5-版本管理": ("git commit", "git push -u origin"),
            "multi-worker": ("tasks.md", "worker_failed", "integration_failed"),
            "0-询问luohe": ("docs/analysis/", "docs/prototypes/", "docs/plans/"),
        }
        for skill_name, terms in required_terms.items():
            text = json.dumps(self._cases(skill_name), ensure_ascii=False)
            for term in terms:
                self.assertIn(term, text, f"{skill_name} must cover {term}")


class TestEvalQualityValidation(unittest.TestCase):
    def test_rejects_empty_expected_output_and_vague_expectations(self):
        payload = {
            "skill_name": "example",
            "evals": [{
                "id": 1,
                "prompt": "Review this change.",
                "expected_output": "",
                "files": [],
                "expectations": ["be good"],
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "evals.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            errors = []
            _validate_eval(path, "example", root, errors)
        self.assertEqual(errors[0]["code"], "eval-shape")


class TestLinkRegex(unittest.TestCase):
    """Test markdown link pattern matching."""

    def test_simple_link(self):
        matches = LINK_RE.findall("[text](url)")
        self.assertEqual(matches, ["url"])

    def test_image_link(self):
        matches = LINK_RE.findall("![alt](image.png)")
        self.assertEqual(matches, ["image.png"])

    def test_multiple_links(self):
        text = "[link1](url1) and [link2](url2)"
        matches = LINK_RE.findall(text)
        self.assertEqual(matches, ["url1", "url2"])

    def test_no_links(self):
        matches = LINK_RE.findall("just plain text")
        self.assertEqual(matches, [])


class TestSlashSkillRegex(unittest.TestCase):
    """Test slash skill reference pattern matching."""

    def test_simple_skill_reference(self):
        matches = SLASH_SKILL_RE.findall("use /code-review here")
        self.assertEqual(matches, ["code-review"])

    def test_numbered_skill_reference(self):
        matches = SLASH_SKILL_RE.findall("try /2-开发 skill")
        self.assertEqual(matches, ["2-开发"])

    def test_multiple_references(self):
        text = "use /skill-one and /skill-two"
        matches = SLASH_SKILL_RE.findall(text)
        self.assertEqual(set(matches), {"skill-one", "skill-two"})

    def test_ignore_double_slash(self):
        matches = SLASH_SKILL_RE.findall("path //comment")
        self.assertEqual(matches, [])

    def test_ignore_url(self):
        matches = SLASH_SKILL_RE.findall("https://example.com/path")
        self.assertEqual(matches, [])


class TestDocumentAuthority(unittest.TestCase):
    """Test CONTEXT, ADR, and task-status authority boundaries."""

    def test_accepts_authoritative_document_locations(self):
        errors = []
        root = Path("/repository")
        _validate_document_authority(
            Path("/repository/vocabulary/domain-modeling/SKILL.md"),
            """\
CONTEXT.md is a glossary of domain terms.
Record architecture decisions in `docs/adr/NNNN-title.md`.
Record task status in `plans/tasks/issue/handoff`.
Use [the ADR template](references/adr-format.md).
""",
            root,
            errors,
        )
        self.assertEqual(errors, [])

    def test_rejects_embedded_adr_in_context_format(self):
        errors = []
        root = Path("/repository")
        path = root / "1-规划/references/context-format.md"
        _validate_document_authority(
            path,
            "## Architecture Decision Records (ADR)\n### ADR-001: embedded decision",
            root,
            errors,
        )
        self.assertEqual(errors[0]["code"], "context-authority")

    def test_rejects_unpublished_cross_skill_adr_template(self):
        errors = []
        root = Path("/repository")
        path = root / "vocabulary/domain-modeling/SKILL.md"
        _validate_document_authority(
            path,
            "Use the template defined in `/references/adr-format.md`.",
            root,
            errors,
        )
        self.assertEqual(errors[0]["code"], "adr-template-owner")
