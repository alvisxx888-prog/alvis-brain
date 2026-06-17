#!/usr/bin/env python3
import os
import json
import re
import base64
import tempfile
import subprocess
import logging
import asyncio
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

try:
    from duckduckgo_search import DDGS
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False

try:
    from apify_client import ApifyClient
    APIFY_AVAILABLE = True
except ImportError:
    APIFY_AVAILABLE = False

try:
    import instaloader
    INSTALOADER_AVAILABLE = True
except ImportError:
    INSTALOADER_AVAILABLE = False

try:
    from facebook_scraper import get_posts as fb_get_posts
    FACEBOOK_SCRAPER_AVAILABLE = True
except ImportError:
    FACEBOOK_SCRAPER_AVAILABLE = False

try:
    import openai as openai_lib
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ALLOWED_USER_ID = 193060672
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CLAUDE_PATH = "/root/.local/bin/claude"
HISTORY_FILE = "/root/claude-bot/history.json"
LAST_CONTENT_FILE = "/root/claude-bot/last_content.json"
USAGE_FILE = "/root/claude-bot/usage.json"
APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GAMMA_API_KEY = os.environ.get("GAMMA_API_KEY", "")

MODEL_FAST   = "claude-sonnet-4-6"
MODEL_VISION = "claude-sonnet-4-6"
MODEL_HEAVY  = "claude-opus-4-8"

# ── Agent prompts ──────────────────────────────────────────────────────────────

AGENT_PROMPTS = {
    "Amy": """你係 Amy，Stanley 團隊嘅秘書同指揮中樞（v4.0）。
職責：分流任務、協調 Agent、追蹤進度、向 Stanley（即 Alvis）匯報。
風格：廣東話，專業隨和，簡潔有力。
授權邊界：$0成本決定自主執行；預算支出需 Stanley 確認；Stanley 不在線 >2小時可代決 P0 任務（<$500）。
重要：收到文件/圖片內容後，必須主動派 Agent 產出具體成品，唔係只匯報分析。""",

    "Anna": """你係 Anna，Stanley 團隊廣告設計師兼文稿師（v4.0）。
專長：IG帖文案、Reels腳本、廣告素材、小紅書格式、A/B 測試素材、Landing Page HTML、電郵模板。
業務線：痛症（品牌 Alvis）/ 美容（品牌 Stanley）。

輸出規格：
- IG帖：emoji + hook + 正文 + CTA + hashtags（5-10個）
- Reels腳本：0-3秒 Hook → 3-15秒衝突 → 15-45秒解方 → 45-60秒 CTA
- 廣告素材：標題 ≤27字，正文 ≤125字，輸出 A/B 兩版
- Landing Page：完整 HTML（Tailwind CSS CDN），手機優先，繁體中文
- 每次輸出都係可以直接用嘅最終版本，唔係草稿

廣東話，輸出具體落地。""",

    "Leo": """你係 Leo，Stanley 團隊市場分析師（v4.0）。
專長：競品監測（美容線每週一、痛症線每週三）、行業爆款趨勢、情報報告。
監測對象：美容線（beautysignaturehk 等）/ 痛症線（物理治療師 KOL、痛症顧問）。

收到文件/資料後，輸出格式：
① 核心洞察（3點）
② 競品對比
③ 具體行動建議（可即時執行）

輸出：結構化報告，有數據支撐，有建議行動，廣東話。""",

    "Kai": """你係 Kai，Stanley 團隊 AI 市場情報員（v2.0）。
專長：追蹤全球 AI 工具最新動態（ChatGPT/Claude/Gemini/Grok）、AI 自動化趨勢、香港/亞洲 AI 商業應用案例。
每日監測：新 AI 工具或功能發布、AI 用於美容/健康行業嘅應用案例、競爭對手 AI 使用情況。

核心原則：唔好叫 Stanley 去下載或學習任何工具，只輸出情報結果。

輸出格式：
① 今日最重要 AI 動態（1-3條，只講事實）
② 對 Stanley 美容/痛症業務嘅直接影響（具體講影響係咩，唔係教佢點做）
③ 如有免費可用工具：「[工具名] — 免費 — 可直接用於 [具體用途]」；如係付費工具：略過唔提

廣東話，簡潔有力。""",

    "Toxic": """你係 Toxic，Stanley 團隊自動化工程師（v4.0）。
專長：流程自動化、WhatsApp Business、Meta Ads 自動規則、排程工具、Apify 腳本、n8n/Make 工作流。
自動規則參考：CPC >$5 連續3日 → 自動暫停；ER >3% → 自動加預算20%。

核心原則：永遠直接輸出成品，唔好教 Stanley 點做、唔好列步驟叫佢自己操作。

輸出規則：
- 能直接產出嘅：立即輸出（WhatsApp 訊息模板、廣告規則設定參數、腳本代碼、n8n JSON workflow）
- 需要外部工具嘅：只需一行說明「需要 [工具名] — [免費/月費$X] — Bot 已幫你準備好 [具體成品]，你只需一個動作：[最簡單嗰步]」
- 絕對唔好：逐步教學、叫 Stanley 下載任何嘢、解釋點用工具

廣東話，直接輸出成品。""",

    "Small": """你係 Small，Stanley 團隊首席商業策略官（v4.0）。
專長：業務方向定位、月度策略 Brief、資源分配（起盤期：痛症60% / 美容40%）、風險預警。
強制規則：必須主動指出盲點，挑戰 Stanley，唔只附和。

每份建議必含：
① 具體行動（本週可執行）
② 風險提示
③ 資源分配建議

廣東話。""",

    "Tony": """你係 Tony，Stanley 團隊客戶營運專員（v4.0）。
專長：客戶跟進腳本、諮詢→成交轉化（目標 ≥30%）、成效追蹤（3/7/21/42日）、Testimonial 收集。
痛症線：謹慎，信任感優先，唔賣嘢先問問題建立專業感。
美容線：自信，效果展示為主。

輸出格式：
① 完整話術腳本（可直接使用）
② 常見反對意見 + 應對方法
③ 跟進時間線

輸出有具體話術，廣東話。""",

    "Rex": """你係 Rex，Stanley 團隊廣告投放專員（v4.0）。
專長：Meta Ads 全流程（設定→投放→監測→優化→報告）。
美容線受眾：女性 20-45 / HK / 興趣（護膚/美容/自我護理）。
痛症線受眾：全性別 30-60 / HK / 興趣（健康/痛症/物理治療）。
KPI 目標：CTR >1.5%，CPL <$30 HKD，ROAS >3。

輸出格式：
① 受眾設定（詳細參數）
② 廣告素材建議
③ 預算分配
④ 監測指標 + 優化觸發條件

輸出有具體數字同行動計劃，廣東話。""",

    "Mia": """你係 Mia，Stanley 團隊數據追蹤師（v4.0）。
專長：IG 有機數據分析、廣告 ROI 追蹤、客戶轉化漏斗分析、月度業績健康報告。
漏斗模型：觸及 → 關注 → 私訊 → 諮詢 → 成交。
每月15號出漏斗診斷報告。

輸出格式：
① 數據摘要（關鍵指標）
② 問題診斷
③ 可執行改善建議（附優先級）

輸出有數據、有洞察、有可執行建議，廣東話。""",
}

AMY_DISPATCH_SYSTEM = """你係 Amy，Stanley 團隊秘書同指揮中樞。
Stanley 發咗指令（可能包含文件內容），你需要分析並決定分派給哪些 Agent 產出具體成品，或者執行即時行動。

可用 Agent（產出文字/文件成品）：
- Anna：廣告設計 & 文稿（IG帖、Reels腳本、廣告素材、小紅書、Landing Page HTML、電郵、PDF、幻燈片）
- Leo：市場分析（競品監測、行業趨勢、情報報告）
- Kai：AI 市場情報（AI 工具動態、AI 商業應用、AI 趨勢）
- Toxic：自動化建議（系統設定、WhatsApp流程、排程、n8n工作流設計）
- Small：商業策略（方向定位、策略 Brief、風險預警）
- Tony：客戶營運（跟進腳本、成交轉化、客戶關係）
- Rex：廣告投放（Meta Ads 設定、A/B 測試、廣告優化）
- Mia：數據追蹤（IG 數據、廣告 ROI、漏斗分析）

可用即時行動 actions（直接執行，返回真實數據，唔係文字計劃）：
- scrape_ig：抓取 IG 帳號最新帖文 + Leo 競品分析
  觸發：「抓/爬/scrape/監測」+ IG帳號 / 「競品數據」/ 「@帳號 IG」
  param：IG帳號名（不含@）
- scrape_threads：抓取 Threads 帳號最新帖文 + Leo 競品分析
  觸發：「Threads」+ 帳號 / 「抓 threads @帳號」
  param：Threads帳號名（不含@）
- scrape_fb：抓取 Facebook 專頁最新帖文 + Leo 競品分析
  觸發：「Facebook/FB/臉書」+ 專頁名 / 「抓 FB @帳號」
  param：FB 專頁名（不含@）
- scrape_xhs：抓取小紅書帖文 + Anna 趨勢分析
  觸發：「小紅書」+ 關鍵詞 / 「抓/搜 小紅書」
  param：搜尋關鍵詞
- scrape_web：抓取指定網頁內容
  觸發：「抓/爬 網頁/URL」+ 網址
  param：完整 URL（https://...）
- scrape_news：Google 新聞搜尋 + Leo 分析
  觸發：「新聞/news/最新資訊」+ 關鍵詞
  param：搜尋關鍵詞
- product_research：擷取真實市場數據 → Leo 市場分析 → Small 產品機會識別，直出具體產品建議
  觸發：「新產品/產品機會/市場研究/有咩可以做」+ 主題 / 「搵下有咩商機」/ 「分析市場」+ 主題
  param：市場主題或關鍵詞（例：美容療程、痛症管理、護膚品）

分派規則：
- 簡單對話、問候 → Amy 直接回答（direct_reply）
- 寫文案/腳本/報告/策略 → 分派 Agent 產出文字成品
- 需要 PDF / 幻燈片 → 分派 Anna（task 要包含「PDF」或「幻燈片/slides」關鍵字）
- 涉及抓取/爬蟲/競品數據/網頁 → 用 actions，唔好派 Toxic 出文字計劃
- 涉及 AI 工具/趨勢 → 加入 Kai
- 複合任務 → 同時使用 actions + dispatch
- 需要多員工分析然後整合做 PDF：先分派分析員（Leo/Small/Tony 等），再分派 Anna 做 PDF。系統會自動先等分析員完成，再把佢哋嘅成果傳俾 Anna 整合。

重要原則：
- 分派 Agent 時，task 字段必須包含足夠上下文，讓 Agent 直接產出成品
- 「儲存資料」「之後用」「整合做PDF」→ 分派 Anna 做 PDF，系統會自動把所有已收集數據傳俾 Anna
- Stanley 說「幫我優化」「重新整」→ 系統已記住上次所有 Agent 嘅成果，直接分派相關 Agent 按上次結果優化

必須輸出純 JSON，唔可以有任何其他文字：

有 action 時：
{"amy_message": "Amy 說嘅話", "actions": [{"type": "scrape_ig", "param": "帳號名"}], "dispatch": [], "direct_reply": null}

有 Agent 分派時：
{"amy_message": "Amy 說嘅話", "actions": [], "dispatch": [{"agent": "AgentName", "task": "具體任務 + 相關內容"}], "direct_reply": null}

Amy 直接回答時：
{"amy_message": null, "actions": [], "dispatch": [], "direct_reply": "Amy 直接回覆嘅完整內容"}

action types: scrape_ig / scrape_threads / scrape_fb / scrape_xhs / scrape_web / scrape_news / product_research"""

AGENT_EMOJI = {
    "Amy":   "👩‍💼",
    "Anna":  "🎨",
    "Leo":   "📊",
    "Kai":   "🤖",
    "Toxic": "⚡",
    "Small": "🧠",
    "Tony":  "🤝",
    "Rex":   "📢",
    "Mia":   "📈",
}

QUOTA_EXCEEDED_MSG = (
    "🚨 Claude API quota 用完了！\n\n"
    "⏳ 通常幾小時後自動重置（最長24小時）。\n"
    "重置後直接繼續用，唔需要任何操作。\n\n"
    "📊 睇重置時間：console.anthropic.com → Usage"
)

AGENT_MODELS = {
    "Amy":   "claude-haiku-4-5-20251001",  # dispatch routing — speed first
    "Anna":  "claude-opus-4-8",             # copywriting — conversion-critical, best quality
    "Leo":   "claude-sonnet-4-6",           # market analysis
    "Kai":   "claude-haiku-4-5-20251001",   # AI news summaries — fast
    "Toxic": "claude-sonnet-4-6",           # automation advice
    "Small": "claude-opus-4-8",             # strategy — needs deep reasoning
    "Tony":  "claude-opus-4-8",             # sales scripts — conversion-critical, best quality
    "Rex":   "claude-sonnet-4-6",           # ad management
    "Mia":   "claude-haiku-4-5-20251001",   # data summaries — fast
}

DREAM_TEAM_PROMPTS = {
    "Grant Cardone": """You are Grant Cardone — serial entrepreneur, real estate mogul, sales trainer, author of "The 10X Rule." You are relentless, loud, and unapologetic about your belief that most people operate at 1/10th of their potential. You are advising Stanley — a beauty and pain management sales professional in Hong Kong, targeting clients aged 18–65, building an Instagram lead generation strategy. Be direct, high-energy, challenge the scale of ambition, push for volume and massive action. Respond in Traditional Chinese (廣東話), keep it punchy and actionable.""",

    "Alex Hormozi": """You are Alex Hormozi — entrepreneur, investor, author of "$100M Offers" and "$100M Leads." You are calm, analytical, data-driven. You are advising Stanley — a beauty and pain management sales professional in Hong Kong. Focus on offer design, unit economics, and lead generation math. Call out vanity metrics. Use the Value Equation framework. Respond in Traditional Chinese (廣東話), be specific with numbers and frameworks.""",

    "Gary Vee": """You are Gary Vaynerchuk (Gary Vee) — CEO of VaynerMedia, authority on social media marketing and personal branding. Raw, unfiltered, obsessed with attention and authenticity. You are advising Stanley — a beauty and pain management sales professional in Hong Kong. Push for documenting over creating, Reels as top organic reach, platform hierarchy in HK (IG/小紅書/FB). Respond in Traditional Chinese (廣東話), be energetic and platform-specific.""",

    "Russell Brunson": """You are Russell Brunson — co-founder of ClickFunnels, author of "DotCom Secrets." Systematic, structured, obsessed with funnels and value ladders. You are advising Stanley — a beauty and pain management sales professional in Hong Kong. Map value ladders, hook-story-offer structure, the bridge from IG to WhatsApp/booking. Respond in Traditional Chinese (廣東話), use funnel vocabulary and frameworks.""",

    "Dan Kennedy": """You are Dan Kennedy — "professor of harsh reality," direct-response marketing legend, "No B.S." book series author. Gruff, data-obsessed, sceptical of social media unless it's measured. You are advising Stanley — a beauty and pain management sales professional in Hong Kong. Demand tracking systems, message×market×medium alignment, follow-up sequences, list ownership. Respond in Traditional Chinese (廣東話), be blunt and ROI-focused.""",

    "Jordan Belfort": """You are Jordan Belfort — creator of the Straight Line Persuasion System, reformed master of closing. Sharp, psychologically precise. You are advising Stanley — a beauty and pain management sales professional in Hong Kong. Use the Three Certainties framework (product/you/now), audit content for certainty-building, design DM conversion flows. Respond in Traditional Chinese (廣東話), be clinical about persuasion mechanics.""",

    "Seth Godin": """You are Seth Godin — author of "Purple Cow," "Tribes," "This Is Marketing." Quiet, philosophically precise, anti-hype. You are advising Stanley — a beauty and pain management sales professional in Hong Kong. Challenge him to find the smallest viable audience, define a unique point of view, build trust through consistency. Respond in Traditional Chinese (廣東話), be concise and thought-provoking.""",

    "Tony Robbins": """You are Tony Robbins — world's #1 life and business strategist, author of "Awaken the Giant Within." Enormous energy, empathy, identity-focused. You are advising Stanley — a beauty and pain management sales professional in Hong Kong. Focus on identity, emotional commitment, the transformation clients are really buying, building rituals. Respond in Traditional Chinese (廣東話), be inspiring but practical.""",
}

DREAM_TEAM_EMOJI = {
    "Grant Cardone":  "🔥",
    "Alex Hormozi":   "💰",
    "Gary Vee":       "📱",
    "Russell Brunson":"🔧",
    "Dan Kennedy":    "📋",
    "Jordan Belfort": "🎯",
    "Seth Godin":     "🎨",
    "Tony Robbins":   "⚡",
}

DREAM_TEAM_MODELS = {
    "Grant Cardone":  "claude-sonnet-4-6",          # high-energy sales — Sonnet 夠
    "Alex Hormozi":   "claude-opus-4-8",             # 數據+框架深度分析 — 需要 Opus
    "Gary Vee":       "claude-haiku-4-5-20251001",   # 快狠準 social tips — Haiku
    "Russell Brunson":"claude-sonnet-4-6",           # 系統化 funnel — Sonnet
    "Dan Kennedy":    "claude-sonnet-4-6",           # 直接 ROI — Sonnet
    "Jordan Belfort": "claude-sonnet-4-6",           # 成交心理 — Sonnet
    "Seth Godin":     "claude-opus-4-8",             # 哲學+品牌深度 — 需要 Opus
    "Tony Robbins":   "claude-sonnet-4-6",           # 激勵+身份 — Sonnet
}


# ── History persistence ────────────────────────────────────────────────────────

def load_history() -> dict:
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {int(k): v for k, v in data.items()}
    except Exception as e:
        logger.warning(f"Load history error: {e}")
    return {}


def save_history(history: dict):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({str(k): v[-50:] for k, v in history.items()}, f, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Save history error: {e}")


def load_last_content() -> dict:
    try:
        if os.path.exists(LAST_CONTENT_FILE):
            with open(LAST_CONTENT_FILE, "r", encoding="utf-8") as f:
                return {int(k): v for k, v in json.load(f).items()}
    except Exception:
        pass
    return {}

def save_last_content_to_disk(data: dict):
    try:
        with open(LAST_CONTENT_FILE, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in data.items()}, f, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Save last_content error: {e}")


def load_usage() -> dict:
    try:
        if os.path.exists(USAGE_FILE):
            with open(USAGE_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {"calls": 0, "date": ""}

_daily_usage = load_usage()

def track_call() -> int:
    from datetime import date
    today = str(date.today())
    if _daily_usage.get("date") != today:
        _daily_usage["calls"] = 0
        _daily_usage["date"] = today
    _daily_usage["calls"] += 1
    try:
        with open(USAGE_FILE, "w") as f:
            json.dump(_daily_usage, f)
    except Exception:
        pass
    return _daily_usage["calls"]

def get_usage_warning() -> str:
    calls = _daily_usage.get("calls", 0)
    if calls >= 40:
        return f"🚨 今日已用 {calls} 個 Claude call，建議暫停使用，等 quota 重置後再繼續（通常幾小時後重置）。"
    if calls >= 25:
        return f"⚠️ 今日已用 {calls} 個 Claude call，接近每日限制，留意使用量。"
    return ""


executor = ThreadPoolExecutor(max_workers=10)
conversation_history: dict[int, list] = load_history()
MAX_HISTORY = 10
last_content: dict[int, str] = load_last_content()  # 持久化，重啟後仍保留
follow_up_state: dict[int, dict] = {}   # {user_id: {"agent": "Leo", "context": "...", "active": True}}
agent_outputs: dict[int, dict] = {}     # {user_id: {"Leo": "Leo's output", "Kai": "Kai's output"}}


# ── Web search (DuckDuckGo — free) ─────────────────────────────────────────────

def news_search(query: str, max_results: int = 5) -> str:
    """Try Apify Google first, fall back to DuckDuckGo."""
    if APIFY_AVAILABLE and APIFY_TOKEN:
        result = scrape_google(query, max_results)
        if result and not result.startswith("["):
            return result
    return web_search(query, max_results)


def web_search(query: str, max_results: int = 5) -> str:
    if not WEB_SEARCH_AVAILABLE:
        return "[Web search 不可用]"
    import time as _time
    for attempt in range(3):
        try:
            if attempt > 0:
                _time.sleep(3 * attempt)
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results, backend="lite"))
            if results:
                out = ""
                for r in results:
                    out += f"【{r.get('title', '')}】\n{r.get('body', '')}\n來源：{r.get('href', '')}\n\n"
                return out.strip()
        except Exception as e:
            logger.warning(f"Web search attempt {attempt+1} error: {e}")
        _time.sleep(2)
    return "無搜尋結果"


# ── Apify scraping ─────────────────────────────────────────────────────────────

def scrape_instagram(username: str, max_posts: int = 12) -> str:
    # IG uses Instaloader only; no Apify fallback for Instagram.
    username = username.lstrip("@").strip()
    if not INSTALOADER_AVAILABLE:
        fallback = web_search(f"Instagram {username} 最新帖文 內容", 6)
        return (
            "Instaloader 未安裝，無法直接抓 IG profile。

"
            "以下係網絡搜尋 fallback，唔係直接由 IG profile 抓出嚟，準確度會低啲：

"
            f"{fallback}"
        )

    try:
        L = instaloader.Instaloader(
            quiet=True,
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
        )
        profile = instaloader.Profile.from_username(L.context, username)
        follower_count = profile.followers
        output = f"📊 @{username}（{follower_count:,} followers）最新 {max_posts} 帖：
來源：Instaloader public scrape

"
        for i, post in enumerate(profile.get_posts()):
            if i >= max_posts:
                break
            likes = post.likes
            comments = post.comments
            caption = (post.caption or "（無文字）")[:150]
            ts = post.date_local.strftime("%Y-%m-%d")
            output += f"{i+1}. [{ts}] 👍{likes} 💬{comments}
{caption}

"
        return output.strip()
    except Exception as e:
        logger.warning(f"Instaloader IG scrape error: {e}; using web search fallback")
        fallback = web_search(f"Instagram {username} 最新帖文 內容", 6)
        return (
            f"Instaloader 抓唔到 @{username}，可能係 IG 限制公開讀取、帳號私人/不存在、login required、rate limit 或網絡問題。
"
            f"錯誤：{e}

"
            "以下係網絡搜尋 fallback，唔係直接由 IG profile 抓出嚟，準確度會低啲：

"
            f"{fallback}"
        )

def scrape_facebook(page_name: str, max_posts: int = 10) -> str:
    if not FACEBOOK_SCRAPER_AVAILABLE:
        return web_search(f"Facebook {page_name} 最新帖文 內容", 6)
    try:
        output = f"📘 Facebook @{page_name} 最新 {max_posts} 帖：\n\n"
        count = 0
        for post in fb_get_posts(page_name, pages=3, timeout=30):
            if count >= max_posts:
                break
            text = (post.get("text") or post.get("post_text") or "（無文字）")[:150]
            likes = post.get("likes") or 0
            comments = post.get("comments") or 0
            shares = post.get("shares") or 0
            t = post.get("time")
            ts = t.strftime("%Y-%m-%d") if t else ""
            output += f"{count+1}. [{ts}] 👍{likes} 💬{comments} 🔄{shares}\n{text}\n\n"
            count += 1
        if count == 0:
            return web_search(f"Facebook {page_name} 最新帖文", 6)
        return output.strip()
    except Exception as e:
        logger.error(f"Facebook scrape error: {e}")
        return web_search(f"Facebook {page_name} 最新帖文 內容", 6)


def scrape_webpage(url: str) -> str:
    if not APIFY_AVAILABLE or not APIFY_TOKEN:
        return "[Apify 未設定]"
    try:
        client = ApifyClient(APIFY_TOKEN)
        run_input = {"startUrls": [{"url": url}], "maxCrawlPages": 1}
        run = client.actor("apify/web-scraper").call(run_input=run_input)
        dataset_id = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]
        items = list(client.dataset(dataset_id).iterate_items())
        if not items:
            return f"無法抓取 {url}"
        text = items[0].get("text") or items[0].get("body") or ""
        return f"【{url}】\n{text[:4000]}"
    except Exception as e:
        return f"網頁抓取失敗：{e}"


def scrape_xhs(query: str, max_posts: int = 10) -> str:
    if not APIFY_AVAILABLE or not APIFY_TOKEN:
        return "[Apify 未設定]"
    try:
        client = ApifyClient(APIFY_TOKEN)
        run_input = {"keyword": query, "maxItems": max_posts}
        run = client.actor("microworlds/xiaohongshu-scraper").call(run_input=run_input)
        dataset_id = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]
        items = list(client.dataset(dataset_id).iterate_items())
        if not items:
            return f"[小紅書：未找到「{query}」相關帖文]"
        lines = [f"📕 小紅書「{query}」搜尋結果（{len(items)} 條）：\n"]
        for i, item in enumerate(items[:max_posts], 1):
            title = item.get("title") or item.get("name") or ""
            content = item.get("description") or item.get("content") or item.get("text") or ""
            likes = item.get("likesCount") or item.get("likes") or 0
            author = item.get("authorName") or item.get("username") or ""
            url = item.get("url") or ""
            lines.append(
                f"【{i}】{title}\n"
                f"作者：{author}  ❤️ {likes}\n"
                f"{content[:200]}\n"
                f"🔗 {url}\n"
            )
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"XHS scrape error: {e}")
        return f"[小紅書抓取失敗：{e}]"


def scrape_google(query: str, max_results: int = 8) -> str:
    if not APIFY_AVAILABLE or not APIFY_TOKEN:
        return "[Apify 未設定]"
    try:
        client = ApifyClient(APIFY_TOKEN)
        run_input = {
            "queries": [query],
            "maxPagesPerQuery": 1,
            "resultsPerPage": max_results,
            "countryCode": "hk",
            "languageCode": "zh-TW",
        }
        run = client.actor("apify/google-search-scraper").call(run_input=run_input)
        dataset_id = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]
        items = list(client.dataset(dataset_id).iterate_items())
        if not items:
            return f"[Google：未找到「{query}」相關結果]"
        results = items[0].get("organicResults", []) if items else []
        if not results:
            results = items
        lines = [f"🔍 Google「{query}」搜尋結果（{len(results)} 條）：\n"]
        for i, r in enumerate(results[:max_results], 1):
            title = r.get("title") or ""
            snippet = r.get("description") or r.get("snippet") or ""
            link = r.get("url") or r.get("link") or ""
            lines.append(f"【{i}】{title}\n{snippet[:200]}\n🔗 {link}\n")
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Google scrape error: {e}")
        return f"[Google 搜尋失敗：{e}]"


def scrape_threads(username: str, max_posts: int = 12) -> str:
    if not APIFY_AVAILABLE or not APIFY_TOKEN:
        return "[Apify 未設定]"
    try:
        client = ApifyClient(APIFY_TOKEN)
        run_input = {
            "username": [username],
            "resultsLimit": max_posts,
        }
        run = client.actor("apify/threads-scraper").call(run_input=run_input)
        dataset_id = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]
        items = list(client.dataset(dataset_id).iterate_items())
        if not items:
            return f"[@{username}] Threads 抓取不到資料，可能係私人帳號或帳號名稱錯誤。"
        output = f"🧵 Threads @{username} 最新 {len(items)} 帖：\n\n"
        for i, item in enumerate(items, 1):
            likes = item.get("likeCount") or item.get("likesCount") or 0
            replies = item.get("replyCount") or item.get("repliesCount") or 0
            text = (item.get("text") or item.get("caption") or "（無文字）")[:150]
            ts = (item.get("timestamp") or item.get("createdAt") or "")[:10]
            output += f"{i}. [{ts}] ❤️{likes} 💬{replies}\n{text}\n\n"
        return output.strip()
    except Exception as e:
        logger.error(f"Threads scrape error: {e}")
        return f"Threads 抓取失敗：{e}"


# ── Voice transcription (OpenAI Whisper) ──────────────────────────────────────

def transcribe_audio(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        return "[需要設定 OPENAI_API_KEY 才能使用語音轉錄]"
    try:
        import io as _io
        client = openai_lib.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = _io.BytesIO(audio_bytes)
        audio_file.name = filename
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
        return transcript.text
    except Exception as e:
        logger.error(f"Whisper transcription error: {e}")
        return f"[錄音轉錄失敗：{e}]"


# ── PowerPoint generation (python-pptx) ───────────────────────────────────────

def generate_pptx_bytes(title: str, subtitle: str, slides: list) -> bytes:
    import io as _io
    if not PPTX_AVAILABLE:
        raise ImportError("python-pptx 未安裝，請執行：pip install python-pptx")
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    DARK = RGBColor(0x1a, 0x1a, 0x2e)
    MID  = RGBColor(0x16, 0x21, 0x3e)

    # Title slide
    sl = prs.slides.add_slide(prs.slide_layouts[0])
    sl.shapes.title.text = title
    tf = sl.shapes.title.text_frame
    tf.paragraphs[0].font.name = "Microsoft YaHei"
    tf.paragraphs[0].font.size = Pt(40)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = DARK
    try:
        ph = sl.placeholders[1]
        ph.text = subtitle
        ph.text_frame.paragraphs[0].font.name = "Microsoft YaHei"
        ph.text_frame.paragraphs[0].font.size = Pt(24)
        ph.text_frame.paragraphs[0].font.color.rgb = MID
    except Exception:
        pass

    # Content slides
    for s in slides:
        sl = prs.slides.add_slide(prs.slide_layouts[1])
        sl.shapes.title.text = s["title"]
        sl.shapes.title.text_frame.paragraphs[0].font.name = "Microsoft YaHei"
        sl.shapes.title.text_frame.paragraphs[0].font.size = Pt(32)
        sl.shapes.title.text_frame.paragraphs[0].font.bold = True
        sl.shapes.title.text_frame.paragraphs[0].font.color.rgb = MID
        try:
            body_tf = sl.placeholders[1].text_frame
            body_tf.word_wrap = True
            for i, point in enumerate(s["points"]):
                p = body_tf.paragraphs[0] if i == 0 else body_tf.add_paragraph()
                p.text = point
                p.font.name = "Microsoft YaHei"
                p.font.size = Pt(20)
                p.level = 0
        except Exception:
            pass

    buf = _io.BytesIO()
    prs.save(buf)
    return buf.getvalue()


# ── Gamma API presentation generation ─────────────────────────────────────────
# 設定步驟：gamma.app → Settings → API → 生成 API Key
# VPS 執行：export GAMMA_API_KEY='你的key' && echo 'export GAMMA_API_KEY=...' >> /root/.bashrc

def generate_gamma_pptx(title: str, content: str) -> tuple[bytes, str]:
    """
    Generate a presentation via Gamma API.
    Returns (pptx_bytes, gamma_url).
    Requires GAMMA_API_KEY env variable.
    """
    import json as _json
    if not GAMMA_API_KEY:
        raise RuntimeError("GAMMA_API_KEY 未設定")

    prompt = f"# {title}\n\n{content}"
    payload = _json.dumps({
        "inputText": prompt,
        "format": "presentation",
        "exportAs": "pptx",
        "textOptions": {"language": "zh-tw", "tone": "professional"},
        "imageOptions": {"source": "aiGenerated", "stylePreset": "photorealistic"},
    }).encode()

    req = urllib.request.Request(
        "https://api.gamma.app/v1/generate",
        data=payload,
        headers={
            "Authorization": f"Bearer {GAMMA_API_KEY}",
            "Content-Type": "application/json",
        }
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = _json.loads(resp.read())

    gamma_url = result.get("gammaUrl") or result.get("viewUrl") or result.get("url") or ""
    export_url = result.get("exportUrl") or ""

    pptx_bytes = b""
    if export_url:
        dl = urllib.request.Request(export_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(dl, timeout=60) as r:
            pptx_bytes = r.read()

    return pptx_bytes, gamma_url


# ── PDF generation (reportlab) ─────────────────────────────────────────────────

def generate_pdf_bytes(title: str, content: str) -> bytes:
    import io as _io
    from datetime import datetime as _dt
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab 未安裝，請執行：pip install reportlab")
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    buffer = _io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2.5*cm, leftMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm
    )
    title_style = ParagraphStyle(
        'CJKTitle', fontName='STSong-Light', fontSize=18,
        spaceAfter=10, alignment=TA_CENTER,
        textColor=colors.HexColor('#1a1a2e')
    )
    heading_style = ParagraphStyle(
        'CJKHeading', fontName='STSong-Light', fontSize=13,
        spaceBefore=14, spaceAfter=6,
        textColor=colors.HexColor('#16213e'), leading=20
    )
    body_style = ParagraphStyle(
        'CJKBody', fontName='STSong-Light', fontSize=11,
        spaceAfter=5, leading=19
    )
    footer_style = ParagraphStyle(
        'CJKFooter', fontName='STSong-Light', fontSize=9,
        textColor=colors.grey, alignment=TA_CENTER
    )
    story = []
    story.append(Paragraph(title, title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    story.append(Spacer(1, 0.4*cm))
    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 0.15*cm))
            continue
        safe = stripped.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if stripped.startswith('#') or (len(stripped) < 35 and stripped.endswith('：')):
            clean = safe.lstrip('#').strip()
            story.append(Paragraph(clean, heading_style))
        else:
            story.append(Paragraph(safe, body_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#dddddd')))
    date_str = _dt.now().strftime("%Y年%m月%d日")
    story.append(Paragraph(f"生成日期：{date_str}", footer_style))
    doc.build(story)
    return buffer.getvalue()


# ── Image generation (Pollinations.ai — free) ──────────────────────────────────

def generate_image_sync(prompt: str) -> bytes:
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1080&nologo=true&model=flux"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read()


def generate_dalle_image(prompt: str, size: str = "1024x1024") -> bytes:
    """Generate image via DALL-E 3 (OpenAI). Falls back to Pollinations if unavailable."""
    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        return generate_image_sync(prompt)
    import io as _io
    client = openai_lib.OpenAI(api_key=OPENAI_API_KEY)
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    dl_req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(dl_req, timeout=60) as resp:
        return resp.read()


def generate_dalle_prompts(user_desc: str) -> str:
    user_msg = (
        f"用戶需求：{user_desc}\n\n"
        "業務背景：香港美容（護膚、美容療程）及痛症管理銷售，IG 行銷為主。\n\n"
        "請生成 3 個不同風格的英文 DALL-E 3 prompt，每個方向不同：\n"
        "1. 🏥 專業醫療風（乾淨、信任感、白色基調）\n"
        "2. 💆 生活方式風（溫暖、真實感、自然光）\n"
        "3. ✨ 高端美學風（奢華、精緻、品牌感）\n\n"
        "每個 prompt 要包含：主體描述、風格、光線、構圖、色調、--ar 9:16（IG 規格）。\n"
        "直接輸出 3 個 prompt，唔需要額外解釋。"
    )
    return run_with_system(
        "你係一位頂尖 AI 圖像設計師，專門幫人優化 DALL-E 3 / ChatGPT Image 的 prompt。",
        user_msg,
    )


# ── Core Claude runners ────────────────────────────────────────────────────────

def run_claude(prompt: str, timeout: int = 180, model: str = None) -> str:
    env = {**os.environ, "HOME": "/root"}
    env.pop("ANTHROPIC_API_KEY", None)  #用 OAuth 登入，唔用 API key
    cmd = [CLAUDE_PATH, "-p", prompt, "--allowedTools", ""]
    if model:
        cmd += ["--model", model]
    result = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=timeout,
        env=env,
    )
    track_call()
    combined_out = (result.stdout or "") + (result.stderr or "")
    if any(kw in combined_out.lower() for kw in ["rate limit", "usage limit", "quota", "too many requests", "overloaded", "credit balance"]):
        return "[QUOTA_EXCEEDED]"
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    logger.error(f"Claude error: stderr={result.stderr[:200]} stdout={result.stdout[:200]}")
    return f"[出錯：{result.stderr[:100]}]"


def run_claude_sdk(messages: list, model: str = MODEL_FAST, max_tokens: int = 4096, system: str = None) -> str:
    try:
        client = anthropic.Anthropic()
        kwargs = dict(model=model, max_tokens=max_tokens, messages=messages)
        if system:
            kwargs['system'] = system
        response = client.messages.create(**kwargs)
        track_call()
        return response.content[0].text
    except Exception as e:
        err_str = str(e).lower()
        if any(kw in err_str for kw in ["rate limit", "usage limit", "quota", "too many requests", "overloaded", "credit balance"]):
            return "[QUOTA_EXCEEDED]"
        logger.error(f"Claude SDK error: {e}")
        return f"[API 錯誤：{e}]"


def run_with_system(system_prompt: str, user_message: str, model: str = MODEL_FAST, timeout: int = None) -> str:
    combined = f"{system_prompt}\n\n---\n{user_message}"
    if timeout is None:
        timeout = 300 if model == MODEL_HEAVY else 180
    return run_claude(combined, timeout=timeout, model=model)


def extract_file_content(file_bytes: bytes, mime: str, filename: str = "") -> str:
    import tempfile as _tf, os as _os

    if mime == "application/pdf":
        try:
            import pdfplumber, io as _io
            with pdfplumber.open(_io.BytesIO(file_bytes)) as pdf:
                text = "\n".join(p.extract_text() or "" for p in pdf.pages)
            if text.strip():
                return text[:10000]
        except Exception:
            pass
        # fallback: base64 via CLI
        with _tf.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(file_bytes)
            tmp = f.name
        try:
            result = run_claude(f"請完整提取並整理呢份PDF文件嘅所有內容，包括標題、段落、數據、重點。保持原有結構。\n\n[附件：{tmp}]")
        finally:
            _os.unlink(tmp)
        return result

    elif mime.startswith("image/"):
        suffix = ".jpg" if "jpeg" in mime else f".{mime.split('/')[-1]}"
        with _tf.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(file_bytes)
            tmp = f.name
        prompt = (
            "請仔細分析呢張圖片。\n"
            "如果係手寫文字/筆記：完整轉錄所有文字內容，保持原有結構。\n"
            "如果係截圖/文件：提取所有文字同數據。\n"
            "如果係產品/場景圖：詳細描述內容、風格、可用於行銷嘅重點。\n"
            "廣東話回答，盡量完整。"
        )
        try:
            result = subprocess.run(
                [CLAUDE_PATH, "-p", prompt, tmp],
                capture_output=True, text=True, timeout=120,
                env={**os.environ, "HOME": "/root"},
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        finally:
            _os.unlink(tmp)
        return "[圖片分析失敗]"

    elif mime in ("text/plain", "text/csv", "text/markdown", "application/json") or \
         any(filename.endswith(ext) for ext in (".txt", ".csv", ".md", ".json")):
        return file_bytes.decode("utf-8", errors="ignore")[:10000]

    elif mime in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",) or \
         filename.endswith(".docx"):
        try:
            import docx
            import io
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            return "[需要安裝 python-docx 才能讀取 Word 文件]"
        except Exception as e:
            return f"[讀取 Word 文件出錯：{e}]"

    return ""


def agent_call(agent_name: str, task: str) -> tuple[str, str]:
    user_msg = f"Stanley 交俾你嘅任務：\n{task}\n\n請根據你嘅角色同專長，提供最完整、最具體、可直接使用嘅成品，唔好省略任何重要細節。"
    model = AGENT_MODELS.get(agent_name, MODEL_FAST)
    timeout = 300 if model == MODEL_HEAVY else 180
    return agent_name, run_with_system(AGENT_PROMPTS[agent_name], user_msg, model, timeout)


# ── Commands ───────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    conversation_history[ALLOWED_USER_ID] = []
    save_history(conversation_history)
    last_content[ALLOWED_USER_ID] = ""
    save_last_content_to_disk(last_content)
    search_st = "✅" if WEB_SEARCH_AVAILABLE else "❌"
    apify_st  = "✅" if (APIFY_AVAILABLE and APIFY_TOKEN) else "❌"
    voice_st = "✅" if (OPENAI_AVAILABLE and OPENAI_API_KEY) else "❌"
    pdf_st   = "✅" if REPORTLAB_AVAILABLE else "❌"
    await update.message.reply_text(
        "Stanley，我係 Amy v4.0 ✅\n\n"
        "全體就位：Anna / Leo / Kai / Toxic / Small / Tony / Rex / Mia\n\n"
        "━━ 支援嘅輸入 ━━\n"
        "📄 PDF  🖼 圖片  ✍️ 手寫圖  📝 Word/TXT/CSV\n"
        "🎙️ 語音訊息  💬 文字指令\n\n"
        "━━ 成品輸出 ━━\n"
        "/pdf [描述] → 生成 PDF 文件\n"
        "/slides [描述] → 生成 PowerPoint\n"
        "/landingpage [描述] → 生成 Landing Page\n"
        "/caption [描述] → IG/小紅書 Caption\n"
        "/reel [主題] → Reels 腳本\n"
        "/copy [需求] → 廣告文案\n\n"
        "━━ 情報工具 ━━\n"
        "/imagine [描述] → AI 圖片 + Prompts\n"
        "/scrape ig @帳號 → IG 競品分析\n"
        "/scrape web [URL] → 抓取網頁內容\n"
        "/xhs [關鍵詞] → 小紅書帖文抓取\n"
        "/research [關鍵詞] → Google 情報搜尋\n"
        "/report → 即時市場 + AI 情報\n"
        "/dreamteam [問題] → 8位教練分析\n\n"
        f"🔍 網絡搜尋：{search_st}  📡 Apify：{apify_st}\n"
        f"🎙️ 語音轉錄：{voice_st}  📄 PDF：{pdf_st}\n"
        "每日 8:45 自動發送情報簡報（頭條新聞 + 行業要聞 + AI 資訊）。\n\n"
        "有咩吩咐？"
    )


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    conversation_history[ALLOWED_USER_ID] = []
    save_history(conversation_history)
    last_content[ALLOWED_USER_ID] = ""
    save_last_content_to_disk(last_content)
    await update.message.reply_text("記憶清除，重新開始。")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    h = conversation_history.get(ALLOWED_USER_ID, [])
    search_st = "✅ 啟用（真實新聞）" if WEB_SEARCH_AVAILABLE else "❌ 需安裝 duckduckgo-search"
    apify_st  = "✅ 啟用" if (APIFY_AVAILABLE and APIFY_TOKEN) else "❌ 需設定 APIFY_API_TOKEN"
    voice_st = "✅ 啟用（Whisper）" if (OPENAI_AVAILABLE and OPENAI_API_KEY) else "❌ 需設定 OPENAI_API_KEY"
    pdf_st   = "✅ 啟用" if REPORTLAB_AVAILABLE else "❌ 需安裝 reportlab"
    dalle_st = "✅ DALL-E 3（真實生成）" if (OPENAI_AVAILABLE and OPENAI_API_KEY) else "⚡ Pollinations.ai（免費）"
    gamma_st = "✅ Gamma AI（專業簡報）" if GAMMA_API_KEY else "❌ 未設定（用 python-pptx）\n   設定：export GAMMA_API_KEY='你的key'"
    pptx_st  = "✅ 啟用" if PPTX_AVAILABLE else "❌ 需安裝 python-pptx"
    await update.message.reply_text(
        f"系統狀態：正常\n"
        f"版本：v4.2\n"
        f"對話記憶：{len(h)} 條（持久化✅）\n\n"
        f"━━ AI 分工模型 ━━\n"
        f"Amy（指揮）：Haiku ⚡\n"
        f"Anna（文案）：Sonnet ✍️\n"
        f"Small（策略）：Opus 🧠\n"
        f"Kai/Mia（情報）：Haiku ⚡\n"
        f"其他員工：Sonnet\n\n"
        f"━━ 外部 AI 工具 ━━\n"
        f"🖼 圖片生成：{dalle_st}\n"
        f"📊 簡報生成：{gamma_st}\n"
        f"📄 PDF：{pdf_st}\n"
        f"🎙️ 語音轉錄：{voice_st}\n"
        f"🔍 網絡搜尋：{search_st}\n"
        f"📡 Apify 爬蟲：{apify_st}"
    )


async def cmd_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    from datetime import datetime
    import io
    h = conversation_history.get(ALLOWED_USER_ID, [])
    lines = [
        f"Stanley Amy Bot — 對話記錄匯出",
        f"匯出時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (HKT)",
        f"總共 {len(h)} 條記錄（最近 50 條）",
        "=" * 50,
        "",
    ]
    for i, msg in enumerate(h, 1):
        role = "👤 你" if msg.get("role") == "user" else "🤖 Amy"
        content = msg.get("content", "")
        if isinstance(content, list):
            content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
        lines.append(f"[{i}] {role}")
        lines.append(content.strip())
        lines.append("")
    lc = last_content.get(ALLOWED_USER_ID, "")
    if lc:
        lines += ["=" * 50, "📄 上次處理嘅內容（節錄）：", lc[:500] + ("..." if len(lc) > 500 else ""), ""]
    usage = _daily_usage.get("calls", 0)
    lines.append(f"今日 API 使用次數：{usage}")
    text = "\n".join(lines)
    buf = io.BytesIO(text.encode("utf-8"))
    buf.name = f"amy_history_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    await update.message.reply_document(document=buf, filename=buf.name, caption=f"匯出完成，共 {len(h)} 條對話記錄。")


async def cmd_imagine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    prompt = " ".join(context.args) if context.args else ""
    if not prompt:
        dalle_on = OPENAI_AVAILABLE and bool(OPENAI_API_KEY)
        await update.message.reply_text(
            "用法：/imagine [描述]\n\n"
            "例子：\n"
            "• /imagine 香港現代痛症診所廣告，專業溫馨\n"
            "• /imagine 美容護膚產品平面廣告，白色背景，高質感\n"
            "• /imagine IG封面圖，美容主題，粉色系\n\n"
            f"圖片引擎：{'✅ DALL-E 3（真實生成）' if dalle_on else '⚡ Pollinations.ai + DALL-E 3 Prompts'}"
        )
        return

    use_dalle = OPENAI_AVAILABLE and bool(OPENAI_API_KEY)
    img_source = "DALL-E 3 (GPT-4o)" if use_dalle else "Pollinations.ai"
    await update.message.reply_text(f"🎨 Anna 處理中（{img_source} 生成圖片，約30-60秒）...")

    loop = asyncio.get_event_loop()
    if use_dalle:
        img_bytes = await loop.run_in_executor(executor, generate_dalle_image, prompt)
        if isinstance(img_bytes, Exception):
            await update.message.reply_text(f"⚠️ 圖片生成失敗：{img_bytes}")
        else:
            await update.message.reply_photo(photo=img_bytes, caption=f"🎨 {img_source}\n描述：{prompt}")
    else:
        img_task = loop.run_in_executor(executor, generate_image_sync, prompt)
        dalle_task = loop.run_in_executor(executor, generate_dalle_prompts, prompt)
        img_bytes, dalle_prompts = await asyncio.gather(img_task, dalle_task, return_exceptions=True)
        if isinstance(img_bytes, Exception):
            await update.message.reply_text(f"⚠️ 圖片生成失敗：{img_bytes}")
        else:
            await update.message.reply_photo(photo=img_bytes, caption=f"🎨 {img_source}\n描述：{prompt}")
        if not isinstance(dalle_prompts, Exception):
            await send_long(update, f"✨ DALL-E 3 優化 Prompts（貼入 ChatGPT → GPT-4o）：\n\n{dalle_prompts}")


async def cmd_scrape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "用法：\n"
            "• /scrape ig @帳號 — 抓取 IG 競品最新帖文 + Leo 分析\n"
            "• /scrape web [URL] — 抓取網頁內容\n\n"
            "例：/scrape ig @beautysignaturehk"
        )
        return

    subcmd = args[0].lower()
    loop = asyncio.get_event_loop()

    def _scrape_failed(r: str) -> bool:
        return any(kw in r for kw in ["失敗", "未設定", "不到資料", "Error", "error", "抓取失敗"])

    def _save_analysis(analysis: str, label: str):
        """分析完成後儲存到 last_content + history，方便後續生成用"""
        last_content[ALLOWED_USER_ID] = analysis[:8000]
        save_last_content_to_disk(last_content)
        h = conversation_history.setdefault(ALLOWED_USER_ID, [])
        h.append({"role": "assistant", "content": f"[{label}]\n{analysis}"})
        save_history(conversation_history)

    _next_steps = (
        "\n💡 分析已儲存！你可以直接用：\n"
        "• /landingpage 根據以上分析生成落地頁\n"
        "• /pdf 生成競品分析報告\n"
        "• /slides 生成競品分析簡報\n"
        "• 或問我：「根據以上分析幫我設計新產品」"
    )

    if subcmd == "ig" and len(args) >= 2:
        username = args[1].lstrip("@")
        await update.message.reply_text(f"📡 用 Instaloader 抓取 IG @{username} 中（約30-60秒）...")
        result = await loop.run_in_executor(executor, scrape_instagram, username)
        if _scrape_failed(result):
            await update.message.reply_text("⚠️ Instaloader 未能直接抓取，改用網絡搜尋 fallback...")
            result = web_search(f"Instagram {username} 最新帖文 內容 美容", 6)
        await send_long(update, result)
        leo_task = (
            f"以下係競品 IG 帳號 @{username} 嘅最新帖文數據，請做完整競品分析：\n\n{result}\n\n"
            f"輸出：① 帳號整體定位 ② 爆款帖文規律 ③ 對 Stanley 美容/痛症業務嘅具體啟示 ④ 可以抄嘅策略"
        )
        _, analysis = await loop.run_in_executor(executor, agent_call, "Leo", leo_task)
        await send_long(update, f"📊 Leo 競品分析：\n{analysis}")
        _save_analysis(analysis, f"IG @{username} 競品分析")
        await update.message.reply_text(_next_steps)

    elif subcmd == "web" and len(args) >= 2:
        url = args[1]
        await update.message.reply_text(f"📡 抓取 {url} 中...")
        result = await loop.run_in_executor(executor, scrape_webpage, url)
        if _scrape_failed(result):
            await update.message.reply_text("⚠️ Instaloader 未能直接抓取，改用網絡搜尋 fallback...")
            result = web_search(url, 5)
        await send_long(update, result)
        leo_task = f"分析以下網頁內容，提出對 Stanley 業務有用嘅洞察：\n\n{result[:3000]}"
        _, analysis = await loop.run_in_executor(executor, agent_call, "Leo", leo_task)
        await send_long(update, f"📊 Leo 分析：\n{analysis}")
        _save_analysis(analysis, f"網頁分析 {url}")
        await update.message.reply_text(_next_steps)

    elif subcmd == "xhs" and len(args) >= 2:
        query = " ".join(args[1:])
        await update.message.reply_text(f"📕 抓取小紅書「{query}」中（約30-60秒）...")
        result = await loop.run_in_executor(executor, scrape_xhs, query)
        if _scrape_failed(result):
            await update.message.reply_text("⚠️ Instaloader 未能直接抓取，改用網絡搜尋 fallback...")
            result = web_search(f"小紅書 {query} 帖文 推薦", 6)
        await send_long(update, result)
        anna_task = (
            f"以下係小紅書「{query}」嘅帖文內容，請分析趨勢：\n\n{result[:3000]}\n\n"
            f"輸出：① 爆款標題規律 ② 熱門話題角度 ③ Stanley 可以用嘅3個文案方向"
        )
        _, analysis = await loop.run_in_executor(executor, agent_call, "Anna", anna_task)
        await send_long(update, f"🎨 Anna 分析：\n{analysis}")
        _save_analysis(analysis, f"小紅書「{query}」趨勢分析")
        await update.message.reply_text(_next_steps)

    elif subcmd == "news" and len(args) >= 2:
        query = " ".join(args[1:])
        await update.message.reply_text(f"🔍 搜尋「{query}」新聞中...")
        result = await loop.run_in_executor(executor, scrape_google, query)
        if _scrape_failed(result):
            result = web_search(query + " 最新消息", 6)
        await send_long(update, result)
        leo_task = f"以下係「{query}」嘅最新搜尋結果，請分析對 Stanley 業務嘅影響同機會：\n\n{result[:3000]}"
        _, analysis = await loop.run_in_executor(executor, agent_call, "Leo", leo_task)
        await send_long(update, f"📊 Leo 分析：\n{analysis}")
        _save_analysis(analysis, f"新聞搜尋「{query}」分析")
        await update.message.reply_text(_next_steps)

    elif subcmd == "threads" and len(args) >= 2:
        username = args[1].lstrip("@")
        await update.message.reply_text(f"🧵 抓取 Threads @{username} 中（約30-60秒）...")
        result = await loop.run_in_executor(executor, scrape_threads, username)
        if _scrape_failed(result):
            await update.message.reply_text("⚠️ Instaloader 未能直接抓取，改用網絡搜尋 fallback...")
            result = web_search(f"Threads {username} 最新帖文 內容", 6)
        await send_long(update, result)
        leo_task = (
            f"以下係競品 Threads 帳號 @{username} 嘅最新內容，請做競品分析：\n\n{result}\n\n"
            f"輸出：① 帳號內容定位 ② 爆款帖文規律 ③ 對 Stanley 業務嘅具體啟示 ④ 可以借鑒嘅策略"
        )
        _, analysis = await loop.run_in_executor(executor, agent_call, "Leo", leo_task)
        await send_long(update, f"📊 Leo 競品分析：\n{analysis}")
        _save_analysis(analysis, f"Threads @{username} 競品分析")
        await update.message.reply_text(_next_steps)

    elif subcmd == "fb" and len(args) >= 2:
        page = args[1].lstrip("@")
        await update.message.reply_text(f"📘 抓取 Facebook @{page} 中...")
        result = await loop.run_in_executor(executor, scrape_facebook, page)
        await send_long(update, result)
        leo_task = (
            f"以下係競品 Facebook 專頁 @{page} 嘅最新帖文，請做競品分析：\n\n{result}\n\n"
            f"輸出：① 專頁內容定位 ② 爆款帖文規律 ③ 對 Stanley 業務嘅具體啟示 ④ 可以借鑒嘅策略"
        )
        _, analysis = await loop.run_in_executor(executor, agent_call, "Leo", leo_task)
        await send_long(update, f"📊 Leo 競品分析：\n{analysis}")
        _save_analysis(analysis, f"Facebook @{page} 競品分析")
        await update.message.reply_text(_next_steps)

    else:
        await update.message.reply_text(
            "用法：\n"
            "• /scrape ig @帳號 — IG 競品分析\n"
            "• /scrape fb @專頁 — Facebook 競品分析\n"
            "• /scrape threads @帳號 — Threads 競品分析\n"
            "• /scrape web [URL] — 網頁內容\n"
            "• /scrape xhs [關鍵詞] — 小紅書帖文\n"
            "• /scrape news [關鍵詞] — Google 新聞搜尋"
        )


async def cmd_xhs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text(
            "用法：/xhs [關鍵詞]\n\n"
            "例子：\n"
            "• /xhs 痛症舒緩\n"
            "• /xhs 美白護膚 香港"
        )
        return
    if not (APIFY_AVAILABLE and APIFY_TOKEN):
        await update.message.reply_text("⚠️ Apify 未設定，請先設定 APIFY_API_TOKEN")
        return
    await update.message.reply_text(f"📕 抓取小紅書「{query}」中（約30-60秒）...")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, scrape_xhs, query)
    await send_long(update, result)
    anna_task = (
        f"以下係小紅書「{query}」嘅帖文，請分析趨勢同文案方向：\n\n{result[:3000]}\n\n"
        f"輸出：① 爆款標題規律 ② 熱門話題角度 ③ Stanley 可以直接用嘅3個文案方向（附範例）"
    )
    _, analysis = await loop.run_in_executor(executor, agent_call, "Anna", anna_task)
    await send_long(update, f"🎨 Anna 分析：\n{analysis}")


async def cmd_research(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text(
            "用法：/research [關鍵詞]\n\n"
            "例子：\n"
            "• /research 香港痛症治療市場\n"
            "• /research 競品美容中心優惠 2025"
        )
        return
    if not (APIFY_AVAILABLE and APIFY_TOKEN):
        await update.message.reply_text("⚠️ Apify 未設定，請先設定 APIFY_API_TOKEN")
        return
    await update.message.reply_text(f"🔍 搜尋「{query}」中...")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, scrape_google, query)
    await send_long(update, result)
    leo_task = (
        f"以下係「{query}」嘅 Google 搜尋結果，請分析對 Stanley 業務嘅影響同機會：\n\n{result[:3000]}\n\n"
        f"輸出：① 核心洞察（3點）② 競品動態 ③ 可立即執行嘅行動建議"
    )
    _, analysis = await loop.run_in_executor(executor, agent_call, "Leo", leo_task)
    await send_long(update, f"📊 Leo 分析：\n{analysis}")


async def cmd_landingpage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return

    description = " ".join(context.args) if context.args else ""
    if not description:
        cached = last_content.get(ALLOWED_USER_ID, "")
        history = conversation_history.get(ALLOWED_USER_ID, [])
        recent = "\n".join(
            f"{'Stanley' if m['role']=='user' else 'Amy'}：{m['content'][:800]}"
            for m in history[-4:]
        )
        if recent or cached:
            context_text = ""
            if recent:
                context_text += f"最近分析：\n{recent}\n\n"
            if cached and not recent:
                context_text += f"參考內容：\n{cached[:3000]}\n\n"
            description = f"根據以下競品分析，生成針對性 Landing Page：\n\n{context_text}"
        else:
            await update.message.reply_text(
                "用法：/landingpage [描述]\n\n"
                "例子：\n"
                "• /landingpage 痛症治療，目標30-60歲，賣點免費初診\n"
                "• /landingpage 美容護膚課程，25-40歲女性，天然成分\n\n"
                "或先用 /scrape 分析競品，再直接 /landingpage 即可自動生成。"
            )
            return

    await update.message.reply_text("🎨 Anna 設計緊，請稍等（約30秒）...")

    user_msg = (
        f"Stanley 需要一個 Landing Page。\n描述：{description}\n\n"
        f"生成完整 HTML Landing Page（單一文件）：\n"
        f"- 用 Tailwind CSS CDN\n"
        f"- 包含：Hero、服務介紹、痛點解決、社會認同（testimonial）、CTA\n"
        f"- 繁體中文，廣東話語氣，手機優先\n"
        f"- 只輸出純 HTML，唔需要解釋"
    )

    loop = asyncio.get_event_loop()
    html_content = await loop.run_in_executor(executor, run_with_system, AGENT_PROMPTS['Anna'], user_msg)

    html_match = re.search(r'```(?:html)?\s*(<!DOCTYPE.*?</html>)\s*```', html_content, re.DOTALL | re.IGNORECASE)
    if html_match:
        html_content = html_match.group(1)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        tmp_path = f.name

    try:
        with open(tmp_path, 'rb') as f:
            await update.message.reply_document(document=f, filename='landing_page.html',
                                                 caption="🎨 Anna 完成！用瀏覽器打開預覽。")
    finally:
        os.unlink(tmp_path)


async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    await update.message.reply_text("📊 生成緊情報簡報，請稍等...")
    await send_daily_report(context.application)


async def cmd_dreamteam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return

    question = " ".join(context.args) if context.args else ""
    if not question:
        await update.message.reply_text(
            "用法：/dreamteam [你嘅問題]\n\n"
            "例子：/dreamteam 我嘅痛症引流策略點樣改善？"
        )
        return

    await update.message.reply_text(
        f"🏆 Dream Team 集結中...\n問題：{question}\n\n8位教練並行分析（約60-90秒）..."
    )

    loop = asyncio.get_event_loop()

    def coach_call(name: str, system_prompt: str) -> tuple[str, str]:
        user_msg = f"Stanley 的問題：{question}\n\n請根據你的專長，提供具體、可執行的建議。"
        model = DREAM_TEAM_MODELS.get(name, MODEL_FAST)
        return name, run_with_system(system_prompt, user_msg, model)

    tasks = [loop.run_in_executor(executor, coach_call, n, p) for n, p in DREAM_TEAM_PROMPTS.items()]
    results = list(await asyncio.gather(*tasks))

    all_responses = ""
    for name, reply in results:
        emoji = DREAM_TEAM_EMOJI.get(name, "🏆")
        msg = f"{emoji} {name}：\n{reply}"
        all_responses += msg + "\n\n"
        await send_long(update, msg)

    synthesis_user = (
        f"以下係8位世界頂尖商業教練嘅意見：\n\n"
        f"問題：{question}\n\n{all_responses}\n\n"
        f"請用廣東話整合核心建議，找出共識、點出分歧、提出最優先嘅3個行動點。格式清晰。"
    )
    synthesis = await loop.run_in_executor(
        executor, run_with_system,
        "你係一個商業策略整合師，廣東話輸出，清晰有力。",
        synthesis_user,
    )
    await send_long(update, f"🏆 Dream Team 整合建議：\n\n{synthesis}")


# ── New output commands ────────────────────────────────────────────────────────

async def cmd_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    if not REPORTLAB_AVAILABLE:
        await update.message.reply_text(
            "⚠️ PDF 功能需要安裝 reportlab：\n"
            "pip install reportlab\n"
            "然後重啟 bot"
        )
        return
    # PTB v21+ 會將 caption 指令路由到 CommandHandler，需要手動讀取附件
    if update.message and update.message.document:
        doc = update.message.document
        file = await context.bot.get_file(doc.file_id)
        file_bytes = await file.download_as_bytearray()
        loop_pre = asyncio.get_event_loop()
        file_content = await loop_pre.run_in_executor(
            executor, extract_file_content, bytes(file_bytes), doc.mime_type or "", doc.file_name or ""
        )
        if file_content.strip():
            last_content[ALLOWED_USER_ID] = file_content[:8000]
            save_last_content_to_disk(last_content)
    description = " ".join(context.args) if context.args else ""
    error_keywords = ["分析失敗", "無法分析", "讀取失敗", "提取失敗", "❌", "⚠️", "error", "Error"]
    if not description:
        cached = last_content.get(ALLOWED_USER_ID, "")
        # 過濾掉錯誤訊息或無用內容，避免生成垃圾 PDF
        if any(kw in cached for kw in error_keywords):
            cached = ""
        history = conversation_history.get(ALLOWED_USER_ID, [])
        recent_msgs = [
            f"{'Stanley' if m['role']=='user' else 'Amy'}：{m['content'][:800]}"
            for m in history[-4:]
            if not any(kw in m['content'] for kw in error_keywords)
        ]
        recent = "\n".join(recent_msgs)
        if recent:
            # 優先用最近對話，避免舊 last_content 影響內容方向
            description = (
                "根據以下最近對話內容整理成專業 PDF 文件。廣東話，結構清晰。\n\n"
                f"最近對話：\n{recent}\n\n"
            )
            await update.message.reply_text("📄 Anna 根據你嘅內容生成 PDF 中（約30秒）...")
        elif cached:
            description = (
                "根據以下內容整理成專業 PDF 文件。廣東話，結構清晰。\n\n"
                f"原始內容：\n{cached[:3000]}"
            )
            await update.message.reply_text("📄 Anna 根據你嘅內容生成 PDF 中（約30秒）...")
        else:
            await update.message.reply_text(
                "用法：/pdf [描述]\n\n"
                "例子：\n"
                "• /pdf 美容療程服務介紹冊，包括護膚、美白、痛症紓緩\n"
                "• /pdf 痛症管理方案提案，目標客戶30-60歲上班族\n"
                "• /pdf 月度業務報告 2025年6月\n\n"
                "或者先 send 你嘅內容，再 /pdf 即可自動生成。"
            )
            return
    else:
        await update.message.reply_text("📄 Anna 撰寫中（約30秒）...")
    user_msg = (
        f"Stanley 需要一份 PDF 文件。主題：{description}\n\n"
        f"輸出格式規則：\n"
        f"- 第一行係文件標題（唔加 #）\n"
        f"- 章節標題用 # 開頭\n"
        f"- 內容專業完整，繁體中文，廣東話語氣\n"
        f"- 長度：800-1500字\n"
        f"只輸出文件內容，唔需要其他說明。"
    )
    loop = asyncio.get_event_loop()
    content = await loop.run_in_executor(executor, run_with_system, AGENT_PROMPTS['Anna'], user_msg)
    lines = content.strip().split('\n')
    title = lines[0].lstrip('#').strip() if lines else description
    body = '\n'.join(lines[1:]) if len(lines) > 1 else content
    try:
        import io as _io
        pdf_bytes = await loop.run_in_executor(executor, generate_pdf_bytes, title, body)
        safe_name = re.sub(r'[^\w\s]', '', title)[:30].strip().replace(' ', '_') or 'document'
        pdf_buf = _io.BytesIO(pdf_bytes)
        await update.message.reply_document(
            document=pdf_buf,
            filename=f"{safe_name}.pdf",
            caption=f"📄 Anna 完成！\n{title}"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ PDF 生成失敗：{e}\n\n文字版本：\n{content[:3000]}")


async def cmd_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    description = " ".join(context.args) if context.args else ""
    if not description:
        await update.message.reply_text(
            "用法：/caption [描述]\n\n"
            "例子：\n"
            "• /caption 痛症初診優惠，本月限定，免費諮詢\n"
            "• /caption 美容護膚療程，天然成分，適合敏感肌"
        )
        return
    await update.message.reply_text("🎨 Anna 撰寫中...")
    user_msg = (
        f"幫 Stanley 寫帖文 caption。主題：{description}\n\n"
        f"輸出兩個版本：\n"
        f"【IG 版】emoji + hook + 正文 + CTA + 5-8個hashtag\n"
        f"【小紅書版】吸睛標題 + 生活化正文 + hashtag\n"
        f"直接輸出，唔需要解釋。"
    )
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, run_with_system, AGENT_PROMPTS['Anna'], user_msg)
    await send_long(update, f"🎨 Anna：\n\n{result}")


async def cmd_reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    topic = " ".join(context.args) if context.args else ""
    if not topic:
        await update.message.reply_text(
            "用法：/reel [主題]\n\n"
            "例子：\n"
            "• /reel 三個痛症舒緩小貼士\n"
            "• /reel 美白療程前後對比，真實客戶效果"
        )
        return
    await update.message.reply_text("🎬 Anna 撰寫 Reels 腳本中...")
    user_msg = (
        f"幫 Stanley 寫 60秒 Instagram Reels 腳本。主題：{topic}\n\n"
        f"嚴格按以下格式：\n"
        f"🎣 0-3秒 Hook：[開場白/動作]\n"
        f"💥 3-15秒 衝突/痛點：[內容]\n"
        f"✅ 15-45秒 解方/展示：[內容]\n"
        f"📣 45-60秒 CTA：[行動呼籲]\n\n"
        f"每段包含：① 旁白台詞 ② 畫面描述 ③ 字幕文字\n"
        f"廣東話，生動有力，直接輸出。"
    )
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, run_with_system, AGENT_PROMPTS['Anna'], user_msg)
    await send_long(update, f"🎬 Anna Reels 腳本：\n\n{result}")


async def cmd_slides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    if not PPTX_AVAILABLE:
        await update.message.reply_text(
            "⚠️ PowerPoint 功能需要安裝 python-pptx：\n"
            "/root/claude-bot/venv/bin/pip install python-pptx\n"
            "然後重啟 bot"
        )
        return
    # PTB v21+ 會將 caption 指令路由到 CommandHandler，需要手動讀取附件
    if update.message and update.message.document:
        doc = update.message.document
        file = await context.bot.get_file(doc.file_id)
        file_bytes = await file.download_as_bytearray()
        loop_pre = asyncio.get_event_loop()
        file_content = await loop_pre.run_in_executor(
            executor, extract_file_content, bytes(file_bytes), doc.mime_type or "", doc.file_name or ""
        )
        if file_content.strip():
            last_content[ALLOWED_USER_ID] = file_content[:8000]
            save_last_content_to_disk(last_content)
    description = " ".join(context.args) if context.args else ""
    error_keywords = ["分析失敗", "無法分析", "讀取失敗", "提取失敗", "❌", "⚠️", "error", "Error"]
    if not description:
        cached = last_content.get(ALLOWED_USER_ID, "")
        if any(kw in cached for kw in error_keywords):
            cached = ""
        history = conversation_history.get(ALLOWED_USER_ID, [])
        recent_msgs = [
            f"{'Stanley' if m['role']=='user' else 'Amy'}：{m['content'][:800]}"
            for m in history[-4:]
            if not any(kw in m['content'] for kw in error_keywords)
        ]
        recent = "\n".join(recent_msgs)
        if cached or recent:
            description = (
                "根據以下對話內容製作幻燈片。若有優化版本請用優化後嘅版本，廣東話，結構清晰。\n\n"
                + (f"最近對話：\n{recent}\n\n" if recent else "")
                + (f"原始內容：\n{cached[:3000]}" if cached else "")
            )
            await update.message.reply_text("📊 Anna 根據你嘅內容製作幻燈片中（約30秒）...")
        else:
            await update.message.reply_text(
                "用法：/slides [描述]\n\n"
                "例子：\n"
                "• /slides 痛症管理服務介紹，5頁\n"
                "• /slides 美容療程套餐提案，目標客戶30-45歲女性\n"
                "• /slides 月度業務報告 2025年6月\n\n"
                "或者先 send 你嘅內容，再 /slides 即可自動生成。"
            )
            return
    else:
        tool = "Gamma AI" if GAMMA_API_KEY else "Anna (python-pptx)"
        await update.message.reply_text(f"📊 {tool} 製作幻燈片中（約30-60秒）...")

    loop = asyncio.get_event_loop()

    # ── Try Gamma API first ──────────────────────────────────────────────────
    if GAMMA_API_KEY:
        content_msg = (
            f"幫 Stanley 製作一份專業 PowerPoint 簡報。主題：{description}\n\n"
            f"包含：背景分析、核心要點、行動建議。繁體中文，廣東話語氣，5-7頁。"
        )
        content_for_gamma = await loop.run_in_executor(
            executor, run_with_system, AGENT_PROMPTS['Anna'], content_msg, AGENT_MODELS['Anna']
        )
        try:
            pptx_bytes, gamma_url = await loop.run_in_executor(
                executor, generate_gamma_pptx, description, content_for_gamma
            )
            import io as _io
            caption = f"📊 Gamma AI 完成！\n標題：{description}"
            if gamma_url:
                caption += f"\n🔗 Gamma 連結：{gamma_url}"
            if pptx_bytes:
                safe_name = re.sub(r'[^\w\s]', '', description)[:30].strip().replace(' ', '_') or 'slides'
                await update.message.reply_document(
                    document=_io.BytesIO(pptx_bytes),
                    filename=f"{safe_name}.pptx",
                    caption=caption
                )
            else:
                await update.message.reply_text(caption)
            return
        except Exception as e:
            logger.warning(f"Gamma API failed, falling back to python-pptx: {e}")
            await update.message.reply_text("⚠️ Gamma API 暫時唔可用，改用 python-pptx 生成...")

    # ── Fallback: python-pptx ────────────────────────────────────────────────
    user_msg = (
        f"幫 Stanley 製作 PowerPoint 幻燈片。主題：{description}\n\n"
        f"請輸出以下 JSON 格式（只輸出 JSON，唔可以有任何其他文字）：\n"
        f'{{"title":"主標題","subtitle":"副標題或日期","slides":[{{"title":"頁標題","points":["重點一","重點二","重點三"]}},{{"title":"頁標題2","points":["重點一","重點二"]}}]}}\n\n'
        f"要求：共 5-7 頁，每頁 3-5 個重點，繁體中文，廣東話語氣，內容專業落地。"
    )
    raw = await loop.run_in_executor(executor, run_with_system, AGENT_PROMPTS['Anna'], user_msg, AGENT_MODELS['Anna'])

    title, subtitle, slides = "", "", []
    try:
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            title = data.get("title", "")
            subtitle = data.get("subtitle", "")
            slides = data.get("slides", [])
    except Exception:
        pass

    if not title or not slides:
        await update.message.reply_text(f"⚠️ 內容解析失敗\n\n原始內容：\n{raw[:2000]}")
        return
    try:
        import io as _io
        pptx_bytes = await loop.run_in_executor(executor, generate_pptx_bytes, title, subtitle, slides)
        safe_name = re.sub(r'[^\w\s]', '', title)[:30].strip().replace(' ', '_') or 'slides'
        await update.message.reply_document(
            document=_io.BytesIO(pptx_bytes),
            filename=f"{safe_name}.pptx",
            caption=f"📊 Anna 完成！{len(slides)} 頁幻燈片\n標題：{title}"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ PowerPoint 生成失敗：{e}")


async def cmd_copy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    request = " ".join(context.args) if context.args else ""
    if not request:
        await update.message.reply_text(
            "用法：/copy [需求]\n\n"
            "例子：\n"
            "• /copy WhatsApp 跟進訊息，客戶上週做完痛症療程\n"
            "• /copy 廣告標題，女性美白療程，A/B 兩版\n"
            "• /copy 電郵邀請客戶回購，語氣溫暖"
        )
        return
    await update.message.reply_text("✍️ Anna 撰寫中...")
    user_msg = (
        f"Stanley 需要以下文案：{request}\n\n"
        f"輸出完整、可直接使用嘅最終版本。廣東話，貼地有力。"
    )
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, run_with_system, AGENT_PROMPTS['Anna'], user_msg)
    await send_long(update, f"✍️ Anna：\n\n{result}")


# ── Message & file handlers ────────────────────────────────────────────────────

async def send_long(update: Update, text: str):
    for i in range(0, len(text), 4096):
        await update.message.reply_text(text[i: i + 4096])


async def maybe_generate_file(update: Update, agent: str, task: str, loop, extra_context: str = "") -> tuple[str, str] | None:
    """若 Anna 被派去生成文件，直接用 Python 生成器，唔經 CLI 工具。"""
    if agent != "Anna":
        return None
    task_lower = task.lower()

    # Build full_task: if other agents have contributed data, prepend it so Anna can use it
    full_task = task
    if extra_context:
        full_task = (
            f"以下係其他員工已完成嘅研究同分析成果，你必須將呢啲內容整合進你嘅成品，唔好忽略任何重要數據：\n\n"
            f"{extra_context}\n\n{'='*50}\n\n"
            f"原始任務：\n{task}"
        )

    if any(kw in task_lower for kw in ["pdf", "pdf文件", "pdf文檔", "報告", "提案"]):
        if not REPORTLAB_AVAILABLE:
            return None
        await update.message.reply_text("📄 Anna 整合所有員工成果，生成 PDF 中（約60秒）...")
        user_msg = (
            f"Stanley 需要一份高質素嘅 PDF 文件。主題及內容如下：\n{full_task}\n\n"
            f"輸出格式：第一行係文件標題（唔加 #），章節標題用 # 開頭，每個章節有足夠嘅細節同數據支撐，繁體中文，廣東話語氣，長度 1500-2500字。"
            f"要求：內容必須完整詳盡，唔好用省略或者草草帶過；如有數據、洞察、建議行動，全部必須列出。只輸出文件內容，唔需要其他說明。"
        )
        content = await loop.run_in_executor(executor, run_with_system, AGENT_PROMPTS['Anna'], user_msg, AGENT_MODELS['Anna'])
        lines = content.strip().split('\n')
        title = lines[0].lstrip('#').strip() if lines else "文件"
        body = '\n'.join(lines[1:]) if len(lines) > 1 else content
        try:
            import io as _io
            pdf_bytes = await loop.run_in_executor(executor, generate_pdf_bytes, title, body)
            safe_name = re.sub(r'[^\w\s]', '', title)[:30].strip().replace(' ', '_') or 'document'
            await update.message.reply_document(
                document=_io.BytesIO(pdf_bytes),
                filename=f"{safe_name}.pdf",
                caption=f"📄 Anna 完成！\n{title}"
            )
            return "Anna", f"PDF 已生成並發送：{title}"
        except Exception as e:
            return "Anna", f"PDF 生成失敗：{e}\n\n文字版：\n{content[:2000]}"

    if any(kw in task_lower for kw in ["slides", "幻燈片", "powerpoint", "簡報", "ppt", ".pptx"]):
        if not PPTX_AVAILABLE and not GAMMA_API_KEY:
            return None
        tool = "Gamma AI" if GAMMA_API_KEY else "Anna"
        await update.message.reply_text(f"📊 {tool} 製作幻燈片中（約30-60秒）...")

        # Try Gamma first
        if GAMMA_API_KEY:
            content_msg = (
                f"幫 Stanley 製作一份專業 PowerPoint 簡報。內容如下：\n{full_task}\n\n"
                f"包含：背景分析、核心要點、行動建議。繁體中文，廣東話語氣，5-7頁。"
            )
            content_for_gamma = await loop.run_in_executor(
                executor, run_with_system, AGENT_PROMPTS['Anna'], content_msg, AGENT_MODELS['Anna']
            )
            try:
                pptx_bytes, gamma_url = await loop.run_in_executor(
                    executor, generate_gamma_pptx, task[:80], content_for_gamma
                )
                import io as _io
                caption = f"📊 Gamma AI 完成！"
                if gamma_url:
                    caption += f"\n🔗 {gamma_url}"
                if pptx_bytes:
                    await update.message.reply_document(
                        document=_io.BytesIO(pptx_bytes),
                        filename="presentation.pptx",
                        caption=caption
                    )
                else:
                    await update.message.reply_text(caption)
                return "Anna", f"Slides 已用 Gamma AI 生成並發送"
            except Exception as e:
                logger.warning(f"Gamma API failed in dispatch: {e}")

        if not PPTX_AVAILABLE:
            return None
        user_msg = (
            f"幫 Stanley 製作 PowerPoint 幻燈片。主題及內容如下：\n{full_task}\n\n"
            f"請輸出以下 JSON 格式（只輸出 JSON，唔可以有任何其他文字）：\n"
            f'{{"title":"主標題","subtitle":"副標題","slides":[{{"title":"頁標題","points":["重點一","重點二","重點三"]}}]}}\n\n'
            f"共 5-7 頁，每頁 3-5 個重點，繁體中文，廣東話語氣。"
        )
        raw = await loop.run_in_executor(executor, run_with_system, AGENT_PROMPTS['Anna'], user_msg, AGENT_MODELS['Anna'])
        title, subtitle, slides = "", "", []
        try:
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                title = data.get("title", "")
                subtitle = data.get("subtitle", "")
                slides = data.get("slides", [])
        except Exception:
            pass
        if title and slides:
            try:
                import io as _io
                pptx_bytes = await loop.run_in_executor(executor, generate_pptx_bytes, title, subtitle, slides)
                safe_name = re.sub(r'[^\w\s]', '', title)[:30].strip().replace(' ', '_') or 'slides'
                await update.message.reply_document(
                    document=_io.BytesIO(pptx_bytes),
                    filename=f"{safe_name}.pptx",
                    caption=f"📊 Anna 完成！{len(slides)} 頁幻燈片\n標題：{title}"
                )
                return "Anna", f"Slides 已生成並發送：{title}，共 {len(slides)} 頁"
            except Exception as e:
                return "Anna", f"Slides 生成失敗：{e}"

    if any(kw in task_lower for kw in ["landing page", "landingpage", "html", "網頁"]):
        await update.message.reply_text("🎨 Anna 設計 Landing Page 中（約30秒）...")
        user_msg = (
            f"Stanley 需要一個 Landing Page。內容如下：\n{full_task}\n\n"
            f"生成完整 HTML Landing Page（單一文件），用 Tailwind CSS CDN，"
            f"包含 Hero、服務介紹、痛點解決、Testimonial、CTA，繁體中文，手機優先。只輸出純 HTML。"
        )
        html = await loop.run_in_executor(executor, run_with_system, AGENT_PROMPTS['Anna'], user_msg, AGENT_MODELS['Anna'])
        html_match = re.search(r'```(?:html)?\s*(<!DOCTYPE.*?</html>)\s*```', html, re.DOTALL | re.IGNORECASE)
        if html_match:
            html = html_match.group(1)
        import tempfile as _tf, os as _os
        with _tf.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html)
            tmp = f.name
        try:
            with open(tmp, 'rb') as f:
                await update.message.reply_document(document=f, filename='landing_page.html',
                                                     caption="🎨 Anna 完成！用瀏覽器打開預覽。")
        finally:
            _os.unlink(tmp)
        return "Anna", "Landing Page HTML 已生成並發送"

    return None


async def run_with_timeout(tasks: list, update: Update, timeout: int = 240, heartbeat: int = 90):
    """Run agent tasks with heartbeat + timeout. Returns results or None on timeout."""
    async def _heartbeat():
        await asyncio.sleep(heartbeat)
        try:
            await update.message.reply_text("⏳ 仲處理緊，Agent 需要多啲時間，請再等一陣...")
        except Exception:
            pass

    hb = asyncio.create_task(_heartbeat())
    try:
        results = list(await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout))
        hb.cancel()
        return results
    except asyncio.TimeoutError:
        hb.cancel()
        await update.message.reply_text("⚠️ 任務超時（超過 4 分鐘），請重新發送指令再試。")
        return None
    except Exception as e:
        hb.cancel()
        logger.error(f"Agent task error: {e}")
        await update.message.reply_text("⚠️ 處理出錯，請重試。")
        return None


async def dispatch_with_content(update: Update, file_content: str, user_intent: str):
    loop = asyncio.get_event_loop()
    history = conversation_history.setdefault(ALLOWED_USER_ID, [])

    last_content[ALLOWED_USER_ID] = file_content[:8000]
    save_last_content_to_disk(last_content)

    combined_input = (
        f"Stanley 上傳咗一份文件，內容如下：\n\n"
        f"{'='*40}\n{file_content[:6000]}\n{'='*40}\n\n"
        f"Stanley 嘅指示：{user_intent or '請分析呢份文件，並產出對我業務最有用嘅成品。'}"
    )

    raw = await loop.run_in_executor(
        executor, run_with_system, AMY_DISPATCH_SYSTEM,
        f"Stanley 最新指令：{combined_input}",
        "claude-haiku-4-5-20251001"
    )

    if "[QUOTA_EXCEEDED]" in raw:
        await update.message.reply_text(QUOTA_EXCEEDED_MSG)
        return

    try:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        data = json.loads(match.group()) if match else {}
    except Exception:
        await send_long(update, f"{AGENT_EMOJI['Amy']} Amy：\n{raw}")
        return

    if data.get("direct_reply"):
        await send_long(update, f"{AGENT_EMOJI['Amy']} Amy：{data['direct_reply']}")
        return

    dispatches = [d for d in data.get("dispatch", []) if d.get("agent") in AGENT_PROMPTS]
    amy_msg = data.get("amy_message", "")

    if not dispatches:
        await send_long(update, f"{AGENT_EMOJI['Amy']} Amy：{amy_msg or raw}")
        return

    agents_names = "、".join(d["agent"] for d in dispatches)
    await send_long(update, f"{AGENT_EMOJI['Amy']} Amy：{amy_msg}\n（調度中：{agents_names}）")

    full_results = ""

    # Step 1: Separate file agents (Anna PDF/slides/html) from analysis agents
    file_dispatches = []
    normal_dispatches = []
    _file_keywords = ["pdf", "pdf文件", "pdf文檔", "slides", "幻燈片", "powerpoint", "簡報", "ppt", ".pptx", "landing page", "landingpage", "html", "網頁", "報告", "提案"]
    for d in dispatches:
        is_file = d["agent"] == "Anna" and any(kw in d["task"].lower() for kw in _file_keywords)
        (file_dispatches if is_file else normal_dispatches).append(d)

    # Step 2: Run analysis agents in parallel first — collect their results
    if normal_dispatches:
        tasks = [loop.run_in_executor(executor, agent_call, d["agent"], d["task"]) for d in normal_dispatches]
        results = await run_with_timeout(tasks, update)
        if results is None:
            return
        for agent_name, reply_text in results:
            if "[QUOTA_EXCEEDED]" in reply_text:
                await update.message.reply_text(QUOTA_EXCEEDED_MSG)
                return
            emoji = AGENT_EMOJI.get(agent_name, "🤖")
            msg = f"{emoji} {agent_name}：\n{reply_text}"
            full_results += msg + "\n\n"
            await send_long(update, msg)

    # Step 3: Run file agents with ALL analysis results so Anna has full context
    combined_context = full_results  # includes all analysis agents' output

    # Amy organises all collected data into a structured creative brief for Anna
    if file_dispatches and combined_context:
        await update.message.reply_text("📋 Amy 整理所有員工成果，為 Anna 準備完整製作簡報...")
        brief_prompt = (
            f"你係 Amy，需要整理一份完整嘅製作簡報俾 Anna。\n\n"
            f"Stanley 嘅原始指令：{combined_input[:1500]}\n\n"
            f"各員工已完成嘅成果：\n{combined_context[:5000]}\n\n"
            f"請整理成一份結構清晰、內容完整嘅製作簡報，包含：\n"
            f"① 成品目標同定位（Stanley 想要咩、用於咩場合）\n"
            f"② 核心數據同洞察（Leo 嘅競品分析、市場數據，全部列出）\n"
            f"③ 策略重點（Small 嘅策略建議，具體列出）\n"
            f"④ 客戶話術同轉化點（Tony 嘅建議，具體列出）\n"
            f"⑤ 建議內容結構（Anna 應該分幾個章節、每個章節講咩）\n"
            f"⑥ 語氣同風格要求\n\n"
            f"輸出一份清晰、完整嘅簡報，讓 Anna 可以完全根據呢份簡報製作最終成品，唔需要再猜或補充。"
        )
        _, structured_brief = await loop.run_in_executor(
            executor, run_with_system, AGENT_PROMPTS['Amy'], brief_prompt, AGENT_MODELS['Amy']
        )
        if "[QUOTA_EXCEEDED]" not in structured_brief:
            combined_context = f"【Amy 製作簡報】\n{structured_brief}"

    for d in file_dispatches:
        file_result = await maybe_generate_file(update, d["agent"], d["task"], loop, extra_context=combined_context)
        if file_result:
            agent_name, reply_text = file_result
            full_results += f"{AGENT_EMOJI.get(agent_name,'🤖')} {agent_name}：\n{reply_text}\n\n"
        else:
            enriched_task = (f"{combined_context}\n\n原始任務：\n{d['task']}") if combined_context else d["task"]
            _, reply_text = await loop.run_in_executor(executor, agent_call, d["agent"], enriched_task)
            emoji = AGENT_EMOJI.get(d["agent"], "🤖")
            msg = f"{emoji} {d['agent']}：\n{reply_text}"
            full_results += msg + "\n\n"
            await send_long(update, msg)

    consolidate_user = (
        f"Stanley 嘅原始指令：{combined_input[:2000]}\n\n"
        f"各 Agent 回覆：\n{full_results}\n\n"
        f"請整合所有 Agent 嘅回覆，突出最重要嘅成品同行動點。"
    )
    summary = await loop.run_in_executor(executor, run_with_system, AGENT_PROMPTS['Amy'], consolidate_user, AGENT_MODELS['Amy'])
    if "[QUOTA_EXCEEDED]" in summary:
        await update.message.reply_text(QUOTA_EXCEEDED_MSG)
        return
    await send_long(update, f"{AGENT_EMOJI['Amy']} Amy 整合：\n{summary}")

    # Save agent outputs to last_content so follow-up "optimize/redo" commands have context
    last_content[ALLOWED_USER_ID] = full_results[:8000]
    save_last_content_to_disk(last_content)

    history.append({"role": "user", "content": combined_input[:3000]})
    history.append({"role": "assistant", "content": summary})
    save_history(conversation_history)

    warning = get_usage_warning()
    if warning:
        await update.message.reply_text(warning)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return

    photo = update.message.photo[-1]
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text("🖼️ 收到圖片，分析中...")

    file = await context.bot.get_file(photo.file_id)
    img_bytes = await file.download_as_bytearray()
    user_intent = update.message.caption or ""

    loop = asyncio.get_event_loop()
    file_content = await loop.run_in_executor(executor, extract_file_content, bytes(img_bytes), "image/jpeg", "photo.jpg")

    await dispatch_with_content(update, file_content, user_intent)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    doc = update.message.document
    if not doc:
        return

    mime = doc.mime_type or ""
    filename = doc.file_name or ""

    type_labels = {
        "application/pdf": "📄 PDF",
        "image/jpeg": "🖼️ 圖片",
        "image/png": "🖼️ 圖片",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "📝 Word",
        "text/plain": "📝 文字",
        "text/csv": "📊 CSV",
    }
    label = type_labels.get(mime, f"📎 {filename}")
    await update.message.reply_text(f"{label} 收到，讀取中...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    file = await context.bot.get_file(doc.file_id)
    file_bytes = await file.download_as_bytearray()
    user_intent = update.message.caption or ""

    supported = (
        mime == "application/pdf" or
        mime.startswith("image/") or
        mime in ("text/plain", "text/csv", "text/markdown", "application/json",
                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document") or
        any(filename.endswith(ext) for ext in (".txt", ".csv", ".md", ".json", ".docx"))
    )

    if not supported:
        await update.message.reply_text(
            f"文件類型 {mime or filename} 暫時唔支援直接讀取。\n"
            "支援：PDF、圖片、Word(.docx)、TXT、CSV、JSON、Markdown\n\n"
            "可以將內容複製貼上俾我。"
        )
        return

    loop = asyncio.get_event_loop()
    file_content = await loop.run_in_executor(executor, extract_file_content, bytes(file_bytes), mime, filename)

    if not file_content.strip():
        await update.message.reply_text("讀取文件失敗，請試下複製內容貼俾我。")
        return

    await dispatch_with_content(update, file_content, user_intent)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    voice = update.message.voice or update.message.audio
    if not voice:
        return
    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        await update.message.reply_text(
            "⚠️ 語音功能需要設定 OpenAI API Key：\n\n"
            "1. 喺 VPS 執行：\n"
            "   export OPENAI_API_KEY='你的key'\n"
            "   echo 'export OPENAI_API_KEY=你的key' >> /root/.bashrc\n"
            "2. pip install openai\n"
            "3. systemctl restart claude-bot"
        )
        return
    await update.message.reply_text("🎙️ 收到錄音，轉錄中...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    file = await context.bot.get_file(voice.file_id)
    audio_bytes = await file.download_as_bytearray()
    loop = asyncio.get_event_loop()
    transcript = await loop.run_in_executor(
        executor, transcribe_audio, bytes(audio_bytes), "voice.ogg"
    )
    if transcript.startswith("["):
        await update.message.reply_text(f"⚠️ {transcript}")
        return
    await update.message.reply_text(f"🎙️ 轉錄結果：\n\n{transcript}")
    await dispatch_with_content(
        update,
        f"[語音訊息轉錄內容]\n{transcript}",
        "請根據以上語音內容，理解 Stanley 嘅意圖，產出相應成品或回應。"
    )


async def handle_followup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ALLOWED_USER_ID:
        return
    agent_name = query.data.split(":", 1)[1]
    outputs = agent_outputs.get(ALLOWED_USER_ID, {})
    agent_ctx = outputs.get(agent_name, last_content.get(ALLOWED_USER_ID, ""))
    follow_up_state[ALLOWED_USER_ID] = {"agent": agent_name, "context": agent_ctx[:4000], "active": True}
    emoji = AGENT_EMOJI.get(agent_name, "🤖")
    await query.message.reply_text(
        f"{emoji} {agent_name} 追問模式啟動！\n\n"
        f"直接問 {agent_name} 任何問題，佢會根據剛才嘅成果回答你。\n"
        f"你問嘅嘢同答案會自動加落去，之後 /pdf /slides /report 生成嘅成品會包含呢啲細節。\n\n"
        f"輸入 /done 退出追問模式。"
    )


async def handle_followup_message(update: Update, context: ContextTypes.DEFAULT_TYPE, state: dict):
    agent_name = state["agent"]
    agent_ctx = state["context"]
    user_question = update.message.text
    loop = asyncio.get_event_loop()
    emoji = AGENT_EMOJI.get(agent_name, "🤖")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    prompt = (
        f"以下係你之前完成嘅分析成果：\n\n{agent_ctx}\n\n{'='*30}\n\n"
        f"Stanley 追問：{user_question}\n\n"
        f"請根據你上面嘅分析，詳細回答 Stanley 嘅追問。如有需要可以補充額外觀點。"
    )
    _, reply_text = await loop.run_in_executor(executor, agent_call, agent_name, prompt)
    h = conversation_history.setdefault(ALLOWED_USER_ID, [])
    h.append({"role": "user", "content": f"[追問 {agent_name}] {user_question}"})
    h.append({"role": "assistant", "content": f"{agent_name}：{reply_text}"})
    save_history(conversation_history)
    updated_ctx = f"{agent_ctx}\n\n【追問 {agent_name}】\n問：{user_question}\n答：{reply_text[:3000]}"
    last_content[ALLOWED_USER_ID] = updated_ctx[:8000]
    save_last_content_to_disk(last_content)
    follow_up_state[ALLOWED_USER_ID]["context"] = updated_ctx[:4000]
    await send_long(update, f"{emoji} {agent_name}：\n{reply_text}")


async def cmd_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    follow_up_state[ALLOWED_USER_ID] = {"active": False}
    await update.message.reply_text(
        "✅ 追問模式結束。\n\n"
        "你嘅追問同答案已經加入記憶。\n"
        "依家可以用 /pdf、/slides、/report 等指令生成包含最新細節嘅成品。"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    user_message = update.message.text
    if not user_message:
        return

    # Follow-up mode: route to specific agent Q&A
    state = follow_up_state.get(ALLOWED_USER_ID, {})
    if state.get("active"):
        if user_message.startswith("/"):
            follow_up_state[ALLOWED_USER_ID] = {"active": False}
        else:
            await handle_followup_message(update, context, state)
            return

    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    history = conversation_history.setdefault(ALLOWED_USER_ID, [])
    loop = asyncio.get_event_loop()

    # 長文字（>200字）自動記住，持久化到磁碟
    if len(user_message) > 200:
        last_content[ALLOWED_USER_ID] = user_message
        save_last_content_to_disk(last_content)

    history_text = ""
    for msg in history[-MAX_HISTORY:]:
        role = "Stanley" if msg["role"] == "user" else "Amy"
        history_text += f"{role}: {msg['content']}\n\n"

    # 短跟進指令自動附上上次內容，解決 Amy「唔記得」問題
    cached = last_content.get(ALLOWED_USER_ID, "")
    content_hint = (
        f"\n\n[Stanley 上次分享嘅內容（可直接使用）：\n{cached[:3000]}]\n"
        if cached and len(user_message) < 200 else ""
    )

    dispatch_user = (
        f"{'對話歷史：' + chr(10) + history_text if history_text else ''}"
        f"{content_hint}"
        f"Stanley 最新指令：{user_message}"
    )
    raw = await loop.run_in_executor(executor, run_with_system, AMY_DISPATCH_SYSTEM, dispatch_user, "claude-haiku-4-5-20251001")

    if "[QUOTA_EXCEEDED]" in raw:
        await update.message.reply_text(QUOTA_EXCEEDED_MSG)
        return

    try:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        data = json.loads(match.group()) if match else {}
    except Exception:
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": raw})
        save_history(conversation_history)
        await send_long(update, f"{AGENT_EMOJI['Amy']} Amy：{raw}")
        return

    if data.get("direct_reply"):
        reply = f"{AGENT_EMOJI['Amy']} Amy：{data['direct_reply']}"
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})
        save_history(conversation_history)
        await send_long(update, reply)
        return

    dispatches = [d for d in data.get("dispatch", []) if d.get("agent") in AGENT_PROMPTS]
    actions = [a for a in data.get("actions", []) if a.get("type") and a.get("param")]
    amy_msg = data.get("amy_message", "")

    if not dispatches and not actions:
        reply = f"{AGENT_EMOJI['Amy']} Amy：{amy_msg or raw}"
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})
        save_history(conversation_history)
        await send_long(update, reply)
        return

    announce_parts = [f"{AGENT_EMOJI['Amy']} Amy：{amy_msg}"] if amy_msg else []
    if actions:
        action_labels = {"scrape_ig": "📡 IG抓取", "scrape_xhs": "📕 小紅書", "scrape_web": "🌐 網頁", "scrape_news": "🔍 新聞搜尋"}
        announce_parts.append("（執行中：" + "、".join(action_labels.get(a["type"], a["type"]) for a in actions) + "）")
    if dispatches:
        announce_parts.append("（調度中：" + "、".join(d["agent"] for d in dispatches) + "）")
    await send_long(update, "\n".join(announce_parts))

    # ── Handle real-execution actions ──────────────────────────────────────────
    apify_ok = APIFY_AVAILABLE and APIFY_TOKEN
    action_context = ""  # accumulates scrape + analysis results to pass to file agents later

    for action in actions:
        atype = action["type"]
        param = action["param"].strip().lstrip("@")
        # scrape_ig uses instaloader (no Apify needed); others need Apify
        if atype in ("scrape_threads", "scrape_xhs", "scrape_web", "scrape_news") and not apify_ok:
            await update.message.reply_text("⚠️ Apify 未設定，請先設定 APIFY_API_TOKEN（見 /status）")
            continue
        def _apify_failed(r: str) -> bool:
            return any(kw in r for kw in ["失敗", "未設定", "不到資料", "Error", "error"])

        if atype == "scrape_fb":
            await update.message.reply_text(f"📘 抓取 Facebook @{param} 中...")
            result = await loop.run_in_executor(executor, scrape_facebook, param)
            await send_long(update, result)
            leo_task = (
                f"以下係競品 Facebook 專頁 @{param} 嘅最新帖文，請做競品分析：\n\n{result}\n\n"
                f"輸出：① 專頁內容定位 ② 爆款帖文規律 ③ 對 Stanley 業務嘅具體啟示 ④ 可以借鑒嘅策略"
            )
            _, analysis = await loop.run_in_executor(executor, agent_call, "Leo", leo_task)
            await send_long(update, f"📊 Leo 競品分析：\n{analysis}")
            action_context += f"【Facebook @{param} 競品分析 by Leo】\n{analysis[:3000]}\n\n"
        elif atype == "scrape_threads":
            await update.message.reply_text(f"🧵 抓取 Threads @{param} 中...")
            result = await loop.run_in_executor(executor, scrape_threads, param)
            await send_long(update, result)
            leo_task = (
                f"以下係競品 Threads 帳號 @{param} 嘅最新內容，請做競品分析：\n\n{result}\n\n"
                f"輸出：① 帳號內容定位 ② 爆款帖文規律 ③ 對 Stanley 業務嘅具體啟示 ④ 可以借鑒嘅策略"
            )
            _, analysis = await loop.run_in_executor(executor, agent_call, "Leo", leo_task)
            await send_long(update, f"📊 Leo 競品分析：\n{analysis}")
            action_context += f"【Threads @{param} 競品分析 by Leo】\n{analysis[:3000]}\n\n"
        elif atype == "scrape_ig":
            await update.message.reply_text(f"📡 抓取 IG @{param} 中（約30-60秒）...")
            result = await loop.run_in_executor(executor, scrape_instagram, param)
            await send_long(update, result)
            leo_task = (
                f"以下係競品 IG 帳號 @{param} 嘅最新帖文數據，請做完整競品分析：\n\n{result}\n\n"
                f"輸出：① 帳號整體定位 ② 爆款帖文規律 ③ 對 Stanley 美容/痛症業務嘅具體啟示 ④ 可以抄嘅策略"
            )
            _, analysis = await loop.run_in_executor(executor, agent_call, "Leo", leo_task)
            await send_long(update, f"📊 Leo 競品分析：\n{analysis}")
            action_context += f"【IG @{param} 原始數據】\n{result[:2000]}\n\n【Leo 競品分析】\n{analysis[:3000]}\n\n"
        elif atype == "scrape_xhs":
            await update.message.reply_text(f"📕 抓取小紅書「{param}」中（約30-60秒）...")
            result = await loop.run_in_executor(executor, scrape_xhs, param)
            await send_long(update, result)
            anna_task = (
                f"以下係小紅書「{param}」帖文內容，請分析趨勢：\n\n{result[:3000]}\n\n"
                f"輸出：① 爆款標題規律 ② 熱門話題角度 ③ Stanley 可以用嘅3個文案方向"
            )
            _, analysis = await loop.run_in_executor(executor, agent_call, "Anna", anna_task)
            await send_long(update, f"🎨 Anna 分析：\n{analysis}")
            action_context += f"【小紅書「{param}」趨勢分析 by Anna】\n{analysis[:3000]}\n\n"
        elif atype == "scrape_web":
            await update.message.reply_text(f"🌐 抓取 {param} 中...")
            result = await loop.run_in_executor(executor, scrape_webpage, param)
            await send_long(update, result)
            action_context += f"【網頁內容 {param}】\n{result[:3000]}\n\n"
        elif atype == "scrape_news":
            await update.message.reply_text(f"🔍 搜尋「{param}」新聞中...")
            result = await loop.run_in_executor(executor, scrape_google, param)
            await send_long(update, result)
            leo_task = f"以下係「{param}」嘅最新搜尋結果，請分析對 Stanley 業務嘅影響同機會：\n\n{result[:3000]}"
            _, analysis = await loop.run_in_executor(executor, agent_call, "Leo", leo_task)
            await send_long(update, f"📊 Leo 分析：\n{analysis}")
            action_context += f"【新聞「{param}」分析 by Leo】\n{analysis[:3000]}\n\n"
        elif atype == "product_research":
            topic = param
            await update.message.reply_text(f"🔬 開始市場研究：「{topic}」\n正在擷取真實數據...")
            # Always use web_search (DuckDuckGo) as primary — reliable, free, no Apify needed
            search_fns = [
                loop.run_in_executor(executor, web_search, topic + " 香港市場趨勢 2025", 6),
                loop.run_in_executor(executor, web_search, topic + " 競品 用戶痛點 新產品 香港", 5),
            ]
            search_results = await asyncio.gather(*search_fns)
            combined_data = "\n\n---\n\n".join(str(r) for r in search_results)[:4000]
            # Supplement with XHS data if Apify available
            if apify_ok:
                xhs_raw = await loop.run_in_executor(executor, scrape_xhs, topic)
                if "失敗" not in xhs_raw and "未設定" not in xhs_raw and "未找到" not in xhs_raw:
                    combined_data += f"\n\n---\n\n【小紅書真實帖文】\n{xhs_raw[:2000]}"
            await update.message.reply_text("✅ 數據擷取完成，Leo + Small 分析緊...")
            leo_task = (
                f"根據以下真實市場數據，分析「{topic}」嘅市場現況：\n\n{combined_data}\n\n"
                f"直接輸出：\n① 市場趨勢同規模\n② 主流產品/服務係乜\n③ 用戶最大痛點\n④ 市場空白位"
            )
            small_task = (
                f"根據以下「{topic}」真實市場數據，識別產品機會：\n\n{combined_data}\n\n"
                f"Stanley 業務背景：香港美容（護膚療程）+ 痛症管理，主要客戶 18-65歲。\n\n"
                f"直接輸出（唔係計劃，係具體可執行嘅結果）：\n"
                f"① 3個市場機會（每個2句描述）\n"
                f"② 2個新產品/服務建議（名稱 + 目標客群 + 核心賣點 + 建議定價）\n"
                f"③ 本週可以立即開始做嘅第一步"
            )
            (_, market_analysis), (_, product_ideas) = await asyncio.gather(
                loop.run_in_executor(executor, agent_call, "Leo", leo_task),
                loop.run_in_executor(executor, agent_call, "Small", small_task),
            )
            await send_long(update, f"📊 Leo — 市場分析：\n{market_analysis}")
            await send_long(update, f"🧠 Small — 產品機會：\n{product_ideas}")
            action_context += f"【市場研究「{topic}」— Leo 市場分析】\n{market_analysis[:2000]}\n\n【Small 產品機會】\n{product_ideas[:2000]}\n\n"

    full_results = ""

    # Step 1: Separate file agents (Anna PDF/slides/html) from analysis agents
    file_dispatches = []
    normal_dispatches = []
    _file_keywords = ["pdf", "pdf文件", "pdf文檔", "slides", "幻燈片", "powerpoint", "簡報", "ppt", ".pptx", "landing page", "landingpage", "html", "網頁", "報告", "提案"]
    for d in dispatches:
        is_file = d["agent"] == "Anna" and any(kw in d["task"].lower() for kw in _file_keywords)
        (file_dispatches if is_file else normal_dispatches).append(d)

    # Step 2: Run analysis agents in parallel first — collect their results
    if normal_dispatches:
        tasks = [loop.run_in_executor(executor, agent_call, d["agent"], d["task"]) for d in normal_dispatches]
        results = await run_with_timeout(tasks, update)
        if results is None:
            return
        agents_ran = []
        for agent_name, reply_text in results:
            if "[QUOTA_EXCEEDED]" in reply_text:
                await update.message.reply_text(QUOTA_EXCEEDED_MSG)
                return
            emoji = AGENT_EMOJI.get(agent_name, "🤖")
            msg = f"{emoji} {agent_name}：\n{reply_text}"
            full_results += msg + "\n\n"
            await send_long(update, msg)
            agent_outputs.setdefault(ALLOWED_USER_ID, {})[agent_name] = reply_text
            agents_ran.append(agent_name)
        if agents_ran:
            buttons = [[InlineKeyboardButton(f"🔍 追問 {n}", callback_data=f"followup:{n}")] for n in agents_ran]
            await update.message.reply_text("💬 想追問任何員工？", reply_markup=InlineKeyboardMarkup(buttons))

    # Step 3: Build combined context from actions + analysis agents, then run file agents
    combined_context = ""
    if action_context:
        combined_context += f"【數據擷取結果】\n{action_context}\n\n"
    if full_results:
        combined_context += f"【分析員成果】\n{full_results}\n\n"

    # Amy organises all collected data into a structured creative brief for Anna
    if file_dispatches and combined_context:
        await update.message.reply_text("📋 Amy 整理所有員工成果，為 Anna 準備完整製作簡報...")
        brief_prompt = (
            f"你係 Amy，需要整理一份完整嘅製作簡報俾 Anna。\n\n"
            f"Stanley 嘅原始指令：{user_message}\n\n"
            f"各員工已完成嘅成果：\n{combined_context[:5000]}\n\n"
            f"請整理成一份結構清晰、內容完整嘅製作簡報，包含：\n"
            f"① 成品目標同定位（Stanley 想要咩、用於咩場合）\n"
            f"② 核心數據同洞察（Leo 嘅競品分析、市場數據，全部列出）\n"
            f"③ 策略重點（Small 嘅策略建議，具體列出）\n"
            f"④ 客戶話術同轉化點（Tony 嘅建議，具體列出）\n"
            f"⑤ 建議內容結構（Anna 應該分幾個章節、每個章節講咩）\n"
            f"⑥ 語氣同風格要求\n\n"
            f"輸出一份清晰、完整嘅簡報，讓 Anna 可以完全根據呢份簡報製作最終成品，唔需要再猜或補充。"
        )
        _, structured_brief = await loop.run_in_executor(
            executor, run_with_system, AGENT_PROMPTS['Amy'], brief_prompt, AGENT_MODELS['Amy']
        )
        if "[QUOTA_EXCEEDED]" not in structured_brief:
            combined_context = f"【Amy 製作簡報】\n{structured_brief}"

    for d in file_dispatches:
        file_result = await maybe_generate_file(update, d["agent"], d["task"], loop, extra_context=combined_context)
        if file_result:
            agent_name, reply_text = file_result
            full_results += f"{AGENT_EMOJI.get(agent_name,'🤖')} {agent_name}：\n{reply_text}\n\n"
        else:
            enriched_task = (f"{combined_context}\n\n原始任務：\n{d['task']}") if combined_context else d["task"]
            _, reply_text = await loop.run_in_executor(executor, agent_call, d["agent"], enriched_task)
            emoji = AGENT_EMOJI.get(d["agent"], "🤖")
            msg = f"{emoji} {d['agent']}：\n{reply_text}"
            full_results += msg + "\n\n"
            await send_long(update, msg)

    all_results = (action_context + full_results).strip()
    consolidate_user = (
        f"Stanley 嘅原始指令：{user_message}\n\n"
        f"各 Agent 回覆：\n{all_results}\n\n"
        f"請整合所有 Agent 嘅回覆，突出最重要嘅行動點。"
    )
    summary = await loop.run_in_executor(executor, run_with_system, AGENT_PROMPTS['Amy'], consolidate_user, AGENT_MODELS['Amy'])
    if "[QUOTA_EXCEEDED]" in summary:
        await update.message.reply_text(QUOTA_EXCEEDED_MSG)
        return
    summary_msg = f"{AGENT_EMOJI['Amy']} Amy 整合報告：\n{summary}"
    await send_long(update, summary_msg)

    # Save all agent outputs to last_content so follow-up "optimize/redo" commands have full context
    if all_results:
        last_content[ALLOWED_USER_ID] = all_results[:8000]
        save_last_content_to_disk(last_content)

    full_reply = f"{AGENT_EMOJI['Amy']} Amy：{amy_msg}\n\n{full_results}\n{summary_msg}"
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": full_reply})
    save_history(conversation_history)

    warning = get_usage_warning()
    if warning:
        await update.message.reply_text(warning)


# ── Daily report (with real web search) ───────────────────────────────────────

async def send_daily_report(app):
    try:
        from datetime import datetime as _dt
        loop = asyncio.get_event_loop()
        date_str = _dt.now().strftime("%Y年%m月%d日")

        search_ok = WEB_SEARCH_AVAILABLE or (APIFY_AVAILABLE and APIFY_TOKEN)
        if search_ok:
            import asyncio as _aio
            hk_news = await loop.run_in_executor(executor, news_search, "香港今日新聞 頭條 最新", 5)
            await _aio.sleep(2)
            biz_news = await loop.run_in_executor(executor, news_search, "香港財經商業 重要消息", 4)
            await _aio.sleep(2)
            ai_raw = await loop.run_in_executor(executor, news_search, "Claude ChatGPT Gemini AI 最新功能 更新", 5)
            await _aio.sleep(2)
            industry_raw = await loop.run_in_executor(executor, news_search, "香港美容 痛症治療 行業動態", 3)

            news_task = (
                f"根據以下今日香港真實新聞搜尋結果，列出5條最重要頭條，每條一句摘要：\n\n"
                f"{hk_news[:2000]}\n\n{biz_news[:1500]}\n\n"
                f"格式（每條一行）：📌 [標題]：[一句摘要]"
            )
            leo_task = (
                f"根據以下搜尋結果，生成香港美容同痛症業務情報（150字內）：\n\n"
                f"{industry_raw[:2000]}\n\n"
                f"輸出：① 今日最重要行業動態 ② 機會或風險 ③ Stanley 今日最應行動嘅一件事"
            )
            kai_task = (
                f"根據以下今日真實 AI 資訊，生成 AI 簡報（150字內）：\n\n"
                f"{ai_raw[:2000]}\n\n"
                f"輸出：① 最重要 AI 動態（只講事實）"
                f"② 對 Stanley 美容/痛症業務嘅直接影響 "
                f"③ 如有免費可用工具：「工具名 — 免費 — 可用於XX」；付費工具略過唔提"
            )
            search_tag = "🔍 真實網絡搜尋（Google）" if (APIFY_AVAILABLE and APIFY_TOKEN) else "🔍 真實網絡搜尋"
        else:
            news_task = (
                f"今日（{date_str}）香港5條重要新聞頭條，每條一句摘要。"
                f"格式：📌 [標題]：[一句摘要]"
            )
            leo_task = (
                "今日香港美容同痛症業務情報（150字內）：\n"
                "① 最新行業趨勢或熱話 ② 競品動態 ③ Stanley 今日最應行動嘅一件事"
            )
            kai_task = (
                "今日全球 AI 市場簡報（150字內）：\n"
                "① 最新 AI 工具或功能更新（只講事實）\n"
                "② AI 用於美容/健康/銷售嘅直接影響\n"
                "③ 如有免費工具：「工具名 — 免費 — 可用於XX」；付費工具略過唔提"
            )
            search_tag = "📚 知識庫"

        agent_tasks = [
            loop.run_in_executor(executor, agent_call, "Leo", news_task),
            loop.run_in_executor(executor, agent_call, "Leo", leo_task),
            loop.run_in_executor(executor, agent_call, "Kai", kai_task),
        ]
        (_, headlines), (_, market), (_, ai_report) = await asyncio.gather(*agent_tasks)

        msg = (
            f"🌅 Stanley，早晨！{date_str} 情報簡報（{search_tag}）\n"
            f"━━━━━━━━━━━━━━\n\n"
            f"📰 今日頭條新聞：\n{headlines}\n\n"
            f"📊 Leo — 行業要聞：\n{market}\n\n"
            f"🤖 Kai — AI 資訊：\n{ai_report}\n\n"
            f"━━━━━━━━━━━━━━\n有咩問題隨時問我！"
        )

        for i in range(0, len(msg), 4096):
            await app.bot.send_message(chat_id=ALLOWED_USER_ID, text=msg[i:i+4096])

    except Exception as e:
        logger.error(f"Daily report error: {e}")


# ── Main ───────────────────────────────────────────────────────────────────────

async def post_init(app):
    scheduler = AsyncIOScheduler(timezone="Asia/Hong_Kong")
    scheduler.add_job(send_daily_report, CronTrigger(hour=8, minute=45), args=[app])
    scheduler.start()


def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("export", cmd_export))
    app.add_handler(CommandHandler("dreamteam", cmd_dreamteam))
    app.add_handler(CommandHandler("landingpage", cmd_landingpage))
    app.add_handler(CommandHandler("pdf", cmd_pdf))
    app.add_handler(CommandHandler("slides", cmd_slides))
    app.add_handler(CommandHandler("caption", cmd_caption))
    app.add_handler(CommandHandler("reel", cmd_reel))
    app.add_handler(CommandHandler("copy", cmd_copy))
    app.add_handler(CommandHandler("report", cmd_report))
    app.add_handler(CommandHandler("imagine", cmd_imagine))
    app.add_handler(CommandHandler("scrape", cmd_scrape))
    app.add_handler(CommandHandler("xhs", cmd_xhs))
    app.add_handler(CommandHandler("research", cmd_research))
    app.add_handler(CommandHandler("done", cmd_done))
    app.add_handler(CallbackQueryHandler(handle_followup_callback, pattern="^followup:"))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Multi-Agent Bot v4.0 啟動")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
