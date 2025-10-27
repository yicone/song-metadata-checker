#!/bin/bash

# QQ Music API 上游服务设置脚本
# 自动克隆 Rain120/qq-music-api 到容器卷

set -e

echo "🚀 设置 QQ Music API 上游服务..."
echo ""

# 创建 volumes 目录
VOLUMES_DIR="./volumes"
QQ_MUSIC_DIR="$VOLUMES_DIR/qq-music-api"

if [ -d "$QQ_MUSIC_DIR" ]; then
    echo "📁 检测到已存在的 qq-music-api 目录"
    read -p "是否删除并重新克隆? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  删除旧目录..."
        rm -rf "$QQ_MUSIC_DIR"
    else
        echo "✅ 使用现有目录"
        echo ""
        echo "如果需要更新，请运行:"
        echo "  cd $QQ_MUSIC_DIR && git pull"
        exit 0
    fi
fi

# 创建 volumes 目录
mkdir -p "$VOLUMES_DIR"

# 克隆 Rain120/qq-music-api
echo "📥 克隆 Rain120/qq-music-api..."
git clone https://github.com/Rain120/qq-music-api.git "$QQ_MUSIC_DIR"

echo "✅ 克隆完成"
echo ""

# 检查项目结构
if [ -f "$QQ_MUSIC_DIR/package.json" ]; then
    echo "✅ 检测到 package.json"
else
    echo "❌ 错误: 未找到 package.json"
    echo "   请检查克隆的项目是否正确"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 设置完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Rain120 API 已克隆到: $QQ_MUSIC_DIR"
echo ""
echo "🐳 下一步: 启动容器化服务"
echo ""
echo "   # 使用完整配置（包含上游 API）"
echo "   docker-compose -f docker-compose-with-upstream.yml up -d"
echo ""
echo "   # 或使用简化配置（仅代理，需要手动启动上游）"
echo "   docker-compose up -d"
echo ""
echo "💡 提示:"
echo "   - 上游 API 端口: 3300"
echo "   - 代理 API 端口: 3001"
echo "   - 首次启动会自动安装 npm 依赖（可能需要 1-2 分钟）"
echo ""
