from __future__ import annotations

import asyncio
import re

from telegram import Update
from telegram.ext import ContextTypes

from app.formatting import send_long
from app.runner import run_agent
from app.security import private_only
from commands.assistant import handle_assistant_text
from commands.content import create_landing_page_document, create_pdf_document, create_slides_document
from services.ai import ask_agent
from services.files import extract_text
from services.router import route_agents
from services.state import get_last_content, set_last_content


INLINE_PDF_RE = re.compile(r"(?im)(?:^|\s)/pdf(?:@\w+)?(?:\s|$)")
INLINE_SLIDES_RE = re.compile(r"(?im)(?:^|\s)/(?:slides|ppt|pptx)(?:@\w+)?(?:\s|$)")
SHORT_PENDING_REPLIES = {
    "hello",
    "hi",
    "hey",
    "ok",
    "okay",
    "test",
    "好",
    "好的",
    "得",
    "可以",
    "收到",
}


def _remove_inline_command(text: str, pattern: re.Pattern[str]) -> str:
    return pattern.sub(" ", text).strip()


def _is_short_pending_reply(text: str) -> bool:
    normalized = re.sub(r"\s+", "", text).strip("，,。.!！?")
    return len(normalized) <= 12 and normalized.lower() in SHORT_PENDING_REPLIES


@private_only
async def document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.document:
        return
    doc = update.message.document
    file = await context.bot.get_file(doc.file_id)
    data = await file.download_as_bytearray()
    text = extract_text(bytes(data), doc.mime_type or "", doc.file_name or "")
    if not text.strip():
        await update.message.reply_text("暫時讀唔到呢種文件。支援 PDF / TXT / CSV / MD / JSON / DOCX。")
        return
    set_last_content(context, text, limit=20000)
    await update.message.reply_text(
        f"已讀取文件：{doc.file_name}\n"
        f"抽到約 {len(text)} 字。\n\n"
        "我已先存起內容，未有燒 AI。\n"
        "你可以打：/pdf、/slides，或者 /analyze_file。"
    )


@private_only
async def analyze_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = get_last_content(context)
    if not text:
        await update.message.reply_text("未有文件內容。請先上載 PDF / TXT / CSV / DOCX。")
        return
    await update.message.reply_text("Leo 分析文件中...")
    result = await run_agent(
        update, context, "Leo",
        f"分析以下文件，輸出：核心重點、可用機會、下一步行動。內容：\n\n{text[:12000]}",
        max_output_tokens=1600,
    )
    if result:
        analysis = f"Leo 文件分析：\n\n{result}"
        set_last_content(context, analysis, limit=20000)
        await send_long(update, analysis)


@private_only
async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    pending_text_task = context.bot_data.pop("pending_text_task", "")
    if pending_text_task:
        if _is_short_pending_reply(text):
            context.bot_data["pending_text_task"] = pending_text_task
            await update.message.reply_text("我仲等緊你貼要處理嗰段內容。你可以直接貼原文過嚟。")
            return

        set_last_content(context, text, limit=20000)
        task = (
            f"Stanley 之前交代嘅任務：{pending_text_task}\n\n"
            "以下係佢剛剛貼出嚟要處理嘅內容。請直接完成任務，輸出可直接使用嘅最終版本；"
            "唔好再叫佢貼內容，唔好只確認收到。\n\n"
            f"內容：\n{text}"
        )
        agent = route_agents(f"{pending_text_task}\n{text}")[0]
        result = await run_agent(update, context, agent, task, max_output_tokens=1400)
        if result:
            reply = f"{agent}：\n\n{result}"
            set_last_content(context, reply, limit=20000)
            await send_long(update, reply)
        return
    if len(text) >= 200:
        set_last_content(context, text, limit=20000)
        if context.bot_data.pop("pending_pdf", False):
            await create_pdf_document(update, text[:5000])
            return
        if context.bot_data.pop("pending_slides", False):
            await create_slides_document(update, text[:5000])
            return
        if context.bot_data.pop("pending_landing", False):
            await create_landing_page_document(update, text[:5000])
            return
        if INLINE_PDF_RE.search(text):
            await create_pdf_document(update, _remove_inline_command(text, INLINE_PDF_RE)[:5000])
            return
        if INLINE_SLIDES_RE.search(text):
            await create_slides_document(update, _remove_inline_command(text, INLINE_SLIDES_RE)[:5000])
            return
        if "pdf" in text.lower() or "整文件" in text or "做文件" in text or "生成文件" in text:
            await handle_assistant_text(update, context, text)
            return
        if (
            "powerpoint" in text.lower()
            or "ppt" in text.lower()
            or "簡報" in text
            or "投影片" in text
        ):
            await handle_assistant_text(update, context, text)
            return
        if "landing" in text.lower() or "落地頁" in text or "網頁" in text or "html" in text.lower():
            await handle_assistant_text(update, context, text)
            return
        if any(k in text.lower() for k in ["優化", "改善", "整理", "分析", "summary", "summarize", "總結", "建議", "idea"]):
            await update.message.reply_text("收到呢段內容，我會直接幫你整理同優化。")
            await handle_assistant_text(update, context, text)
            return
        await update.message.reply_text(
            f"收到，我已經讀到呢段長內容（約 {len(text)} 字），先幫你保存咗。\n"
            "你可以直接講：幫我優化、幫我總結、幫我整成 PDF，或者幫我拆下一步。"
        )
        return
    await handle_assistant_text(update, context, text)
