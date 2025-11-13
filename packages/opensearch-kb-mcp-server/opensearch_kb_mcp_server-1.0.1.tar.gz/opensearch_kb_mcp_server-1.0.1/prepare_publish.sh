#!/bin/bash
# 准备发布到 PyPI

echo "========================================="
echo "准备发布到 PyPI"
echo "========================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误: 必须在 mcp-server 目录中运行"
    exit 1
fi

# 步骤 1: 更新配置
echo "📝 步骤 1: 检查配置"
echo "-----------------------------------"
echo ""

# 检查作者邮箱
AUTHOR_EMAIL=$(grep 'email = ' pyproject.toml | head -1 | cut -d'"' -f2)
echo "当前作者邮箱: $AUTHOR_EMAIL"

if [[ "$AUTHOR_EMAIL" == *"example.com"* ]]; then
    echo ""
    read -p "输入你的邮箱 (或按 Enter 跳过): " NEW_EMAIL
    if [ -n "$NEW_EMAIL" ]; then
        # 使用 Python 来更新（更可靠）
        python3 << EOF
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
content = re.sub(r'email = "[^"]*"', f'email = "$NEW_EMAIL"', content, count=1)
with open('pyproject.toml', 'w') as f:
    f.write(content)
print("✅ 邮箱已更新")
EOF
    fi
fi

# 检查 GitHub URL
GITHUB_URL=$(grep 'Homepage = ' pyproject.toml | cut -d'"' -f2)
echo ""
echo "当前 GitHub URL: $GITHUB_URL"

if [[ "$GITHUB_URL" == *"your-org"* ]] || [[ "$GITHUB_URL" == *"your-username"* ]]; then
    echo ""
    read -p "输入你的 GitHub 仓库 URL (或按 Enter 跳过): " NEW_URL
    if [ -n "$NEW_URL" ]; then
        python3 << EOF
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
content = re.sub(r'Homepage = "[^"]*"', f'Homepage = "$NEW_URL"', content)
content = re.sub(r'Documentation = "[^"]*"', f'Documentation = "$NEW_URL/blob/main/docs/MCP_SERVER_GUIDE.md"', content)
content = re.sub(r'Repository = "[^"]*"', f'Repository = "$NEW_URL"', content)
content = re.sub(r'Issues = "[^"]*"', f'Issues = "$NEW_URL/issues"', content)
with open('pyproject.toml', 'w') as f:
    f.write(content)
print("✅ GitHub URL 已更新")
EOF
    fi
fi

echo ""
echo "✅ 配置检查完成"
echo ""

# 步骤 2: 安装工具
echo "📦 步骤 2: 安装构建工具"
echo "-----------------------------------"
echo ""

pip install -q build twine
echo "✅ 工具已安装"
echo ""

# 步骤 3: 运行测试
echo "🧪 步骤 3: 运行测试"
echo "-----------------------------------"
echo ""

# 设置测试环境变量
export OPENSEARCH_KB_API_URL="${OPENSEARCH_KB_API_URL:-https://example.com}"
export OPENSEARCH_KB_API_TOKEN="${OPENSEARCH_KB_API_TOKEN:-dummy-token}"

python test_simple.py || {
    echo ""
    echo "❌ 测试失败"
    echo "请修复问题后重试"
    exit 1
}

echo ""

# 步骤 4: 构建包
echo "🔨 步骤 4: 构建包"
echo "-----------------------------------"
echo ""

# 清理旧构建
rm -rf dist/ build/ *.egg-info opensearch_kb_mcp_server.egg-info

# 构建
python -m build

echo ""
echo "✅ 构建完成:"
ls -lh dist/
echo ""

# 步骤 5: 检查包
echo "🔍 步骤 5: 检查包"
echo "-----------------------------------"
echo ""

python -m twine check dist/*

echo ""
echo "========================================="
echo "✅ 准备完成！"
echo "========================================="
echo ""
echo "下一步:"
echo ""
echo "1. 如果还没有 PyPI 账户:"
echo "   访问 https://pypi.org/account/register/"
echo ""
echo "2. 生成 API Token:"
echo "   访问 https://pypi.org/manage/account/token/"
echo "   复制 token (以 pypi- 开头)"
echo ""
echo "3. 发布到 TestPyPI (测试):"
echo "   python -m twine upload --repository testpypi dist/*"
echo "   Username: __token__"
echo "   Password: <your-testpypi-token>"
echo ""
echo "4. 发布到 PyPI (生产):"
echo "   python -m twine upload dist/*"
echo "   Username: __token__"
echo "   Password: <your-pypi-token>"
echo ""
echo "或者运行交互式脚本:"
echo "   ./publish_interactive.sh"
echo ""
