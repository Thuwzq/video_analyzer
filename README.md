# Video Analyzer

## 项目简介
本项目是一个基于 FFmpeg 的 C 语言视频分析工具，配合 Python 脚本实现批量视频帧统计、I帧数据与分辨率分析、可视化等功能

## 主要功能
- **视频帧统计**：统计每个视频的所有帧大小、类型等信息（C 工具 all_video_frame_size）。
- **批量处理脚本**：`run_all.sh` 支持对 videos/ 目录下所有视频自动化处理，输出到 results/ 目录。
- **I帧数据提取**：`parse_iframes.py` 批量提取 I 帧大小，生成结构化 CSV 数据。
- **视频信息提取**：`extract_video_info.sh` 批量获取视频比特率、分辨率等元数据。
- **数据分析与可视化**：
  - `python_scripts/cdf_again.py` 以 packet（1430 字节）为单位绘制 I 帧大小的 CDF 图。
  -`draw3.py`支持 I 帧大小分布分辨率关系的多种可视化
## 环境与依赖
- **操作系统**：Linux（已在 Ubuntu 5.4.0-204-generic 测试），MacOS ARM 也可运行
- **依赖库**：
  - FFmpeg 开发库（libavutil-dev, libavformat-dev, libavcodec-dev 等）
  - pkg-config
- **Python 依赖**（用于数据分析与可视化）：
  - pandas
  - matplotlib
  - numpy

## 编译方法
```bash
# 确保 pkg-config 能找到 FFmpeg 库
pkg-config --cflags --libs libavutil libavformat

# 编译
./configure
make
```

## 使用方法

### 1. 批量统计视频帧信息
使用 `run_all.sh` 脚本可自动批量处理 `videos/` 目录下所有视频，结果输出到 `results/` 目录：
```bash
bash run_all.sh
```
脚本会自动跳过空文件，并对每个视频生成对应的帧统计结果。

### 2. I帧数据提取与分析
- 使用 `parse_iframes.py` 提取所有视频的 I 帧数据，生成 `iframe_data.csv`。
- 使用 `python_scripts/cdf_again.py` 以"每 1430 字节为一个 packet"为单位，绘制 I 帧大小的 CDF 图：
  ```bash
  python3 python_scripts/cdf_again.py
  ```
  结果图片保存在 `output2/iframe_cdf_packets.png`。

### 3. 其他分析与可视化
- 使用 `extract_video_info.sh` 批量提取比特率、分辨率，生成 `video_info.csv`。
- 使用 `draw3.py` 等脚本进行数据合并、可视化（如 I 帧与比特率/分辨率关系图等）。

## 结果示例
- 输出目录下可见各类统计图（如 I 帧大小 CDF、I 帧与比特率/分辨率关系图等）。
- 生成的 CSV 文件可用于进一步分析。

