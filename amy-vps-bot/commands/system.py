from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.config import settings
from app.security import private_only
from services.system import restart_service, service_logs


@private_only
async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    service = context.args[0] if context.args else settings.bot_service_name
    await update.message.reply_text(service_logs(service))


@private_only
async def restart_hermes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(restart_service(settings.hermes_service_name))
