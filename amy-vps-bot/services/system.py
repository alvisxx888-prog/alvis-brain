from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass

from app.config import settings


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    text: str


def _run(args: list[str], timeout: int = 20) -> CommandResult:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except Exception as exc:
        return CommandResult(False, f"執行失敗：{exc}")

    output = (result.stdout or result.stderr or "").strip()
    return CommandResult(result.returncode == 0, output[:3500] or "完成，沒有輸出。")


def system_status() -> str:
    load = os.getloadavg()
    disk = shutil.disk_usage("/")
    disk_used = disk.used / disk.total * 100
    lines = [
        "系統狀態：正常",
        f"Load average：{load[0]:.2f} / {load[1]:.2f} / {load[2]:.2f}",
        f"Disk：{disk_used:.1f}% used",
    ]

    result = _run(["systemctl", "is-active", settings.bot_service_name], timeout=8)
    status = result.text.strip() if result.text else "unknown"
    lines.append(f"{settings.bot_service_name}：{status}")

    return "\n".join(lines)


def service_logs(service_name: str, lines: int = 80) -> str:
    safe = {
        settings.hermes_service_name: settings.hermes_service_name,
        settings.bot_service_name: settings.bot_service_name,
    }
    if service_name not in safe:
        return "呢個 service 唔喺白名單，唔會讀取。"
    result = _run(["journalctl", "-u", safe[service_name], "-n", str(lines), "--no-pager"], timeout=20)
    return result.text


def restart_service(service_name: str) -> str:
    safe = {
        settings.hermes_service_name: settings.hermes_service_name,
        settings.bot_service_name: settings.bot_service_name,
    }
    if service_name not in safe:
        return "呢個 service 唔喺白名單，唔會重啟。"
    result = _run(["systemctl", "restart", safe[service_name]], timeout=20)
    if result.ok:
        return f"已重啟 {safe[service_name]}。"
    return f"重啟失敗：\n{result.text}"

