# 使用 UVX 快速启动 ZSXQ MCP 服务器

## 什么是 UVX？

`uvx` 是一个强大的 Python 工具，可以临时运行 Python 应用而无需预先安装依赖。它会：

1. 自动创建临时环境
2. 安装所需依赖
3. 运行应用程序
4. 运行结束后清理临时环境

## 快速启动

### 方法一：使用启动脚本（推荐）

```bash
# 进入项目目录
cd zsxq-mcp

# 运行启动脚本
./start_with_uvx.sh
```

### 方法二：直接使用 uvx 命令

```bash
# 进入项目目录
cd zsxq-mcp

# 使用 uvx 直接运行
uvx --from . python -m zsxq_mcp.server
```

### 方法三：如果从 Git 仓库运行

```bash
# 直接从 Git 仓库运行（无需克隆）
uvx --from git+https://github.com/your-username/zsxq-mcp.git python -m zsxq_mcp.server
```

## 配置要求

使用 `uvx` 启动前，请确保：

1. **环境变量配置**：编辑 `.env` 文件
   ```bash
   # 复制模板文件
   cp .env.example .env

   # 编辑配置文件
   nano .env
   ```

2. **必要的配置项**：
   ```env
   ZSXQ_COOKIE=your_complete_cookie_value_here
   ZSXQ_GROUP_ID=your_group_id_here
   ```

## Claude Desktop 配置

在 Claude Desktop 配置中使用 `uvx`：

```json
{
  "mcpServers": {
    "zsxq": {
      "command": "uvx",
      "args": [
        "--from",
        "/path/to/your/zsxq-mcp",
        "python",
        "-m",
        "zsxq_mcp.server"
      ],
      "env": {
        "ZSXQ_COOKIE": "your_cookie_value_here",
        "ZSXQ_GROUP_ID": "your_group_id_here"
      }
    }
  }
}
```

**注意**：将 `/path/to/your/zsxq-mcp` 替换为项目的实际路径。

## 优势

- **无需预先安装**：不需要 `pip install -e .`
- **隔离环境**：每次运行都是干净的环境
- **自动依赖管理**：自动安装所需依赖
- **版本隔离**：不同项目使用不同依赖版本不会冲突
- **便携性**：可以在任何有 `uvx` 的机器上运行

## 故障排除

### 1. uvx 未安装

```bash
# 安装 uv（包含 uvx）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip
pip install uv
```

### 2. 权限问题

```bash
# 确保启动脚本有执行权限
chmod +x start_with_uvx.sh
```

### 3. 环境变量问题

确保 `.env` 文件在项目根目录，并且包含正确的配置值。

### 4. 网络问题

如果依赖下载缓慢，可以配置镜像源：

```bash
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/
uvx --from . python -m zsxq_mcp.server
```

## 高级用法

### 指定 Python 版本

```bash
uvx --python 3.11 --from . python -m zsxq_mcp.server
```

### 开发模式运行

```bash
# 包含开发依赖
uvx --from . --with pytest python -m zsxq_mcp.server
```

### 调试模式

```bash
# 启用详细输出
uvx --verbose --from . python -m zsxq_mcp.server
```