#!/bin/bash

# 服务器环境检查脚本
# 用于检查服务器是否满足部署要求，以及验证已部署服务的健康状态

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查结果统计
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════╗"
echo "║   AI公众号自动写作助手 Pro - 服务器环境检查   ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查函数
check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNING_CHECKS++))
    ((TOTAL_CHECKS++))
}

# ========================================
# 1. 操作系统检查
# ========================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 1. 操作系统检查${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID

    echo -e "操作系统: ${BLUE}$PRETTY_NAME${NC}"

    # 检查是否为支持的操作系统
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ] || [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
        check_pass "操作系统兼容性检查通过"
    else
        check_warning "操作系统 $OS 未经过测试，可能存在兼容性问题"
    fi
else
    check_fail "无法检测操作系统"
fi

# ========================================
# 2. 系统资源检查
# ========================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}💾 2. 系统资源检查${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查内存
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
echo -e "总内存: ${BLUE}${TOTAL_MEM}MB${NC}"

if [ "$TOTAL_MEM" -ge 4096 ]; then
    check_pass "内存充足 (${TOTAL_MEM}MB >= 4096MB 推荐值)"
elif [ "$TOTAL_MEM" -ge 2048 ]; then
    check_warning "内存满足最低要求 (${TOTAL_MEM}MB >= 2048MB)，但推荐 4GB+"
else
    check_fail "内存不足 (${TOTAL_MEM}MB < 2048MB 最低要求)"
fi

# 检查磁盘空间
AVAILABLE_DISK=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
echo -e "可用磁盘空间: ${BLUE}${AVAILABLE_DISK}GB${NC}"

if [ "$AVAILABLE_DISK" -ge 50 ]; then
    check_pass "磁盘空间充足 (${AVAILABLE_DISK}GB >= 50GB 推荐值)"
elif [ "$AVAILABLE_DISK" -ge 20 ]; then
    check_warning "磁盘空间满足最低要求 (${AVAILABLE_DISK}GB >= 20GB)，但推荐 50GB+"
else
    check_fail "磁盘空间不足 (${AVAILABLE_DISK}GB < 20GB 最低要求)"
fi

# 检查 CPU
CPU_CORES=$(nproc)
echo -e "CPU 核心数: ${BLUE}${CPU_CORES}${NC}"

if [ "$CPU_CORES" -ge 2 ]; then
    check_pass "CPU 核心数充足 (${CPU_CORES} >= 2)"
else
    check_warning "CPU 核心数较少 (${CPU_CORES} < 2)，可能影响性能"
fi

# ========================================
# 3. 必要软件检查
# ========================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🛠️  3. 必要软件检查${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查 Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
    echo -e "Docker 版本: ${BLUE}${DOCKER_VERSION}${NC}"
    check_pass "Docker 已安装"

    # 检查 Docker 服务状态
    if systemctl is-active --quiet docker; then
        check_pass "Docker 服务正在运行"
    else
        check_fail "Docker 服务未运行"
    fi

    # 检查当前用户是否在 docker 组
    if groups | grep -q docker || [ "$EUID" -eq 0 ]; then
        check_pass "用户有 Docker 执行权限"
    else
        check_warning "当前用户不在 docker 组，可能需要 sudo"
    fi
else
    check_fail "Docker 未安装"
fi

# 检查 Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | awk '{print $4}' | sed 's/,//')
    echo -e "Docker Compose 版本: ${BLUE}${COMPOSE_VERSION}${NC}"
    check_pass "Docker Compose 已安装"
else
    check_fail "Docker Compose 未安装"
fi

# 检查 Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    echo -e "Git 版本: ${BLUE}${GIT_VERSION}${NC}"
    check_pass "Git 已安装"
else
    check_fail "Git 未安装"
fi

# 检查 curl
if command -v curl &> /dev/null; then
    check_pass "curl 已安装"
else
    check_warning "curl 未安装，建议安装"
fi

# ========================================
# 4. 网络和端口检查
# ========================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🌐 4. 网络和端口检查${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查端口占用
check_port() {
    local port=$1
    local service=$2

    if ss -tuln 2>/dev/null | grep -q ":${port} " || netstat -tuln 2>/dev/null | grep -q ":${port} "; then
        check_warning "端口 ${port} (${service}) 已被占用"
    else
        check_pass "端口 ${port} (${service}) 可用"
    fi
}

check_port 80 "HTTP"
check_port 443 "HTTPS"
check_port 22 "SSH"

# 检查外网连通性
if curl -s --max-time 5 https://www.google.com > /dev/null 2>&1; then
    check_pass "外网连通性正常"
else
    check_warning "无法连接到外网，可能影响 Docker 镜像拉取"
fi

# 检查 GitHub 连通性
if curl -s --max-time 5 https://github.com > /dev/null 2>&1; then
    check_pass "GitHub 连通性正常"
else
    check_warning "无法连接到 GitHub"
fi

# 检查 Docker Hub 连通性
if curl -s --max-time 5 https://hub.docker.com > /dev/null 2>&1; then
    check_pass "Docker Hub 连通性正常"
else
    check_warning "无法连接到 Docker Hub"
fi

# ========================================
# 5. 防火墙检查
# ========================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔥 5. 防火墙检查${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查 UFW
if command -v ufw &> /dev/null; then
    if sudo ufw status | grep -q "Status: active"; then
        check_pass "UFW 防火墙已启用"

        # 检查必要端口是否开放
        if sudo ufw status | grep -q "22/tcp.*ALLOW"; then
            check_pass "SSH 端口 (22) 已开放"
        else
            check_warning "SSH 端口 (22) 未开放"
        fi

        if sudo ufw status | grep -q "80/tcp.*ALLOW"; then
            check_pass "HTTP 端口 (80) 已开放"
        else
            check_warning "HTTP 端口 (80) 未开放"
        fi
    else
        check_warning "UFW 防火墙未启用"
    fi
elif command -v firewall-cmd &> /dev/null; then
    if sudo systemctl is-active --quiet firewalld; then
        check_pass "Firewalld 防火墙已启用"
    else
        check_warning "Firewalld 防火墙未启用"
    fi
else
    check_warning "未检测到防火墙配置"
fi

# ========================================
# 6. 项目配置检查
# ========================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📁 6. 项目配置检查${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

PROJECT_DIR="/opt/wechat-ai-writer"

# 检查项目目录
if [ -d "$PROJECT_DIR" ]; then
    echo -e "项目目录: ${BLUE}${PROJECT_DIR}${NC}"
    check_pass "项目目录存在"

    # 检查 Git 仓库
    if [ -d "$PROJECT_DIR/.git" ]; then
        check_pass "Git 仓库已初始化"

        # 检查 Git 状态
        cd "$PROJECT_DIR"
        CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
        if [ -n "$CURRENT_BRANCH" ]; then
            echo -e "当前分支: ${BLUE}${CURRENT_BRANCH}${NC}"
            check_pass "Git 分支检查通过"
        fi
    else
        check_warning "项目目录不是 Git 仓库"
    fi

    # 检查 .env 文件
    if [ -f "$PROJECT_DIR/.env" ]; then
        check_pass ".env 文件存在"

        # 检查必要的环境变量
        check_env_var() {
            local var_name=$1
            if grep -q "^${var_name}=" "$PROJECT_DIR/.env" && ! grep -q "^${var_name}=.*CHANGE_ME" "$PROJECT_DIR/.env" && ! grep -q "^${var_name}=.*your-.*-here" "$PROJECT_DIR/.env"; then
                check_pass "环境变量 ${var_name} 已配置"
            else
                check_warning "环境变量 ${var_name} 未配置或使用默认值"
            fi
        }

        check_env_var "SECRET_KEY"
        check_env_var "OPENAI_API_KEY"
        check_env_var "WECHAT_APP_ID"
        check_env_var "WECHAT_APP_SECRET"
    else
        check_warning ".env 文件不存在"
    fi

    # 检查 Docker Compose 配置
    if [ -f "$PROJECT_DIR/docker-compose.production.yml" ]; then
        check_pass "生产环境 Docker Compose 配置存在"
    else
        check_warning "生产环境 Docker Compose 配置不存在"
    fi
else
    check_warning "项目目录 ${PROJECT_DIR} 不存在"
fi

# ========================================
# 7. SSH 密钥检查
# ========================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔑 7. SSH 密钥检查${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -d "$HOME/.ssh" ]; then
    check_pass ".ssh 目录存在"

    # 检查权限
    SSH_DIR_PERM=$(stat -c %a "$HOME/.ssh" 2>/dev/null || stat -f %A "$HOME/.ssh" 2>/dev/null)
    if [ "$SSH_DIR_PERM" = "700" ]; then
        check_pass ".ssh 目录权限正确 (700)"
    else
        check_warning ".ssh 目录权限不正确 (当前: ${SSH_DIR_PERM}, 应为: 700)"
    fi

    # 检查 authorized_keys
    if [ -f "$HOME/.ssh/authorized_keys" ]; then
        KEY_COUNT=$(wc -l < "$HOME/.ssh/authorized_keys")
        echo -e "已授权的公钥数量: ${BLUE}${KEY_COUNT}${NC}"
        check_pass "authorized_keys 文件存在"

        AUTH_KEYS_PERM=$(stat -c %a "$HOME/.ssh/authorized_keys" 2>/dev/null || stat -f %A "$HOME/.ssh/authorized_keys" 2>/dev/null)
        if [ "$AUTH_KEYS_PERM" = "600" ]; then
            check_pass "authorized_keys 权限正确 (600)"
        else
            check_warning "authorized_keys 权限不正确 (当前: ${AUTH_KEYS_PERM}, 应为: 600)"
        fi
    else
        check_warning "authorized_keys 文件不存在"
    fi
else
    check_warning ".ssh 目录不存在"
fi

# ========================================
# 8. Docker 服务检查
# ========================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🐳 8. Docker 服务检查${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v docker &> /dev/null && [ -d "$PROJECT_DIR" ]; then
    # 检查是否有运行中的容器
    RUNNING_CONTAINERS=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -c "wechat-ai" || echo "0")

    if [ "$RUNNING_CONTAINERS" -gt 0 ]; then
        echo -e "运行中的容器数量: ${BLUE}${RUNNING_CONTAINERS}${NC}"
        check_pass "检测到运行中的项目容器"

        # 检查各个服务
        check_container() {
            local container_name=$1
            local service_name=$2

            if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
                # 检查容器健康状态
                HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "none")

                if [ "$HEALTH_STATUS" = "healthy" ]; then
                    check_pass "${service_name} 容器运行正常且健康"
                elif [ "$HEALTH_STATUS" = "none" ]; then
                    check_pass "${service_name} 容器运行正常 (无健康检查)"
                else
                    check_warning "${service_name} 容器运行中但健康状态异常: ${HEALTH_STATUS}"
                fi
            else
                check_warning "${service_name} 容器未运行"
            fi
        }

        check_container "wechat-ai-postgres" "PostgreSQL"
        check_container "wechat-ai-redis" "Redis"
        check_container "wechat-ai-backend" "Backend API"
        check_container "wechat-ai-celery-worker" "Celery Worker"
        check_container "wechat-ai-celery-beat" "Celery Beat"
        check_container "wechat-ai-frontend" "Frontend"
        check_container "wechat-ai-nginx" "Nginx"

        # 检查 Docker 网络
        if docker network ls | grep -q "wechat-ai"; then
            check_pass "Docker 网络已创建"
        else
            check_warning "Docker 网络未创建"
        fi

        # 检查 Docker 卷
        VOLUME_COUNT=$(docker volume ls | grep -c "wechat-ai" || echo "0")
        if [ "$VOLUME_COUNT" -gt 0 ]; then
            echo -e "数据卷数量: ${BLUE}${VOLUME_COUNT}${NC}"
            check_pass "Docker 数据卷已创建"
        else
            check_warning "未检测到 Docker 数据卷"
        fi
    else
        check_warning "未检测到运行中的项目容器"
    fi
fi

# ========================================
# 9. 服务可访问性检查
# ========================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🌍 9. 服务可访问性检查${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 获取服务器 IP
if command -v curl &> /dev/null; then
    SERVER_IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || echo "未知")
    echo -e "服务器公网 IP: ${BLUE}${SERVER_IP}${NC}"
fi

# 检查本地服务
if curl -s --max-time 5 http://localhost/health > /dev/null 2>&1; then
    check_pass "Nginx 健康检查端点响应正常"
else
    check_warning "Nginx 健康检查端点无响应"
fi

if curl -s --max-time 5 http://localhost:8000/api/health > /dev/null 2>&1; then
    check_pass "Backend API 健康检查端点响应正常"
else
    check_warning "Backend API 健康检查端点无响应"
fi

# ========================================
# 检查结果汇总
# ========================================
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 检查结果汇总${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo ""
echo -e "总检查项: ${BLUE}${TOTAL_CHECKS}${NC}"
echo -e "${GREEN}✅ 通过: ${PASSED_CHECKS}${NC}"
echo -e "${YELLOW}⚠️  警告: ${WARNING_CHECKS}${NC}"
echo -e "${RED}❌ 失败: ${FAILED_CHECKS}${NC}"
echo ""

# 计算通过率
if [ "$TOTAL_CHECKS" -gt 0 ]; then
    PASS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    echo -e "通过率: ${BLUE}${PASS_RATE}%${NC}"
    echo ""
fi

# 给出建议
if [ "$FAILED_CHECKS" -eq 0 ] && [ "$WARNING_CHECKS" -eq 0 ]; then
    echo -e "${GREEN}🎉 恭喜！服务器环境完美，可以开始部署了！${NC}"
elif [ "$FAILED_CHECKS" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  服务器基本满足要求，但有 ${WARNING_CHECKS} 项警告需要注意${NC}"
    echo -e "${YELLOW}建议解决警告项以获得更好的部署体验${NC}"
else
    echo -e "${RED}❌ 检测到 ${FAILED_CHECKS} 项严重问题，建议先解决后再部署${NC}"
    echo ""
    echo -e "${YELLOW}💡 修复建议：${NC}"
    echo -e "  1. 运行 setup-server.sh 脚本自动配置环境"
    echo -e "  2. 查看 SERVER-DEPLOY.md 获取详细的部署指南"
    echo -e "  3. 手动安装缺失的软件和依赖"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}检查完成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
