from __future__ import annotations

import base64
import tempfile
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path

from openai import OpenAI

from app.config import settings


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _openai_client() -> OpenAI:
    if not settings.openai_api_key:
        raise RuntimeError("呢個功能需要 OPENAI_API_KEY。")
    return OpenAI(api_key=settings.openai_api_key)


def _openrouter_client() -> OpenAI:
    return OpenAI(
        api_key=settings.openrouter_api_key,
        base_url=OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": "https://local.amy-vps-bot",
            "X-OpenRouter-Title": "Amy VPS Telegram Bot",
        },
    )


def _chat_client() -> OpenAI:
    if settings.openai_api_key:
        return _openai_client()
    return _openrouter_client()


def _chat_model(*, heavy: bool = False) -> str:
    if settings.openai_api_key:
        return settings.model_heavy if heavy else settings.model_fast
    return settings.openrouter_model_heavy if heavy else settings.openrouter_model_fast


@dataclass(frozen=True)
class Agent:
    name: str
    system: str
    model: str | None = None


AGENTS: dict[str, Agent] = {
    "Jasmine": Agent(
        "Jasmine",
        "你係 Jasmine，Stanley 團隊嘅秘書同指揮中樞（OpenAI base）。"
        "職責：分流任務、協調員工、追蹤進度、向 Stanley（即 Alvis）匯報。"
        "風格：廣東話，專業隨和，簡潔有力。"
        "授權邊界：$0成本決定自主執行；預算支出需 Stanley 確認；Stanley 不在線 >2小時可代決 P0 任務（<$500）。"
        "唔好自稱大型語言模型；如果係操作風險，先提醒。"
        "收到文件/圖片內容後，必須主動派員工產出具體成品，唔係只匯報分析。",
    ),
    "Tiffany": Agent(
        "Tiffany",
        "你係 Tiffany，Stanley 團隊廣告設計師兼文稿師。"
        "專長：IG帖文案、Reels腳本、廣告素材、小紅書格式、A/B 測試素材、Landing Page HTML、電郵模板。"
        "業務線：痛症（品牌 Alvis）/ 美容（品牌 Stanley）。"
        "輸出規格："
        "IG帖：emoji + hook + 正文 + CTA + hashtags（5-10個）；"
        "Reels腳本：0-3秒 Hook → 3-15秒衝突 → 15-45秒解方 → 45-60秒 CTA；"
        "廣告素材：標題 ≤27字，正文 ≤125字，輸出 A/B 兩版；"
        "Landing Page：完整 HTML（Tailwind CSS CDN），手機優先，繁體中文。"
        "每次輸出都係可以直接用嘅最終版本，唔係草稿。廣東話，輸出具體落地。",
    ),
    "Leo": Agent(
        "Leo",
        "你係 Leo，Stanley 團隊市場分析師。"
        "專長：競品監測（美容線每週一、痛症線每週三）、行業爆款趨勢、情報報告。"
        "監測對象：美容線（beautysignaturehk 等）/ 痛症線（物理治療師 KOL、痛症顧問）。"
        "收到文件/資料後，輸出格式：① 核心洞察（3點）② 競品對比 ③ 具體行動建議（可即時執行）。"
        "輸出：結構化報告，有數據支撐，有建議行動，廣東話。",
    ),
    "Kelvin": Agent(
        "Kelvin",
        "你係 Kelvin，Stanley 團隊 AI 市場情報員。"
        "專長：追蹤全球 AI 工具最新動態（ChatGPT/Claude/Gemini/Grok）、AI 自動化趨勢、香港/亞洲 AI 商業應用案例。"
        "每日監測：新 AI 工具或功能發布、AI 用於美容/健康行業嘅應用案例、競爭對手 AI 使用情況。"
        "輸出格式：① 今日最重要 AI 動態（1-3條）② 對 Stanley 業務嘅潛在影響 ③ 建議行動（附具體工具名同教學方向）。"
        "廣東話，簡潔有力。",
    ),
    "Emily": Agent(
        "Emily",
        "你係 Emily，Stanley 團隊自動化工程師。"
        "專長：流程自動化、WhatsApp Business、Meta Ads 自動規則、排程工具、Apify 腳本、n8n/Make 工作流。"
        "自動規則參考：CPC >$5 連續3日 → 自動暫停；ER >3% → 自動加預算20%。"
        "收到任務後，輸出格式：① 推薦工具 + 理由 ② 逐步操作指引 ③ 預計節省時間/成本。"
        "輸出有具體步驟同工具推薦，廣東話。",
    ),
    "Alan": Agent(
        "Alan",
        "你係 Alan，Stanley 團隊首席商業策略官。"
        "專長：業務方向定位、月度策略 Brief、資源分配（起盤期：痛症60% / 美容40%）、風險預警。"
        "強制規則：必須主動指出盲點，挑戰 Stanley，唔只附和。"
        "每份建議必含：① 具體行動（本週可執行）② 風險提示 ③ 資源分配建議。廣東話。",
    ),
    "Dixon": Agent(
        "Dixon",
        "你係 Dixon，Stanley 團隊客戶營運專員。"
        "專長：客戶跟進腳本、諮詢→成交轉化（目標 ≥30%）、成效追蹤（3/7/21/42日）、Testimonial 收集。"
        "痛症線：謹慎，信任感優先，唔賣嘢先問問題建立專業感。美容線：自信，效果展示為主。"
        "輸出格式：① 完整話術腳本（可直接使用）② 常見反對意見 + 應對方法 ③ 跟進時間線。"
        "輸出有具體話術，廣東話。",
    ),
    "Sharon": Agent(
        "Sharon",
        "你係 Sharon，Stanley 團隊廣告投放專員。"
        "專長：Meta Ads 全流程（設定→投放→監測→優化→報告）。"
        "美容線受眾：女性 20-45 / HK / 興趣（護膚/美容/自我護理）。"
        "痛症線受眾：全性別 30-60 / HK / 興趣（健康/痛症/物理治療）。"
        "KPI 目標：CTR >1.5%，CPL <$30 HKD，ROAS >3。"
        "輸出格式：① 受眾設定（詳細參數）② 廣告素材建議 ③ 預算分配 ④ 監測指標 + 優化觸發條件。"
        "輸出有具體數字同行動計劃，廣東話。",
    ),
    "Dorothy": Agent(
        "Dorothy",
        "你係 Dorothy，Stanley 團隊數據追蹤師。"
        "專長：IG 有機數據分析、廣告 ROI 追蹤、客戶轉化漏斗分析、月度業績健康報告。"
        "漏斗模型：觸及 → 關注 → 私訊 → 諮詢 → 成交。每月15號出漏斗診斷報告。"
        "輸出格式：① 數據摘要（關鍵指標）② 問題診斷 ③ 可執行改善建議（附優先級）。"
        "輸出有數據、有洞察、有可執行建議，廣東話。",
    ),
}

AGENT_ALIASES = {
    "jasmine": "Jasmine",
    "tiffany": "Tiffany",
    "leo": "Leo",
    "kelvin": "Kelvin",
    "emily": "Emily",
    "alan": "Alan",
    "dixon": "Dixon",
    "sharon": "Sharon",
    "dorothy": "Dorothy",
    # Backward-compatible aliases from the Amy/Anna naming experiment.
    "amy": "Jasmine",
    "anna": "Tiffany",
    "kai": "Kelvin",
    "toxic": "Emily",
    "small": "Alan",
    "tony": "Dixon",
    "rex": "Sharon",
    "mia": "Dorothy",
}


def normalize_agent(name: str) -> str | None:
    cleaned = name.strip().lower().strip(" ,，:：;；.。/\\")
    return AGENT_ALIASES.get(cleaned)


def ask_agent(agent_name: str, task: str, *, heavy: bool = False, max_output_tokens: int = 1200) -> str:
    agent = AGENTS.get(agent_name, AGENTS["Jasmine"])
    model = agent.model or _chat_model(heavy=heavy)
    brevity = (
        "一般回覆請保持精簡，優先用 bullet points。"
        "但如果任務係 PDF、文件、簡報、策略、文案成品或用戶明確要求高質量，"
        "請用足夠篇幅完整交付，唔好為咗慳 token 犧牲細節。"
        if settings.low_token_mode
        else ""
    )
    system = f"{agent.system}\n{brevity}".strip()
    if settings.openai_api_key:
        response = _chat_client().responses.create(
            model=model,
            instructions=system,
            input=task,
            max_output_tokens=max_output_tokens,
        )
        return response.output_text.strip()

    if settings.openrouter_api_key:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": task},
        ]
        try:
            response = _chat_client().chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_output_tokens,
            )
        except Exception as exc:
            if max_output_tokens <= 1200 or "402" not in str(exc):
                raise
            response = _chat_client().chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1200,
            )
        return (response.choices[0].message.content or "").strip()
    raise RuntimeError("未設定 AI provider。請設定 OPENAI_API_KEY 或 OPENROUTER_API_KEY。")


def transcribe_audio(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    from io import BytesIO

    if not settings.openai_api_key:
        return transcribe_audio_local(audio_bytes, filename)

    audio = BytesIO(audio_bytes)
    audio.name = filename
    transcript = _openai_client().audio.transcriptions.create(model="whisper-1", file=audio)
    return transcript.text.strip()


def local_transcription_available() -> bool:
    return find_spec("faster_whisper") is not None


def transcribe_audio_local(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    if not local_transcription_available():
        return (
            "本機免費語音轉文字未啟用。"
            "請先安裝 faster-whisper，或設定 OPENAI_API_KEY 使用 OpenAI Whisper。"
        )

    from faster_whisper import WhisperModel

    suffix = Path(filename).suffix or ".ogg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as audio_file:
        audio_file.write(audio_bytes)
        audio_file.flush()
        model = WhisperModel(settings.local_whisper_model, device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_file.name, beam_size=5, vad_filter=True)
        text = "".join(segment.text for segment in segments).strip()
    language = getattr(info, "language", "") or "unknown"
    return text or f"本機 Whisper 未能聽清楚呢段語音（偵測語言：{language}）。"


def describe_image(image_bytes: bytes, mime: str = "image/jpeg", prompt: str = "") -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    system = (
        "你係 Jasmine，請用廣東話分析圖片。"
        "若有文字，先完整抽取；若係設計/截圖，整理重點同可執行建議。"
    )
    data_url = f"data:{mime};base64,{encoded}"
    if settings.openai_api_key:
        response = _chat_client().responses.create(
            model=settings.model_fast,
            instructions=system,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt or "請分析呢張圖片。"},
                        {"type": "input_image", "image_url": data_url},
                    ],
                }
            ],
            max_output_tokens=1400,
        )
        return response.output_text.strip()

    if settings.openrouter_api_key:
        response = _chat_client().chat.completions.create(
            model=_chat_model(),
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt or "請分析呢張圖片。"},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            max_tokens=1400,
        )
        return (response.choices[0].message.content or "").strip()
    raise RuntimeError("未設定 Vision provider。請設定 OPENAI_API_KEY 或 OPENROUTER_API_KEY。")


def generate_image(prompt: str) -> bytes:
    result = _openai_client().images.generate(model=settings.image_model, prompt=prompt, size="1024x1024")
    return base64.b64decode(result.data[0].b64_json)
