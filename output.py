#!/usr/bin/env python3
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

content = f"""# 現在時刻（JST）
**{NOW}**

このページは GitHub Actions により自動生成・更新されています。
- 更新タイミング: 毎日 09:00（JST）
- 生成元: `.github/workflows/daily-pages.yml`
"""

(DOCS_DIR / "index.md").write_text(content, encoding="utf-8")
print("Wrote docs/index.md")
