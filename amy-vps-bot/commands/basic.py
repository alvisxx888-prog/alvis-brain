from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.config import settings
from app.security import private_only
from services.system import system_status


def _briefing_time() -> str:
    return f"{settings.daily_briefing_hour:02d}:{settings.daily_briefing_minute:02d}"


COMMAND_GUIDE = (
    "你可以咁用我：\n\n"
    "自然講法會自動演繹：\n"
    "「幫我優化呢個方案」→ /team 用最近內容交畀 Agent\n"
    "「幫我整成 PowerPoint」→ /slides 用最近內容生成 PPT\n"
    "「幫我整成 PDF」→ /pdf 用最近內容生成文件\n"
    "「搜尋最新 AI marketing 工具」→ /research 搜尋同分析\n\n"
    "情報抓取：\n"
    "「監測 IG @帳號」→ Instaloader → 搜尋 fallback → Leo 分析\n"
    "「抓 FB @專頁」→ facebook_scraper → 搜尋 fallback → Leo 分析\n"
    "「抓 Threads @帳號」→ Apify → 搜尋 fallback → Leo 分析\n"
    "「市場研究/產品機會 [主題]」→ Google/Apify 搜尋 → Leo + Alan 分析\n\n"
    "最常用：\n"
    "/ask [你想做嘅事]\n"
    "例：/ask 幫我優化呢個活動方案\n"
    "例：/ask 幫我整成 PowerPoint\n"
    "例：/ask 幫我將上面內容整成 PDF\n\n"
    "成品輸出：\n"
    "/pdf [內容/要求] - 生成 PDF\n"
    "/slides [內容/要求] - 生成 PowerPoint\n"
    "/caption [主題] - IG/小紅書 Caption\n"
    "/reel [主題] - Reels 腳本\n"
    "/copy [需求] - 廣告/WhatsApp 文案\n"
    "/landingpage [描述] - Landing Page HTML\n\n"
    "資料處理：\n"
    "貼一大段文字或上載文件，我會先存起；之後你可以講：\n"
    "/ask 幫我優化上面內容\n"
    "/ask 幫我整成 PowerPoint\n"
    "/ask 幫我整成 PDF\n\n"
    "檢查狀態：\n"
    "/ping - 測試 bot 有冇收到\n"
    "/status_ai - AI provider 狀態\n"
    "/test_ai - 測試 AI 回覆\n"
    "/status - VPS/service 狀態\n\n"
    "Group 用法：\n"
    "- 最穩陣：/ask@stanley_amy_vps_bot 幫我優化上面段文字\n"
    "- 或者 reply bot 其中一個訊息再打自然語言\n"
    "- 如果普通文字完全冇反應，多數係 BotFather privacy mode 未關；要去 @BotFather /setprivacy -> Disable。"
)


def home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("系統狀態", callback_data="status"),
                InlineKeyboardButton("最近 Logs", callback_data="logs"),
            ],
            [
                InlineKeyboardButton("生成 Caption", callback_data="help_caption"),
                InlineKeyboardButton("生成 PDF", callback_data="help_pdf"),
            ],
        ]
    )


@private_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(
        f"Stanley，我係 {settings.bot_name} v4.0 ✅\n\n"
        "全體就位：Jasmine / Tiffany / Kelvin / Leo /\n"
        "Emily / Alan / Dixon / Sharon / Dorothy\n\n"
        "━━ 支援嘅輸入 ━━\n"
        "📄 PDF  🖼 圖片  ✍️ 手寫圖  📝 Word/TXT/CSV\n"
        "🎙️ 語音訊息  💬 文字指令\n\n"
        "━━ 成品輸出 ━━\n"
        "/caption [描述] → IG/小紅書 Caption\n"
        "/reel [主題] → Reels 腳本\n"
        "/copy [需求] → 廣告/WhatsApp 文案\n"
        "/pdf [描述] → 生成 PDF\n"
        "/slides [描述] → 生成 PowerPoint\n\n"
        "/landingpage [描述] → 生成 Landing Page\n\n"
        "━━ 情報 / 系統 ━━\n"
        "/imagine 或 /image [描述] → AI 圖片 + Prompts\n"
        "/scrape ig @帳號 → IG 競品分析（Instaloader → 搜尋 fallback）\n"
        "/scrape fb @專頁 → Facebook 專頁分析\n"
        "/scrape threads @帳號 → Threads 帳號分析\n"
        "/scrape web [URL] → 抓取網頁內容\n"
        "/xhs [關鍵詞] → 小紅書帖文抓取\n"
        "/research [關鍵詞] → 搜尋摘要 + 可選分析\n"
        "/report → 即時市場 + AI 情報\n"
        "/dreamteam [問題] → 8位教練/員工分析\n\n"
        "━━ 團隊模式 ━━\n"
        "/staff → 睇員工架構\n"
        "/agent [員工] [任務] → 指名員工處理\n"
        "/team [任務] → 自動揀 1-2 位員工\n\n"
        "/status → VPS / service 狀態\n"
        "/logs → 最近 service log\n\n"
        "🔍 網絡搜尋：✅  📡 Apify："
        f"{'✅' if settings.apify_api_token else '❌'}\n"
        "🎙️ 語音轉錄：✅  📄 PDF：✅\n"
        f"每日 {_briefing_time()} 自動發送情報簡報："
        f"{'✅' if settings.daily_briefing_enabled else '❌'}\n\n"
        "你亦可以直接打自然語言，例如：\n"
        "「幫我諗痛症 IG 引流策略」\n"
        "「搜尋最新 AI marketing automation 工具」\n"
        "或者用 /ask [你想做嘅事]\n\n"
        "如果喺 group 入面普通文字冇反應，唔係你講得唔好，係 Telegram privacy mode 可能未關。\n"
        "最穩陣用：/ask@stanley_amy_vps_bot 幫我優化上面段文字\n\n"
        "有咩吩咐？",
        reply_markup=home_keyboard(),
    )


@private_only
async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(COMMAND_GUIDE)


@private_only
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(system_status())


@private_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await commands(update, context)


@private_only
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(
        "呢個指令我未識。你可以打 /commands 睇用法。\n\n"
        "如果你想自然咁講，建議用：\n"
        "/ask 幫我整成 PowerPoint\n"
        "/ask 幫我整成 PDF\n"
        "/ask 幫我優化上面內容"
    )
