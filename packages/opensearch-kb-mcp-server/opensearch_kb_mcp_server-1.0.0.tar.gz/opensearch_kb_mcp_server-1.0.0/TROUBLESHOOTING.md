# MCP Server 故障排除

## 常见错误

### 错误 1: "connection closed: initialize response"

**完整错误**:
```
McpError(ErrorData { code: ErrorCode(-32002), message: "connection closed: initialize response", data: None })
```

**原因**: MCP Server 在初始化时崩溃或退出

**解决方案**:

#### A. 检查环境变量

```bash
# 确保设置了必需的环境变量
export OPENSEARCH_KB_API_URL="https://your-api-url"
export OPENSEARCH_KB_API_TOKEN="your-token"

# 验证
echo $OPENSEARCH_KB_API_URL
echo $OPENSEARCH_KB_API_TOKEN
```

#### B. 测试 MCP Server

```bash
cd mcp-server

# 安装包
pip install -e .

# 测试运行
python -m opensearch_kb_mcp_server
# 应该等待输入，不应该立即退出
```

#### C. 查看详细日志

```bash
# 运行并查看 stderr 输出
python -m opensearch_kb_mcp_server 2>&1 | head -20
```

#### D. 检查配置文件

确保 AI Agent 配置正确：

```json
{
  "mcpServers": {
    "opensearch-kb": {
      "command": "python",
      "args": ["-m", "opensearch_kb_mcp_server"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://your-actual-url",
        "OPENSEARCH_KB_API_TOKEN": "your-actual-token"
      }
    }
  }
}
```

**注意**: 
- 不要有拼写错误
- URL 不要有尾部斜杠
- Token 要完整

### 错误 2: "OPENSEARCH_KB_API_URL environment variable is required"

**原因**: 环境变量未设置

**解决方案**:

在 AI Agent 配置中添加 `env` 部分：

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

### 错误 3: "API request failed with status 401"

**原因**: Token 无效或过期

**解决方案**:

1. 验证 Token:
   ```bash
   curl -X POST "$OPENSEARCH_KB_API_URL/api/v1/query" \
     -H "Authorization: Bearer $OPENSEARCH_KB_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"question":"test"}'
   ```

2. 如果失败，获取新 Token:
   ```bash
   curl -X POST "$OPENSEARCH_KB_API_URL/admin/tokens" \
     -H "X-Admin-API-Key: $ADMIN_API_KEY" \
     -d '{"name":"mcp-server","expires_days":90}'
   ```

3. 更新配置中的 Token

### 错误 4: "command not found: opensearch-knowledge-base-mcp-server"

**原因**: 包未安装或 uvx 未找到

**解决方案**:

#### A. 检查 uvx

```bash
# 安装 uv (包含 uvx)
pip install uv

# 或使用 homebrew (macOS)
brew install uv
```

#### B. 手动安装包

```bash
pip install opensearch-knowledge-base-mcp-server

# 测试
opensearch-knowledge-base-mcp-server --help
```

#### C. 使用完整路径

```json
{
  "command": "python",
  "args": ["-m", "opensearch_kb_mcp_server"]
}
```

### 错误 5: "Connection timeout"

**原因**: 网络问题或 API Gateway 不可达

**解决方案**:

1. 测试网络连接:
   ```bash
   curl -I $OPENSEARCH_KB_API_URL
   ```

2. 检查 API Gateway 状态

3. 检查防火墙/代理设置

4. 增加超时时间（在 server.py 中已设置为 60 秒）

## 调试步骤

### 1. 验证包安装

```bash
cd mcp-server
pip install -e .
python -c "import opensearch_kb_mcp_server; print(opensearch_kb_mcp_server.__version__)"
```

### 2. 测试 MCP 协议

```bash
cd mcp-server
./test_mcp_protocol.sh
```

### 3. 手动测试初始化

```bash
export OPENSEARCH_KB_API_URL="https://your-url"
export OPENSEARCH_KB_API_TOKEN="your-token"

# 发送初始化请求
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | \
  python -m opensearch_kb_mcp_server
```

应该返回类似：
```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"opensearch-knowledge-base","version":"1.0.0"}}}
```

### 4. 查看日志

MCP Server 的日志输出到 stderr：

```bash
python -m opensearch_kb_mcp_server 2>server.log &
# 使用 AI Agent
# 然后查看日志
cat server.log
```

### 5. 使用 RUST_BACKTRACE

如果是 Rust 客户端（如 q cli）：

```bash
RUST_BACKTRACE=full your-ai-agent-command
```

## 配置示例

### Claude Desktop (macOS)

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "opensearch-kb": {
      "command": "uvx",
      "args": ["opensearch-knowledge-base-mcp-server"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://xxx.execute-api.us-east-1.amazonaws.com",
        "OPENSEARCH_KB_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

### Cline (VS Code)

Settings → MCP Servers:

```json
{
  "mcpServers": {
    "opensearch-kb": {
      "command": "uvx",
      "args": ["opensearch-knowledge-base-mcp-server"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://xxx.execute-api.us-east-1.amazonaws.com",
        "OPENSEARCH_KB_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

### Kiro IDE

`.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "opensearch-kb": {
      "command": "uvx",
      "args": ["opensearch-knowledge-base-mcp-server"],
      "env": {
        "OPENSEARCH_KB_API_URL": "https://xxx.execute-api.us-east-1.amazonaws.com",
        "OPENSEARCH_KB_API_TOKEN": "your-token-here"
      },
      "disabled": false,
      "autoApprove": ["search_opensearch_knowledge"]
    }
  }
}
```

## 获取帮助

如果问题仍然存在：

1. 运行诊断脚本:
   ```bash
   cd mcp-server
   ./test_mcp_protocol.sh
   ```

2. 收集信息:
   - AI Agent 名称和版本
   - 错误消息（完整）
   - 配置文件内容（隐藏 token）
   - 日志输出

3. 检查文档:
   - [README.md](README.md)
   - [QUICKSTART.md](QUICKSTART.md)
   - [MCP Server Guide](../docs/MCP_SERVER_GUIDE.md)

4. 提交 Issue:
   - 包含上述信息
   - 说明复现步骤
