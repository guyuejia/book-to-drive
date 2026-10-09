
import os
import asyncio
import logging
import tempfile
from pathlib import Path

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))
DRIVE = "gdrive:ZLibrary"
MAX_SIZE = 20 * 1024 * 1024
SUPPORTED = {".epub", ".pdf", ".mobi", ".azw3"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("book-to-drive")


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    await update.message.reply_text(
        f"你的 Telegram User ID：{update.effective_user.id}"
    )


async def receive_book(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    msg = update.message
    user = update.effective_user

    if not msg or not user:
        return

    # 只处理指定用户发送的私聊消息
    if update.effective_chat.type != "private" or user.id != USER_ID:
        return

    doc = msg.document
    if not doc:
        return

    # 防止文件名包含目录路径
    filename = (doc.file_name or "unknown").replace("\\", "/")
    filename = filename.split("/")[-1].replace("\x00", "")
    filename = filename[:180]

    if Path(filename).suffix.lower() not in SUPPORTED:
        await msg.reply_text("不支持此格式，仅接收电子书文件。")
        return

    if doc.file_size is not None and doc.file_size > MAX_SIZE:
        await msg.reply_text(
            "文件超过 20 MB，当前版本暂不支持。"
        )
        return

    await msg.reply_text(f"📥 开始转存：{filename}")

    # 文件名前增加 Telegram 消息 ID，避免同名覆盖
    remote_filename = f"{msg.message_id}_{filename}"
    remote_path = f"{DRIVE}/{remote_filename}"

    try:
        with tempfile.TemporaryDirectory() as tmp:
            local_path = Path(tmp) / filename

            # 从 Telegram 下载附件
            tgfile = await doc.get_file(
                read_timeout=60,
                connect_timeout=30,
            )
            await tgfile.download_to_drive(
                custom_path=local_path,
                read_timeout=180,
                connect_timeout=30,
            )

            # 直接使用现有 Google Drive Remote
            proc = await asyncio.create_subprocess_exec(
                "rclone",
                "copyto",
                str(local_path),
                remote_path,
                "--retries", "3",
                "--stats", "0",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            _, stderr = await proc.communicate()

            if proc.returncode != 0:
                log.error(
                    "rclone upload failed: %s",
                    stderr.decode(errors="replace")[-2000:],
                )
                raise RuntimeError("rclone upload failed")

        await msg.reply_text(
            f"✅ 上传完成\n"
            f"文件：{filename}\n"
            f"位置：Google Drive / ZLibrary"
        )

    except Exception:
        log.exception("Book transfer failed")
        await msg.reply_text(
            f"❌ 转存失败：{filename}\n"
            "请检查服务日志，或稍后重新转发。"
        )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(
        MessageHandler(filters.Document.ALL, receive_book)
    )

    log.info("BookToDrive started")
    app.run_polling(drop_pending_updates=False)


if __name__ == "__main__":
    main()

