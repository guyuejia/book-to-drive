# BookToDrive

A lightweight Telegram bot that transfers ebooks to Google Drive.

轻量级 Telegram 电子书自动归档工具。

## 功能

- 将 Telegram 收到的电子书手动转发给自己的 Bot
- 自动下载 EPUB、PDF、MOBI、AZW3 文件
- 使用 rclone 上传到 Google Drive
- 上传成功或失败后通过 Telegram 发送通知
- Telegram 用户 ID 白名单
- Docker Compose 部署
- 临时文件自动清理

## 架构

Telegram → BookToDrive Bot → rclone → Google Drive

使用 Telegram Bot API 长轮询，不需要公网端口或 Webhook。

## 环境要求

- Linux
- Docker / Docker Compose
- Telegram Bot Token
- 已配置的 rclone Google Drive Remote

## 部署

1. 克隆项目：

   git clone https://github.com/guyuejia/book-to-drive.git

2. 进入目录并创建环境变量：

   cd book-to-drive
   cp .env.example .env

3. 编辑 `.env`，设置 Bot Token 和 Telegram User ID。

4. 根据实际服务器环境，检查 `docker-compose.yml`
   中的 rclone 配置目录挂载。

5. 验证 Google Drive：

   docker compose run --rm book-to-drive rclone lsd gdrive:

6. 启动服务：

   docker compose up -d --build

7. 查看日志：

   docker compose logs -f

## 使用方法

1. 打开 Telegram。
2. 将 EPUB/PDF 等图书附件转发到自己的 BookToDrive Bot。
3. Bot 自动下载并上传 Google Drive。
4. 收到上传结果通知。

## 当前限制

- 官方云端 Telegram Bot API 文件下载上限为 20 MB。
- 不支持文件内容去重。
- 不支持持久化任务队列。
- 上传文件名前增加 Telegram 消息 ID，避免同名冲突。

## 安全

不要提交 `.env`、Telegram Bot Token、rclone OAuth 凭据或
Telegram Session 文件。

## License

暂未指定开源许可证。
