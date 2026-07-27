"""Progressive-disclosure contract tests for diagnosing-bugs."""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "vocabulary" / "diagnosing-bugs" / "SKILL.md"
REFERENCES = SKILL.parent / "references"


class TestDiagnosingBugsProgressiveDisclosure(unittest.TestCase):
    def setUp(self):
        self.text = SKILL.read_text(encoding="utf-8")
        self.lines = self.text.splitlines()

    def test_skill_is_under_recommended_size_limit(self):
        self.assertLessEqual(len(self.lines), 200)

    def test_six_stages_have_checkable_exit_gates(self):
        for stage in (
            "构建反馈回路",
            "复现与最小化",
            "假设",
            "工具验证",
            "修复与验收",
            "清理",
        ):
            self.assertIn(stage, self.text)
        self.assertGreaterEqual(self.text.count("完成条件"), 6)

    def test_core_diagnostic_gates_remain_in_main_skill(self):
        for gate in (
            "可比较的观测信号",
            "根因证据",
            "一次只改一个变量",
            "稳定或统计可信",
            "统计可信改善",
            "回归测试",
            "临时调试代码",
        ):
            self.assertIn(gate, self.text)

    def test_reference_links_have_context_pointers_and_resolve(self):
        pointers = {
            "references/intermittent-failures.md": "偶发、时序或并发",
            "references/performance.md": "性能回归",
            "references/memory.md": "内存增长",
            "references/tooling.md": "按语言、运行环境",
        }
        for relative_path, context in pointers.items():
            self.assertIn(f"]({relative_path})", self.text)
            self.assertIn(context, self.text)
            self.assertTrue((SKILL.parent / relative_path).is_file())


if __name__ == "__main__":
    unittest.main()
