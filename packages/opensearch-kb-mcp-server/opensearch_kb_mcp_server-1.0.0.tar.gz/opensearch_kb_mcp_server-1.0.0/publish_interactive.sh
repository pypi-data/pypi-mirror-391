#!/bin/bash
# 交互式 PyPI 发布助手

set -e

echo "========================================="
echo "PyPI 发布助手"
echo "========================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误: 必须在 mcp-server 目录中运行"
    exit 1
fi

# 步骤 1: 检查配置
echo "📋 步骤 1: 检查配置"
echo "-----------------------------------"
echo ""

# 检查作者信息
AUTHOR_EMAIL=$(grep 'email = ' pyproject.toml | head -1 | cut -d'"' -f2)
if [[ "$AUTHOR_EMAIL" == *"example.com"* ]]; then
    echo "⚠️  警告: 作者邮箱还是示例值"
    echo "当前: $AUTHOR_EMAIL"
    read -p "是否继续？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "请先更新 pyproject.toml 中的作者信息"
        exit 1
    fi
fi

# 检查 GitHub URL
GITHUB_URL=$(grep 'Homepage = ' pyproject.toml | cut -d'"' -f2)
if [[ "$GITHUB_URL" == *"your-org"* ]] || [[ "$GITHUB_URL" == *"your-username"* ]]; then
    echo "⚠️  警告: GitHub URL 还是示例值"
    echo "当前: $GITHUB_URL"
    read -p "是否继续？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "请先更新 pyproject.toml 中的 GitHub URL"
        exit 1
    fi
fi

# 获取版本号
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
PACKAGE_NAME=$(grep '^name = ' pyproject.toml | cut -d'"' -f2)

echo "✅ 配置检查完成"
echo "   包名: $PACKAGE_NAME"
echo "   版本: $VERSION"
echo ""

# 步骤 2: 检查 PyPI 账户
echo "📋 步骤 2: PyPI 账户"
echo "-----------------------------------"
echo ""
echo "你需要："
echo "1. PyPI 账户 (https://pypi.org/account/register/)"
echo "2. API Token (https://pypi.org/manage/account/token/)"
echo ""
read -p "已经有 PyPI 账户和 Token？(y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "请先完成以下步骤："
    echo "1. 访问 https://pypi.org/account/register/ 注册"
    echo "2. 验证邮箱"
    echo "3. 访问 https://pypi.org/manage/account/token/ 生成 Token"
    echo "4. 保存 Token（以 pypi- 开头）"
    echo ""
    echo "完成后重新运行此脚本"
    exit 0
fi

# 步骤 3: 检查包名是否可用
echo ""
echo "📋 步骤 3: 检查包名"
echo "-----------------------------------"
echo ""
echo "检查包名 '$PACKAGE_NAME' 是否可用..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://pypi.org/project/$PACKAGE_NAME/")

if [ "$HTTP_CODE" = "404" ]; then
    echo "✅ 包名可用"
elif [ "$HTTP_CODE" = "200" ]; then
    echo "⚠️  包名已被占用: https://pypi.org/project/$PACKAGE_NAME/"
    echo ""
    echo "你可以："
    echo "1. 选择不同的包名（编辑 pyproject.toml）"
    echo "2. 如果这是你的包，继续更新版本"
    echo ""
    read -p "继续？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
else
    echo "⚠️  无法检查包名（网络问题？）"
fi

# 步骤 4: 安装构建工具
echo ""
echo "📋 步骤 4: 安装构建工具"
echo "-----------------------------------"
echo ""

if ! command -v twine &> /dev/null; then
    echo "安装 build 和 twine..."
    pip install build twine
    echo "✅ 工具已安装"
else
    echo "✅ 工具已安装"
fi

# 步骤 5: 构建包
echo ""
echo "📋 步骤 5: 构建包"
echo "-----------------------------------"
echo ""

echo "清理旧的构建..."
rm -rf dist/ build/ *.egg-info opensearch_kb_mcp_server.egg-info

echo "构建包..."
python -m build

echo ""
echo "✅ 构建完成:"
ls -lh dist/

# 步骤 6: 选择发布目标
echo ""
echo "📋 步骤 6: 发布"
echo "-----------------------------------"
echo ""
echo "选择发布目标:"
echo "1. TestPyPI (测试环境，推荐首次发布)"
echo "2. PyPI (生产环境)"
echo "3. 两者都发布（先 TestPyPI，再 PyPI）"
echo ""
read -p "选择 (1/2/3): " -n 1 -r
echo
echo ""

case $REPLY in
    1)
        echo "📤 上传到 TestPyPI..."
        python -m twine upload --repository testpypi dist/*
        echo ""
        echo "✅ 已上传到 TestPyPI"
        echo ""
        echo "测试安装:"
        echo "  pip install --index-url https://test.pypi.org/simple/ $PACKAGE_NAME"
        echo ""
        echo "或使用 uvx:"
        echo "  uvx --index-url https://test.pypi.org/simple/ $PACKAGE_NAME"
        ;;
    2)
        echo "📤 上传到 PyPI..."
        python -m twine upload dist/*
        echo ""
        echo "✅ 已上传到 PyPI"
        echo ""
        echo "包地址: https://pypi.org/project/$PACKAGE_NAME/"
        echo ""
        echo "用户可以使用:"
        echo "  uvx $PACKAGE_NAME"
        ;;
    3)
        echo "📤 上传到 TestPyPI..."
        python -m twine upload --repository testpypi dist/*
        echo ""
        echo "✅ 已上传到 TestPyPI"
        echo ""
        read -p "测试通过？继续上传到 PyPI？(y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo ""
            echo "📤 上传到 PyPI..."
            python -m twine upload dist/*
            echo ""
            echo "✅ 已上传到 PyPI"
            echo ""
            echo "包地址: https://pypi.org/project/$PACKAGE_NAME/"
        else
            echo "已停止"
            exit 0
        fi
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

# 完成
echo ""
echo "========================================="
echo "🎉 发布完成！"
echo "========================================="
echo ""
echo "下一步:"
echo "1. 测试安装: uvx $PACKAGE_NAME"
echo "2. 更新文档"
echo "3. 通知用户"
echo "4. 在 GitHub 创建 Release (git tag v$VERSION)"
echo ""
