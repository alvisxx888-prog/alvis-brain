from __future__ import annotations

import asyncio
import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app.config_v2 import settings_v2
from app.formatting import send_long
from services.providers_v2 import analyze_image, answer_text, status_text, test_ai


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("amy-v2")


def _allowed(update: Update) -> bool:
    user = update.effective_user
    return bool(user and user.id in settings_v2.allowed_user_ids)


async def _guard(update: Update) -> bool:
    if _allowed(update):
        return True
    if update.message:
        await update.message.reply_text("呢個 bot 係私人助手，未授權。")
    return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update) or not update.message:
        return
    await update.message.reply_text(
        f"{settings_v2.bot_name} 已啟動。\n\n"
        "可用：\n"
        "/status_ai - 睇 provider 狀態\n"
        "/test_ai - 測試 AI 連線\n"
        "直接打文字 - 問答\n"
        "直接傳圖片 - Vision 分析"
    )


async def status_ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update) or not update.message:
        return
    await update.message.reply_text(status_text())


async def test_ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update) or not update.message:
        return
    await update.message.reply_text("測試 AI provider 中...")
    try:
        result = await asyncio.to_thread(test_ai)
    except Exception as exc:
        await update.message.reply_text(f"AI test 失敗：{exc}")
        return
    await send_long(update, result)


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update) or not update.message or not update.message.text:
        return
    await update.message.reply_text("收到，處理中...")
    try:
        result = await asyncio.to_thread(answer_text, update.message.text.strip())
    except Exception as exc:
        await update.message.reply_text(f"處理失敗：{exc}")
        return
    await send_long(update, result)


async def photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update) or not update.message or not update.message.photo:
        return
    await update.message.reply_text("收到圖片，Vision 分析中...")
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    data = await file.download_as_bytearray()
    try:
        result = await asyncio.to_thread(analyze_image, bytes(data), "image/jpeg", update.message.caption or "")
    except Exception as exc:
        await update.message.reply_text(f"圖片分析失敗：{exc}")
        return
    await send_long(update, result)


def build_app() -> Application:
    errors = settings_v2.startup_errors()
    if errors:
        raise RuntimeError("Amy V2 config error: " + " ".join(errors))

    app = Application.builder().token(settings_v2.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status_ai", status_ai))
    app.add_handler(CommandHandler("test_ai", test_ai_command))
    app.add_handler(MessageHandler(filters.PHOTO, photo_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))
    return app


def main() -> None:
    logger.info("Starting %s", settings_v2.bot_name)
    build_app().run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
