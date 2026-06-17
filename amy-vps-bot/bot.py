from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import BotCommand, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from app.config import settings
from commands import assistant, basic, content, files, intel, media, research, system, team
from services.ai import ask_agent, local_transcription_available
from services.state import bootstrap_bot_data
from services.system import service_logs, system_status


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("amy-vps-bot")
BOT_BUILD = "2026-06-17-ig-public-instaloader-v1"


async def callback_router(update: Update, context) -> None:
    query = update.callback_query
    if not query or not update.effective_user or update.effective_user.id not in settings.allowed_user_ids:
        return
    await query.answer()
    if query.data == "status":
        await query.message.reply_text(system_status())
    elif query.data == "logs":
        await query.message.reply_text(service_logs(settings.bot_service_name))
    elif query.data == "help_caption":
        await query.message.reply_text("/caption [描述]\n例：/caption 痛症初診優惠，免費諮詢")
    elif query.data == "help_pdf":
        await query.message.reply_text("先貼內容或上載文件，再打 /pdf；或者 /pdf [描述]。")

async def daily_briefing(app: Application) -> None:
    if not settings.daily_briefing_enabled:
        return
    import asyncio
    briefing = await asyncio.to_thread(
        ask_agent,
        "Leo",
        "生成今日 Stanley 早晨簡報：美容/痛症市場一個機會、AI工具一個機會、今日最值得做嘅3件事。",
        max_output_tokens=900,
    )
    for user_id in settings.allowed_user_ids:
        await app.bot.send_message(chat_id=user_id, text=f"早晨簡報：\n\n{briefing}")


async def post_init(app: Application) -> None:
    bootstrap_bot_data(app.bot_data)

    await app.bot.set_my_commands(
        [
            BotCommand("start", "開主選單"),
            BotCommand("commands", "睇指令同例句"),
            BotCommand("ask", "自然語言交代任務"),
            BotCommand("pdf", "生成 PDF"),
            BotCommand("slides", "生成 PowerPoint"),
            BotCommand("caption", "寫 IG/小紅書 caption"),
            BotCommand("reel", "寫 Reels 腳本"),
            BotCommand("copy", "寫廣告/WhatsApp 文案"),
            BotCommand("landingpage", "生成 Landing Page HTML"),
            BotCommand("imagine", "生成 AI 圖片 + prompts"),
            BotCommand("image", "生成 AI 圖片 + prompts"),
            BotCommand("scrape", "抓 IG/FB/Threads/網頁"),
            BotCommand("xhs", "抓小紅書帖文"),
            BotCommand("report", "即時市場 + AI 情報"),
            BotCommand("research", "搜尋同分析"),
            BotCommand("staff", "睇員工架構"),
            BotCommand("agent", "指名員工處理"),
            BotCommand("team", "自動揀員工"),
            BotCommand("team_all", "全隊分析"),
            BotCommand("dreamteam", "全隊分析"),
            BotCommand("analyze_file", "分析最近內容/文件"),
            BotCommand("status_ai", "睇 AI provider 狀態"),
            BotCommand("test_ai", "測試 AI 回覆"),
            BotCommand("ping", "測試 bot 有冇收到"),
            BotCommand("version", "睇 bot build 版本"),
        ]
    )

    scheduler = AsyncIOScheduler(timezone="Asia/Hong_Kong")
    scheduler.add_job(
        daily_briefing,
        CronTrigger(hour=settings.daily_briefing_hour, minute=settings.daily_briefing_minute),
        args=[app],
    )
    scheduler.start()


async def ping(update: Update, context) -> None:
    if not update.effective_user or update.effective_user.id not in settings.allowed_user_ids:
        return
    if update.message:
        await update.message.reply_text(
            "✅ Bot 運行正常，收到你嘅訊息。\n"
            f"Build：{BOT_BUILD}"
        )


async def version(update: Update, context) -> None:
    if not update.effective_user or update.effective_user.id not in settings.allowed_user_ids:
        return
    if update.message:
        await update.message.reply_text(
            f"Bot build：{BOT_BUILD}\n"
            "如果你見到呢行，代表 VPS 已經跑緊新版自然語言 interpreter。"
        )


async def error_handler(update: object, context) -> None:
    logger.exception("Unhandled bot error", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "處理時出錯，我已記低 log。\n"
            f"錯誤：{context.error}"
        )


async def status_ai(update: Update, context) -> None:
    if not update.effective_user or update.effective_user.id not in settings.allowed_user_ids:
        if update.message:
            await update.message.reply_text("呢個 bot 係私人助手，未授權。請檢查 ALLOWED_TELEGRAM_USER_IDS。")
        return
    if not update.message:
        return

    text_provider = "OpenAI base" if settings.openai_api_key else ("OpenRouter fallback" if settings.openrouter_api_key else "未設定")
    vision_provider = "OpenAI base" if settings.openai_api_key else ("OpenRouter fallback" if settings.openrouter_api_key else "未設定")
    image_provider = "OpenAI" if settings.openai_api_key else "未設定 OPENAI_API_KEY"
    gamma_provider = "已設定" if settings.gamma_api_key else "未設定"
    apify_provider = "已設定" if settings.apify_api_token else "未設定 APIFY_API_TOKEN"
    briefing_time = f"{settings.daily_briefing_hour:02d}:{settings.daily_briefing_minute:02d}"
    briefing_provider = f"{briefing_time} 已啟用" if settings.daily_briefing_enabled else f"{briefing_time} 未啟用"
    if settings.openai_api_key:
        voice_provider = "OpenAI Whisper API"
        voice_ok = "✅"
    elif local_transcription_available():
        voice_provider = f"本機 Whisper 免費（{settings.local_whisper_model}）"
        voice_ok = "✅"
    else:
        voice_provider = "未設定 OPENAI_API_KEY / 未安裝本機 Whisper"
        voice_ok = "⚠️"
    text_ok = "✅" if text_provider != "未設定" else "⚠️"
    vision_ok = "✅" if vision_provider != "未設定" else "⚠️"
    image_ok = "✅" if settings.openai_api_key else "⚠️"
    await update.message.reply_text(
        "AI 狀態：\n"
        f"- 文字分析：{text_provider} {text_ok}\n"
        f"- 圖片理解：{vision_provider} {vision_ok}\n"
        f"- AI 整圖：{image_provider} {image_ok}\n"
        f"- 語音轉文字：{voice_provider} {voice_ok}\n"
        f"- 文字模型：{settings.model_fast if settings.openai_api_key else settings.openrouter_model_fast}\n"
        f"- 圖片理解模型：{settings.model_fast if settings.openai_api_key else settings.openrouter_model_fast}\n"
        f"- 整圖模型：{settings.image_model}\n"
        f"- Apify 爬蟲：{apify_provider}\n"
        f"- Gamma API：{gamma_provider}\n"
        f"- 每日簡報：{briefing_provider}\n"
        f"- Low token mode：{'✅' if settings.low_token_mode else '❌'}\n\n"
        "目前運作：文字/圖片理解優先用 OpenAI base；冇 OpenAI key 先用 OpenRouter fallback。整圖需要 OPENAI_API_KEY；語音可用本機 Whisper 免費 fallback。"
    )


async def test_ai_command(update: Update, context) -> None:
    if not update.effective_user or update.effective_user.id not in settings.allowed_user_ids:
        if update.message:
            await update.message.reply_text("呢個 bot 係私人助手，未授權。請檢查 ALLOWED_TELEGRAM_USER_IDS。")
        return
    if not update.message:
        return

    await update.message.reply_text("測試 AI provider 中...")
    try:
        import asyncio

        result = await asyncio.to_thread(
            ask_agent,
            "Jasmine",
            "用一句廣東話回覆：AI provider test ok。",
            max_output_tokens=80,
        )
    except Exception as exc:
        await update.message.reply_text(f"AI test 失敗：{exc}")
        return
    await update.message.reply_text(f"AI test 成功：\n{result}")


def build_app() -> Application:
    app = Application.builder().token(settings.telegram_bot_token).post_init(post_init).build()
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("version", version))
    app.add_handler(CommandHandler("start", basic.start))
    app.add_handler(CommandHandler("help", basic.help_command))
    app.add_handler(CommandHandler("commands", basic.commands))
    app.add_handler(CommandHandler("ask", assistant.ask))
    app.add_handler(CommandHandler("status", basic.status))
    app.add_handler(CommandHandler("status_ai", status_ai))
    app.add_handler(CommandHandler("test_ai", test_ai_command))
    app.add_handler(CommandHandler("staff", team.staff))
    app.add_handler(CommandHandler("agent", team.agent))
    app.add_handler(CommandHandler("team", team.team))
    app.add_handler(CommandHandler("team_all", team.team_all))
    app.add_handler(CommandHandler("logs", system.logs))
    app.add_handler(CommandHandler("restart_hermes", system.restart_hermes))
    app.add_handler(CommandHandler("caption", content.caption))
    app.add_handler(CommandHandler("reel", content.reel))
    app.add_handler(CommandHandler("copy", content.copy))
    app.add_handler(CommandHandler("pdf", content.pdf))
    app.add_handler(CommandHandler("slides", content.slides))
    app.add_handler(CommandHandler("landingpage", content.landingpage))
    app.add_handler(CommandHandler("imagine", content.imagine))
    app.add_handler(CommandHandler("image", content.imagine))
    app.add_handler(CommandHandler("scrape", intel.scrape))
    app.add_handler(CommandHandler("xhs", intel.xhs))
    app.add_handler(CommandHandler("report", intel.report))
    app.add_handler(CommandHandler("research", research.research))
    app.add_handler(CommandHandler("dreamteam", team.team_all))
    app.add_handler(CommandHandler("analyze_file", files.analyze_file))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.PHOTO, media.photo))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, media.voice))
    app.add_handler(MessageHandler(filters.Document.ALL, files.document))
    app.add_handler(MessageHandler(filters.COMMAND, basic.unknown_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, files.text_message))
    app.add_error_handler(error_handler)
    return app


def main() -> None:
    logger.info("Starting %s", settings.bot_service_name)
    build_app().run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
