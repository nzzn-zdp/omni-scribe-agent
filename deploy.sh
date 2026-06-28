#!/bin/bash

# OmniScribeAgent 部署脚本

set -e

echo "=========================================="
echo "  OmniScribeAgent 部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python() {
    print_info "检查Python版本..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        print_info "Python版本: $PYTHON_VERSION"
    else
        print_error "Python3未安装，请先安装Python 3.11+"
        exit 1
    fi
}

# 检查并安装pip
check_pip() {
    print_info "检查pip..."
    if ! command -v pip3 &> /dev/null; then
        print_warn "pip3未安装，正在安装..."
        apt-get update && apt-get install -y python3-pip
    fi
    print_info "pip已就绪"
}

# 安装系统依赖
install_system_deps() {
    print_info "安装系统依赖..."
    apt-get update
    apt-get install -y \
        python3-dev \
        gcc \
        redis-server \
        sqlite3
    print_info "系统依赖安装完成"
}

# 安装Python依赖
install_python_deps() {
    print_info "安装Python依赖..."
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
    print_info "Python依赖安装完成"
}

# 检查并初始化环境配置
setup_env() {
    print_info "检查环境配置..."
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_warn "已从.env.example创建.env文件，请编辑配置"
        else
            print_error ".env.example文件不存在"
            exit 1
        fi
    else
        print_info ".env文件已存在"
    fi
}

# 创建数据目录
create_data_dirs() {
    print_info "创建数据目录..."
    mkdir -p data/db
    mkdir -p data/logs
    print_info "数据目录创建完成"
}

# 检查数据库
check_database() {
    print_info "检查数据库..."
    
    # 检查SQLite数据库是否存在
    if [ ! -f data/db/omniscribe.db ]; then
        print_warn "数据库不存在，将在首次启动时自动创建"
    else
        print_info "数据库已存在"
        # 检查数据库完整性
        sqlite3 data/db/omniscribe.db "PRAGMA integrity_check;" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            print_info "数据库完整性检查通过"
        else
            print_warn "数据库可能已损坏，建议备份后重新初始化"
        fi
    fi
}

# 检查Redis
check_redis() {
    print_info "检查Redis..."
    if command -v redis-cli &> /dev/null; then
        redis-cli ping > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            print_info "Redis连接正常"
        else
            print_warn "Redis未运行，正在启动..."
            redis-server --daemonize yes
            if [ $? -eq 0 ]; then
                print_info "Redis启动成功"
            else
                print_error "Redis启动失败，请手动启动"
            fi
        fi
    else
        print_warn "Redis未安装，部分功能可能受限"
    fi
}

# 初始化数据库表
init_database() {
    print_info "初始化数据库表..."
    python3 -c "
import asyncio
from src.database import init_db

async def main():
    await init_db()
    print('数据库表初始化完成')

asyncio.run(main())
"
    if [ $? -eq 0 ]; then
        print_info "数据库表初始化成功"
    else
        print_error "数据库表初始化失败"
        exit 1
    fi
}

# 启动应用
start_app() {
    print_info "启动OmniScribeAgent..."
    echo ""
    echo "=========================================="
    echo "  应用启动中..."
    echo "  访问地址: http://0.0.0.0:8000"
    echo "  管理界面: http://0.0.0.0:8000/settings"
    echo "=========================================="
    echo ""
    
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
}

# 主函数
main() {
    echo ""
    print_info "开始部署OmniScribeAgent..."
    echo ""
    
    check_python
    check_pip
    install_system_deps
    install_python_deps
    setup_env
    create_data_dirs
    check_database
    check_redis
    init_database
    
    echo ""
    print_info "部署准备完成！"
    echo ""
    
    start_app
}

# 运行主函数
main
