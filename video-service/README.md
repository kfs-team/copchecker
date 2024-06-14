### Video Service

curl http://localhost:9999/video/{uuid}

curl -X POST "http://localhost:9999/video" \
  -F "video=@/path/to/your/video.mp4" \
  -F "name=video.mp4" \
  -F "index=true"

Или же запуск скрипта:

./upload_video.sh /path/to/your/video.mp4 [true/false]
