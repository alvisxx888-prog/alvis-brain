from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math

FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"
BASE = "/Users/rickyc./Desktop/Vs code /Project 2 (Stanley)/IG_Assets"

# ── Directories ──────────────────────────────────────────────
for d in ["profile","highlights","day01_intro","day03_reel","day08_case","day17_reel","day10_myth",
          "day12_office","day15_case2","day19_shockwave","day22_case3","day24_reel","day26_case4",
          "day29_case5","day30_reel","stories"]:
    os.makedirs(f"{BASE}/{d}", exist_ok=True)

# ── Colours ──────────────────────────────────────────────────
BLUE   = (27, 58, 107)
TEAL   = (42, 157, 143)
WHITE  = (255, 255, 255)
CREAM  = (245, 249, 255)
DARK   = (22, 28, 48)
GREY   = (110, 120, 145)
ORANGE = (220, 110, 40)
GREEN  = (40, 140, 80)
RED    = (180, 40, 40)

# ── Fonts ────────────────────────────────────────────────────
def F(sz): return ImageFont.truetype(FONT_PATH, sz)

# ── Helpers ──────────────────────────────────────────────────
def new_img(w, h, bg=WHITE):
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)

def gradient_bg(w, h, c1, c2, vertical=True):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    steps = h if vertical else w
    for i in range(steps):
        t = i / steps
        r = int(c1[0] + (c2[0]-c1[0])*t)
        g = int(c1[1] + (c2[1]-c1[1])*t)
        b = int(c1[2] + (c2[2]-c1[2])*t)
        if vertical:
            d.line([(0,i),(w,i)], fill=(r,g,b))
        else:
            d.line([(i,0),(i,h)], fill=(r,g,b))
    return img, ImageDraw.Draw(img)

def wrap_text(draw, text, x, y, font, color, max_w, line_gap=8):
    """Draw wrapped text, return final y"""
    paras = text.split("\n")
    for para in paras:
        if para.strip() == "":
            y += F(36).size + line_gap
            continue
        words = para.split()
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            bb = draw.textbbox((0,0), test, font=font)
            if bb[2]-bb[0] <= max_w:
                line = test
            else:
                if line:
                    draw.text((x,y), line, font=font, fill=color)
                    bb2 = draw.textbbox((0,0), line, font=font)
                    y += bb2[3]-bb2[1] + line_gap
                line = w
        if line:
            draw.text((x,y), line, font=font, fill=color)
            bb2 = draw.textbbox((0,0), line, font=font)
            y += bb2[3]-bb2[1] + line_gap
    return y

def footer_bar(img, draw, w, h, text="Stanley | 痛症方案顧問"):
    draw.rectangle([0, h-70, w, h], fill=BLUE)
    draw.text((w//2, h-50), text, font=F(28), fill=WHITE, anchor="mm")

def top_label(draw, w, text, bg=TEAL):
    draw.rectangle([0,0,w,80], fill=bg)
    draw.text((w//2, 40), text, font=F(32), fill=WHITE, anchor="mm")

def divider(draw, y, w, margin=60, color=TEAL):
    draw.line([(margin, y),(w-margin, y)], fill=color, width=3)

def rounded_rect(draw, box, radius, fill):
    x0,y0,x1,y1 = box
    draw.rectangle([x0+radius,y0,x1-radius,y1], fill=fill)
    draw.rectangle([x0,y0+radius,x1,y1-radius], fill=fill)
    draw.ellipse([x0,y0,x0+2*radius,y0+2*radius], fill=fill)
    draw.ellipse([x1-2*radius,y0,x1,y0+2*radius], fill=fill)
    draw.ellipse([x0,y1-2*radius,x0+2*radius,y1], fill=fill)
    draw.ellipse([x1-2*radius,y1-2*radius,x1,y1], fill=fill)

def bullet_item(draw, x, y, text, font, dot_color=TEAL, text_color=DARK, max_w=880):
    draw.ellipse([x, y+10, x+18, y+28], fill=dot_color)
    wrap_text(draw, text, x+32, y, font, text_color, max_w-32)
    bb = draw.textbbox((0,0), text[:30], font=font)
    return y + bb[3]-bb[1] + 16

# ═══════════════════════════════════════════════════════════
# PROFILE PICTURE  (1080x1080 → crop to circle for IG)
# ═══════════════════════════════════════════════════════════
def make_profile_pic():
    img, d = gradient_bg(1080, 1080, BLUE, (15, 35, 75))
    # Outer ring
    d.ellipse([60,60,1020,1020], outline=TEAL, width=18)
    # Big S
    d.text((540,440), "S", font=F(520), fill=WHITE, anchor="mm")
    # Subtitle
    d.text((540,780), "痛症方案顧問", font=F(68), fill=TEAL, anchor="mm")
    d.text((540,860), "Stanley", font=F(52), fill=(180,200,230), anchor="mm")
    img.save(f"{BASE}/profile/profile_picture.png")
    print("  profile_picture.png")

# ═══════════════════════════════════════════════════════════
# HIGHLIGHT COVERS  (1080x1080)
# ═══════════════════════════════════════════════════════════
highlights = [
    ("個案分享", "CASE", BLUE,     TEAL,   "📂"),
    ("痛症教育", "EDU",  TEAL,     BLUE,   "🔬"),
    ("療法科普", "RX",   (50,80,50),(42,157,100),"💊"),
    ("生活日常", "LIFE", (80,50,20),(180,110,40),"🌅"),
    ("免費評估", "FREE", (80,20,60),(160,50,120),"🆓"),
]

def make_highlight(title, code, bg1, bg2, icon_text):
    img, d = gradient_bg(1080, 1080, bg1, bg2, vertical=False)
    # Big circle bg
    d.ellipse([140,140,940,940], fill=(255,255,255,0), outline=WHITE, width=8)
    # Icon substitute (large letter)
    d.text((540,460), code, font=F(220), fill=WHITE, anchor="mm")
    d.text((540,700), title, font=F(88), fill=WHITE, anchor="mm")
    # Dots decoration
    for i in range(5):
        cx = 340 + i*100
        d.ellipse([cx-10,900,cx+10,920], fill=(255,255,255,100))
    img.save(f"{BASE}/highlights/{title}.png")
    print(f"  highlight_{title}.png")

# ═══════════════════════════════════════════════════════════
# DAY 1 — 帳號介紹 Carousel (4 slides, 1080x1080)
# ═══════════════════════════════════════════════════════════
def make_day01():
    # Slide 1 — Cover
    img, d = gradient_bg(1080, 1080, BLUE, (15,35,80))
    d.text((540,80), "STANLEY", font=F(52), fill=TEAL, anchor="mm")
    d.text((540,150), "痛症方案顧問", font=F(44), fill=(180,200,230), anchor="mm")
    divider(d, 200, 1080, color=TEAL)
    d.text((540,380), "我唔係醫生", font=F(110), fill=WHITE, anchor="mm")
    d.text((540,510), "但我知你嘅痛", font=F(110), fill=WHITE, anchor="mm")
    d.text((540,640), "點解搞唔掂", font=F(100), fill=TEAL, anchor="mm")
    divider(d, 740, 1080, color=(255,255,255,80))
    d.text((540,820), "向左掃了解更多  >>", font=F(44), fill=(200,220,255), anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day01_intro/slide_01_cover.png")

    # Slide 2 — 我係邊個
    img, d = new_img(1080, 1080, CREAM)
    d.rectangle([0,0,1080,90], fill=BLUE)
    d.text((540,45), "我係邊個？", font=F(44), fill=WHITE, anchor="mm")
    d.rectangle([60,110,75,700], fill=TEAL)
    d.text((120,150), "我係 Stanley", font=F(76), fill=BLUE, anchor="lm")
    y = 260
    items = [
        f"X 年痛症管理經驗",
        "見過幾百個真實個案",
        "了解多種療法同儀器技術",
        "唔係醫生，但見過最多人唔同嘅痛",
    ]
    for item in items:
        y = bullet_item(d, 100, y, item, F(46))
        y += 10
    divider(d, y+20, 1080)
    d.text((540, y+70), "我的工作：", font=F(48), fill=BLUE, anchor="mm")
    d.text((540, y+140), "幫你搵啱最適合你的方案", font=F(52), fill=DARK, anchor="mm")
    rounded_rect(d, [160, y+190, 920, y+270], 20, TEAL)
    d.text((540, y+230), "唔係幫你賣任何一樣嘢", font=F(46), fill=WHITE, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day01_intro/slide_02_who.png")

    # Slide 3 — 呢個 IG 你會睇到
    img, d = new_img(1080, 1080, WHITE)
    d.rectangle([0,0,1080,90], fill=TEAL)
    d.text((540,45), "呢個 IG 你會睇到", font=F(46), fill=WHITE, anchor="mm")
    boxes = [
        (60,  130, 490, 440, BLUE,  "CASE", "每週個案分享",    "真實個案，全部匿名"),
        (590, 130, 1020,440, TEAL,  "EDU",  "痛症謬誤破解",   "坊間好多嘢係錯嘅"),
        (60,  490, 490, 800, (50,80,50), "RX","療法比較解釋",  "點解有人做A有人做B"),
        (590, 490, 1020,800, (100,60,20),"FREE","免費方案諮詢","DM 我，免費傾吓"),
    ]
    for x0,y0,x1,y1,bg,code,title,sub in boxes:
        rounded_rect(d,[x0,y0,x1,y1],20,bg)
        d.text(((x0+x1)//2, y0+80), code, font=F(62), fill=WHITE, anchor="mm")
        d.text(((x0+x1)//2, y0+165), title, font=F(44), fill=WHITE, anchor="mm")
        d.text(((x0+x1)//2, y0+225), sub, font=F(32), fill=(220,235,255), anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day01_intro/slide_03_content.png")

    # Slide 4 — CTA
    img, d = gradient_bg(1080, 1080, BLUE, (30,60,120))
    d.text((540,150), "你而家", font=F(88), fill=WHITE, anchor="mm")
    d.text((540,270), "有痛症困擾？", font=F(88), fill=TEAL, anchor="mm")
    divider(d, 340, 1080, color=TEAL)
    questions = [
        "唔知應該睇邊科？",
        "試過好多方法但冇用？",
        "唔知做物理治療定中醫好？",
        "想知道自己適合咩方案？",
    ]
    y = 380
    for q in questions:
        d.text((540, y), q, font=F(46), fill=(200,220,255), anchor="mm")
        y += 70
    divider(d, y+20, 1080, color=TEAL)
    rounded_rect(d,[200,y+50,880,y+150],30,TEAL)
    d.text((540, y+100), "DM 我  |  Link in Bio", font=F(52), fill=WHITE, anchor="mm")
    d.text((540, y+200), "免費幫你分析最適合你嘅方向", font=F(40), fill=(180,210,240), anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day01_intro/slide_04_cta.png")
    print("  day01 carousel (4 slides)")

# ═══════════════════════════════════════════════════════════
# DAY 3 — 個人故事 Reel Cover (1080x1920)
# ═══════════════════════════════════════════════════════════
def make_day03_reel():
    img, d = gradient_bg(1080, 1920, BLUE, (10,25,60))
    # Top label
    d.rectangle([0,0,1080,100], fill=(255,255,255,30))
    d.text((540,50), "我的故事", font=F(44), fill=TEAL, anchor="mm")
    # Main text
    d.text((540,480), "點解我", font=F(140), fill=WHITE, anchor="mm")
    d.text((540,650), "會做痛症？", font=F(120), fill=WHITE, anchor="mm")
    divider(d, 780, 1080, color=TEAL)
    d.text((540,860), "唔係因為錢", font=F(80), fill=TEAL, anchor="mm")
    # Sub lines
    lines = ["7年，幾百個案", "我見過嘅，令我唔可以唔講"]
    y = 1000
    for l in lines:
        d.text((540,y), l, font=F(52), fill=(180,205,240), anchor="mm")
        y += 80
    # CTA
    rounded_rect(d,[200,1200,880,1310],30,(255,255,255,40))
    d.text((540,1255), "Follow 住 + DM 我", font=F(52), fill=WHITE, anchor="mm")
    # Footer
    d.rectangle([0,1820,1080,1920], fill=BLUE)
    d.text((540,1870), "Stanley | 痛症方案顧問", font=F(36), fill=WHITE, anchor="mm")
    img.save(f"{BASE}/day03_reel/reel_cover.png")
    print("  day03 reel cover")

# ═══════════════════════════════════════════════════════════
# DAY 8 — 個案分享 #1 Carousel (6 slides, 1080x1080)
# ═══════════════════════════════════════════════════════════
def make_day08():
    # Slide 1 — Cover
    img, d = gradient_bg(1080, 1080, BLUE, (20,45,100))
    d.rectangle([0,0,1080,80], fill=TEAL)
    d.text((540,40), "個案分享  第 1 回", font=F(38), fill=WHITE, anchor="mm")
    d.text((540,320), "頸痛 2 年", font=F(108), fill=WHITE, anchor="mm")
    d.text((540,450), "做過物理治療", font=F(84), fill=(200,220,255), anchor="mm")
    d.text((540,560), "都冇用？", font=F(108), fill=TEAL, anchor="mm")
    divider(d, 660, 1080, color=TEAL)
    d.text((540,730), "向左掃看完整個案  >>", font=F(44), fill=(180,210,240), anchor="mm")
    # Series tag
    rounded_rect(d,[300,810,780,870],20,(255,255,255,30))
    d.text((540,840), "#Stanley痛症個案", font=F(34), fill=WHITE, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day08_case/slide_01_cover.png")

    # Slide 2 — 客人背景
    img, d = new_img(1080, 1080, CREAM)
    top_label(d, 1080, "客人背景", bg=BLUE)
    d.text((540, 200), "CASE #01", font=F(52), fill=TEAL, anchor="mm")
    d.line([(300,250),(780,250)], fill=TEAL, width=3)
    info = [("年齡",  "30歲出頭"), ("職業", "銀行文職"),
            ("工作", "每日對住電腦 8 小時"), ("狀態","已有頸痛問題超過 2 年")]
    y = 300
    for label, val in info:
        rounded_rect(d,[80,y,440,y+80],12,BLUE)
        d.text((260,y+40), label, font=F(40), fill=WHITE, anchor="mm")
        d.text((560,y+40), val, font=F(42), fill=DARK, anchor="lm")
        y += 110
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day08_case/slide_02_background.png")

    # Slide 3 — 困擾問題
    img, d = new_img(1080, 1080, WHITE)
    top_label(d, 1080, "困擾問題", bg=TEAL)
    d.text((540,180), "頸椎痛 + 頭痛", font=F(72), fill=BLUE, anchor="mm")
    divider(d, 250, 1080)
    symptoms = ["頸梗到轉唔到頭，尤其係收工後",
                "嚴重時連帶頭痛，有時蔓延至眼眉",
                "嚴重影響睡眠質素",
                "試過買枕頭、頸椎墊都冇效"]
    y = 310
    for s in symptoms:
        y = bullet_item(d, 80, y, s, F(44), dot_color=TEAL)
        y += 8
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day08_case/slide_03_problem.png")

    # Slide 4 — 試過嘅方法
    img, d = new_img(1080, 1080, WHITE)
    top_label(d, 1080, "試過但冇用", bg=ORANGE)
    d.text((540,180), "3種方法都失敗", font=F(64), fill=BLUE, anchor="mm")
    divider(d, 240, 1080, color=ORANGE)
    fails = [("物理治療 6 次",   "做完即時舒服，但 2 日後痛返"),
             ("頸部按摩器",       "用咗 1 個月，冇明顯改善"),
             ("長期食止痛藥",     "停藥就痛返，治標唔治本")]
    y = 300
    for method, result in fails:
        rounded_rect(d,[80,y,1000,y+130],15,CREAM)
        d.rectangle([80,y,110,y+130], fill=RED)
        d.text((120,y+30), method, font=F(46), fill=BLUE)
        d.text((120,y+88), result, font=F(38), fill=GREY)
        y += 155
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day08_case/slide_04_failed.png")

    # Slide 5 — 最終方案 + 效果
    img, d = new_img(1080, 1080, CREAM)
    top_label(d, 1080, "最終方案 + 效果", bg=GREEN)
    d.text((540,160), "衝擊波 + 姿勢矯正訓練", font=F(54), fill=BLUE, anchor="mm")
    rounded_rect(d,[80,210,1000,300],15,(235,248,235))
    d.text((540,255), "根源：頸椎輕微錯位 + 長期姿勢問題積累", font=F(38), fill=(30,80,30), anchor="mm")
    divider(d, 320, 1080, color=GREEN)
    d.text((540,380), "4 次療程後", font=F(52), fill=GREEN, anchor="mm")
    results = ["頭痛基本消失，唔再依賴止痛藥",
               "頸部活動度明顯改善，可以正常轉頭",
               "停止療程後冇再反覆（關鍵）"]
    y = 450
    for r in results:
        y = bullet_item(d, 80, y, r, F(44), dot_color=GREEN, text_color=DARK)
        y += 8
    # Difficulty
    d.text((540, y+40), "難度指數：", font=F(40), fill=GREY, anchor="mm")
    stars = "★★★☆☆"
    d.text((540, y+95), stars, font=F(68), fill=ORANGE, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day08_case/slide_05_result.png")

    # Slide 6 — CTA
    img, d = gradient_bg(1080, 1080, BLUE, (25,50,110))
    d.text((540,160), "唔知自己係咪", font=F(80), fill=WHITE, anchor="mm")
    d.text((540,270), "同樣情況？", font=F(80), fill=TEAL, anchor="mm")
    divider(d, 360, 1080, color=TEAL)
    d.text((540,460), "點解做完物理治療痛返？", font=F(50), fill=(200,220,255), anchor="mm")
    d.text((540,540), "因為治標唔治本，", font=F(46), fill=(180,210,245), anchor="mm")
    d.text((540,610), "根源問題未解決，痛係一定會返嘅。", font=F(40), fill=(160,195,235), anchor="mm")
    rounded_rect(d,[160,700,920,800],30,TEAL)
    d.text((540,750), "DM 我，免費幫你分析方向", font=F(50), fill=WHITE, anchor="mm")
    d.text((540,860), "Link in Bio 預約免費諮詢", font=F(42), fill=(180,215,245), anchor="mm")
    d.text((540, 940), "#Stanley痛症個案  #頸椎痛  #痛症管理", font=F(32), fill=GREY, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day08_case/slide_06_cta.png")
    print("  day08 carousel (6 slides)")

# ═══════════════════════════════════════════════════════════
# DAY 10 — 迷思破解 Reel Cover (1080x1920)
# ═══════════════════════════════════════════════════════════
def make_day10_reel():
    img, d = gradient_bg(1080, 1920, (15,30,70), BLUE, vertical=False)
    d.rectangle([0,0,1080,100], fill=TEAL)
    d.text((540,50), "痛症謬誤破解  #001", font=F(40), fill=WHITE, anchor="mm")
    # Split design — cold vs hot
    d.rectangle([0,200,540,900], fill=(20,50,120))
    d.rectangle([540,200,1080,900], fill=(150,50,20))
    d.text((270,350), "凍", font=F(220), fill=(180,220,255), anchor="mm")
    d.text((810,350), "熱", font=F(220), fill=(255,180,120), anchor="mm")
    d.text((270,600), "COLD", font=F(60), fill=(140,200,255), anchor="mm")
    d.text((810,600), "HOT", font=F(60), fill=(255,160,80), anchor="mm")
    d.text((270,700), "凍敷", font=F(52), fill=WHITE, anchor="mm")
    d.text((810,700), "熱敷", font=F(52), fill=WHITE, anchor="mm")
    # VS in middle
    rounded_rect(d,[460,490,620,640],30,WHITE)
    d.text((540,565), "VS", font=F(72), fill=BLUE, anchor="mm")
    # Main question
    divider(d, 950, 1080, color=TEAL)
    d.text((540,1060), "熱敷定凍敷？", font=F(96), fill=WHITE, anchor="mm")
    d.text((540,1180), "9成人整錯！", font=F(80), fill=ORANGE, anchor="mm")
    divider(d, 1280, 1080, color=TEAL)
    d.text((540,1380), "你係咪其中之一？", font=F(56), fill=(200,220,255), anchor="mm")
    rounded_rect(d,[200,1480,880,1570],30,(255,255,255,40))
    d.text((540,1525), "Comment「評估」換自我判斷指引", font=F(40), fill=WHITE, anchor="mm")
    d.rectangle([0,1820,1080,1920], fill=BLUE)
    d.text((540,1870), "Stanley | 痛症方案顧問", font=F(36), fill=WHITE, anchor="mm")
    img.save(f"{BASE}/day10_myth/reel_cover.png")
    print("  day10 myth reel cover")

# ═══════════════════════════════════════════════════════════
# DAY 17 — 留言換資料 Reel Cover (1080x1920)
# ═══════════════════════════════════════════════════════════
def make_day17_reel():
    img, d = gradient_bg(1080, 1920, (10,20,55), (35,65,130))
    d.rectangle([0,0,1080,100], fill=(255,255,255,20))
    d.text((540,50), "止痛藥依賴？", font=F(44), fill=TEAL, anchor="mm")
    divider(d, 110, 1080, color=TEAL)
    # Main message
    d.text((540,350), "食完又痛返", font=F(120), fill=WHITE, anchor="mm")
    d.text((540,500), "係因為你", font=F(100), fill=(200,220,255), anchor="mm")
    d.text((540,640), "搵錯方向了", font=F(110), fill=TEAL, anchor="mm")
    # Pill icon (simple rectangle)
    d.ellipse([420,740,660,840], fill=ORANGE)
    d.text((540,790), "PAIN", font=F(44), fill=WHITE, anchor="mm")
    divider(d, 900, 1080, color=TEAL)
    # 3 reasons
    reasons = ["1.  肌肉失衡", "2.  關節錯位", "3.  筋膜沾黏"]
    y = 960
    for r in reasons:
        d.text((540,y), r, font=F(62), fill=WHITE, anchor="mm")
        y += 90
    divider(d, y+20, 1080, color=(255,255,255,60))
    # CTA box
    rounded_rect(d,[100,y+60,980,y+200],30,TEAL)
    d.text((540,y+100), "Comment 打「止痛」", font=F(54), fill=WHITE, anchor="mm")
    d.text((540,y+165), "即刻 PM 你份免費指南", font=F(44), fill=(220,245,240), anchor="mm")
    d.rectangle([0,1820,1080,1920], fill=BLUE)
    d.text((540,1870), "Stanley | 痛症方案顧問", font=F(36), fill=WHITE, anchor="mm")
    img.save(f"{BASE}/day17_reel/reel_cover.png")
    print("  day17 reel cover")

# ═══════════════════════════════════════════════════════════
# DAY 12 — 辦公室急救貼士 Carousel (5 slides, 1080x1080)
# ═══════════════════════════════════════════════════════════
def make_day12():
    # Slide 1 — Cover
    img, d = gradient_bg(1080, 1080, BLUE, (20,45,100))
    d.rectangle([0,0,1080,80], fill=TEAL)
    d.text((540,40), "辦公室痛症急救", font=F(38), fill=WHITE, anchor="mm")
    d.text((540,280), "OT 頸痛", font=F(120), fill=WHITE, anchor="mm")
    d.text((540,420), "即時急救", font=F(100), fill=TEAL, anchor="mm")
    d.text((540,540), "3 個動作", font=F(120), fill=WHITE, anchor="mm")
    divider(d, 660, 1080, color=TEAL)
    d.text((540,730), "做完即時舒緩  >>", font=F(44), fill=(180,210,240), anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day12_office/slide_01_cover.png")

    # Slides 2-4 — 每個動作
    moves = [
        ("動作 1", "頸部側伸展",
         ["頭側向右邊", "右手輕輕放頭頂", "加少少向下壓力", "感受左邊頸側拉緊", "保持 15 秒，換邊做"]),
        ("動作 2", "肩膀後收",
         ["雙手垂低放身旁", "肩膀同時向後收", "盡量夾埋兩邊肩胛骨", "保持 10 秒", "重複 5 次"]),
        ("動作 3", "Chin Tuck 頸後縮",
         ["下巴輕輕向後縮", "唔係低頭，係向後", "好似有人頂住你前額", "保持 5 秒", "重複 10 次"]),
    ]
    for i, (label, title, steps) in enumerate(moves, 2):
        img, d = new_img(1080, 1080, WHITE)
        top_label(d, 1080, label, bg=TEAL)
        d.text((540,170), title, font=F(72), fill=BLUE, anchor="mm")
        divider(d, 230, 1080)
        y = 280
        for s in steps:
            y = bullet_item(d, 80, y, s, F(46))
            y += 12
        rounded_rect(d,[80,y+20,1000,y+90],15,(235,248,235))
        d.text((540,y+55), "每日做，5 分鐘，收工即刻做", font=F(36), fill=(30,80,30), anchor="mm")
        footer_bar(img, d, 1080, 1080)
        img.save(f"{BASE}/day12_office/slide_0{i}_move{i-1}.png")

    # Slide 5 — CTA
    img, d = gradient_bg(1080, 1080, BLUE, (25,50,110))
    d.text((540,200), "做完仲係痛？", font=F(88), fill=WHITE, anchor="mm")
    divider(d, 310, 1080, color=TEAL)
    d.text((540,420), "可能唔係「累」——", font=F(60), fill=(200,220,255), anchor="mm")
    d.text((540,510), "係需要評估的信號", font=F(60), fill=TEAL, anchor="mm")
    rounded_rect(d,[160,640,920,740],30,TEAL)
    d.text((540,690), "DM 我，免費傾吓", font=F(52), fill=WHITE, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day12_office/slide_05_cta.png")
    print("  day12 carousel (5 slides)")


# ═══════════════════════════════════════════════════════════
# DAY 15 — 個案分享 #2 膝蓋退化 Carousel (6 slides, 1080x1080)
# ═══════════════════════════════════════════════════════════
def make_day15():
    # Slide 1 — Cover
    img, d = gradient_bg(1080, 1080, (10,40,10), (20,80,30))
    d.rectangle([0,0,1080,80], fill=TEAL)
    d.text((540,40), "個案分享  第 2 回", font=F(38), fill=WHITE, anchor="mm")
    d.text((540,280), "膝蓋痛到", font=F(100), fill=WHITE, anchor="mm")
    d.text((540,400), "以為要換骨", font=F(90), fill=(200,255,200), anchor="mm")
    d.text((540,520), "最後唔使手術", font=F(80), fill=TEAL, anchor="mm")
    divider(d, 630, 1080, color=TEAL)
    d.text((540,710), "向左掃看完整個案  >>", font=F(44), fill=(180,240,200), anchor="mm")
    rounded_rect(d,[300,790,780,850],20,(255,255,255,30))
    d.text((540,820), "#Stanley痛症個案", font=F(34), fill=WHITE, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day15_case2/slide_01_cover.png")

    # Slide 2 — 客人背景
    img, d = new_img(1080, 1080, CREAM)
    top_label(d, 1080, "客人背景", bg=BLUE)
    d.text((540,200), "CASE #02", font=F(52), fill=TEAL, anchor="mm")
    d.line([(300,250),(780,250)], fill=TEAL, width=3)
    info = [("年齡","50歲"), ("身份","家庭主婦"),
            ("困擾","落樓梯必定痛，行多路腫脹"), ("狀態","骨科建議考慮換骨")]
    y = 300
    for label, val in info:
        rounded_rect(d,[80,y,440,y+80],12,BLUE)
        d.text((260,y+40), label, font=F(40), fill=WHITE, anchor="mm")
        d.text((560,y+40), val, font=F(42), fill=DARK, anchor="lm")
        y += 110
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day15_case2/slide_02_background.png")

    # Slide 3 — 困擾問題
    img, d = new_img(1080, 1080, WHITE)
    top_label(d, 1080, "困擾問題", bg=TEAL)
    d.text((540,180), "膝關節退化", font=F(72), fill=BLUE, anchor="mm")
    divider(d, 250, 1080)
    symptoms = ["落樓梯必定有痛感，無法避免",
                "行路多啲就腫脹，要休息先消退",
                "關節有聲音（卡卡聲）",
                "骨科醫生建議考慮換人工關節"]
    y = 310
    for s in symptoms:
        y = bullet_item(d, 80, y, s, F(44), dot_color=TEAL)
        y += 8
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day15_case2/slide_03_problem.png")

    # Slide 4 — 試過嘅方法
    img, d = new_img(1080, 1080, WHITE)
    top_label(d, 1080, "試過但冇用", bg=ORANGE)
    d.text((540,180), "3種方法都治標不治本", font=F(60), fill=BLUE, anchor="mm")
    divider(d, 240, 1080, color=ORANGE)
    fails = [("玻尿酸針",   "費用高，效果3-6個月，需定期打"),
             ("消炎藥",     "胃部副作用，長期服用有風險"),
             ("護膝",       "減少不適，但無法根治退化問題")]
    y = 300
    for method, result in fails:
        rounded_rect(d,[80,y,1000,y+130],15,CREAM)
        d.rectangle([80,y,110,y+130], fill=RED)
        d.text((120,y+30), method, font=F(46), fill=BLUE)
        d.text((120,y+88), result, font=F(38), fill=GREY)
        y += 155
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day15_case2/slide_04_failed.png")

    # Slide 5 — 最終方案 + 效果
    img, d = new_img(1080, 1080, CREAM)
    top_label(d, 1080, "最終方案 + 效果", bg=GREEN)
    d.text((540,160), "衝擊波 + 股四頭肌訓練", font=F(58), fill=BLUE, anchor="mm")
    rounded_rect(d,[80,210,1000,300],15,(235,248,235))
    d.text((540,255), "根源：周邊肌肉太弱，令膝關節承受不必要壓力", font=F(34), fill=(30,80,30), anchor="mm")
    divider(d, 320, 1080, color=GREEN)
    d.text((540,380), "3 個月後", font=F(52), fill=GREEN, anchor="mm")
    results = ["落樓梯痛感由 8 分降至 2 分",
               "腫脹情況明顯減退",
               "暫時唔需要手術（最重要）",
               "學識如何保護膝蓋，防止惡化"]
    y = 450
    for r in results:
        y = bullet_item(d, 80, y, r, F(44), dot_color=GREEN, text_color=DARK)
        y += 8
    d.text((540, y+40), "難度指數：", font=F(40), fill=GREY, anchor="mm")
    d.text((540, y+95), "★★★★☆", font=F(68), fill=ORANGE, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day15_case2/slide_05_result.png")

    # Slide 6 — CTA
    img, d = gradient_bg(1080, 1080, (10,40,10), (25,70,35))
    d.text((540,160), "退化係無法逆轉的", font=F(72), fill=WHITE, anchor="mm")
    d.text((540,260), "但「痛」係可以控制的", font=F(66), fill=TEAL, anchor="mm")
    divider(d, 350, 1080, color=TEAL)
    d.text((540,450), "唔一定要等到手術", font=F(56), fill=(200,255,210), anchor="mm")
    d.text((540,540), "先係唯一出路", font=F(56), fill=(200,255,210), anchor="mm")
    rounded_rect(d,[160,660,920,760],30,TEAL)
    d.text((540,710), "DM 我，免費幫你分析方向", font=F(48), fill=WHITE, anchor="mm")
    d.text((540, 840), "#Stanley痛症個案  #膝關節退化  #痛症管理", font=F(30), fill=GREY, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day15_case2/slide_06_cta.png")
    print("  day15 carousel (6 slides)")


# ═══════════════════════════════════════════════════════════
# DAY 19 — 療法科普：衝擊波 Carousel (5 slides, 1080x1080)
# ═══════════════════════════════════════════════════════════
def make_day19():
    # Slide 1 — Cover
    img, d = gradient_bg(1080, 1080, BLUE, (15,35,80))
    d.rectangle([0,0,1080,80], fill=TEAL)
    d.text((540,40), "療法科普", font=F(40), fill=WHITE, anchor="mm")
    d.text((540,270), "衝擊波治療", font=F(100), fill=WHITE, anchor="mm")
    d.text((540,390), "係咩？", font=F(120), fill=TEAL, anchor="mm")
    divider(d, 510, 1080, color=TEAL)
    d.text((540,610), "用 3 分鐘解釋清楚", font=F(56), fill=(180,210,240), anchor="mm")
    d.text((540,710), "包括哪些人不適合做", font=F(46), fill=(150,185,225), anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day19_shockwave/slide_01_cover.png")

    # Slide 2 — 原理
    img, d = new_img(1080, 1080, CREAM)
    top_label(d, 1080, "衝擊波原理", bg=BLUE)
    d.text((540,170), "聲波能量治療", font=F(64), fill=BLUE, anchor="mm")
    divider(d, 230, 1080)
    principles = ["透過儀器將聲波能量傳入身體深層組織",
                  "刺激細胞再生，加速自我修復",
                  "促進血液循環，改善局部代謝",
                  "打散鈣化沉積，軟化硬化組織",
                  "啟動身體自然康復機制"]
    y = 280
    for p in principles:
        y = bullet_item(d, 80, y, p, F(44), dot_color=BLUE)
        y += 10
    rounded_rect(d,[80,y+20,1000,y+90],15,(235,240,255))
    d.text((540,y+55), "唔係電療，唔係打針，係聲波震動", font=F(38), fill=BLUE, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day19_shockwave/slide_02_principle.png")

    # Slide 3 — 適合情況
    img, d = new_img(1080, 1080, WHITE)
    top_label(d, 1080, "適合情況", bg=GREEN)
    d.text((540,180), "以下情況可考慮衝擊波", font=F(58), fill=BLUE, anchor="mm")
    divider(d, 240, 1080, color=GREEN)
    suitable = [("慢性肌腱炎", "網球肘、足底筋膜炎、旋轉肌腱炎"),
                ("肌腱撕裂", "旋轉肌、跟腱等部位"),
                ("鈣化性肌腱炎", "鈣質沉積引起的疼痛"),
                ("運動創傷康復", "訓練後遺症、反覆舊患")]
    y = 290
    for title, desc in suitable:
        rounded_rect(d,[80,y,1000,y+120],15,(235,252,235))
        d.rectangle([80,y,110,y+120], fill=GREEN)
        d.text((130,y+28), title, font=F(46), fill=(20,90,20))
        d.text((130,y+82), desc, font=F(36), fill=GREY)
        y += 140
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day19_shockwave/slide_03_suitable.png")

    # Slide 4 — 唔適合情況
    img, d = new_img(1080, 1080, WHITE)
    top_label(d, 1080, "唔適合情況", bg=RED)
    d.text((540,180), "以下人士不建議做", font=F(62), fill=BLUE, anchor="mm")
    divider(d, 240, 1080, color=RED)
    not_suitable = [("急性炎症期", "受傷頭 48 小時，炎症未穩定"),
                    ("骨折未癒合", "骨骼結構未完全復原"),
                    ("懷孕期間",   "安全起見，所有儀器治療暫緩"),
                    ("凝血問題人士", "出血風險較高")]
    y = 290
    for title, desc in not_suitable:
        rounded_rect(d,[80,y,1000,y+120],15,(255,240,240))
        d.rectangle([80,y,110,y+120], fill=RED)
        d.text((130,y+28), title, font=F(46), fill=(120,20,20))
        d.text((130,y+82), desc, font=F(36), fill=GREY)
        y += 140
    rounded_rect(d,[80,y+10,1000,y+70],15,(255,248,220))
    d.text((540,y+40), "唔係人人都適合，要先評估先", font=F(38), fill=(140,80,0), anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day19_shockwave/slide_04_unsuitable.png")

    # Slide 5 — CTA
    img, d = gradient_bg(1080, 1080, BLUE, (25,50,110))
    d.text((540,200), "想知自己係咪", font=F(80), fill=WHITE, anchor="mm")
    d.text((540,300), "適合衝擊波？", font=F(80), fill=TEAL, anchor="mm")
    divider(d, 390, 1080, color=TEAL)
    d.text((540,490), "唔係貴嘅就係最好", font=F(52), fill=(200,220,255), anchor="mm")
    d.text((540,570), "係要先判斷你係咪適合", font=F(48), fill=(180,210,245), anchor="mm")
    rounded_rect(d,[160,680,920,780],30,TEAL)
    d.text((540,730), "DM 我，免費幫你評估", font=F(52), fill=WHITE, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day19_shockwave/slide_05_cta.png")
    print("  day19 carousel (5 slides)")


# ═══════════════════════════════════════════════════════════
# DAY 22 — 個案分享 #3 健身男肩痛 Carousel (6 slides, 1080x1080)
# ═══════════════════════════════════════════════════════════
def make_day22():
    # Slide 1 — Cover
    img, d = gradient_bg(1080, 1080, (40,10,10), (90,20,20))
    d.rectangle([0,0,1080,80], fill=ORANGE)
    d.text((540,40), "個案分享  第 3 回", font=F(38), fill=WHITE, anchor="mm")
    d.text((540,260), "健身男", font=F(120), fill=WHITE, anchor="mm")
    d.text((540,390), "忍痛練落去", font=F(90), fill=(255,200,150), anchor="mm")
    d.text((540,500), "係最錯嘅決定", font=F(80), fill=ORANGE, anchor="mm")
    divider(d, 610, 1080, color=ORANGE)
    d.text((540,700), "向左掃看完整個案  >>", font=F(44), fill=(255,200,160), anchor="mm")
    rounded_rect(d,[300,780,780,840],20,(255,255,255,30))
    d.text((540,810), "#Stanley痛症個案", font=F(34), fill=WHITE, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day22_case3/slide_01_cover.png")

    # Slide 2 — 客人背景
    img, d = new_img(1080, 1080, CREAM)
    top_label(d, 1080, "客人背景", bg=BLUE)
    d.text((540,200), "CASE #03", font=F(52), fill=TEAL, anchor="mm")
    d.line([(300,250),(780,250)], fill=TEAL, width=3)
    info = [("年齡","28歲"), ("身份","自僱人士"),
            ("習慣","健身 3 年，每週 4-5 次"), ("困擾","右肩刺痛，停健身 2 個月仍反覆")]
    y = 300
    for label, val in info:
        rounded_rect(d,[80,y,440,y+80],12,BLUE)
        d.text((260,y+40), label, font=F(40), fill=WHITE, anchor="mm")
        d.text((560,y+40), val, font=F(38), fill=DARK, anchor="lm")
        y += 110
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day22_case3/slide_02_background.png")

    # Slide 3 — 困擾問題
    img, d = new_img(1080, 1080, WHITE)
    top_label(d, 1080, "困擾問題", bg=TEAL)
    d.text((540,180), "右肩痛 + 活動受限", font=F(68), fill=BLUE, anchor="mm")
    divider(d, 250, 1080)
    symptoms = ["做 Bench Press 時右肩刺痛",
                "右手舉高就有痛感，無法正常訓練",
                "停健身 2 個月，但痛感仍反覆出現",
                "擔心係嚴重受傷，影響長期訓練"]
    y = 310
    for s in symptoms:
        y = bullet_item(d, 80, y, s, F(44), dot_color=TEAL)
        y += 8
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day22_case3/slide_03_problem.png")

    # Slide 4 — 試過嘅方法
    img, d = new_img(1080, 1080, WHITE)
    top_label(d, 1080, "試過但冇用", bg=ORANGE)
    d.text((540,180), "以為「休息夠就好」", font=F(64), fill=BLUE, anchor="mm")
    divider(d, 240, 1080, color=ORANGE)
    fails = [("痛症貼布",  "舒緩效果短暫，訓練完仲係痛"),
             ("跌打",      "做完好，但練番又痛——反覆"),
             ("純粹休息",  "停練 2 個月，痛仍反覆發作")]
    y = 300
    for method, result in fails:
        rounded_rect(d,[80,y,1000,y+130],15,CREAM)
        d.rectangle([80,y,110,y+130], fill=RED)
        d.text((120,y+30), method, font=F(46), fill=BLUE)
        d.text((120,y+88), result, font=F(38), fill=GREY)
        y += 155
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day22_case3/slide_04_failed.png")

    # Slide 5 — 最終方案 + 效果
    img, d = new_img(1080, 1080, CREAM)
    top_label(d, 1080, "最終方案 + 效果", bg=GREEN)
    d.text((540,160), "衝擊波 + 旋轉肌專項訓練", font=F(54), fill=BLUE, anchor="mm")
    rounded_rect(d,[80,210,1000,300],15,(235,248,235))
    d.text((540,255), "根源：肌腱輕微撕裂 + 健身動作有代償", font=F(36), fill=(30,80,30), anchor="mm")
    divider(d, 320, 1080, color=GREEN)
    d.text((540,380), "6 次療程後", font=F(52), fill=GREEN, anchor="mm")
    results = ["恢復訓練時無刺痛感",
               "Bench Press 重量仲升咗（意外收穫）",
               "學識正確肩部動作，防止復發",
               "明白「痛咗唔代表要停練」的界線"]
    y = 450
    for r in results:
        y = bullet_item(d, 80, y, r, F(44), dot_color=GREEN, text_color=DARK)
        y += 8
    d.text((540, y+40), "難度指數：", font=F(40), fill=GREY, anchor="mm")
    d.text((540, y+95), "★★★★☆", font=F(68), fill=ORANGE, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day22_case3/slide_05_result.png")

    # Slide 6 — CTA
    img, d = gradient_bg(1080, 1080, (40,10,10), (80,20,20))
    d.text((540,160), "痛咗唔代表", font=F(80), fill=WHITE, anchor="mm")
    d.text((540,260), "要永遠停練", font=F(80), fill=ORANGE, anchor="mm")
    divider(d, 360, 1080, color=ORANGE)
    d.text((540,460), "但「忍住練」係最快搞壞嘅方法", font=F(50), fill=(255,200,160), anchor="mm")
    rounded_rect(d,[160,600,920,700],30,TEAL)
    d.text((540,650), "DM 我，幫你判斷可唔可以繼續練", font=F(44), fill=WHITE, anchor="mm")
    d.text((540,810), "#Stanley痛症個案  #肩痛  #健身受傷", font=F(30), fill=GREY, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day22_case3/slide_06_cta.png")
    print("  day22 carousel (6 slides)")


# ═══════════════════════════════════════════════════════════
# DAY 24 — 比較 Reel Cover：3種療法 (1080x1920)
# ═══════════════════════════════════════════════════════════
def make_day24_reel():
    img, d = gradient_bg(1080, 1920, BLUE, (20,45,100))
    d.rectangle([0,0,1080,100], fill=TEAL)
    d.text((540,50), "療法比較", font=F(44), fill=WHITE, anchor="mm")
    divider(d, 110, 1080, color=TEAL)
    d.text((540,280), "中醫", font=F(130), fill=WHITE, anchor="mm")
    d.text((540,430), "vs", font=F(80), fill=TEAL, anchor="mm")
    d.text((540,570), "物理治療", font=F(110), fill=WHITE, anchor="mm")
    d.text((540,690), "vs", font=F(80), fill=TEAL, anchor="mm")
    d.text((540,830), "儀器治療", font=F(110), fill=(180,210,255), anchor="mm")
    divider(d, 940, 1080, color=TEAL)
    d.text((540,1040), "邊個最啱你？", font=F(90), fill=TEAL, anchor="mm")
    d.text((540,1160), "唔係邊個最好——", font=F(60), fill=(200,220,255), anchor="mm")
    d.text((540,1250), "係邊個最適合你嘅情況", font=F(54), fill=(180,205,240), anchor="mm")
    divider(d, 1350, 1080, color=(255,255,255,60))
    d.text((540,1450), "睇完你就知", font=F(64), fill=WHITE, anchor="mm")
    rounded_rect(d,[200,1530,880,1630],30,(255,255,255,30))
    d.text((540,1580), "DM 我，免費幫你判斷", font=F(44), fill=WHITE, anchor="mm")
    d.rectangle([0,1820,1080,1920], fill=BLUE)
    d.text((540,1870), "Stanley | 痛症方案顧問", font=F(36), fill=WHITE, anchor="mm")
    img.save(f"{BASE}/day24_reel/reel_cover.png")
    print("  day24 reel cover")


# ═══════════════════════════════════════════════════════════
# DAY 26 — 個案分享 #4 Template (6 slides, 1080x1080)
# ═══════════════════════════════════════════════════════════
def make_day26():
    # Slide 1 — Cover (template)
    img, d = gradient_bg(1080, 1080, (10,10,50), (30,30,100))
    d.rectangle([0,0,1080,80], fill=BLUE)
    d.text((540,40), "個案分享  第 4 回", font=F(38), fill=WHITE, anchor="mm")
    d.text((540,280), "[症狀]", font=F(100), fill=WHITE, anchor="mm")
    d.text((540,400), "[轉折句]", font=F(80), fill=TEAL, anchor="mm")
    d.text((540,510), "[結果]", font=F(90), fill=(180,210,255), anchor="mm")
    divider(d, 620, 1080, color=TEAL)
    d.text((540,710), "向左掃看完整個案  >>", font=F(44), fill=(180,210,240), anchor="mm")
    rounded_rect(d,[300,790,780,850],20,(255,255,255,30))
    d.text((540,820), "#Stanley痛症個案", font=F(34), fill=WHITE, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day26_case4/slide_01_cover_template.png")

    # Slides 2-6 — 同 Day 08 格式，用文字提示填寫
    labels = [
        ("客人背景", BLUE,   "年齡 / 職業 / 生活習慣 / 困擾時間"),
        ("困擾問題", TEAL,   "主要症狀描述 + 影響日常程度"),
        ("試過方法", ORANGE, "之前試過嘅治療 + 點解冇效"),
        ("最終方案", GREEN,  "方案名稱 + 根源分析 + 效果數據"),
        ("CTA",      BLUE,   "有類似情況？DM 我免費分析"),
    ]
    for i, (title, color, hint) in enumerate(labels, 2):
        img, d = new_img(1080, 1080, CREAM)
        top_label(d, 1080, title, bg=color)
        d.text((540,300), f"[ {title} ]", font=F(80), fill=color, anchor="mm")
        divider(d, 420, 1080, color=color)
        wrap_text(d, hint, 80, 460, F(44), GREY, 920)
        rounded_rect(d,[80,700,1000,780],15,(235,240,255))
        d.text((540,740), "根據你真實個案填入內容", font=F(36), fill=BLUE, anchor="mm")
        footer_bar(img, d, 1080, 1080)
        img.save(f"{BASE}/day26_case4/slide_0{i}_template.png")
    print("  day26 case4 template (6 slides)")


# ═══════════════════════════════════════════════════════════
# DAY 29 — 個案分享 #5 Template (6 slides, 1080x1080)
# ═══════════════════════════════════════════════════════════
def make_day29():
    img, d = gradient_bg(1080, 1080, (20,10,50), (50,20,110))
    d.rectangle([0,0,1080,80], fill=BLUE)
    d.text((540,40), "個案分享  第 5 回", font=F(38), fill=WHITE, anchor="mm")
    d.text((540,280), "[你最有力嘅個案]", font=F(72), fill=WHITE, anchor="mm")
    d.text((540,390), "展示顧問視角", font=F(80), fill=TEAL, anchor="mm")
    d.text((540,490), "試過唔同方法", font=F(70), fill=(180,210,255), anchor="mm")
    d.text((540,580), "最後搵到啱方向", font=F(66), fill=(160,195,240), anchor="mm")
    divider(d, 660, 1080, color=TEAL)
    d.text((540,750), "向左掃看完整個案  >>", font=F(44), fill=(180,210,240), anchor="mm")
    rounded_rect(d,[300,830,780,890],20,(255,255,255,30))
    d.text((540,860), "#Stanley痛症個案", font=F(34), fill=WHITE, anchor="mm")
    footer_bar(img, d, 1080, 1080)
    img.save(f"{BASE}/day29_case5/slide_01_cover_template.png")

    labels = [
        ("客人背景", BLUE,   "年齡 / 職業 / 生活習慣 / 困擾時間"),
        ("困擾問題", TEAL,   "主要症狀 + 對生活影響"),
        ("試過方法", ORANGE, "多種方法都失敗嘅經歷"),
        ("最終方案", GREEN,  "找對方向後的根本改善"),
        ("CTA",      BLUE,   "試過很多方法？DM 我重新評估方向"),
    ]
    for i, (title, color, hint) in enumerate(labels, 2):
        img, d = new_img(1080, 1080, CREAM)
        top_label(d, 1080, title, bg=color)
        d.text((540,300), f"[ {title} ]", font=F(80), fill=color, anchor="mm")
        divider(d, 420, 1080, color=color)
        wrap_text(d, hint, 80, 460, F(44), GREY, 920)
        rounded_rect(d,[80,700,1000,780],15,(235,240,255))
        d.text((540,740), "根據你真實個案填入內容", font=F(36), fill=BLUE, anchor="mm")
        footer_bar(img, d, 1080, 1080)
        img.save(f"{BASE}/day29_case5/slide_0{i}_template.png")
    print("  day29 case5 template (6 slides)")


# ═══════════════════════════════════════════════════════════
# DAY 30 — 30日總結 Reel Cover (1080x1920)
# ═══════════════════════════════════════════════════════════
def make_day30_reel():
    img, d = gradient_bg(1080, 1920, BLUE, (15,35,80))
    d.rectangle([0,0,1080,100], fill=TEAL)
    d.text((540,50), "30 日總結", font=F(44), fill=WHITE, anchor="mm")
    divider(d, 110, 1080, color=TEAL)
    d.text((540,320), "開咗 30 日", font=F(120), fill=WHITE, anchor="mm")
    d.text((540,480), "我學到啲咩", font=F(100), fill=TEAL, anchor="mm")
    divider(d, 590, 1080, color=TEAL)
    insights = ["好多人有痛症，但唔知由邊度開始",
                "坊間謬誤真係好多，每次分享都有人話第一次聽到",
                "大部分人唔係治療唔好——係方向錯了"]
    y = 640
    for ins in insights:
        rounded_rect(d,[60,y,1020,y+110],20,(255,255,255,20))
        wrap_text(d, ins, 90, y+20, F(36), WHITE, 880)
        y += 130
    divider(d, y+20, 1080, color=(255,255,255,60))
    d.text((540,y+80), "真心話", font=F(80), fill=TEAL, anchor="mm")
    rounded_rect(d,[160,y+180,920,y+290],30,(255,255,255,30))
    d.text((540,y+235), "Follow 住，下個月更多", font=F(48), fill=WHITE, anchor="mm")
    d.rectangle([0,1820,1080,1920], fill=BLUE)
    d.text((540,1870), "Stanley | 痛症方案顧問", font=F(36), fill=WHITE, anchor="mm")
    img.save(f"{BASE}/day30_reel/reel_cover.png")
    print("  day30 reel cover")


# ═══════════════════════════════════════════════════════════
# STORY TEMPLATES — 通用 Story 模板 (1080x1920)
# ═══════════════════════════════════════════════════════════
story_configs = [
    ("day02", "投票問卷", "你而家最困擾你嘅係？",
     [("A) 頸 / 肩 / 背痛", TEAL), ("B) 膝蓋 / 關節痛", BLUE)]),
    ("day04", "Q&A", "你有咩關於痛症\n嘅問題想問我？",
     [("在下面留言 / DM 我", TEAL), ("所有問題都會回覆", BLUE)]),
    ("day06", "日常分享", "準備緊下週個案分享\n你最想睇邊類？",
     [("頸肩痛", TEAL), ("膝蓋 / 關節痛", BLUE)]),
    ("day09", "痛症貼士", "頸椎痛延伸貼士\n每日一個習慣改變",
     [("低頭族注意", TEAL), ("DM 我了解更多", BLUE)]),
    ("day11", "互動", "多謝大家留言！\n我逐一回覆緊",
     [("有問題隨時問", TEAL), ("DM 我免費傾", BLUE)]),
    ("day13", "生活分享", "今日工作日常\n幫緊另一個個案分析",
     [("有痛症困擾？", TEAL), ("DM 我免費評估", BLUE)]),
    ("day16", "收集問題", "下次分享你最想知咩？",
     [("留言告訴我", TEAL), ("所有問題都睇", BLUE)]),
    ("day18", "回覆留言", "多謝留言換資料嘅朋友\n已逐一 PM 咗",
     [("未收到？DM 我", TEAL), ("歡迎 Follow", BLUE)]),
    ("day20", "生活日常", "見完個案，分享一個\n今日最印象深刻嘅發現",
     [("DM 我了解更多", TEAL), ("免費評估", BLUE)]),
    ("day23", "Story", "今日分享一個\n小小痛症知識",
     [("Follow 住學更多", TEAL), ("DM 我免費傾", BLUE)]),
    ("day25", "Story", "距離30日總結\n仲有 5 日",
     [("你有成長感覺嗎？", TEAL), ("DM 我分享", BLUE)]),
    ("day27", "生活分享", "30日快完成\n多謝大家一路支持",
     [("Follow 住繼續", TEAL), ("有問題 DM 我", BLUE)]),
]

def make_story(day_id, topic, main_text, options):
    img, d = gradient_bg(1080, 1920, BLUE, (15,35,80))
    d.rectangle([0,0,1080,120], fill=TEAL)
    d.text((540,60), f"Story — {topic}", font=F(44), fill=WHITE, anchor="mm")
    divider(d, 130, 1080, color=TEAL)
    wrap_text(d, main_text, 80, 500, F(78), WHITE, 920, line_gap=20)
    divider(d, 900, 1080, color=(255,255,255,60))
    y = 960
    for opt_text, opt_color in options:
        rounded_rect(d,[100,y,980,y+120],30,opt_color)
        d.text((540,y+60), opt_text, font=F(48), fill=WHITE, anchor="mm")
        y += 150
    d.rectangle([0,1820,1080,1920], fill=BLUE)
    d.text((540,1870), "Stanley | 痛症方案顧問", font=F(36), fill=WHITE, anchor="mm")
    img.save(f"{BASE}/stories/{day_id}_story.png")
    print(f"  {day_id} story")


# ═══════════════════════════════════════════════════════════
# HTML MOCKUP — IG Profile Preview
# ═══════════════════════════════════════════════════════════
def make_html_mockup():
    html = """<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Stanley 痛症 IG — 帳號預覽</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#fafafa; font-family:'Arial Unicode MS',Arial,sans-serif; }
  .phone-frame {
    max-width:430px; margin:20px auto; background:#fff;
    border-radius:40px; overflow:hidden;
    box-shadow:0 20px 60px rgba(0,0,0,.25);
    border:8px solid #1B3A6B;
  }
  /* Status bar */
  .status { background:#1B3A6B; color:#fff; font-size:11px;
            display:flex; justify-content:space-between;
            padding:6px 18px; }
  /* Top nav */
  .nav { display:flex; align-items:center; justify-content:space-between;
         padding:10px 16px; border-bottom:1px solid #eee; }
  .nav .username { font-size:17px; font-weight:700; color:#1B3A6B; }
  .nav .icons { display:flex; gap:18px; font-size:20px; }
  /* Profile section */
  .profile-section { padding:16px; }
  .profile-top { display:flex; align-items:center; gap:16px; margin-bottom:12px; }
  .avatar {
    width:86px; height:86px; border-radius:50%;
    background:linear-gradient(135deg,#1B3A6B,#2A9D8F);
    display:flex; align-items:center; justify-content:center;
    color:#fff; font-size:36px; font-weight:700;
    border:3px solid #2A9D8F;
    flex-shrink:0;
  }
  .stats { display:flex; gap:0; flex:1; justify-content:space-around; }
  .stat { text-align:center; }
  .stat .num { font-size:17px; font-weight:700; color:#1B3A6B; }
  .stat .label { font-size:11px; color:#666; }
  .name { font-size:14px; font-weight:700; color:#1a1a2e; }
  .category { font-size:12px; color:#2A9D8F; margin:2px 0 6px; }
  .bio { font-size:13px; color:#333; line-height:1.5; }
  .bio .tag { color:#1B3A6B; font-weight:600; }
  /* Buttons */
  .btn-row { display:flex; gap:8px; margin:12px 0; }
  .btn { flex:1; padding:7px; border-radius:8px; font-size:13px;
         font-weight:600; border:1.5px solid #ddd; text-align:center;
         cursor:pointer; }
  .btn-primary { background:#1B3A6B; color:#fff; border-color:#1B3A6B; }
  .btn-secondary { background:#fff; color:#1a1a2e; }
  /* Highlights */
  .highlights { display:flex; gap:14px; padding:0 12px 12px;
                overflow-x:auto; }
  .highlight { display:flex; flex-direction:column; align-items:center; gap:4px; }
  .hl-circle {
    width:62px; height:62px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:11px; font-weight:700; color:#fff;
    border:2px solid #ddd;
  }
  .hl-label { font-size:11px; color:#333; text-align:center; max-width:66px; }
  /* Tab bar */
  .tabs { display:flex; border-top:1px solid #ddd; border-bottom:1px solid #eee; }
  .tab { flex:1; padding:10px; text-align:center; font-size:18px; cursor:pointer; }
  .tab.active { border-bottom:2px solid #1B3A6B; color:#1B3A6B; }
  /* Grid */
  .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:2px; }
  .grid-item {
    aspect-ratio:1; overflow:hidden; position:relative;
    cursor:pointer;
  }
  .grid-item img { width:100%; height:100%; object-fit:cover; }
  .grid-item .overlay {
    position:absolute; inset:0; background:rgba(27,58,107,0);
    display:flex; align-items:center; justify-content:center;
    transition:.2s;
  }
  .grid-item:hover .overlay { background:rgba(27,58,107,.25); }
  /* Type badges */
  .badge {
    position:absolute; top:6px; right:6px;
    background:rgba(0,0,0,.55); color:#fff;
    font-size:9px; padding:2px 5px; border-radius:4px;
  }
  /* Bottom nav */
  .bottom-nav {
    display:flex; justify-content:space-around;
    padding:10px 0 16px; border-top:1px solid #eee;
    background:#fff;
  }
  .bottom-nav span { font-size:22px; cursor:pointer; }
  .bottom-nav span.active { color:#1B3A6B; }
  /* Post placeholders */
  .post-placeholder {
    width:100%; height:100%;
    display:flex; align-items:center; justify-content:center;
    font-size:11px; font-weight:600; text-align:center;
    padding:6px;
  }
</style>
</head>
<body>
<div style="text-align:center;padding:16px;background:#1B3A6B;color:#fff;font-size:13px;">
  Stanley 痛症 IG — 帳號視覺預覽 | 2026年5月
</div>

<div class="phone-frame">
  <!-- Status -->
  <div class="status">
    <span>9:41</span>
    <span>&#9679;&#9679;&#9679; WiFi &#9646;&#9646;&#9646;&#9646;</span>
  </div>

  <!-- Nav -->
  <div class="nav">
    <span style="font-size:20px;">&#8592;</span>
    <div class="username">stanley.paincare.hk</div>
    <div class="icons">
      <span>&#43;</span>
      <span>&#8942;</span>
    </div>
  </div>

  <!-- Profile -->
  <div class="profile-section">
    <div class="profile-top">
      <div class="avatar">S</div>
      <div class="stats">
        <div class="stat"><div class="num">0</div><div class="label">帖子</div></div>
        <div class="stat"><div class="num">0</div><div class="label">粉絲</div></div>
        <div class="stat"><div class="num">0</div><div class="label">已追蹤</div></div>
      </div>
    </div>
    <div class="name">Stanley</div>
    <div class="category">痛症方案顧問</div>
    <div class="bio">
      <span class="tag">&#128138;</span> 痛症管理｜幫你搵啱方法止痛<br>
      <span class="tag">&#128269;</span> X年見過幾百個痛症個案<br>
      <span class="tag">&#128202;</span> 個案分享｜療法比較｜日常護理<br>
      <span class="tag">&#127468;&#127472;</span> <span style="color:#2A9D8F;font-style:italic;">「唔係醫生，但我知你需要乜」</span><br>
      <span class="tag">&#128336;</span> 免費痛症方案諮詢 &#128071;
    </div>
    <div style="margin-top:6px;font-size:12px;color:#1B3A6B;font-weight:600;">
      linktr.ee/stanley.paincare
    </div>
    <div class="btn-row">
      <div class="btn btn-primary">追蹤</div>
      <div class="btn btn-secondary">發訊息</div>
      <div class="btn btn-secondary" style="flex:0.3;">&#9650;</div>
    </div>
  </div>

  <!-- Highlights -->
  <div class="highlights">
    <div class="highlight">
      <div class="hl-circle" style="background:linear-gradient(135deg,#1B3A6B,#2A9D8F);">CASE</div>
      <div class="hl-label">個案分享</div>
    </div>
    <div class="highlight">
      <div class="hl-circle" style="background:linear-gradient(135deg,#2A9D8F,#1B5E4F);">EDU</div>
      <div class="hl-label">痛症教育</div>
    </div>
    <div class="highlight">
      <div class="hl-circle" style="background:linear-gradient(135deg,#32644A,#1E3D2C);">RX</div>
      <div class="hl-label">療法科普</div>
    </div>
    <div class="highlight">
      <div class="hl-circle" style="background:linear-gradient(135deg,#8B4513,#D2691E);">LIFE</div>
      <div class="hl-label">生活日常</div>
    </div>
    <div class="highlight">
      <div class="hl-circle" style="background:linear-gradient(135deg,#6B1B6B,#9B4D9B);">FREE</div>
      <div class="hl-label">免費評估</div>
    </div>
  </div>

  <!-- Tabs -->
  <div class="tabs">
    <div class="tab active">&#9783;</div>
    <div class="tab">&#9651;</div>
    <div class="tab">&#9873;</div>
  </div>

  <!-- Grid — 9 posts preview -->
  <div class="grid">
    <!-- Row 1 -->
    <div class="grid-item">
      <div class="post-placeholder" style="background:linear-gradient(135deg,#1B3A6B,#0F2240);color:#fff;">
        我唔係醫生<br>但我知你嘅痛<br><span style="color:#2A9D8F;font-size:9px;">帳號介紹</span>
      </div>
    </div>
    <div class="grid-item">
      <div class="post-placeholder" style="background:linear-gradient(135deg,#1B3A6B,#2A9D8F);color:#fff;">
        點解我<br>會做痛症？<br><span style="color:#90EED4;font-size:9px;">個人故事</span>
      </div>
      <div class="badge">Reel</div>
    </div>
    <div class="grid-item">
      <div class="post-placeholder" style="background:linear-gradient(135deg,#0F2240,#1B3A6B);color:#fff;">
        頸痛 2 年<br>都冇用？<br><span style="color:#2A9D8F;font-size:9px;">個案分享 #1</span>
      </div>
      <div class="badge">1/6</div>
    </div>
    <!-- Row 2 -->
    <div class="grid-item">
      <div class="post-placeholder" style="background:linear-gradient(135deg,#0F2240,#3A2010);color:#fff;">
        熱敷定凍敷？<br>9成人整錯！<br><span style="color:#FF9070;font-size:9px;">謬誤破解</span>
      </div>
      <div class="badge">Reel</div>
    </div>
    <div class="grid-item">
      <div class="post-placeholder" style="background:#F0F4FF;color:#1B3A6B;">
        OT 頸痛<br>急救 3 招<br><span style="color:#2A9D8F;font-size:9px;">辦公室貼士</span>
      </div>
      <div class="badge">1/5</div>
    </div>
    <div class="grid-item">
      <div class="post-placeholder" style="background:linear-gradient(135deg,#1B4A1B,#2A7A2A);color:#fff;">
        膝蓋痛<br>唔使手術<br><span style="color:#90EE90;font-size:9px;">個案分享 #2</span>
      </div>
      <div class="badge">1/6</div>
    </div>
    <!-- Row 3 -->
    <div class="grid-item">
      <div class="post-placeholder" style="background:linear-gradient(135deg,#0F2240,#2A9D8F);color:#fff;">
        止痛藥食完<br>又痛返？<br><span style="color:#FFD700;font-size:9px;">留言換資料</span>
      </div>
      <div class="badge">Reel</div>
    </div>
    <div class="grid-item">
      <div class="post-placeholder" style="background:#F0F4FF;color:#1B3A6B;">
        衝擊波<br>係咩？<br><span style="color:#2A9D8F;font-size:9px;">療法科普</span>
      </div>
      <div class="badge">1/5</div>
    </div>
    <div class="grid-item">
      <div class="post-placeholder" style="background:linear-gradient(135deg,#3A1B00,#7A3500);color:#fff;">
        中醫 vs PT<br>vs 儀器<br><span style="color:#FFA060;font-size:9px;">療法比較</span>
      </div>
      <div class="badge">Reel</div>
    </div>
  </div>

  <!-- Bottom Nav -->
  <div class="bottom-nav">
    <span>&#8962;</span>
    <span>&#128269;</span>
    <span style="font-size:28px;color:#1B3A6B;">&#10010;</span>
    <span>&#9825;</span>
    <span class="active">&#128100;</span>
  </div>
</div>

<div style="text-align:center;padding:20px;color:#999;font-size:12px;">
  視覺預覽僅供參考 | 實際 IG 效果以正式發佈為準<br>
  Stanley 痛症方案顧問 | 2026年5月
</div>
</body>
</html>"""
    with open(f"{BASE}/IG_Profile_Preview.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  IG_Profile_Preview.html")

# ═══════════════════════════════════════════════════════════
# RUN ALL
# ═══════════════════════════════════════════════════════════
print("Generating IG assets...")
make_profile_pic()
for title, code, bg1, bg2, icon in highlights:
    make_highlight(title, code, bg1, bg2, icon)
make_day01()
make_day03_reel()
make_day08()
make_day10_reel()
make_day12()
make_day15()
make_day17_reel()
make_day19()
make_day22()
make_day24_reel()
make_day26()
make_day29()
make_day30_reel()
for day_id, topic, main_text, options in story_configs:
    make_story(day_id, topic, main_text, options)
make_html_mockup()

# Summary
total = sum(len(os.listdir(f"{BASE}/{d}")) for d in os.listdir(BASE) if os.path.isdir(f"{BASE}/{d}"))
root_files = [f for f in os.listdir(BASE) if os.path.isfile(f"{BASE}/{f}")]
print(f"\nDone! Generated {total + len(root_files)} files in:")
print(f"  {BASE}/")
for d in sorted(os.listdir(BASE)):
    p = f"{BASE}/{d}"
    if os.path.isdir(p):
        files = os.listdir(p)
        print(f"  /{d}/  ({len(files)} files)")
    else:
        print(f"  {d}")
