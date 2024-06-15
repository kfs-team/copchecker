FROM golang:1.22-alpine AS builder

WORKDIR /app

COPY go.mod .
RUN go mod download

# Копируем исходные файлы
COPY . .

RUN go build -o bin/video-service cmd/service/main.go

FROM alpine:latest

WORKDIR /root/

COPY --from=builder /app/bin/video-service .

EXPOSE 1111

CMD ["./video-service"]
