#!/bin/bash

###############################################################################
# AI 规则仓库自动配置脚本
# 功能：下载 airules 仓库并根据 AI 工具类型配置规则文件
# 支持的工具：Cursor、ClaudeCode
###############################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 常量定义
REPO_URL="http://git.dev.sh.ctripcorp.com/ibu/airules.git"
TEMP_DIR="./airules_temp"

# 获取目标目录：
# 1. 如果提供了命令行参数，使用参数指定的目录
# 2. 否则使用当前工作目录（执行命令的位置）
if [ -n "$1" ]; then
    TARGET_DIR="$1"
else
    TARGET_DIR="$(pwd)"
fi

###############################################################################
# 函数：打印彩色信息
###############################################################################
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

###############################################################################
# 函数：检查必要的命令
###############################################################################
check_requirements() {
    print_info "检查前置条件..."
    
    if ! command -v git &> /dev/null; then
        print_error "未找到 git 命令，请先安装 git"
        exit 1
    fi
    
    print_info "前置条件检查通过"
}

###############################################################################
# 函数：选择 AI 工具
###############################################################################
select_ai_tool() {
    echo ""
    echo "请选择您使用的 AI 客户端工具："
    echo "1) Cursor"
    echo "2) ClaudeCode"
    echo ""
    
    while true; do
        read -p "请输入选项 [1-2]: " choice
        case $choice in
            1)
                AI_TOOL="cursor"
                print_info "您选择了: Cursor"
                break
                ;;
            2)
                AI_TOOL="claudecode"
                print_info "您选择了: ClaudeCode"
                break
                ;;
            *)
                print_warning "无效选项，请重新输入"
                ;;
        esac
    done
}

###############################################################################
# 函数：下载规则仓库
###############################################################################
download_rules_repo() {
    print_info "开始下载规则仓库..."
    
    # 如果临时目录已存在，先删除
    if [ -d "$TEMP_DIR" ]; then
        print_warning "临时目录已存在，正在清理..."
        rm -rf "$TEMP_DIR"
    fi
    
    # 克隆仓库
    if git clone "$REPO_URL" "$TEMP_DIR" 2>&1; then
        print_info "仓库下载成功"
    else
        print_error "仓库下载失败，请检查网络连接或仓库地址"
        exit 1
    fi
}

###############################################################################
# 函数：拷贝规则文件
###############################################################################
copy_rules() {
    local tool=$1
    local target_dir=""
    
    case $tool in
        cursor)
            target_dir="$TARGET_DIR/.cursor"
            ;;
        claudecode)
            target_dir="$TARGET_DIR/.claude"
            ;;
    esac
    
    print_info "目标配置目录: $target_dir"
    
    # 创建目标目录（如果不存在）
    if [ ! -d "$target_dir" ]; then
        print_info "创建配置目录: $target_dir"
        mkdir -p "$target_dir"
    fi
    
    # 检查源文件夹是否存在
    if [ ! -d "$TEMP_DIR/rules" ]; then
        print_error "源仓库中未找到 rules 文件夹"
        cleanup
        exit 1
    fi
    
    if [ ! -d "$TEMP_DIR/commands" ]; then
        print_error "源仓库中未找到 commands 文件夹"
        cleanup
        exit 1
    fi
    
    # 拷贝文件
    print_info "正在拷贝 rules 文件夹..."
    cp -r "$TEMP_DIR/rules" "$target_dir/"
    
    print_info "正在拷贝 commands 文件夹..."
    cp -r "$TEMP_DIR/commands" "$target_dir/"
    
    print_info "文件拷贝完成！"
    echo ""
    print_info "配置文件已安装到: $target_dir"
    print_info "  - rules 目录: $target_dir/rules"
    print_info "  - commands 目录: $target_dir/commands"
}

###############################################################################
# 函数：清理临时文件
###############################################################################
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        print_info "清理临时文件..."
        rm -rf "$TEMP_DIR"
    fi
}

###############################################################################
# 主函数
###############################################################################
main() {
    echo "=========================================="
    echo "  AI 规则仓库自动配置脚本"
    echo "=========================================="
    echo ""
    
    print_info "目标安装目录: $TARGET_DIR"
    echo ""
    
    # 检查前置条件
    check_requirements
    
    # 选择工具
    select_ai_tool
    
    # 下载仓库
    download_rules_repo
    
    # 拷贝文件
    copy_rules "$AI_TOOL"
    
    # 清理临时文件
    cleanup
    
    echo ""
    echo "=========================================="
    print_info "配置完成！请重启您的 AI 工具以使配置生效"
    echo "=========================================="
}

# 捕获中断信号，确保清理临时文件
trap cleanup EXIT INT TERM

# 执行主函数
main

