---
name: feedback-project2-pain-permissions
description: Permission behaviour for Project 2 (Pain) — auto-allow everything except deletions and major decisions
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2bc27f39-5977-442b-af8e-845b48781894
---

喺 Project 2 (Pain) 工作時，所有操作自動執行，唔需要問用戶確認。

**Why:** 用戶明確要求唔想被打斷，已設定 bypassPermissions。

**How to apply:**
- Read / Edit / Write / Bash / 任何工具 → 直接做，唔問
- 刪除檔案或資料 → 先問用戶意見
- 重大決定（例如改變整體策略、大規模重構、影響生產環境） → 先問用戶意見
