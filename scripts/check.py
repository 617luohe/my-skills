#!/usr/bin/env python3
"""单一门禁入口：先跑源码治理校验，通过后再跑 pytest。CI 与本地共用这一条。

父仓库根目录执行：``python my-skills/scripts/check.py``
CI 执行：``python scripts/check.py --claude-md 0-claude/references/template.md``
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--claude-md",
        type=Path,
        default=ROOT.parent / "CLAUDE.md",
        help="CLAUDE.md 指针检查目标；文件不存在时跳过该项检查",
    )
    args = parser.parse_args(argv)

    validate = [sys.executable, str(ROOT / "scripts" / "validate_skills.py")]
    if args.claude_md.is_file():
        validate += ["--check-claude-pointer", "--claude-md", str(args.claude_md)]
    else:
        print(f"skip CLAUDE.md pointer check: {args.claude_md} not found")

    status = subprocess.call(validate)
    if status != 0:
        return status
    return subprocess.call([sys.executable, "-m", "pytest", "-q"], cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
