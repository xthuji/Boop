#!/bin/bash
# 测试运行应用程序

cd "$(dirname "$0")"

# 运行 Go 应用
echo "编译并运行应用..."
go run main.go
