# 发布步骤

## 快速发布（3 步）

### 步骤 1: 准备

```bash
cd mcp-server
./prepare_publish.sh
```

这会：
- ✅ 检查配置
- ✅ 运行测试
- ✅ 构建包

### 步骤 2: 创建 PyPI 账户和 Token

1. 注册: https://pypi.org/account/register/
2. 生成 Token: https://pypi.org/manage/account/token/
   - Name: `opensearch-kb-mcp`
   - Scope: "Entire account"
   - **复制 token**（以 `pypi-` 开头）

### 步骤 3: 发布

```bash
# 发布到 PyPI
python -m twine upload dist/*

# 输入:
# Username: __token__
# Password: pypi-YOUR_TOKEN_HERE
```

## 完成！

访问: https://pypi.org/project/opensearch-knowledge-base-mcp-server/

## 测试安装

```bash
# 使用 uvx
uvx opensearch-knowledge-base-mcp-server

# 或使用 pip
pip install opensearch-knowledge-base-mcp-server
```

## 用户配置

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

## 可选: 先测试 TestPyPI

```bash
# 上传到 TestPyPI
python -m twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ opensearch-knowledge-base-mcp-server

# 如果测试通过，再上传到生产 PyPI
python -m twine upload dist/*
```
