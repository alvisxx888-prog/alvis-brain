#!/usr/bin/env python3
import os
import subprocess
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ALLOWED_USER_ID = 193060672
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CLAUDE_PATH = "/root/.local/bin/claude"

SYSTEM_PROMPT = """你係 Alvis 嘅私人 AI 商業策略顧問，部署喺 VPS，24/7 隨時可用。

關於 Alvis：
- 香港美容及痛症管理銷售從業者，同時兼任 V Sing 嘅 marketing
- 對話稱呼：Alvis
- 三條業務線：
  - 痛症管理 → 品牌名 Alvis（唔係 Stanley）
  - 美容護膚 → 品牌名 Stanley（唔係 Alvis）
  - V Sing → KTV/酒吧娛樂場所，目標 20-70 歲，娛樂/社交向
- 目標客群：18-65 歲，有美容改善或痛症舒緩需求
- WhatsApp: 85260901523

對話風格：
- 隨和，不拘謹，像戰友/Partner 傾偈
- 廣東話或中英夾雜，跟 Alvis 習慣走
- 唔只係助手，係商業策略顧問，主動提供洞見

挑戰者模式（強制執行）：
- 當 Alvis 分享想法或策略，唔可以只係附和
- 必須適時挑戰，指出邏輯盲點、執行漏洞、市場風險
- 目標：讓 Alvis 知道自己睇漏咗咩

工作原則：
- 建議要落地，不說廢話
- 指出問題時附帶替代方案或下一步行動"""

conversation_history: dict[int, list] = {}
MAX_HISTORY = 16


def call_claude(history: list, user_message: str) -> str:
    history_text = ""
    for msg in history[-MAX_HISTORY:]:
        role = "Alvis" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n\n"

    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"---\n\n"
        f"{history_text}"
        f"Alvis: {user_message}"
    )

    result = subprocess.run(
        [CLAUDE_PATH, "-p", full_prompt],
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "HOME": "/root"},
    )

    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    else:
        logger.error(f"Claude error: {result.stderr}")
        return f"出錯了：{result.stderr[:200]}"


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    conversation_history[ALLOWED_USER_ID] = []
    await update.message.reply_text("Alvis，我喺度。有咩搞？")


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    conversation_history[ALLOWED_USER_ID] = []
    await update.message.reply_text("記憶清除，重新開始。")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    history = conversation_history.get(ALLOWED_USER_ID, [])
    await update.message.reply_text(f"目前對話記憶：{len(history)} 條消息")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return

    user_message = update.message.text
    if not user_message:
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    history = conversation_history.setdefault(ALLOWED_USER_ID, [])

    reply = call_claude(history, user_message)

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})

    for i in range(0, len(reply), 4096):
        await update.message.reply_text(reply[i : i + 4096])


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot 啟動，等待消息...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
