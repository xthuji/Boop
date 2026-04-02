#!/bin/bash

# 脚本名称：update_boop_scripts.sh
# 功能：将自定义脚本目录下的脚本文件移动到应用程序目录，替换原有的脚本文件

# 测试模式：设置为 true 时，只显示操作，不实际执行
TEST_MODE=false

# 源目录：自定义脚本目录（使用相对路径，支持从任何位置运行脚本）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/app/scripts"
SCRIPT_PATTERN="*.py"

# 目标目录：应用程序脚本目录
TARGET_DIR="/Applications/Boop.app/Contents/Resources/scripts"

# 备份目录：用于备份原有的脚本文件
BACKUP_DIR="${SCRIPT_DIR}/scripts.bak"

# 时间戳，用于备份目录命名
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 完整的备份目录路径
BACKUP_DIR_WITH_TIMESTAMP="${BACKUP_DIR}_${TIMESTAMP}"

# 显示脚本信息
echo "========================================"
echo "Boop 脚本更新工具"
echo "========================================"
echo "源目录: $SOURCE_DIR"
echo "目标目录: $TARGET_DIR"
echo "备份目录: $BACKUP_DIR_WITH_TIMESTAMP"
echo "========================================"

# 检查源目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
    echo "错误：源目录不存在！"
    exit 1
fi

# 检查目标目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo "错误：目标目录不存在！"
    echo "请确认 Boop 应用程序已正确安装。"
    exit 1
fi

# 创建备份目录
echo "正在创建备份目录..."
mkdir -p "$BACKUP_DIR_WITH_TIMESTAMP"

# 备份原有脚本文件
echo "正在备份原有脚本文件..."
if [ "$TEST_MODE" = false ]; then
    cp -r "$TARGET_DIR"/* "$BACKUP_DIR_WITH_TIMESTAMP"/
    if [ $? -eq 0 ]; then
        echo "备份成功：$BACKUP_DIR_WITH_TIMESTAMP"
    else
        echo "警告：备份失败，但将继续执行更新操作。"
    fi
else
    echo "[测试模式] 将要执行：cp -r \"$TARGET_DIR\"/* \"$BACKUP_DIR_WITH_TIMESTAMP\"/"
fi

# 清除目标目录中的脚本文件（保留lib目录）
echo "正在清除目标目录中的脚本文件..."
if [ "$TEST_MODE" = false ]; then
    find "$TARGET_DIR" -name "${SCRIPT_PATTERN}" -type f -not -path "*/lib/*" -delete
    if [ $? -eq 0 ]; then
        echo "清除成功"
    else
        echo "警告：清除失败，但将继续执行复制操作。"
    fi
else
    echo "[测试模式] 将要执行：find \"$TARGET_DIR\" -name \"${SCRIPT_PATTERN}\" -type f -not -path \"*/lib/*\" -delete"
fi

# 复制新的脚本文件
echo "正在复制新的脚本文件..."
if [ "$TEST_MODE" = false ]; then
    # 复制所有 .py 文件
    find "$SOURCE_DIR" -maxdepth 1 -name "${SCRIPT_PATTERN}" -type f -exec cp {} "$TARGET_DIR/" \;
    if [ $? -eq 0 ]; then
        echo "脚本文件复制成功"
    else
        echo "错误：脚本文件复制失败！"
        exit 1
    fi
    
    # 复制 lib 目录（如果存在）
    if [ -d "$SOURCE_DIR/lib" ]; then
        echo "正在复制lib目录..."
        cp -r "$SOURCE_DIR/lib" "$TARGET_DIR/"
        if [ $? -eq 0 ]; then
            echo "lib目录复制成功"
        else
            echo "警告：lib目录复制失败，但脚本文件已更新。"
        fi
    fi
else
    echo "[测试模式] 将要执行：find \"$SOURCE_DIR\" -maxdepth 1 -name \"${SCRIPT_PATTERN}\" -type f -exec cp {} \"$TARGET_DIR\"/ \\;"
    echo "[测试模式] 将要执行：cp -r \"$SOURCE_DIR/lib\" \"$TARGET_DIR\"/"
fi

# 显示操作结果
echo "========================================"
echo "脚本更新完成！"
echo "========================================"
echo "已将以下目录中的脚本文件复制到 Boop 应用程序："
echo "$SOURCE_DIR"
echo ""
echo "原有脚本文件已备份到："
echo "$BACKUP_DIR_WITH_TIMESTAMP"
echo "========================================"

# 提示用户重新启动应用程序
echo "请重新启动 Boop 应用程序以应用更改。"
echo ""
