from fpdf import FPDF

FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
OUTPUT_PATH = "/Users/rickyc./Desktop/Vs code /Project 2 (Stanley)/Dream_Team_IG引流策略分析.pdf"


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
        self.cell(0, 10, f"Stanley Dream Team 終極作戰室  |  第 {self.page_no()} 頁", align="C")

    def cover(self):
        self.add_page()
        self.set_fill_color(18, 18, 36)
        self.rect(0, 0, 210, 297, "F")
        self.set_y(70)
        self.set_font("u", size=26)
        self.set_text_color(255, 210, 0)
        self.multi_cell(0, 13, "Dream Team 終極作戰室", align="C")
        self.ln(5)
        self.set_font("u", size=14)
        self.set_text_color(180, 180, 255)
        self.multi_cell(0, 9, "Stanley IG 引流策略全面分析", align="C")
        self.ln(4)
        self.set_font("u", size=10)
        self.set_text_color(130, 130, 200)
        self.multi_cell(0, 7, "問題：開 IG 帳號 + 生成吸睛文稿 -> 網上引流吸客，可唔可行？", align="C")
        self.ln(2)
        self.multi_cell(0, 7, "背景：美容及痛症管理銷售從業者，目標客群 18-65 歲", align="C")
        self.ln(10)
        self.set_font("u", size=9)
        self.set_text_color(90, 90, 130)
        self.multi_cell(0, 6, "8 位頂尖教練  x  5 個天才維度  x  終極裁決", align="C")
        self.ln(2)
        self.multi_cell(0, 6, "2026年5月11日", align="C")

    def layer_title(self, text, r=25, g=25, b=55, tr=255, tg=210, tb=0):
        self.ln(5)
        self.set_fill_color(r, g, b)
        self.set_text_color(tr, tg, tb)
        self.set_font("u", size=13)
        self.multi_cell(0, 9, f"  {text}", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def coach_block(self, name, subtitle, insight, body1, body2, action, warning):
        self.ln(3)
        self.set_fill_color(42, 42, 75)
        self.set_text_color(255, 195, 45)
        self.set_font("u", size=12)
        self.multi_cell(0, 8, f"  {name}", fill=True)
        self.set_fill_color(55, 55, 95)
        self.set_text_color(190, 190, 240)
        self.set_font("u", size=9)
        self.multi_cell(0, 6, f"  {subtitle}", fill=True)
        self.ln(2)
        # Insight
        self.set_fill_color(255, 248, 215)
        self.set_font("u", size=10)
        self.set_text_color(80, 55, 0)
        self.multi_cell(0, 6, f"核心洞察：{insight}", fill=True)
        self.ln(2)
        # Body
        self.set_font("u", size=10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, body1)
        self.ln(2)
        self.multi_cell(0, 6, body2)
        self.ln(2)
        # Action
        self.set_fill_color(225, 248, 225)
        self.set_text_color(0, 80, 0)
        self.multi_cell(0, 6, f"要你做：{action}", fill=True)
        self.ln(1)
        # Warning
        self.set_fill_color(252, 232, 232)
        self.set_text_color(170, 0, 0)
        self.multi_cell(0, 6, f"[!] 質疑你：{warning}", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(4)
        self.set_draw_color(210, 210, 210)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)

    def dim_block(self, name, subtitle, insight, body1, body2, action, risk):
        self.ln(3)
        self.set_fill_color(12, 48, 72)
        self.set_text_color(90, 210, 255)
        self.set_font("u", size=12)
        self.multi_cell(0, 8, f"  {name}", fill=True)
        self.set_fill_color(18, 65, 95)
        self.set_text_color(170, 230, 255)
        self.set_font("u", size=9)
        self.multi_cell(0, 6, f"  {subtitle}", fill=True)
        self.ln(2)
        self.set_fill_color(230, 248, 255)
        self.set_font("u", size=10)
        self.set_text_color(0, 60, 100)
        self.multi_cell(0, 6, f"核心洞察：{insight}", fill=True)
        self.ln(2)
        self.set_font("u", size=10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, body1)
        self.ln(2)
        self.multi_cell(0, 6, body2)
        self.ln(2)
        self.set_fill_color(225, 248, 225)
        self.set_text_color(0, 80, 0)
        self.multi_cell(0, 6, f"行動建議：{action}", fill=True)
        self.ln(1)
        self.set_fill_color(255, 243, 215)
        self.set_text_color(140, 75, 0)
        self.multi_cell(0, 6, f"風險：{risk}", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(4)
        self.set_draw_color(210, 210, 210)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)

    def verdict_section(self, title, body, r=50, g=50, b=100):
        self.ln(3)
        self.set_fill_color(r, g, b)
        self.set_text_color(255, 255, 200)
        self.set_font("u", size=11)
        self.multi_cell(0, 8, f"  {title}", fill=True)
        self.ln(2)
        self.set_font("u", size=10)
        self.set_text_color(25, 25, 25)
        self.multi_cell(0, 6, body)
        self.ln(2)

    def priority_row(self, num, label, text, cr, cg, cb):
        self.set_fill_color(cr, cg, cb)
        self.set_text_color(255, 255, 255)
        self.set_font("u", size=10)
        x = self.get_x()
        y = self.get_y()
        self.cell(9, 8, str(num), fill=True, align="C")
        self.set_fill_color(cr + 30 if cr + 30 <= 255 else 255,
                            cg + 30 if cg + 30 <= 255 else 255,
                            cb + 30 if cb + 30 <= 255 else 255)
        self.set_text_color(20, 20, 60)
        self.set_font("u", size=9)
        self.set_fill_color(240, 242, 255)
        self.multi_cell(0, 8, f"  [{label}]  {text}", fill=True)
        self.ln(1)


def build():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_font("u", fname=FONT_PATH)
    pdf.set_margins(15, 15, 15)

    pdf.cover()

    # ──────────────────────────────────────────────
    # LAYER 1
    # ──────────────────────────────────────────────
    pdf.add_page()
    pdf.layer_title("第一層：教練作戰室   8位教練各自從專業框架出發")
    pdf.set_font("u", size=10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 6, "每位教練超過 80 字分析，語氣符合各自身份", align="C")
    pdf.ln(4)

    # CARDONE
    pdf.coach_block(
        "Grant Cardone   銷售規模化 · 10X 行動量",
        "銷售規模化 · 行動量至上 · 唔妥協",
        "你諗住「開個 IG 試下」——呢個思維已經輸咗，要係「開 IG 然後每日轟炸市場」。",
        "IG 引流唔係試驗，係你嘅第二個銷售員。問題唔係「可唔可行」，係你願唔願意以10倍速度去做。大部分人開 IG 係一個星期發5篇，見唔到即時成效就放棄——呢個係普通人思維。你要喺頭90日發出300個觸點：post、story、reels、comment、DM，全部一齊出。",
        "美容同痛症係高關注度行業，客人喺作決定之前平均睇你7至12次先信你。你唔係要「吸精」，你係要「建立信任密度」。一篇文稿唔夠，要鋪天蓋地，令客人喺香港 IG 界睇美容痛症嘅時候，第一個想起嘅名係你。",
        "頭30日每日最少3個 content 觸點（post / story / reel），唔完美都出，量先於質，先佔領演算法再優化。",
        "你講「生成文稿」——你係打算自己拍片做 face of the brand，定係純文字帖？如果你唔出鏡，Cardone 話你：冇臉就冇信任，冇信任就冇成交。",
    )

    # HORMOZI
    pdf.coach_block(
        "Alex Hormozi   報價設計 · 商業模式數學",
        "報價設計 · 價值方程式 · LTV/CAC · 冷靜邏輯",
        "IG 係注意力，但注意力唔等於收入——你需要一個清晰嘅 offer 等人 follow 完之後知道要買乜。",
        "你而家嘅計劃有個根本漏洞：「吸精文稿」→「引流」之間缺少一個橋樑——就係一個令人無法拒絕嘅 offer。如果你 IG 搞到10萬 followers，但 profile 入面冇清晰嘅 lead magnet 或者 CTA，你只係免費娛樂人群，唔係做生意。計數：每1000個真實 followers，你平均可以轉化幾多個詢問？如果你唔知呢個數字，你係在燒時間。",
        "Hormozi 嘅 value equation：夢想結果 x 實現可能性 / 時間成本 / 風險 = 你 offer 嘅吸引力。你嘅內容唔係講你有幾叻，係要令睇嘅人感受到「我的夢想結果好近」。美容講逆齡、痛症講重拾生活質素——每一篇 post 都要對應呢條公式。",
        "未開 IG 之前，先寫清楚你嘅 hero offer：一個具體服務 + 具體結果 + 具體時間 + 具體保證，放喺 bio 第一行。",
        "你嘅美容線同痛症線係兩個完全唔同嘅 offer，擺埋一個 IG 係稀釋定係互補？你有冇計過混帳號對轉化率嘅影響？",
    )

    # GARY VEE
    pdf.add_page()
    pdf.coach_block(
        "Gary Vee   社交媒體 · 注意力經濟",
        "內容策略 · 平台機會 · 個人品牌 · 直接率真",
        "2026年 IG 最值錢嘅資產唔係文稿，係你這個人——document，唔係 create。",
        "我唔係話文稿唔重要，但你諗「生成文稿」嘅思維已經係舊世界。而家 IG 最高 organic reach 係 reels，最高信任度係 stories，最高轉化率係「真實記錄過程」嘅內容。香港美容痛症市場好飽和，純靠美圖 + 精美文案係2020年嘅打法。你要贏，要靠 authenticity arbitrage——就係大品牌做唔到嘅真實人味。",
        "你嘅武器係你嘅日常：同客人對話嘅片段（得到許可下）、你去上課進修嘅 behind-the-scenes、你解答痛症問題嘅30秒 reel。呢啲嘢大牌子做唔到，你做得到。「吸精文稿」係 push marketing，「真實記錄」係 pull marketing，後者喺2026年係十倍速。",
        "開 IG 之前，用手機錄3條30秒 reel：第一條係「你係邊個 + 點樣幫到人」，第二條係解答一個常見痛症問題，第三條係一個美容 before/after。開帳號即日出。",
        "你話「生成文稿」——係用 AI 幫你寫？定係你自己根本唔打算出鏡？如果係後者，你放棄咗 IG 最大嘅優勢：個人信任建立。",
    )

    # BRUNSON
    pdf.coach_block(
        "Russell Brunson   銷售漏斗 · 故事銷售",
        "漏斗設計 · 故事結構 · 自動化轉化 · 系統化思維",
        "IG 係漏斗嘅頂端，你而家只係在設計頂端，但冇設計漏斗其他部份——流量進來之後去邊？",
        "好多人開 IG，但冇諗清楚 IG → 下一步係咩。係 WhatsApp 查詢？係 Google Form 預約？係一個免費試用 offer？係一篇長文 lead magnet？如果你嘅 IG 係個水喉，但冇接水桶，水流哂走都係浪費。你要在開 IG 之前，設計清楚呢個 value ladder：免費內容（IG）→ 微承諾（DM）→ 低門檻 offer → 核心服務 → 高端套餐。",
        "另外，你嘅內容要用「英雄故事結構」：客人原本係咩狀態（痛點）→ 遇到咩挑戰 → 點樣透過你嘅服務解決 → 現在係咩狀態。呢個係比「我哋服務好好」有效100倍嘅 storytelling，而且 IG 演算法特別鍾意帶情感的內容。",
        "畫出你嘅5步 value ladder，確保 IG bio 有清晰嘅「下一步」連結（唔係「查詢請 DM」，係一個具體 offer 連結）。",
        "你嘅漏斗在哪裡斷開？客人 follow 你之後，你有冇系統去 nurture 佢到成交？定係你期望 IG post 本身就可以直接成交？",
    )

    # KENNEDY
    pdf.add_page()
    pdf.coach_block(
        "Dan Kennedy   直接回應行銷 · 文案",
        "可量度行銷 · 文案效力 · 理想客戶精準度 · 務實量化",
        "「吸睛」係虛榮指標，「吸單」先係真正目標——你每一篇 post 要有 direct response 機制。",
        "我做行銷超過40年，見過太多人執著於 likes 同 followers，最後 bank account 係空嘅。真正有效嘅行銷有三個元素：對的人（Message）、對的訊息（Market）、對的媒介（Media）——你三個都要對齊。你嘅美容同痛症客群喺 IG 上係唔同人，佢哋用 IG 嘅方式唔同，對內容嘅反應唔同，你唔可以用同一套文案打兩個截然不同嘅市場。",
        "每一篇 post 都要有清晰嘅 call-to-action，唔係「like if you agree」，係「如果你有呢個問題，依家 DM 我『了解』兩個字，我 send 你一份免費資料」。呢個係 trackable 嘅。我唔理你 IG 有幾多 followers，我只關心你每個月透過 IG 帶嚟幾多個真實查詢，同呢啲查詢最終成交率係幾多。如果你唔追蹤呢個數字，你係在黑暗中燒錢。",
        "為每條 post 設計一個 measurable CTA，建立追蹤表格：每月 IG 觸及數、DM 查詢數、WhatsApp 轉介數、最終成交數。從第一日開始追蹤。",
        "你知唔知而家你嘅客人係從哪個渠道來嘅？如果連現有客源都唔清楚，開 IG 只係在增加一條你唔追蹤的渠道。",
    )

    # BELFORT
    pdf.coach_block(
        "Jordan Belfort   說服力 · 成交科學",
        "成交率 · 三個十確定性 · 反對意見處理 · 精準分析",
        "你嘅 IG 內容要同時提高三個確定性分數：對產品、對你、對現在行動。",
        "銷售有三個確定性：客人對你個 product/service 嘅信心、對你呢個人嘅信心、對「依家就要行動」嘅緊迫感。大部分人嘅 IG 只係提高第一個確定性（講產品好），完全忽略第二同第三。你嘅內容組合要係：40% 建立你個人可信度同專業（你的確定性）、40% 展示成果同案例（產品確定性）、20% 創造緊迫感（依家行動嘅確定性）。",
        "緊迫感唔係造假，係真實嘅限制：名額有限、季節性優惠、特定活動配合的推廣。如果你嘅 IG 永遠係「歡迎查詢」，係最低成交率嘅 CTA。你要令睇帖嘅人有「依家唔行動會後悔」嘅感覺，但係用真實原因，唔係虛假倒數。",
        "審視你計劃的內容結構，確保三類內容都有：個人背景/故事 post、客戶成果/testimonial post、限時 offer post，三者缺一唔可。",
        "你有冇想過 IG 的成交率係極低的？大部分行業 IG lead → 成交係低於3%。你嘅計劃係點系統性地提升呢個數字，定係只係希望「量多自然有」？",
    )

    # SETH GODIN
    pdf.add_page()
    pdf.coach_block(
        "Seth Godin   品牌定位 · 部落建立",
        "定位策略 · 最小可行受眾 · 值得被談論嘅設計 · 哲學安靜",
        "香港 IG 美容痛症帳號有幾千個——你係 another one，還是 the only one？",
        "在你買第一個 follower 之前，你要回答一個問題：你嘅帳號係為誰而存在？唔係「18-65歲有美容或痛症需求的人」——呢個唔係受眾，係人口統計數字。真正嘅部落係有共同信念嘅人：「相信痛症唔應該靠止痛藥解決而係靠根源治理」、「相信自然美容比醫學美容更可持續」。你選擇哪一個信念站隊，就決定你吸引哪一種人。",
        "「吸睛文稿」係大眾化思維。值得被談論嘅設計係：你嘅帳號有冇一個唔 follow 就後悔嘅獨特觀點？有冇一個清晰嘅立場，令一部分人非常喜歡、另一部分人完全不喜歡？模糊嘅定位吸引模糊嘅客人，清晰嘅立場建立忠實部落。",
        "在開帳號之前，寫一句話「我嘅帳號係香港唯一一個___的地方」，填入呢個空格，先決定你想做邊個小眾市場嘅第一名。",
        "如果你嘅美容線同痛症線放喺同一個帳號，你係在服務兩個完全不同信念的部落——呢個係否模糊咗你嘅定位，令兩邊都唔夠 resonance？",
    )

    # TONY ROBBINS
    pdf.coach_block(
        "Tony Robbins   巔峰心理 · 狀態管理",
        "信念系統 · 客戶心理需求 · 執行狀態 · 熱情激勵",
        "你嘅 IG 成敗，90% 取決於你係咪真係相信自己提供嘅係真正嘅價值轉化。",
        "客人買嘅唔係美容服務或痛症管理，佢哋買嘅係「更好版本的自己」。你嘅每一篇 content，都係在回答一個問題：「我能讓你的生活有什麼改變？」如果你只係在賣服務，你係在跟幾千個對手打價格戰。如果你係在賣轉化，你係在做一場完全唔同嘅遊戲。",
        "好多人開 IG 第一個月好勤力，第二個月見唔到回報開始散，第三個月放棄——然後話「IG 對我冇用」。你嘅內容質素同一致性，係你內心信念嘅直接反映。如果你唔係真心相信你嘅服務改變緊人嘅生活，你嘅 content 會透出一種「試下啫」的能量，而客人感受得到。你要先喺內心建立一個清晰嘅 vision：5年後你嘅品牌係點樣嘅？你幫助咗幾多人？",
        "搵出你最近3個真實客人成功案例，唔論大小——寫低佢哋嘅轉化故事。呢個係你 IG 內容嘅情感燃料，同時係你自己維持動力嘅錨點。",
        "你講「諗住開個 IG」——你係真心投入定係半信半疑試下？IG 引流係一個需要至少6個月持續投入先見成效嘅渠道，你準備好呢個心理預算未？",
    )

    # ──────────────────────────────────────────────
    # LAYER 2
    # ──────────────────────────────────────────────
    pdf.add_page()
    pdf.layer_title("第二層：天才維度審視   5個維度對教練集體智慧嘅更高層拆解", 10, 45, 70, 90, 215, 255)
    pdf.set_font("u", size=10)
    pdf.set_text_color(90, 90, 90)
    pdf.multi_cell(0, 6, "唔係重複教練建議，而係從更高維度審視、補充、甚至推翻", align="C")
    pdf.ln(4)

    # WISDOM
    pdf.dim_block(
        "智者維度",
        "從最深嘅智慧和歷史規律審視教練們嘅建議",
        "8位教練嘅建議合在一起揭示了一個古老真理——信任永遠比流量更值錢，而信任係靠時間密度，唔係內容密度建立。",
        "教練們各自從不同角度講，但佢哋建議嘅底層邏輯係一致：你要建立嘅唔係一個 IG 帳號，而係一個信任基礎設施。Hormozi 話 offer，Brunson 話漏斗，Kennedy 話追蹤，Godin 話定位——所有這些都只係信任建立嘅不同載體。歷史上每一個成功嘅諮詢服務行業，從律師到醫生到美容師，客人最終選擇你嘅原因都係同一個：「我信任你」。而 IG 在呢件事上嘅獨特價值，係佢讓你以前所未有嘅低成本建立高頻接觸點。",
        "但有一個規律所有教練都冇講清楚：美容同痛症係高度依賴「社交證明」嘅行業，因為客人係在購買一個佢眼睛還未看到的結果。所以你嘅 IG 最核心的資產唔係你的文采，係你的 testimonials、case studies、before/after——呢啲係 social proof 的燃料，係客人跨越猶豫門檻嘅關鍵。所有技巧圍繞呢個核心，而唔係相反。",
        "從今日起，每個成功服務嘅客人都要系統性地收集「轉化故事」——唔係硬銷式的 testimonial，係真實的生活改變，呢個才是你 IG 嘅真正地基。",
        "如果你的 IG 建立在精美文稿上，但缺乏真實 social proof，一旦有一個客人公開差評或者一個競爭對手比你更真實，你嘅信任基礎係脆弱嘅。",
    )

    # CHALLENGER
    pdf.add_page()
    pdf.dim_block(
        "挑戰者維度",
        "質疑教練們嘅假設，包括挑戰教練本身嘅盲點",
        "8位教練嘅建議全部建基於一個未經驗證的假設——你嘅目標客群真係活躍喺 IG 上，而且係透過 IG 發現服務的。",
        "Cardone 叫你每日3個觸點、Gary Vee 叫你做 reels、Brunson 叫你設計漏斗——但他們全部都冇問一個最根本的問題：你現有客人係從哪度嚟的？香港美容痛症嘅消費決策，傳統上極度依賴熟人轉介、口碑、同場地見聞。如果你現有客源80%係 word of mouth，IG 係一個全新的客戶獲取渠道，它嘅轉化邏輯同你現有成功模式係完全唔同嘅——唔係「做多啲就好」，係「要重新學一套客人信任建立方式」。",
        "另外，教練們都係美國市場背景，但香港 IG 生態有幾個重要分別：香港用戶對 IG 購物轉化率遠低於小紅書或 Facebook；香港美容客群大量集中喺 Facebook Groups 同小紅書，唔係 IG；痛症管理嘅客群喺 YouTube 搜索「頸痛點算」比喺 IG 刷到你高轉化得多。換言之，Cardone 同 Gary Vee 叫你死磕 IG，但香港市場係咪 IG 真係最高 ROI 的渠道？你有冇驗證過？",
        "開 IG 之前，先做一個快速驗證：問你現有10個客人，佢哋係點樣發現你、點樣決定用你嘅服務——答案可能會完全改變你嘅渠道優先級。",
        "盲目跟隨教練的「IG 全押」策略，最大危險係你用6個月時間建立一個唔係你客群聚集地的渠道，同時放棄了把同等時間投入到真正有效渠道的機會。",
    )

    # EMPATHY
    pdf.dim_block(
        "同理者維度",
        "從人嘅感受、關係、情感因素審視",
        "教練們設計的是一個讓人「被轉化」的機器，但客人——尤其是美容同痛症客人——想要的是「被看見」，唔係「被轉化」。",
        "痛症同美容都係極度私人嘅需求。一個揹住慢性頸痛嘅人，係帶著羞恥感或挫敗感的——「我試過好多方法都冇用」。一個想改善皮膚嘅女士，係帶著自我批判同焦慮嘅——「我點解唔夠靚」。呢啲人打開 IG 嘅時候，佢哋係在尋找認同感同希望，唔係在等你嘅 sales funnel。如果你嘅 IG 感覺像一部銷售機器，呢班人會在情感上退縮，即使佢哋理性上認為你係專業的。",
        "教練們，尤其係 Cardone 同 Hormozi，極度強調 offer 同轉化率，但完全唔講「何時不要 push」。美容痛症客人有時需要先喺你嘅 IG 上「養」3個月，只係 like，唔查詢，然後突然有一日 DM 你。呢個「養」的過程唔係浪費，係信任建立嘅必要期。你嘅內容要有空間讓人「靜靜地觀察你」，而唔係每一篇都係 CTA。",
        "設計「人味內容」比例——至少30%嘅 post 係純分享，唔帶任何 CTA：你遇到一個有趣嘅個案、你今日學到嘅嘢、你對痛症或美容某個誤解嘅看法。令人想留喺你身邊，唔係即刻被推去詢問。",
        "如果你嘅 IG 從一開始就100%  sales-driven，你會吸引到最容易流失嘅客人——那些只看優惠嘅人——而嚇走最忠實的客人——那些需要先建立信任的人。",
    )

    # PROPHET
    pdf.add_page()
    pdf.dim_block(
        "預言者維度",
        "從10年後回望今日嘅決定",
        "10年後嘅 Stanley 最後悔嘅，唔係「開早咗定開遲咗 IG」，係「有冇在那個時候建立屬於自己的數據資產」。",
        "2036年回望2026年，有幾個趨勢係而家已經清晰可見的：AI 生成內容成本趨近零，意味著所有人都可以做高質文案，唔係你嘅競爭優勢；平台演算法隨時改變，依賴單一平台等於把你的業務基礎放在別人的地上；但有一樣嘢唔會變——一個高質量的客戶 WhatsApp 列表，係你永久擁有的資產。教練們其中 Kennedy 提過追蹤，但都冇人係咁講：你今日 IG 所有嘅努力，最終目標係建立你自己的 first-party data——客人嘅聯絡方式、需求、消費模式。",
        "另一個10年視角：美容同痛症行業正在走向「信任經濟」。隨著市場上 AI 建議、網上資訊越來越多，客人對人的需求唔係降低，係提高——但他們要求的是「深度信任」而非「曝光量」。今日係量嘅遊戲，10年後會係質的遊戲。如果你今日就開始建立「深度」的 IG 而不只是「廣度」的 IG，你在2036年嘅起點比其他人高出很多。",
        "從第一日起，你嘅 IG 每一個 CTA 都要指向「加入你的 WhatsApp channel」或者「登記你的名單」，唔係只係 DM 查詢。你要在 IG 以外建立你自己的客戶資產。",
        "今日最可能後悔嘅決定係：花了12個月做 IG，積累了5000個 followers，然後 IG 演算法改了，reach 跌90%，但你冇任何 WhatsApp list 或 email list。你嘅5000個 followers 係 IG 嘅，唔係你嘅。",
    )

    # OUTSIDER - ER DOCTOR
    pdf.dim_block(
        "局外者維度   急症室醫生視角",
        "用急症室的思維框架審視 Stanley 的 IG 計劃",
        "你係在「診斷之前就開藥」——IG 係你選擇的治療方案，但你仲未完成對症狀的評估。",
        "急症室最危險嘅錯誤唔係誤診，係「confirmation bias」——病人話我胃痛，醫生聽完就開胃藥，但胃痛係心臟病嘅症狀，真正嘅問題係冠狀動脈梗塞。你話「我諗住開 IG 引流」，但你有冇先診斷清楚你嘅問題係「引流不足」還是「轉化率低」？一個引流不足的業務同一個轉化率低的業務，表面症狀可能係一樣（生意唔夠好），但正確嘅治療方案係完全唔同嘅。",
        "急症室另一個原則：triage——先處理最緊急最高影響的問題，唔係所有問題同時醫。如果你現有20個客人，轉化率係10%，即係每10個問你的人只有1個成交，呢個時候去做 IG 引流，係把更多人放入一個有漏洞的系統——100個 leads 入來，只成交10個。但如果你先把轉化率提升至30%，然後同樣做 IG，100個 leads 成交30個。病治好先，再 Scale。",
        "做一個快速「業務體檢」：最近30日，你有幾多個 leads，成交咗幾多個，放棄嘅人最常見理由係咩。呢個數據決定你應該先修轉化還是先做引流。",
        "開 IG 嘅最大隱藏風險，唔係冇流量，係有流量但轉化率低，然後你以為係「IG 唔好用」，其實係你嘅銷售流程有漏洞。開 IG 前唔先修轉化，係最大嘅資源浪費。",
    )

    # ──────────────────────────────────────────────
    # VERDICT
    # ──────────────────────────────────────────────
    pdf.add_page()
    pdf.layer_title("終極裁決   第一層 x 第二層 綜合結論", 70, 0, 0, 255, 200, 50)

    pdf.verdict_section(
        "第一層 x 第二層 交叉發現",
        "教練們集體告訴你「點做 IG」，但天才維度嘅最重要發現係：你仲未確認 IG 係正確嘅主戰場，同時你嘅轉化系統係咪準備好接收流量。最關鍵嘅交叉矛盾係——Cardone/Gary Vee 叫你立即大量行動，但挑戰者同急症室醫生嘅分析指出，盲目行動之前需要先驗證假設。呢兩者唔係互相排斥，而係有優先次序：先用兩週時間做基礎驗證，然後再全力衝刺。",
        55, 20, 20,
    )

    pdf.verdict_section(
        "所有聲音一致同意",
        "1.  IG 只係漏斗頂端，必須配合清晰嘅 offer + CTA + 下一步，否則 followers 唔等於收入\n"
        "2.  個人真實性係2026年最大嘅競爭優勢——純 AI 文稿冇人味，出鏡同真實案例係必要元素\n"
        "3.  要從第一日起追蹤可量化嘅數字——唔係 likes，係 leads → 查詢 → 成交這條轉化路徑",
        0, 55, 25,
    )

    pdf.verdict_section(
        "最重要嘅分歧",
        "Cardone vs Seth Godin：Cardone 叫你立即大量出內容佔領演算法；Godin 叫你先找清楚你係邊個小眾嘅第一名再出發。\n"
        "Stanley 嘅情況：香港美容痛症市場係 Red Ocean，「generic 美容痛症帳號」冇定位，量多都係噪音。\n"
        "建議：先花3日定清楚你的帳號立場，然後用 Cardone 的執行速度出內容。\n\n"
        "教練集體 vs 挑戰者：教練們預設 IG 係正確渠道；挑戰者質疑香港市場渠道選擇。\n"
        "建議：IG 值得做，但同步考慮小紅書（美容線）同 YouTube/FB（痛症線），唔好把所有雞蛋放一個籃。",
        55, 35, 0,
    )

    pdf.ln(3)
    pdf.set_fill_color(18, 18, 45)
    pdf.set_text_color(255, 210, 0)
    pdf.set_font("u", size=12)
    pdf.multi_cell(0, 9, "  Stanley 嘅行動優先級", fill=True, align="L")
    pdf.ln(3)

    pdf.set_font("u", size=10)
    pdf.set_text_color(60, 0, 80)
    pdf.multi_cell(0, 7, "本週立即做")
    pdf.ln(1)
    pdf.priority_row(1, "業務體檢", "問你最近10個成交同10個流失嘅客人，佢哋係點樣發現你、點樣決定嘅。15分鐘對話，決定你嘅渠道策略。", 90, 0, 110)
    pdf.priority_row(2, "帳號定位句", "「我嘅帳號係香港唯一一個___的地方」，填完呢個空格先開帳號。同時確定你的 bio + hero offer + 第一個 CTA 連結。", 90, 0, 110)

    pdf.ln(2)
    pdf.set_text_color(0, 55, 100)
    pdf.multi_cell(0, 7, "本月完成")
    pdf.ln(1)
    pdf.priority_row(3, "建立客戶接觸點", "建立 WhatsApp channel 或 landing page——你 IG 所有流量嘅目的地，唔係 DM，係一個你擁有嘅客戶資產，確保流量唔係全部留在 IG 手中。", 0, 70, 130)
    pdf.priority_row(4, "出頭30篇內容", "比例：40% 個人/教育內容，40% 客戶案例/social proof，20% 限時 offer/CTA。用 Gary Vee 嘅速度，唔完美都出。", 0, 70, 130)

    pdf.ln(2)
    pdf.set_text_color(0, 80, 40)
    pdf.multi_cell(0, 7, "下季度規劃")
    pdf.ln(1)
    pdf.priority_row(5, "渠道多元化評估", "根據頭90日嘅數據，決定係咪要同步開小紅書（美容線）或 YouTube（痛症線），唔好在未有數據前就分散資源，但要預備呢個擴展路徑。", 0, 100, 55)

    pdf.ln(8)
    pdf.set_fill_color(18, 18, 36)
    pdf.set_text_color(170, 170, 210)
    pdf.set_font("u", size=9)
    pdf.multi_cell(
        0, 7,
        "最後講一句：你嘅 idea 方向係對的，IG 引流係可行的，但「諗住試下」同「有策略地執行」係兩個完全唔同嘅遊戲。\n而家你有13個聲音幫你把「試下」變成「有策略」——用唔用，在你。",
        fill=True, align="C",
    )

    pdf.output(OUTPUT_PATH)
    print(f"PDF saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
