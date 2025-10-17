import json
import re
import os
from pathlib import Path
from typing import List, Tuple
from dotenv import load_dotenv
# .envファイルを読み込む
load_dotenv()


# ====== 設定（必要に応じて変更）======
INPUT_JSON = "jsons/sale_list.json"
OUTPUT_MD = "templates/sale_list.md"
PARTNER_TAG = os.getenv("PAAPI_ASSOCIATE_TAG2")
SORT_KEY = "salesrank"
# =====================================

POINT_FILTERS = {
    "51%以上還元": "10476517051",
    "41%以上還元": "10476515051",
    "31%以上還元": "10476513051",
    "21%以上還元": "10476511051",
    "11%以上還元": "10476509051",
}

ASCII_ONLY = re.compile(r"^[ -~]+$")  # 半角ASCIIのみ

def md_escape(s: str) -> str:
    """
    Markdownのリンクテキスト内で表記崩れを起こしやすい記号をエスケープ。
    特に '|' はテーブル判定を誘発するため必ず '\\|' にします。
    """
    # 先にバックスラッシュ自体をエスケープ
    s = s.replace("\\", "\\\\")
    # 一般的に崩れやすい記号をエスケープ
    for ch in ["|", "[", "]", "(", ")", "*", "_", "`", "{", "}", "#", "+", "!", ">"]:
        s = s.replace(ch, "\\" + ch)
    # 連続スペースや末尾スペースは意図せず改行扱いになることがあるので整形（任意）
    return s.strip()

def is_ascii_only(text: str) -> bool:
    return bool(ASCII_ONLY.fullmatch(text))

def load_children_items(json_path: Path) -> List[Tuple[str, str]]:
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    items: List[Tuple[str, str]] = []
    if isinstance(data, list):
        for node in data:
            if not isinstance(node, dict):
                continue
            for ch in node.get("children", []):
                if not isinstance(ch, dict):
                    continue
                id_ = str(ch.get("id", "")).strip()
                name = str(ch.get("display_name", "")).strip()
                if not id_ or not name:
                    continue
                if is_ascii_only(name):  # 半角のみは除外
                    continue
                items.append((id_, name))

    # 重複除去（順序保持）
    seen = set()
    uniq: List[Tuple[str, str]] = []
    for pair in items:
        if pair not in seen:
            seen.add(pair)
            uniq.append(pair)
    # id を数値として降順
    uniq.sort(key=lambda x: int(x[0]), reverse=True)
    return uniq

def build_base_url(node_id: str) -> str:
    """カテゴリ（ノード）指定のKindle検索URLを生成。"""
    base = "https://www.amazon.co.jp/s"
    params = [f"i=digital-text", f"rh=n:{node_id}", f"tag={PARTNER_TAG}", f"s={SORT_KEY}"]
    return f"{base}?{'&'.join(params)}"

def build_points_url(node_id: str, points_code: str) -> str:
    """ポイント還元率フィルタ付きURLを生成。"""
    base = "https://www.amazon.co.jp/s"
    rh = f"n:{node_id},p_n_amazon_points_ratio:{points_code}"
    params = [f"i=digital-text", f"rh={rh}", f"tag={PARTNER_TAG}", f"s={SORT_KEY}"]
    return f"{base}?{'&'.join(params)}"

def main():
    input_path = Path(INPUT_JSON)
    output_path = Path(OUTPUT_MD)

    items = load_children_items(input_path)

    lines = ["## セールイベント一覧（Kindleストアリンク付き）", f"### 現在**{len(items)}件**のセールが開催されています  ","※セールによってはXX%以上の還元作品がなく検索エラーになる可能性があります。  "," その時は一番上のセールリンクから飛んでください。"]
    for node_id, name in items:
        safe_name = md_escape(name)
        base_url = build_base_url(node_id)
        parts = [f"- **[{safe_name}]({base_url})**"]
        lines.append(" ".join(parts))
        for label, code in POINT_FILTERS.items():
            lines.append(f"  - [{label}]({build_points_url(node_id, code)})")
        lines.append("")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(items)} 件のセールを {OUTPUT_MD} に出力しました。")

if __name__ == "__main__":
    main()
