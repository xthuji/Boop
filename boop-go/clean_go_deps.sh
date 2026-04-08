#!/bin/bash

# 清理Go依赖文件缓存，仅保留当前项目用到的依赖

echo "开始清理Go依赖文件缓存..."

# 进入项目目录
cd "$(dirname "$0")"

# 确保go.mod文件存在
if [ ! -f "go.mod" ]; then
    echo "错误：未找到go.mod文件，请在项目根目录运行此脚本"
    exit 1
fi

# 清理未使用的依赖
echo "清理未使用的依赖..."
go mod tidy

# 清理模块缓存
echo "清理模块缓存..."
go clean -modcache

# 重新下载依赖
echo "重新下载依赖..."
go mod download

echo "依赖清理完成！"
echo "当前项目依赖："
go list -m all
