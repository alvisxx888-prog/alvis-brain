---
name: project-command-panel
description: Command Panel 工作台現狀同升級計劃——A方案已建立，B方案待升級
metadata: 
  node_type: memory
  type: project
  originSessionId: d64dcbe4-68a1-400c-a357-4be334209885
---

Alvis 想要一個跨設備工作台，可以喺手機或電腦指派任務俾 AI 員工自動執行並生成結果。

**Why:** 佢有時用手機做嘢，唔方便返電腦用 VS Code，希望隨時隨地都可以下達任務。

---

## A 方案（已完成）

**檔案：** `command_panel/index.html`
**部署：** 需要拖落 Netlify Drop → 得到公開 URL，任何設備可開

**功能：**
- 手機友好介面（iOS Safari 可加入主畫面）
- 選擇 8 個 Agent（Amy / Anna / Leo / Toxic / Small / Tony / Rex / Mia）
- 快速模板 + 任務填寫 + 緊急程度選擇
- 自動格式化任務指令 → 一鍵複製
- 團隊狀態頁 + Brief 頁

**限制：** 靜態頁面，無後端。生成嘅指令仍需手動複製貼入 VS Code 才執行。唔係自動執行。

---

## B 方案（待升級）

Alvis 明確表示想要呢個效果：**喺 Command Panel 填任務 → 後台自動執行 → 結果直接顯示**，唔需要返電腦。

**需要材料：**
1. Claude API Key（從 console.anthropic.com 申請，約 $5 USD/月起）
2. 後端服務（Vercel 免費版可行）

**How to apply:** 下次 Alvis 提返呢件事，直接問佢係咪已經申請咗 API Key，有就立即開始建 B 方案。
