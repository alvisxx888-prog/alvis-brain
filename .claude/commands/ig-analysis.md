# IG 競品分析 Skill

當 Stanley 提供一個或多個 IG 賬號用名（handle），自動完成以下全流程：

1. **抓取目標賬號數據**（Apify Instagram Scraper）
2. **搜尋同類定位競品賬號**（WebSearch）
3. **平行抓取競品賬號數據**
4. **生成視覺化 HTML 報告**，包含：
   - 各賬號 KPI 卡片（粉絲、互動率、平均讚好、評論）
   - 互動率對比圖表
   - 各品牌頭5篇 Post 明細表
   - 定位差異矩陣
   - 具體優化行動建議
   - 90天落地路線圖
5. **以挑戰者模式**指出目標賬號嘅盲點與競爭機會

## 使用方式

```
/ig-analysis @<目標賬號>
/ig-analysis @<目標賬號> vs @<競品1> @<競品2>  # 指定競品
```

例如：
```
/ig-analysis @beautysignaturehk
/ig-analysis @beautysignaturehk vs @vitae.hk @tbm.hk
```

## 執行步驟

### Step 1：取得 Apify API Key
問 Stanley："請提供你的 Apify API Key，或者確認使用上次嘅 key。"

### Step 2：抓取目標賬號

```bash
curl -X POST "https://api.apify.com/v2/acts/apify~instagram-scraper/runs?token=<API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "directUrls": ["https://www.instagram.com/<TARGET_HANDLE>/"],
    "resultsType": "details",
    "resultsLimit": 1
  }'
```

**重要：必須用 `directUrls`，唔好用 `usernames`，否則會 no_items。**

### Step 3：搜尋競品（如冇指定）

用 WebSearch 搜尋：`"香港 <行業類別> Instagram 賬號"` 搵5個定位相近嘅賬號。

### Step 4：平行抓取競品

用 Python 腳本同時啟動多個 Apify run，然後輪詢等待所有完成：

```python
import subprocess, time, json

runs = {}  # { handle: (run_id, dataset_id) }
TOKEN = "<API_KEY>"

for handle in competitor_handles:
    r = subprocess.run([
        "curl","-s","-X","POST",
        f"https://api.apify.com/v2/acts/apify~instagram-scraper/runs?token={TOKEN}",
        "-H","Content-Type: application/json",
        "-d", json.dumps({"directUrls":[f"https://www.instagram.com/{handle}/"],"resultsType":"details","resultsLimit":1})
    ], capture_output=True, text=True)
    d = json.loads(r.stdout)["data"]
    runs[handle] = (d["id"], d["defaultDatasetId"])

pending = set(runs.keys())
while pending:
    for h in list(pending):
        run_id = runs[h][0]
        r = subprocess.run(["curl","-s",f"https://api.apify.com/v2/acts/apify~instagram-scraper/runs/{run_id}?token={TOKEN}"], capture_output=True, text=True)
        st = json.loads(r.stdout)["data"]["status"]
        if st in ("SUCCEEDED","FAILED","ABORTED"):
            pending.discard(h)
    if pending:
        time.sleep(10)
```

### Step 5：提取關鍵數據

每個賬號提取：
- `followersCount`, `followsCount`, `postsCount`
- `biography`, `externalUrl`, `businessCategoryName`
- `latestPosts[]` 頭5篇：`timestamp`, `type`, `likesCount`, `commentsCount`, `caption`

計算 `engagement_rate = avg_likes / followers * 100`

### Step 6：生成 HTML 報告

報告命名：`<target>_competitor_report.html`，儲存到 project 根目錄。

**必須包含以下板塊：**

1. **市場總覽 KPI**（4格）：賬號數、最高互動率、目標互動率、全行評論中位數
2. **各賬號檔案卡**：粉絲/互動率/貼文數/平均讚，定位標籤
3. **4個圖表**（Chart.js）：互動率 bar、粉絲 vs 互動率 bubble、平均讚好橫向、內容類型 donut
4. **各品牌頭5篇 Post 明細表**：日期、類型、摘要、讚好 bar、評論數
5. **定位差異矩陣**：核心差異化/內容多元度/專業可信度/社群建立/轉化路徑/價格透明度/目標客群
6. **優化行動**（6-8個）：每個有問題描述 + 競品對比依據 + 立即行動步驟
7. **90天路線圖**（三欄）：基礎建設/內容升級/轉化優化
8. **最核心洞察**：一段話總結最大機會

**設計規格：**
- 深色背景（#09090f），使用 CSS variables
- Chart.js 4.x CDN
- 響應式 grid layout
- 主色：紫(#a78bfa)、藍(#60a5fa)、綠(#34d399)、紅(#f87171)、黃(#fbbf24)、粉(#f472b6)

### Step 7：挑戰者模式分析

報告完成後，主動指出：
1. 目標賬號嘅最大弱點（唔好只說互動率低，要說為什麼）
2. 競品中最值得借鑑嘅具體做法
3. 整個行業嘅共同盲點（機會所在）
4. 如果係目標公司員工，第一步應該做乜

## 注意事項

- Apify key 係敏感資訊，唔好保存喺文件或 commit
- 若賬號返回 `no_items`，必須改用 `directUrls` 重試
- 平行抓取時用 Python，唔好用 shell until loop（shell `status` 係 read-only variable）
- 結果超過 2KB 時用 python `-c` 解析輸出，唔好直接 print 全部 JSON
- 生成報告後自動 `open` 喺瀏覽器
