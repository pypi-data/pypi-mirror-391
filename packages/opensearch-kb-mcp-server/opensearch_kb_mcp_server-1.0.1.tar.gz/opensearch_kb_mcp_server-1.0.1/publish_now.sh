#!/bin/bash
# 快速发布脚本

echo "========================================="
echo "发布 opensearch-kb-mcp-server 到 PyPI"
echo "========================================="
echo ""

# 检查 dist 目录
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo "❌ dist 目录不存在或为空"
    echo "请先运行: python -m build"
    exit 1
fi

echo "📦 准备发布的文件:"
ls -lh dist/
echo ""

# 检查包
echo "🔍 检查包..."
python -m twine check dist/*
echo ""

# 确认
read -p "确认发布到 PyPI? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "📤 上传到 PyPI..."
echo ""
echo "提示:"
echo "  Username: __token__"
echo "  Password: pypi-YOUR_TOKEN_HERE"
echo ""

python -m twine upload dist/*

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "🎉 发布成功！"
    echo "========================================="
    echo ""
    echo "包地址: https://pypi.org/project/opensearch-kb-mcp-server/"
    echo ""
    echo "用户可以使用:"
    echo "  uvx opensearch-kb-mcp-server"
    echo ""
    echo "配置示例:"
    echo '  "command": "uvx",'
    echo '  "args": ["opensearch-kb-mcp-server"]'
else
    echo ""
    echo "❌ 发布失败"
    echo "请检查错误信息"
fi
