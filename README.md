# Video Analysis Utils

## Introduction
An personal util set for analysis videos

## Requirements
pkg-config  
FFmpeg

## Environments
We have run this project on MacOS ARM system, but we do not guarantee working on other systems.

## Build
```
#check if pkg-config can find ffmpeg libs
#if show "Package libavutil/libavformat was not found in the pkg-config search path."
#please make sure your pkg-config can find ffmpeg headers and libs
pkg-config --cflags --libs libavutil libavformat

./configure
make
```

## Run
```
./target/bin/all_video_frame_size ./videos/pilot.flv
```

## Functions
- Video statistic information
    - Get all video frames size: all_video_frame_size
- Split videos with Gop: We can get all Gop ranges for an input video file.
    - Split Flv file with Gop: flv_gop_splitter
