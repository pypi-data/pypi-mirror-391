# 立即发布到 PyPI

## 快速步骤

### 1. 准备工作（5 分钟）

#### A. 创建 PyPI 账户
1. 访问 https://pypi.org/account/register/
2. 注册并验证邮箱

#### B. 生成 API Token
1. 登录后访问 https://pypi.org/manage/account/token/
2. 点击 "Add API token"
3. Name: `opensearch-kb-mcp`
4. Scope: "Entire account"
5. 点击 "Add token"
6. **复制 token**（以 `pypi-` 开头，只显示一次！）

#### C. 更新配置（可选）

编辑 `mcp-server/pyproject.toml`，更新你的信息：

```toml
authors = [
    { name = "Your Name", email = "your@email.com" }
]

[project.urls]
Homepage = "https://github.com/your-username/your-repo"
Repository = "https://github.com/your-username/your-repo"
```

### 2. 发布（2 分钟）

```bash
cd mcp-server

# 运行交互式发布脚本
./publish_interactive.sh
```

脚本会引导你完成：
1. ✅ 检查配置
2. ✅ 构建包
3. ✅ 选择发布到 TestPyPI 或 PyPI
4. ✅ 上传

### 3. 测试（1 分钟）

```bash
# 测试安装
uvx opensearch-knowledge-base-mcp-server --help

# 或
pip install opensearch-knowledge-base-mcp-server
```

## 手动发布（如果脚本不工作）

```bash
cd mcp-server

# 1. 安装工具
pip install build twine

# 2. 清理
rm -rf dist/ build/ *.egg-info

# 3. 构建
python -m build

# 4. 上传到 TestPyPI（测试）
python -m twine upload --repository testpypi dist/*
# 输入:
#   Username: __token__
#   Password: pypi-YOUR_TOKEN_HERE

# 5. 测试
pip install --index-url https://test.pypi.org/simple/ opensearch-knowledge-base-mcp-server

# 6. 上传到 PyPI（生产）
python -m twine upload dist/*
# 输入:
#   Username: __token__
#   Password: pypi-YOUR_TOKEN_HERE
```

## 发布后

### 验证

访问 https://pypi.org/project/opensearch-knowledge-base-mcp-server/

### 测试使用

```bash
# 设置环境变量
export OPENSEARCH_KB_API_URL="https://your-api-url"
export OPENSEARCH_KB_API_TOKEN="your-token"

# 运行
uvx opensearch-knowledge-base-mcp-server
```

### 配置 AI Agent

```json
{
  "mcpServers": {
    "opensearch-kb": {
      "command": "uvx",
      "args": ["opensearch-knowledge-base-mcp-server"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://your-api-url",
        "OPENSEARCH_KB_API_TOKEN": "your-token"
      }
    }
  }
}
```

## 常见问题

### Q: 包名已被占用

**错误**: `The name 'opensearch-knowledge-base-mcp-server' is already in use`

**解决**: 改名

```toml
# pyproject.toml
name = "opensearch-kb-mcp"  # 新名字
```

### Q: 版本已存在

**错误**: `File already exists`

**解决**: 增加版本号

```toml
# pyproject.toml
version = "1.0.1"  # 递增
```

### Q: Token 错误

**错误**: `Invalid credentials`

**解决**:
1. 确认 Username 是 `__token__`
2. 确认 Password 是完整的 token（包括 `pypi-` 前缀）
3. 重新生成 token

### Q: 网络错误

**错误**: `Connection timeout`

**解决**:
1. 检查网络连接
2. 使用代理（如果需要）
3. 稍后重试

## 需要帮助？

1. 查看 [PUBLISHING.md](PUBLISHING.md) 详细指南
2. 查看 [PRE_PUBLISH_CHECKLIST.md](PRE_PUBLISH_CHECKLIST.md) 检查清单
3. PyPI 文档: https://packaging.python.org/
