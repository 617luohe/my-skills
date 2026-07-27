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


class TestMultiWorkerContract(unittest.TestCase):
    """Prevent unsafe implicit orchestration and premature cleanup."""

    def test_multi_worker_is_user_invoked_everywhere(self):
        skill = (REPO_ROOT / "multi-worker" / "SKILL.md").read_text(encoding="utf-8")
        openai = (REPO_ROOT / "multi-worker" / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        manifest = (REPO_ROOT / "skills-manifest.yaml").read_text(encoding="utf-8")
        usage = (REPO_ROOT / "USAGE.md").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("disable-model-invocation: true", skill)
        self.assertIn("allow_implicit_invocation: false", openai)
        self.assertIn("name: multi-worker\n    path: multi-worker", manifest)
        multi_worker_manifest = manifest.split("  - name: multi-worker", 1)[1].split(
            "  - name:", 1
        )[0]
        self.assertIn("invocation: user", multi_worker_manifest)
        self.assertIn("仅可由用户显式调用", usage)
        self.assertIn("消费已确认任务", usage)
        self.assertNotIn("管理内置 worker 的任务拆解", usage)
        self.assertIn("**仅用户调用**", readme)

    def test_multi_worker_requires_confirmed_tasks_file_and_never_invokes_planning(self):
        skill = (REPO_ROOT / "multi-worker" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("已由用户确认的 `tasks.md`", skill)
        self.assertIn("停止，不得拆解、建分支或派发", skill)
        self.assertIn("请用户显式运行 `/1-规划`", skill)
        self.assertNotIn("调用 `/1-规划`", skill)
        self.assertNotIn("调用 `/2-开发`", skill)

    def test_multi_worker_failure_blocks_cleanup_and_completion(self):
        skill = (REPO_ROOT / "multi-worker" / "SKILL.md").read_text(encoding="utf-8")

        for failure in ("worker_failed", "merge_failed", "integration_failed"):
            self.assertIn(failure, skill)
        self.assertIn("保留全部 worktree", skill)
        self.assertIn("不得报告完成", skill)
        self.assertIn("完整测试套件", skill)
        self.assertIn("lint / type check", skill)
        self.assertIn("集成 diff 最终 review", skill)
        self.assertIn("全部通过后才清理 worktree", skill)


if __name__ == "__main__":
    unittest.main()
