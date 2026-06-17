from __future__ import annotations

import asyncio
import re

from telegram import Update
from telegram.ext import ContextTypes

from commands.content import (
    _landing_source_from_request,
    _pdf_source_from_request,
    _slides_source_from_request,
    create_landing_page_document,
    create_pdf_document,
    create_slides_document,
)
from app.formatting import send_long
from app.runner import run_agent
from app.security import private_only
from services.ai import normalize_agent
from services.ai import ask_agent
from services.router import route_agents
from services.scraping import (
    apify_xhs,
    scrape_facebook,
    scrape_google,
    scrape_instagram,
    scrape_threads,
    web_text,
)
from services.state import get_last_content, set_last_content


URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
RECENT_CONTENT_WORDS = [
    "呢個",
    "依個",
    "剛才",
    "啱啱",
    "上面",
    "以上",
    "內容",
    "方案",
    "佢",
    "佢哋",
    "嗰啲",
    "他們",
    "它",
    "之前",
    "最近",
]
HANDOFF_WORDS = ["俾一段", "貼一段", "send 一段", "send段", "貼段", "俾段", "我而家俾", "等陣俾", "等陣貼"]
ACCOUNTABILITY_WORDS = ["盯住", "跟進", "記住", "提醒", "提我", "check住", "check 我", "accountable", "追住"]


def _args(context: ContextTypes.DEFAULT_TYPE) -> str:
    return " ".join(context.args).strip() if context.args else ""


def _is_help_request(text: str) -> bool:
    lowered = text.lower()
    return any(k in lowered for k in ["你識咩", "有咩功能", "help", "指令", "點用", "咩都識"])


def _wants_search(text: str) -> bool:
    lowered = text.lower()
    return any(k in lowered for k in ["搜尋", "search", "research", "最新", "今日", "查下", "搵下", "市場", "趨勢"])


def _extract_ig_target(text: str) -> str | None:
    lowered = text.lower()
    if not any(k in lowered for k in ["ig", "instagram", "競品", "監測", "scrape", "抓", "爬"]):
        return None
    match = re.search(r"(?:ig|instagram)?\s*@([A-Za-z0-9._]+)", text, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"(?:ig|instagram)\s+([A-Za-z0-9._]+)", text, re.IGNORECASE)
    return match.group(1) if match else None


def _is_ig_skill_request(text: str) -> bool:
    lowered = text.lower()
    return "ig-instaloader-scraper" in lowered or (
        "instaloader" in lowered and any(k in lowered for k in ["ig", "instagram", "scrape", "擷取", "抓取", "檢查"])
    )


def _extract_any_ig_handle(text: str) -> str | None:
    match = re.search(r"@([A-Za-z0-9._]+)", text)
    if match:
        return match.group(1)
    return _extract_ig_target(text)


def _extract_social_target(text: str, platform_words: list[str]) -> str | None:
    lowered = text.lower()
    if not any(word in lowered for word in platform_words):
        return None
    match = re.search(r"@([A-Za-z0-9._-]+)", text)
    if match:
        return match.group(1)
    words = "|".join(re.escape(word) for word in platform_words)
    match = re.search(rf"(?:{words})\s+([A-Za-z0-9._-]+)", text, re.IGNORECASE)
    return match.group(1) if match else None


def _extract_xhs_query(text: str) -> str | None:
    if "小紅書" not in text and "xhs" not in text.lower():
        return None
    cleaned = re.sub(r"(?i)\bxhs\b|小紅書|搜尋|搜|搵|抓|爬|監測|分析|帖文|內容", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ，,。")
    return cleaned or None


def _extract_product_research_query(text: str) -> str | None:
    lowered = text.lower()
    if not any(k in lowered for k in ["產品機會", "新產品", "product research", "市場研究", "商機"]):
        return None
    cleaned = re.sub(r"(?i)product research|產品機會|新產品|市場研究|商機|搵下|分析|有咩可以做", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ，,。")
    return cleaned or text


def _mentions_recent_content(text: str) -> bool:
    return any(k in text for k in RECENT_CONTENT_WORDS)


def _requests_fresh_team_work(text: str) -> bool:
    lowered = text.lower()
    return any(
        k in lowered
        for k in [
            "分析",
            "研究",
            "諗",
            "幫我做",
            "做完",
            "整完",
            "完成之後",
            "等兩個",
            "等佢哋",
            "等他們",
            "由 jasmine",
            "jasmine 整合",
            "再整成",
            "再做成",
            "再生成",
        ]
    )


def _wants_revision(text: str) -> bool:
    lowered = text.lower()
    return any(
        k in lowered
        for k in [
            "優化",
            "改善",
            "執靚",
            "整靚",
            "改好",
            "upgrade",
            "improve",
            "完善",
            "整理",
            "變成",
            "改成",
        ]
    )


def _expects_content_next(text: str) -> bool:
    lowered = text.lower()
    if not any(k in lowered for k in HANDOFF_WORDS):
        return False
    return any(
        k in lowered
        for k in [
            "優化",
            "改善",
            "整理",
            "改",
            "文案",
            "caption",
            "proposal",
            "內容",
            "段文字",
            "篇文",
        ]
    )


def _expects_brief_next(text: str) -> bool:
    lowered = text.lower()
    compact = re.sub(r"\s+", "", text)
    if len(compact) > 24 or _mentions_recent_content(text):
        return False
    if not any(k in lowered for k in ["廣告", "文案", "caption", "reel", "帖文", "post", "小紅書"]):
        return False
    return any(k in lowered for k in ["幫我整", "幫我寫", "幫我做", "整", "寫", "做", "生成"])


def _accountability_items(context: ContextTypes.DEFAULT_TYPE) -> list[str]:
    items = context.bot_data.setdefault("accountability_items", [])
    return items if isinstance(items, list) else []


def _is_accountability_request(text: str) -> bool:
    lowered = text.lower()
    if any(k in lowered for k in ACCOUNTABILITY_WORDS):
        return True
    return any(k in text for k in ["今晚要", "今日要", "聽日要", "一定要", "唔可以再拖"])


def _is_accountability_review(text: str) -> bool:
    lowered = text.lower()
    return any(k in lowered for k in ["checkin", "check-in", "今日要做咩", "有咩要跟", "我有咩未做", "待辦"])


def _clean_accountability_goal(text: str) -> str:
    cleaned = re.sub(
        r"幫我|幫手|唔該|請|記住|提醒|提我|盯住|跟進|check住|check 我|accountable|一定要|唔可以再拖",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ，,。")
    return cleaned or text


def _with_recent_context(text: str, last_content: str) -> str:
    if last_content and (_mentions_recent_content(text) or _wants_revision(text)):
        return f"用戶要求：{text}\n\n最近內容：\n{last_content[:16000]}"
    return text


def _brief(text: str, limit: int = 80) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else f"{text[:limit]}..."


def _human_preview(text: str) -> str:
    preview = _brief(text, 52)
    return f"「{preview}」" if preview else "呢件事"


async def normalize_group_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> str:
    bot_username = ""
    try:
        me = await context.bot.get_me()
        bot_username = me.username or ""
    except Exception:
        bot_username = ""

    if bot_username:
        text = re.sub(rf"(?i)@{re.escape(bot_username)}\b", " ", text)

    text = re.sub(r"\s+", " ", text).strip(" ，,。")
    return text


def _named_agents(text: str) -> list[str]:
    names: list[str] = []
    for raw in re.findall(r"[A-Za-z]+", text):
        agent = normalize_agent(raw)
        if agent and agent not in names:
            names.append(agent)
    return names


async def _run_named_team(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    agents: list[str],
    *,
    create_pdf: bool = False,
    create_slides: bool = False,
    create_landing: bool = False,
) -> None:
    last_content = get_last_content(context)
    task = _with_recent_context(text, last_content)
    workers = [agent for agent in agents if agent != "Jasmine"]
    if not workers:
        workers = route_agents(task)[:2]
    await update.message.reply_text(
        f"收到，我會先搵 {' / '.join(workers)} 做內容，之後由 Jasmine 整合把關。"
        + (" 再交俾 Tiffany 出 PDF。" if create_pdf else "")
        + (" 做埋 PowerPoint。" if create_slides else "")
        + (" 再交俾 Tiffany 出 Landing Page。" if create_landing else "")
    )
    outputs: list[str] = []
    for agent in workers:
        result = await run_agent(
            update,
            context,
            agent,
            f"Stanley 指名你參與呢個任務：{task}\n請按你角色輸出可直接使用嘅建議。",
            max_output_tokens=900,
        )
        if result:
            outputs.append(f"{agent}：\n{result}")

    if not outputs:
        return

    summary = await run_agent(
        update,
        context,
        "Jasmine",
        "你係 Jasmine，現在只可以做整合員，不可以做資料來源。\n"
        "必須只根據以下已完成嘅員工輸出整理最終版本；唔可以用自己記憶、常識或角色設定新增未出現嘅內容。\n"
        "如果某部分資料不足，請標明「待補資料」，唔好腦補。\n"
        "請用廣東話整理成清晰、可執行嘅最終版本，保留各員工已提出嘅重點同下一步：\n\n"
        + "\n\n".join(outputs),
        max_output_tokens=1400,
    )
    final_text = f"Jasmine 整合：\n\n{summary}" if summary else "\n\n".join(outputs)
    set_last_content(context, final_text, limit=12000)
    await send_long(update, final_text)

    if create_pdf:
        await update.message.reply_text("Jasmine 已整合好，我而家交俾 Tiffany 生成 PDF。")
        await create_pdf_document(update, final_text)

    if create_slides:
        await update.message.reply_text("Jasmine 已整合好，我而家交俾 Tiffany 生成 PowerPoint。")
        await create_slides_document(update, final_text)

    if create_landing:
        await update.message.reply_text("Jasmine 已整合好，我而家交俾 Tiffany 生成 Landing Page。")
        await create_landing_page_document(update, final_text)


async def _dispatch_scrape_result(
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


def _wants_pdf(text: str) -> bool:
    lowered = text.lower().replace(" ", "")
    return any(
        k in lowered
        for k in [
            "pdf",
            "file",
            "document",
            "doc",
            "整份文件", "整文件", "做文件", "生成文件", "轉文件",
            "整個file", "做個file", "整個檔案", "做個檔案",
            "出份", "出個文件", "出個pdf", "出個file",
            "報告", "檔案", "文檔",
        ]
    )


def _wants_slides(text: str) -> bool:
    lowered = text.lower().replace(" ", "")
    return any(
        k in lowered
        for k in [
            "powerpoint",
            "ppt",
            "pptx",
            "slides",
            "slide",
            "簡報",
            "投影片",
            "整成powerpoint",
            "整個powerpoint",
            "做個powerpoint",
            "整成ppt",
            "做成ppt",
            "整簡報",
            "做簡報",
        ]
    )


def _wants_landing_page(text: str) -> bool:
    lowered = text.lower().replace(" ", "")
    return any(k in lowered for k in ["landingpage", "landing", "落地頁", "網頁", "html"])


def _extract_pdf_description(text: str, last_content: str) -> str:
    referenced = _pdf_source_from_request(text, last_content)
    if referenced != text and referenced:
        return referenced
    cleaned = re.sub(
        r"(?i)\bpdf\b|幫我|幫手|唔該|請|整成|整個|整份|整|做成|做個|做份|做|生成|轉成|轉|文件|呢個|依個|剛才|上面|內容",
        " ",
        text,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ，,。")
    if len(cleaned) >= 20:
        if last_content and any(k in text for k in ["呢個", "依個", "剛才", "上面", "內容"]):
            return f"用戶要求：{text}\n\n資料：\n{last_content}"
        return cleaned
    return last_content


def _extract_landing_description(text: str, last_content: str) -> str:
    referenced = _landing_source_from_request(text, last_content)
    if referenced != text and referenced:
        return referenced
    cleaned = re.sub(
        r"(?i)\blanding\s*page\b|\blandingpage\b|\bhtml\b|幫我|幫手|唔該|請|整成|整個|整份|整|做成|做個|做份|做|生成|轉成|轉|落地頁|網頁|呢個|依個|剛才|上面|內容",
        " ",
        text,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ，,。")
    if len(cleaned) >= 20:
        if last_content and any(k in text for k in ["呢個", "依個", "剛才", "上面", "內容", "嗰啲", "佢哋"]):
            return f"用戶要求：{text}\n\n資料：\n{last_content}"
        return cleaned
    return last_content


def _extract_slides_description(text: str, last_content: str) -> str:
    referenced = _slides_source_from_request(text, last_content)
    if referenced != text and referenced:
        return referenced
    cleaned = re.sub(
        r"(?i)\bpowerpoint\b|\bpptx?\b|\bslides?\b|幫我|幫手|唔該|請|整成|整個|整份|整|做成|做個|做份|做|生成|轉成|轉|簡報|投影片|呢個|依個|剛才|上面|內容",
        " ",
        text,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ，,。")
    if len(cleaned) >= 20:
        if last_content and any(k in text for k in ["呢個", "依個", "剛才", "上面", "內容"]):
            return f"用戶要求：{text}\n\n資料：\n{last_content}"
        return cleaned
    return last_content


def assistant_capabilities() -> str:
    return (
        "我可以做你嘅全能小助手入口：\n\n"
        "1. 直接問問題：例如「幫我諗痛症引流策略」\n"
        "2. 口語交代：例如「我而家俾段文字你，你幫我優化」\n"
        "3. 寫內容：caption、Reels、廣告、WhatsApp 跟進、Landing Page\n"
        "4. 做研究：最新市場/AI 工具/競品方向\n"
        "5. 分析資料：貼長文、上載 PDF/DOCX/TXT/CSV，再叫我分析或整 PDF/Slides\n"
        "6. accountability：例如「我今晚要搞掂 proposal，幫我盯住」\n"
        "7. 系統/VPS：status、logs、restart Hermes\n\n"
        "你可以自然講，我會先回覆我理解到咩；如果唔夠資料，我會問你補充。"
    )


async def handle_assistant_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    if not update.message:
        return

    text = text.strip()
    text = await normalize_group_text(update, context, text)
    if not text:
        await update.message.reply_text("我收到。你可以直接講想我做咩，例如：幫我優化上面段文字。")
        return

    if _is_help_request(text):
        await update.message.reply_text(assistant_capabilities())
        return

    if _is_ig_skill_request(text):
        handle = _extract_any_ig_handle(text)
        if not handle:
            await update.message.reply_text(
                "收到。`ig-instaloader-scraper` 係我哋嘅 Codex 開發規則；"
                "Telegram 呢邊真正使用方法係：\n"
                "/scrape ig @帳號\n\n"
                "你直接俾我 IG 帳號，例如：/scrape ig @beautysignaturehk"
            )
            return
        await update.message.reply_text(f"收到，我會用 Instaloader 檢查 IG @{handle}，唔用 Apify。")
        raw = await asyncio.to_thread(scrape_instagram, handle)
        set_last_content(context, raw, limit=12000)
        await send_long(update, raw)
        await _dispatch_scrape_result(
            update,
            context,
            f"IG Instaloader 擷取檢查：@{handle}",
            raw,
            fallback_agents=["Leo", "Tiffany"],
        )
        return

    if _is_accountability_review(text):
        items = _accountability_items(context)
        if not items:
            await update.message.reply_text("暫時未有待跟進事項。你可以講：今晚要做 X，幫我盯住。")
            return
        lines = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items[-10:]))
        await update.message.reply_text(f"你目前要跟進嘅事項：\n{lines}\n\n做完可以同我講：完成咗 [事項]。")
        return

    if any(k in text for k in ["完成咗", "做完", "搞掂", "done"]):
        items = _accountability_items(context)
        if items:
            done_text = re.sub(r"完成咗|做完|搞掂|done", " ", text, flags=re.IGNORECASE).strip(" ，,。")
            removed = None
            for item in list(items):
                if not done_text or done_text in item or item in done_text:
                    removed = item
                    items.remove(item)
                    break
            await update.message.reply_text(
                f"好，已標記完成：{removed or done_text or '最近一項'}。\n"
                f"仲有 {len(items)} 項待跟進。"
            )
            return

    if _expects_content_next(text):
        context.bot_data["pending_text_task"] = text
        await update.message.reply_text(
            "得，我明你想點做。\n"
            "你下一個訊息直接貼段文字過嚟就得，我會接住幫你優化，唔需要再打指令。"
        )
        return

    if _expects_brief_next(text):
        context.bot_data["pending_text_task"] = text
        await update.message.reply_text(
            "可以，我等你補資料先寫，咁會準好多。\n"
            "你直接貼：產品/服務、offer、目標客群、語氣、想放嘅平台。"
        )
        return

    if _is_accountability_request(text):
        goal = _clean_accountability_goal(text)
        items = _accountability_items(context)
        if goal not in items:
            items.append(goal)
        await update.message.reply_text(
            f"收到，我幫你記低同跟進：{goal}\n\n"
            "下一步：你可以話我知第一步係咩，或者直接叫我幫你拆成 3 個可做步驟。"
        )
        return

    named_agents = _named_agents(text)
    wants_pdf = _wants_pdf(text)
    wants_slides = _wants_slides(text)
    wants_landing = _wants_landing_page(text)
    refers_to_recent = _mentions_recent_content(text)

    if len(named_agents) >= 2 and (wants_pdf or wants_slides or wants_landing) and (
        not refers_to_recent or _requests_fresh_team_work(text)
    ):
        await _run_named_team(
            update,
            context,
            text,
            named_agents[:4],
            create_pdf=wants_pdf,
            create_slides=wants_slides,
            create_landing=wants_landing,
        )
        return

    if wants_pdf:
        description = _extract_pdf_description(text, get_last_content(context))
        if not description:
            context.bot_data["pending_pdf"] = True
            await update.message.reply_text("可以。你貼內容過嚟，我會幫你整理成 PDF。")
            return
        context.bot_data.pop("pending_pdf", None)
        await update.message.reply_text("收到，我幫你將內容整理成一份 PDF。")
        await create_pdf_document(update, description)
        return

    if len(named_agents) >= 2 and not (wants_slides or wants_landing):
        await _run_named_team(update, context, text, named_agents[:4], create_slides=wants_slides, create_landing=wants_landing)
        return

    if wants_slides:
        description = _extract_slides_description(text, get_last_content(context))
        if not description:
            context.bot_data["pending_slides"] = True
            await update.message.reply_text("可以。你貼內容過嚟，我會幫你整理成 PowerPoint。")
            return
        context.bot_data.pop("pending_slides", None)
        await update.message.reply_text("收到，我幫你整理成 PowerPoint。")
        await create_slides_document(update, description)
        return

    if wants_landing:
        description = _extract_landing_description(text, get_last_content(context))
        if not description:
            context.bot_data["pending_landing"] = True
            await update.message.reply_text("可以。你貼內容過嚟，我會幫你整理成 Landing Page。")
            return
        context.bot_data.pop("pending_landing", None)
        await update.message.reply_text("收到，我幫你整理成 Landing Page。")
        await create_landing_page_document(update, description)
        return

    ig_target = _extract_ig_target(text)
    if ig_target:
        await update.message.reply_text(f"收到，我去睇 IG @{ig_target} 嘅資料，然後幫你整理重點。")
        raw = await asyncio.to_thread(scrape_instagram, ig_target)
        set_last_content(context, raw, limit=12000)
        await send_long(update, raw)
        await _dispatch_scrape_result(update, context, f"{text}\nIG @{ig_target}", raw, fallback_agents=["Leo", "Tiffany"])
        return

    fb_target = _extract_social_target(text, ["fb", "facebook", "臉書"])
    if fb_target:
        await update.message.reply_text(f"收到，我去睇 Facebook @{fb_target}，再幫你分析可以點用。")
        raw = await asyncio.to_thread(scrape_facebook, fb_target)
        set_last_content(context, raw, limit=12000)
        await send_long(update, raw)
        await _dispatch_scrape_result(update, context, f"{text}\nFacebook {fb_target}", raw, fallback_agents=["Leo", "Tiffany"])
        return

    threads_target = _extract_social_target(text, ["threads", "thread"])
    if threads_target:
        await update.message.reply_text(f"收到，我去睇 Threads @{threads_target}，再幫你整理方向。")
        raw = await asyncio.to_thread(scrape_threads, threads_target)
        set_last_content(context, raw, limit=12000)
        await send_long(update, raw)
        await _dispatch_scrape_result(update, context, f"{text}\nThreads @{threads_target}", raw, fallback_agents=["Leo", "Tiffany"])
        return

    xhs_query = _extract_xhs_query(text)
    if xhs_query:
        await update.message.reply_text(f"收到，我幫你搵小紅書「{xhs_query}」相關內容，再整理可用角度。")
        raw = await asyncio.to_thread(apify_xhs, xhs_query)
        set_last_content(context, raw, limit=12000)
        await send_long(update, raw)
        if "Apify 未設定" in raw:
            return
        result = await run_agent(
            update, context, "Tiffany",
            "根據以下小紅書資料，整理：爆款標題規律、熱門角度、Stanley 可用嘅3個內容方向。"
            f"\n\n用戶要求：{text}\n\n資料：\n{raw[:5000]}",
            max_output_tokens=1800,
        )
        if result:
            reply = f"Tiffany 小紅書分析：\n\n{result}"
            set_last_content(context, reply, limit=12000)
            await send_long(update, reply)
        return

    url_match = URL_RE.search(text)
    if url_match:
        url = url_match.group(0)
        await update.message.reply_text("收到條 link。我會先讀內容，再幫你抽重點同下一步。")
        try:
            raw = await asyncio.to_thread(web_text, url)
        except Exception as exc:
            await update.message.reply_text(f"抓取失敗：{exc}")
            return
        set_last_content(context, raw, limit=12000)
        await _dispatch_scrape_result(update, context, text, raw, fallback_agents=["Leo"])
        return

    product_query = _extract_product_research_query(text)
    if product_query:
        await update.message.reply_text(f"收到，我會圍繞「{_brief(product_query, 40)}」搵市場線索，再幫你拆產品機會。")
        raw = await asyncio.to_thread(scrape_google, f"{product_query} 香港 美容 痛症 市場 產品 機會", 8)
        set_last_content(context, raw, limit=12000)
        leo = await run_agent(
            update, context, "Leo",
            "根據以下市場搜尋資料，整理真實市場線索、需求缺口、競品訊號。"
            f"\n\n資料：\n{raw[:6000]}",
            max_output_tokens=1200,
        )
        alan = await run_agent(
            update, context, "Alan",
            "根據以下市場資料同 Leo 線索，提出 Stanley 可以即時測試嘅產品/服務機會。"
            "每個機會要有：目標客群、offer、驗證方法、風險。"
            f"\n\nLeo：\n{leo or ''}\n\n資料：\n{raw[:6000]}",
            max_output_tokens=1400,
        )
        reply = f"Leo 市場線索：\n\n{leo or '未能取得 Leo 回應'}\n\nAlan 產品機會：\n\n{alan or '未能取得 Alan 回應'}"
        set_last_content(context, reply, limit=12000)
        await send_long(update, reply)
        return

    if _wants_search(text):
        await update.message.reply_text(f"收到，我先幫你查資料，再整理成可行動嘅重點：{_human_preview(text)}")
        try:
            raw = await asyncio.to_thread(scrape_google, text, 6)
        except Exception as exc:
            await update.message.reply_text(f"搜尋失敗：{exc}")
            return
        set_last_content(context, raw, limit=12000)
        await send_long(update, raw)
        result = await run_agent(
            update, context, "Leo",
            "根據以下搜尋結果，整理成可執行情報。"
            "輸出：3個洞察、3個行動、需要小心嘅假設。"
            f"\n\n{raw[:6000]}",
            max_output_tokens=1300,
        )
        if result:
            reply = f"Leo 分析：\n\n{result}"
            set_last_content(context, reply, limit=12000)
            await send_long(update, reply)
        return

    last_content = get_last_content(context)
    agent_task = _with_recent_context(text, last_content)
    agents = route_agents(agent_task)[:2]
    await update.message.reply_text(
        f"收到，我明你想處理：{_human_preview(text)}\n"
        "我先幫你諗一版可直接用嘅回覆。"
    )
    replies: list[str] = []
    for agent in agents:
        result = await run_agent(
            update, context, agent,
            f"Stanley 直接用自然語言交代任務：{agent_task}\n請輸出可以立即使用嘅結果。",
            max_output_tokens=1200,
        )
        if result:
            reply = f"{agent}：\n\n{result}"
            replies.append(reply)
            await send_long(update, reply)
    if replies:
        set_last_content(context, "\n\n".join(replies), limit=20000)


@private_only
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    request = _args(context)
    if not request:
        await update.message.reply_text("用法：/ask [你想我做嘅事]\n例：/ask 幫我諗痛症 IG 引流策略")
        return
    await handle_assistant_text(update, context, request)
