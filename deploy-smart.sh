#!/bin/bash

# 🚀 FinanceTool 智能部署脚本
# 特点：自动从 Git 拉取最新代码，确保版本同步

echo "🚀 FinanceTool 智能部署助手"
echo "============================"
echo ""
echo "💡 功能：自动拉取最新代码 → 部署到 Cloudflare + Vercel"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查 Git 状态和更新
echo -e "${BLUE}🔍 检查代码版本...${NC}"

# 检查是否有未提交的更改
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️  检测到本地有未提交的更改：${NC}"
    git status --porcelain
    echo ""
    echo "选择操作："
    echo "1) 📝 提交更改并继续"
    echo "2) 🔄 暂存更改并拉取"
    echo "3) ❌ 取消部署"
    read -p "请选择 (1-3): " git_choice
    
    case $git_choice in
        1)
            echo -e "${BLUE}📝 提交本地更改...${NC}"
            git add .
            read -p "输入提交信息: " commit_msg
            git commit -m "$commit_msg"
            ;;
        2)
            echo -e "${BLUE}🔄 暂存本地更改...${NC}"
            git stash push -m "deploy-smart auto stash $(date)"
            echo "更改已暂存，稍后可用 'git stash pop' 恢复"
            ;;
        3)
            echo "已取消部署"
            exit 0
            ;;
    esac
fi

# 拉取最新代码
echo -e "${BLUE}⬇️  拉取最新代码...${NC}"
if git pull origin main; then
    echo -e "${GREEN}✅ 代码已更新到最新版本${NC}"
else
    echo -e "${RED}❌ 拉取代码失败，请检查网络或Git状态${NC}"
    echo "您可以手动运行: git pull origin main"
    read -p "是否继续使用当前代码部署？(y/N): " continue_choice
    if [[ ! "$continue_choice" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# 显示当前状态
echo "📊 当前服务状态："
echo "  Railway 后端: https://backend-production-2750.up.railway.app"
echo "  Cloudflare Worker: https://financetool-proxy.oscarzhangunsw.workers.dev"
echo "  Vercel 前端: https://financetool-qi8cex1ev-oscarkas-projects.vercel.app"
echo ""

# 选择部署目标
echo "选择要更新的服务："
echo "1) 🎯 智能部署（推荐）- 前端 + Worker"
echo "2) ⚡ 仅更新前端（最常用）"
echo "3) ☁️  仅更新 Worker（配置变更时）"
echo "4) 🧪 仅测试服务状态"
echo "5) ❌ 取消"
echo ""
read -p "请选择 (1-5): " choice

case $choice in
    1)
        echo -e "${BLUE}🎯 开始智能部署...${NC}"
        
        # 部署前端
        echo -e "${BLUE}⚡ 更新 Vercel 前端...${NC}"
        cd frontend
        echo "🔨 构建前端..."
        if npm run build; then
            echo "🚀 部署到 Vercel..."
            if vercel --prod --yes; then
                echo -e "${GREEN}✅ 前端更新完成${NC}"
            else
                echo -e "${RED}❌ Vercel 部署失败${NC}"
            fi
        else
            echo -e "${RED}❌ 前端构建失败${NC}"
        fi
        cd ..
        
        # 部署 Worker
        echo -e "${BLUE}☁️  更新 Cloudflare Worker...${NC}"
        cd cloudflare-workers
        if wrangler deploy; then
            echo -e "${GREEN}✅ Worker 更新完成${NC}"
        else
            echo -e "${RED}❌ Worker 部署失败${NC}"
        fi
        cd ..
        
        echo ""
        echo -e "${GREEN}🎉 智能部署完成！${NC}"
        ;;
        
    2)
        echo -e "${BLUE}⚡ 仅更新前端...${NC}"
        cd frontend
        echo "🔨 构建前端..."
        if npm run build; then
            echo "🚀 部署到 Vercel..."
            if vercel --prod --yes; then
                echo -e "${GREEN}✅ 前端更新完成${NC}"
            else
                echo -e "${RED}❌ Vercel 部署失败${NC}"
            fi
        else
            echo -e "${RED}❌ 前端构建失败${NC}"
        fi
        cd ..
        ;;
        
    3)
        echo -e "${BLUE}☁️  仅更新 Worker...${NC}"
        cd cloudflare-workers
        if wrangler deploy; then
            echo -e "${GREEN}✅ Worker 更新完成${NC}"
        else
            echo -e "${RED}❌ Worker 部署失败${NC}"
        fi
        cd ..
        ;;
        
    4)
        echo -e "${BLUE}🧪 测试服务状态...${NC}"
        
        echo "测试 Cloudflare Worker..."
        if curl -s "https://financetool-proxy.oscarzhangunsw.workers.dev/health" > /dev/null; then
            echo -e "${GREEN}✅ Cloudflare Worker 正常${NC}"
        else
            echo -e "${YELLOW}⚠️  Cloudflare Worker 可能有问题${NC}"
        fi
        
        echo "测试 Railway 后端..."
        if curl -s "https://backend-production-2750.up.railway.app/" > /dev/null; then
            echo -e "${GREEN}✅ Railway 后端正常${NC}"
        else
            echo -e "${YELLOW}⚠️  Railway 后端可能有问题${NC}"
        fi
        
        echo "测试 Vercel 前端..."
        if curl -s "https://financetool-qi8cex1ev-oscarkas-projects.vercel.app/" > /dev/null; then
            echo -e "${GREEN}✅ Vercel 前端正常${NC}"
        else
            echo -e "${YELLOW}⚠️  Vercel 前端可能有问题${NC}"
        fi
        ;;
        
    5)
        echo "已取消"
        exit 0
        ;;
        
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "📱 访问地址："
echo "  🌍 无需 VPN 前端: https://financetool-qi8cex1ev-oscarkas-projects.vercel.app"
echo "  🔗 无需 VPN API: https://financetool-proxy.oscarzhangunsw.workers.dev/api/v1"
echo ""
echo "💡 下次使用：./deploy-smart.sh"
echo "📝 提示：脚本会自动拉取最新代码，确保版本同步"
