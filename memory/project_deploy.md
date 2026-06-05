---
name: project-deploy-netlify
description: 如何將 landing page 部署到 Netlify 並取得可分享連結
metadata: 
  node_type: memory
  type: project
  originSessionId: 2bc27f39-5977-442b-af8e-845b48781894
---

Landing page 用 Netlify Drop 部署，步驟如下：

1. 先確保 `deploy/index.html` 係最新版本（用 Python script 從 `pain_landing_page.html` 生成，logo 已 base64 內嵌）
2. 打開 https://app.netlify.com/drop
3. 打開 Finder 到 `/Users/rickyc./Desktop/Vs code /Project 2 (Pain)/deploy` 資料夾
4. 將整個 **`deploy` 資料夾**拖落 Netlify 網頁虛線框
5. Upload 完後得到 `xxxx.netlify.app` 連結，可直接 send 俾朋友

**Why:** 單一 HTML 檔案，logo base64 內嵌，唔需要 server，Netlify Drop 免費即用。

**How to apply:** 每次修改完 `pain_landing_page.html` 之後，先跑 Python embed script 更新 deploy 資料夾，再重新拖落 Netlify Drop。
