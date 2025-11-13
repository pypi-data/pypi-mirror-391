# 最终检查 - 准备发布

## ✅ 检查清单

### 1. 包结构
```
mcp-server/
├── opensearch_kb_mcp_server/
│   ├── __init__.py          ✅
│   ├── __main__.py          ✅
│   └── server.py            ✅
├── pyproject.toml           ✅
├── LICENSE                  ✅
├── README.md                ✅
└── test_simple.py           ✅
```

### 2. 测试

```bash
cd mcp-server

# 测试 1: 包可以导入
python -c "import opensearch_kb_mcp_server; print(opensearch_kb_mcp_server.__version__)"

# 测试 2: 可以作为模块运行
export OPENSEARCH_KB_API_URL="https://example.com"
export OPENSEARCH_KB_API_TOKEN="dummy"
python -m opensearch_kb_mcp_server &
PID=$!
sleep 2
kill $PID

# 测试 3: MCP 协议测试
python test_simple.py

# 测试 4: 命令可用（安装后）
pip install -e .
opensearch-knowledge-base-mcp-server --help || echo "Command installed"
```

### 3. 配置检查

编辑 `pyproject.toml`，确认：

- [ ] `name` - 包名正确
- [ ] `version` - 版本号正确
- [ ] `authors` - 作者信息正确
- [ ] `[project.urls]` - GitHub URL 正确
- [ ] `[project.scripts]` - 入口点正确

### 4. 文档检查

- [ ] README.md - 安装和使用说明完整
- [ ] QUICKSTART.md - 快速开始指南
- [ ] TROUBLESHOOTING.md - 故障排除
- [ ] PUBLISHING.md - 发布指南

### 5. 发布前测试

```bash
cd mcp-server

# 构建包
python -m build

# 检查包内容
tar -tzf dist/opensearch-knowledge-base-mcp-server-*.tar.gz | head -20

# 检查 wheel
unzip -l dist/opensearch_knowledge_base_mcp_server-*.whl
```

### 6. 本地安装测试

```bash
# 创建虚拟环境测试
python -m venv test_env
source test_env/bin/activate  # macOS/Linux
# 或 test_env\Scripts\activate  # Windows

# 从构建的包安装
pip install dist/opensearch_knowledge_base_mcp_server-*.whl

# 测试命令
opensearch-knowledge-base-mcp-server --help

# 测试运行
export OPENSEARCH_KB_API_URL="https://your-url"
export OPENSEARCH_KB_API_TOKEN="your-token"
python -m opensearch_kb_mcp_server

# 清理
deactivate
rm -rf test_env
```

## 🚀 准备发布

所有检查通过后：

### 选项 1: 使用交互式脚本

```bash
./publish_interactive.sh
```

### 选项 2: 手动发布

```bash
# 1. 清理
rm -rf dist/ build/ *.egg-info

# 2. 构建
python -m build

# 3. 上传到 TestPyPI（测试）
python -m twine upload --repository testpypi dist/*

# 4. 测试安装
pip install --index-url https://test.pypi.org/simple/ opensearch-knowledge-base-mcp-server

# 5. 上传到 PyPI（生产）
python -m twine upload dist/*
```

## ✅ 发布后验证

```bash
# 1. 检查 PyPI 页面
open https://pypi.org/project/opensearch-knowledge-base-mcp-server/

# 2. 测试安装
pip install opensearch-knowledge-base-mcp-server

# 3. 测试 uvx
uvx opensearch-knowledge-base-mcp-server --help

# 4. 在 AI Agent 中配置测试
```

## 📝 发布后任务

- [ ] 在 GitHub 创建 Release
- [ ] 更新主 README.md
- [ ] 通知用户
- [ ] 更新文档链接

## 🎉 完成！

你的 MCP Server 现在可以被全世界的 AI Agent 使用了！
