# ZSXQ MCP Server - 在线包安装指南

## 📦 在线包安装方式

用户现在可以通过多种方式安装和使用 ZSXQ MCP Server！

### 方法一：使用 pip 安装（推荐）

```bash
# 从 PyPI 安装
pip install zsxq-mcp

# 或者安装最新版本
pip install --upgrade zsxq-mcp
```

### 方法二：使用 uvx（临时运行）

```bash
# 临时运行，无需安装
uvx zsxq-mcp

# 或者从 git 仓库运行
uvx --from git+https://github.com/yourusername/zsxq-mcp.git zsxq-mcp
```

### 方法三：从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/zsxq-mcp.git
cd zsxq-mcp

# 安装依赖
pip install -e .
```

## 🚀 快速开始

### 1. 配置环境变量

```bash
# 创建配置文件
cat > ~/.zsxq-mcp.env << EOF
ZSXQ_COOKIE=your_complete_cookie_value_here
ZSXQ_GROUP_ID=your_group_id_here
EOF
```

### 2. Claude Desktop 配置

**使用 pip 安装的版本**：
```json
{
  "mcpServers": {
    "zsxq": {
      "command": "zsxq-mcp",
      "env": {
        "ZSXQ_COOKIE": "your_cookie_value_here",
        "ZSXQ_GROUP_ID": "your_group_id_here"
      }
    }
  }
}
```

**使用 uvx**：
```json
{
  "mcpServers": {
    "zsxq": {
      "command": "uvx",
      "args": ["zsxq-mcp"],
      "env": {
        "ZSXQ_COOKIE": "your_cookie_value_here",
        "ZSXQ_GROUP_ID": "your_group_id_here"
      }
    }
  }
}
```

### 3. 验证安装

```bash
# 检查命令是否可用
zsxq-mcp --help

# 或者使用 python 模块
python -m zsxq_mcp --help
```

## 📋 系统要求

- **Python**: 3.10 或更高版本
- **操作系统**: Windows, macOS, Linux
- **依赖**: 会自动安装以下依赖：
  - `fastmcp>=0.2.0`
  - `httpx>=0.27.0`
  - `python-dotenv>=1.0.0`

## 🔧 开发安装

如果你想参与开发或修改代码：

```bash
# 克隆仓库
git clone https://github.com/yourusername/zsxq-mcp.git
cd zsxq-mcp

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 以开发模式安装
pip install -e ".[dev]"

# 运行测试
pytest

# 构建包
python -m build
```

## 🆙 版本更新

```bash
# 检查当前版本
pip show zsxq-mcp

# 更新到最新版本
pip install --upgrade zsxq-mcp

# 安装特定版本
pip install zsxq-mcp==0.1.0
```

## 🐛 故障排除

### 问题 1: 命令未找到

```bash
# 确保 Python scripts 目录在 PATH 中
# Windows
echo %PATH%
# macOS/Linux
echo $PATH

# 重新安装
pip uninstall zsxq-mcp
pip install zsxq-mcp
```

### 问题 2: 权限错误

```bash
# 使用用户安装
pip install --user zsxq-mcp

# 或者使用虚拟环境
python -m venv zsxq-env
source zsxq-env/bin/activate
pip install zsxq-mcp
```

### 问题 3: 依赖冲突

```bash
# 使用 uvx 避免依赖冲突
uvx zsxq-mcp

# 或者创建干净的环境
python -m venv fresh-env
source fresh-env/bin/activate
pip install zsxq-mcp
```

### 问题 4: 网络问题

```bash
# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ zsxq-mcp

# 或者配置永久镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 📚 更多资源

- **GitHub 仓库**: https://github.com/yourusername/zsxq-mcp
- **PyPI 页面**: https://pypi.org/project/zsxq-mcp/
- **文档**: https://github.com/yourusername/zsxq-mcp#readme
- **问题反馈**: https://github.com/yourusername/zsxq-mcp/issues

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](https://github.com/yourusername/zsxq-mcp/blob/main/CONTRIBUTING.md) 了解详细信息。

## 📄 许可证

本项目使用 MIT 许可证。详见 [LICENSE](https://github.com/yourusername/zsxq-mcp/blob/main/LICENSE) 文件。