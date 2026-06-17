from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _csv_ints(value: str) -> set[int]:
    ids: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if not item or _is_placeholder(item):
            continue
        try:
            ids.add(int(item))
        except ValueError:
            continue
    return ids


def _is_placeholder(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith(("paste_", "replace_with_", "your_")) or "here" in lowered


def _clean_secret(value: str) -> str:
    value = value.strip()
    if _is_placeholder(value):
        return ""
    return value


@dataclass(frozen=True)
class SettingsV2:
    telegram_bot_token: str
    allowed_user_ids: set[int]
    openrouter_api_key: str
    openrouter_model_fast: str
    openrouter_model_vision: str
    openai_api_key: str
    openai_image_model: str
    bot_name: str

    @classmethod
    def from_env(cls) -> "SettingsV2":
        return cls(
            telegram_bot_token=_clean_secret(os.getenv("TELEGRAM_BOT_TOKEN", "")),
            allowed_user_ids=_csv_ints(os.getenv("ALLOWED_TELEGRAM_USER_IDS", "")),
            openrouter_api_key=_clean_secret(os.getenv("OPENROUTER_API_KEY", "")),
            openrouter_model_fast=os.getenv("OPENROUTER_MODEL_FAST", "~openai/gpt-latest"),
            openrouter_model_vision=os.getenv("OPENROUTER_MODEL_VISION", "~openai/gpt-latest"),
            openai_api_key=_clean_secret(os.getenv("OPENAI_API_KEY", "")),
            openai_image_model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2"),
            bot_name=os.getenv("BOT_NAME", "Amy V2"),
        )

    def startup_errors(self) -> list[str]:
        errors: list[str] = []
        if not self.telegram_bot_token:
            errors.append("TELEGRAM_BOT_TOKEN is missing or still a placeholder.")
        if not self.allowed_user_ids:
            errors.append("ALLOWED_TELEGRAM_USER_IDS is missing or invalid.")
        if not (self.openrouter_api_key or self.openai_api_key):
            errors.append("Set OPENROUTER_API_KEY or OPENAI_API_KEY.")
        return errors


settings_v2 = SettingsV2.from_env()
