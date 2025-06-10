#!/bin/bash

echo "video,bitrate,resolution" > video_info.csv

video_files=(videos/*)
total=${#video_files[@]}
count=0

for f in "${video_files[@]}"; do
    count=$((count + 1))
    filename=$(basename "$f")

    echo "[${count}/${total}] Processing: $filename"

    # Get bitrate
    bitrate=$(ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate -of csv=p=0 "$f")
    
    # Get resolution
    resolution=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$f" | awk -F',' '{print $1"x"$2}')
    
    # If bitrate or resolution fails to be obtained, mark as unknown
    if [[ -z "$bitrate" || -z "$resolution" ]]; then
        echo "Unable to parse $filename"
        bitrate="0"
        resolution="unknown"
    fi

    echo "$filename,$bitrate,$resolution" >> video_info.csv
done

echo "All processing completed, total $total videos, results saved to video_info.csv"
