#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression tests for the development, review, and versioning workflow."""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestDevelopmentReviewVersioningContract(unittest.TestCase):
    """Keep Git commits out of the default development-to-review path."""

    def test_development_hands_off_uncommitted_changes_to_review(self):
        development = (REPO_ROOT / "2-开发" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("审查基点", development)
        self.assertIn("需求来源", development)
        self.assertIn("不执行 `git commit`", development)
        self.assertNotIn("### 5. 提交", development)
        self.assertNotIn("git commit -m", development)

    def test_review_requires_explicit_user_authorization_before_versioning(self):
        review = (REPO_ROOT / "3-检查" / "SKILL.md").read_text(encoding="utf-8")
        versioning = (REPO_ROOT / "5-版本管理" / "SKILL.md").read_text(encoding="utf-8")
        review_core = (REPO_ROOT / "vocabulary" / "code-review" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("审查通过", review)
        self.assertIn("用户明确授权", review)
        self.assertIn("用户明确授权", versioning)
        self.assertIn("git diff --cached", review_core)
        self.assertIn("无新增提交，审查未提交改动", review_core)


if __name__ == "__main__":
    unittest.main()
