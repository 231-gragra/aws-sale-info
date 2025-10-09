from datetime import datetime, timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# タイムゾーン設定
try:
    TZ = ZoneInfo("Asia/Tokyo")
except Exception:
    TZ = timezone(timedelta(hours=9))  # フォールバック（JST固定）

# 現在時刻
NOW = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %Z")

# 出力ディレクトリ
DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# テンプレートファイルのパス
HEADER_PATH = Path("templates/header.md")
CONTENT1_PATH = Path("templates/content1.md")
FOOTER_PATH = Path("templates/footer.md")

# テンプレートファイルの内容を読み込む
header_content = HEADER_PATH.read_text(encoding="utf-8").replace("{NOW}", NOW) if HEADER_PATH.exists() else ""
content1_content = CONTENT1_PATH.read_text(encoding="utf-8") if CONTENT1_PATH.exists() else ""
footer_content = FOOTER_PATH.read_text(encoding="utf-8") if FOOTER_PATH.exists() else ""

final_content = f"{header_content}\n\n{content1_content}\n\n{footer_content}"
(DOCS_DIR / "index.md").write_text(final_content, encoding="utf-8")

with open(DOCS_DIR / "index.md", "a", encoding="utf-8") as f:
    f.write("\n<!-- Google tag (gtag.js) -->\n")
    f.write('<script async src="https://www.googletagmanager.com/gtag/js?id=G-K16BHGC520"></script>\n')
    f.write("<script>\n")
    f.write("window.dataLayer = window.dataLayer || [];\n")
    f.write("function gtag(){dataLayer.push(arguments);} \n")
    f.write("gtag('js', new Date());\n")
    f.write("gtag('config', 'G-K16BHGC520');\n")
    f.write("</script>\n")
print("docs/index.md を生成しました")