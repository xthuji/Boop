#!/bin/bash
# 测试运行应用程序

cd "$(dirname "$0")"

# 编译应用
echo "编译应用..."
cargo build

# 打印编译结果文件的大小
echo "编译结果文件大小："
ls -lh target/debug/boop

# 运行应用
echo "运行应用..."
cargo run
