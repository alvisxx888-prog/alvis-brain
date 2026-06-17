from __future__ import annotations

import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from app.formatting import send_long
from app.security import private_only
from services.ai import ask_agent
from services.scraping import scrape_google


@private_only
async def research(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args).strip() if context.args else ""
    if not query:
        await update.message.reply_text("用法：/research [關鍵詞]")
        return
    await update.message.reply_text(f"搜尋「{query}」中...")
    raw = await asyncio.to_thread(scrape_google, query, 6)
    await send_long(update, raw)

    await update.message.reply_text("Leo 生成精簡分析中...")
    analysis = await asyncio.to_thread(
        ask_agent,
        "Leo",
        f"根據以下搜尋結果，整理對 Stanley 美容/痛症業務有用嘅情報。"
        f"輸出：3個洞察、3個行動、需要小心嘅假設。\n\n{raw[:5000]}",
        max_output_tokens=1200,
    )
    await send_long(update, f"Leo 分析：\n\n{analysis}")
