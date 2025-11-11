# ZSXQ MCP Server

知识星球 MCP 服务器 - 通过 Model Context Protocol 发布内容到知识星球。

## 功能特性

- ✅ 发布文字主题到知识星球
- ✅ 上传并发布带图片的内容
- ✅ 从本地文件读取内容发布
- ✅ Cookie 身份验证
- ✅ 灵活的配置方式

## 安装

### 方法一：pip 安装（推荐）

```bash
pip install zsxq-mcp
```

### 方法二：uvx 快速启动

```bash
uvx zsxq-mcp
```

### 方法三：从源码安装

```bash
pip install -e .
```

## 配置

### 1. 获取知识星球 Cookie

1. 浏览器登录知识星球（https://wx.zsxq.com/）
2. 打开开发者工具（F12）
3. Network 标签页中找到 API 请求的 `Cookie` 字段
4. 复制完整 Cookie 值

### 2. 获取星球 ID

访问星球页面，URL 中的数字部分即为星球 ID：
`https://wx.zsxq.com/group/12345678901234` → `12345678901234`

### 3. 配置 Claude Desktop

在配置文件中添加：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

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

重启 Claude Desktop 即可使用。

## 使用方法

### 发布文字主题

```
帮我发布到知识星球："今天学习了 MCP 的使用方法，非常有趣！"
```

### 发布文件内容

```
把这个文件发布到知识星球：/Users/xxx/article.txt
```

### 发布带图片内容

```
发布带图片的动态："分享今天的成果"，图片：/Users/xxx/screenshot.png
```

## 可用工具

- `publish_topic` - 发布文字主题
- `publish_topic_from_file` - 从文件发布内容
- `publish_topic_with_images` - 发布带图片的主题
- `upload_image` - 上传图片
- `get_group_info` - 获取星球信息

## 安全提醒

- ⚠️ 请勿分享你的 Cookie，它包含登录凭证
- 🔒 Cookie 会定期过期，需要重新获取
- 📖 详细配置说明请查看 [CONFIGURATION.md](./CONFIGURATION.md)

## 许可证

MIT License