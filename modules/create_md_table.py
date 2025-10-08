import json

# Markdownテンプレート
MD_TEMPLATE = """
# 商品一覧

| 商品画像 | タイトル | 価格 | 割引率 |
|----------|----------|------|--------|
{items}
"""

# JSONデータをMarkdownの表形式に変換する関数
def json_to_md_table(json_data):
    items_md = ""
    for item in json_data:
        image_url = item.get("images", {}).get("primary", {}).get("medium", {}).get("url", "")
        title = item.get("item_info", {}).get("title", {}).get("display_value", "N/A")
        detail_page_url = item.get("detail_page_url", "#")
        
        # 価格と割引率を取得
        price_info = item.get("offers", {}).get("listings", [{}])[0]
        amount = price_info.get("price", {}).get("amount", "N/A")
        loyalty_points = price_info.get("loyalty_points", {}).get("points", 0)
        if amount != "N/A" and loyalty_points > 0:
            discount_rate = int(round((loyalty_points / (amount)) * 100, 0))
        if amount != "N/A":
            price_display = int(amount)  # 数値型に変換して小数点以下を取り除く
        else:
            price_display = "N/A"

        items_md += f"| ![商品画像]({image_url}) | [{title}]({detail_page_url}) | {price_display}円 | 還元率{discount_rate}% ({loyalty_points}pt還元) |\n"
    return items_md

# メイン処理
def main():
    # JSONファイルを読み込む
    with open("jsons/item.json", "r", encoding="utf-8") as file:
        json_data = json.load(file)

    # Markdownの表を生成
    items_md = json_to_md_table(json_data)

    # Markdownファイルを生成
    md_content = MD_TEMPLATE.format(items=items_md)
    with open("templates/header.md", "w", encoding="utf-8") as file:
        file.write(md_content)

    print("header.md を更新しました。")

if __name__ == "__main__":
    main()