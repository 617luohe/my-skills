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

    def test_check_routes_from_input_contract_without_mode_prompt(self):
        review = (REPO_ROOT / "3-检查" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("fixed point/base", review)
        self.assertIn("spec/需求来源", review)
        self.assertIn("diff 审查意图", review)
        self.assertIn("强制进入 Review", review)
        self.assertIn("不再询问模式", review)
        self.assertIn("立即修复", review)
        self.assertIn("/4-调试", review)
        self.assertIn("仅在输入确实模糊时", review)
        self.assertIn("一个澄清问题", review)

    def test_bug_reporting_uses_one_detected_tracker_and_stops_safely(self):
        review = (REPO_ROOT / "3-检查" / "SKILL.md").read_text(encoding="utf-8")
        bug_report = review.split("## Bug 报告 — 只建单", 1)[1].split("## 边界", 1)[0]

        self.assertIn("GitHub（`gh`）", bug_report)
        self.assertIn("GitLab（`glab`）", bug_report)
        self.assertIn("Jira", bug_report)
        self.assertIn("探测 → 查重 → 创建 → URL/编号", bug_report)
        self.assertIn("同一 tracker", bug_report)
        self.assertIn("标题、完整正文和目标 tracker", bug_report)
        self.assertIn("用户确认", bug_report)
        self.assertIn("不跨 tracker 回退", bug_report)
        self.assertIn("CLI 缺失", bug_report)
        self.assertIn("认证失败", bug_report)
        self.assertIn("查重失败", bug_report)
        self.assertIn("创建失败", bug_report)

    def test_bug_reporting_never_uses_gh_for_gitlab_or_jira(self):
        review = (REPO_ROOT / "3-检查" / "SKILL.md").read_text(encoding="utf-8")
        bug_report = review.split("## Bug 报告 — 只建单", 1)[1].split("## 边界", 1)[0]
        gitlab = bug_report.split("### GitLab", 1)[1].split("### Jira", 1)[0]
        jira = bug_report.split("### Jira", 1)[1].split("### 无远程", 1)[0]

        self.assertIn("`glab`", gitlab)
        self.assertIn("不改用 `gh`", gitlab)
        self.assertNotIn("`gh issue", gitlab)
        self.assertIn("不执行 `gh`、`glab`", jira)
        self.assertIn("任何别的平台 CLI", jira)

    def test_jira_and_missing_tracker_create_docs_issue_drafts_without_false_creation(self):
        review = (REPO_ROOT / "3-检查" / "SKILL.md").read_text(encoding="utf-8")
        bug_report = review.split("## Bug 报告 — 只建单", 1)[1].split("## 边界", 1)[0]
        jira = bug_report.split("### Jira", 1)[1].split("### 无远程", 1)[0]
        no_tracker = bug_report.split("### 无远程", 1)[1]

        for section in (jira, no_tracker):
            self.assertIn("`docs/issues/", section)
            self.assertIn("未提交", section)
        self.assertIn("不得声称已自动创建", jira)
        self.assertIn("不声称远程 issue 已创建", no_tracker)

    def test_check_review_decision_is_a_formal_optional_versioning_handoff(self):
        review = (REPO_ROOT / "3-检查" / "SKILL.md").read_text(encoding="utf-8")
        review_core = (REPO_ROOT / "vocabulary" / "code-review" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        for verdict in ("PASS", "PASS WITH WARNINGS", "FAIL"):
            self.assertIn(verdict, review)
            self.assertIn(verdict, review_core)
        self.assertIn("正式交接产物", review)
        self.assertIn("可选进入 `/5-版本管理`", review)
        self.assertIn("用户明确授权", review)

    def test_router_includes_independent_review_issue_only_and_root_cause_paths(self):
        router = (REPO_ROOT / "0-询问luohe" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("独立 Review", router)
        self.assertIn("只建单", router)
        self.assertIn("根因修复", router)
        self.assertIn("/3-检查", router)
        self.assertIn("/4-调试", router)

    def test_review_routing_is_documented_in_usage_readme_and_template(self):
        usage = (REPO_ROOT / "USAGE.md").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        template = (REPO_ROOT / "0--claude" / "references" / "template.md").read_text(
            encoding="utf-8"
        )

        for document in (usage, readme, template):
            self.assertIn("/3-检查", document)
            self.assertIn("/4-调试", document)
        self.assertIn("只建单", usage)
        self.assertIn("根因修复", readme)
        self.assertIn("输入契约", template)


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
