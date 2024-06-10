#!/bin/sh


# Usage:
# ./upload_video.sh /path/to/your/video.mp4 [true/false]

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 /path/to/your/video.mp4"
    exit 1
fi

VIDEO_PATH=$1
VIDEO_NAME=$(basename $VIDEO_PATH)
INDEX=$2 || false



curl -X POST "http://localhost:9999/video" \
  -F "video=@${VIDEO_PATH}" \
  -F "name=${VIDEO_NAME}" \
  -F "index=${INDEX}"
