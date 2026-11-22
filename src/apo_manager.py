"""
apo_manager.py
极简变声 (MiniVoice) - Equalizer APO 配置管理核心模块
原理：Equalizer APO 会实时监听 config.txt 的文件变更（毫秒级热重载）。
本模块通过写入一个独立的路由文件 `minivoice.txt` 并在主 `config.txt` 中
通过 `Include:` 挂载它，实现一键开关变声与无缝切换预设，且不破坏用户原有 EQ 配置。
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


HOOK_FILENAME = "minivoice.txt"
HOOK_MARKER = "# [MiniVoice-AutoManaged]"
DEFAULT_SETTINGS = {
    "apo_config_dir": r"C:\Program Files\EqualizerAPO\config",
    "apo_editor_exe": r"C:\Program Files\EqualizerAPO\Editor.exe",
    "apo_device_selector_exe": r"C:\Program Files\EqualizerAPO\DeviceSelector.exe",
    "sonar_exe": r"C:\Program Files\SteelSeries\GG\SteelSeriesGG.exe",
    "target_device": "SteelSeries Sonar - Microphone",
    "vst_dll_path": "",
    "active_preset": "00_bypass_original.txt",
    "enabled": False,
}


class APOManager:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_dir = project_root / "config"
        self.presets_dir = self.config_dir / "presets"
        self.settings_path = self.config_dir / "settings.json"
        self.settings = self._load_settings()

    def _effective_apo_config_dir(self) -> Path:
        """Use the configured path, or the install path recorded by Equalizer APO."""
        configured = Path(self.settings.get("apo_config_dir", DEFAULT_SETTINGS["apo_config_dir"]))
        if configured.is_dir():
            return configured
        if sys.platform == "win32":
            try:
                import winreg

                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\EqualizerAPO") as key:
                    value, _ = winreg.QueryValueEx(key, "ConfigPath")
                detected = Path(value)
                if detected.is_dir():
                    self.settings["apo_config_dir"] = str(detected)
                    return detected
            except (OSError, ImportError):
                pass
        return configured

    def _load_settings(self) -> Dict:
        if self.settings_path.exists():
            try:
                loaded = json.loads(self.settings_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    return {**DEFAULT_SETTINGS, **loaded}
            except (OSError, json.JSONDecodeError):
                pass
        return DEFAULT_SETTINGS.copy()

    def save_settings(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.settings_path.write_text(
            json.dumps(self.settings, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def list_presets(self) -> List[str]:
        if not self.presets_dir.exists():
            return []
        return sorted(p.name for p in self.presets_dir.glob("*.txt"))

    def read_preset(self, preset_name: str) -> str:
        if Path(preset_name).name != preset_name:
            return ""
        path = self.presets_dir / preset_name
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def save_preset(self, preset_name: str, content: str) -> None:
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        (self.presets_dir / preset_name).write_text(content, encoding="utf-8")

    def check_environment(self) -> Dict[str, bool]:
        apo_dir = self._effective_apo_config_dir()
        return {
            "apo_installed": apo_dir.exists(),
            "apo_config_writable": self._is_dir_writable(apo_dir),
            "sonar_installed": Path(self.settings["sonar_exe"]).exists(),
            "vst_configured": bool(self.settings.get("vst_dll_path"))
            and Path(self.settings["vst_dll_path"]).exists(),
        }

    @staticmethod
    def _is_dir_writable(directory: Path) -> bool:
        if not directory.exists():
            return False
        test_file = directory / ".minivoice_write_test.tmp"
        try:
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink()
            return True
        except Exception:
            return False

    def ensure_main_config_hook(self) -> Tuple[bool, str]:
        """确保 Equalizer APO 的主 config.txt 包含对本工具路由文件的 Include 引用。"""
        apo_dir = self._effective_apo_config_dir()
        main_cfg = apo_dir / "config.txt"
        if not apo_dir.exists():
            return False, f"未找到 Equalizer APO 配置目录：{apo_dir}"

        try:
            existing = main_cfg.read_text(encoding="utf-8") if main_cfg.exists() else ""
            if HOOK_FILENAME in existing:
                return True, "Equalizer APO 主配置已挂载。"

            # 备份原 config.txt
            if main_cfg.exists():
                backup_name = f"config.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                shutil.copy2(main_cfg, apo_dir / backup_name)

            addition = f"\n{HOOK_MARKER}\nInclude: {HOOK_FILENAME}\n"
            main_cfg.write_text(existing.rstrip() + "\n" + addition, encoding="utf-8")
            return True, "已自动备份原 config.txt 并完成挂载。"
        except PermissionError:
            return False, (
                "没有写入 Program Files 的权限。请右键以【管理员身份运行】本程序，"
                "或先运行 scripts/setup_apo_hook.ps1 授权。"
            )
        except Exception as exc:
            return False, f"挂载失败：{exc}"

    def render_active_config(self) -> str:
        """根据当前开关、目标设备、VST 路径和所选预设生成最终写入 APO 的配置文本。"""
        device = self.settings.get("target_device", "SteelSeries Sonar - Microphone").strip()
        vst_path = self.settings.get("vst_dll_path", "").strip()
        enabled = bool(self.settings.get("enabled", False))
        preset_name = self.settings.get("active_preset", "00_bypass_original.txt")

        header = [
            HOOK_MARKER,
            f"# Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"# Status: {'ON' if enabled else 'OFF (Bypass)'}",
            f"# Preset: {preset_name}",
            "",
            f"Device: {device}",
            "Stage: capture",
            "",
        ]

        if not enabled or preset_name == "00_bypass_original.txt":
            header.append("# 变声已关闭（仅直通 SteelSeries Sonar AI 降噪后的纯净人声）")
            return "\n".join(header) + "\n"

        preset_body = self.read_preset(preset_name)
        if vst_path:
            rendered_body = preset_body.replace("{{VST_PATH}}", vst_path)
        else:
            lines = []
            for line in preset_body.splitlines():
                if "{{VST_PATH}}" in line:
                    lines.append(f"# [未配置VST路径，已跳过] {line}")
                else:
                    lines.append(line)
            rendered_body = "\n".join(lines)

        return "\n".join(header) + rendered_body.strip() + "\n"

    def apply_changes(self) -> Tuple[bool, str]:
        """将当前配置写入 Equalizer APO，触发实时热生效。"""
        self.save_settings()
        ok, msg = self.ensure_main_config_hook()
        if not ok:
            return False, msg

        apo_dir = self._effective_apo_config_dir()
        hook_file = apo_dir / HOOK_FILENAME
        content = self.render_active_config()

        try:
            hook_file.write_text(content, encoding="utf-8")
            state_str = "已开启" if self.settings["enabled"] else "已关闭（原声直通）"
            return True, f"配置已实时生效！当前状态：{state_str} | 预设：{self.settings['active_preset']}"
        except PermissionError:
            return False, "写入失败：请以管理员身份运行，或运行 scripts/setup_apo_hook.ps1 赋予目录写权限。"
        except Exception as exc:
            return False, f"写入配置失败：{exc}"
