# 更新 MCP Server

## 包名已更改

**旧包名**: `opensearch-knowledge-base-mcp-server` (已被占用)  
**新包名**: `opensearch-kb-mcp-server` ✅

## 更新步骤

### 1. 更新配置

编辑你的 q cli 配置文件，更新包名：

**旧配置**:
```json
{
  "mcpServers": {
    "opensearch-kb": {
      "command": "python",
      "args": ["-m", "opensearch_kb_mcp_server"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://your-api-url",
        "OPENSEARCH_KB_API_TOKEN": "your-token"
      }
    }
  }
}
```

**新配置** (使用 uvx，发布后):
```json
{
  "mcpServers": {
    "opensearch-kb": {
      "command": "uvx",
      "args": ["opensearch-kb-mcp-server"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://your-api-url",
        "OPENSEARCH_KB_API_TOKEN": "your-token"
      }
    }
  }
}
```

### 2. 清理旧版本

#### 如果使用本地安装

```bash
# 卸载旧包（如果有）
pip uninstall opensearch-knowledge-base-mcp-server -y
pip uninstall opensearch_kb_mcp_server -y

# 安装新包
pip install opensearch-kb-mcp-server
```

#### 如果使用 uvx

```bash
# uvx 会自动使用最新版本，但可以手动清理缓存

# 查找 uvx 缓存位置
echo $HOME/.local/share/uv/

# 清理特定包的缓存
rm -rf ~/.local/share/uv/cache/opensearch*

# 或清理所有 uvx 缓存
uvx cache clean
```

### 3. 重启 q cli

```bash
# 完全退出 q cli
# 然后重新启动

# q cli 会自动下载新版本
```

### 4. 验证

```bash
# 测试 MCP Server
uvx opensearch-kb-mcp-server --help

# 或查看版本
python -c "import opensearch_kb_mcp_server; print(opensearch_kb_mcp_server.__version__)"
```

## 本地开发版本

如果你在本地开发，使用本地路径：

```json
{
  "mcpServers": {
    "opensearch-kb": {
      "command": "python",
      "args": ["-m", "opensearch_kb_mcp_server"],
      "cwd": "/path/to/mcp-server",
      "env": {
        "OPENSEARCH_KB_API_URL": "https://your-api-url",
        "OPENSEARCH_KB_API_TOKEN": "your-token"
      }
    }
  }
}
```

然后：
```bash
cd /path/to/mcp-server
pip install -e .
```

## 故障排除

### 问题: 仍然使用旧版本

**解决**:
1. 完全退出 q cli
2. 清理缓存:
   ```bash
   rm -rf ~/.local/share/uv/cache/opensearch*
   ```
3. 删除旧的虚拟环境（如果有）
4. 重启 q cli

### 问题: 找不到包

**解决**:
1. 确认包已发布: https://pypi.org/project/opensearch-kb-mcp-server/
2. 等待几分钟（PyPI 索引更新）
3. 手动安装测试:
   ```bash
   pip install opensearch-kb-mcp-server
   ```

### 问题: 配置错误

**解决**:
1. 检查 JSON 语法
2. 确认包名正确: `opensearch-kb-mcp-server`
3. 确认环境变量已设置
4. 查看 q cli 日志

## 推荐配置

### 生产环境（使用 PyPI）

```json
{
  "mcpServers": {
    "opensearch-kb": {
      "command": "uvx",
      "args": ["opensearch-kb-mcp-server"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://your-api-url",
        "OPENSEARCH_KB_API_TOKEN": "your-token"
      }
    }
  }
}
```

**优点**:
- ✅ 自动使用最新版本
- ✅ 无需手动安装
- ✅ 隔离的环境

### 开发环境（使用本地代码）

```json
{
  "mcpServers": {
    "opensearch-kb": {
      "command": "python",
      "args": ["-m", "opensearch_kb_mcp_server"],
      "cwd": "/path/to/your/repo/mcp-server",
      "env": {
        "OPENSEARCH_KB_API_URL": "https://your-api-url",
        "OPENSEARCH_KB_API_TOKEN": "your-token"
      }
    }
  }
}
```

**优点**:
- ✅ 可以实时修改代码
- ✅ 便于调试
- ✅ 不需要重新发布

## 版本管理

### 固定版本

如果需要固定特定版本：

```json
{
  "mcpServers": {
    "opensearch-kb": {
      "command": "uvx",
      "args": ["opensearch-kb-mcp-server==1.0.0"],
      "env": {...}
    }
  }
}
```

### 更新到最新版本

```bash
# 清理缓存
rm -rf ~/.local/share/uv/cache/opensearch*

# 重启 q cli
# uvx 会自动下载最新版本
```

## 检查当前版本

```bash
# 方法 1: 使用 pip
pip show opensearch-kb-mcp-server

# 方法 2: 使用 Python
python -c "import opensearch_kb_mcp_server; print(opensearch_kb_mcp_server.__version__)"

# 方法 3: 查看 PyPI
curl -s https://pypi.org/pypi/opensearch-kb-mcp-server/json | jq -r '.info.version'
```

## 自动更新

uvx 默认行为：
- ✅ 每次启动时检查更新
- ✅ 自动下载新版本
- ✅ 使用缓存加速

如果想强制更新：
```bash
uvx --refresh opensearch-kb-mcp-server
```
