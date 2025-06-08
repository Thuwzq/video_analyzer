import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 创建输出目录
os.makedirs("output2", exist_ok=True)

# 读取 I 帧数据
iframe_df = pd.read_csv("iframe_data.csv")
iframe_df.columns = [col.strip() for col in iframe_df.columns]
iframe_df["video"] = iframe_df["video"].apply(lambda x: x.replace(".txt", ""))

# 读取视频元数据，去除列名空格，兼容 BOM
info_df = pd.read_csv("video_info.csv", encoding="utf-8-sig")
info_df.columns = [col.strip() for col in info_df.columns]

# 统计每个视频的平均 I 帧大小
avg_iframe = iframe_df.groupby("video")["size_bytes"].mean().reset_index()
avg_iframe.columns = ["video", "avg_iframe_size"]

# 合并比特率和分辨率
merged = pd.merge(avg_iframe, info_df, on="video")

print("列名：", merged.columns.tolist())
print("合并后前10行：\n", merged.head(10))
print(f"合并后总行数: {len(merged)}")

# 只保留比特率为数字的行
merged["bitrate"] = pd.to_numeric(merged["bitrate"], errors="coerce")
merged = merged[merged["bitrate"].notnull()]
merged["bitrate"] = merged["bitrate"].astype(int)

print("过滤后用于画图的数据：")
print(merged[["video", "avg_iframe_size", "bitrate", "resolution"]].head(20))
print(f"用于画图的总行数: {len(merged)}")

# 去除异常点：使用 IQR 方法筛除 I 帧极端大小
Q1 = merged["avg_iframe_size"].quantile(0.25)
Q3 = merged["avg_iframe_size"].quantile(0.75)
IQR = Q3 - Q1
filtered = merged[(merged["avg_iframe_size"] >= Q1 - 1.5 * IQR) & (merged["avg_iframe_size"] <= Q3 + 1.5 * IQR)]
print(f"去除异常点后用于画图的总行数: {len(filtered)}")

# 分辨率字符串转面积（像素数）
def res_key(res):
    try:
        w, h = map(int, res.lower().split('x'))
        return w * h
    except:
        return 0

# 生成每种分辨率对应的平均 I 帧大小和像素面积
res_group = filtered.groupby("resolution")["avg_iframe_size"].mean().reset_index()
res_group["area"] = res_group["resolution"].apply(res_key)
res_group = res_group[res_group["area"] > 0]
res_group["mpix"] = res_group["area"] / 1_000_000  # 转为百万像素
res_group = res_group.sort_values("area")

plt.figure(figsize=(12,6))
plt.bar(res_group["mpix"], res_group["avg_iframe_size"], width=0.1, edgecolor='black')
plt.xlabel("Resolution Area (Megapixels)")
plt.ylabel("Average I-frame size (bytes)")
plt.title("Average I-frame size vs Resolution Area (Bar Chart)")
plt.xlim(0, 3)  # ✅ 加这一行
plt.grid(axis='y')
plt.tight_layout()
plt.savefig("output2/iframe_vs_resolution_area_bar.png")

plt.figure(figsize=(12,6))
plt.plot(res_group["mpix"], res_group["avg_iframe_size"], marker='o')
plt.xlabel("Resolution Area (Megapixels)")
plt.ylabel("Average I-frame size (bytes)")
plt.title("Average I-frame size vs Resolution Area (Line Chart)")
plt.xlim(0, 3)  # ✅ 加这一行
plt.grid(True)
plt.tight_layout()
plt.savefig("output2/iframe_vs_resolution_area_line.png")