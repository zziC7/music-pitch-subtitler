# 🎵 Music Pitch Subtitler (基于 YourMT3+)

本项目是一个自动化的音乐音高可视化工具。它通过集成 **Demucs** 深度学习音源分离和 **YourMT3+** 高精度音高转录模型，能够从任何音频或视频中提取人声，并实时生成对应的音名可视化视频及 SRT 字幕。

---

## ✨ 功能亮点

- **智能音源分离**：自动提取纯净人声，极大减少背景音乐对音高识别的干扰。
- **高精度音高转录**：利用 `YourMT3+` 多任务学习模型，实现毫秒级的 MIDI 级别音高跟踪。
- **动态可视化生成**：一键生成带有 80pt 超大字号、屏幕正中心对齐的黑底背景视频。
- **双格式输出**：同步导出硬压制字幕视频 (.mp4) 与标准外挂字幕 (.srt)。
- **硬件加速支持**：全面适配 `NVIDIA CUDA` 加速（支持 Demucs 分离与 FFmpeg NVENC 编码）。
- **自动化清理**：内置 `CLEAN_UP` 机制，任务完成后自动清除中间产生的临时缓存（WAV, ASS 等）。

---

## 📂 模块化结构

```text
.
├── YourMT3/             # YourMT3 模型核心源码及预训练权重
├── input/               # 输入源文件目录 (支持 .wav, .mp3, .mp4 等)
├── output_mp4/          # 最终生成的音高可视化视频
├── output_srt/          # 导出的标准 SRT 字幕文件
├── main.py              # 主程序入口：协调转录与合成流水线
├── audio_utils.py       # 音频处理：FFmpeg 提取、黑底生成与 Demucs 分离
├── subtitle_utils.py    # 字幕逻辑：MIDI 转 ASS 格式与 SRT 格式
└── requirements.txt     # 项目依赖清单

```

## 🚀 快速上手

### 1. 安装依赖
建议在 Linux 环境下运行，确保系统已安装 `FFmpeg`。

```bash
pip install -r requirements.txt
```

### 2. 下载模型权重
由于YourMT3+模型权重文件 (`.ckpt`) 体积较大，未上传至 GitHub。请执行以下操作：
- 从 [[该链接](https://huggingface.co/spaces/mimbres/YourMT3/blob/main/amt/logs/2024/mc13_256_g4_all_v7_mt3f_sqr_rms_moe_wf4_n8k2_silu_rope_rp_b36_nops/checkpoints/last.ckpt)] 下载预训练权重`last.ckpt`。
- 将权重文件放置于项目根目录下的 `YourMT3/amt/logs/2024/mc13_256_g4_all_v7_mt3f_sqr_rms_moe_wf4_n8k2_silu_rope_rp_b36_nops/checkpoints` 文件夹内。

### 3. 运行转录
将您的音频放入 input/ 文件夹，在 main.py 中配置输入路径：

```bash
INPUT_FILE = "input/你的音频.wav"
```

启动程序：
```bash
python main.py
```

## 📺 效果展示

### 1. 输入源文件 (原始音频/视频)
> 包含背景音乐和人声的原始素材。

<video src="input/demo_video.mp4" controls width="100%">
  您的浏览器不支持播放该视频，请检查路径或手动下载。
</video>

### 2. 输出结果 (音高可视化版)
> 经过音源分离、YourMT3 转录并合成字幕后的最终效果。

<video src="output_mp4/demo_video.mp4" controls width="100%">
  您的浏览器不支持播放该视频，请检查路径或手动下载。
</video>

---

## 📄 SRT 字幕示例

生成的 `.srt` 文件位于 `output_srt/` 目录下，其内容格式如下：
```text
1
00:00:30,040 --> 00:00:30,719
G#3

2
00:00:31,300 --> 00:00:32,260
E3

3
00:00:35,300 --> 00:00:36,210
G#3

4
00:00:36,220 --> 00:00:37,450
F#3

5
00:00:38,810 --> 00:00:38,910
B2
```

## 📬 联系方式 (Contact)

如果您对本项目有任何建议或合作意向，欢迎通过以下方式联系我：

- **Email**: [zczhang23@m.fudan.edu.cn](mailto:zczhang23@m.fudan.edu.cn)

---

感谢支持本项目！🙌