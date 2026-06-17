from __future__ import annotations

import asyncio
import re

from telegram import Update
from telegram.ext import ContextTypes

from app.formatting import send_long
from app.runner import run_agent
from app.security import private_only
from services.ai import AGENTS, ask_agent, normalize_agent
from services.router import route_agents
from services.state import set_last_content


TEAM_ORDER = ["Jasmine", "Tiffany", "Kelvin", "Leo", "Emily", "Alan", "Dixon", "Sharon", "Dorothy"]


def _wants_pdf(text: str) -> bool:
    lowered = text.lower().replace(" ", "")
    return any(k in lowered for k in ["pdf", "document", "doc", "文件", "檔案"])


def _wants_slides(text: str) -> bool:
    lowered = text.lower().replace(" ", "")
    return any(k in lowered for k in ["powerpoint", "ppt", "pptx", "slides", "slide", "簡報", "投影片"])


def _wants_landing_page(text: str) -> bool:
    lowered = text.lower().replace(" ", "")
    return any(k in lowered for k in ["landingpage", "landing", "落地頁", "網頁", "html"])


@private_only
async def team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    request = " ".join(context.args).strip() if context.args else ""
    if not request:
        await update.message.reply_text(
            "用法：/team [問題或任務]\n"
            "我會用本地規則揀 1-2 位最相關員工，慳 token。\n\n"
            "例：/team 幫我諗痛症 IG 引流策略"
        )
        return

    agents = route_agents(request)[:2]
    await update.message.reply_text(
        f"調度：{' / '.join(agents)}\n"
        "Jasmine 會等員工全部完成輸出後，先根據佢哋嘅內容整合。"
    )
    outputs: list[str] = []
    for agent in agents:
        result = await run_agent(update, context, agent, f"Stanley 嘅任務：{request}", max_output_tokens=1200)
        if result:
            output = f"{agent}：\n\n{result}"
            outputs.append(output)
            await send_long(update, output)

    if not outputs:
        return

    if _wants_pdf(request) or _wants_slides(request) or _wants_landing_page(request):
        await update.message.reply_text("員工內容已完成，Jasmine 而家整合把關。")
        summary = await run_agent(
            update,
            context,
            "Jasmine",
            "你係 Jasmine，現在只可以做整合員，不可以做資料來源。\n"
            "必須只根據以下已完成嘅員工輸出整合成最終版本；唔可以用自己記憶、常識或角色設定新增未出現嘅內容。\n"
            "保留來源內容重點，不要新增未提供嘅 offer、數字、案例、承諾或策略。\n"
            "如果資料不足，請標明「待補資料」，唔好腦補：\n\n"
            + "\n\n".join(outputs),
            max_output_tokens=1200,
        )
        final_text = f"Jasmine 整合：\n\n{summary}" if summary else "\n\n".join(outputs)
        set_last_content(context, final_text, limit=12000)
        await send_long(update, final_text)

        if _wants_pdf(request):
            from commands.content import create_pdf_document

            await update.message.reply_text("Jasmine 已整合好，我而家交俾 Tiffany 生成 PDF。")
            await create_pdf_document(update, final_text)
        if _wants_slides(request):
            from commands.content import create_slides_document

            await update.message.reply_text("Jasmine 已整合好，我而家交俾 Tiffany 生成 PowerPoint。")
            await create_slides_document(update, final_text)
        if _wants_landing_page(request):
            from commands.content import create_landing_page_document

            await update.message.reply_text("Jasmine 已整合好，我而家交俾 Tiffany 生成 Landing Page。")
            await create_landing_page_document(update, final_text)


@private_only
async def agent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "用法：/agent [員工名] [任務]\n"
            "員工：Jasmine / Tiffany / Kelvin / Leo / Emily / Alan / Dixon / Sharon / Dorothy\n\n"
            "例：/agent Sharon 幫我設計痛症廣告受眾"
        )
        return

    full_request = " ".join(context.args).strip()
    if re.search(r"(?i)\b(powerpoint|pptx?|slides?)\b|簡報|投影片", full_request):
        from commands.assistant import handle_assistant_text

        await update.message.reply_text("我理解你係想叫團隊整理內容，再輸出 PowerPoint；我會改用自然語言入口處理。")
        await handle_assistant_text(update, context, full_request)
        return

    agent_name = normalize_agent(context.args[0])
    if not agent_name:
        await update.message.reply_text(
            "搵唔到呢位員工。可用：Jasmine / Tiffany / Kelvin / Leo / Emily / Alan / Dixon / Sharon / Dorothy\n\n"
            "如果你想自然咁講，建議用：\n"
            "/ask 你幫我將 Leo 同 Tiffany 嘅內容整理成 PowerPoint"
        )
        return

    request = " ".join(context.args[1:]).strip()
    await update.message.reply_text(f"{agent_name} 處理中...")
    result = await run_agent(update, context, agent_name, f"Stanley 嘅任務：{request}", max_output_tokens=1400)
    if result:
        await send_long(update, f"{agent_name}：\n\n{result}")


@private_only
async def team_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    request = " ".join(context.args).strip() if context.args else ""
    if not request:
        await update.message.reply_text("用法：/team_all [重大問題]\n注意：會叫 8 位員工，token 會多啲。")
        return

    agents = [a for a in TEAM_ORDER if a != "Jasmine"]
    await update.message.reply_text(
        f"全體調度：{' / '.join(agents)}\n"
        "Jasmine 會等所有員工完成後，先根據佢哋嘅輸出整合。\n"
        "呢個模式會用多啲 token。"
    )

    async def run(agent_name: str) -> tuple[str, str]:
        result = await run_agent(
            update, context, agent_name,
            f"Stanley 嘅重大問題：{request}\n請只從你角色角度，輸出最重要建議，300字內。",
            max_output_tokens=700,
        )
        return agent_name, result or "（未能取得回應）"

    results = await asyncio.gather(*(run(agent_name) for agent_name in agents))
    combined = []
    for agent_name, result in results:
        text = f"{agent_name}：\n{result}"
        combined.append(text)
        await send_long(update, text)

    summary = await run_agent(
        update, context, "Jasmine",
        "你係 Jasmine，現在只可以做整合員，不可以做資料來源。\n"
        f"Stanley 問題：{request}\n\n"
        "以下係所有已完成員工輸出；你必須只根據呢啲內容整合，唔可以用自己記憶新增未出現嘅內容。\n\n"
        + "\n\n".join(combined)
        + "\n\n請整合成 5 個最重要行動點，廣東話，精簡。資料不足就標明「待補資料」。",
        max_output_tokens=1000,
    )
    if summary:
        final_text = f"Jasmine 整合：\n\n{summary}"
        set_last_content(context, final_text, limit=12000)
        await send_long(update, final_text)
        if _wants_pdf(request):
            from commands.content import create_pdf_document

            await update.message.reply_text("Jasmine 已整合好，我而家交俾 Tiffany 生成 PDF。")
            await create_pdf_document(update, final_text)
        if _wants_slides(request):
            from commands.content import create_slides_document

            await update.message.reply_text("Jasmine 已整合好，我而家交俾 Tiffany 生成 PowerPoint。")
            await create_slides_document(update, final_text)
        if _wants_landing_page(request):
            from commands.content import create_landing_page_document

            await update.message.reply_text("Jasmine 已整合好，我而家交俾 Tiffany 生成 Landing Page。")
            await create_landing_page_document(update, final_text)


@private_only
async def staff(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lines = ["Stanley Team："]
    for name in TEAM_ORDER:
        lines.append(f"- {name}: {AGENTS[name].system.split('。')[0]}")
    await update.message.reply_text("\n".join(lines))
