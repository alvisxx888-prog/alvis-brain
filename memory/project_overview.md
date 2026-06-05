---
name: project-overview
description: Alvis 嘅兩個 landing page 項目總覽——痛症版同美容版
metadata: 
  node_type: memory
  type: project
  originSessionId: 2bc27f39-5977-442b-af8e-845b48781894
---

Alvis 係香港美容及痛症管理銷售從業者，喺 Project 2 (Pain) 資料夾有兩個 landing page。

**品牌名稱分工（重要）：**
- 痛症版 → 用 **Alvis**
- 美容版 → 用 **Stanley**
- 兩個係同一個人，但品牌名唔同，唔好混用。

---

## 痛症版 Landing Page

**檔案：**
- `pain_landing_page.html` — 主編輯檔
- `pain_landing_page_deploy.html` — 單檔部署版（logo base64 內嵌）
- `deploy/index.html` — Netlify 用嘅部署版

**定位：** Alvis 痛症健康顧問，局內人角度，唔推銷，直接講
**主色：** Navy #123047 + 霧藍背景 #EAF3F7 + 金色 #D8B76A + Teal CTA #16736B
**主標題：** 痛咗好耐都唔斷尾？可能你一直處理錯方向。
**WhatsApp：** 85260901523

**已完成功能：**
- 醫療病歷卡風格個案區（4個案例）
- 內嵌 SVG 圖示（頸椎、膝關節、坐骨神經、媽媽手）
- Hero 脊椎線稿背景裝飾
- Hero 浮動「免費 WhatsApp 痛症方向分析」小卡
- WhatsApp 表單提交（唔用 window.open，用 anchor click）
- FAQ 手風琴
- Netlify 可部署

---

## 美容版 Landing Page

**檔案：**
- `beauty_landing_page.html` — 主編輯檔
- `deploy_beauty/index.html` — Netlify 用嘅部署版

**定位：** Stanley 美容顧問，親身體驗分享，唔推銷，直接講
**主色：** Navy #1A2540 + 暖奶油背景 #FAF4EE + 玫瑰金 #B87860 + 金色 #C9A870
**主標題：** 護膚品換咗一個又一個，可能你一直揀錯方向。
**WhatsApp：** 85260901523（同痛症版）
**名稱：** Stanley（唔係 Alvis）

**涵蓋服務：** 護膚 / 面部療程、纖體 / 身形管理
**目標客群：** 18-35年輕女性、35-55熟齡女性、男士、產後媽媽

**已完成功能：**
- Beauty Diary 卡風格個案區（4個案例：暗瘡、熟齡緊緻、產後纖體、男士護膚）
- 內嵌 SVG 圖示（面部、熟齡、纖體身形、男士）
- Hero 幾何圓圈美容裝飾背景
- Hero 浮動「免費 WhatsApp 護膚方向分析」小卡
- ✦ 閃石浮動裝飾
- FAQ 手風琴
- Netlify 可部署

**待更新（已確認）：**
1. 公司有新 game / promotion 時加落去
2. 儀器資料——Stanley 遲啲會提供公司儀器嘅詳細資料，加入美容版 landing page，令頁面內容更豐富，客戶亦可以針對儀器資料製作文案

---

## 部署方法

兩個版本都用 Netlify Drop：
- 痛症版：拖 `deploy` 資料夾
- 美容版：拖 `deploy_beauty` 資料夾
- 詳見 [[project-deploy-netlify]]

**Why:** 每次修改主檔後要重新跑 Python embed script 更新 deploy 資料夾先可以部署。
