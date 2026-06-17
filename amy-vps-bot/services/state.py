from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from telegram.ext import ContextTypes


logger = logging.getLogger(__name__)

STATE_DIR = Path(os.getenv("AMY_BOT_STATE_DIR", "/root/amy-vps-bot/state"))
LAST_CONTENT_FILE = STATE_DIR / "last_content.json"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception as exc:
        logger.warning("Failed to read state file %s: %s", path, exc)
    return {}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(path)
    except Exception as exc:
        logger.warning("Failed to write state file %s: %s", path, exc)


def load_last_content() -> str:
    data = _read_json(LAST_CONTENT_FILE)
    value = data.get("last_content", "")
    return value if isinstance(value, str) else ""


def save_last_content(value: str) -> None:
    _write_json(LAST_CONTENT_FILE, {"last_content": value})


def bootstrap_bot_data(bot_data: dict[str, Any]) -> None:
    if not bot_data.get("last_content"):
        loaded = load_last_content()
        if loaded:
            bot_data["last_content"] = loaded


def get_last_content(context: ContextTypes.DEFAULT_TYPE) -> str:
    value = context.bot_data.get("last_content", "")
    if isinstance(value, str) and value:
        return value
    loaded = load_last_content()
    if loaded:
        context.bot_data["last_content"] = loaded
    return loaded


def set_last_content(context: ContextTypes.DEFAULT_TYPE, value: str, *, limit: int = 20000) -> str:
    clipped = (value or "")[-limit:]
    context.bot_data["last_content"] = clipped
    save_last_content(clipped)
    return clipped
