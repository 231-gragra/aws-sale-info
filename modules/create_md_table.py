import json
from pathlib import Path

# Markdownテンプレート
MD_TEMPLATE = """
# 商品還元率一覧

このページでは、還元率の高い商品をカテゴリ別に一覧表示しています。

{lists}
"""

# JSONデータをMarkdownのリスト形式に変換する関数
def json_to_md_lists(json_data):
    # 割引率ごとに分類する辞書
    discount_categories = {f"{i*10}-{(i+1)*10-1}%": [] for i in range(10)}
    discount_categories["100%"] = []  # 100%還元用

    for item in json_data:
        title = item.get("item_info", {}).get("title", {}).get("display_value", "N/A")
        detail_page_url = item.get("detail_page_url", "#")
        
        # 価格と割引率を取得
        price_info = item.get("offers", {}).get("listings", [{}])[0]
        amount = price_info.get("price", {}).get("amount", "N/A")
        loyalty_points = price_info.get("loyalty_points", {}).get("points", 0)
        
        if amount != "N/A" and loyalty_points > 0:
            discount_rate = int(round((loyalty_points / (amount)) * 100, 0))
        else:
            discount_rate = 0
        
        if amount != "N/A":
            price_display = int(amount)  # 数値型に変換して小数点以下を取り除く
        else:
            price_display = "N/A"

        # リスト形式の行を作成
        row = f"- [{title}]({detail_page_url}): {price_display}円, 還元率{discount_rate}% ({loyalty_points}pt)"
        
        # 割引率に応じて適切なカテゴリーに追加
        if discount_rate == 100:
            discount_categories["100%"].append(row)
        else:
            category_key = f"{(discount_rate // 10) * 10}-{((discount_rate // 10) + 1) * 10 - 1}%"
            discount_categories[category_key].append(row)

    return discount_categories

# メイン処理
def main():
    # JSONファイルを読み込む
    with open("jsons/item.json", "r", encoding="utf-8") as file:
        json_data = json.load(file)

    # 割引率ごとのリストを生成
    discount_categories = json_to_md_lists(json_data)

    # 各カテゴリーのリストをMarkdownに整形
    lists = ""
    for category, rows in sorted(discount_categories.items(), reverse=True):  # 高い還元率から順に処理
        if rows:  # データがある場合のみ出力
            lists += f"## {category} 還元\n"
            lists += "\n".join(rows) + "\n\n"

    # Markdownファイルを生成
    md_content = MD_TEMPLATE.format(lists=lists)
    output_file = Path("templates/header.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(md_content, encoding="utf-8")

    print("templates/header.md を更新しました。")

# 実行
if __name__ == "__main__":
    main()