#!/bin/bash

echo "video,bitrate,resolution" > video_info.csv

video_files=(videos/*)
total=${#video_files[@]}
count=0

for f in "${video_files[@]}"; do
    count=$((count + 1))
    filename=$(basename "$f")

    echo "[${count}/${total}] 处理中: $filename"

    # 获取比特率
    bitrate=$(ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate -of csv=p=0 "$f")
    
    # 获取分辨率
    resolution=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$f" | awk -F',' '{print $1"x"$2}')
    
    # 如果比特率或分辨率获取失败，则标记为 unknown
    if [[ -z "$bitrate" || -z "$resolution" ]]; then
        echo "⚠️  无法解析 $filename"
        bitrate="0"
        resolution="unknown"
    fi

    echo "$filename,$bitrate,$resolution" >> video_info.csv
done

echo "✅ 全部处理完成，共 $total 个视频，结果已保存至 video_info.csv"
