from __future__ import annotations

from functools import wraps
from typing import Awaitable, Callable, TypeVar

from telegram import Update
from telegram.ext import ContextTypes

from app.config import settings


Handler = TypeVar("Handler", bound=Callable[..., Awaitable[None]])


def user_allowed(update: Update) -> bool:
    user = update.effective_user
    return bool(user and user.id in settings.allowed_user_ids)


def private_only(fn: Handler) -> Handler:
    @wraps(fn)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not user_allowed(update):
            if update.message:
                await update.message.reply_text("呢個 bot 係私人助手，未授權。請檢查 ALLOWED_TELEGRAM_USER_IDS。")
            return
        return await fn(update, context)

    return wrapper  # type: ignore[return-value]
