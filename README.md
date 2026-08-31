# Hermes Native NapCat

一个轻量的 [NapCatQQ](https://github.com/NapNeko/NapCatQQ) → OneBot 11 → [Hermes Agent](https://github.com/NousResearch/hermes-agent) 适配器。

本仓库**不包含完整 Hermes 源码**，只包含适配器、安装器、文档和测试。

## 快速开始

前提：已经安装 Hermes Agent 和 NapCatQQ。

```bash
git clone https://github.com/mino118/hermes-napcat-native.git
cd hermes-napcat-native
python install.py --hermes-dir C:/Users/<用户名>/AppData/Local/hermes/hermes-agent
```

安装器会：

- 检查 Hermes 源码目录；
- 复制 NapCat 适配器；
- 给 Hermes 添加 `napcat` 平台；
- 给现有文件创建 `.napcat-backup` 备份；
- 不上传、不保存 QQ 登录凭据。

然后配置 Hermes：

```bash
hermes config set platforms.napcat.enabled true
hermes config set platforms.napcat.extra.http_api http://127.0.0.1:18801
hermes config set platforms.napcat.extra.ws_port 18800
hermes config set platforms.napcat.extra.self_id <QQ小号>
hermes config set platforms.napcat.extra.access_token <OneBot_TOKEN>
hermes config set platforms.napcat.extra.dm_policy allowlist
hermes config set platforms.napcat.extra.allow_from '["<你的QQ号>"]'
hermes config set platforms.napcat.extra.group_policy allowlist
hermes config set platforms.napcat.extra.group_allow_from '["<QQ群号>"]'
hermes gateway restart
```

## NapCat 配置

NapCat WebUI 中创建并启用：

### HTTP Server

```text
Host: 127.0.0.1
Port: 18801
Message format: Array
Token: 与 Hermes 配置一致
```

### WebSocket Client

```text
URL: ws://127.0.0.1:18800
Message format: Array
Token: 与 Hermes 配置一致
Report self message: off
```

启动 NapCat 后，用手机 QQ 扫码登录专用小号。

## 使用方式

私聊：给 QQ 小号发送消息。

群聊：在允许的群中真正 @QQ 小号，例如：

```text
@小号 你好
```

群聊默认只处理 @小号的消息。

## 一键下载 NapCat（Windows）

如果还没有 NapCat，可以使用仓库提供的辅助脚本：

```bash
python scripts/setup_napcat.py
```

它会自动检测 QQ、下载官方 NapCat Shell、生成本地 Token、写入 Hermes 配置并启动服务。首次使用仍需扫码，并在 NapCat WebUI 中确认网络配置。

## 安全说明

- NapCat 使用个人 QQ 账号，不是官方 QQ Bot API；
- 请使用专用小号，不要使用主账号；
- 可能存在风控、限制登录或封号风险；
- 不要把 QQ 密码、Token、二维码或 `.env` 提交到 Git；
- 只监听 `127.0.0.1`，不要把 OneBot 端口暴露到公网。

## 卸载

安装器会为修改过的 Hermes 文件创建备份。卸载时可以根据备份恢复：

```text
gateway/config.py.napcat-backup
gateway/run.py.napcat-backup
gateway/authz_mixin.py.napcat-backup
```

同时删除：

```text
gateway/platforms/napcat_adapter.py
gateway/platforms/napcat_api.py
```

## 测试

```bash
python -m pytest tests -q -o addopts=''
python -m compileall -q install.py napcat scripts
```

## 相关项目

- Hermes Agent：https://github.com/NousResearch/hermes-agent
- NapCatQQ：https://github.com/NapNeko/NapCatQQ
- OneBot 11：https://github.com/botuniverse/onebot-11
