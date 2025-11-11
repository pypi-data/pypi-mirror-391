# 配置方式更改说明

## 更改内容

从 `.env` 文件配置 改为 **Claude Desktop MCP 配置**中的环境变量配置。

## 为什么要改？

✅ **用户友好**: 所有配置集中在 Claude Desktop 配置文件中
✅ **易于修改**: 用户只需修改一个配置文件
✅ **多实例支持**: 可以轻松配置多个星球
✅ **配置隔离**: 不需要修改项目代码或 .env 文件

## 改动对比

### 之前的方式 ❌

**步骤 1**: 创建 `.env` 文件
```bash
cd /path/to/zsxq-mcp
cp .env.example .env
nano .env  # 编辑配置
```

**步骤 2**: 配置 Claude Desktop
```json
{
  "mcpServers": {
    "zsxq": {
      "command": "python3",
      "args": ["-m", "zsxq_mcp.server"],
      "cwd": "/path/to/zsxq-mcp"
    }
  }
}
```

❌ 问题：需要修改两个地方

### 现在的方式 ✅

**只需一步**: 在 Claude Desktop 配置中完成所有配置

```json
{
  "mcpServers": {
    "zsxq": {
      "command": "python3",
      "args": ["-m", "zsxq_mcp.server"],
      "cwd": "/path/to/zsxq-mcp",
      "env": {
        "ZSXQ_COOKIE": "your_cookie_here",
        "ZSXQ_GROUP_ID": "your_group_id"
      }
    }
  }
}
```

✅ 优势：只需修改一个配置文件

## 代码改动

### config.py

**之前**:
```python
from dotenv import load_dotenv
load_dotenv()  # 从 .env 文件加载

class Config:
    def __init__(self):
        self.cookie = os.getenv("ZSXQ_COOKIE", "")
```

**现在**:
```python
# 不需要 dotenv，直接从环境变量读取
class Config:
    def __init__(self):
        self.cookie = os.getenv("ZSXQ_COOKIE", "")
```

### 依赖移除

不再需要 `python-dotenv` 依赖（但保留了兼容性）

## 测试结果

✅ 环境变量配置测试通过
✅ 成功发布测试笔记（Topic ID: 14588282558124212）
✅ Cookie 和 GROUP_ID 正确读取
✅ 所有功能正常工作

## 迁移指南

如果你之前使用 `.env` 文件配置：

### 方法 1: 直接迁移到 MCP 配置（推荐）

1. 打开你的 `.env` 文件
2. 复制 `ZSXQ_COOKIE` 和 `ZSXQ_GROUP_ID` 的值
3. 粘贴到 Claude Desktop 配置文件的 `env` 字段
4. 删除或保留 `.env` 文件（不再使用）

### 方法 2: 继续使用 .env 文件

你也可以继续使用 `.env` 文件，代码仍然兼容：

1. 保留你的 `.env` 文件
2. 在 Claude Desktop 配置中不设置 `env` 字段
3. 代码会自动从 `.env` 文件读取（如果安装了 python-dotenv）

**注意**: 如果同时设置了环境变量和 .env 文件，环境变量优先。

## 新增文件

- ✅ `CONFIGURATION.md` - 详细的配置指南
- ✅ `claude_desktop_config.example.json` - 完整的配置示例
- ✅ `CHANGES.md` - 本文件，说明配置方式的改动

## 文档更新

- ✅ `README.md` - 更新配置说明，添加配置指南链接
- ✅ `QUICKSTART.md` - 更新快速开始指南
- ✅ `TEST_RESULTS.md` - 保持不变，记录测试结果

## 向后兼容

✅ 仍然支持 `.env` 文件配置
✅ 环境变量优先级更高
✅ 不影响现有用户

## 建议

🎯 **新用户**: 直接使用 Claude Desktop MCP 配置
🔄 **老用户**: 可选择迁移或继续使用 .env 文件
📝 **多星球管理**: 使用 MCP 配置更方便
