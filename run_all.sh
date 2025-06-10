#!/bin/bash

mkdir -p results

video_files=(videos/*)
total=${#video_files[@]}
count=0

for f in "${video_files[@]}"; do
    count=$((count + 1))
    filename=$(basename "$f")

    # Skip if file is empty
    if [ ! -s "$f" ]; then
        echo "[${count}/${total}] ⚠️ Skipping empty file: $filename"
        continue
    fi

    echo "[${count}/${total}] Processing: $filename"
    ./all_video_frame_size "$f" > "results/${filename}.txt"

    if [ $? -eq 0 ]; then
        echo "Done: $filename"
    else
        echo "Processing failed (possibly corrupted file): $filename"
    fi
done

echo "All processing completed, total ${total} videos"
