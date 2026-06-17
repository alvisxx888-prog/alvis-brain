from __future__ import annotations


def route_agents(text: str) -> list[str]:
    """Cheap local router. It avoids an AI call just to decide who should answer."""
    t = text.lower()
    routes: list[str] = []

    def add(agent: str) -> None:
        if agent not in routes:
            routes.append(agent)

    if any(k in t for k in ["caption", "ig", "小紅書", "reel", "文案", "廣告文", "landing", "post", "內容"]):
        add("Tiffany")
    if any(k in t for k in ["競品", "市場", "趨勢", "research", "分析", "情報", "行業"]):
        add("Leo")
    if any(k in t for k in ["ai", "chatgpt", "claude", "gemini", "grok", "工具", "prompt"]):
        add("Kelvin")
    if any(k in t for k in ["自動化", "vps", "bot", "telegram", "apify", "n8n", "make", "流程"]):
        add("Emily")
    if any(k in t for k in ["策略", "定位", "方向", "盲點", "商業", "資源", "優先"]):
        add("Alan")
    if any(k in t for k in ["客戶", "成交", "跟進", "whatsapp", "dm", "諮詢", "反對"]):
        add("Dixon")
    if any(k in t for k in ["meta", "ads", "廣告投放", "cpl", "ctr", "roas", "受眾", "預算"]):
        add("Sharon")
    if any(k in t for k in ["數據", "roi", "漏斗", "轉化", "報表", "成效", "追蹤"]):
        add("Dorothy")

    return routes or ["Jasmine"]
