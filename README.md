# copchecker
Video Copyright Checker

# RUN
```
make run
```

#STOP
```
make stop
```

# TEST
```
curl -X POST "http://localhost:1111/video" \
  -F "video=@/path/to/your/video.mp4" \
  -F "name=video.mp4" \
  -F "index=true"
```

# GET
```
curl http://localhost:1111/video/{uuid}
```
# GET PROCESSING
```
curl http://localhost:1111/processing/{uuid}
```
