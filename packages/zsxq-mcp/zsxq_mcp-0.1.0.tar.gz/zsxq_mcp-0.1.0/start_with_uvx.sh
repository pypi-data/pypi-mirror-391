#!/bin/bash

# ZSXQ MCP Server - UVX 启动脚本
# 使用 uvx 临时启动 MCP 服务器，无需预先安装依赖

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否在正确的目录
if [ ! -f "pyproject.toml" ]; then
    print_error "未找到 pyproject.toml 文件，请确保在项目根目录运行此脚本"
    exit 1
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    print_warning "未找到 .env 文件，将从 .env.example 创建模板"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_info "已创建 .env 文件，请编辑并填入你的配置信息"
        print_info "特别是需要设置 ZSXQ_COOKIE 和 ZSXQ_GROUP_ID"
    else
        print_error "未找到 .env.example 文件"
        exit 1
    fi
fi

print_info "启动 ZSXQ MCP 服务器..."
print_info "使用 uvx 从当前项目目录运行"

# 使用 uvx 启动 MCP 服务器
# --from . 指从当前目录的 pyproject.toml 安装
# --with httpx --with python-dotenv 明确指定依赖
uvx --from . --with httpx --with python-dotenv python -m zsxq_mcp.server