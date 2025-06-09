#!/bin/bash

mkdir -p results

video_files=(videos/*)
total=${#video_files[@]}
count=0

for f in "${video_files[@]}"; do
    count=$((count + 1))
    filename=$(basename "$f")

    # 文件为空就跳过
    if [ ! -s "$f" ]; then
        echo "[${count}/${total}] ⚠️ 跳过空文件：$filename"
        continue
    fi

    echo "[${count}/${total}] 正在处理：$filename"
    ./all_video_frame_size "$f" > "results/${filename}.txt"

    if [ $? -eq 0 ]; then
        echo "✅ 完成：$filename"
    else
        echo "❌ 处理失败（可能是损坏文件）：$filename"
    fi
done

echo "📦 全部处理完成，共 ${total} 个视频"
