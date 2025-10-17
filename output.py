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
SALE_LIST_PATH = Path("templates/sale_list.md")
FOOTER_PATH = Path("templates/footer.md")

# テンプレートファイルの内容を読み込む
header_content = HEADER_PATH.read_text(encoding="utf-8").replace("{NOW}", NOW) if HEADER_PATH.exists() else ""
content1_content = CONTENT1_PATH.read_text(encoding="utf-8") if CONTENT1_PATH.exists() else ""
sale_list_content = SALE_LIST_PATH.read_text(encoding="utf-8") if SALE_LIST_PATH.exists() else ""
footer_content = FOOTER_PATH.read_text(encoding="utf-8") if FOOTER_PATH.exists() else ""

final_content = f"{header_content}\n\n{content1_content}\n\n{footer_content}"
(DOCS_DIR / "index.md").write_text(final_content, encoding="utf-8")

final_content = f"{header_content}\n\n{sale_list_content}\n\n{footer_content}"
(DOCS_DIR / "sale_list.md").write_text(final_content, encoding="utf-8")

print("docs/index.mdとdocs/sale_list.md を生成しました")