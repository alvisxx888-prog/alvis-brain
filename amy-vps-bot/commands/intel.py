from __future__ import annotations

import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from app.formatting import send_long
from app.runner import run_agent
from app.security import private_only
from services.ai import ask_agent
from services.router import route_agents
from services.scraping import apify_xhs, scrape_facebook, scrape_google, scrape_instagram, scrape_threads, web_text
from services.state import set_last_content


async def _dispatch_scrape_agents(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    task: str,
    raw: str,
    *,
    fallback_agents: list[str] | None = None,
) -> None:
    agents = route_agents(task)[:2]
    if fallback_agents:
        for agent in fallback_agents:
            if agent not in agents:
                agents.append(agent)
    agents = agents[:2] or ["Leo"]
    await update.message.reply_text(f"資料已抓取，調度：{' / '.join(agents)}")
    replies: list[str] = []
    for agent in agents:
        result = await run_agent(
            update,
            context,
            agent,
            "Stanley 已抓取以下資料，請根據你嘅角色輸出可執行分析。\n"
            "只可根據資料內容推論；資料不足就標明「待補資料」。\n\n"
            f"任務：{task}\n\n資料：\n{raw[:6000]}",
            max_output_tokens=1400,
        )
        if result:
            reply = f"{agent} 分析：\n\n{result}"
            replies.append(reply)
            await send_long(update, reply)
    if replies:
        set_last_content(context, "\n\n".join(replies), limit=20000)


@private_only
async def scrape(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args or []
    if len(args) < 2:
        await update.message.reply_text(
            "用法：\n"
            "/scrape ig @帳號 → IG 競品分析（Instaloader → Search fallback）\n"
            "/scrape fb @專頁 → Facebook 專頁分析\n"
            "/scrape threads @帳號 → Threads 帳號分析\n"
            "/scrape web [URL] → 抓取網頁內容"
        )
        return
    mode = args[0].lower()
    target = " ".join(args[1:]).strip()

    if mode == "ig":
        await update.message.reply_text(f"IG 抓取 {target} 中：Instaloader → Search fallback")
        raw = await asyncio.to_thread(scrape_instagram, target)
        set_last_content(context, raw, limit=12000)
        await send_long(update, raw)
        await _dispatch_scrape_agents(update, context, f"IG 競品分析：{target}", raw, fallback_agents=["Leo", "Tiffany"])
        return

    if mode in {"fb", "facebook"}:
        await update.message.reply_text(f"Facebook 抓取 {target} 中：facebook_scraper → Search fallback")
        raw = await asyncio.to_thread(scrape_facebook, target)
        set_last_content(context, raw, limit=12000)
        await send_long(update, raw)
        await _dispatch_scrape_agents(update, context, f"Facebook 專頁分析：{target}", raw, fallback_agents=["Leo", "Tiffany"])
        return

    if mode in {"threads", "thread"}:
        await update.message.reply_text(f"Threads 抓取 {target} 中：Apify → Search fallback")
        raw = await asyncio.to_thread(scrape_threads, target)
        set_last_content(context, raw, limit=12000)
        await send_long(update, raw)
        await _dispatch_scrape_agents(update, context, f"Threads 帳號分析：{target}", raw, fallback_agents=["Leo", "Tiffany"])
        return

    if mode == "web":
        await update.message.reply_text(f"抓取網頁中：{target}")
        try:
            raw = await asyncio.to_thread(web_text, target)
        except Exception as exc:
            await update.message.reply_text(f"抓取失敗：{exc}")
            return
        set_last_content(context, raw, limit=12000)
        await send_long(update, f"網頁內容：\n\n{raw[:4000]}")
        await _dispatch_scrape_agents(update, context, f"網頁內容分析：{target}", raw, fallback_agents=["Leo"])
        return

    await update.message.reply_text("只支援：/scrape ig @帳號、/scrape fb @專頁、/scrape threads @帳號 或 /scrape web [URL]")


@private_only
async def xhs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args).strip() if context.args else ""
    if not query:
        await update.message.reply_text("用法：/xhs [關鍵詞]")
        return
    await update.message.reply_text(f"抓取小紅書「{query}」中...")
    raw = await asyncio.to_thread(apify_xhs, query)
    await send_long(update, raw)
    if "Apify 未設定" in raw:
        return
    analysis = await asyncio.to_thread(
        ask_agent,
        "Tiffany",
        f"根據以下小紅書資料，整理：爆款標題規律、熱門角度、Stanley 可用嘅3個內容方向。\n\n{raw[:5000]}",
        max_output_tokens=1200,
    )
    set_last_content(context, f"Tiffany 小紅書分析：\n\n{analysis}", limit=12000)
    await send_long(update, f"Tiffany 小紅書分析：\n\n{analysis}")


@private_only
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("生成即時市場 + AI 情報中...")
    queries = [
        "香港 美容 市場 趨勢",
        "香港 痛症 治療 市場",
        "AI marketing automation latest tools",
    ]
    raws = []
    for q in queries:
        try:
            raws.append(await asyncio.to_thread(scrape_google, q, 4))
        except Exception as exc:
            raws.append(f"{q}: 搜尋失敗 {exc}")
    raw = "\n\n".join(raws)
    result = await asyncio.to_thread(
        ask_agent,
        "Leo",
        "根據以下搜尋資料，生成 Stanley 今日情報簡報。"
        "輸出：市場動態、AI工具機會、今日3個行動。\n\n"
        f"{raw[:7000]}",
        max_output_tokens=1500,
    )
    set_last_content(context, f"今日情報簡報：\n\n{result}", limit=12000)
    await send_long(update, f"今日情報簡報：\n\n{result}")
