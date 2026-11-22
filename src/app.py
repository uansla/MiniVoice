"""
app.py
极简变声 (MiniVoice)
架构：物理麦克风 -> SteelSeries Sonar (AI降噪，屏蔽猫狗叫/杂音) -> Equalizer APO + VST (系统级静默变声) -> 所有语音/游戏/会议软件
"""

import os
import subprocess
import sys
import ctypes
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from apo_manager import APOManager
from vst_inspector import inspect_dll_architecture


PRESET_LABELS = {
    "00_bypass_original.txt": "00 - 原声直通（仅 AI 降噪）",
    "01_male_to_female_bright.txt": "01 - 男变女（清亮/偏年轻）",
    "02_male_to_female_soft.txt": "02 - 男变女（柔和/自然）",
    "03_female_to_male_young.txt": "03 - 女变男（青年男声）",
    "04_female_to_male_deep.txt": "04 - 女变男（低沉稳重）",
}


class MiniVoiceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # In a PyInstaller build __file__ points inside the bundle. Keep mutable
        # settings and presets beside the executable so users can update them.
        self.project_root = (
            Path(sys.executable).resolve().parent
            if getattr(sys, "frozen", False)
            else Path(__file__).resolve().parent.parent
        )
        self.manager = APOManager(self.project_root)

        self.title("极简变声 (MiniVoice) · Sonar AI降噪 + Equalizer APO")
        self.geometry("680x560")
        self.minsize(640, 520)
        self.configure(bg="#1E1F24")

        self._setup_styles()
        self._build_ui()
        self._select_bundled_vst_if_available()
        self._refresh_status()

    def _bundled_vst_plugins(self):
        """Return VST DLLs shipped beside the portable app (or in the source tree)."""
        plugin_dir = self.project_root / "vst_plugins"
        if not plugin_dir.is_dir():
            return []
        return sorted(plugin_dir.glob("*.dll"), key=lambda path: path.name.lower())

    def _select_bundled_vst_if_available(self):
        """Preselect a bundled plugin when settings do not point to a valid DLL."""
        configured = self.vst_var.get().strip()
        if configured and Path(configured).is_file():
            return
        candidates = self._bundled_vst_plugins()
        if candidates:
            self.vst_var.set(str(candidates[0].resolve()))

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#1E1F24")
        style.configure("Card.TFrame", background="#282A32", relief="flat")
        style.configure("TLabel", background="#1E1F24", foreground="#E6E8EE", font=("Microsoft YaHei UI", 10))
        style.configure("Card.TLabel", background="#282A32", foreground="#E6E8EE", font=("Microsoft YaHei UI", 10))
        style.configure("Title.TLabel", background="#1E1F24", foreground="#FFFFFF", font=("Microsoft YaHei UI", 14, "bold"))
        style.configure("Sub.TLabel", background="#282A32", foreground="#9AA0AE", font=("Microsoft YaHei UI", 9))
        style.configure("TButton", font=("Microsoft YaHei UI", 9), padding=(10, 6), background="#3B82F6", foreground="#FFFFFF")
        style.map("TButton", background=[("disabled", "#454852"), ("active", "#2563EB")], foreground=[("disabled", "#9AA0AE")])
        style.configure("Accent.TButton", background="#3B82F6", foreground="#FFFFFF", font=("Microsoft YaHei UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#2563EB")])

    def _build_ui(self):
        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        # Header
        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="极简变声 MiniVoice", style="Title.TLabel").pack(side="left")
        ttk.Label(
            header,
            text="AI 降噪 (Sonar)  →  系统级变声 (Equalizer APO + VST)",
            foreground="#60A5FA",
        ).pack(side="right", pady=4)

        # 1. 主开关与预设卡片
        main_card = ttk.Frame(container, style="Card.TFrame", padding=14)
        main_card.pack(fill="x", pady=(0, 10))

        row1 = ttk.Frame(main_card, style="Card.TFrame")
        row1.pack(fill="x", pady=(0, 10))

        self.enabled_var = tk.BooleanVar(value=self.manager.settings.get("enabled", False))
        self.toggle_btn = tk.Button(
            row1,
            text="",
            command=self._on_toggle_master,
            font=("Microsoft YaHei UI", 11, "bold"),
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
        )
        self.toggle_btn.pack(side="left")
        self._update_toggle_button_visual()

        preset_frame = ttk.Frame(row1, style="Card.TFrame")
        preset_frame.pack(side="right", fill="x", expand=True, padx=(16, 0))
        ttk.Label(preset_frame, text="变声预设：", style="Card.TLabel").pack(side="left")

        self.preset_files = self.manager.list_presets()
        self.preset_display_map = {
            PRESET_LABELS.get(name, name): name for name in self.preset_files
        }
        reverse_map = {v: k for k, v in self.preset_display_map.items()}
        current_preset = self.manager.settings.get("active_preset", "00_bypass_original.txt")
        self.preset_var = tk.StringVar(value=reverse_map.get(current_preset, current_preset))

        self.preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            values=list(self.preset_display_map.keys()),
            state="readonly",
            width=30,
        )
        self.preset_combo.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self.preset_combo.bind("<<ComboboxSelected>>", lambda _e: self._apply_current())

        # 2. 音频路由与 VST 插件设置卡片
        cfg_card = ttk.Frame(container, style="Card.TFrame", padding=14)
        cfg_card.pack(fill="x", pady=(0, 10))

        # 目标设备
        dev_row = ttk.Frame(cfg_card, style="Card.TFrame")
        dev_row.pack(fill="x", pady=(0, 8))
        ttk.Label(dev_row, text="降噪输入设备名：", style="Card.TLabel", width=16).pack(side="left")
        self.device_var = tk.StringVar(
            value=self.manager.settings.get("target_device", "SteelSeries Sonar - Microphone")
        )
        ttk.Entry(dev_row, textvariable=self.device_var).pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.apply_button = ttk.Button(dev_row, text="保存并应用", command=self._apply_current)
        self.apply_button.pack(side="right")

        # VST 插件路径
        vst_row = ttk.Frame(cfg_card, style="Card.TFrame")
        vst_row.pack(fill="x", pady=(0, 6))
        ttk.Label(vst_row, text="变声 VST 插件：", style="Card.TLabel", width=16).pack(side="left")
        self.vst_var = tk.StringVar(value=self.manager.settings.get("vst_dll_path", ""))
        ttk.Entry(vst_row, textvariable=self.vst_var).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(vst_row, text="选择 DLL...", command=self._browse_vst).pack(side="right")

        self.vst_hint_label = ttk.Label(cfg_card, text="", style="Sub.TLabel", wraplength=610)
        self.vst_hint_label.pack(fill="x", pady=(2, 0))

        # 3. 快捷工具栏
        tools_card = ttk.Frame(container, style="Card.TFrame", padding=12)
        tools_card.pack(fill="x", pady=(0, 10))
        ttk.Label(tools_card, text="快捷操作（首次调音请在 APO 编辑器中打开 VST 面板微调音高/共振峰）：", style="Sub.TLabel").pack(
            anchor="w", pady=(0, 8)
        )
        btn_row = ttk.Frame(tools_card, style="Card.TFrame")
        btn_row.pack(fill="x")

        self.sonar_button = ttk.Button(btn_row, text="打开 SteelSeries GG", command=self._open_sonar)
        self.sonar_button.pack(side="left", padx=(0, 8))
        self.editor_button = ttk.Button(btn_row, text="打开 APO 配置编辑器", command=self._open_apo_editor)
        self.editor_button.pack(side="left", padx=(0, 8))
        self.selector_button = ttk.Button(btn_row, text="APO 设备选择器", command=self._open_device_selector)
        self.selector_button.pack(side="left", padx=(0, 8))
        self.install_button = ttk.Button(btn_row, text="安装/修复音频引擎", command=self._install_audio_engine)
        self.install_button.pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="检测环境", command=self._refresh_status).pack(side="right")

        # 4. 实时配置预览与状态日志
        log_card = ttk.Frame(container, style="Card.TFrame", padding=12)
        log_card.pack(fill="both", expand=True)

        ttk.Label(log_card, text="环境状态与实时配置预览：", style="Sub.TLabel").pack(anchor="w", pady=(0, 6))
        self.log_text = tk.Text(
            log_card,
            bg="#15161A",
            fg="#CBD5E1",
            insertbackground="#FFFFFF",
            font=("Consolas", 9),
            relief="flat",
            height=10,
            wrap="word",
        )
        self.log_text.pack(fill="both", expand=True)

    def _update_toggle_button_visual(self):
        if self.enabled_var.get():
            self.toggle_btn.configure(text="● 变声已开启 (点击关闭)", bg="#10B981", fg="#FFFFFF")
        else:
            self.toggle_btn.configure(text="○ 变声已关闭 (点击开启)", bg="#4B5563", fg="#FFFFFF")

    def _on_toggle_master(self):
        self.enabled_var.set(not self.enabled_var.get())
        self._update_toggle_button_visual()
        self._apply_current()

    def _browse_vst(self):
        initial_dir = str(self.project_root / "vst_plugins")
        candidates = self._bundled_vst_plugins()
        if not candidates:
            messagebox.showinfo(
                "插件目录为空",
                "当前安装包没有附带 VST2 变声插件。请将已获授权的 64 位 VST2 DLL 放入：\n"
                f"{initial_dir}\n\n"
                "Equalizer APO 64 位不能加载 32 位插件；VST3 也不能作为此处的 DLL 使用。",
            )
        path = filedialog.askopenfilename(
            title="选择变声 VST2 插件 (.dll)",
            initialdir=initial_dir,
            filetypes=[("VST2 Plugin DLL", "*.dll"), ("All Files", "*.*")],
        )
        if path:
            self.vst_var.set(path)
            self._inspect_vst_and_display(path)
            self._apply_current()

    def _inspect_vst_and_display(self, path: str):
        if not path:
            self.vst_hint_label.configure(
                text="提示：请将 64 位 VST2 插件（或桥接后的 RoVee）放入 vst_plugins 目录并选择。",
                foreground="#9AA0AE",
            )
            return
        info = inspect_dll_architecture(path)
        color_map = {
            "ok": "#34D399",
            "warn_32bit": "#FBBF24",
            "missing": "#F87171",
            "invalid": "#F87171",
            "error": "#F87171",
        }
        self.vst_hint_label.configure(
            text=f"[插件检测] {info['message']}",
            foreground=color_map.get(info["status"], "#9AA0AE"),
        )

    def _apply_current(self):
        display_name = self.preset_var.get()
        preset_file = self.preset_display_map.get(display_name, "00_bypass_original.txt")

        self.manager.settings["enabled"] = self.enabled_var.get()
        self.manager.settings["active_preset"] = preset_file
        self.manager.settings["target_device"] = self.device_var.get().strip() or "SteelSeries Sonar - Microphone"
        self.manager.settings["vst_dll_path"] = self.vst_var.get().strip()

        ok, msg = self.manager.apply_changes()
        self._refresh_status(extra_message=msg)
        if not ok:
            messagebox.showwarning("应用配置提示", msg)

    def _refresh_status(self, extra_message: str = ""):
        env = self.manager.check_environment()
        apo_state = "normal" if env["apo_installed"] else "disabled"
        for widget in (self.toggle_btn, self.preset_combo, self.apply_button, self.editor_button, self.selector_button):
            widget.configure(state=apo_state)
        self._inspect_vst_and_display(self.vst_var.get().strip())

        lines = []
        if extra_message:
            lines.append(f"[操作结果] {extra_message}")
            lines.append("-" * 60)

        lines.append(f"1. SteelSeries GG (Sonar): {'[已安装]' if env['sonar_installed'] else '[未检测到，请运行 scripts/install_tools.ps1]'}")
        lines.append(f"2. Equalizer APO 目录:     {'[已安装]' if env['apo_installed'] else '[未安装；管理员权限不会自动安装，请点击“安装/修复音频引擎”]'}")
        lines.append(f"3. APO 配置写入权限:       {'[正常]' if env['apo_config_writable'] else '[无权限，请以管理员身份运行或执行 setup_apo_hook.ps1]'}")
        lines.append(f"4. VST 变声插件文件:       {'[已就绪]' if env['vst_configured'] else '[未选择 DLL]'}")
        lines.append("")
        lines.append("--- 即将/当前写入 Equalizer APO 的路由配置 ---")
        lines.append(self.manager.render_active_config().strip())

        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", "\n".join(lines))
        self.log_text.configure(state="disabled")

    def _install_audio_engine(self):
        script = self.project_root / "scripts" / "install_tools.ps1"
        if not script.is_file():
            messagebox.showerror("缺少安装文件", f"没有找到安装脚本：\n{script}")
            return
        messagebox.showinfo(
            "安装音频引擎",
            "将以管理员权限启动安装脚本。安装 Equalizer APO 后，请在设备选择器中勾选正在使用的麦克风，并按安装程序提示重启电脑。安装需要联网。",
        )
        args = f'-NoProfile -ExecutionPolicy Bypass -File "{script}"'
        result = ctypes.windll.shell32.ShellExecuteW(None, "runas", "powershell.exe", args, str(script.parent), 1)
        if result <= 32:
            messagebox.showerror("无法启动安装程序", f"Windows ShellExecute 错误码：{result}")

    def _launch_exe(self, exe_path: str, name: str):
        if os.path.exists(exe_path):
            # Equalizer APO's Editor ships its own Qt runtime. Inherited Qt or
            # Python paths can make it load an incompatible platform plugin.
            child_env = os.environ.copy()
            for variable in (
                "QT_PLUGIN_PATH",
                "QT_QPA_PLATFORM_PLUGIN_PATH",
                "QT_QPA_FONTDIR",
                "PYTHONHOME",
                "PYTHONPATH",
            ):
                child_env.pop(variable, None)
            try:
                subprocess.Popen(
                    [exe_path],
                    cwd=str(Path(exe_path).resolve().parent),
                    env=child_env,
                )
            except OSError as exc:
                messagebox.showerror("无法启动程序", f"启动 {name} 失败：\n{exc}")
        else:
            messagebox.showinfo("未找到程序", f"未在默认路径找到 {name}：\n{exe_path}\n\n请先运行 scripts/install_tools.ps1 安装。")

    def _open_sonar(self):
        self._launch_exe(self.manager.settings["sonar_exe"], "SteelSeries GG")

    def _open_apo_editor(self):
        self._launch_exe(self.manager.settings["apo_editor_exe"], "Equalizer APO Configuration Editor")

    def _open_device_selector(self):
        self._launch_exe(self.manager.settings["apo_device_selector_exe"], "Equalizer APO Device Selector")


if __name__ == "__main__":
    app = MiniVoiceApp()
    app.mainloop()
