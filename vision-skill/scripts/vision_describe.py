#!/usr/bin/env python3
"""Vision 描述脚本：为纯文本模型补视觉。

把本地图片 / 图片 URL 交给视觉 API 模型（OpenCode Go 套餐），返回结构化文字描述。
纯文本模型（如 DeepSeek）不直接看图，只读本脚本输出的 description。

配置（环境变量，均可选，未设时用默认）：
  VISION_API_URL    OpenAI 兼容 base_url，默认 https://opencode.ai/zen/go/v1
  VISION_API_KEY    优先于 cc-switch 数据库；未设则尝试从 ~/.cc-switch/cc-switch.db 读
  VISION_MODEL      视觉模型，默认 minimax-m3
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_BASE_URL = "https://opencode.ai/zen/go/v1"
DEFAULT_MODEL = "minimax-m3"
MODEL_NAMES = {
    "minimax-m3": "MiniMax M3（视觉，成本低）",
    "qwen3.8-max": "Qwen3.8-Max（视觉，更强）",
    "glm-5.2": "GLM 5.2",
    "kimi-k2.7-code": "Kimi K2.7 Code",
    "gpt-5.6-luna": "gpt-5.6-luna",
    "deepseek-v4-flash": "DeepSeek V4 Flash（纯文本，不支持图片）",
    "deepseek-v4-pro": "DeepSeek V4 Pro（纯文本，不支持图片）",
}
ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
MAX_MEDIA_BYTES = 20 * 1024 * 1024  # base64 后约 27MB，超出多数 API 限制
DEFAULT_PROMPT = (
    "你是一个视觉描述器。请依次用中文描述这张图（多图则逐张说明）："
    "1) 整体内容与场景；2) 布局与关键元素；3) 图中所有可见文字（OCR，逐字保留）；"
    "4) 对图表/截图给出结构化要点。只描述你实际看到的内容，不要推测图中不存在的东西。"
)
THINK_RE = re.compile(r"<think>.*?</think>", re.S)


def _ensure_utf8() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def read_cc_switch_key() -> str | None:
    """从 cc-switch 数据库读取 OpenCode Go 的 apiKey。"""
    db = Path.home() / ".cc-switch" / "cc-switch.db"
    if not db.is_file():
        return None
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        try:
            row = con.execute(
                "SELECT settings_config FROM providers WHERE id='opencode-go'"
            ).fetchone()
        finally:
            con.close()
    except sqlite3.Error:
        return None
    if not row:
        return None
    try:
        cfg = json.loads(row[0])
        return cfg["options"].get("apiKey")
    except (json.JSONDecodeError, KeyError, AttributeError):
        return None


def load_config(env: dict[str, str]) -> dict[str, str]:
    """解析配置：环境变量 > 默认值；key 最后兜底 cc-switch。"""
    api_key = env.get("VISION_API_KEY") or read_cc_switch_key()
    return {
        "base_url": env.get("VISION_API_URL", DEFAULT_BASE_URL).rstrip("/"),
        "api_key": api_key,
        "model": env.get("VISION_MODEL", DEFAULT_MODEL),
    }


def is_url(value: str) -> bool:
    return value.lower().startswith(("http://", "https://"))


def encode_image(path: str) -> str:
    """本地图片 -> base64 data URL。"""
    p = Path(path)
    if not p.is_file():
        raise ValueError(f"文件不存在: {path}")
    if p.suffix.lower() not in ALLOWED_EXTS:
        raise ValueError(
            f"不支持的图片类型: {p.suffix or '(无扩展名)'}，支持 {'/'.join(sorted(ALLOWED_EXTS))}"
        )
    data = p.read_bytes()
    if len(data) > MAX_MEDIA_BYTES:
        raise ValueError(
            f"图片过大（{len(data) / 1024 / 1024:.1f}MB > 20MB），请压缩后再试"
        )
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(data).decode()


def strip_think(content: str) -> str:
    """防御性清理：去掉模型内联在 content 里的 <think> 思维链。"""
    cleaned = THINK_RE.sub("", content)
    return cleaned.strip() or content.strip()


def describe(
    images: list[str],
    prompt: str,
    *,
    base_url: str,
    api_key: str,
    model: str,
    timeout: int,
    thinking: bool,
) -> tuple[str, dict]:
    """调用视觉 API 返回 (描述文本, 用量信息)。images 为 data URL 或 http(s) URL。"""
    if not api_key:
        raise RuntimeError(
            "未找到 API key：请设置环境变量 VISION_API_KEY，或在 cc-switch 中配置 OpenCode Go"
        )
    content: list[dict] = [{"type": "text", "text": prompt}]
    content += [{"type": "image_url", "image_url": {"url": url}} for url in images]
    body: dict = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 2048,
        "thinking": {"type": "enabled" if thinking else "disabled"},
    }
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) vision-skill",
        },
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        raise RuntimeError(f"API 请求失败 HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"网络请求失败: {exc.reason}") from exc

    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"API 返回空结果: {str(data)[:200]}")
    message = choices[0].get("message") or {}
    content_text = message.get("content") or ""
    if not content_text:
        raise RuntimeError("API 返回内容为空，请重试或换模型（--model qwen3.8-max）")
    usage = data.get("usage") or {}
    return strip_think(content_text), {
        "model": model,
        "elapsed_s": round(time.monotonic() - started, 1),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="为纯文本模型生成图片描述（OpenCode Go 视觉 API）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  vision_describe.py screenshot.png\n"
            "  vision_describe.py a.png b.png --model qwen3.8-max\n"
            "  vision_describe.py https://example.com/img.png\n"
        ),
    )
    parser.add_argument("media", nargs="*", help="图片路径或 http(s) URL，可多个")
    parser.add_argument("--model", help=f"视觉模型，默认 {DEFAULT_MODEL}")
    parser.add_argument("--prompt", help="自定义描述提示词（默认中文结构化描述）")
    parser.add_argument(
        "--thinking", action="store_true", help="开启模型推理（更准但更贵更慢）"
    )
    parser.add_argument("--timeout", type=int, default=90, help="请求超时秒数，默认 90")
    parser.add_argument(
        "--list-models", action="store_true", help="列出 OpenCode Go 可用模型"
    )
    parser.add_argument("--api-url", help="覆盖 OpenAI 兼容 base_url")
    parser.add_argument("--api-key", help="覆盖 API key（默认环境变量或 cc-switch）")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _ensure_utf8()
    args = parse_args(argv)
    env = dict(os.environ)
    cfg = load_config(env)

    if args.list_models:
        for name, note in MODEL_NAMES.items():
            print(f"{name}\t{note}")
        return 0
    if not args.media:
        print(
            "错误: 至少需要一个图片路径或 URL（或用 --list-models 查看可用模型）",
            file=sys.stderr,
        )
        return 2

    base_url = args.api_url or cfg["base_url"]
    api_key = args.api_key or cfg["api_key"]
    model = args.model or cfg["model"]
    prompt = args.prompt or DEFAULT_PROMPT

    try:
        images = []
        for media in args.media:
            images.append(media if is_url(media) else encode_image(media))
        description, meta = describe(
            images,
            prompt,
            base_url=base_url,
            api_key=api_key,
            model=model,
            timeout=args.timeout,
            thinking=args.thinking,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    print(description)
    usage_line = f"[{meta['model']}] {meta['elapsed_s']}s" + (
        f", {meta['prompt_tokens']}+{meta['completion_tokens']} tokens"
        if meta["prompt_tokens"]
        else ""
    )
    print(usage_line, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
