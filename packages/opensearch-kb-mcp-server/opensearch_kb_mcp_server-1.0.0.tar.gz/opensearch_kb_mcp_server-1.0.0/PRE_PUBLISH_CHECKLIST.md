# 发布前检查清单

在发布到 PyPI 之前，请完成以下步骤：

## ✅ 必须完成

### 1. 更新 pyproject.toml 中的信息

编辑 `mcp-server/pyproject.toml`：

```toml
[project]
authors = [
    { name = "Your Name", email = "your.email@example.com" }  # 改为你的信息
]

[project.urls]
Homepage = "https://github.com/your-username/your-repo"  # 改为你的 GitHub 仓库
Documentation = "https://github.com/your-username/your-repo/blob/main/docs/MCP_SERVER_GUIDE.md"
Repository = "https://github.com/your-username/your-repo"
Issues = "https://github.com/your-username/your-repo/issues"
```

### 2. 创建 PyPI 账户

1. 访问 https://pypi.org/account/register/
2. 注册账户
3. 验证邮箱

### 3. 生成 API Token

1. 登录 PyPI
2. 访问 https://pypi.org/manage/account/token/
3. 点击 "Add API token"
4. Token name: `opensearch-kb-mcp-server`
5. Scope: "Entire account" (首次发布) 或 "Project: opensearch-knowledge-base-mcp-server" (更新时)
6. 复制 token（以 `pypi-` 开头）
7. **保存好这个 token！它只显示一次**

### 4. 配置 PyPI 凭证

创建 `~/.pypirc` 文件：

```bash
cat > ~/.pypirc <<EOF
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
EOF

chmod 600 ~/.pypirc
```

或者在发布时手动输入。

### 5. 安装构建工具

```bash
pip install build twine
```

## 📋 可选但推荐

### 6. 测试 PyPI 账户（可选）

1. 访问 https://test.pypi.org/account/register/
2. 注册测试账户
3. 生成测试 token

### 7. 检查包名是否可用

访问 https://pypi.org/project/opensearch-knowledge-base-mcp-server/

- 如果显示 404：✅ 名字可用
- 如果已存在：❌ 需要改名

如果需要改名，编辑 `pyproject.toml`：
```toml
name = "opensearch-kb-mcp-server"  # 或其他名字
```

## 🚀 准备就绪

完成上述步骤后，运行：

```bash
cd mcp-server
./publish.sh
```

或手动发布：

```bash
cd mcp-server

# 清理
rm -rf dist/ build/ *.egg-info

# 构建
python -m build

# 上传到 TestPyPI（测试）
python -m twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ opensearch-knowledge-base-mcp-server

# 上传到 PyPI（生产）
python -m twine upload dist/*
```

## ❓ 常见问题

### Q: 包名已被占用怎么办？

A: 在 `pyproject.toml` 中改名：
```toml
name = "opensearch-kb-mcp"  # 新名字
```

然后更新配置中的命令：
```json
"args": ["opensearch-kb-mcp"]
```

### Q: 忘记保存 API Token？

A: 删除旧 token，重新生成一个新的。

### Q: 上传失败？

A: 检查：
1. Token 是否正确
2. 包名是否已存在
3. 版本号是否已发布过

## 📝 发布后

1. 测试安装：
   ```bash
   uvx opensearch-knowledge-base-mcp-server
   ```

2. 更新文档中的安装说明

3. 通知用户可以使用了

4. 在 GitHub 创建 Release
