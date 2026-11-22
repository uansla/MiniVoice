"""
vst_inspector.py
极简变声 (MiniVoice) - VST 插件架构检测模块
解析 Windows PE 文件头（.dll），判断 VST 插件是 32 位 (x86) 还是 64 位 (x64)。
Equalizer APO (64位) 原生仅支持加载 64 位 VST2 插件；若放入 32 位 RoVee.dll，
本模块会自动识别并给出明确提示，防止音频服务 (audiodg.exe) 加载失败或无声。
"""

import struct
from pathlib import Path
from typing import Dict


IMAGE_FILE_MACHINE_I386 = 0x014C
IMAGE_FILE_MACHINE_AMD64 = 0x8664
IMAGE_FILE_MACHINE_ARM64 = 0xAA64


def inspect_dll_architecture(dll_path: str) -> Dict[str, str]:
    """检查 DLL 文件的架构信息。"""
    path = Path(dll_path)
    if not path.exists() or not path.is_file():
        return {"status": "missing", "arch": "unknown", "message": "未找到指定的 VST 插件文件"}

    if path.suffix.lower() != ".dll":
        return {"status": "invalid", "arch": "unknown", "message": "仅支持 .dll 格式的 VST2 插件"}

    try:
        with path.open("rb") as f:
            mz = f.read(2)
            if mz != b"MZ":
                return {"status": "invalid", "arch": "unknown", "message": "不是有效的 Windows DLL 文件"}

            f.seek(0x3C)
            pe_offset_bytes = f.read(4)
            if len(pe_offset_bytes) < 4:
                return {"status": "invalid", "arch": "unknown", "message": "PE 文件头损坏"}

            pe_offset = struct.unpack("<I", pe_offset_bytes)[0]
            f.seek(pe_offset)
            pe_sig = f.read(4)
            if pe_sig != b"PE\x00\x00":
                return {"status": "invalid", "arch": "unknown", "message": "无效的 PE 签名"}

            machine = struct.unpack("<H", f.read(2))[0]

        if machine == IMAGE_FILE_MACHINE_AMD64:
            return {
                "status": "ok",
                "arch": "x64",
                "message": "64 位 VST2 插件（与 64 位 Equalizer APO 完全兼容）",
            }
        elif machine == IMAGE_FILE_MACHINE_I386:
            return {
                "status": "warn_32bit",
                "arch": "x86",
                "message": (
                    "检测到 32 位插件（如原版 RoVee.dll）。64 位 Equalizer APO 无法直接加载 32 位 DLL，"
                    "请使用 jBridge 桥接为 64 位，或改用 64 位免费变声 VST（如 GVST GForm x64 / Graillon Free x64）。"
                ),
            }
        elif machine == IMAGE_FILE_MACHINE_ARM64:
            return {
                "status": "warn_arm64",
                "arch": "arm64",
                "message": "检测到 ARM64 插件，请确认与当前系统架构一致。",
            }
        else:
            return {
                "status": "unknown",
                "arch": hex(machine),
                "message": f"未知架构类型 ({hex(machine)})",
            }
    except Exception as exc:
        return {"status": "error", "arch": "unknown", "message": f"读取 DLL 失败: {exc}"}
