# NapCat (QQ OneBot 11) 原生适配器

Hermes 的 NapCat 适配器通过 OneBot 11 接收 NapCat 的反向 WebSocket，并通过 NapCat HTTP API 发消息。

## 当前实现

- 私聊文字消息
- 群聊文字消息（默认要求 @小号）
- 文字消息发送与超长分片
- Markdown 转普通 QQ 文本
- 基础图片、语音、视频、文件发送接口
- 会话按 QQ 用户/群隔离

## 配置

在 Hermes 配置中加入：

```yaml
platforms:
  napcat:
    enabled: true
    extra:
      http_api: "http://127.0.0.1:18801"
      access_token: ""
      self_id: "你的QQ小号"
      ws_port: 18800
      dm_policy: "allowlist"
      allow_from: ["你的QQ号"]
      group_policy: "open"
      group_allow_from: []
```

正式配置请使用：

```bash
hermes config set platforms.napcat.enabled true
hermes config set platforms.napcat.extra.http_api http://127.0.0.1:18801
hermes config set platforms.napcat.extra.self_id 你的QQ小号
hermes config set platforms.napcat.extra.ws_port 18800
hermes config set platforms.napcat.extra.dm_policy allowlist
hermes config set platforms.napcat.extra.group_policy open
```

## NapCat 端

将 OneBot 11 配置为：

- HTTP API：`127.0.0.1:18801`
- 反向 WebSocket：`ws://127.0.0.1:18800`
- 消息格式：`array`
- Token 与 Hermes 配置保持一致（如果启用）

启动顺序：

1. 启动 Hermes Gateway，使其监听 `18800`；
2. 启动 NapCat；
3. 使用 QQ 扫码登录小号；
4. 在群里 @小号发送测试消息。

## 安全建议

只在本机监听 OneBot 端口，不要把 `18800` 或 `18801` 暴露到公网。使用专门的小号，并把 `allow_from` 和管理员权限限制为可信账号。NapCat 使用个人 QQ 登录，可能存在账号风控和封禁风险。
