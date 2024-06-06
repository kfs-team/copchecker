#!/bin/sh

# Upload video script

# Usage:
# ./upload_video.sh /path/to/your/video.mp4

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 /path/to/your/video.mp4"
    exit 1
fi

VIDEO_PATH=$1

curl -X POST http://127.0.0.1:9999/upload -F "video=@${VIDEO_PATH}"
