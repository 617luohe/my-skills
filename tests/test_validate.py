#!/usr/bin/env python3
"""Unit tests for validate_skills.py"""

import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_skills import BANNED_SKILLS, LINK_RE, SLASH_SKILL_RE


class TestBannedSkills(unittest.TestCase):
    """Test banned skills constant."""

    def test_banned_skills_tuple(self):
        self.assertIsInstance(BANNED_SKILLS, tuple)
        self.assertGreater(len(BANNED_SKILLS), 0)

    def test_banned_skills_content(self):
        expected = ("0--Agent统筹", "0--auto-iteration", "0--graphify")
        self.assertEqual(BANNED_SKILLS, expected)


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


if __name__ == "__main__":
    unittest.main()
