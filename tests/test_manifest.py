#!/usr/bin/env python3
"""Unit tests for skill_manifest.py"""

import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from skill_manifest import _scalar, load_manifest, SEMVER


class TestScalarParsing(unittest.TestCase):
    """Test the _scalar function that parses YAML scalar values."""

    def test_parse_true(self):
        self.assertIs(_scalar("true", 1), True)
        self.assertIs(_scalar("  true  ", 1), True)

    def test_parse_false(self):
        self.assertIs(_scalar("false", 1), False)
        self.assertIs(_scalar("  false  ", 1), False)

    def test_parse_empty_list(self):
        self.assertEqual(_scalar("[]", 1), [])
        self.assertEqual(_scalar("  []  ", 1), [])

    def test_parse_inline_list(self):
        self.assertEqual(_scalar("[a, b, c]", 1), ["a", "b", "c"])
        self.assertEqual(
            _scalar("[claude, cursor, codex]", 1), ["claude", "cursor", "codex"]
        )

    def test_parse_integer(self):
        self.assertEqual(_scalar("123", 1), 123)
        self.assertEqual(_scalar("0", 1), 0)

    def test_parse_string(self):
        self.assertEqual(_scalar("test-string", 1), "test-string")
        self.assertEqual(_scalar("user", 1), "user")

    def test_empty_value_raises(self):
        with self.assertRaises(ValueError):
            _scalar("", 1)
        with self.assertRaises(ValueError):
            _scalar("   ", 1)

    def test_quoted_value_raises(self):
        with self.assertRaises(ValueError):
            _scalar('"quoted"', 1)
        with self.assertRaises(ValueError):
            _scalar("'quoted'", 1)


class TestSemverRegex(unittest.TestCase):
    """Test the semantic version regex."""

    def test_valid_semver(self):
        self.assertIsNotNone(SEMVER.fullmatch("1.0.0"))
        self.assertIsNotNone(SEMVER.fullmatch("10.20.30"))
        self.assertIsNotNone(SEMVER.fullmatch("0.0.1"))

    def test_invalid_semver(self):
        self.assertIsNone(SEMVER.fullmatch("1.0"))
        self.assertIsNone(SEMVER.fullmatch("v1.0.0"))
        self.assertIsNone(SEMVER.fullmatch("1.0.0-beta"))
        self.assertIsNone(SEMVER.fullmatch("1.0.0.0"))


if __name__ == "__main__":
    unittest.main()
