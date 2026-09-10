#!/bin/bash
# 测试运行应用程序

cd "$(dirname "$0")"
# readonly PYTHON="$HOME/miniconda3/envs/python39/bin/python3"
readonly PYTHON=$(jq -r '.python_path' "${HOME}/common_config.json" | sed "s#~#$HOME#g")

$PYTHON -m app
