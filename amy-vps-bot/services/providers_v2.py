from __future__ import annotations

import base64
from dataclasses import dataclass
from importlib.util import find_spec

from openai import OpenAI

from app.config_v2 import settings_v2


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
SYSTEM_PROMPT = (
    "你係 Amy V2，Stanley 嘅私人小助手。"
    "用廣東話回答，直接、有條理、可執行。"
    "如果係設定或 API 問題，先講原因，再講下一步。"
)


@dataclass(frozen=True)
class ProviderStatus:
    text_provider: str
    vision_provider: str
    image_provider: str
    voice_provider: str


def _openrouter_client() -> OpenAI:
    return OpenAI(
        api_key=settings_v2.openrouter_api_key,
        base_url=OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": "https://local.amy-v2",
            "X-OpenRouter-Title": "Amy V2 Telegram Bot",
        },
    )


def _openai_client() -> OpenAI:
    return OpenAI(api_key=settings_v2.openai_api_key)


def provider_status() -> ProviderStatus:
    text = "OpenAI base" if settings_v2.openai_api_key else ("OpenRouter fallback" if settings_v2.openrouter_api_key else "未設定")
    vision = "OpenAI base" if settings_v2.openai_api_key else ("OpenRouter fallback" if settings_v2.openrouter_api_key else "未設定")
    image = "OpenAI" if settings_v2.openai_api_key else "未設定 OPENAI_API_KEY"
    voice = "OpenAI Whisper API" if settings_v2.openai_api_key else (
        "本機 Whisper 免費" if find_spec("faster_whisper") is not None else "未設定 OPENAI_API_KEY / 未安裝本機 Whisper"
    )
    return ProviderStatus(text, vision, image, voice)


def status_text() -> str:
    status = provider_status()
    text_ok = "✅" if status.text_provider != "未設定" else "⚠️"
    vision_ok = "✅" if status.vision_provider != "未設定" else "⚠️"
    image_ok = "✅" if settings_v2.openai_api_key else "⚠️"
    voice_ok = "✅" if settings_v2.openai_api_key or find_spec("faster_whisper") is not None else "⚠️"
    return (
        "AI 狀態：\n"
        f"- 文字分析：{status.text_provider} {text_ok}\n"
        f"- 圖片理解：{status.vision_provider} {vision_ok}\n"
        f"- AI 整圖：{status.image_provider} {image_ok}\n"
        f"- 語音轉文字：{status.voice_provider} {voice_ok}\n"
        f"- 文字模型：{'OpenAI default' if settings_v2.openai_api_key else settings_v2.openrouter_model_fast}\n"
        f"- 圖片理解模型：{'OpenAI default' if settings_v2.openai_api_key else settings_v2.openrouter_model_vision}\n"
        f"- 整圖模型：{settings_v2.openai_image_model}\n\n"
        "目前運作：文字/圖片理解優先用 OpenAI base；冇 OpenAI key 先用 OpenRouter fallback。整圖需要 OPENAI_API_KEY；語音可用本機 Whisper 免費 fallback。"
    )


def answer_text(text: str, *, max_tokens: int = 900) -> str:
    if settings_v2.openai_api_key:
        response = _openai_client().responses.create(
            model="gpt-4.1-mini",
            instructions=SYSTEM_PROMPT,
            input=text,
            max_output_tokens=max_tokens,
        )
        return response.output_text.strip()

    if settings_v2.openrouter_api_key:
        response = _openrouter_client().chat.completions.create(
            model=settings_v2.openrouter_model_fast,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            max_tokens=max_tokens,
        )
        return (response.choices[0].message.content or "").strip()

    raise RuntimeError("未設定 AI provider。請設定 OPENROUTER_API_KEY 或 OPENAI_API_KEY。")


def analyze_image(image_bytes: bytes, mime: str = "image/jpeg", prompt: str = "") -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    data_url = f"data:{mime};base64,{encoded}"
    user_text = prompt or "請分析呢張圖片，抽取文字，講重點同下一步。"

    if settings_v2.openai_api_key:
        response = _openai_client().responses.create(
            model="gpt-4.1-mini",
            instructions=SYSTEM_PROMPT,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": user_text},
                        {"type": "input_image", "image_url": data_url},
                    ],
                }
            ],
            max_output_tokens=1000,
        )
        return response.output_text.strip()

    if settings_v2.openrouter_api_key:
        response = _openrouter_client().chat.completions.create(
            model=settings_v2.openrouter_model_vision,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            max_tokens=1000,
        )
        return (response.choices[0].message.content or "").strip()

    raise RuntimeError("未設定 Vision provider。請設定 OPENROUTER_API_KEY 或 OPENAI_API_KEY。")


def test_ai() -> str:
    result = answer_text("用一句廣東話回覆：AI provider test ok。", max_tokens=80)
    return f"AI test 成功：\n{result}"
