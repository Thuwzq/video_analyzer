import pandas as pd
import matplotlib.pyplot as plt
import os

# 输出文件夹
os.makedirs("output2", exist_ok=True)

# 读取 I 帧数据
iframe_df = pd.read_csv("iframe_data.csv")
iframe_df.columns = [col.strip() for col in iframe_df.columns]
iframe_df["video"] = iframe_df["video"].str.replace(".txt", "")

# 读取视频信息数据
info_df = pd.read_csv("video_info.csv", encoding="utf-8-sig")
info_df.columns = [col.strip() for col in info_df.columns]

# 每个视频的平均 I 帧大小
avg_iframe = iframe_df.groupby("video")["size_bytes"].mean().reset_index()
avg_iframe.columns = ["video", "avg_iframe_size"]

# 合并数据
merged = pd.merge(avg_iframe, info_df, on="video")

# 筛除非法比特率
merged["bitrate"] = pd.to_numeric(merged["bitrate"], errors="coerce")
merged = merged[merged["bitrate"].notnull()]
merged["bitrate"] = merged["bitrate"].astype(int)

# 去除 I 帧大小异常值（IQR）
Q1 = merged["avg_iframe_size"].quantile(0.25)
Q3 = merged["avg_iframe_size"].quantile(0.75)
IQR = Q3 - Q1
filtered = merged[(merged["avg_iframe_size"] >= Q1 - 1.5 * IQR) &
                  (merged["avg_iframe_size"] <= Q3 + 1.5 * IQR)]

# 分辨率转为清晰度标签
def resolution_to_label(res):
    try:
        w, h = map(int, res.lower().split('x'))
        area = w * h
        if area <= 600_000:
            return "<=480p"
        elif area <= 1_000_000:
            return "720p"
        elif area <= 2_500_000:
            return "1080p"
        elif area <= 4_000_000:
            return "2K"
        elif area <= 8_500_000:
            return "4K"
        else:
            return "8K+"
    except:
        return "Unknown"

filtered["resolution_label"] = filtered["resolution"].apply(resolution_to_label)
filtered[["video", "resolution", "resolution_label", "avg_iframe_size"]].to_csv("output2/video_resolution_label.csv", index=False)
print("每个视频的分辨率类别和平均I帧大小已保存到 output2/video_resolution_label.csv")

# 统计每个清晰度类别下的视频数量
label_counts = filtered["resolution_label"].value_counts().sort_index()
print("每个清晰度类别下的视频数量：")
print(label_counts)
label_counts.to_csv("output2/resolution_label_counts.csv", header=["count"])
print("每个清晰度类别下的视频数量已保存到 output2/resolution_label_counts.csv")

# 按清晰度标签分组并求平均
res_group = filtered.groupby("resolution_label")["avg_iframe_size"].mean().reset_index()
res_group = res_group.sort_values("avg_iframe_size")  # 可改为固定顺序排序

# 指定清晰度标签顺序（从低到高）
# 指定清晰度标签顺序（从低到高）
label_order = ["<=480p", "720p", "1080p", "2K", "4K", "8K+"]

# 将 resolution_label 设置为分类变量，并指定顺序
res_group["resolution_label"] = pd.Categorical(res_group["resolution_label"], categories=label_order, ordered=True)
res_group = res_group.sort_values("resolution_label")

# 绘图
plt.figure(figsize=(10, 6))
bars = plt.bar(res_group["resolution_label"], res_group["avg_iframe_size"], color='skyblue', edgecolor='black')

# 数值标注
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 500, f"{int(height)}", 
             ha='center', va='bottom', fontsize=9)

plt.xlabel("Video Resolution Category")
plt.ylabel("Average I-frame size (bytes)")
plt.title("Average I-frame Size by Resolution Label")
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig("output2/iframe_by_resolution_label_bar.png")
print("✅ 图已保存至 output2/iframe_by_resolution_label_bar.png")
