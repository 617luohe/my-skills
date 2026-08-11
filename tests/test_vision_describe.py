"""vision-skill 脚本的离线单元测试（不打真实 API，不依赖网络/key）。"""

import base64
import importlib.util
import struct
import zlib
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "vision-skill"
    / "scripts"
    / "vision_describe.py"
)
spec = importlib.util.spec_from_file_location("vision_describe", SCRIPT)
vision_describe = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(vision_describe)


def make_png(width=16, height=16):
    """标准库生成一张最小 PNG（红块）。"""

    def chunk(tag, data):
        blob = struct.pack(">I", len(data)) + tag + data
        return blob + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    row = b"\x00" + struct.pack("BBB", 255, 0, 0) * width
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(row * height))
    png += chunk(b"IEND", b"")
    return png


def test_load_config_defaults():
    cfg = vision_describe.load_config({})
    assert cfg["base_url"] == "https://opencode.ai/zen/go/v1"
    assert cfg["model"] == "minimax-m3"


def test_load_config_env_override():
    cfg = vision_describe.load_config(
        {
            "VISION_API_URL": "http://x/",
            "VISION_MODEL": "qwen3.8-max",
            "VISION_API_KEY": "k",
        }
    )
    assert cfg["base_url"] == "http://x"
    assert cfg["model"] == "qwen3.8-max"
    assert cfg["api_key"] == "k"


def test_is_url():
    assert vision_describe.is_url("https://a.com/b.png")
    assert vision_describe.is_url("http://a.com/b")
    assert not vision_describe.is_url("b.png")
    assert not vision_describe.is_url("C:/x/y.png")


def test_encode_image_ok(tmp_path):
    p = tmp_path / "t.png"
    p.write_bytes(make_png())
    url = vision_describe.encode_image(str(p))
    assert url.startswith("data:image/png;base64,")
    assert base64.b64decode(url.split(",", 1)[1]) == p.read_bytes()


def test_encode_image_missing(tmp_path):
    with pytest.raises(ValueError, match="文件不存在"):
        vision_describe.encode_image(str(tmp_path / "nope.png"))


def test_encode_image_bad_ext(tmp_path):
    p = tmp_path / "t.txt"
    p.write_text("hello")
    with pytest.raises(ValueError, match="不支持的图片类型"):
        vision_describe.encode_image(str(p))


def test_encode_image_too_large(tmp_path, monkeypatch):
    monkeypatch.setattr(vision_describe, "MAX_MEDIA_BYTES", 8)
    p = tmp_path / "big.png"
    p.write_bytes(make_png())  # 一张 PNG 必然 > 8 字节
    with pytest.raises(ValueError, match="图片过大"):
        vision_describe.encode_image(str(p))


def test_strip_think():
    assert vision_describe.strip_think("<think>inner</think>answer") == "answer"
    assert vision_describe.strip_think("no think here") == "no think here"
    # 只有 think 链时保底返回原文，不返回空
    assert vision_describe.strip_think("<think>only</think>") == "<think>only</think>"


def test_list_models_mentions_vision_models(capsys):
    assert vision_describe.main(["--list-models"]) == 0
    out = capsys.readouterr().out
    assert "minimax-m3" in out
    assert "qwen3.8-max" in out


def test_main_requires_media(capsys):
    assert vision_describe.main([]) == 2
    assert "至少需要一个图片路径" in capsys.readouterr().err
