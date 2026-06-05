from fpdf import FPDF
import os

OUTPUT_PATH = "/Users/rickyc./Desktop/Vs code /Project 2 (Stanley)/Stanley_痛症IG_30日執行手冊_v2.pdf"
FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"

class PDF(FPDF):
    def header(self):
        self.set_font("ArialUnicode", "B", 9)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(27, 58, 107)
        self.cell(0, 8, "Stanley | 痛症方案顧問 | IG 30日執行手冊 v2.0 | 2026年5月更新", fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("ArialUnicode", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 6, f"第 {self.page_no()} 頁", align="C")

    def add_fonts(self):
        self.add_font("ArialUnicode", "", FONT_PATH)
        self.add_font("ArialUnicode", "B", FONT_PATH)
        self.add_font("ArialUnicode", "I", FONT_PATH)

    def ch_title(self, title):
        self.set_font("ArialUnicode", "B", 14)
        self.set_text_color(27, 58, 107)
        self.set_fill_color(235, 240, 255)
        self.cell(0, 10, title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def section_bar(self, title, bg=(42, 157, 143), fg=(255, 255, 255)):
        self.set_font("ArialUnicode", "B", 10)
        self.set_text_color(*fg)
        self.set_fill_color(*bg)
        self.cell(0, 7, "  " + title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text):
        self.set_font("ArialUnicode", "", 9)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")

    def bullet(self, text, color=(27, 58, 107)):
        self.set_font("ArialUnicode", "", 9)
        self.set_text_color(*color)
        self.cell(5, 5, "•")
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")

    def box(self, text, bg=(245, 250, 255), border=(27, 58, 107)):
        self.set_fill_color(*bg)
        self.set_draw_color(*border)
        self.set_font("ArialUnicode", "", 9)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5, text, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def warn(self, text):
        self.set_fill_color(255, 248, 220)
        self.set_draw_color(200, 140, 0)
        self.set_font("ArialUnicode", "B", 9)
        self.set_text_color(140, 80, 0)
        self.multi_cell(0, 5, "  [!]  " + text, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def upgrade_tag(self, text):
        self.set_fill_color(220, 245, 220)
        self.set_draw_color(40, 130, 80)
        self.set_font("ArialUnicode", "B", 9)
        self.set_text_color(30, 100, 50)
        self.multi_cell(0, 5, "  [v2 更新]  " + text, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def day_bar(self, num, wd, task, fmt):
        self.set_font("ArialUnicode", "B", 10)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(27, 58, 107)
        self.cell(22, 7, f"Day {num}", fill=True)
        self.set_fill_color(42, 157, 143)
        self.cell(18, 7, wd, fill=True)
        self.set_fill_color(55, 75, 115)
        self.cell(0, 7, f"  {task}  [{fmt}]", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def day_bar_new(self, num, wd, task, fmt):
        self.set_font("ArialUnicode", "B", 10)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(27, 58, 107)
        self.cell(22, 7, f"Day {num}", fill=True)
        self.set_fill_color(42, 157, 143)
        self.cell(18, 7, wd, fill=True)
        self.set_fill_color(30, 100, 50)
        self.cell(0, 7, f"  {task}  [{fmt}]  ★NEW", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def table_header(self, cols, widths):
        self.set_font("ArialUnicode", "B", 9)
        self.set_fill_color(27, 58, 107)
        self.set_text_color(255, 255, 255)
        for c, w in zip(cols, widths):
            self.cell(w, 6, c, border=1, fill=True)
        self.ln()

    def table_row(self, cols, widths, highlight=False):
        self.set_font("ArialUnicode", "", 9)
        if highlight:
            self.set_fill_color(220, 245, 220)
        else:
            self.set_fill_color(245, 247, 252)
        self.set_text_color(40, 40, 40)
        for c, w in zip(cols, widths):
            self.cell(w, 6, c, border=1, fill=True)
        self.ln()

    def divider(self):
        self.set_draw_color(200, 210, 230)
        self.line(self.l_margin, self.get_y(), self.l_margin + 170, self.get_y())
        self.ln(2)

    def slide_label(self, name):
        self.set_font("ArialUnicode", "B", 9)
        self.set_text_color(42, 157, 143)
        self.cell(0, 5, "  >> " + name, new_x="LMARGIN", new_y="NEXT")


pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_fonts()

# ── COVER ────────────────────────────────────────────────────
pdf.add_page()
pdf.set_font("ArialUnicode", "B", 26)
pdf.set_fill_color(27, 58, 107)
pdf.rect(0, 0, 210, 297, "F")

pdf.set_y(45)
pdf.set_text_color(255, 255, 255)
pdf.cell(0, 14, "Stanley", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("ArialUnicode", "B", 17)
pdf.set_text_color(42, 157, 143)
pdf.cell(0, 10, "痛症 IG 30日完整執行手冊", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)
pdf.set_font("ArialUnicode", "", 11)
pdf.set_text_color(180, 200, 230)
pdf.cell(0, 7, "從零開始 | 品牌視覺 | 每日任務 | 完整文案 | 影片腳本", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)
pdf.set_font("ArialUnicode", "B", 11)
pdf.set_text_color(255, 255, 255)
pdf.cell(0, 7, "痛症方案顧問 | 個人品牌 IG 引流", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(12)

pdf.set_font("ArialUnicode", "B", 12)
pdf.set_text_color(220, 245, 220)
pdf.cell(0, 8, "v2.0 重大更新：三個原創系列正式整合", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("ArialUnicode", "", 9)
pdf.set_text_color(160, 200, 160)
pdf.cell(0, 6, "局內人說話 | 香港人痛症地圖 | 痛症性格類型", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)
pdf.set_font("ArialUnicode", "", 9)
pdf.set_text_color(160, 200, 160)
pdf.cell(0, 6, "CTA 全面升級 | 核武帖加強版", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.ln(28)
pdf.set_font("ArialUnicode", "", 9)
pdf.set_text_color(120, 150, 190)
pdf.cell(0, 6, "更新日期：2026年5月17日", align="C", new_x="LMARGIN", new_y="NEXT")

# ── TOC ──────────────────────────────────────────────────────
pdf.add_page()
pdf.ch_title("目錄")
toc = [
    ("第一部分", "品牌視覺系統", "設定顏色、字體、Logo"),
    ("第二部分", "三個原創系列框架【v2 新增】", "局內人說話 | 痛症地圖 | 性格類型"),
    ("第三部分", "30日行程總覽【v2 更新】", "每日任務一覽表（整合三個原創系列）"),
    ("第四部分", "Week 1 詳細指引", "Day 1-7：帳號建立期"),
    ("第五部分", "Week 2 詳細指引【v2 更新】", "Day 8-14：內容引流期（含局內人說話）"),
    ("第六部分", "Week 3 詳細指引【v2 更新】", "Day 15-21：互動爆發期（含痛症地圖）"),
    ("第七部分", "Week 4 詳細指引【v2 更新】", "Day 22-30：深化建立期（含性格類型）"),
    ("第八部分", "每日互動任務", "15分鐘例行公事"),
    ("第九部分", "開始前準備清單", "Day 1 前必須搞掂"),
    ("附錄", "完整 Caption 文案索引", "所有帖子文案（含 v2 新增）"),
]
for part, title, desc in toc:
    self = pdf
    is_new = "v2" in title
    pdf.set_font("ArialUnicode", "B", 10)
    if is_new:
        pdf.set_text_color(30, 100, 50)
    else:
        pdf.set_text_color(27, 58, 107)
    pdf.cell(40, 7, part)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(80, 7, title)
    pdf.set_font("ArialUnicode", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, desc, new_x="LMARGIN", new_y="NEXT")
    pdf.divider()

# ── PART 1: BRAND ────────────────────────────────────────────
pdf.add_page()
pdf.ch_title("第一部分：品牌視覺系統")
pdf.body("一次設定，全部沿用。開始之前先喺 Canva 建立以下品牌設定。")
pdf.ln(2)

pdf.section_bar("品牌顏色（Hex Code）")
pdf.table_header(["用途", "顏色名稱", "Hex Code"], [80, 40, 50])
for r in [("主色（背景/標題）","深藍","#1B3A6B"),("底色","純白","#FFFFFF"),("點綴色（重點字）","青綠","#2A9D8F")]:
    pdf.table_row(list(r), [80, 40, 50])
pdf.ln(3)

pdf.section_bar("字體設定（Canva 搜尋）")
pdf.table_header(["用途", "字體名稱"], [60, 110])
pdf.table_row(["標題用字", "Noto Sans TC Bold"], [60, 110])
pdf.table_row(["內文用字", "Noto Sans TC Regular"], [60, 110])
pdf.ln(3)

pdf.section_bar("固定署名")
pdf.box("每張 Carousel 頁面右下角或左下角加上：\nStanley｜痛症方案顧問\n字體 8-9pt，深藍色或白色（視乎背景）")

pdf.section_bar("Canva 設定步驟")
steps = [
    "1. 登入 Canva → 右上角按你的名字 → Brand Kit",
    "2. 新增品牌顏色：#1B3A6B（深藍）、#FFFFFF（白）、#2A9D8F（青綠）",
    "3. 設定字體：標題 Noto Sans TC Bold，內文 Noto Sans TC Regular",
    "4. 儲存後，之後新增設計時可以一鍵套用",
    "5. IG 帖尺寸：1080x1080px（方形），Reels 封面：1080x1920px",
]
for s in steps:
    pdf.bullet(s)
pdf.ln(2)

# ── PART 2: THREE ORIGINAL SERIES (NEW) ──────────────────────
pdf.add_page()
pdf.ch_title("第二部分：三個原創系列框架【v2 新增】")
pdf.upgrade_tag("呢三個系列係 v2 最大升級——差異化同病毒傳播力嘅核心武器。")
pdf.body("一般痛症 IG 只係分享知識，你嘅三個原創系列令你成為唯一「局內人視角」帳號。")
pdf.ln(3)

pdf.section_bar("系列一：局內人說話", bg=(27,58,107))
pdf.box("""定位：銷售員視角揭露行業真相，業界人知但唔敢公開講嘅事
差異化：普通 IG 係教你知識，你係告訴你幕後現實
內容方向舉例：
• 「為什麼醫生唔推薦你做衝擊波？——唔係療效問題」
• 「診所點樣決定推薦你做哪種療法（真相）」
• 「為什麼做完好，停咗又痛——從業員角度解釋」
• 「物理治療 vs 儀器治療——點解咁多人揀錯」

格式建議：Carousel 4-5頁（深藍背景為主，字大，震撼感）
CTA：「DM 我『評估』，15分鐘電話了解你情況——局內人同你講清楚」
發佈節奏：每兩週一次（Day 11 / Day 25）""")

pdf.section_bar("系列二：香港人痛症地圖", bg=(100, 60, 150))
pdf.box("""定位：本地化場景，令香港人一睇就「係呀我」
差異化：唔係一般教育內容，係你自己嘅生活場景，極高認同感
內容方向舉例：
• 「港鐵打工仔篇：地鐵頸痛的三個元兇」
• 「茶樓篇：飲茶坐姿點解係腰痛炸彈」
• 「打麻雀篇：四圈麻雀完結後你嘅腰會有幾咁慘」
• 「爬唐樓篇：膝蓋唔夠力嘅人最驚嘅事」

格式建議：Reel 30-45秒（幽默輕鬆語氣，可以有輕微自嘲感）
CTA：「你係邊類痛症香港人？Comment 你最中嘅情況」
發佈節奏：每兩週一次（Day 20 / 下個月）""")

pdf.section_bar("系列三：痛症性格類型", bg=(170, 80, 30))
pdf.box("""定位：互動分類內容，讀者極易轉發俾朋友（病毒傳播機制）
差異化：唔係教你知識，而係幫你「認識自己」——人天生愛分類
內容類型：
• 「你係哪種痛症人？忍痛型 / Panadol型 / 就係唔去睇醫生型 / Google到死型」
• 「痛症4種反應：你係哪類？點解唔同反應有唔同後果」
• 「你識唔識的痛症盲點：你屬於哪種？」

格式建議：Carousel 4-6頁（每頁一種類型，最後一頁問「你係哪類？」）
設計風格：可以較輕鬆，用emoji圖示，唔使太嚴肅
CTA：「Tag 一個你認識嘅[類型名]朋友」/ 「Comment 你係哪一類」
發佈節奏：每個月一次（Day 23），係最適合病毒傳播嘅高互動帖""")

pdf.warn("三個原創系列唔係孤立——做完「局內人說話」之後，轉到「香港人痛症地圖」放鬆語氣，再用「性格類型」炒熱互動。節奏係認真 → 輕鬆 → 互動。")

# ── PART 3: UPDATED SCHEDULE ─────────────────────────────────
pdf.add_page()
pdf.ch_title("第三部分：30日行程總覽【v2 更新版】")
pdf.upgrade_tag("綠色底色 = v2 新增帖（三個原創系列整合）；其他維持原有計劃。")
pdf.table_header(["日期","星期","任務","格式","重要度"], [18,16,96,26,14])
schedule = [
    ("Day 1","一","帳號介紹 Carousel","Carousel","★★★", False),
    ("Day 2","二","Story：投票問卷","Story","★★", False),
    ("Day 3","三","個人故事 Reel","Reel","★★★★", False),
    ("Day 4","四","Story：Q&A","Story","★★", False),
    ("Day 5","五","互動日（無發帖）","互動","★", False),
    ("Day 6","六","Story：日常分享","Story","★★", False),
    ("Day 7","日","互動日","互動","★", False),
    ("Day 8","一","個案分享 #1 Carousel","Carousel","★★★★", False),
    ("Day 9","二","Story：頸痛延伸貼士","Story","★★", False),
    ("Day 10","三","迷思破解 Reel（熱敷vs凍敷）","Reel","★★★★", False),
    ("Day 11","二","【局內人說話 #1】行業真相 Carousel","Carousel","★★★★★", True),
    ("Day 12","五","辦公室急救貼士 Carousel","Carousel","★★★", False),
    ("Day 13","六","Story：生活分享","Story","★★", False),
    ("Day 14","日","互動日（回覆DM）","互動","★", False),
    ("Day 15","一","個案分享 #2 Carousel","Carousel","★★★★", False),
    ("Day 16","二","Story：收集問題","Story","★★", False),
    ("Day 17","三","留言換資料 Reel【核武】","Reel","★★★★★", False),
    ("Day 18","四","Story：回覆留言截圖","Story","★★★", False),
    ("Day 19","五","療法科普 Carousel（衝擊波）","Carousel","★★★", False),
    ("Day 20","六","【香港人痛症地圖 #1】打工仔篇 Reel","Reel","★★★★", True),
    ("Day 21","日","互動日","互動","★", False),
    ("Day 22","一","個案分享 #3 Carousel","Carousel","★★★★", False),
    ("Day 23","二","【痛症性格類型】轉發炸彈 Carousel","Carousel","★★★★★", True),
    ("Day 24","三","比較 Reel（3種療法）","Reel","★★★★", False),
    ("Day 25","四","【局內人說話 #2】Story/小貼士","Story","★★★", True),
    ("Day 26","五","個案分享 #4 Carousel","Carousel","★★★★", False),
    ("Day 27","六","Story：生活分享","Story","★★", False),
    ("Day 28","日","互動日","互動","★", False),
    ("Day 29","一","個案分享 #5 Carousel","Carousel","★★★", False),
    ("Day 30","二","30日總結 Reel","Reel","★★★★", False),
]
for row in schedule:
    pdf.table_row(list(row[:5]), [18,16,96,26,14], highlight=row[5])
pdf.ln(3)
pdf.warn("Day 3（個人故事）、Day 11（局內人說話）、Day 17（留言換資料）、Day 23（性格類型）係四條最重要帖——要花最多時間準備。")

# ── PART 4: WEEK 1 ───────────────────────────────────────────
pdf.add_page()
pdf.ch_title("第四部分：Week 1 詳細指引（Day 1-7）帳號建立期")

# Day 1
pdf.day_bar(1, "週一", "帳號介紹 Carousel", "4頁 Carousel")
pdf.section_bar("圖片設計指引（4頁）", bg=(27,58,107))
for name, desc in [
    ("封面（第1頁）",
     "背景：深藍 #1B3A6B\n上方白色小字：STANLEY｜痛症方案顧問\n中間白色粗體大字：「我唔係醫生 / 但我知你嘅痛 / 點解搞唔掂」\n下方青綠色小字：👉 向左掃了解更多"),
    ("第2頁",
     "背景：白色，左側深藍豎線\n標題（深藍粗體）：我係 Stanley\n內文：✅ X年痛症管理經驗 / ✅ 見過幾百個真實個案 / ✅ 了解多種療法\n我的工作：幫你搵啱最適合你的方案，唔係幫你賣任何東西"),
    ("第3頁",
     "背景：白色\n標題（深藍）：呢個 IG 你會睇到\n4個方格：📂每週個案分享 / 🔬痛症謬誤破解 / 💊療法比較解釋 / 🆓免費方案諮詢\n底部青綠橫條：DM 我，15分鐘電話了解你情況"),
    ("第4頁（CTA）",
     "背景：深藍\n白色大字：你而家有痛症困擾？\n白色細字：唔知應該睇邊科？/ 試過好多方法但冇用？/ 唔知做物理治療定中醫好？\n青綠按鈕：DM 我「評估」/ Link in Bio"),
]:
    pdf.slide_label(name)
    pdf.box(desc)

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("我係 Stanley，痛症方案顧問。\n唔係醫生，唔係治療師——\n但過去 [X] 年，我見過幾百個有痛症問題的人。\n\n呢個 IG，我會每週分享：\n📂 真實個案（全部匿名）\n🔬 拆解坊間痛症謬誤\n💊 唔同療法比較同解釋\n\n有痛症困擾？DM 我「評估」，15分鐘電話了解你情況 😊\n\n#痛症 #痛症管理 #香港痛症 #肩頸痛 #腰背痛 #坐骨神經痛 #痛症顧問", bg=(245,250,255))

pdf.ln(1)
pdf.day_bar(2, "週二", "Story：投票問卷", "Story")
pdf.box("設計：深藍背景 + 白字\n文字：「你而家最困擾你嘅係？」\nIG 投票貼紙：A) 頸/肩/背痛   B) 膝蓋/關節痛\n目的：了解受眾，推高 Story 互動率")

# Day 3
pdf.add_page()
pdf.day_bar(3, "週三", "個人故事 Reel", "60秒 Reel")
pdf.section_bar("封面圖設計", bg=(27,58,107))
pdf.box("背景：深藍\n上方白字（小）：我的故事\n中間白字（大粗體）：「點解我 / 會做痛症？」\n下方青綠色字：唔係因為錢\n右下角：Stanley｜痛症方案顧問")

pdf.section_bar("拍攝 Pose 指引", bg=(42,157,143))
for p in ["地點：屋企梳化或辦公枱前，白牆背景","設備：手機架或三腳架，鏡頭對準胸口以上","光線：自然光從側面（坐喺窗邊，光從左或右，唔好背光）","著裝：深色上衣（深藍/黑/深灰）","Pose：坐直，身體微微向前傾，雙手自然放枱上","眼神：望住鏡頭講，唔好望旁邊","開場3秒：停頓一秒先開口"]:
    pdf.bullet(p)
pdf.ln(1)

pdf.section_bar("完整影片腳本（60秒）", bg=(60,80,120))
pdf.box("""【開場 0-5秒】
「你有冇試過痛到訓唔著，但去睇醫生，佢話你冇事？」

【中段 5-40秒】
「我叫 Stanley，我唔係醫生，唔係物理治療師。
但過去[X]年，我見過幾百個有痛症問題嘅人。
入行之前，我自己身邊[家人/朋友]有[痛症問題]——
佢試過[中醫/西醫/物理治療]，成效唔理想，
後來係因為[某個方法]先真正改善。

我唔係因為呢行賺錢先做——
我係因為想搞清楚，點解咁多人痛咗咁耐都搵唔到方法。

呢兩年我睇過幾百個案，我發現一件事：
大部分人唔係治療做得唔好，係一開始搵錯咗方向。」

【結尾 40-60秒】
「所以我開咗呢個 IG。每週分享真實個案、拆解常見謬誤、
同你解釋唔同療法係點運作。
如果你有痛症問題，唔知應該點樣開始——
Follow 住先，或者 DM 我「評估」，15分鐘電話傾下你情況。」

【字幕提示（Reel 必加）】
開場：「你痛過，但醫生話你冇事？」
中段：「我唔係醫生，但我見過幾百個案」
結尾：「DM 我『評估』——15分鐘電話」""", bg=(245,250,255))

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("點解我會做痛症方案顧問？\n\n唔係因為呢行賺錢——\n係因為我見過太多人，痛咗幾年，試過好多方法，但搵唔到啱自己的方案。\n\n呢個 IG：📂 真實個案 | 🔬 謬誤破解 | 💊 療法比較\n\n有任何痛症困擾，DM 我「評估」，15分鐘電話了解你情況 😊\n\n#痛症 #痛症管理 #個人故事 #香港 #痛症顧問", bg=(245,250,255))

pdf.ln(1)
pdf.day_bar(4, "週四", "Story：Q&A", "Story")
pdf.box("背景：白色或淺藍\n文字：「你有咩關於痛症嘅問題想問我？」\n加入 IG 問答貼紙\n收到問題後，Day 6 Story 回答")

pdf.day_bar(5, "週五", "互動日（無發帖）", "互動任務")
pdf.box("1. 去 #痛症 #肩頸痛 #腰背痛 下留有意義留言\n2. 回覆所有 Day 1-4 嘅留言\n3. 回覆 DM\n時間：15-20 分鐘")

pdf.day_bar(6, "週六", "Story：日常 + 投票", "Story")
pdf.box("隨手拍一個日常畫面（食早餐/工作環境）\n文字：「準備緊下週個案分享——你最想睇邊類？」\n投票貼紙：頸肩痛 / 膝蓋痛 / 腰背痛 / 其他")

pdf.day_bar(7, "週日", "互動日", "互動任務")
pdf.box("回覆所有本週留言\n查看 Story 投票結果，記低受眾最多咩痛症\n思考下週個案分享主題（配合投票結果）")

# ── PART 5: WEEK 2 ───────────────────────────────────────────
pdf.add_page()
pdf.ch_title("第五部分：Week 2 詳細指引（Day 8-14）內容引流期")

pdf.day_bar(8, "週一", "個案分享 #1（頸痛2年）", "6頁 Carousel")
pdf.section_bar("圖片設計（6頁）", bg=(27,58,107))
for name, desc in [
    ("封面（第1頁）", "背景：深藍\n上方白字小：📂 個案分享 第1回\n中間白字大：「頸痛2年 / 做過物理治療 / 都冇用？」\n下方青綠：向左掃看個案詳情 👉"),
    ("第2頁（客人背景）", "背景：白色，頂部深藍橫條（白字）：🙋🏻 客人背景\n年齡：30歲出頭 / 職業：銀行文職 / 每日對住電腦 8 小時"),
    ("第3頁（問題）", "背景：白色，頂部青綠橫條：🎯 困擾問題\n〈頸椎痛 + 頭痛〉\n• 頸梗到轉唔到頭  • 嚴重時連帶頭痛  • 嚴重影響睡眠"),
    ("第4頁（試過嘅方法）", "背景：白色，頂部橙色橫條：🚨 試過但冇用\n❌ 物理治療6次——做完舒服，兩日後痛返\n❌ 頸部按摩器——一個月冇改善\n❌ 止痛藥——停藥就痛返"),
    ("第5頁（方案+效果）", "背景：白色，頂部深藍橫條：✅ 最終方案\n衝擊波 + 姿勢矯正訓練（根源：頸椎輕微錯位）\n📈 4次療程後：頭痛消失 / 活動度改善 / 冇再反覆\n⭐️ 難度：★★★☆☆"),
    ("第6頁（CTA）", "背景：深藍\n白字大：唔知自己係咪同樣情況？\n白字細：DM 我「評估」，15分鐘電話了解你情況\n青綠：Link in Bio 預約免費諮詢 👆🏻"),
]:
    pdf.slide_label(name)
    pdf.box(desc)

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("【頸痛2年，做過物理治療都冇用？】\n📂 個案分享第 1 回  #Stanley痛症個案\n\n🙋🏻 客人背景：30歲出頭，銀行文職\n🎯 困擾：頸椎痛 + 頭痛，每日對住電腦8小時\n🚨 試過：物理治療6次、按摩器、止痛藥——全部治標不治本\n✅ 方案：衝擊波 + 姿勢矯正（根源係頸椎輕微錯位）\n📈 4次後：頭痛消失，活動度改善，冇再反覆\n\n唔知自己係咪同樣情況？DM 我「評估」，15分鐘電話傾 😊\n\n#頸椎痛 #頸痛 #頭痛 #辦公室痛症 #痛症 #痛症管理 #衝擊波治療 #香港痛症", bg=(245,250,255))

pdf.add_page()
pdf.day_bar(10, "週三", "迷思破解 Reel（熱敷vs凍敷）", "45秒 Reel")
pdf.section_bar("封面圖設計", bg=(27,58,107))
pdf.box("背景：深藍\n大字白色：「熱敷定凍敷？/ 9成人整錯 冰火圖示」\n小字青綠：你係咪其中之一？\n右下角：Stanley｜痛症方案顧問")

pdf.section_bar("完整影片腳本（45秒）", bg=(60,80,120))
pdf.box("""【開場 0-5秒】
「拉傷咗第一時間熱敷？你可能愈敷愈差。」

【中段 5-35秒】
「急性受傷——即係頭48小時——要用凍敷。原因係新傷有炎症反應，熱敷係幫炎症擴散。
相反，慢性痛症——例如長期頸痛、腰痛——係可以熱敷嘅，幫肌肉放鬆。
問題唔係熱敷定凍敷——係你先要判斷：係急性，定係慢性？」

【結尾 35-45秒】
「唔確定係哪種？下面 Comment 打「評估」，我即刻 PM 你份自我判斷指引。」""", bg=(245,250,255))

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("熱敷定凍敷？9成人整錯\n\n急性受傷（頭48小時）→ 凍敷\n慢性痛症（長期反覆）→ 熱敷\n\n搞錯咗唔係冇效，係愈搞愈差\n\n👇 Comment 打「評估」，即刻 PM 你份自我判斷指引\n\n#痛症 #熱敷 #凍敷 #頸痛 #腰痛 #痛症常識 #香港痛症", bg=(245,250,255))

# Day 11 NEW: 局內人說話
pdf.add_page()
pdf.day_bar_new(11, "週四", "【局內人說話 #1】行業真相 Carousel", "4頁 Carousel")
pdf.upgrade_tag("呢帖係 v2 新增。差異化最強嘅一類帖——業界人唔敢講，你敢講。")

pdf.section_bar("主題建議：「為什麼物理治療做完好，停咗又痛返？」", bg=(27,58,107))
pdf.section_bar("圖片設計（4頁）", bg=(27,58,107))
for name, desc in [
    ("封面（第1頁）",
     "背景：深藍，重衝擊感\n大字白色：「物理治療做完好 / 停咗又痛返 / 因為冇人話你知呢件事」\n青綠小字：局內人視角 👉"),
    ("第2頁（問題根源）",
     "背景：白色，頂部深藍橫條：🔍 真正原因\n物理治療幫你處理症狀——但唔係消除根源\n根源通常係：肌肉失衡 / 姿勢問題 / 舊患未完全康復\n如果唔改變根源，停止療程後症狀自然回來"),
    ("第3頁（行業現實）",
     "背景：白色，頂部橙色橫條：🏥 業界現實\n每個診所各有側重，唔係所有PT都會同你講這些\n有些人需要的唔係更多PT，係換一個方向\n作為顧問，我見過太多人走冤枉路——唔一定係治療師問題，係方向對唔上"),
    ("第4頁（CTA）",
     "背景：深藍\n白字大：你嘅情況係咁嗎？\n白字細：DM 我「評估」，15分鐘電話——局內人同你講清楚你應該點\n青綠：免費，唔推銷"),
]:
    pdf.slide_label(name)
    pdf.box(desc)

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("【局內人說話 #1】物理治療做完好，停咗又痛返？\n\n唔係你做得唔夠，也唔係PT無效——\n係因為冇人告訴你，療程解決症狀，唔係根源。\n\n見過太多人：PT做咗20次，好咗，停咗，3個月後痛返——再做20次。\n係呢個循環有問題，唔係你。\n\n如果你係咁，DM 我「評估」——15分鐘電話，局內人角度分析你情況。\n唔推銷，直接講。\n\n#物理治療 #痛症 #痛症管理 #局內人 #頸痛 #腰背痛 #香港痛症", bg=(245,250,255))

pdf.day_bar(12, "週五", "辦公室急救貼士 Carousel", "5頁 Carousel")
pdf.section_bar("三個動作（設計格式同 v1）", bg=(42,157,143))
for name, desc in [
    ("動作1：頸部側伸展", "頭側向右邊，右手輕輕放頭頂加少少壓力——保持15秒，換邊做"),
    ("動作2：肩膀後收", "雙手垂低，肩膀向後收，夾埋兩邊肩胛骨——保持10秒，重複5次"),
    ("動作3：頸部後縮（Chin Tuck）", "下巴向後縮，好似有人用手指頂住你前額——保持5秒，重複10次"),
]:
    pdf.slide_label(name)
    pdf.box(desc)

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("OT 頸痛急救 3招\n\n第1招：頸部側伸展\n第2招：肩膀後收\n第3招：Chin Tuck 頸後縮\n\n每日做，5分鐘，收工即刻做\n\n如果做完仲係痛，或者痛超過2週——\nDM 我「評估」，可能唔係「累」，係需要認真分析\n\n#頸痛 #OT #辦公室痛症 #頸椎痛 #打工仔 #痛症管理 #香港痛症", bg=(245,250,255))

# ── PART 6: WEEK 3 ───────────────────────────────────────────
pdf.add_page()
pdf.ch_title("第六部分：Week 3 詳細指引（Day 15-21）互動爆發期")

pdf.day_bar(15, "週一", "個案分享 #2（膝蓋退化）", "6頁 Carousel")
pdf.section_bar("個案內容", bg=(42,157,143))
pdf.box("客人背景：50歲，家庭主婦\n困擾：膝關節退化，落樓梯必定痛，行多路腫脹，骨科建議考慮換骨\n試過：玻尿酸針 / 消炎藥（胃副作用）/ 護膝（無根治）\n最終方案：體外衝擊波 + 股四頭肌訓練\n效果（3個月）：落樓梯痛感由8分降至2分，腫脹明顯減退，暫時唔需要手術\n\n封面文字：「膝蓋痛到以為要換骨 / 最後唔使手術」\nCTA：DM 我「評估」，15分鐘電話了解你情況", bg=(245,250,255))

pdf.add_page()
pdf.day_bar(17, "週三", "留言換資料 Reel【核武】", "60秒 Reel")
pdf.warn("呢條係整個30日計劃最重要嘅一條——要花最多時間準備。拍唔好就重拍，直至你自己覺得「有力」先 post。")

pdf.section_bar("Day 17 前必須準備好的物料", bg=(150,30,30), fg=(255,255,255))
pdf.box("""✅ 「慢性痛症根源自我判斷清單」PDF（收到 Comment 後即刻 PM）
   內容：5條問題幫讀者判斷自己係肌肉失衡 / 關節錯位 / 筋膜沾黏
   格式：A4 單頁，深藍白字，底部加 Stanley 聯絡方式

✅ DM 標準開場白（即刻可 copy paste）：
   「收到你嘅清單！我睇完係[類型]，建議係[方向]。
   如果想詳細了解，可以約15分鐘電話傾下，唔收費，唔推銷。你方便嗎？」

✅ 關鍵：Day 17 發佈後第一個鐘要在線——Comment 一到即刻 PM，速度係關鍵。""", bg=(255,240,240))

pdf.section_bar("封面圖設計", bg=(27,58,107))
pdf.box("背景：深藍\n上方白字小：止痛藥依賴？\n中間白字大：「食完又痛返 / 係因為你 / 搵錯方向了」\n下方青綠色：留言「止痛」換免費指南 👇")

pdf.section_bar("完整影片腳本（60秒）", bg=(60,80,120))
pdf.box("""【開場 0-5秒——鉤子】
「你食止痛藥，食完唔痛，停咗又痛返——你有冇諗過，係咪你一直食錯咗？」

【中段 5-45秒——核心內容】
「止痛藥做嘅嘢，係阻斷你感受痛嘅神經信號——佢唔係幫你修復任何嘢。
打個比喻：你屋企火警警報響——你唔係去滅火，而係拆咗警報器。
火依然喺度燒，只係你唔知咋。

慢性痛症嘅根源通常得幾樣：
1. 肌肉失衡——某部分肌肉太弱，另一部分補償過度
2. 關節錯位——長期姿勢問題積累
3. 筋膜沾黏——舊患未正確處理

唔同根源，方向完全唔同。」

【結尾 45-60秒——CTA】
「我整理咗一份【慢性痛症根源自我判斷清單】
喺下面 Comment 打「止痛」，我即刻 PM 俾你。唔收費，直接用。」""", bg=(245,250,255))

# Day 20 NEW: 香港人痛症地圖
pdf.add_page()
pdf.day_bar_new(20, "週六", "【香港人痛症地圖 #1】打工仔篇 Reel", "30-45秒 Reel")
pdf.upgrade_tag("呢帖係 v2 新增。輕鬆語氣，高認同感，令香港打工仔一睇就「係呀」。")

pdf.section_bar("封面圖設計", bg=(100, 60, 150))
pdf.box("背景：深藍\n大字白色：「港鐵打工仔 / 你條頸真係 / 捱唔住㗎」\n青綠小字：香港人痛症地圖 #1 👉")

pdf.section_bar("拍攝 Pose 指引", bg=(42,157,143))
for p in ["地點：可以係港鐵站附近（公共場合拍攝）或白牆前模擬","語氣：輕鬆幽默，可以自嘲同共情","開場：做一個低頭望手機嘅動作，然後望返鏡頭","中段：講數據同原因時保持輕鬆，唔好太說教","結尾：笑住講 CTA"]:
    pdf.bullet(p)

pdf.section_bar("完整影片腳本（45秒）", bg=(60,80,120))
pdf.box("""【開場 0-5秒】
「每日搭港鐵，低頭睇手機——你條頸知道你做緊咩。」

【中段 5-35秒】
「香港人平均每日係咁：
搭港鐵低頭45分鐘 → 返工坐定定8小時 → 收工搭港鐵又係45分鐘

你條頸一日要頂住個頭（大概5公斤）——
低頭45度嘅時候，頸承受嘅壓力係22公斤。

呢唔係危言聳聽——係你條頸每日嘅現實。

好多人嘅慢性頸痛唔係病，係習慣。
係港鐵 + 辦公室 + 手機加起來嘅結果。

改唔到搭港鐵，但有啲嘢你可以做。」

【結尾 35-45秒】
「Comment 打「頸痛」，我 PM 你份港鐵族頸痛急救指南。」""", bg=(245,250,255))

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("香港人痛症地圖 #1：港鐵打工仔篇\n\n搭港鐵低頭45度 → 頸部承受22公斤壓力\n\n呢唔係危言聳聽，係你條頸每日嘅現實。\n\n每日港鐵 + 辦公室 + 手機——三重疊加，難怪頸痛係香港最普遍嘅痛症。\n\n👇 Comment 打「頸痛」，PM 你份港鐵族頸痛急救指南\n\n你係邊區嘅港鐵族？Comment 落嚟 😂\n\n#香港 #港鐵 #打工仔 #頸痛 #辦公室痛症 #痛症 #香港人", bg=(245,250,255))

pdf.day_bar(21, "週日", "互動日", "互動任務")
pdf.box("回覆所有本週留言\nDay 17 核武帖收到嘅 Comment + DM 全部跟進\n統計 Day 17 帶來嘅 DM 數量，記錄轉化情況")

# ── PART 7: WEEK 4 ───────────────────────────────────────────
pdf.add_page()
pdf.ch_title("第七部分：Week 4 詳細指引（Day 22-30）深化建立期")

pdf.day_bar(22, "週一", "個案分享 #3（健身男肩痛）", "6頁 Carousel")
pdf.section_bar("個案內容", bg=(42,157,143))
pdf.box("客人背景：28歲，自僱，健身3年\n困擾：做 Bench Press 時右肩刺痛，右手舉高就痛\n試過：痛症貼布 / 跌打 / 休息（反覆）\n最終方案：體外衝擊波 + 旋轉肌專項訓練\n效果（6次）：恢復訓練無刺痛，Bench Press 重量仲升咗\n封面文字：「健身男 / 忍痛練落去 / 係最錯嘅決定」\nCTA：DM 我「評估」，15分鐘電話了解情況", bg=(245,250,255))

# Day 23 NEW: 痛症性格類型
pdf.add_page()
pdf.day_bar_new(23, "週二", "【痛症性格類型】轉發炸彈 Carousel", "5頁 Carousel")
pdf.upgrade_tag("呢帖係 v2 新增。目標：讀者轉發俾朋友，病毒式傳播機制，係引流最強嘅一類帖。")

pdf.section_bar("圖片設計（5頁）", bg=(170, 80, 30))
for name, desc in [
    ("封面（第1頁）",
     "背景：深藍\n大字白色：「你係哪種痛症人？/ 4種類型 / 第幾種係你？」\n青綠小字：Tag 你嘅朋友 👉"),
    ("第2頁：忍痛型",
     "背景：白色，頂部深藍橫條\n類型名：😤 忍痛型\n描述：「痛？忍吓囉。係咁㗎啦。唔係大病。」\n後果：忍到變慢性，治療成本翻倍\n小字底部：你識唔識呢類人？Tag 佢"),
    ("第3頁：Panadol 型",
     "背景：白色，頂部橙色橫條\n類型名：💊 Panadol 型\n描述：「食粒止痛藥就好㗎喇。唔痛就係好咗。」\n後果：停藥又痛，以為藥唔夠强，藥量愈來愈多\n小字：火警警報響，你唔係去滅火，係拆咗警報器"),
    ("第4頁：Google 型",
     "背景：白色，頂部青綠橫條\n類型名：🔍 Google 型\n描述：「Google 話係XXX，我自己診斷係XXX，唔使睇醫生。」\n後果：睇完10篇文章，愈睇愈驚，但仲係唔知應該點\n小字：資訊唔等於判斷，你需要嘅係對住自己情況嘅分析"),
    ("第5頁（互動+CTA）",
     "背景：深藍\n白字大：你係哪種？\n白字細：Comment 你嘅類型\nTag 你識嘅[忍痛型/Panadol型/Google型]朋友\n\n青綠橫條：唔想做任何一種？DM 我「評估」"),
]:
    pdf.slide_label(name)
    pdf.box(desc)

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("你係哪種痛症人？\n\n😤 忍痛型：「係咁㗎啦，大家都係咁」\n💊 Panadol 型：「食粒先，唔痛就係好咗」\n🔍 Google 型：「我自己診斷好，唔使睇醫生」\n\n三種類型，三種後果——但有一個共同點：\n最後都係問題更大嗰個。\n\nTag 你識嘅[忍痛型]朋友 😂\nComment 你係哪種？\n\n如果你唔想做任何一種——DM 我「評估」，15分鐘電話了解你情況。\n\n#痛症 #香港人 #止痛藥 #痛症管理 #你係哪種 #香港痛症", bg=(245,250,255))

pdf.add_page()
pdf.day_bar(24, "週三", "比較 Reel（3種療法）", "60秒 Reel")
pdf.section_bar("完整影片腳本（60秒）", bg=(60,80,120))
pdf.box("""【開場 0-5秒】
「中醫、物理治療、儀器治療——唔係哪個最好，係哪個最啱你。」

【中段 5-50秒】
「中醫：從整體入手，調理身體環境。
適合：慢性痛症、反覆發作、體質偏弱
唔適合：需要即時止痛嘅急性創傷

物理治療：以運動同手法矯正為主。
適合：姿勢問題、肌力不足、術後康復

儀器治療（如衝擊波）：直接針對組織修復。
適合：肌腱炎、鈣化問題、PT效果唔理想
唔適合：急性炎症期

所以問題唔係邊個好——係你係哪種情況。
好多人失敗，係因為一開始用錯咗方向。」

【結尾 50-60秒】
「唔確定自己適合邊種？DM 我「評估」，15分鐘電話幫你判斷。」""", bg=(245,250,255))

pdf.day_bar(25, "週四", "【局內人說話 #2】Story 版小貼士", "Story x3")
pdf.upgrade_tag("v2 新增：用 Story 延伸「局內人說話」系列，保持曝光但唔需要大製作。")
pdf.box("""Story 1：「你知唔知，有啲儀器治療，係唔適合所有人做嘅？但好多地方唔會告訴你。」
投票：你做過衝擊波 / 其他儀器治療？ A) 有  B) 未

Story 2：「作為顧問，我見過最多嘅情況係——客人花咗幾千蚊，做完好，但唔知為什麼好咗。」
問卷：「你做過的療程，有人解釋過原因嗎？」

Story 3：「如果你對任何療法有問題——DM 我，局內人角度解釋，唔賣嘢。」""", bg=(245,250,255))

pdf.day_bar(26, "週五", "個案分享 #4（坐骨神經痛）", "6頁 Carousel")
pdf.section_bar("圖片設計（6頁）", bg=(27,58,107))
for name, desc in [
    ("封面（第1頁）", "背景：深藍\n上方白字小：📂 個案分享 第4回\n中間白字大：「坐骨神經痛 / 睇咗大半年 / 終於唔使打針」\n下方青綠：向左掃看個案詳情 👉"),
    ("第2頁（客人背景）", "背景：白色，頂部深藍橫條（白字）：🙋🏻 客人背景\n年齡：40歲出頭 / 職業：自由工作者（在家工作）\n每日坐係電腦前10小時以上，唔多郁"),
    ("第3頁（問題）", "背景：白色，頂部青綠橫條：🎯 困擾問題\n〈右邊坐骨神經痛 + 右腳麻痹〉\n• 坐多過30分鐘右邊屁股就開始痹  • 右腳有時麻到感覺唔到  • 站起身嗰刻最痛  • 嚴重影響工作效率"),
    ("第4頁（試過嘅方法）", "背景：白色，頂部橙色橫條：🚨 試過但冇用\n❌ 中醫針灸6次——做完當時好，第二日又痹返\n❌ 消炎止痛藥——胃唔好受，停藥即刻痛返\n❌ 自己拉筋——拉錯方向，反而加劇症狀"),
    ("第5頁（方案+效果）", "背景：白色，頂部深藍橫條：✅ 最終方案\n體外衝擊波 + 核心肌群訓練（根源：梨狀肌緊張壓住坐骨神經）\n📈 6週後：麻痹感消失 / 可以連續坐2小時工作 / 自己學識識別復發先兆\n⭐️ 難度：★★★★☆"),
    ("第6頁（CTA）", "背景：深藍\n白字大：你有類似情況？\n白字細：坐骨神經痛唔係一定要打針——方向對先係關鍵\nDM 我「評估」，15分鐘電話了解你情況 👆🏻"),
]:
    pdf.slide_label(name)
    pdf.box(desc)

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("【坐骨神經痛睇咗大半年，終於唔使打針】\n📂 個案分享第 4 回  #Stanley痛症個案\n\n🙋🏻 40歲自由工作者，長期在家工作\n🎯 右邊坐骨神經痛 + 右腳麻痹，坐30分鐘就痹\n🚨 試過：針灸、消炎藥、自己拉筋——全部治標不治本\n✅ 方案：衝擊波 + 核心肌群訓練（根源係梨狀肌壓神經）\n📈 6週後：麻痹消失，可以正常工作，唔再需要打針\n\n坐骨神經痛唔係一定要打針或者開刀——方向對先係關鍵。\nDM 我「評估」，15分鐘電話了解你情況 😊\n\n#坐骨神經痛 #坐骨神經 #腰背痛 #麻痹 #在家工作 #痛症 #痛症管理 #香港痛症", bg=(245,250,255))

pdf.day_bar(29, "週一", "個案分享 #5（媽媽手/腱鞘炎）", "6頁 Carousel")
pdf.section_bar("圖片設計（6頁）", bg=(27,58,107))
for name, desc in [
    ("封面（第1頁）", "背景：深藍\n上方白字小：📂 個案分享 第5回\n中間白字大：「抱個BB / 痛到想喊 / 唔係你唔捱得」\n下方青綠：向左掃看個案詳情 👉"),
    ("第2頁（客人背景）", "背景：白色，頂部深藍橫條（白字）：🙋🏻 客人背景\n年齡：28歲 / 新手媽媽，BB 3個月大\n每日抱 BB 超過8小時，未睡好已經2個月"),
    ("第3頁（問題）", "背景：白色，頂部青綠橫條：🎯 困擾問題\n〈右手拇指根部 + 手腕腫痛〉（媽媽手/腱鞘炎）\n• 抱BB時手腕劇痛，放唔低又唔捨得  • 扭鈕扣、開樽蓋都做唔到  • 早上起身最嚴重，手腕好似「鎖死」咗  • 唔想影響照顧BB"),
    ("第4頁（試過嘅方法）", "背景：白色，頂部橙色橫條：🚨 試過但冇用\n❌ 護腕托板——短暫舒緩，但根本冇法唔用隻手照顧BB\n❌ 消炎藥——哺乳期不確定能否用，唔敢食\n❌ 休息——根本休息唔到，BB要人抱"),
    ("第5頁（方案+效果）", "背景：白色，頂部深藍橫條：✅ 最終方案\n體外衝擊波（針對腱鞘炎）+ 抱BB姿勢調整指導\n根源：手腕同拇指長期受力不當，加上產後荷爾蒙令肌腱更易發炎\n📈 4次後：痛感由8分降至2分 / 可以正常抱BB / 鈕扣扭回到\n⭐️ 關鍵：姿勢改變同療程一樣重要"),
    ("第6頁（CTA）", "背景：深藍\n白字大：你係媽媽，或者身邊有新手媽媽？\n白字細：媽媽手唔係「捱吓就過」——方向對先可以快咗好\nDM 我「評估」，15分鐘電話了解你情況 👆🏻"),
]:
    pdf.slide_label(name)
    pdf.box(desc)

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("【抱個BB痛到想喊——唔係你唔捱得，係媽媽手】\n📂 個案分享第 5 回  #Stanley痛症個案\n\n🙋🏻 28歲新手媽媽，BB 3個月大\n🎯 右手拇指根部 + 手腕腫痛，抱BB就痛，扭鈕扣都做唔到\n🚨 試過：護腕托板、想休息但休息唔到、消炎藥哺乳期唔敢食\n✅ 方案：衝擊波 + 抱BB姿勢調整（根源：腱鞘炎 + 錯誤受力）\n📈 4次後：痛感由8分降至2分，可以正常抱BB照顧小朋友\n\n媽媽手唔係「捱吓就過」——正確方向係關鍵。\n分享俾身邊新手媽媽 😊\nDM 我「評估」，15分鐘電話了解你情況\n\n#媽媽手 #腱鞘炎 #新手媽媽 #手腕痛 #媽媽 #痛症 #痛症管理 #香港痛症 #衝擊波", bg=(245,250,255))

pdf.add_page()
pdf.day_bar(30, "週二", "30日總結 Reel", "60秒 Reel")
pdf.section_bar("完整影片腳本（60秒）", bg=(60,80,120))
pdf.box("""【開場 0-5秒】
「呢個 IG 開咗30日，我想同大家分享幾樣嘢。」

【中段 5-45秒】
「第一樣：好多人有痛症，但唔知由邊度開始——呢個係我見到最多嘅情況。

第二樣：坊間謬誤真係好多——呢個月我分享過[X個]，每一個都有人話係第一次聽到正確答案。

第三樣：[你自己覺得最有意義嘅一句話，來自某個個案]

三十日前，我開呢個 IG 係因為想幫到更多人——
唔係因為賣嘢，係因為睇住咁多人痛咗咁耐都搵唔到方向。

30日入面，我哋分享咗：
📂 [X]個真實個案 | 🔬 [X]個謬誤破解 | 💡局內人視角 | 🗺️ 香港人痛症地圖」

【結尾 45-60秒】
「如果你今日先第一次睇到我——我係 Stanley，痛症方案顧問。
每週分享真實個案、療法比較、局內人視角痛症知識。
Follow 住，下個月仲有更多。或者 DM 我「評估」，15分鐘電話了解你情況。」""", bg=(245,250,255))

# ── PART 8: DAILY ENGAGEMENT ─────────────────────────────────
pdf.add_page()
pdf.ch_title("第八部分：每日15分鐘互動任務")
pdf.body("不論有冇發帖，以下任務每日都要做。持之以恆比任何技巧都重要。")
pdf.ln(2)

pdf.table_header(["任務","時間","做法"], [50,20,110])
for row in [
    ("回覆所有留言","5分鐘","每條留言都回，唔好只係 Like。短回覆都好過冇回。"),
    ("回覆 DM","5分鐘","當日 DM 當日回，唔好拖超過24小時。"),
    ("去相關 Hashtag 互動","5分鐘","#痛症 #頸痛 #腰背痛 下留有意義留言"),
]:
    pdf.table_row(list(row), [50,20,110])
pdf.ln(4)

pdf.section_bar("推薦 Hashtag 清單")
pdf.table_header(["類別","Hashtag"], [40,150])
for row in [
    ("主題","#痛症 #痛症管理 #香港痛症 #痛症治療 #痛症顧問"),
    ("症狀","#肩頸痛 #腰背痛 #坐骨神經痛 #膝蓋痛 #五十肩 #頸椎痛"),
    ("療法","#衝擊波 #物理治療 #中醫 #脊醫 #運動創傷"),
    ("生活","#打工仔 #辦公室 #健身 #香港 #健康"),
    ("新增（v2）","#局內人 #香港人 #港鐵 #痛症地圖 #你係哪種"),
]:
    pdf.table_row(list(row), [40,150])

pdf.upgrade_tag("v2 新增 Hashtag：在「局內人說話」系列用 #局內人；在「香港人痛症地圖」用 #香港人 #港鐵；在「性格類型」用 #你係哪種")

# ── PART 9: CHECKLIST ────────────────────────────────────────
pdf.add_page()
pdf.ch_title("第九部分：開始前準備清單（Day 1 前必須搞掂）")
pdf.table_header(["準備事項","說明"], [55,135])
for row, is_new in [
    (("Canva 帳號","免費版夠用。設定好品牌顏色（3個Hex Code）同字體。"), False),
    (("帳號名稱","決定好，一旦開始唔好改。建議：stanley.paincare.hk"), False),
    (("Bio 寫好","痛症方案顧問 | 見過幾百個案 | 幫你搵啱方向 | DM「評估」免費傾"), True),
    (("留言換資料 PDF","「慢性痛症根源自我判斷清單」——Day 17 前必須準備好。"), False),
    (("DM 標準回覆模板（v2）","「DM 我評估」收到後：你好！我係Stanley，X分鐘電話唔收費，我哋傾下你情況可以嗎？"), True),
    (("手機架/三腳架","拍 Reel 必備。50-100港元，淘寶或士多可以搵到。"), False),
    (("補光燈（可選）","夜晚拍攝用，100-200港元。日間有自然光可以唔使。"), False),
    (("真實個案5個","準備5個真實個案（匿名），記低：背景/問題/試過方法/方案/效果。"), False),
    (("局內人話題清單（v2）","列出3條你作為業界人知道、但客人唔知嘅真相，作為局內人說話素材。"), True),
]:
    pdf.table_row(list(row[0]), [55,135], highlight=is_new)

pdf.ln(4)
pdf.warn("最快開始方法：今日搞掂 Canva 設定，明日完成 Day 1 帳號介紹 Carousel，後日正式 post 出去。唔好等完美，先開始先。")
pdf.upgrade_tag("v2 Bio 升級：舊版 Bio 用「免費傾吓」，太被動。新版主動引導：「DM 我『評估』——15分鐘電話了解你情況」")

# ── APPENDIX ─────────────────────────────────────────────────
pdf.add_page()
pdf.ch_title("附錄：完整 Caption 文案索引（v2 更新版）")
pdf.body("以下為本手冊所有 Caption 文案的快速索引，綠色底色為 v2 新增帖。")
pdf.ln(2)

pdf.table_header(["發帖日","類型","Caption 開頭"], [20,65,105])
index_rows = [
    ("Day 1","帳號介紹","我係 Stanley，痛症方案顧問...", False),
    ("Day 3","個人故事 Reel","點解我會做痛症方案顧問？...", False),
    ("Day 8","個案分享 #1（頸痛）","【頸痛2年，做過物理治療都冇用？】...", False),
    ("Day 10","迷思破解（熱敷vs凍敷）","熱敷定凍敷？9成人整錯...", False),
    ("Day 11","【局內人說話 #1】★NEW","【局內人說話】物理治療做完好，停咗又痛返...", True),
    ("Day 12","辦公室急救貼士","OT 頸痛急救 3招...", False),
    ("Day 15","個案分享 #2（膝蓋痛）","【膝蓋痛到以為要換骨，最後唔使手術】...", False),
    ("Day 17","留言換資料 Reel【核武】","止痛藥食完又痛返？唔係你食得唔夠...", False),
    ("Day 19","療法科普（衝擊波）","衝擊波係咩？唔係電療，唔係打針...", False),
    ("Day 20","【香港人痛症地圖 #1】★NEW","香港人痛症地圖 #1：港鐵打工仔篇...", True),
    ("Day 22","個案分享 #3（健身男）","【健身男忍痛練落去係最錯嘅決定】...", False),
    ("Day 23","【痛症性格類型】★NEW","你係哪種痛症人？4種類型...", True),
    ("Day 24","比較 Reel（3種療法）","中醫 vs 物理治療 vs 儀器治療...", False),
    ("Day 26","個案分享 #4（坐骨神經痛）","【坐骨神經痛睇咗大半年，終於唔使打針】...", False),
    ("Day 29","個案分享 #5（媽媽手）","【抱個BB痛到想喊——唔係你唔捱得，係媽媽手】...", False),
    ("Day 30","30日總結 Reel","呢個 IG 開咗30日，我想同大家分享...", False),
]
for day, typ, opening, is_new in index_rows:
    pdf.table_row([day, typ, opening], [20,65,105], highlight=is_new)

pdf.ln(6)
pdf.section_bar("v2 更新總結", bg=(30, 100, 50))
pdf.box("""本次更新（v2.0）主要改動：

1. 新增三個原創系列框架說明（第二部分）
2. 整合三個新帖入30日計劃：
   - Day 11：局內人說話 #1（高差異化 Carousel）
   - Day 20：香港人痛症地圖 #1（港鐵打工仔 Reel）
   - Day 23：痛症性格類型（病毒傳播 Carousel）
3. Day 25 加入局內人說話 #2（Story 版輕量格式）
4. 全部 CTA 升級：「免費傾吓」→「DM 我『評估』，15分鐘電話了解情況」
5. Day 17 核武帖加入「發佈前必備物料清單」
6. Bio 推薦升級（附錄第九部分）
7. 新增 Hashtag 建議""", bg=(240,250,240))

pdf.ln(4)
pdf.set_font("ArialUnicode", "B", 10)
pdf.set_text_color(27, 58, 107)
pdf.cell(0, 7, "如需任何內容更新或新增，隨時繼續完善本手冊。", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("ArialUnicode", "", 9)
pdf.set_text_color(100,100,100)
pdf.cell(0, 6, "Stanley 痛症 IG 30日執行手冊 v2.0 | 更新於 2026年5月17日", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.output(OUTPUT_PATH)
print(f"Done: {OUTPUT_PATH}")
