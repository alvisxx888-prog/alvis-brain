from __future__ import annotations

import asyncio
import io
import json
import re
import tempfile
import os

from telegram import Update
from telegram.ext import ContextTypes

from app.config import settings
from app.formatting import send_long
from app.security import private_only
from services.ai import ask_agent, generate_image
from services.files import extract_text, make_pdf, make_pptx
from services.state import get_last_content, set_last_content

AI_TIMEOUT_SECONDS = 240
AGENT_REFERENCE_WORDS = {
    "jasmine",
    "tiffany",
    "leo",
    "kelvin",
    "emily",
    "alan",
    "dixon",
    "sharon",
    "dorothy",
}
RECENT_REFERENCE_WORDS = [
    "整合",
    "合併",
    "總結",
    "上面",
    "以上",
    "啱啱",
    "剛才",
    "佢哋",
    "他們",
]


def _args(context: ContextTypes.DEFAULT_TYPE) -> str:
    return " ".join(context.args).strip() if context.args else ""


def _provider_output_budget(openai_tokens: int, openrouter_tokens: int) -> int:
    return openai_tokens if settings.openai_api_key else openrouter_tokens


def _looks_like_recent_output_reference(text: str) -> bool:
    lowered = text.lower()
    if any(word in lowered for word in AGENT_REFERENCE_WORDS):
        return True
    if any(word in text for word in RECENT_REFERENCE_WORDS):
        return True
    return "+" in text or "＋" in text


def _pdf_source_from_request(request: str, last_content: str) -> str:
    if request and last_content and _looks_like_recent_output_reference(request):
        return (
            f"用戶要求：{request}\n\n"
            "請整合以下最近由團隊輸出嘅內容，去重、補齊邏輯，整理成一份 PDF 文件。\n\n"
            f"最近內容：\n{last_content}"
        )
    return request or last_content


def _slides_source_from_request(request: str, last_content: str) -> str:
    if request and last_content and _looks_like_recent_output_reference(request):
        return (
            f"用戶要求：{request}\n\n"
            "請整合以下最近由團隊輸出嘅內容，去重、補齊邏輯，整理成一份 PowerPoint 簡報。\n\n"
            f"最近內容：\n{last_content}"
        )
    return request or last_content


def _landing_source_from_request(request: str, last_content: str) -> str:
    if request and last_content and _looks_like_recent_output_reference(request):
        return (
            f"用戶要求：{request}\n\n"
            "請整合以下最近由團隊輸出嘅內容，去重、補齊邏輯，整理成一頁 Landing Page。\n\n"
            f"最近內容：\n{last_content}"
        )
    return request or last_content


async def _ask_agent(agent_name: str, task: str, *, heavy: bool = False, max_output_tokens: int = 1200) -> str:
    return await asyncio.wait_for(
        asyncio.to_thread(
            ask_agent,
            agent_name,
            task,
            heavy=heavy,
            max_output_tokens=max_output_tokens,
        ),
        timeout=AI_TIMEOUT_SECONDS,
    )


@private_only
async def caption(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    topic = _args(context)
    if not topic:
        await update.message.reply_text("用法：/caption [描述]\n例：/caption 痛症初診優惠，免費諮詢，本月限定")
        return
    await update.message.reply_text("Tiffany 撰寫中...")
    try:
        result = await _ask_agent(
            "Tiffany",
            f"幫 Stanley 寫帖文 caption。主題：{topic}\n"
            "輸出兩版：IG 版、小紅書版。每版要有 hook、正文、CTA、hashtags。",
        )
    except asyncio.TimeoutError:
        await update.message.reply_text("AI 生成超時，可能係 OpenAI/API 或 VPS 網絡卡住。請稍後再試，或者打 /logs 睇最近錯誤。")
        return
    except Exception as exc:
        await update.message.reply_text(f"AI 生成失敗：{exc}\n可以打 /logs 睇詳細記錄。")
        return
    await send_long(update, f"Tiffany：\n\n{result}")


@private_only
async def reel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    topic = _args(context)
    if not topic:
        await update.message.reply_text("用法：/reel [主題]")
        return
    await update.message.reply_text("Tiffany 寫 Reels 腳本中...")
    result = await _ask_agent(
        "Tiffany",
        f"幫 Stanley 寫 60 秒 Reels 腳本。主題：{topic}\n"
        "格式：0-3秒 Hook / 3-15秒痛點 / 15-45秒解方 / 45-60秒CTA。"
        "每段包含旁白、畫面、字幕。",
    )
    await send_long(update, f"Reels 腳本：\n\n{result}")


@private_only
async def copy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    request = _args(context)
    if not request:
        await update.message.reply_text("用法：/copy [需求]\n例：/copy WhatsApp 跟進訊息，客人上星期做完療程")
        return
    await update.message.reply_text("Tiffany 寫文案中...")
    result = await _ask_agent("Tiffany", f"Stanley 需要以下文案：{request}\n請輸出可直接使用嘅最終版本。")
    await send_long(update, f"文案：\n\n{result}")


@private_only
async def landingpage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    request = _args(context)
    last_content = get_last_content(context)
    description = _landing_source_from_request(request, last_content)
    if not description:
        await update.message.reply_text("用法：/landingpage [描述]\n例：/landingpage 痛症治療，免費初診，目標30-60歲")
        return
    await create_landing_page_document(update, description)


async def create_landing_page_document(update: Update, description: str) -> None:
    await update.message.reply_text("Tiffany 生成 Landing Page HTML 中...")
    html = await _ask_agent(
        "Tiffany",
        "幫 Stanley 將以下已提供資料整理成完整單頁 Landing Page HTML。\n"
        "資料來源規則：只可使用下方資料入面已出現嘅內容；唔可以憑記憶新增 offer、價錢、數字、案例、療效、承諾或策略。"
        "如果資料不足，請用「待補資料」作 placeholder。\n"
        "要求：繁體中文、手機優先、可直接開啟、包含 Hero/痛點/服務/見證/FAQ/CTA。"
        "只輸出 HTML，不要 markdown fence。\n\n"
        f"描述：{description[:5000]}",
        max_output_tokens=3500,
    )
    match = re.search(r"<!doctype html.*?</html>|<html.*?</html>", html, re.DOTALL | re.IGNORECASE)
    html = match.group(0) if match else html
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        path = f.name
    try:
        with open(path, "rb") as f:
            await update.message.reply_document(document=f, filename="landing_page.html", caption="Landing Page 完成。")
    finally:
        os.unlink(path)


@private_only
async def imagine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = _args(context)
    if not prompt:
        await update.message.reply_text("用法：/imagine [描述]\n例：/imagine 香港痛症診所 IG 廣告圖，專業溫暖")
        return
    await update.message.reply_text("Tiffany 生成圖片 + prompts 中...")
    if settings.openai_api_key:
        try:
            img = await asyncio.to_thread(generate_image, prompt)
            await update.message.reply_photo(photo=io.BytesIO(img), caption=f"AI 圖片：{prompt}")
        except Exception:
            await update.message.reply_text(
                "圖片生成失敗：/image 生成實圖需要有效 OPENAI_API_KEY。"
                "我會先幫你生成可複製 prompts。"
            )
    else:
        await update.message.reply_text("未設定 OPENAI_API_KEY，先用 OpenRouter 幫你生成可複製 prompts。")

    try:
        prompts = await _ask_agent(
            "Tiffany",
            f"根據呢個需求生成 3 個高質英文 AI image prompts，適合 IG/廣告：{prompt}",
            max_output_tokens=900,
        )
    except Exception:
        await update.message.reply_text("Prompts 生成都失敗：請檢查 OPENROUTER_API_KEY 或 OPENAI_API_KEY，再重開 bot。")
        return
    await send_long(update, f"可複製 prompts：\n\n{prompts}")


@private_only
async def pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # PTB v21+ routes caption commands here too — extract the attached doc if present
    if update.message and update.message.document:
        doc = update.message.document
        file = await context.bot.get_file(doc.file_id)
        data = await file.download_as_bytearray()
        text = extract_text(bytes(data), doc.mime_type or "", doc.file_name or "")
        if text.strip():
            set_last_content(context, text, limit=12000)

    request = _args(context)
    last_content = get_last_content(context)
    description = _pdf_source_from_request(request, last_content)
    if not description:
        await update.message.reply_text("用法：/pdf [描述]\n或者先上載/貼上一段內容，再打 /pdf。")
        return
    await create_pdf_document(update, description)


async def create_pdf_document(update: Update, description: str) -> None:
    await update.message.reply_text("Jasmine 會先將來源內容整理成結構化簡報，再交俾 Tiffany 做 PDF。")
    brief = await _ask_agent(
        "Jasmine",
        "你係 Jasmine，現在只可以做結構化簡報員，不可以做資料來源。\n"
        "請只根據下方已提供資料，整理成俾 Tiffany 製作 PDF 用嘅清晰 brief。\n"
        "輸出格式：① 文件目標 ② 已有重點 ③ 建議章節 ④ 必須保留內容 ⑤ 待補資料。\n"
        "唔可以憑記憶新增 offer、價錢、數字、案例、療效、承諾或策略；資料不足就寫「待補資料」。\n\n"
        f"資料：\n{description[:12000]}",
        heavy=True,
        max_output_tokens=_provider_output_budget(1800, 1200),
    )
    content = await _ask_agent(
        "Tiffany",
        "你而家係文件整理員，任務係根據 Jasmine brief 同原始資料整理成一份 PDF 內容，唔係重新創作。\n"
        "要求：\n"
        "1. 只可使用下方資料入面已出現嘅內容；唔可以憑記憶新增 offer、價錢、數字、案例、療效、承諾或策略。\n"
        "2. 第一行係清晰標題。\n"
        "3. 章節用 # 開頭，內容要有層次；可以去重、排序、合併相同意思、補自然過渡。\n"
        "4. 繁體中文／廣東話自然書面語。\n"
        "5. 如果資料不足以支撐某個章節，寫「待補資料」，唔好自己作。\n"
        "6. 保留 Leo / Tiffany / 其他員工已提出嘅重點同下一步，唔好換成另一套建議。\n"
        "7. 目標長度 1500-2500 字；如果資料不足，寧願用「待補資料」標示，唔好填充作大。\n\n"
        f"Jasmine brief：\n{brief}\n\n原始資料：\n{description[:12000]}",
        heavy=True,
        max_output_tokens=_provider_output_budget(3800, 2800),
    )
    lines = content.splitlines()
    title = (lines[0].lstrip("#").strip() if lines else "document") or "document"
    body = "\n".join(lines[1:]) if len(lines) > 1 else content
    pdf_bytes = make_pdf(title, body)
    await update.message.reply_document(document=io.BytesIO(pdf_bytes), filename="amy_output.pdf", caption=f"PDF 完成：{title}")


@private_only
async def slides(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # PTB v21+ routes caption commands here too — extract the attached doc if present
    if update.message and update.message.document:
        doc = update.message.document
        file = await context.bot.get_file(doc.file_id)
        data = await file.download_as_bytearray()
        text = extract_text(bytes(data), doc.mime_type or "", doc.file_name or "")
        if text.strip():
            set_last_content(context, text, limit=12000)

    request = _args(context)
    last_content = get_last_content(context)
    description = _slides_source_from_request(request, last_content)
    if not description:
        await update.message.reply_text("用法：/slides [描述]\n或者先上載/貼上一段內容，再打 /slides。")
        return
    await create_slides_document(update, description)


async def create_slides_document(update: Update, description: str) -> None:
    await update.message.reply_text("Jasmine 會先確認內容來源，再交俾 Tiffany 做簡報整理。")
    raw = await _ask_agent(
        "Tiffany",
        "你而家係簡報整理員，任務係將下方已提供資料整理成 PowerPoint JSON，唔係重新創作。\n"
        "資料來源規則：只可使用下方資料入面已出現嘅內容；唔可以憑記憶新增 offer、價錢、數字、案例、療效、承諾或策略。\n"
        "可以整理故事線、章節排序、重點取捨、去重同補自然過渡，但唔好輸出思考過程。\n"
        "每頁要有清晰標題，points 要具體、有行動性；如果資料不足，寫「待補資料」。\n"
        "只輸出 JSON，不要 markdown。\n"
        '格式：{"title":"...","slides":[{"title":"...","points":["...","..."]}]}\n'
        f"資料：\n{description[:12000]}",
        heavy=True,
        max_output_tokens=_provider_output_budget(3500, 1600),
    )
    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(match.group(0) if match else raw)
        pptx_bytes = make_pptx(data["title"], data["slides"])
    except Exception:
        await send_long(update, f"PowerPoint 內容解析失敗，先回傳文字版：\n\n{raw}")
        return
    await update.message.reply_document(document=io.BytesIO(pptx_bytes), filename="amy_slides.pptx", caption="PowerPoint 完成。")
