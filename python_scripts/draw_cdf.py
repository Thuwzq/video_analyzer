import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 读取 I 帧数据
df = pd.read_csv("iframe_data.csv")
sizes = df["size_bytes"].astype(int).sort_values().values

# 计算 CDF
cdf = np.arange(len(sizes)) / len(sizes)

# 画图
plt.figure(figsize=(8, 6))
plt.plot(sizes, cdf, label="CDF of I-frame Sizes")
plt.xlabel("I-frame Size (Bytes)")
plt.ylabel("CDF")
plt.title("CDF of I-frame Sizes")
plt.grid(True)
plt.legend()

# 输出到文件
os.makedirs("output", exist_ok=True)
plt.savefig("output/iframe_cdf.png")
print("✅ 图像已保存为 output/iframe_cdf.png")
