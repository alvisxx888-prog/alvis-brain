#!/usr/bin/env python3
import os
import json
import re
import subprocess
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ALLOWED_USER_ID = 193060672
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CLAUDE_PATH = "/root/.local/bin/claude"

AGENT_PROMPTS = {
    "Amy": """你係 Amy，Stanley 團隊嘅秘書同指揮中樞（v2.0）。
職責：分流任務、協調 Agent、追蹤進度、向 Stanley（即 Alvis）匯報。
風格：廣東話，專業隨和，簡潔有力。
授權邊界：$0成本決定自主執行；預算支出需 Stanley 確認；Stanley 不在線 >2小時可代決 P0 任務（<$500）。""",

    "Anna": """你係 Anna，Stanley 團隊廣告設計師兼文稿師（v2.0）。
專長：IG帖文案、Reels腳本、廣告素材、小紅書格式、A/B 測試素材。
業務線：痛症（品牌 Alvis）/ 美容（品牌 Stanley）。
Reels 腳本結構：0-3秒 Hook → 3-15秒衝突 → 15-45秒解方 → 45-60秒 CTA。
廣告素材規格：標題 ≤27字，正文 ≤125字，輸出 A/B 兩版。
輸出具體落地，廣東話。""",

    "Leo": """你係 Leo，Stanley 團隊市場分析師（v2.0）。
專長：競品監測（美容線每週一、痛症線每週三）、行業爆款趨勢、情報報告。
監測對象：美容線（beautysignaturehk 等）/ 痛症線（物理治療師 KOL、痛症顧問）。
輸出：結構化報告，有數據支撐，有建議行動，廣東話。""",

    "Toxic": """你係 Toxic，Stanley 團隊自動化工程師（v2.0）。
專長：流程自動化、WhatsApp Business、Meta Ads 自動規則、排程工具、Apify 腳本。
自動規則參考：CPC >$5 連續3日 → 自動暫停；ER >3% → 自動加預算20%。
輸出有具體步驟同工具推薦，廣東話。""",

    "Small": """你係 Small，Stanley 團隊首席商業策略官（v2.0）。
專長：業務方向定位、月度策略 Brief、資源分配（起盤期：痛症60% / 美容40%）、風險預警。
強制規則：必須主動指出盲點，挑戰 Stanley，唔只附和。
每份建議必含：具體行動、風險提示、資源分配建議。廣東話。""",

    "Tony": """你係 Tony，Stanley 團隊客戶營運專員（v2.0）。
專長：客戶跟進腳本、諮詢→成交轉化（目標 ≥30%）、成效追蹤（3/7/21/42日）、Testimonial 收集。
痛症線：謹慎，信任感優先，唔賣嘢先問問題建立專業感。
美容線：自信，效果展示為主。
輸出有具體話術，廣東話。""",

    "Rex": """你係 Rex，Stanley 團隊廣告投放專員（v2.0）。
專長：Meta Ads 全流程（設定→投放→監測→優化→報告）。
美容線受眾：女性 20-45 / HK / 興趣（護膚/美容/自我護理）。
痛症線受眾：全性別 30-60 / HK / 興趣（健康/痛症/物理治療）。
KPI 目標：CTR >1.5%，CPL <$30 HKD，ROAS >3。
輸出有具體數字同行動計劃，廣東話。""",

    "Mia": """你係 Mia，Stanley 團隊數據追蹤師（v2.0）。
專長：IG 有機數據分析、廣告 ROI 追蹤、客戶轉化漏斗分析、月度業績健康報告。
漏斗模型：觸及 → 關注 → 私訊 → 諮詢 → 成交。
每月15號出漏斗診斷報告。
輸出有數據、有洞察、有可執行建議，廣東話。""",
}

AMY_DISPATCH_SYSTEM = """你係 Amy，Stanley 團隊秘書同指揮中樞。
Stanley 發咗指令，你需要分析並決定分派給哪些 Agent。

可用 Agent：
- Anna：廣告設計 & 文稿（IG帖、Reels腳本、廣告素材、小紅書）
- Leo：市場分析（競品監測、行業趨勢、情報報告）
- Toxic：自動化（系統設定、WhatsApp、排程、Meta 自動規則）
- Small：商業策略（方向定位、策略 Brief、風險預警）
- Tony：客戶營運（跟進腳本、成交轉化、客戶關係）
- Rex：廣告投放（Meta Ads 設定、A/B 測試、廣告優化）
- Mia：數據追蹤（IG 數據、廣告 ROI、漏斗分析）

分派規則：
- 簡單對話、問候、一般策略討論 → Amy 直接回答，唔分派
- 有具體創作/分析/執行任務 → 分派給相關 Agent
- 複合任務 → 同時分派多個 Agent 並行處理

必須輸出純 JSON，唔可以有任何其他文字：

需要分派時：
{"amy_message": "Amy 對 Stanley 說嘅話（確認收到 + 說明分派計劃）", "dispatch": [{"agent": "AgentName", "task": "具體任務描述"}], "direct_reply": null}

Amy 直接回答時（唔分派）：
{"amy_message": null, "dispatch": [], "direct_reply": "Amy 直接回覆嘅完整內容"}"""

AGENT_EMOJI = {
    "Amy":   "👩‍💼",
    "Anna":  "🎨",
    "Leo":   "📊",
    "Toxic": "⚡",
    "Small": "🧠",
    "Tony":  "🤝",
    "Rex":   "📢",
    "Mia":   "📈",
}

executor = ThreadPoolExecutor(max_workers=8)
conversation_history: dict[int, list] = {}
MAX_HISTORY = 10


def run_claude(prompt: str, timeout: int = 150) -> str:
    result = subprocess.run(
        [CLAUDE_PATH, "-p", prompt],
        capture_output=True, text=True, timeout=timeout,
        env={**os.environ, "HOME": "/root"},
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    logger.error(f"Claude error: {result.stderr[:200]}")
    return f"[出錯：{result.stderr[:100]}]"


def agent_call(agent_name: str, task: str) -> tuple[str, str]:
    prompt = (
        f"{AGENT_PROMPTS[agent_name]}\n\n"
        f"---\n\n"
        f"Stanley 交俾你嘅任務：\n{task}\n\n"
        f"請根據你嘅角色同專長，提供具體、可執行嘅回覆。"
    )
    return agent_name, run_claude(prompt)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    conversation_history[ALLOWED_USER_ID] = []
    await update.message.reply_text(
        "Stanley，我係 Amy。\n\n"
        "全體 Agent 就位：Anna / Leo / Toxic / Small / Tony / Rex / Mia\n\n"
        "有咩吩咐？"
    )


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    conversation_history[ALLOWED_USER_ID] = []
    await update.message.reply_text("記憶清除，重新開始。")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    h = conversation_history.get(ALLOWED_USER_ID, [])
    agents = " / ".join(AGENT_PROMPTS.keys())
    await update.message.reply_text(
        f"系統狀態：正常\n"
        f"對話記憶：{len(h)} 條\n"
        f"Agent 團隊：{agents}"
    )


async def send_long(update: Update, text: str):
    for i in range(0, len(text), 4096):
        await update.message.reply_text(text[i: i + 4096])


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    user_message = update.message.text
    if not user_message:
        return

    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    history = conversation_history.setdefault(ALLOWED_USER_ID, [])
    loop = asyncio.get_event_loop()

    # Step 1: Amy dispatches
    history_text = ""
    for msg in history[-MAX_HISTORY:]:
        role = "Stanley" if msg["role"] == "user" else "Amy"
        history_text += f"{role}: {msg['content']}\n\n"

    dispatch_prompt = (
        f"{AMY_DISPATCH_SYSTEM}\n\n"
        f"{'對話歷史：' + chr(10) + history_text if history_text else ''}"
        f"Stanley 最新指令：{user_message}"
    )
    raw = await loop.run_in_executor(executor, run_claude, dispatch_prompt)

    try:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        data = json.loads(match.group()) if match else {}
    except Exception:
        logger.error(f"JSON parse failed: {raw[:300]}")
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": raw})
        await send_long(update, f"{AGENT_EMOJI['Amy']} Amy：{raw}")
        return

    # Direct reply
    if data.get("direct_reply"):
        reply = f"{AGENT_EMOJI['Amy']} Amy：{data['direct_reply']}"
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})
        await send_long(update, reply)
        return

    dispatches = [d for d in data.get("dispatch", []) if d.get("agent") in AGENT_PROMPTS]
    amy_msg = data.get("amy_message", "")

    if not dispatches:
        reply = f"{AGENT_EMOJI['Amy']} Amy：{amy_msg or raw}"
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})
        await send_long(update, reply)
        return

    # Step 2: Send Amy's dispatch message immediately
    agents_names = "、".join(d["agent"] for d in dispatches)
    await send_long(update, f"{AGENT_EMOJI['Amy']} Amy：{amy_msg}\n（調度中：{agents_names}）")

    # Step 3: Run all agents in parallel
    tasks = [
        loop.run_in_executor(executor, agent_call, d["agent"], d["task"])
        for d in dispatches
    ]
    results = list(await asyncio.gather(*tasks))

    # Step 4: Send each agent's response as a separate message
    full_results = ""
    for agent_name, reply_text in results:
        emoji = AGENT_EMOJI.get(agent_name, "🤖")
        msg = f"{emoji} {agent_name}：\n{reply_text}"
        full_results += msg + "\n\n"
        await send_long(update, msg)

    # Step 5: Amy consolidates
    consolidate_prompt = (
        f"{AGENT_PROMPTS['Amy']}\n\n"
        f"Stanley 嘅原始指令：{user_message}\n\n"
        f"各 Agent 回覆如下：\n{full_results}\n\n"
        f"請整合以上所有 Agent 嘅回覆，去除重複內容，"
        f"用清晰格式匯報俾 Stanley，突出最重要嘅行動點。"
    )
    summary = await loop.run_in_executor(executor, run_claude, consolidate_prompt)
    summary_msg = f"{AGENT_EMOJI['Amy']} Amy 整合報告：\n{summary}"
    await send_long(update, summary_msg)

    full_reply = f"{AGENT_EMOJI['Amy']} Amy：{amy_msg}\n\n{full_results}\n{summary_msg}"
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": full_reply})


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Multi-Agent Bot 啟動，等待 Stanley 指令...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
