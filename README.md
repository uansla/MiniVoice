# 极简变声 (MiniVoice)

本项目为 **“AI 降噪 + 系统级静默变声”** 的自动化部署脚本与轻量级桌面工具，彻底告别广告弹窗、付费套壳与冗余功能。

## 核心音频链路

```text
物理麦克风
   │
   ▼
SteelSeries Sonar (ClearCast AI 降噪) ──► 实时屏蔽狗叫、猫叫、鸟叫、鸣笛、键盘声
   │  (输出虚拟设备: SteelSeries Sonar - Microphone)
   ▼
Equalizer APO + 变声 VST 插件          ──► 系统级静默变声 + 轻量人声 EQ 修饰
   │
   ▼
微信 / QQ / 游戏语音 / 腾讯会议 / Discord（输入设备选择 SteelSeries Sonar - Microphone）
```

## 项目目录结构

```text
MiniVoice/
├── run.bat                       # 双击启动极简变声（纯 Python 标准库，免 pip 装包）
├── build_exe.bat                 # 本地构建 Windows 可移植测试包
├── scripts/
│   ├── install_tools.ps1         # 通过 winget 一键安装 SteelSeries GG 与 Equalizer APO
│   └── setup_apo_hook.ps1        # 自动授权并挂载 Equalizer APO 路由文件（运行一次即可）
├── src/
│   ├── app.py                    # 极简变声主界面（一键开关、秒切预设、环境自检）
│   ├── apo_manager.py            # Equalizer APO 配置热重载引擎
│   └── vst_inspector.py          # PE 文件头检测器（自动识别 VST 是 32 位还是 64 位）
├── config/
│   ├── settings.json             # 路径与设备配置
│   └── presets/                  # 预设模板（原声直通 / 男变女 / 女变男）
└── vst_plugins/                  # 放置变声 VST2 插件 (.dll)
```

## GitHub Actions Windows 测试包

推送到 `main`/`master`、创建 Pull Request，或在 GitHub 的 **Actions → Windows build → Run workflow** 手动触发构建后，可从对应运行记录的 **Artifacts** 下载 `MiniVoice-windows-x64`。解压后运行 `MiniVoice.exe`。该包是可移植目录包，请保留整个目录，不要只复制 EXE。包内附 Equalizer APO 1.4.2 安装程序及其对应 GPL 源码压缩包；安装驱动仍需管理员确认并重启 Windows。

运行 MiniVoice 本体不需要 Python、模型或联网；不过目前 Windows 包**没有内置 VST2 变声插件**，需要用户先从插件作者处获取 64 位 DLL 并放入 `vst_plugins/`。Equalizer APO 和已安装的插件处理音频时无需模型或网络。SteelSeries Sonar 是可选的 AI 降噪环节，不是变声必需项。系统音频驱动/软件需要预先安装和配置，首次安装依赖时可能需要联网；安装完成后，MiniVoice 的变声配置和实时音频处理在本机完成。

GitHub 构建会附带 Equalizer APO 安装程序，但**当前没有随包分发 VST2 变声 DLL**。例如 GVST GForm 支持音高/共振峰处理，但其作者规定插件只能由官网或获授权方分发，故本项目不能把它复制进构建包。可从 [GVST 官方下载页](https://gvst.uk/Downloads)获取官方压缩包，按其许可自行安装/复制 64 位 `GForm.dll` 到 `vst_plugins/`；程序会自动发现该目录中的 DLL，也可以使用“选择 DLL...”浏览。不要把普通 VST3 文件放进来，Equalizer APO 标准版的配置加载使用的是 VST2 DLL。

本项目构建目标是 x64。32 位 Windows VST2 DLL 无法由此包内的 64 位 Equalizer APO 直接加载；因此不会为了“同时提供 32/64 位”而把不可用的 32 位插件放进目录。

## 快速部署步骤（约 5 分钟）

### 第 1 步：一键安装基础软件
1. 点击界面里的 **“安装/修复音频引擎”**，在管理员确认框中选择“是”。不要在资源管理器里寻找 `.ps1` 的“安装”菜单；它是 PowerShell 脚本，由应用按钮启动。完整测试包内含 Equalizer APO 安装程序。
2. 脚本询问是否安装 SteelSeries GG/Sonar 时，输入 `y` 并回车。Sonar 是可选降噪组件，脚本通过 `winget` 下载，需要联网；若电脑没有 winget，请从 [SteelSeries 官网](https://steelseries.com/gg)单独下载安装。也可以输入 `n` 跳过，之后仍可使用 Equalizer APO 变声。
3. 在 Equalizer APO 安装器/Device Selector 中选择实际麦克风设备，完成后按提示重启 Windows。仅以管理员身份运行 MiniVoice 不会替代这一步，也不会自动创建 Equalizer APO 配置目录。

### 第 2 步（可选）：配置 AI 降噪
1. 打开 **SteelSeries GG**，进入左侧 **Sonar** 模块（完全免费，无需赛睿硬件）。
2. 切换到 **Mic（麦克风）** 选项卡，输入源选择你的真实物理麦克风。
3. 开启 **ClearCast AI Noise Cancellation（AI 降噪）**，强度建议调至 `75% ~ 85%`。

### 第 3 步：选择 Equalizer APO 要处理的麦克风
1. 打开开始菜单中的 **Equalizer APO -> Device Selector（设备选择器）**。
2. 切换到 **Capture devices（录音设备）** 选项卡。
3. 使用 Sonar 时勾选 **`SteelSeries Sonar - Microphone`**；不使用 Sonar 时勾选你的物理麦克风。点击确定并按提示**重启电脑**。

### 第 4 步：放入变声 VST 插件
1. 从插件作者处获取并按其许可安装/复制 64 位 VST2 变声插件（`.dll`）到 `vst_plugins/` 目录中。
   - **重要提示**：原版 `RoVee.dll` (v1.21) 为 32 位插件，64 位 Equalizer APO 不能直接加载 32 位 DLL。可考虑原生 64 位插件，例如 **GVST GForm**；请遵循插件作者的分发和安装许可。
2. 右键以管理员身份运行一次 `scripts/setup_apo_hook.ps1`，完成配置文件挂载。

### 第 5 步：启动极简变声并微调音色
1. 双击根目录的 `run.bat` 启动 **极简变声 (MiniVoice)**。
2. 点击 **“选择 DLL...”** 选中你放入的变声插件，确认下方显示 `64 位 VST2 插件（完全兼容）`。
3. 点击 **“打开 APO 配置编辑器”**，在 `minivoice.txt` 标签页中找到 VST 插件行，点击 **Open Panel** 微调你的音高（Pitch）和共振峰（Formant），勾选 **Apply automatically** 即可实时保存。
4. 以后日常使用只需在极简变声界面点击 **开启/关闭变声** 或切换预设，配置在本机生效；在微信、游戏或会议软件中选择 Equalizer APO 已处理的对应麦克风设备即可。Sonar 未安装时，设置 MiniVoice 的设备名为你的物理麦克风。
