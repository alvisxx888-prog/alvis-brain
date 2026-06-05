"""
將 Stanley_IG主控台.html 所有本地圖片轉成 base64 內嵌，
生成一個可以直接上傳到任何網站的獨立 HTML 檔案。
"""
import re, base64, os

SRC  = "/Users/rickyc./Desktop/Vs code /Project 2 (Stanley)/Stanley_IG主控台.html"
OUT  = "/Users/rickyc./Desktop/Vs code /Project 2 (Stanley)/Stanley_IG主控台_網頁版.html"
BASE = "/Users/rickyc./Desktop/Vs code /Project 2 (Stanley)/"

with open(SRC, "r", encoding="utf-8") as f:
    html = f.read()

def encode_img(path):
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        print(f"  ⚠ 找不到: {path}")
        return None
    with open(full, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = path.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{data}"

# 找出所有 src="IG_Assets/..." 的圖片
pattern = re.compile(r'src="(IG_Assets/[^"]+)"')
found = pattern.findall(html)
unique = list(dict.fromkeys(found))
print(f"共找到 {len(unique)} 張圖片，開始轉換...")

for path in unique:
    encoded = encode_img(path)
    if encoded:
        html = html.replace(f'src="{path}"', f'src="{encoded}"')
        print(f"  ✓ {path}")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

size_mb = os.path.getsize(OUT) / 1024 / 1024
print(f"\n完成！輸出：{OUT}")
print(f"檔案大小：{size_mb:.1f} MB")
