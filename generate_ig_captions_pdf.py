from fpdf import FPDF

FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
OUTPUT_PATH = "/Users/rickyc./Desktop/Vs code /Project 2 (Stanley)/Stanley_IG_十大文案.pdf"

CAPTIONS = [
    {
        "num": 1,
        "title": "頸痛打工仔",
        "pillar": "生活場景共鳴",
        "format": "Reel 15-30秒",
        "priority": "🔥 最優先",
        "body": (
            "返工坐夠8小時\n"
            "放工頸梗到轉唔到頭\n"
            "你以為係姿勢問題——\n"
            "其實係你條筋膜已經黏埋一路\n\n"
            "唔係按一按就算㗎\n"
            "你需要嘅係真正放鬆筋膜嘅方法👇\n\n"
            "留言「頸」我送你一個即用評估🙋‍♀️\n\n"
            "#頸痛 #打工仔 #香港痛症 #辦公室痛症"
        ),
    },
    {
        "num": 2,
        "title": "腰痛最大誤解",
        "pillar": "科普糾錯",
        "format": "Carousel 5-7 slides",
        "priority": "每兩週一次",
        "body": (
            "【腰痛≠要休息】好多人越休息越痛，原因係⋯⋯\n\n"
            "➡️ Slide 1：「腰痛就要躺平」— 大錯特錯\n"
            "➡️ Slide 2：真正原因係核心肌群失活\n"
            "➡️ Slide 3：你應該做的 vs 你一直做錯的\n"
            "➡️ Slide 4：一個動作自測你嘅腰有幾危\n"
            "➡️ Slide 5：想知自己屬於邊種？DM「腰」\n\n"
            "痛係信號，唔係叫你停下嚟\n\n"
            "#腰痛 #腰背痛 #香港 #痛症治療"
        ),
    },
    {
        "num": 3,
        "title": "美容 × 痛症獨家角度",
        "pillar": "美容 × 痛症",
        "format": "Reel",
        "priority": "🔥 你嘅獨家武器",
        "body": (
            "做完 facial 仍然顯老？\n"
            "可能唔係個皮膚問題——\n\n"
            "係你副頸㗎\n\n"
            "頸前傾 → 下巴紋加深 → 顴骨位變扁\n"
            "體態影響你個樣，多過你想像\n\n"
            "美容做100次，唔解決根源都係白費💆‍♀️\n\n"
            "想知你副頸係咪影響緊你個樣？\n"
            "留言「頸樣」👇\n\n"
            "#體態矯正 #美容 #痛症 #香港女生 #駝背"
        ),
    },
    {
        "num": 4,
        "title": "真人見證 Tracy",
        "pillar": "真人前後 / Social Proof",
        "format": "Static（真人相）",
        "priority": "有見證就出",
        "body": (
            "「以為膝痛係老人病，點知我得32歲」\n\n"
            "Tracy，文員，每日上落樓梯都係挑戰\n"
            "做完6次療程後——第一次可以行完整個沙田廣場\n\n"
            "佢話：「唔係神奇，係終於搵對原因」\n\n"
            "你嘅痛，可能一直都係有得解決的\n"
            "📩 DM 我了解更多\n\n"
            "#膝痛 #真實見證 #香港痛症 #痛症治療"
        ),
    },
    {
        "num": 5,
        "title": "肩頸族夜晚共鳴",
        "pillar": "生活場景共鳴",
        "format": "Reel 15-30秒",
        "priority": "🔥 最優先",
        "body": (
            "每晚訓落枕頭\n"
            "係唔係有一邊膊頭唔知點解高咗？\n\n"
            "唔係你訓姿勢問題\n"
            "係你係日頂住一邊揼電話、打字\n"
            "肌肉已經記憶咗呢個歪嘅位置\n\n"
            "歪得耐，個樣都會跟住歪\n\n"
            "想知你歪咗幾多？\n"
            "留言「膊頭」我教你自測方法🙋\n\n"
            "#肩頸痛 #姿勢矯正 #香港 #打工仔痛症"
        ),
    },
    {
        "num": 6,
        "title": "5種你唔知係痛症嘅症狀",
        "pillar": "科普糾錯",
        "format": "Carousel 5-7 slides",
        "priority": "每兩週一次",
        "body": (
            "【唔係腰痛先係痛症】\n"
            "呢5樣嘢，好多人唔知係身體響緊警號👇\n\n"
            "1️⃣ 早上起床手指攣住\n"
            "2️⃣ 坐低超過20分鐘就坐唔住\n"
            "3️⃣ 深呼吸嗰下背部有輕微刺痛\n"
            "4️⃣ 落樓梯膝頭有輕微卡住感\n"
            "5️⃣ 仰頭望天花板會頭暈\n\n"
            "中咗幾個？\n"
            "留言數字，我逐一解釋你係邊種情況\n\n"
            "#痛症 #健康常識 #香港健康 #預防痛症"
        ),
    },
    {
        "num": 7,
        "title": "拉筋反直覺 Hook",
        "pillar": "科普糾錯",
        "format": "Reel 15-30秒",
        "priority": "🔥 最優先",
        "body": (
            "「我每日拉筋，點解痛症冇改善？」\n\n"
            "因為你拉嘅方向，係加深你嘅問題\n\n"
            "坐骨神經痛患者做呢個動作👇\n"
            "係加壓——唔係放鬆\n\n"
            "我知你睇過好多 YouTube 教程\n"
            "但每個人嘅痛症根源唔同\n"
            "一個方法唔係萬能\n\n"
            "想知你嘅情況係咪做錯咗？留言「拉筋」\n\n"
            "#坐骨神經痛 #拉筋 #痛症知識 #香港"
        ),
    },
    {
        "num": 8,
        "title": "美容 × 痛症 靜態引發思考",
        "pillar": "美容 × 痛症",
        "format": "Static",
        "priority": "🔥 你嘅獨家武器",
        "body": (
            "你花幾多時間保養皮膚？\n"
            "又花咗幾多時間保養身體？\n\n"
            "皮膚老化係外在\n"
            "筋膜退化係內在\n\n"
            "兩樣都影響你嘅外貌\n"
            "但大部分人只顧一樣\n\n"
            "真正嘅狀態管理，由內到外一起做\n\n"
            "📩 了解我哋嘅方案\n\n"
            "#美容 #痛症 #筋膜 #香港女生健康 #整體健康"
        ),
    },
    {
        "num": 9,
        "title": "Poll 結果分享互動",
        "pillar": "互動 Story 轉 Post",
        "format": "Static / Story",
        "priority": "每月一次",
        "body": (
            "上週問大家：「你有冇長期痛症但唔理？」\n\n"
            "78% 話「有，但唔知去邊」\n"
            "只有 22% 話「有跟進緊」\n\n"
            "呢個數字唔令我意外\n"
            "因為大部分人唔係唔想處理\n"
            "係唔知從何入手\n\n"
            "我哋做嘅，就係幫你搵到呢個「入手位」\n\n"
            "今日起，留言或 DM 我「評估」\n"
            "我哋幫你揾清楚根源 💬\n\n"
            "#香港痛症 #痛症管理 #從何入手"
        ),
    },
    {
        "num": 10,
        "title": "CTA 收網 Offer",
        "pillar": "Call To Action",
        "format": "Reel",
        "priority": "每月收網一次",
        "body": (
            "如果你係咁——\n\n"
            "✅ 長期頸痛腰痛唔見好\n"
            "✅ 試過唔同方法冇效果\n"
            "✅ 唔知自己嘅痛係咪有得醫\n\n"
            "我想同你傾15分鐘\n\n"
            "唔係賣嘢\n"
            "係真正幫你了解自己嘅情況\n\n"
            "📩 DM「評估」或 WhatsApp 我\n"
            "名額有限，認真嘅先留言\n\n"
            "#痛症治療 #香港 #免費評估 #痛症解決方案"
        ),
    },
]

PILLAR_COLORS = {
    "生活場景共鳴":     (30, 80, 140,   220, 235, 255),
    "科普糾錯":         (20, 100, 60,    220, 255, 230),
    "美容 × 痛症":      (120, 30, 100,   255, 220, 248),
    "真人前後 / Social Proof": (140, 70, 0, 255, 240, 210),
    "互動 Story 轉 Post": (60, 60, 60,   240, 240, 240),
    "Call To Action":   (160, 10, 10,    255, 220, 220),
}


class PDF(FPDF):
    def multi_cell(self, *args, **kwargs):
        kwargs.setdefault("new_x", "LMARGIN")
        return super().multi_cell(*args, **kwargs)

    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("u", size=8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Stanley IG 十大文案手冊  |  第 {self.page_no()} 頁", align="C")

    def cover(self):
        self.add_page()
        self.set_fill_color(15, 15, 30)
        self.rect(0, 0, 210, 297, "F")

        # Decorative top bar
        self.set_fill_color(180, 130, 255)
        self.rect(0, 0, 210, 4, "F")

        self.set_y(65)
        self.set_font("u", size=11)
        self.set_text_color(160, 120, 220)
        self.multi_cell(0, 7, "Stanley  ·  美容 × 痛症管理", align="C")
        self.ln(6)

        self.set_font("u", size=28)
        self.set_text_color(255, 255, 255)
        self.multi_cell(0, 14, "IG 十大文案手冊", align="C")
        self.ln(4)

        self.set_font("u", size=13)
        self.set_text_color(180, 230, 255)
        self.multi_cell(0, 8, "四大內容柱  ×  十個即用文案", align="C")
        self.ln(10)

        # Pillars summary box
        box_y = self.get_y()
        self.set_fill_color(28, 28, 55)
        self.set_draw_color(80, 80, 160)
        self.rect(25, box_y, 160, 68, "FD")
        self.set_y(box_y + 6)

        pillars = [
            ("柱一", "生活場景共鳴",   "Stop the scroll，觸發「係我呀！」"),
            ("柱二", "真人前後",       "建立信任，推動詢問"),
            ("柱三", "科普糾錯",       "成為 go-to 資訊來源"),
            ("柱四", "美容 × 痛症",    "你嘅獨家差異化角度"),
        ]
        colors = [(100, 180, 255), (255, 180, 100), (100, 220, 140), (255, 140, 220)]
        for (label, name, desc), col in zip(pillars, colors):
            self.set_font("u", size=10)
            self.set_text_color(*col)
            self.set_x(30)
            self.cell(18, 7, label)
            self.set_text_color(255, 255, 255)
            self.cell(45, 7, name)
            self.set_text_color(160, 160, 200)
            self.set_font("u", size=9)
            self.multi_cell(0, 7, desc, new_x="LMARGIN")

        self.ln(10)
        self.set_font("u", size=9)
        self.set_text_color(80, 80, 120)
        self.multi_cell(0, 6, "2026年5月  ·  主攻 25–40 歲香港打工仔/女  ·  IG 優先", align="C")

        # Decorative bottom bar
        self.set_fill_color(180, 130, 255)
        self.rect(0, 293, 210, 4, "F")

    def caption_page(self, cap):
        self.add_page()

        pillar = cap["pillar"]
        bg_r, bg_g, bg_b, tx_r, tx_g, tx_b = PILLAR_COLORS.get(pillar, (40, 40, 80, 220, 220, 255))

        # Header strip
        self.set_fill_color(bg_r, bg_g, bg_b)
        self.rect(0, 0, 210, 28, "F")

        # Post number badge
        self.set_fill_color(255, 255, 255)
        self.set_text_color(bg_r, bg_g, bg_b)
        self.set_font("u", size=16)
        self.set_xy(15, 6)
        self.cell(18, 16, f"#{cap['num']:02d}", fill=True, align="C")

        # Title
        self.set_text_color(tx_r, tx_g, tx_b) if (bg_r + bg_g + bg_b) < 300 else self.set_text_color(20, 20, 40)
        self.set_font("u", size=15)
        self.set_xy(37, 7)
        self.cell(0, 8, cap["title"])

        # Pillar tag
        self.set_font("u", size=9)
        self.set_xy(37, 17)
        self.set_text_color(tx_r, tx_g, tx_b) if (bg_r + bg_g + bg_b) < 300 else self.set_text_color(50, 50, 80)
        self.cell(0, 7, f"內容柱：{pillar}")

        # Meta row
        self.set_y(33)
        self.set_fill_color(245, 245, 252)
        self.set_draw_color(210, 210, 230)
        self.rect(15, 33, 180, 14, "FD")
        self.set_font("u", size=9)
        self.set_text_color(80, 80, 120)
        self.set_xy(18, 36)
        self.cell(70, 7, f"格式：{cap['format']}")
        self.cell(0, 7, f"建議頻率：{cap['priority']}")

        # Divider
        self.set_y(52)
        self.set_draw_color(200, 200, 220)
        self.line(15, 52, 195, 52)
        self.ln(4)

        # Caption body
        self.set_font("u", size=11)
        self.set_text_color(20, 20, 40)
        self.set_x(15)
        self.multi_cell(180, 7, cap["body"])

        # Bottom tip box
        self.ln(4)
        tip_y = self.get_y()
        if tip_y < 255:
            self.set_fill_color(bg_r, bg_g, bg_b)
            self.set_draw_color(bg_r, bg_g, bg_b)
            self.set_x(15)
            self.set_font("u", size=9)
            dark = (bg_r + bg_g + bg_b) < 300
            self.set_text_color(tx_r, tx_g, tx_b) if dark else self.set_text_color(30, 30, 50)
            hints = {
                1:  "開頭3秒 Hook：鏡頭拍頸部特寫 + 字幕出「8小時」即吸眼球",
                2:  "封面用大字「腰痛≠休息」配衝突感插圖，誘人 swipe",
                3:  "最強差異化貼，建議搭配頸前傾體態圖解動畫",
                4:  "用真實相片（得到客人同意），情感感染力遠高於設計圖",
                5:  "夜晚燈光昏暗場景拍攝，代入感最強",
                6:  "每個症狀一張 slide，配對應身體部位插圖",
                7:  "開頭直接問句，然後停頓1秒再講答案——演算法最愛完播率高嘅 Reel",
                8:  "高質感平面設計，玫瑰金配色，主打女性受眾",
                9:  "先喺 Story 出 Poll，收集真實數據，再出呢個 Post 分享結果",
                10: "加入真實限額（「本月只接10個評估」），唔係造假倒數",
            }
            hint = hints.get(cap["num"], "")
            self.set_fill_color(bg_r, bg_g, bg_b)
            self.multi_cell(180, 6, f"  拍攝/設計提示：{hint}", fill=True, new_x="LMARGIN")


def build():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_font("u", fname=FONT_PATH)
    pdf.set_margins(15, 15, 15)

    pdf.cover()

    for cap in CAPTIONS:
        pdf.caption_page(cap)

    # Summary page
    pdf.add_page()
    pdf.set_fill_color(15, 15, 30)
    pdf.rect(0, 0, 210, 297, "F")
    pdf.set_fill_color(180, 130, 255)
    pdf.rect(0, 0, 210, 4, "F")

    pdf.set_y(30)
    pdf.set_font("u", size=18)
    pdf.set_text_color(255, 255, 255)
    pdf.multi_cell(0, 10, "發布節奏總覽", align="C")
    pdf.ln(6)

    schedule = [
        ("星期一", "生活場景共鳴 / 痛症場景",  "Reel 15-30秒",  "#1  #5  #7"),
        ("星期三", "科普糾錯 Carousel",        "Carousel",      "#2  #6"),
        ("星期五", "客戶見證 / 美容×痛症",      "Reel 或 Static", "#3  #4  #8"),
        ("每月一次", "互動 Poll + CTA 收網",   "Story + Reel",  "#9  #10"),
    ]
    col_w = [35, 55, 42, 38]
    headers = ["日子", "主題", "格式", "對應文案"]
    header_cols = [(100, 180, 255), (255, 200, 100), (140, 220, 140), (220, 140, 255)]

    # Table header
    pdf.set_x(10)
    for h, w, col in zip(headers, col_w, header_cols):
        pdf.set_fill_color(*col)
        pdf.set_text_color(15, 15, 30)
        pdf.set_font("u", size=10)
        pdf.cell(w, 9, h, fill=True, align="C")
    pdf.ln()

    row_colors = [(28, 28, 55), (20, 20, 45)]
    for i, (day, topic, fmt, posts) in enumerate(schedule):
        pdf.set_x(10)
        pdf.set_fill_color(*row_colors[i % 2])
        row_data = [day, topic, fmt, posts]
        for val, w in zip(row_data, col_w):
            pdf.set_text_color(210, 210, 255)
            pdf.set_font("u", size=9)
            pdf.cell(w, 9, val, fill=True, align="C")
        pdf.ln()

    pdf.ln(12)
    pdf.set_font("u", size=11)
    pdf.set_text_color(180, 230, 255)
    pdf.multi_cell(0, 8, "每週最少 3 次  ·  Reel 優先  ·  開頭3秒係生死線", align="C")
    pdf.ln(8)

    # Three rules
    rules = [
        ("Rule 1", "開頭3秒用問句或反直覺講法",   "每個 Reel 第一格必須係 Hook，唔係 Logo"),
        ("Rule 2", "每個 Post 只有一個 CTA",       "唔好叫人又 Like 又 Share 又 DM，揀一個"),
        ("Rule 3", "真人 > AI 圖",                  "你出鏡或用真實客戶相，信任度高10倍"),
    ]
    for rule, title, desc in rules:
        pdf.set_fill_color(28, 28, 60)
        pdf.set_draw_color(100, 100, 200)
        pdf.set_x(20)
        pdf.set_font("u", size=9)
        pdf.set_text_color(140, 140, 220)
        pdf.cell(20, 7, rule, fill=True, align="C")
        pdf.set_fill_color(22, 22, 50)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("u", size=10)
        pdf.cell(75, 7, f"  {title}", fill=True)
        pdf.set_text_color(160, 160, 200)
        pdf.set_font("u", size=9)
        pdf.multi_cell(0, 7, f"  {desc}", fill=True, new_x="LMARGIN")
        pdf.ln(2)

    pdf.set_fill_color(180, 130, 255)
    pdf.rect(0, 293, 210, 4, "F")

    pdf.output(OUTPUT_PATH)
    print(f"PDF saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    build()