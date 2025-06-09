import os
import re
import csv

input_dir = "results"
output_csv = "iframe_data.csv"

with open(output_csv, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["video", "frame_idx", "size_bytes"])

    for fname in os.listdir(input_dir):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(input_dir, fname)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "type=I" in line:
                    m = re.search(r"frame #(\d+): size before decode=(\d+)", line)
                    if m:
                        idx, size = m.groups()
                        writer.writerow([fname, idx, size])
