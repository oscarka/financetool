#!/bin/bash

# Railway 日志获取脚本
# 使用方法: ./get_railway_logs.sh [选项]

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认参数
LOG_TYPE="deployment"
OUTPUT_FILE=""
LINES=100
FILTER=""

# 显示帮助信息
show_help() {
    echo "Railway 日志获取脚本"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -t, --type TYPE        日志类型 (deployment|build) [默认: deployment]"
    echo "  -f, --filter FILTER    日志过滤条件 (例如: '@level:error')"
    echo "  -o, --output FILE      输出到文件"
    echo "  -l, --lines LINES      获取行数 [默认: 100]"
    echo "  -j, --json             JSON格式输出"
    echo "  -h, --help             显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -t deployment -f '@level:error' -l 50"
    echo "  $0 -t build -o build_logs.txt"
    echo "  $0 -j -f 'database connection'"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            LOG_TYPE="$2"
            shift 2
            ;;
        -f|--filter)
            FILTER="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -l|--lines)
            LINES="$2"
            shift 2
            ;;
        -j|--json)
            JSON_OUTPUT=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 检查 Railway CLI 是否已安装
check_railway_cli() {
    if ! command -v railway &> /dev/null; then
        echo -e "${RED}错误: Railway CLI 未安装${NC}"
        echo "请运行: npm install -g @railway/cli"
        exit 1
    fi
}

# 检查是否已登录和连接项目
check_railway_status() {
    if ! railway status &> /dev/null; then
        echo -e "${RED}错误: 未连接到Railway项目${NC}"
        echo "请先运行:"
        echo "  railway login"
        echo "  railway link"
        exit 1
    fi
}

# 获取项目信息
get_project_info() {
    echo -e "${BLUE}获取项目信息...${NC}"
    PROJECT_INFO=$(railway status --json 2>/dev/null)
    if [ $? -eq 0 ]; then
        PROJECT_NAME=$(echo "$PROJECT_INFO" | jq -r '.project.name // "未知项目"')
        SERVICE_NAME=$(echo "$PROJECT_INFO" | jq -r '.service.name // "未知服务"')
        ENVIRONMENT=$(echo "$PROJECT_INFO" | jq -r '.environment.name // "未知环境"')
        echo -e "${GREEN}项目: $PROJECT_NAME${NC}"
        echo -e "${GREEN}服务: $SERVICE_NAME${NC}"
        echo -e "${GREEN}环境: $ENVIRONMENT${NC}"
    fi
}

# 构建日志命令
build_log_command() {
    local cmd="railway logs"
    
    if [ "$LOG_TYPE" = "build" ]; then
        cmd="$cmd --build"
    elif [ "$LOG_TYPE" = "deployment" ]; then
        cmd="$cmd --deployment"
    fi
    
    if [ "$JSON_OUTPUT" = true ]; then
        cmd="$cmd --json"
    fi
    
    echo "$cmd"
}

# 格式化输出
format_output() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local separator="=" 
    local line=$(printf "%.80s" "$separator$separator$separator$separator$separator$separator$separator$separator$separator$separator")
    
    echo "$line"
    echo "Railway 日志导出"
    echo "时间: $timestamp"
    echo "项目: ${PROJECT_NAME:-未知}"
    echo "服务: ${SERVICE_NAME:-未知}"
    echo "环境: ${ENVIRONMENT:-未知}"
    echo "类型: $LOG_TYPE"
    if [ -n "$FILTER" ]; then
        echo "过滤: $FILTER"
    fi
    echo "$line"
    echo ""
}

# 主函数
main() {
    echo -e "${YELLOW}Railway 日志获取工具${NC}"
    echo ""
    
    # 检查依赖
    check_railway_cli
    check_railway_status
    
    # 获取项目信息
    get_project_info
    echo ""
    
    # 构建命令
    local log_cmd=$(build_log_command)
    echo -e "${BLUE}执行命令: $log_cmd${NC}"
    echo ""
    
    # 获取日志
    if [ -n "$OUTPUT_FILE" ]; then
        echo -e "${YELLOW}正在保存日志到文件: $OUTPUT_FILE${NC}"
        {
            format_output
            eval "$log_cmd"
        } > "$OUTPUT_FILE"
        echo -e "${GREEN}日志已保存到: $OUTPUT_FILE${NC}"
        echo -e "${YELLOW}你可以将此文件内容复制给AI助手进行调试${NC}"
    else
        echo -e "${YELLOW}获取日志 (最近 $LINES 行):${NC}"
        echo ""
        format_output
        eval "$log_cmd" | head -n "$LINES"
        echo ""
        echo -e "${YELLOW}提示: 使用 -o 选项可以保存到文件${NC}"
        echo -e "${YELLOW}复制以上日志内容给AI助手进行bug调试${NC}"
    fi
}

# 运行主函数
main "$@"