from __future__ import annotations

import re
import urllib.request
from html.parser import HTMLParser

from duckduckgo_search import DDGS

from app.config import settings


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "noscript"}:
            self.skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"}:
            self.skip = False

    def handle_data(self, data: str) -> None:
        if not self.skip:
            text = re.sub(r"\s+", " ", data).strip()
            if text:
                self.parts.append(text)


def web_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    parser = TextExtractor()
    parser.feed(html)
    return "\n".join(parser.parts)[:6000]


def search_text(query: str, max_results: int = 6) -> str:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    lines = [f"搜尋結果：{query}\n"]
    for i, item in enumerate(results, 1):
        lines.append(f"{i}. {item.get('title', '')}\n{item.get('body', '')}\n{item.get('href', '')}\n")
    return "\n".join(lines)


def _apify_items(actor: str, run_input: dict) -> list[dict]:
    if not settings.apify_api_token:
        raise RuntimeError("Apify 未設定。請喺 .env 加 APIFY_API_TOKEN。")
    from apify_client import ApifyClient

    client = ApifyClient(settings.apify_api_token)
    run = client.actor(actor).call(run_input=run_input)
    dataset_id = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]
    return list(client.dataset(dataset_id).iterate_items())


def _search_fallback(query: str, max_results: int = 6) -> str:
    return search_text(query, max_results)


def scrape_instagram(username: str, max_posts: int = 12) -> str:
    """Fetch public Instagram posts with Instaloader first, then search fallback."""
    clean = username.lstrip("@").strip()
    try:
        import instaloader

        loader = instaloader.Instaloader(
            quiet=True,
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
        )
        profile = instaloader.Profile.from_username(loader.context, clean)
        lines = [f"IG @{clean}（{profile.followers:,} followers）最新 {max_posts} 帖：\n來源：Instaloader public scrape\n"]
        for i, post in enumerate(profile.get_posts()):
            if i >= max_posts:
                break
            caption = (post.caption or "無 caption")[:250]
            ts = post.date_local.strftime("%Y-%m-%d")
            lines.append(f"{i + 1}. [{ts}] likes={post.likes} comments={post.comments}\n{caption}\n")
        return "\n".join(lines)
    except Exception as exc:
        fallback = _search_fallback(f"Instagram {clean} 最新帖文 內容 Instaloader失敗：{exc}", 6)
        return (
            f"Instaloader 抓唔到 @{clean}，可能係 IG 限制公開讀取、帳號私人/不存在、login required、rate limit 或網絡問題。\n"
            f"錯誤：{exc}\n\n"
            "以下係 Search fallback，唔係直接由 IG profile 抓出嚟，準確度會低啲：\n\n"
            f"{fallback}"
        )


def apify_instagram(username: str, max_posts: int = 12) -> str:
    return scrape_instagram(username, max_posts)


def scrape_facebook(page_name: str, max_posts: int = 10) -> str:
    clean = page_name.lstrip("@").strip()
    try:
        from facebook_scraper import get_posts

        lines = [f"Facebook @{clean} 最新 {max_posts} 帖：\n"]
        count = 0
        for post in get_posts(clean, pages=3, timeout=30):
            if count >= max_posts:
                break
            text = (post.get("text") or post.get("post_text") or "無文字")[:250]
            likes = post.get("likes") or 0
            comments = post.get("comments") or 0
            shares = post.get("shares") or 0
            t = post.get("time")
            ts = t.strftime("%Y-%m-%d") if t else ""
            lines.append(f"{count + 1}. [{ts}] likes={likes} comments={comments} shares={shares}\n{text}\n")
            count += 1
        if count:
            return "\n".join(lines)
    except Exception:
        pass
    return _search_fallback(f"Facebook {clean} 最新帖文 內容", 6)


def scrape_threads(username: str, max_posts: int = 12) -> str:
    clean = username.lstrip("@").strip()
    try:
        items = _apify_items(
            "apify/threads-scraper",
            {"username": [clean], "resultsLimit": max_posts},
        )
        if not items:
            return f"Threads @{clean} 抓取唔到資料。"
        lines = [f"Threads @{clean} 最新 {len(items)} 帖：\n"]
        for i, item in enumerate(items, 1):
            likes = item.get("likeCount") or item.get("likesCount") or 0
            replies = item.get("replyCount") or item.get("repliesCount") or 0
            text = (item.get("text") or item.get("caption") or "無文字")[:250]
            ts = (item.get("timestamp") or item.get("createdAt") or "")[:10]
            lines.append(f"{i}. [{ts}] likes={likes} replies={replies}\n{text}\n")
        return "\n".join(lines)
    except Exception as exc:
        return _search_fallback(f"Threads @{clean} 最新帖文 內容 {exc}", 6)


def scrape_google(query: str, max_results: int = 8) -> str:
    try:
        items = _apify_items(
            "apify/google-search-scraper",
            {
                "queries": [query],
                "maxPagesPerQuery": 1,
                "resultsPerPage": max_results,
                "countryCode": "hk",
                "languageCode": "zh-TW",
            },
        )
        results = items[0].get("organicResults", []) if items else []
        if not results:
            results = items
        lines = [f"Google「{query}」搜尋結果：\n"]
        for i, item in enumerate(results[:max_results], 1):
            title = item.get("title") or ""
            snippet = item.get("description") or item.get("snippet") or ""
            link = item.get("url") or item.get("link") or ""
            lines.append(f"{i}. {title}\n{snippet[:250]}\n{link}\n")
        return "\n".join(lines)
    except Exception:
        return _search_fallback(query, max_results)


def apify_xhs(query: str, max_posts: int = 10) -> str:
    try:
        items = _apify_items(
            "microworlds/xiaohongshu-scraper",
            {"keyword": query, "maxItems": max_posts},
        )
    except Exception as exc:
        return f"小紅書抓取失敗：{exc}"
    if not items:
        return f"小紅書搵唔到「{query}」資料。"
    lines = [f"小紅書「{query}」結果：\n"]
    for i, item in enumerate(items[:max_posts], 1):
        lines.append(
            f"{i}. {item.get('title') or item.get('name') or ''}\n"
            f"{(item.get('description') or item.get('content') or item.get('text') or '')[:250]}\n"
            f"{item.get('url') or ''}\n"
        )
    return "\n".join(lines)
