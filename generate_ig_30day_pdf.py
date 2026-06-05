from fpdf import FPDF
import os

OUTPUT_PATH = "/Users/rickyc./Desktop/Vs code /Project 2 (Stanley)/Stanley_痛症IG_30日執行手冊.pdf"
FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"

class PDF(FPDF):
    def header(self):
        self.set_font("ArialUnicode", "B", 9)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(27, 58, 107)
        self.cell(0, 8, "Stanley | 痛症方案顧問 | IG 30日執行手冊", fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
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

    def table_header(self, cols, widths):
        self.set_font("ArialUnicode", "B", 9)
        self.set_fill_color(27, 58, 107)
        self.set_text_color(255, 255, 255)
        for c, w in zip(cols, widths):
            self.cell(w, 6, c, border=1, fill=True)
        self.ln()

    def table_row(self, cols, widths):
        self.set_font("ArialUnicode", "", 9)
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

pdf.set_y(55)
pdf.set_text_color(255, 255, 255)
pdf.cell(0, 14, "Stanley", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("ArialUnicode", "B", 17)
pdf.set_text_color(42, 157, 143)
pdf.cell(0, 10, "痛症 IG 30日完整執行手冊", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)
pdf.set_font("ArialUnicode", "", 11)
pdf.set_text_color(180, 200, 230)
pdf.cell(0, 7, "從零開始 | 品牌視覺 | 每日任務 | 完整文案 | 影片腳本", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(18)
pdf.set_font("ArialUnicode", "B", 11)
pdf.set_text_color(255, 255, 255)
pdf.cell(0, 7, "痛症方案顧問 | 個人品牌 IG 引流", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(55)
pdf.set_font("ArialUnicode", "", 9)
pdf.set_text_color(120, 150, 190)
pdf.cell(0, 6, "生成日期：2026年5月", align="C", new_x="LMARGIN", new_y="NEXT")

# ── TOC ──────────────────────────────────────────────────────
pdf.add_page()
pdf.ch_title("目錄")
toc = [
    ("第一部分", "品牌視覺系統", "設定顏色、字體、Logo"),
    ("第二部分", "30日行程總覽", "每日任務一覽表"),
    ("第三部分", "Week 1 詳細指引", "Day 1-7：帳號建立期"),
    ("第四部分", "Week 2 詳細指引", "Day 8-14：內容引流期"),
    ("第五部分", "Week 3 詳細指引", "Day 15-21：互動爆發期"),
    ("第六部分", "Week 4 詳細指引", "Day 22-30：深化建立期"),
    ("第七部分", "每日互動任務", "15分鐘例行公事"),
    ("第八部分", "開始前準備清單", "Day 1 前必須搞掂"),
    ("附錄", "完整 Caption 文案索引", "所有帖子文案"),
]
for part, title, desc in toc:
    self = pdf
    pdf.set_font("ArialUnicode", "B", 10)
    pdf.set_text_color(27, 58, 107)
    pdf.cell(35, 7, part)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(60, 7, title)
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

# ── PART 2: SCHEDULE ─────────────────────────────────────────
pdf.add_page()
pdf.ch_title("第二部分：30日行程總覽")
pdf.table_header(["日期","星期","任務","格式","重要度"], [18,16,90,26,20])
schedule = [
    ("Day 1","一","帳號介紹 Carousel","Carousel","★★★"),
    ("Day 2","二","Story：投票問卷","Story","★★"),
    ("Day 3","三","個人故事 Reel","Reel","★★★★"),
    ("Day 4","四","Story：Q&A","Story","★★"),
    ("Day 5","五","互動日（無發帖）","互動","★"),
    ("Day 6","六","Story：日常分享","Story","★★"),
    ("Day 7","日","互動日","互動","★"),
    ("Day 8","一","個案分享 #1 Carousel","Carousel","★★★★"),
    ("Day 9","二","Story：頸痛延伸貼士","Story","★★"),
    ("Day 10","三","迷思破解 Reel（熱敷vs凍敷）","Reel","★★★★"),
    ("Day 11","四","Story：留言回覆截圖","Story","★★"),
    ("Day 12","五","辦公室急救貼士 Carousel","Carousel","★★★"),
    ("Day 13","六","Story：生活分享","Story","★★"),
    ("Day 14","日","互動日（回覆DM）","互動","★"),
    ("Day 15","一","個案分享 #2 Carousel","Carousel","★★★★"),
    ("Day 16","二","Story：收集問題","Story","★★"),
    ("Day 17","三","留言換資料 Reel【核武】","Reel","★★★★★"),
    ("Day 18","四","Story：回覆留言截圖","Story","★★★"),
    ("Day 19","五","療法科普 Carousel（衝擊波）","Carousel","★★★"),
    ("Day 20","六","Story：生活日常","Story","★★"),
    ("Day 21","日","互動日","互動","★"),
    ("Day 22","一","個案分享 #3 Carousel","Carousel","★★★★"),
    ("Day 23","二","Story","Story","★★"),
    ("Day 24","三","比較 Reel（3種療法）","Reel","★★★★"),
    ("Day 25","四","Story","Story","★★"),
    ("Day 26","五","個案分享 #4 Carousel","Carousel","★★★★"),
    ("Day 27","六","Story：生活分享","Story","★★"),
    ("Day 28","日","互動日","互動","★"),
    ("Day 29","一","個案分享 #5 Carousel","Carousel","★★★"),
    ("Day 30","二","30日總結 Reel","Reel","★★★★"),
]
for row in schedule:
    pdf.table_row(list(row), [18,16,90,26,20])
pdf.ln(3)
pdf.warn("Day 3（個人故事）同 Day 17（留言換資料）係最重要兩條 Reel——要花最多時間準備，拍唔好就重拍。")

# ── PART 3: WEEK 1 ───────────────────────────────────────────
pdf.add_page()
pdf.ch_title("第三部分：Week 1 詳細指引（Day 1-7）帳號建立期")

# Day 1
pdf.day_bar(1, "週一", "帳號介紹 Carousel", "4頁 Carousel")
pdf.section_bar("圖片設計指引（4頁）", bg=(27,58,107))
for name, desc in [
    ("封面（第1頁）",
     "背景：深藍 #1B3A6B\n上方白色小字：STANLEY｜痛症方案顧問\n中間白色粗體大字：「我唔係醫生 / 但我知你嘅痛 / 點解搞唔掂」\n下方青綠色小字：👉 向左掃了解更多"),
    ("第2頁",
     "背景：白色，左側深藍豎線\n標題（深藍粗體）：我係 Stanley\n內文：✅ X年痛症管理經驗 / ✅ 見過幾百個真實個案 / ✅ 了解多種療法\n我的工作：幫你搵啱最適合你的方案，唔係幫你賣任何東西"),
    ("第3頁",
     "背景：白色\n標題（深藍）：呢個 IG 你會睇到\n4個方格：📂每週個案分享 / 🔬痛症謬誤破解 / 💊療法比較解釋 / 🆓免費方案諮詢\n底部青綠橫條：DM 我，免費傾吓"),
    ("第4頁（CTA）",
     "背景：深藍\n白色大字：你而家有痛症困擾？\n白色細字：唔知應該睇邊科？/ 試過好多方法但冇用？/ 唔知做物理治療定中醫好？\n青綠按鈕：DM 我 / Link in Bio"),
]:
    pdf.slide_label(name)
    pdf.box(desc)

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("我係 Stanley，痛症方案顧問。\n唔係醫生，唔係治療師——\n但過去 [X] 年，我見過幾百個有痛症問題的人。\n\n呢個 IG，我會每週分享：\n📂 真實個案（全部匿名）\n🔬 拆解坊間痛症謬誤\n💊 唔同療法比較同解釋\n\n有痛症困擾？歡迎 DM 我，免費傾吓 😊\n\n#痛症 #痛症管理 #香港痛症 #肩頸痛 #腰背痛 #坐骨神經痛 #痛症顧問", bg=(245,250,255))

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
Follow 住先，或者 DM 我，我哋傾吓。」

【字幕提示（Reel 必加）】
開場：「你痛過，但醫生話你冇事？」
中段：「我唔係醫生，但我見過幾百個案」
結尾：「DM 我，免費幫你分析」""", bg=(245,250,255))

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("點解我會做痛症方案顧問？\n\n唔係因為呢行賺錢——\n係因為我見過太多人，痛咗幾年，試過好多方法，但搵唔到啱自己的方案。\n\n呢個 IG：📂 真實個案 | 🔬 謬誤破解 | 💊 療法比較\n\n有任何痛症困擾，DM 我，免費傾吓 😊\n\n#痛症 #痛症管理 #個人故事 #香港 #痛症顧問", bg=(245,250,255))

pdf.ln(1)
pdf.day_bar(4, "週四", "Story：Q&A", "Story")
pdf.box("背景：白色或淺藍\n文字：「你有咩關於痛症嘅問題想問我？」\n加入 IG 問答貼紙\n收到問題後，Day 6 Story 回答")

pdf.day_bar(5, "週五", "互動日（無發帖）", "互動任務")
pdf.box("1. 去 #痛症 #肩頸痛 #腰背痛 下留有意義留言\n2. 回覆所有 Day 1-4 嘅留言\n3. 回覆 DM\n時間：15-20 分鐘")

pdf.day_bar(6, "週六", "Story：日常 + 投票", "Story")
pdf.box("隨手拍一個日常畫面（食早餐/工作環境）\n文字：「準備緊下週個案分享——你最想睇邊類？」\n投票貼紙：頸肩痛 / 膝蓋痛 / 腰背痛 / 其他")

pdf.day_bar(7, "週日", "互動日", "互動任務")
pdf.box("回覆所有本週留言\n查看 Story 投票結果，記低受眾最多咩痛症\n思考下週個案分享主題（配合投票結果）")

# ── PART 4: WEEK 2 ───────────────────────────────────────────
pdf.add_page()
pdf.ch_title("第四部分：Week 2 詳細指引（Day 8-14）內容引流期")

pdf.day_bar(8, "週一", "個案分享 #1（頸痛2年）", "6頁 Carousel")
pdf.section_bar("圖片設計（6頁）", bg=(27,58,107))
for name, desc in [
    ("封面（第1頁）", "背景：深藍\n上方白字小：📂 個案分享 第1回\n中間白字大：「頸痛2年 / 做過物理治療 / 都冇用？」\n下方青綠：向左掃看個案詳情 👉"),
    ("第2頁（客人背景）", "背景：白色，頂部深藍橫條（白字）：🙋🏻 客人背景\n年齡：30歲出頭 / 職業：銀行文職 / 每日對住電腦 8 小時"),
    ("第3頁（問題）", "背景：白色，頂部青綠橫條：🎯 困擾問題\n〈頸椎痛 + 頭痛〉\n• 頸梗到轉唔到頭  • 嚴重時連帶頭痛  • 嚴重影響睡眠"),
    ("第4頁（試過嘅方法）", "背景：白色，頂部橙色橫條：🚨 試過但冇用\n❌ 物理治療6次——做完舒服，兩日後痛返\n❌ 頸部按摩器——一個月冇改善\n❌ 止痛藥——停藥就痛返"),
    ("第5頁（方案+效果）", "背景：白色，頂部深藍橫條：✅ 最終方案\n衝擊波 + 姿勢矯正訓練（根源：頸椎輕微錯位）\n📈 4次療程後：頭痛消失 / 活動度改善 / 冇再反覆\n⭐️ 難度：★★★☆☆"),
    ("第6頁（CTA）", "背景：深藍\n白字大：唔知自己係咪同樣情況？\n白字細：DM 我，免費幫你分析\n青綠：Link in Bio 預約免費諮詢 👆🏻"),
]:
    pdf.slide_label(name)
    pdf.box(desc)

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("【頸痛2年，做過物理治療都冇用？】\n📂 個案分享第 1 回  #Stanley痛症個案\n\n🙋🏻 客人背景：30歲出頭，銀行文職\n🎯 困擾：頸椎痛 + 頭痛，每日對住電腦8小時\n🚨 試過：物理治療6次、按摩器、止痛藥——全部治標不治本\n✅ 方案：衝擊波 + 姿勢矯正（根源係頸椎輕微錯位）\n📈 4次後：頭痛消失，活動度改善，冇再反覆\n\n唔知自己係咪同樣情況？DM 我，免費幫你分析 😊\n\n#頸椎痛 #頸痛 #頭痛 #辦公室痛症 #痛症 #痛症管理 #衝擊波治療 #香港痛症", bg=(245,250,255))

pdf.add_page()
pdf.day_bar(10, "週三", "迷思破解 Reel（熱敷vs凍敷）", "45秒 Reel")
pdf.section_bar("封面圖設計", bg=(27,58,107))
pdf.box("背景：深藍\n大字白色：「熱敷定凍敷？/ 9成人整錯 冰火圖示」\n小字青綠：你係咪其中之一？\n右下角：Stanley｜痛症方案顧問")

pdf.section_bar("拍攝 Pose 指引", bg=(42,157,143))
for p in ["地點：廚房/浴室門口或白牆前","道具：一包冰（凍敷）+ 一條熱毛巾（熱敷）","開場：正面望鏡頭，企直，兩手各持一樣道具","講「急性受傷」：舉起冰袋","講「慢性痛症」：舉起熱毛巾","結尾：放低道具，雙手垂低，直視鏡頭"]:
    pdf.bullet(p)
pdf.ln(1)

pdf.section_bar("完整影片腳本（45秒）", bg=(60,80,120))
pdf.box("""【開場 0-5秒】
「拉傷咗第一時間熱敷？你可能愈敷愈差。」

【中段 5-35秒】
「好多人記得一個原則：痛就熱敷。但呢係最常見嘅誤解之一。

正確做法：
急性受傷——即係頭48小時——要用凍敷。
原因係新傷有炎症反應，血管擴張緊。熱敷係幫炎症擴散，只會更嚴重。
凍敷係收窄血管，控制炎症，減腫脹。

相反，慢性痛症——例如長期頸痛、腰痛——
係可以熱敷嘅，幫肌肉放鬆，增加血液循環。

問題唔係熱敷定凍敷——係你先要判斷：係急性，定係慢性？」

【結尾 35-45秒】
「唔確定係哪種？下面 Comment 打「評估」，我即刻 PM 你一份自我判斷指引。」""", bg=(245,250,255))

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("熱敷定凍敷？9成人整錯\n\n急性受傷（頭48小時）→ 凍敷\n慢性痛症（長期反覆）→ 熱敷\n\n搞錯咗唔係冇效，係愈搞愈差\n\n👇 Comment 打「評估」\n即刻 PM 你份自我判斷指引\n\n#痛症 #熱敷 #凍敷 #頸痛 #腰痛 #痛症常識 #香港痛症", bg=(245,250,255))

pdf.add_page()
pdf.day_bar(12, "週五", "辦公室急救貼士 Carousel", "5頁 Carousel")
pdf.section_bar("圖片設計（5頁）", bg=(27,58,107))
for name, desc in [
    ("封面（第1頁）", "背景：深藍\n大字白色：「OT 頸痛 / 即時急救 / 3個動作」\n小字青綠：做完即時舒緩 👉"),
    ("第2-4頁（每頁一個動作）", "背景：白色，頂部青綠橫條：動作 1 / 2 / 3\n標題（深藍粗體）：[動作名稱]\n圖示：Canva 人型火柴圖 或 自己示範靜態圖\n說明：動作描述 + 保持X秒 + 重複X次\n底部小字：如持續痛超過2週，建議尋求評估"),
    ("第5頁（CTA）", "背景：深藍\n白字：「做完仲係痛？ / 可能唔係累—— / 係需要評估的信號」\n青綠：DM 我，免費傾吓"),
]:
    pdf.slide_label(name)
    pdf.box(desc)

pdf.section_bar("三個動作內容", bg=(42,157,143))
for name, desc in [
    ("動作1：頸部側伸展", "頭側向右邊，右手輕輕放頭頂加少少壓力\n感受左邊頸側拉緊——保持15秒，換邊做"),
    ("動作2：肩膀後收", "雙手垂低，肩膀向後收，盡量夾埋兩邊肩胛骨\n保持10秒，重複5次，對抗長期向前伸的姿勢"),
    ("動作3：頸部後縮（Chin Tuck）", "下巴輕輕向後縮，好似有人用手指頂住你前額\n唔係低頭，係向後縮，保持5秒，重複10次\n激活頸深層肌肉，最多物理治療師都會教嘅動作"),
]:
    pdf.slide_label(name)
    pdf.box(desc)

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("OT 頸痛急救 3招\n\n第1招：頸部側伸展\n第2招：肩膀後收\n第3招：Chin Tuck 頸後縮\n\n每日做，5分鐘，收工即刻做\n\n如果做完仲係痛，或者痛超過2週——\n可能唔係「累」，係需要評估\n\nDM 我，免費傾吓\n\n#頸痛 #OT #辦公室痛症 #頸椎痛 #打工仔 #痛症管理 #香港痛症", bg=(245,250,255))

# ── PART 5: WEEK 3 ───────────────────────────────────────────
pdf.add_page()
pdf.ch_title("第五部分：Week 3 詳細指引（Day 15-21）互動爆發期")

pdf.day_bar(15, "週一", "個案分享 #2（膝蓋退化）", "6頁 Carousel")
pdf.section_bar("個案內容", bg=(42,157,143))
pdf.box("客人背景：50歲，家庭主婦\n困擾：膝關節退化，落樓梯必定痛，行多路腫脹，骨科建議考慮換骨\n試過：玻尿酸針（費用高需定期打）/ 消炎藥（胃副作用）/ 護膝（無根治）\n最終方案：體外衝擊波 + 股四頭肌訓練\n根源分析：周邊肌肉太弱，令膝關節承受不必要壓力\n效果（3個月）：落樓梯痛感由8分降至2分，腫脹明顯減退，暫時唔需要手術\n難度：★★★★☆\n\n設計格式完全參考 Day 8。封面文字：「膝蓋痛到以為要換骨 / 最後唔使手術」", bg=(245,250,255))

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("【膝蓋痛到以為要換骨，最後唔使手術】\n📂 個案分享第 2 回  #Stanley痛症個案\n\n🙋🏻 50歲，家庭主婦\n🎯 膝關節退化，落樓梯必定痛\n🚨 玻尿酸針、消炎藥、護膝——冇根治\n✅ 衝擊波 + 股四頭肌訓練（根源係肌肉太弱）\n📈 3個月後：痛感由8分降至2分，暫唔需要手術\n\n退化係無法逆轉嘅，但「痛」係可以控制嘅。\nDM 我，唔一定要手術先係唯一出路 😊\n\n#膝蓋痛 #膝關節退化 #退化性關節炎 #痛症 #痛症管理 #香港痛症", bg=(245,250,255))

pdf.add_page()
pdf.day_bar(17, "週三", "留言換資料 Reel【核武】", "60秒 Reel")
pdf.warn("呢條係整個30日計劃最重要嘅一條——要花最多時間準備。拍唔好就重拍，直至你自己覺得「有力」先 post。")

pdf.section_bar("封面圖設計", bg=(27,58,107))
pdf.box("背景：深藍\n上方白字小：止痛藥依賴？\n中間白字大：「食完又痛返 / 係因為你 / 搵錯方向了」\n下方青綠色：留言「止痛」換免費指南 👇")

pdf.section_bar("拍攝 Pose 指引", bg=(42,157,143))
for p in ["地點：坐喺枱前或梳化，背景乾淨","道具（可選）：桌上放一盒 Panadol，開場時指住佢","開場3秒：嚴肅表情，望鏡頭，停頓一下先講","解釋部分：自然手勢，唔需要刻意","講「火警警報」比喻時：雙手做「擴散」手勢","結尾：輕鬆表情，直接提醒留言","重要：前10秒係關鍵——要令人想繼續睇"]:
    pdf.bullet(p)
pdf.ln(1)

pdf.section_bar("完整影片腳本（60秒）", bg=(60,80,120))
pdf.box("""【開場 0-5秒——鉤子】
「你食止痛藥，食完唔痛，停咗又痛返——你有冇諗過，係咪你一直食錯咗？」

【中段 5-45秒——核心內容】
「好多人以為止痛藥係治痛嘅。
但其實止痛藥做嘅嘢，係阻斷你感受痛嘅神經信號——佢唔係幫你修復任何嘢。

打個比喻：你屋企火警警報響——你唔係去滅火，而係拆咗警報器。
火依然喺度燒，只係你唔知咋。

痛係身體話俾你知有問題嘅信號。止痛藥係關閉信號，唔係解決問題。

咁根源係咩？好多人嘅慢性痛症，根源得幾樣：
1. 肌肉失衡——某部分肌肉太弱，另一部分補償過度
2. 關節錯位——長期姿勢問題積累
3. 筋膜沾黏——舊患未正確處理

唔同根源，方向完全唔同。」

【結尾 45-60秒——CTA】
「我整理咗一份【慢性痛症根源自我判斷清單】
喺下面 Comment 打「止痛」，我即刻 PM 俾你。唔收費，直接用。」""", bg=(245,250,255))

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("止痛藥食完又痛返？唔係你食得唔夠，係你搵錯方向了\n\n止痛藥 = 關閉警報器，根源問題 = 火依然喺燒\n\n慢性痛症根源通常得幾樣：\n1. 肌肉失衡\n2. 關節錯位\n3. 筋膜沾黏\n\n👇 Comment 打「止痛\"\n即刻 PM 你份【慢性痛症根源自我判斷清單】\n免費，直接用\n\n#止痛藥 #慢性痛症 #痛症根源 #頸痛 #腰痛 #痛症管理 #香港痛症", bg=(245,250,255))

pdf.warn("準備工作：Day 17 發佈前，必須備好「慢性痛症根源自我判斷清單」PDF，收到留言即刻可以 PM。")

pdf.add_page()
pdf.day_bar(19, "週五", "療法科普（衝擊波）", "5頁 Carousel")
pdf.section_bar("各頁內容", bg=(27,58,107))
for name, desc in [
    ("封面", "背景：深藍\n大字白色：「衝擊波治療 / 係咩？ / 用3分鐘解釋清楚」"),
    ("第2頁：原理", "衝擊波 = 聲波能量，透過儀器傳入身體深層組織\n→ 刺激細胞再生  → 促進血液循環\n→ 打散鈣化沉積  → 啟動自我修復機制"),
    ("第3頁：適合情況", "✅ 慢性肌腱炎（網球肘、足底筋膜炎）\n✅ 肌腱撕裂（旋轉肌、跟腱）\n✅ 鈣化性肌腱炎\n✅ 運動創傷康復"),
    ("第4頁：唔適合情況", "❌ 急性炎症期（受傷頭48小時）\n❌ 骨折未癒合\n❌ 懷孕期間\n❌ 有凝血問題人士\n注意：唔係人人都適合，要先評估"),
    ("第5頁（CTA）", "背景：深藍\n白字：想知自己係咪適合衝擊波？\n青綠：DM 我，免費幫你評估 👇"),
]:
    pdf.slide_label(name)
    pdf.box(desc)

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("衝擊波係咩？唔係電療，唔係打針\n\n好多客第一次聽「衝擊波」都一面懵\n今次幫大家解釋清楚——包括哪些人不適合做\n\n向左掃睇完整解釋 👉\n\n有問題？DM 我，免費傾吓\n\n#衝擊波 #衝擊波治療 #痛症治療 #肌腱炎 #足底筋膜炎 #網球肘 #運動創傷", bg=(245,250,255))

# ── PART 6: WEEK 4 ───────────────────────────────────────────
pdf.add_page()
pdf.ch_title("第六部分：Week 4 詳細指引（Day 22-30）深化建立期")

pdf.day_bar(22, "週一", "個案分享 #3（健身男肩痛）", "6頁 Carousel")
pdf.section_bar("個案內容", bg=(42,157,143))
pdf.box("客人背景：28歲，自僱，健身3年\n困擾：做 Bench Press 時右肩刺痛，右手舉高就痛，停健身兩個月仍反覆\n試過：痛症貼布（舒緩無根治）/ 跌打（做完好但練番又痛）/ 以為「休息夠就好」\n最終方案：體外衝擊波 + 旋轉肌專項訓練\n根源：肌腱輕微撕裂 + 健身動作有代償\n效果（6次）：恢復訓練無刺痛，Bench Press 重量仲升咗，學識正確肩部動作防復發\n難度：★★★★☆\n\n封面文字：「健身男 / 忍痛練落去 / 係最錯嘅決定」\n設計格式參考 Day 8", bg=(245,250,255))

pdf.add_page()
pdf.day_bar(24, "週三", "比較 Reel（3種療法）", "60秒 Reel")
pdf.section_bar("封面圖設計", bg=(27,58,107))
pdf.box("背景：深藍\n大字白色：「中醫 vs 物理治療 / vs 儀器治療 / 邊個最啱你？」\n青綠色：睇完你就知")

pdf.section_bar("拍攝 Pose 指引", bg=(42,157,143))
for p in ["地點：坐喺枱前，桌上放3張白紙","每張白紙寫：中醫 / 物理治療 / 儀器治療","開場：指住3張紙，問「你知邊個最啱你嗎？」","介紹每種療法時：指住對應嘅紙","分析「適合邊種人」時：望鏡頭直接講"]:
    pdf.bullet(p)
pdf.ln(1)

pdf.section_bar("完整影片腳本（60秒）", bg=(60,80,120))
pdf.box("""【開場 0-5秒】
「中醫、物理治療、儀器治療——唔係哪個最好，係哪個最啱你。」

【中段 5-50秒】
「三種療法，三種邏輯：

中醫：從整體入手，調理身體環境。
適合：慢性痛症、反覆發作、體質偏弱
唔適合：需要即時止痛嘅急性創傷

物理治療：以運動同手法矯正為主。
適合：姿勢問題、肌力不足、術後康復
唔適合：喺家唔做功課嘅人——PT需要你配合

儀器治療（如衝擊波）：直接針對組織修復。
適合：肌腱炎、鈣化問題、PT效果唔理想
唔適合：急性炎症期

所以問題唔係邊個好——係你係哪種情況，就用哪種方案。
好多人失敗，係因為一開始用錯咗方向。」

【結尾 50-60秒】
「唔確定自己適合邊種？DM 我，免費幫你判斷。」""", bg=(245,250,255))

pdf.day_bar(26, "週五", "個案分享 #4", "6頁 Carousel")
pdf.box("自選一個你最近處理過的真實個案，格式完全同 Day 8。\n\n封面公式：「[症狀] / [轉折句] / [結果]」\n例：「坐骨神經痛 / 睇咗半年 / 終於唔使打針」\n設計同 Day 8 一樣，換內容即可。")

pdf.day_bar(29, "週一", "個案分享 #5", "6頁 Carousel")
pdf.box("自選個案，格式同 Day 8。\n建議揀一個最能展示你「顧問視角」嘅個案——試過唔同方法最後搵到啱方向嘅故事。")

pdf.add_page()
pdf.day_bar(30, "週二", "30日總結 Reel", "60秒 Reel")
pdf.section_bar("封面圖設計", bg=(27,58,107))
pdf.box("背景：深藍\n大字白色：「開咗30日 / 我學到啲咩」\n青綠色：真心話 👇")

pdf.section_bar("拍攝 Pose 指引", bg=(42,157,143))
pdf.box("同 Day 3（個人故事）設定相同：坐喺梳化或枱前，輕鬆自然，對住鏡頭講。")

pdf.section_bar("完整影片腳本（60秒）", bg=(60,80,120))
pdf.box("""【開場 0-5秒】
「呢個 IG 開咗30日，我想同大家分享幾樣嘢。」

【中段 5-45秒】
「第一樣：好多人有痛症，但唔知由邊度開始——呢個係我見到最多嘅情況。

第二樣：坊間謬誤真係好多——呢個月我分享過[X個]，每一個都有人話係第一次聽到正確答案。

第三樣：[你自己覺得最有意義嘅一句話，來自某個個案]

三十日前，我開呢個 IG 係因為想幫到更多人——
唔係因為賣嘢，係因為睇住咁多人痛咗咁耐都搵唔到方向。」

【結尾 45-60秒】
「如果你今日先第一次睇到我——我係 Stanley，痛症方案顧問。
每週分享真實個案、療法比較、痛症知識。
Follow 住，下個月仲有更多。或者 DM 我，免費傾吓你的情況。」""", bg=(245,250,255))

pdf.section_bar("Caption 文案", bg=(60,80,120))
pdf.box("開咗30日，最多人問我嘅問題係：\n「我試過好多方法，點解都唔work？」\n\n答案通常係：方向未必錯，但順序錯了。\n\n下個月繼續分享更多個案同療法知識。\n有任何痛症問題，DM 我 😊\n\n#痛症 #痛症管理 #香港痛症 #一個月總結", bg=(245,250,255))

# ── PART 7: DAILY ENGAGEMENT ─────────────────────────────────
pdf.add_page()
pdf.ch_title("第七部分：每日15分鐘互動任務")
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
]:
    pdf.table_row(list(row), [40,150])

# ── PART 8: CHECKLIST ────────────────────────────────────────
pdf.add_page()
pdf.ch_title("第八部分：開始前準備清單（Day 1 前必須搞掂）")
pdf.table_header(["準備事項","說明"], [50,140])
for row in [
    ("Canva 帳號","免費版夠用。設定好品牌顏色（3個Hex Code）同字體。"),
    ("帳號名稱","決定好，一旦開始唔好改。建議：stanley.paincare.hk"),
    ("Bio 寫好","參考本手冊 Bio 設計，加入你真實嘅年資同聯絡方式。"),
    ("留言換資料 PDF","「慢性痛症根源自我判斷清單」——Week 3 前必須準備好。"),
    ("DM 標準回覆模板","收到 DM 後的第一句寫好，唔好每次即興。"),
    ("手機架/三腳架","拍 Reel 必備。50-100港元，淘寶或士多可以搵到。"),
    ("補光燈（可選）","夜晚拍攝用，100-200港元。日間有自然光可以唔使。"),
    ("真實個案5個","準備5個真實個案（匿名），記低：背景/問題/試過方法/方案/效果。"),
]:
    pdf.table_row(list(row), [50,140])

pdf.ln(6)
pdf.warn("最快開始方法：今日搞掂 Canva 設定，明日完成 Day 1 帳號介紹 Carousel，後日正式 post 出去。唔好等完美，先開始先。")

# ── APPENDIX ─────────────────────────────────────────────────
pdf.add_page()
pdf.ch_title("附錄：完整 Caption 文案索引")
pdf.body("以下為本手冊所有 Caption 文案的快速索引，方便 copy-paste 使用。")
pdf.ln(2)

pdf.table_header(["發帖日","類型","Caption 開頭"], [20,55,115])
for row in [
    ("Day 1","帳號介紹","我係 Stanley，痛症方案顧問..."),
    ("Day 3","個人故事 Reel","點解我會做痛症方案顧問？..."),
    ("Day 8","個案分享 #1（頸痛）","【頸痛2年，做過物理治療都冇用？】..."),
    ("Day 10","迷思破解（熱敷vs凍敷）","熱敷定凍敷？9成人整錯..."),
    ("Day 12","辦公室急救貼士","OT 頸痛急救 3招..."),
    ("Day 15","個案分享 #2（膝蓋痛）","【膝蓋痛到以為要換骨，最後唔使手術】..."),
    ("Day 17","留言換資料 Reel","止痛藥食完又痛返？..."),
    ("Day 19","療法科普（衝擊波）","衝擊波係咩？唔係電療，唔係打針..."),
    ("Day 24","比較 Reel（3種療法）","中醫 vs 物理治療 vs 儀器治療..."),
    ("Day 30","30日總結 Reel","開咗30日，最多人問我嘅問題係..."),
]:
    pdf.table_row(list(row), [20,55,115])

pdf.ln(8)
pdf.set_font("ArialUnicode", "B", 10)
pdf.set_text_color(27, 58, 107)
pdf.cell(0, 7, "如需任何內容更新或新增，隨時繼續完善本手冊。", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("ArialUnicode", "", 9)
pdf.set_text_color(100,100,100)
pdf.cell(0, 6, "Stanley 痛症 IG 30日執行手冊 | 生成於 2026年5月", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.output(OUTPUT_PATH)
print(f"Done: {OUTPUT_PATH}")