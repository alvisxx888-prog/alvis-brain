from fpdf import FPDF

OUTPUT_PATH = "/Users/rickyc./Desktop/Vs code /Project 2 (Stanley)/Stanley_痛症IG_DreamTeam分析.pdf"
FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"

class PDF(FPDF):
    def header(self):
        self.set_font("U", "B", 9)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(27, 58, 107)
        self.cell(0, 8, "Stanley | Dream Team 終極作戰室 | 痛症 IG 方案評審", fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("U", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 6, f"第 {self.page_no()} 頁", align="C")

    def setup_fonts(self):
        self.add_font("U", "", FONT_PATH)
        self.add_font("U", "B", FONT_PATH)
        self.add_font("U", "I", FONT_PATH)

    def cover(self):
        self.set_fill_color(27, 58, 107)
        self.rect(0, 0, 210, 297, "F")
        self.set_y(50)
        self.set_font("U", "B", 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "Dream Team", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("U", "B", 16)
        self.set_text_color(42, 157, 143)
        self.cell(0, 10, "終極作戰室", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_font("U", "", 12)
        self.set_text_color(200, 215, 235)
        self.cell(0, 7, "痛症 IG 方案：夠唔夠好？點樣更有創意？", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(16)
        self.set_font("U", "B", 11)
        self.set_text_color(255, 255, 255)
        for line in ["8 位頂尖教練  x  5 個天才維度", "第一層：教練作戰室 | 第二層：天才審視", "終極裁決 + 行動優先級"]:
            self.cell(0, 8, line, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_y(250)
        self.set_font("U", "", 9)
        self.set_text_color(120, 150, 190)
        self.cell(0, 6, "生成日期：2026年5月 | Stanley 痛症方案顧問", align="C", new_x="LMARGIN", new_y="NEXT")

    def ch_title(self, t, bg=(27,58,107)):
        self.set_font("U", "B", 13)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(*bg)
        self.cell(0, 10, "  " + t, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def coach_header(self, emoji, name, subtitle):
        self.set_font("U", "B", 11)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(27, 58, 107)
        self.cell(0, 8, f"  {emoji}  {name}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_font("U", "I", 9)
        self.set_text_color(80, 100, 140)
        self.set_fill_color(235, 240, 252)
        self.cell(0, 6, f"  {subtitle}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def insight_bar(self, text):
        self.set_font("U", "B", 9)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(42, 157, 143)
        self.cell(0, 6, "  核心洞察：" + text, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text):
        self.set_font("U", "", 9)
        self.set_text_color(45, 45, 45)
        self.multi_cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def action_warn(self, action, warn):
        self.set_font("U", "B", 9)
        self.set_text_color(27, 58, 107)
        self.set_fill_color(235, 245, 255)
        self.multi_cell(0, 5, "  [要你做] " + action, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_font("U", "B", 9)
        self.set_text_color(160, 60, 0)
        self.set_fill_color(255, 245, 220)
        self.multi_cell(0, 5, "  [質疑你] " + warn, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def dim_header(self, emoji, name, subtitle):
        self.set_font("U", "B", 11)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(60, 100, 60)
        self.cell(0, 8, f"  {emoji}  {name}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_font("U", "I", 9)
        self.set_text_color(60, 100, 60)
        self.set_fill_color(235, 248, 235)
        self.cell(0, 6, f"  {subtitle}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def risk_box(self, text):
        self.set_font("U", "B", 9)
        self.set_text_color(140, 40, 0)
        self.set_fill_color(255, 240, 235)
        self.multi_cell(0, 5, "  [風險] " + text, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def verdict_box(self, title, items, bg=(235,240,255), title_color=(27,58,107)):
        self.set_font("U", "B", 10)
        self.set_text_color(*title_color)
        self.set_fill_color(*bg)
        self.cell(0, 7, "  " + title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_font("U", "", 9)
        self.set_text_color(40, 40, 40)
        for item in items:
            self.multi_cell(0, 5, "  " + item, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def priority_item(self, num, text, bg=(27,58,107)):
        self.set_font("U", "B", 10)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(*bg)
        self.cell(10, 7, f" {num}", fill=True)
        self.set_font("U", "", 9)
        self.set_text_color(40, 40, 40)
        self.set_fill_color(245, 247, 255)
        self.multi_cell(0, 7, " " + text, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def divider(self):
        self.set_draw_color(200, 210, 230)
        self.line(self.l_margin, self.get_y(), self.l_margin + 170, self.get_y())
        self.ln(3)


pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.setup_fonts()

# COVER
pdf.add_page()
pdf.cover()

# CONTEXT
pdf.add_page()
pdf.ch_title("問題與背景")
pdf.set_font("U", "B", 11)
pdf.set_text_color(27, 58, 107)
pdf.set_fill_color(235, 245, 255)
pdf.multi_cell(0, 7, "  問題：呢個痛症 IG 方案夠唔夠好？點樣令佢更有創意同更有效？", fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.ln(1)
pdf.set_font("U", "", 9)
pdf.set_text_color(60, 60, 60)
pdf.set_fill_color(248, 250, 255)
pdf.multi_cell(0, 5, "  背景：Stanley 剛完成30日 IG 內容計劃，但發現方案太依賴兩個競品帳號格式（hair.refresh_terrence + hk.mpm），缺乏原創性，想知道應該點改。", fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

pdf.set_font("U", "B", 10)
pdf.set_text_color(27, 58, 107)
pdf.cell(0, 6, "原有方案問題所在：", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("U", "", 9)
pdf.set_text_color(50, 50, 50)
for item in [
    "• 個案分享格式 = 直接照抄 hair.refresh_terrence，換成痛症主題",
    "• 留言換資料機制 = 同樣照抄，只換咗關鍵字",
    "• 節日帖 = 改良版 hk.mpm，但本質相同",
    "• 本質係「填色書」——框架係人哋嘅，只換咗顏色",
]:
    pdf.multi_cell(0, 5, item, new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)

# LAYER 1 TITLE
pdf.ch_title("第一層：教練作戰室   8位教練從各自專業框架出發")

# CARDONE
pdf.coach_header("", "Cardone", "銷售規模化 · 10X 行動量")
pdf.insight_bar("你係喺度研究創意，但你連第一條片都未拍——創意係行動嘅敵人。")
pdf.body("你話「唔想抄」，但你而家做緊嘅嘢係：坐喺度諗、討論、改計劃、再諗——一條片都冇出街。Terrence 嗰個帳號係因為佢拍咗380條片先搵到節奏，唔係因為佢第一條片就好有創意。你連起步線都未踩到，創唔創意根本唔重要。\n\n創意係執行之後嘅產物，唔係執行之前嘅條件。你需要嘅唔係一個更有創意嘅計劃——你需要係今日就開始拍。拍爛咗又點？重拍。第100條片一定比第1條片有創意。")
pdf.action_warn(
    "今日拍第一條60秒Reel，唔完美都好，今晚po出去。",
    "你用「唔夠創意」呢個藉口，係唔係其實係「驚人睇」？"
)

# HORMOZI
pdf.coach_header("", "Hormozi", "報價設計 · 商業模式數學")
pdf.insight_bar("整個方案有內容策略，但冇business model——你唔知道一個IG follower值幾多錢。")
pdf.body("我睇咗你成個計劃，由頭到尾都係「免費痛症諮詢」作為CTA。問題係：免費咩都唔值。你要問自己一條數學題——一個痛症客人嘅LTV（終身價值）係幾多？如果係$3,000，你願意用幾多錢/時間去換取一個lead？你嘅IG唔係藝術project，係lead generation machine。但而家你完全唔知道呢部機器嘅conversion rate係幾多。\n\n「創意」唔係你最大嘅問題——你最大嘅問題係冇一個清晰嘅offer。「免費諮詢」唔係offer，係commodity。你需要一個具體嘅入門offer：限時、有具體價值、有清晰下一步。例如「$X 30分鐘痛症方案評估，附送XXX報告」比「免費傾吓」更有吸引力，更容易成交。")
pdf.action_warn(
    "計算你嘅理想客人LTV，然後設計一個$200-500嘅入門offer，取代「免費諮詢」。",
    "你po咗30日帖之後，你預計會有幾多個付費客？你有冇一個數字？"
)

pdf.add_page()
# GARY VEE
pdf.coach_header("", "Gary Vee", "社交媒體 · 注意力經濟")
pdf.insight_bar("你喺度糾結「抄唔抄」，但真正嘅問題係你完全唔了解2026年嘅IG算法。")
pdf.body("聽住——冇人在乎你嘅格式係咪original。算法在乎嘅係：有冇人睇完你條片？有冇人save？有冇人share俾朋友？你嘅計劃入面，每條Reel都係「坐定定講野」——呢種格式喺2022年得，2026年觀眾早就睇厭咗。你需要pattern interrupt——頭3秒要令人完全冇預期，先有機會留住人。\n\n仲有，你個計劃完全冇提TikTok同YouTube Shorts。痛症內容喺YouTube嘅搜尋量係IG嘅幾十倍——「坐骨神經痛點解」「膝蓋痛點算」呢類搜尋每日有幾千次，但你完全唔做search-based content，只做feed-based content。你係喺最細嘅池塘釣魚。")
pdf.action_warn(
    "每條Reel前3秒要有一個視覺hook——唔係講野，係一個畫面令人停止滑動。同時開TikTok帳號，相同內容cross-post。",
    "你上次睇自己條片睇到完係幾時？你自己都唔會睇完，點解別人會？"
)

# RUSSELL
pdf.coach_header("", "Russell Brunson", "銷售漏斗 · 故事銷售")
pdf.insight_bar("你有traffic strategy，但冇funnel——人哋睇完你條片，然後呢？")
pdf.body("你成個30日計劃，本質上係一個content calendar。但content calendar唔係business。一個完整嘅漏斗係：陌生人→follower→lead→客戶→回頭客→推薦人。你嘅計劃只解決咗「陌生人→follower」呢一步，其餘所有步驟都係靠「DM我」一句話搞掂——呢個唔係漏斗，係一個希望。\n\n你需要嘅係一個「value ladder」。最低層係免費內容（你而家做緊）；下一層係一個低門檻paid產品（$100-300嘅資訊產品或評估）；再上一層係你嘅主要服務；最頂係VIP或長期跟進。冇呢個ladder，你所有IG努力都係在幫人增加知識，但唔係在建立你嘅business。")
pdf.action_warn(
    "設計一個三頁landing page：1)痛症自我評估quiz，2)結果頁+低門檻offer，3)感謝頁+預約。然後把所有IG CTA指向呢個page。",
    "你嘅IG link in bio而家係去邊？如果係去你WhatsApp，你係在浪費所有流量。"
)

pdf.add_page()
# DAN KENNEDY
pdf.coach_header("", "Dan Kennedy", "直接回應行銷 · 文案")
pdf.insight_bar("「18-65歲有痛症需求」唔係target market，係香港成年人口。")
pdf.body("你嘅計劃最根本嘅問題唔係創意，係定位太闊。Terrence成功，係因為佢明確係做「頭皮問題嘅打工仔同健身男」——佢嘅每一條片都係對住一個具體人說話。你嘅計劃想服務頸痛、膝痛、腰痛、運動創傷、中年女士、年輕健身族——你係想捉住所有人，結果係捉唔住任何人。\n\n直接回應行銷最基本嘅原則：一個message，一個audience，一個action。你要問自己——如果我只能服務一種人，係邊種？邊種人最有錢？邊種人最痛？邊種人最願意付錢解決問題？答案就係你嘅target。其他人係bonus，唔係target。")
pdf.action_warn(
    "揀一個主力客群（建議：35-55歲，有慢性痛症，試過多種方法失敗），所有內容只對呢個人說話，唔理其他人。",
    "你上一個付費客係邊種人？係咪你真正嘅target？"
)

# BELFORT
pdf.coach_header("", "Belfort", "說服力 · 成交科學")
pdf.insight_bar("你嘅IG會產生leads，但你冇一個系統把leads變成錢。")
pdf.body("我拆解一下你嘅sales cycle：有人睇咗你條片→覺得有用→DM你→你點回覆？你有冇一套script？定係每次都係improvise？如果係後者，你係在把marketing budget（時間）浪費喺一個漏水嘅桶。用「三個十」嘅框架睇：客人需要對你嘅產品有信心、對你呢個人有信心、對採取行動有信心。你嘅IG內容只建立咗前兩個，但第三個——「為咩要而家做」——幾乎冇處理。\n\n你需要一個DM接待腳本，分三步：首先搞清楚佢嘅具體情況（問問題，唔好一開始就介紹服務）；然後建立urgency（為咩等落去會更差）；最後提供一個清晰嘅next step（唔係「係咁先」）。")
pdf.action_warn(
    "寫一個10步DM轉化腳本，由第一個回覆到預約，每一步都有標準說話。",
    "你上次有人DM你，最後有幾多個真係成為客戶？轉化率係幾多？"
)

pdf.add_page()
# SETH
pdf.coach_header("", "Seth Godin", "品牌定位 · 部落建立")
pdf.insight_bar("你係因為睇住競品先設計自己——呢個係跟隨者嘅思維，唔係領導者嘅思維。")
pdf.body("整個計劃嘅出發點係：「Terrence做得好，hk.mpm做咩，我點樣混合」。但市場唔需要另一個Terrence，市場需要嘅係一個只有你才能做嘅嘢。你嘅「痛症方案銷售員」身份，其實係一個完全未被佔領嘅位置——但呢個位置嘅力量，唔係來自借用別人嘅格式，而係來自你自己最真實、最獨特嘅觀點。問你自己一條問題：關於痛症，有咩嘢係只有你知、但你從來唔敢公開講嘅？\n\n最小可行受眾嘅概念係：你唔需要100萬人認識你，你需要1,000個真正在乎你講嘅嘢嘅人。但要找到呢1,000人，你要先有一個「只有你才會講」嘅觀點。「局內人說話」係你提到嘅原創概念——呢個方向係對的，但你冇把佢做成你整個帳號嘅核心哲學，只係其中一條系列。")
pdf.action_warn(
    "寫低一句話——「我相信痛症行業入面，有一件事係人人知但冇人敢講嘅，就係___」。呢句話就係你整個品牌嘅核心。",
    "如果你唔做呢個IG，世界係咪少咗咩？如果答案係「冇分別」，你嘅定位就未夠清晰。"
)

# TONY
pdf.coach_header("", "Tony Robbins", "巔峰心理 · 狀態管理")
pdf.insight_bar("「唔想抄」背後係一個更深嘅恐懼——你唔係怕唔creative，你係怕被人judge。")
pdf.body("我做咗幾十年，我見過無數人用「計劃唔夠好」呢個藉口delay行動。但係我要問你：如果你知道一定唔會失敗，你今日會做咩？你嘅答案——那個毫無顧慮嘅版本——就係你真正想做嘅事。你有「局內人說話」呢個概念，你有「香港痛症地圖」呢個idea，你有「痛症性格類型」呢個創意——但你依然喺度等。係咪因為你覺得自己「唔夠資格」做呢個創意版本？\n\n你嘅限制性信念係：「我係個銷售員，冇資格做original content creator。」但係你見過幾百個痛症個案，你係行業局內人，你係香港人，你有自己嘅故事——呢啲全部係資格。問題唔係你有冇料，問題係你係咪願意vulnerable，願意先做後完美。")
pdf.action_warn(
    "每日早上問自己：「今日我願意俾人睇到真實嘅我嗎？」如果答案係yes，就係拍片嘅日子。",
    "你真正嘅恐懼係咩——唔係「唔夠創意」，係咩令你真係猶豫？"
)

# LAYER 2
pdf.add_page()
pdf.ch_title("第二層：天才維度審視   對教練集體智慧做更高層嘅拆解", bg=(40,90,40))

# WISDOM
pdf.dim_header("", "智者維度", "從最深嘅智慧和歷史規律審視教練們嘅建議")
pdf.insight_bar("教練們合在一起，最深層嘅智慧係：信任係唯一嘅貨幣，而信任唔係靠格式建立嘅，係靠一致性建立嘅。")
pdf.body("Cardone話行動，Hormozi話offer，Gary Vee話格式，Russell話漏斗，Kennedy話定位，Belfort話成交，Seth話哲學，Tony話心理——每個人都講一個「缺失」嘅部分。但喺更高維度睇，所有呢些建議嘅前提係一樣嘅：你要成為一個人們願意信任嘅存在。而信任只有一種建法——時間 x 一致性 x 真實性。\n\n歷史上所有持久嘅個人品牌有一個共同點：佢哋有一個清晰嘅「我相信」聲明，然後用一生嘅行動去印證呢個聲明。Stanley而家最缺乏嘅，唔係創意，唔係offer，係一句「我相信痛症嘅XXXXX」——然後所有內容都係呢個信念嘅延伸。")
pdf.set_font("U", "B", 9)
pdf.set_text_color(40, 90, 40)
pdf.cell(0, 5, "  行動建議：", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("U", "", 9)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 5, "  寫低你對痛症行業嘅三個最深信念，然後把呢三個信念變成你帳號嘅骨架", new_x="LMARGIN", new_y="NEXT")
pdf.risk_box("如果你只係追求「格式有創意」但冇核心信念，你嘅帳號會係一個好睇但冇靈魂嘅殼——人哋會follow但唔會買。")

# CHALLENGER
pdf.dim_header("", "挑戰者維度", "質疑教練們嘅假設，包括挑戰教練本身嘅盲點")
pdf.insight_bar("8位教練全部假設「IG引流 = 業務增長」，但呢個邏輯鏈對一個痛症銷售員係咪成立，從來冇人問過。")
pdf.body("教練們嘅建議係為美國市場、英語市場設計嘅，成個框架假設你係直接賣服務俾消費者（B2C）。但Stanley係「銷售員」——你代理某些品牌或服務，你嘅客人係最終消費者，但你嘅生意可能依賴更多係B2B關係（診所、中心、合作夥伴）。如果係咁，你花幾個月做IG引流消費者，但你嘅業務增長其實係靠搵到更多合作診所——呢個係完全不同嘅策略，IG根本就係錯嘅渠道。\n\n仲有，Hormozi話「設計清晰offer」，Russell話「建立sales funnel」，呢啲全部假設Stanley係可以直接成交嘅。但作為銷售員，你嘅成交依賴你代理嘅中心願唔願意接受你引過嚟嘅客——你有冇問過你嘅合作中心，佢哋係咪願意用一個特定offer去接收IG lead？")
pdf.set_font("U", "B", 9)
pdf.set_text_color(40, 90, 40)
pdf.cell(0, 5, "  行動建議：", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("U", "", 9)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 5, "  先問清楚：你嘅業務增長，主要係靠「直接搵到消費者」定係「搵到更多合作診所/中心」？唔同答案，完全唔同嘅IG策略", new_x="LMARGIN", new_y="NEXT")
pdf.risk_box("如果你嘅business model係靠診所合作，你喺IG做消費者教育可能係在幫競爭對手建立客源，而唔係幫自己。")

pdf.add_page()
# EMPATHY
pdf.dim_header("", "同理者維度", "從人嘅感受、關係、情感因素審視")
pdf.insight_bar("教練們設計咗一個完美嘅內容機器，但完全忽略咗一件事——痛係最私人嘅人類體驗之一。")
pdf.body("痛唔係一個資訊問題，係一個情感問題。一個長期有腰痛嘅人，佢嘅真實內心話唔係「我需要了解衝擊波治療原理」，係「我好攰，我試過好多方法都失敗，我開始唔信任任何人」。現有計劃嘅所有內容都係資訊層面——教育、個案、比較——但幾乎冇一條內容係直接對住呢種「我好攰、好絕望」嘅情緒說話。而呢種情緒，先係令人願意採取行動嘅真正驅動力。\n\nTerrence有一條「WHO AM I」帖係佢第二高互動，唔係因為資訊有用，係因為人哋感受到佢嘅真實。Stanley嘅計劃裡面，最欠缺嘅係Stanley自己嘅情感。你為咩入行？你有冇自己試過痛症？你有冇幫過一個令你真正感動嘅個案？呢啲嘢比任何教育內容都更有力量。")
pdf.set_font("U", "B", 9)
pdf.set_text_color(40, 90, 40)
pdf.cell(0, 5, "  行動建議：", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("U", "", 9)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 5, "  喺30日計劃入面加至少兩條「情感共鳴」內容——唔係教育，係你自己嘅真實感受同經歷", new_x="LMARGIN", new_y="NEXT")
pdf.risk_box("一個只有資訊、冇情感嘅帳號，會吸引到想學知識嘅人，但唔會吸引到願意付錢嘅人。後者要嘅係信任，信任來自情感連結，唔係資訊量。")

# PROPHET
pdf.dim_header("", "預言者維度", "從10年後回望今日嘅決定")
pdf.insight_bar("10年後，你而家計劃做嘅所有教育內容，全部都會被AI做得比你更好、更快、更免費——你嘅護城河唔可以係資訊。")
pdf.body("Terrence嘅「蛋白質對頭髮嘅影響」——呢種資訊2030年係ChatGPT一秒答到，比任何KOL都詳細。hk.mpm嘅療法介紹——AI已經可以做得比佢更好。Stanley而家計劃入面嘅「熱敷vs凍敷」「止痛藥謬誤」「衝擊波原理」——呢啲全部係knowledge-based content，全部都會被AI取代。教練們——特別係Gary Vee同Kennedy——嘅建議係為一個pre-AI世界設計嘅。\n\n但有一樣嘢AI永遠取代唔到：你同一個真實人之間建立嘅關係同信任。10年後仍然成立嘅唯一護城河係：人哋唔係因為你有知識而選擇你，係因為佢哋信任你呢個人。「局內人說話」系列值得做，唔係因為資訊，係因為佢展示咗一個只有Stanley才有嘅真實視角——呢個係AI複製唔到嘅。")
pdf.set_font("U", "B", 9)
pdf.set_text_color(40, 90, 40)
pdf.cell(0, 5, "  行動建議：", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("U", "", 9)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 5, "  把內容策略從「教育人」轉向「建立關係」——更多你嘅真實觀點，更少generic嘅痛症知識", new_x="LMARGIN", new_y="NEXT")
pdf.risk_box("今日花最多時間做嘅「教育型內容」，係10年後最快被淘汰嘅內容。今日花時間建立嘅「真實關係」，係唯一長期資產。")

# OUTSIDER
pdf.dim_header("", "局外者維度（電影導演視角）", "Christopher Nolan 式思維框架")
pdf.insight_bar("所有教練都喺度討論「內容」，但冇人問最基本嘅問題——Stanley係主角還是旁白？")
pdf.body("一部好電影嘅力量來自主角嘅transformation journey。觀眾跟住睇唔係因為主角知道最多——係因為主角有最真實嘅衝突、成長、同轉變。而家嘅計劃把Stanley定位為「有知識的顧問」——一個旁白角色，站在旁邊解說。但最compelling嘅narrative係把Stanley變成主角：一個有自己痛點、自己懷疑、自己突破嘅人。\n\n電影導演話：「Show, don't tell.」你嘅30日計劃入面，幾乎全部係tell（我教你、我分享、我解釋）。但最viral嘅內容係show——帶人睇你嘅真實工作日、一個客人從第一次諮詢到康復嘅完整旅程（得到同意）、你自己試一種新療法嘅反應。呢種「紀錄片式」內容係兩個競品完全冇做、係AI永遠複製唔到、係觀眾最難停止睇下去嘅格式。")
pdf.set_font("U", "B", 9)
pdf.set_text_color(40, 90, 40)
pdf.cell(0, 5, "  行動建議：", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("U", "", 9)
pdf.set_text_color(50, 50, 50)
pdf.multi_cell(0, 5, "  設計一條「跟拍系列」：用4-6條Reels記錄一個真實客人（匿名）嘅完整痛症旅程，由第一次諮詢到見效", new_x="LMARGIN", new_y="NEXT")
pdf.risk_box("如果呢個故事講唔好——中途斷片、客人唔配合——反而損害信任。需要先揀一個「結局已知係好」嘅個案先開始拍。")

# VERDICT
pdf.add_page()
pdf.ch_title("終極裁決", bg=(120, 30, 30))

pdf.set_font("U", "B", 10)
pdf.set_text_color(120, 30, 30)
pdf.set_fill_color(255, 240, 240)
pdf.multi_cell(0, 6, "  第一層 x 第二層 交叉發現", fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.body("教練們幾乎一致話「立即行動」，但天才維度發現咗一個更深嘅問題——你連自己嘅business model係咪B2C都未搞清楚。如果你嘅業務增長係靠診所合作而唔係直接消費者，整個IG策略可能係建喺錯誤嘅前提上。呢個問題必須先答，其他所有建議才有意義。")

pdf.verdict_box("所有聲音一致同意：", [
    "1. 而家嘅計劃太依賴競品格式，真正原創嘅部分係「局內人視角」，呢個必須做成核心而唔係旁枝",
    "2. 「免費諮詢」作為唯一CTA係太弱，需要一個更清晰嘅next step同monetization路徑",
    "3. 資訊型內容嘅護城河越來越低，關係同信任先係長期資產",
], bg=(240, 248, 240), title_color=(30, 100, 30))

pdf.verdict_box("最重要嘅分歧：", [
    "Cardone vs Seth Godin：Cardone話立即行動；Seth話冇清晰定位就係浪費精力。",
    "Stanley取捨：先用Cardone嘅邏輯開始拍，同時用Seth嘅框架喺拍嘅過程中找到自己嘅聲音。唔好等完美先開始，但要帶住問題去行動。",
    "",
    "Kennedy vs Tony Robbins：Kennedy話揀窄target；Tony話任何人都有潛力服務。",
    "Stanley取捨：先揀一個主力客群開始，但唔好因此拒絕其他人，讓數據告訴你邊個客群最有反應。",
], bg=(255, 248, 230), title_color=(140, 80, 0))

pdf.set_font("U", "B", 11)
pdf.set_text_color(255, 255, 255)
pdf.set_fill_color(27, 58, 107)
pdf.cell(0, 8, "  Stanley 嘅行動優先級", fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)

pdf.set_font("U", "B", 9)
pdf.set_text_color(27, 58, 107)
pdf.cell(0, 6, "  本週立即做：", new_x="LMARGIN", new_y="NEXT")
pdf.priority_item("1", "答一條問題：你嘅業務增長，主要係靠消費者直接搵你（B2C），定係靠診所/中心合作（B2B）？答案決定整個IG策略嘅根本方向", bg=(27,58,107))
pdf.priority_item("2", "拍第一條片：唔完美都好，今晚出街——Cardone係對嘅，行動比計劃重要", bg=(27,58,107))

pdf.set_font("U", "B", 9)
pdf.set_text_color(42, 157, 143)
pdf.cell(0, 6, "  本月完成：", new_x="LMARGIN", new_y="NEXT")
pdf.priority_item("3", "寫你嘅「我相信」聲明：關於痛症行業，有一件你敢講但業界人唔敢講嘅事——呢句話係你整個品牌嘅核心", bg=(42,157,143))
pdf.priority_item("4", "設計一個具體入門offer：取代「免費諮詢」，要有具體內容、具體價值、具體價格（$200-500範圍）", bg=(42,157,143))

pdf.set_font("U", "B", 9)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 6, "  下季度規劃：", new_x="LMARGIN", new_y="NEXT")
pdf.priority_item("5", "開拍「跟拍系列」：揀一個結果已知嘅客人，用4-6條Reels記錄完整旅程——呢個係你最original、最有競爭壁壘嘅內容，冇人可以抄走", bg=(80,80,80))

pdf.ln(4)
pdf.set_font("U", "", 9)
pdf.set_text_color(120, 120, 120)
pdf.cell(0, 5, "Dream Team 終極作戰室 | Stanley 痛症 IG 方案評審 | 2026年5月", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.output(OUTPUT_PATH)
print(f"Done: {OUTPUT_PATH}")
