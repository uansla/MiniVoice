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

推送到 `main`/`master`、创建 Pull Request，或在 GitHub 的 **Actions → Windows build → Run workflow** 手动触发构建后，可从对应运行记录的 **Artifacts** 下载 `MiniVoice-windows-x64`。解压后运行 `MiniVoice.exe`。该包是可移植目录包，请保留整个目录，不要只复制 EXE。

运行 MiniVoice 本体不需要 Python、模型或联网；不过实时变声目前由 **Equalizer APO + 用户自行提供的 64 位 VST2 插件**完成，语音应用应选择相应的处理后麦克风设备。SteelSeries Sonar 是可选的 AI 降噪环节，不是变声必需项。系统音频驱动/软件需要预先安装和配置，首次安装依赖时可能需要联网；安装完成后，MiniVoice 的变声配置和实时音频处理在本机完成。

GitHub 构建仅生成 MiniVoice 桌面程序，不会打包 Equalizer APO、Sonar 或第三方 VST 插件。VST 插件需单独获取，并确认其来源与许可证。

## 快速部署步骤（约 5 分钟）

### 第 1 步：一键安装基础软件
1. 右键点击 `scripts/install_tools.ps1`，选择 **“使用 PowerShell 运行”**（需要管理员权限）。
2. 脚本会自动通过 `winget` 安装 **SteelSeries GG** 和 **Equalizer APO**。

### 第 2 步：配置 AI 降噪（屏蔽猫狗叫）
1. 打开 **SteelSeries GG**，进入左侧 **Sonar** 模块（完全免费，无需赛睿硬件）。
2. 切换到 **Mic（麦克风）** 选项卡，输入源选择你的真实物理麦克风。
3. 开启 **ClearCast AI Noise Cancellation（AI 降噪）**，强度建议调至 `75% ~ 85%`。

### 第 3 步：将 Equalizer APO 挂载到降噪麦克风
1. 打开开始菜单中的 **Equalizer APO -> Device Selector（设备选择器）**。
2. 切换到 **Capture devices（录音设备）** 选项卡。
3. 勾选 **`SteelSeries Sonar - Microphone`**，点击确定并按提示**重启电脑**。

### 第 4 步：放入变声 VST 插件
1. 将 64 位免费变声 VST2 插件（`.dll`）复制到 `vst_plugins/` 目录中。
   - **重要提示**：原版 `RoVee.dll` (v1.21) 为 32 位插件，64 位 Equalizer APO 不能直接加载 32 位 DLL。如需使用 RoVee 请通过 jBridge 桥接为 64 位；或者直接选用原生 64 位免费插件 **GVST GForm (64-bit)** 或 **Graillon Free (64-bit)**（效果同样自然，且原生兼容）。
2. 右键以管理员身份运行一次 `scripts/setup_apo_hook.ps1`，完成配置文件挂载。

### 第 5 步：启动极简变声并微调音色
1. 双击根目录的 `run.bat` 启动 **极简变声 (MiniVoice)**。
2. 点击 **“选择 DLL...”** 选中你放入的变声插件，确认下方显示 `64 位 VST2 插件（完全兼容）`。
3. 点击 **“打开 APO 配置编辑器”**，在 `minivoice.txt` 标签页中找到 VST 插件行，点击 **Open Panel** 微调你的音高（Pitch）和共振峰（Formant），勾选 **Apply automatically** 即可实时保存。
4. 以后日常使用只需在极简变声界面点击 **开启/关闭变声** 或切换预设，毫秒级生效；在微信、游戏或会议软件中将麦克风设为 **`SteelSeries Sonar - Microphone`** 即可。
