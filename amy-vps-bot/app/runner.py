from __future__ import annotations

import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from services.ai import ask_agent


async def run_agent(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    agent_name: str,
    task: str,
    *,
    max_output_tokens: int = 1200,
    heavy: bool = False,
    timeout: int = 240,
    heartbeat: int = 45,
) -> str | None:
    """Run ask_agent in a thread with typing indicator, heartbeat, and timeout."""
    chat_id = update.effective_chat.id

    async def _keep_typing() -> None:
        while True:
            try:
                await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            except Exception:
                pass
            await asyncio.sleep(4)

    async def _heartbeat() -> None:
        await asyncio.sleep(20)
        try:
            await update.message.reply_text("我仲處理緊，俾我少少時間。")
        except Exception:
            pass
        await asyncio.sleep(40)
        try:
            await update.message.reply_text("仲喺度，唔係冇反應，啱啱整理緊結果。")
        except Exception:
            pass
        await asyncio.sleep(30)
        try:
            await update.message.reply_text("呢個任務有啲耐，如果最後冇出結果，你可以再 send 一次，我會接住做。")
        except Exception:
            pass

    typing_task = asyncio.create_task(_keep_typing())
    hb_task = asyncio.create_task(_heartbeat())
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(ask_agent, agent_name, task, heavy=heavy, max_output_tokens=max_output_tokens),
            timeout=timeout,
        )
        return result
    except asyncio.TimeoutError:
        try:
            await update.message.reply_text("我試咗一陣都未完成，可能上游 AI 太慢。你可以再 send 一次，我會重新接住做。")
        except Exception:
            pass
        return None
    except Exception as exc:
        try:
            await update.message.reply_text(f"我收到你嘅意思，但處理時出咗錯：{exc}")
        except Exception:
            pass
        return None
    finally:
        typing_task.cancel()
        hb_task.cancel()
