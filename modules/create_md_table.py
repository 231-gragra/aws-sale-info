import json
from pathlib import Path

# Markdownテンプレート
MD_TEMPLATE = """
# 商品還元率一覧

## 目次
{toc}

{low_price_books}

{discount_tables}
"""

# JSONデータをMarkdownのテーブル形式に変換する関数
def json_to_md_tables(json_data):
    # 割引率ごとに分類する辞書
    discount_categories = {f"{i*10}-{(i+1)*10-1}": [] for i in range(10)}
    discount_categories["100"] = []  # 100%還元用
    low_price_books = []  # 価格が100円未満の本を保存するリスト

    for item in json_data:
        title = item.get("item_info", {}).get("title", {}).get("display_value", "N/A")
        detail_page_url = item.get("detail_page_url", "#")
        
        # 価格と割引率を取得
        offers = item.get("offers") or {}
        listings = offers.get("listings") or [{}]
        price_info = listings[0] if listings else {}
        amount = (price_info.get("price") or {}).get("amount", "N/A")
        loyalty_points = (price_info.get("loyalty_points") or {} ).get("points", 0)
        
        if amount != "N/A" and loyalty_points > 0:
            discount_rate = int(round((loyalty_points / (amount)) * 100, 0))
        else:
            discount_rate = 0
        
        if amount != "N/A":
            price_display = int(amount)  # 数値型に変換して小数点以下を取り除く
        else:
            price_display = "N/A"

        # テーブル形式の行を作成（タイトル、値段、還元率の順）
        row = f"| [{title}]({detail_page_url}) | {price_display}円 | {discount_rate}% ({loyalty_points}pt) |"
        
        # 割引率に応じて適切なカテゴリーに追加
        if discount_rate == 100:
            discount_categories["100"].append(row)
        else:
            category_key = f"{(discount_rate // 10) * 10}-{((discount_rate // 10) + 1) * 10 - 1}"
            discount_categories[category_key].append(row)

        # 価格が100円未満の本をテーブル用に保存
        if amount != "N/A" and amount < 100:
            low_price_books.append(row)

    return discount_categories, low_price_books

# 割引率ごとのテーブルを生成する関数
def generate_md_tables(discount_categories):
    tables = []
    # カテゴリを降順にソート
    sorted_categories = sorted(discount_categories.keys(), key=lambda x: int(x.split("-")[0].replace("%", "")) if "-" in x else 100, reverse=True)
    for category in sorted_categories:
            rows = discount_categories[category]
            if rows:  # データがある場合のみテーブルを生成
                # 還元率でソート（降順）
                sorted_rows = sorted(rows, key=lambda row: int(row.split("|")[3].split("%")[0].strip()), reverse=True)
                # カテゴリごとのタイトルを追加
                table = f"## {category}％ 還元\n\n| タイトル | 価格 | 還元率 |\n|----------|------|--------|\n" + "\n".join(rows)
                tables.append(table)
    return "\n\n".join(tables)

# 目次を生成する関数
def generate_toc(discount_categories):
    toc = []
    toc.append("- [価格が100円未満の本](#価格が100円未満の本)")
    # カテゴリを降順にソート
    sorted_categories = sorted(discount_categories.keys(), key=lambda x: int(x.split("-")[0].replace("%", "")) if "-" in x else 100, reverse=True)
    for category in sorted_categories:
        rows = discount_categories[category]
        if rows:  # データがある場合のみテーブルを生成
            # アンカーリンク用のカテゴリ名を加工
            anchor_link = f"- [{category}% 還元](#{category}-還元)"
            toc.append(anchor_link)

    # 目次を生成
    toc_content = "\n".join(toc)
    toc_section = f"{toc_content}\n"

    # 目次を返す
    return toc_section

# 価格が100円未満の本のテーブルを生成する関数
def generate_low_price_table(low_price_books):
    if low_price_books:
        return "## 価格が100円未満の本\n\n| タイトル | 価格 | 還元率 |\n|----------|------|--------|\n" + "\n".join(low_price_books)
    return ""

# メイン処理
def main():
    import json

    # JSONデータを読み込む（例: ファイルから読み込む場合）
    with open("jsons/item.json", "r", encoding="utf-8") as file:
        json_data = json.load(file)

    # JSONデータを処理してカテゴリ別データと低価格データを取得
    discount_categories, low_price_books = json_to_md_tables(json_data)

    # ページ全体のタイトルと説明
    page_title = "# 商品還元率一覧\n\nこのページでは、還元率の高い商品をカテゴリ別に一覧表示しています。\n"

    # 目次を生成
    toc = generate_toc(discount_categories)

    # 割引率ごとのテーブルを生成
    discount_tables = generate_md_tables(discount_categories)

    # 価格が100円未満の本のテーブルを生成
    low_price_table = generate_low_price_table(low_price_books)

    # 結果を結合して出力
    result = f"{page_title}\n## 目次\n{toc}\n\n{low_price_table}\n\n{discount_tables}"

    # Markdownファイルを生成
    md_content = MD_TEMPLATE.format(toc=toc, discount_tables=discount_tables, low_price_books=low_price_table)
    output_file = Path("templates/content1.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(md_content, encoding="utf-8")

    print("templates/content1.md を更新しました。")

# 実行
if __name__ == "__main__":
    main()