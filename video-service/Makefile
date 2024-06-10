.PHONY: build
build:
	go build -o bin/video-service cmd/service/main.go

.PHONY: run
	@build
run:
	go run cmd/service/main.go

.PHONY: test
test:
	go test -v ./...

.PHONY: lint
lint:
	golangci-lint run

.PHONY: format
format:	
	gofmt -w -s .

.PHONY: vendor
vendor:
	go mod vendor
