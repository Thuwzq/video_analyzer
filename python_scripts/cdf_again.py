import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import math

# 读取 I 帧数据
df = pd.read_csv("iframe_data.csv")
# 计算每个I帧需要多少个packet（每个packet最大1430字节，向上取整）
sizes = df["size_bytes"].astype(int).apply(lambda x: math.ceil(x / 1430)).sort_values().values

# 计算 CDF
cdf = np.arange(len(sizes)) / len(sizes)

# 画图
plt.figure(figsize=(8, 6))
plt.plot(sizes, cdf, label="CDF of I-frame Packets (1430 bytes/packet)")
plt.xlabel("I-frame Size (Packets, 1430 bytes/packet)")
plt.ylabel("CDF")
plt.title("CDF of I-frame Size (in Packets)")
plt.grid(True)
plt.legend()

# 输出到文件
os.makedirs("output2", exist_ok=True)
plt.savefig("output2/iframe_cdf_packets.png")
print("✅ 图像已保存为 output2/iframe_cdf_packets.png")
