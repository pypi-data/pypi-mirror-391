# ZSXQ MCP 配置指南

## 配置方式

ZSXQ MCP 使用**环境变量**进行配置，所有配置都在 Claude Desktop 的配置文件中完成，用户无需修改项目代码或 .env 文件。

## 快速配置步骤

### 1. 获取知识星球 Cookie

1. 打开浏览器，访问 https://wx.zsxq.com/
2. 登录你的知识星球账号
3. 按 `F12` 打开开发者工具
4. 切换到 **Network（网络）** 标签
5. 刷新页面（`F5` 或 `Cmd+R`）
6. 在请求列表中点击任意一个请求
7. 在右侧找到 **Request Headers（请求头）**
8. 找到 `Cookie:` 字段
9. 复制**完整的** Cookie 值（很长的一串文本）

**示例**：
```
sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221484124882%22...很长...zsxq_access_token=E39D01A9-58C6-4CA9-9609-B8B9CE5B4BFE_F6607C65B55BCDA2
```

### 2. 获取星球 ID

1. 在浏览器中访问你想要发布的知识星球
2. 查看浏览器地址栏的 URL
3. 提取 `/group/` 后面的数字

**示例**：
```
https://wx.zsxq.com/group/28888188458521
                          ^^^^^^^^^^^^^^
                          这就是星球 ID
```

### 3. 配置 Claude Desktop

找到 Claude Desktop 配置文件：

- **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

编辑配置文件，添加以下内容：

```json
{
  "mcpServers": {
    "zsxq": {
      "command": "python3",
      "args": ["-m", "zsxq_mcp.server"],
      "cwd": "/Users/chenxingyu/Desktop/zsxq-mcp",
      "env": {
        "ZSXQ_COOKIE": "这里粘贴你复制的完整Cookie值",
        "ZSXQ_GROUP_ID": "这里填入你的星球ID"
      }
    }
  }
}
```

### 4. 修改配置路径

将 `cwd` 改为你的实际项目路径：

**MacOS/Linux**:
```json
"cwd": "/Users/你的用户名/Desktop/zsxq-mcp"
```

**Windows**:
```json
"cwd": "C:\\Users\\你的用户名\\Desktop\\zsxq-mcp"
```

### 5. 重启 Claude Desktop

完全退出 Claude Desktop，然后重新打开。

## 完整配置示例

```json
{
  "mcpServers": {
    "zsxq": {
      "command": "python3",
      "args": ["-m", "zsxq_mcp.server"],
      "cwd": "/Users/chenxingyu/Desktop/zsxq-mcp",
      "env": {
        "ZSXQ_COOKIE": "sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221484124882%22%2C%22first_id%22%3A%22191446dd0172f8-0e43ea5e40c148-18525637-1296000-191446dd018fa0%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkxNDQ2ZGQwMTcyZjgtMGU0M2VhNWU0MGMxNDgtMTg1MjU2MzctMTI5NjAwMC0xOTE0NDZkZDAxOGZhMCIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjE0ODQxMjQ4ODIifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221484124882%22%7D%2C%22%24device_id%22%3A%221930fe19180298-0adf0f85836804-1f525636-1296000-1930fe191814c1%22%7D; abtest_env=product; zsxq_access_token=E39D01A9-58C6-4CA9-9609-B8B9CE5B4BFE_F6607C65B55BCDA2",
        "ZSXQ_GROUP_ID": "28888188458521"
      }
    }
  }
}
```

## 配置字段说明

| 字段 | 说明 | 必填 |
|------|------|------|
| `command` | Python 命令，使用 `python3` | ✅ 必填 |
| `args` | 启动参数，固定为 `["-m", "zsxq_mcp.server"]` | ✅ 必填 |
| `cwd` | 项目路径，改为你的实际路径 | ✅ 必填 |
| `env.ZSXQ_COOKIE` | 知识星球 Cookie | ✅ 必填 |
| `env.ZSXQ_GROUP_ID` | 默认星球 ID | ⚠️ 可选* |

\* 如果不配置 `ZSXQ_GROUP_ID`，每次发布时需要手动指定 `group_id` 参数

## 验证配置

重启 Claude Desktop 后，在对话中输入：

```
帮我查看一下知识星球信息
```

如果配置正确，会返回你的星球信息。

## 修改配置

### 更换 Cookie（Cookie 过期时）

1. 打开 Claude Desktop 配置文件
2. 找到 `ZSXQ_COOKIE` 字段
3. 替换为新的 Cookie 值
4. 保存文件
5. 重启 Claude Desktop

### 更换星球 ID

1. 打开 Claude Desktop 配置文件
2. 找到 `ZSXQ_GROUP_ID` 字段
3. 替换为新的星球 ID
4. 保存文件
5. 重启 Claude Desktop

### 同时管理多个星球

你可以配置多个 MCP 服务器实例：

```json
{
  "mcpServers": {
    "zsxq-star1": {
      "command": "python3",
      "args": ["-m", "zsxq_mcp.server"],
      "cwd": "/path/to/zsxq-mcp",
      "env": {
        "ZSXQ_COOKIE": "cookie_value_1",
        "ZSXQ_GROUP_ID": "star_id_1"
      }
    },
    "zsxq-star2": {
      "command": "python3",
      "args": ["-m", "zsxq_mcp.server"],
      "cwd": "/path/to/zsxq-mcp",
      "env": {
        "ZSXQ_COOKIE": "cookie_value_2",
        "ZSXQ_GROUP_ID": "star_id_2"
      }
    }
  }
}
```

## 常见问题

### Q: Cookie 在哪里找？
A: 浏览器开发者工具 → Network 标签 → 任意请求 → Request Headers → Cookie

### Q: Cookie 会过期吗？
A: 会的。如果遇到 401 错误，说明 Cookie 过期了，需要重新获取。

### Q: 可以不配置 GROUP_ID 吗？
A: 可以。但每次发布时需要指定 `group_id` 参数。

### Q: 如何验证配置是否正确？
A: 在 Claude 中说"查看知识星球信息"，如果返回星球信息说明配置成功。

### Q: Windows 路径怎么写？
A: 使用双反斜杠：`"cwd": "C:\\Users\\username\\Desktop\\zsxq-mcp"`

### Q: 配置修改后需要重启吗？
A: 是的，必须完全退出并重启 Claude Desktop。

## 安全提示

⚠️ **重要提醒**：

1. **不要分享 Cookie**：Cookie 包含你的登录凭证，泄露后他人可以控制你的账号
2. **定期更新**：Cookie 会过期，建议定期更新
3. **配置文件安全**：Claude Desktop 配置文件权限已受保护，但仍需注意不要分享
4. **多设备使用**：如果在多台设备登录，Cookie 可能会失效

## 技术原理

配置通过以下方式传递：

1. Claude Desktop 读取配置文件
2. 将 `env` 中的环境变量传递给 MCP 服务器进程
3. Python 代码通过 `os.getenv()` 读取环境变量
4. 无需 `.env` 文件，配置集中在一处

这样的好处：
- ✅ 配置集中管理
- ✅ 用户友好，只需修改一个文件
- ✅ 支持多实例配置
- ✅ 配置隔离，不影响代码
