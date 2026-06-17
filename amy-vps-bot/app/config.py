from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _csv_ints(value: str) -> set[int]:
    ids: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if item:
            try:
                ids.add(int(item))
            except ValueError as exc:
                raise RuntimeError(
                    "ALLOWED_TELEGRAM_USER_IDS must be comma-separated Telegram numeric IDs."
                ) from exc
    return ids


def _is_placeholder(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith(("paste_", "replace_with_", "your_")) or "here" in lowered


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    allowed_user_ids: set[int]
    openai_api_key: str
    openrouter_api_key: str
    model_fast: str
    model_heavy: str
    image_model: str
    local_whisper_model: str
    openrouter_model_fast: str
    openrouter_model_heavy: str
    bot_name: str
    low_token_mode: bool
    daily_briefing_enabled: bool
    daily_briefing_hour: int
    daily_briefing_minute: int
    hermes_service_name: str
    bot_service_name: str
    apify_api_token: str
    gamma_api_key: str

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        allowed = os.getenv("ALLOWED_TELEGRAM_USER_IDS", "").strip()
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()

        missing = []
        if not token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not allowed:
            missing.append("ALLOWED_TELEGRAM_USER_IDS")
        if not openai_key and not openrouter_key:
            missing.append("OPENAI_API_KEY or OPENROUTER_API_KEY")
        if missing:
            raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
        placeholders = []
        if _is_placeholder(token):
            placeholders.append("TELEGRAM_BOT_TOKEN")
        if _is_placeholder(allowed):
            placeholders.append("ALLOWED_TELEGRAM_USER_IDS")
        if openai_key and _is_placeholder(openai_key):
            openai_key = ""
        if openrouter_key and _is_placeholder(openrouter_key):
            openrouter_key = ""
        if not openai_key and not openrouter_key:
            placeholders.append("OPENAI_API_KEY or OPENROUTER_API_KEY")
        if placeholders:
            raise RuntimeError(f"Please replace placeholder env vars: {', '.join(placeholders)}")

        return cls(
            telegram_bot_token=token,
            allowed_user_ids=_csv_ints(allowed),
            openai_api_key=openai_key,
            openrouter_api_key=openrouter_key,
            model_fast=os.getenv("OPENAI_MODEL_FAST", "gpt-4.1-mini"),
            model_heavy=os.getenv("OPENAI_MODEL_HEAVY", "gpt-4.1"),
            image_model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2"),
            local_whisper_model=os.getenv("LOCAL_WHISPER_MODEL", "base"),
            openrouter_model_fast=os.getenv("OPENROUTER_MODEL_FAST", "~openai/gpt-latest"),
            openrouter_model_heavy=os.getenv("OPENROUTER_MODEL_HEAVY", "~openai/gpt-latest"),
            bot_name=os.getenv("BOT_NAME", "Amy"),
            low_token_mode=os.getenv("LOW_TOKEN_MODE", "true").lower() in {"1", "true", "yes", "on"},
            daily_briefing_enabled=os.getenv("DAILY_BRIEFING_ENABLED", "false").lower()
            in {"1", "true", "yes", "on"},
            daily_briefing_hour=int(os.getenv("DAILY_BRIEFING_HOUR", "8")),
            daily_briefing_minute=int(os.getenv("DAILY_BRIEFING_MINUTE", "45")),
            hermes_service_name=os.getenv("HERMES_SERVICE_NAME", "hermes-agent"),
            bot_service_name=os.getenv("BOT_SERVICE_NAME", "amy-vps-bot"),
            apify_api_token=os.getenv("APIFY_API_TOKEN", "").strip(),
            gamma_api_key=os.getenv("GAMMA_API_KEY", "").strip(),
        )


settings = Settings.from_env()
