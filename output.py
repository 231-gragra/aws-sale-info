#!/usr/bin/env python3
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ---- JST（Asia/Tokyo）を安全に扱う：tzdataが無い環境でも動作 ----
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
    TZ = ZoneInfo("Asia/Tokyo")
except Exception:
    TZ = timezone(timedelta(hours=9))  # フォールバック（JST固定）

NOW = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %Z")

DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(parents=True, exist_ok=True)

content = f"""### 最終更新時刻（JST）
**{NOW}**

このページは自動生成・更新されています。  
更新タイミング: 毎日 04:00（JST）  
"""

(DOCS_DIR / "index.md").write_text(content, encoding="utf-8")
print("Wrote docs/index.md")

# templates/header.mdを読み込んでindex.mdの最初に追加
header_path = Path("templates/header.md")
if header_path.exists():
    header_content = header_path.read_text(encoding="utf-8")
    (DOCS_DIR / "index.md").write_text(header_content + "\n\n" + content, encoding="utf-8")
    print("header.mdの内容をindex.mdの最初に追加しました")