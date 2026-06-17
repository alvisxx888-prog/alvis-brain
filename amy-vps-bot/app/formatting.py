from __future__ import annotations

from telegram import Update


TELEGRAM_LIMIT = 4096


async def send_long(update: Update, text: str) -> None:
    if not update.message:
        return
    for i in range(0, len(text), TELEGRAM_LIMIT):
        await update.message.reply_text(text[i : i + TELEGRAM_LIMIT])
