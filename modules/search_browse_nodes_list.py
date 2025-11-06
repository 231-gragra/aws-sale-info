#!/usr/bin/env python3
import logging
import time
import json
import argparse
import os
import sys

from datetime import date, datetime
from decimal import Decimal
from dotenv import load_dotenv
from pathlib import Path
# PAAPI5 SDKをインポートできるようにパスを追加
sys.path.append(str(Path(__file__).resolve().parent.parent / "paapi5-python-sdk-example"))

from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models import (
    SearchItemsRequest,
    GetItemsResource,
    PartnerType,
    Condition,
)
from paapi5_python_sdk.rest import ApiException

# .envファイルを読み込む
load_dotenv()

# ===== 認証情報を設定してください =====
ACCESS_KEY = os.getenv("PAAPI_ACCESS_KEY")
SECRET_KEY = os.getenv("PAAPI_SECRET_KEY")
PARTNER_TAG = os.getenv("PAAPI_ASSOCIATE_TAG")  # 例：xxxxxx-22

# ===== 固定パラメータ =====
HOST = "webservices.amazon.co.jp"
REGION = "us-west-2"


# 検索ワードを指定
SEARCH_KEYWORD = "集英社"
ITEMS_PER_PAGE = 10  # API制限により1リクエスト最大10件
TOTAL_ITEMS = 10     # 取得したい総件数（10の倍数で）


def fetch_items():
    """PAAPI で複数ページにわたってアイテム情報を検索"""

    api = DefaultApi(ACCESS_KEY, SECRET_KEY, HOST, REGION)
    all_items = []

    for page in range(1, (TOTAL_ITEMS // ITEMS_PER_PAGE) + 1):
        request = SearchItemsRequest(
            partner_tag=PARTNER_TAG,
            partner_type=PartnerType.ASSOCIATES,
            marketplace="www.amazon.co.jp",
            keywords=SEARCH_KEYWORD,
            browse_node_id=None,#"210340181051",
            search_index="KindleStore",
            condition=Condition.NEW,
            item_count=ITEMS_PER_PAGE,
            item_page=page,
            # resourcesの各項目の設定リファレンス
            # https://webservices.amazon.com/paapi5/documentation/search-items.html
            resources=[
                    # BROWNODEINFOは現在と過去で使用されたセール情報が入っているが、どれが今も使われているのかが分からないため除外
                    # GetItemsResource.BROWSENODEINFO_BROWSENODES, #アイテムに関連付けられたブラウズノードを取得
                    # GetItemsResource.BROWSENODEINFO_BROWSENODES_ANCESTOR, #親ジャンルの情報
                    # GetItemsResource.BROWSENODEINFO_BROWSENODES_SALESRANK, #ジャンルのセールスランク
                    # GetItemsResource.BROWSENODEINFO_WEBSITESALESRANK, #アイテムに関連付けられたWebsiteSalesRank情報を取得
                    # GetItemsResource.CUSTOMERREVIEWS_COUNT, #カスタマーレビューの数
                    # GetItemsResource.CUSTOMERREVIEWS_STARRATING, #カスタマーレビューの星
                    # GetItemsResource.IMAGES_PRIMARY_SMALL, #画像小
                    GetItemsResource.IMAGES_PRIMARY_MEDIUM, #画像中
                    # GetItemsResource.IMAGES_PRIMARY_LARGE, #画像大
                    # GetItemsResource.IMAGES_VARIANTS_SMALL, #画像小
                    # GetItemsResource.IMAGES_VARIANTS_MEDIUM, #画像中
                    # GetItemsResource.IMAGES_VARIANTS_LARGE, #画像大
                    # GetItemsResource.ITEMINFO_BYLINEINFO, #著者情報
                    # GetItemsResource.ITEMINFO_CONTENTINFO, #販売言語とページ数と出版日
                    # GetItemsResource.ITEMINFO_CONTENTRATING, #コンテンツの適正年齢層
                    # GetItemsResource.ITEMINFO_CLASSIFICATIONS, #販売分類
                    # GetItemsResource.ITEMINFO_EXTERNALIDS, #特定の製品をグローバルに識別するために使用される識別子のセット
                    # GetItemsResource.ITEMINFO_FEATURES, #製品の主な機能に関する情報
                    # # GetItemsResource.ITEMINFO_MANUFACTUREINFO, #製品の製造関連情報
                    # GetItemsResource.ITEMINFO_PRODUCTINFO, #製品の非技術的な側面を表す属性セット
                    # GetItemsResource.ITEMINFO_TECHNICALINFO, #製品の技術的な側面を表す属性セット
                    GetItemsResource.ITEMINFO_TITLE, #製品のタイトル
                    # GetItemsResource.ITEMINFO_TRADEININFO, #アイテムの下取り情報
                    # GetItemsResource.OFFERS_LISTINGS_AVAILABILITY_MAXORDERQUANTITY, #商品の購入可能な最大数量
                    # GetItemsResource.OFFERS_LISTINGS_AVAILABILITY_MESSAGE, #商品の在庫状況メッセージ
                    # GetItemsResource.OFFERS_LISTINGS_AVAILABILITY_MINORDERQUANTITY, #商品の購入に必要な最小数量
                    # GetItemsResource.OFFERS_LISTINGS_AVAILABILITY_TYPE, #商品の在庫状況の種類
                    # GetItemsResource.OFFERS_LISTINGS_CONDITION, #商品の状態を返品
                    # GetItemsResource.OFFERS_LISTINGS_CONDITION_CONDITIONNOTE, #返品時の商品状態に関する注記（販売者が提供する商品状態）
                    # GetItemsResource.OFFERS_LISTINGS_CONDITION_SUBCONDITION, #商品のサブコンディション
                    # GetItemsResource.OFFERS_LISTINGS_DELIVERYINFO_ISAMAZONFULFILLED, #商品のオファーがAmazonによって発送されるかどうかを返す
                    # GetItemsResource.OFFERS_LISTINGS_DELIVERYINFO_ISFREESHIPPINGELIGIBLE, #商品のオファーが送料無料の対象となるかどうかを返す
                    # GetItemsResource.OFFERS_LISTINGS_DELIVERYINFO_ISPRIMEELIGIBLE, #商品のオファーがプライム対象かどうかを返す
                    # GetItemsResource.OFFERS_LISTINGS_DELIVERYINFO_SHIPPINGCHARGES, #謎
                    # GetItemsResource.OFFERS_LISTINGS_ISBUYBOXWINNER, #指定された商品のオファーが商品詳細ページで購入ボックス獲得者かどうかを返す
                    GetItemsResource.OFFERS_LISTINGS_LOYALTYPOINTS_POINTS, #ポイント還元率
                    # GetItemsResource.OFFERS_LISTINGS_MERCHANTINFO, #商品のオファーの販売者情報
                    GetItemsResource.OFFERS_LISTINGS_PRICE, #価格
                    # GetItemsResource.OFFERS_LISTINGS_PROGRAMELIGIBILITY_ISPRIMEEXCLUSIVE, #商品がプライム会員限定商品かどうか
                    # GetItemsResource.OFFERS_LISTINGS_PROGRAMELIGIBILITY_ISPRIMEPANTRY, #商品がプライムパントリープログラムに関連付けられているかどうか
                    # GetItemsResource.OFFERS_LISTINGS_PROMOTIONS, #商品の様々なプロモーションを返す
                    # GetItemsResource.OFFERS_LISTINGS_SAVINGBASIS, #特定の商品のオファーの取り消し線価格を返す
                    # GetItemsResource.OFFERS_SUMMARIES_HIGHESTPRICE, #特定の商品について、特定の条件で提示されたすべてのオファーの中で最高購入価格を返す
                    # GetItemsResource.OFFERS_SUMMARIES_LOWESTPRICE, #特定の商品について、特定の条件で提示されたすべてのオファーの中で最低購入価格を返す
                    # GetItemsResource.OFFERS_SUMMARIES_OFFERCOUNT, #特定の条件で指定された商品に対するオファーの総数を返す
                    GetItemsResource.PARENTASIN #指定された商品の親ASINを返します
            ],
        )
        time.sleep(5)

        try:
            response = api.search_items(request)
            if response.search_result and response.search_result.items:
                all_items.extend(response.search_result.items)
        except ApiException as e:
            print(f"ページ {page} の取得中にエラーが発生しました: {e}")

    return all_items

def to_plain(obj):
    """PA-APIのモデル → 素のdict/list/プリミティブへ再帰的に変換"""
    if hasattr(obj, "to_dict"):
        return {k: to_plain(v) for k, v in obj.to_dict().items()}
    if isinstance(obj, list):
        return [to_plain(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)  # 小数はfloatへ（必要ならstrでもOK）
    return obj

def main():
    try:
        items = fetch_items()
        items_dict = [to_plain(it) for it in items]
        # jsons/item.jsonがない場合は自動で作成
        json_file_path = Path("jsons/item1.json")
        json_file_path.parent.mkdir(parents=True, exist_ok=True)  # ディレクトリ作成
        if not json_file_path.exists():  # ファイルが存在しない場合
            json_file_path.write_text("[]", encoding="utf-8")  # 空のJSONファイルを作成

        with open("jsons/item1.json","w",encoding="utf-8") as f:
            json.dump(items_dict, f, ensure_ascii=False, indent=2)
            print("item1.json を更新しました。")

    except ApiException as e:
        print("PAAPI 呼び出しでエラーが発生しました:", e)


if __name__ == "__main__":
    main()
