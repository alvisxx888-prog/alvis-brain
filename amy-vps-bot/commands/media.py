from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.formatting import send_long
from app.security import private_only
from services.ai import describe_image, transcribe_audio
from services.state import set_last_content


@private_only
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.photo:
        return
    await update.message.reply_text("收到圖片，Jasmine 分析中...")
    photo_obj = update.message.photo[-1]
    file = await context.bot.get_file(photo_obj.file_id)
    data = await file.download_as_bytearray()
    result = describe_image(bytes(data), "image/jpeg", update.message.caption or "")
    set_last_content(context, result)
    await send_long(update, f"圖片分析：\n\n{result}")


@private_only
async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    voice_obj = update.message.voice or update.message.audio if update.message else None
    if not voice_obj:
        return
    await update.message.reply_text("收到語音，轉錄中...")
    file = await context.bot.get_file(voice_obj.file_id)
    data = await file.download_as_bytearray()
    result = transcribe_audio(bytes(data), "voice.ogg")
    set_last_content(context, result)
    await send_long(update, f"語音轉錄：\n\n{result}\n\n你可以打 /team、/pdf、/slides 或 /analyze_file 繼續。")
