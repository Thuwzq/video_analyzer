import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

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
merged = pd.merge(avg_iframe, info_df, left_on="video", right_on="video")

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

# 去除异常点：只保留I帧大小在5%~95%分位数之间的数据
low = merged["avg_iframe_size"].quantile(0.05)
high = merged["avg_iframe_size"].quantile(0.95)
filtered = merged[(merged["avg_iframe_size"] >= low) & (merged["avg_iframe_size"] <= high)]
print(f"去除异常点后用于画图的总行数: {len(filtered)}")

# 画 I帧大小 vs 比特率 散点图
os.makedirs("output", exist_ok=True)
plt.figure(figsize=(10,6))
plt.scatter(merged["bitrate"]/1e6, merged["avg_iframe_size"], alpha=0.7)
plt.xlabel("Bitrate (Mbps)")
plt.ylabel("Average I-frame size (bytes)")
plt.title("Average I-frame size vs Bitrate")
plt.grid(True)
plt.tight_layout()
plt.savefig("output/iframe_vs_bitrate.png")
print("✅ 已保存 output/iframe_vs_bitrate.png")

# 新增：比特率分组与平均I帧大小的柱状图（原始分组，仍用merged）
bins = [0, 1e6, 3e6, 10e6, float('inf')]
labels = ['<1Mbps', '1-3Mbps', '3-10Mbps', '>10Mbps']
merged['bitrate_group'] = pd.cut(merged['bitrate'], bins=bins, labels=labels, right=False)
grouped = merged.groupby('bitrate_group')["avg_iframe_size"].mean()
plt.figure(figsize=(8,6))
plt.bar(grouped.index.astype(str), grouped.values)
plt.xlabel("Bitrate Group")
plt.ylabel("Average I-frame size (bytes)")
plt.title("Average I-frame size vs Bitrate Group (Bar Chart)")
plt.grid(axis='y')
plt.tight_layout()
plt.savefig("output/iframe_vs_bitrate_bar.png")
print("✅ 已保存 output/iframe_vs_bitrate_bar.png")

# 新增：比特率等宽分箱（20组）柱状图（用filtered）
num_bins = 20
filtered['bitrate_bin'] = pd.cut(filtered['bitrate'], bins=num_bins)
grouped_bin = filtered.groupby('bitrate_bin')["avg_iframe_size"].mean()

# 画法1：用区间中点作为x轴
bin_centers = [interval.mid for interval in grouped_bin.index]
plt.figure(figsize=(10,6))
plt.bar(bin_centers, grouped_bin.values, width=[interval.length for interval in grouped_bin.index], align='center', edgecolor='black')
plt.xlabel("Bitrate (bps)")
plt.ylabel("Average I-frame size (bytes)")
plt.title("Average I-frame size vs Bitrate (20 bins, by bin center, filtered)")
plt.grid(axis='y')
plt.tight_layout()
plt.savefig("output/iframe_vs_bitrate_bar_20bins_centered.png")
print("✅ 已保存 output/iframe_vs_bitrate_bar_20bins_centered.png")

# 画法2：用简化标签作为x轴
labels = [f"{int(interval.left/1e6)}M-{int(interval.right/1e6)}M" for interval in grouped_bin.index]
plt.figure(figsize=(10,6))
plt.bar(labels, grouped_bin.values)
plt.xlabel("Bitrate Range (Mbps)")
plt.ylabel("Average I-frame size (bytes)")
plt.title("Average I-frame size vs Bitrate (20 bins, simple label, filtered)")
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.tight_layout()
plt.savefig("output/iframe_vs_bitrate_bar_20bins_simplelabel.png")
print("✅ 已保存 output/iframe_vs_bitrate_bar_20bins_simplelabel.png")

# 新增：比特率分箱折线图（用简化标签，filtered）
plt.figure(figsize=(10,6))
plt.plot(labels, grouped_bin.values, marker='o')
plt.xlabel("Bitrate Range (Mbps)")
plt.ylabel("Average I-frame size (bytes)")
plt.title("Average I-frame size vs Bitrate (20 bins, line chart, filtered)")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig("output/iframe_vs_bitrate_line_20bins_simplelabel.png")
print("✅ 已保存 output/iframe_vs_bitrate_line_20bins_simplelabel.png")

# 新增：比特率 vs 平均I帧大小 折线图
sorted_df = merged.sort_values("bitrate")
plt.figure(figsize=(10,6))
plt.plot(sorted_df["bitrate"]/1e6, sorted_df["avg_iframe_size"], marker='o')
plt.xlabel("Bitrate (Mbps)")
plt.ylabel("Average I-frame size (bytes)")
plt.title("Average I-frame size vs Bitrate (Line Chart)")
plt.grid(True)
plt.tight_layout()
plt.savefig("output/iframe_vs_bitrate_line.png")
print("✅ 已保存 output/iframe_vs_bitrate_line.png")

# 画 I帧大小 vs 分辨率 柱状图（分辨率从小到大排序）
def res_key(res):
    try:
        w, h = map(int, res.split('x'))
        return w * h
    except:
        return 0

res_group = merged.groupby("resolution")["avg_iframe_size"].mean()
res_group = res_group.reset_index()
res_group["area"] = res_group["resolution"].apply(res_key)
res_group = res_group.sort_values("area")

plt.figure(figsize=(12,6))
plt.bar(res_group["resolution"], res_group["avg_iframe_size"])
plt.xlabel("Resolution")
plt.ylabel("Average I-frame size (bytes)")
plt.title("Average I-frame size vs Resolution (Bar Chart, sorted)")
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.tight_layout()
plt.savefig("output/iframe_vs_resolution_bar_sorted.png")
print("✅ 已保存 output/iframe_vs_resolution_bar_sorted.png")

# 新增：分辨率 vs 平均I帧大小 折线图
plt.figure(figsize=(12,6))
plt.plot(res_group["resolution"], res_group["avg_iframe_size"], marker='o')
plt.xlabel("Resolution")
plt.ylabel("Average I-frame size (bytes)")
plt.title("Average I-frame size vs Resolution (Line Chart, sorted)")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig("output/iframe_vs_resolution_line_sorted.png")
print("✅ 已保存 output/iframe_vs_resolution_line_sorted.png")