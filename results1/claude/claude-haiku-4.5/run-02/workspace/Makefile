.PHONY: build test clean install

build:
	go mod tidy
	go build -o code-analyzer

test: build
	./code-analyzer .

install: build
	go install

clean:
	rm -f code-analyzer
	go clean

# Analyze the analyzer itself
self-analyze: build
	./code-analyzer .

# Build for multiple platforms
build-all:
	GOOS=linux GOARCH=amd64 go build -o code-analyzer-linux-amd64
	GOOS=darwin GOARCH=amd64 go build -o code-analyzer-darwin-amd64
	GOOS=darwin GOARCH=arm64 go build -o code-analyzer-darwin-arm64
	GOOS=windows GOARCH=amd64 go build -o code-analyzer-windows-amd64.exe

help:
	@echo "Available targets:"
	@echo "  build       - Build the binary"
	@echo "  test        - Build and test on current directory"
	@echo "  clean       - Remove build artifacts"
	@echo "  install     - Build and install to GOPATH"
	@echo "  self-analyze - Analyze the project itself"
	@echo "  build-all   - Build for linux, macOS, and Windows"
