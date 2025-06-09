import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import math

# Read I-frame data
df = pd.read_csv("iframe_data.csv")
# Calculate how many packets are needed for each I-frame (each packet max 1430 bytes, round up)
sizes = df["size_bytes"].astype(int).apply(lambda x: math.ceil(x / 1430)).sort_values().values

# Calculate CDF
cdf = np.arange(len(sizes)) / len(sizes)

# Plotting
plt.figure(figsize=(8, 6))
plt.plot(sizes, cdf, label="CDF of I-frame Packets (1430 bytes/packet)")
plt.xlabel("I-frame Size (Packets, 1430 bytes/packet)")
plt.ylabel("CDF")
plt.title("CDF of I-frame Size (in Packets)")
plt.grid(True)
plt.legend()

# Output to file
os.makedirs("output2", exist_ok=True)
plt.savefig("output2/iframe_cdf_packets.png")
print("The plot has been saved as output2/iframe_cdf_packets.png")
