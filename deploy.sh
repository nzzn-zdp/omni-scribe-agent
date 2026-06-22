#!/bin/bash

# OmniScribeAgent 部署脚本
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 项目配置
REPO_URL="git@github.com:nzzn-zdp/omni-scribe-agent.git"
PROJECT_DIR=$(pwd)
CONTAINER_NAME="omni-scribe-agent"

# Docker Compose命令
DOCKER_COMPOSE=""

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

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_warn "Docker未安装，开始安装..."
        # 使用阿里云镜像安装
        curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
        # 配置Docker镜像加速
        sudo mkdir -p /etc/docker
        sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://registry.docker-cn.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
EOF
        sudo systemctl daemon-reload
        sudo systemctl restart docker
        print_info "Docker安装完成"
    else
        print_info "Docker已安装"
    fi
}

# 检查Docker Compose是否安装
check_docker_compose() {
    # 优先使用docker compose (新版)
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
        print_info "Docker Compose已安装 (插件模式)"
        return
    fi
    
    # 检查docker-compose命令
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
        print_info "Docker Compose已安装"
        return
    fi
    
    print_warn "Docker Compose未安装，开始安装..."
    
    # 创建目录
    sudo mkdir -p /usr/local/bin
    
    # 使用国内镜像快速安装
    sudo curl -L "https://mirror.ghproxy.com/https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 设置权限
    sudo chmod +x /usr/local/bin/docker-compose
    
    DOCKER_COMPOSE="docker-compose"
    print_info "Docker Compose安装完成"
}

# 拉取代码
pull_code() {
    print_info "拉取最新代码..."
    
    if [ -d ".git" ]; then
        # 已有git仓库，丢弃本地修改并拉取更新
        git checkout -- . 2>/dev/null || true
        git clean -fd 2>/dev/null || true
        git pull origin master
    else
        # 克隆仓库
        git clone $REPO_URL temp_repo
        # 移动文件到当前目录
        shopt -s dotglob
        mv temp_repo/* temp_repo/.* . 2>/dev/null || true
        rm -rf temp_repo
    fi
    
    print_info "代码拉取完成"
}

# 创建必要目录
create_dirs() {
    print_info "创建必要目录..."
    mkdir -p data/db data/logs data/drafts config
    print_info "目录创建完成"
}

# 配置环境变量
setup_env() {
    if [ ! -f ".env" ]; then
        print_info "创建环境变量文件..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warn "请编辑 .env 文件配置API密钥等信息"
        else
            cat > .env << EOF
APP_NAME=OmniScribeAgent
APP_VERSION=1.0.0
DEBUG=false
DATABASE_URL=sqlite+aiosqlite:///./data/db/omniscribe.db
REDIS_URL=redis://localhost:6379/0
EOF
        fi
    else
        print_info "环境变量文件已存在"
    fi
}

# 停止旧容器
stop_old_container() {
    print_info "停止旧容器..."
    $DOCKER_COMPOSE down 2>/dev/null || true
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    print_info "旧容器已停止"
}

# 构建并启动服务
build_and_start() {
    print_info "构建Docker镜像..."
    $DOCKER_COMPOSE build --no-cache
    
    print_info "启动服务..."
    $DOCKER_COMPOSE up -d
    
    print_info "等待服务启动..."
    sleep 5
    
    # 检查服务状态
    if $DOCKER_COMPOSE ps | grep -q "Up"; then
        print_info "服务启动成功!"
    else
        print_error "服务启动失败，请查看日志:"
        $DOCKER_COMPOSE logs
        exit 1
    fi
}

# 初始化配置
init_configs() {
    print_info "初始化系统配置..."
    sleep 2
    curl -X POST http://localhost:8000/api/admin/configs/init 2>/dev/null || print_warn "配置初始化将在首次访问时自动完成"
}

# 显示部署信息
show_info() {
    echo ""
    echo "========================================="
    echo "       OmniScribeAgent 部署完成!"
    echo "========================================="
    echo ""
    echo "应用地址: http://$(hostname -I | awk '{print $1}'):8000"
    echo "管理界面: http://$(hostname -I | awk '{print $1}'):8000/settings"
    echo ""
    echo "常用命令:"
    echo "  查看日志: $DOCKER_COMPOSE logs -f"
    echo "  重启服务: $DOCKER_COMPOSE restart"
    echo "  停止服务: $DOCKER_COMPOSE down"
    echo "  查看状态: $DOCKER_COMPOSE ps"
    echo ""
    echo "首次使用请访问系统设置页面初始化配置"
    echo "========================================="
}

# 主函数
main() {
    print_info "开始部署 OmniScribeAgent..."
    echo ""
    
    check_docker
    check_docker_compose
    pull_code
    create_dirs
    setup_env
    stop_old_container
    build_and_start
    init_configs
    show_info
}

# 执行主函数
main