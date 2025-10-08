#!/usr/bin/env python3
"""
PAAPI 5.0 から検索キーワードで商品を検索し、HTML リストに整形して保存するスクリプト
必要パッケージ:
    pip install paapi5-python-sdk
使用方法:
    1. ACCESS_KEY / SECRET_KEY / PARTNER_TAG を書き換える。
    2. SEARCH_KEYWORD を任意の検索語に変更。
    3. python3 paapi_html_generator.py を実行すると items.html が生成されます。
"""
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
# プロジェクト直下をパスに追加
# sys.path.append(str(Path(__file__).resolve().parent.parent / "paapi5-python-sdk-example"))

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
            search_index="KindleStore",
            condition=Condition.NEW,
            item_count=ITEMS_PER_PAGE,
            item_page=page,
            resources=[
                    # BROWNODEINFOは現在と過去で使用されたセール情報が入っているが、どれが今も使われているのかが分からないため除外
                    # GetItemsResource.BROWSENODEINFO_BROWSENODES,
                    # GetItemsResource.BROWSENODEINFO_BROWSENODES_ANCESTOR, #親ジャンルの情報
                    # GetItemsResource.BROWSENODEINFO_BROWSENODES_SALESRANK,
                    # GetItemsResource.BROWSENODEINFO_WEBSITESALESRANK,
                    GetItemsResource.CUSTOMERREVIEWS_COUNT,
                    GetItemsResource.CUSTOMERREVIEWS_STARRATING,
                    # GetItemsResource.IMAGES_PRIMARY_SMALL,
                    GetItemsResource.IMAGES_PRIMARY_MEDIUM,
                    # GetItemsResource.IMAGES_PRIMARY_LARGE,
                    # GetItemsResource.IMAGES_VARIANTS_SMALL,
                    # GetItemsResource.IMAGES_VARIANTS_MEDIUM,
                    # GetItemsResource.IMAGES_VARIANTS_LARGE,
                    GetItemsResource.ITEMINFO_BYLINEINFO,
                    GetItemsResource.ITEMINFO_CONTENTINFO,
                    GetItemsResource.ITEMINFO_CONTENTRATING,
                    GetItemsResource.ITEMINFO_CLASSIFICATIONS,
                    GetItemsResource.ITEMINFO_EXTERNALIDS,
                    GetItemsResource.ITEMINFO_FEATURES,
                    GetItemsResource.ITEMINFO_MANUFACTUREINFO,
                    GetItemsResource.ITEMINFO_PRODUCTINFO,
                    GetItemsResource.ITEMINFO_TECHNICALINFO,
                    GetItemsResource.ITEMINFO_TITLE,
                    GetItemsResource.ITEMINFO_TRADEININFO,
                    GetItemsResource.OFFERS_LISTINGS_AVAILABILITY_MAXORDERQUANTITY,
                    GetItemsResource.OFFERS_LISTINGS_AVAILABILITY_MESSAGE,
                    GetItemsResource.OFFERS_LISTINGS_AVAILABILITY_MINORDERQUANTITY,
                    GetItemsResource.OFFERS_LISTINGS_AVAILABILITY_TYPE,
                    GetItemsResource.OFFERS_LISTINGS_CONDITION,
                    GetItemsResource.OFFERS_LISTINGS_CONDITION_CONDITIONNOTE,
                    GetItemsResource.OFFERS_LISTINGS_CONDITION_SUBCONDITION,
                    GetItemsResource.OFFERS_LISTINGS_DELIVERYINFO_ISAMAZONFULFILLED,
                    GetItemsResource.OFFERS_LISTINGS_DELIVERYINFO_ISFREESHIPPINGELIGIBLE,
                    GetItemsResource.OFFERS_LISTINGS_DELIVERYINFO_ISPRIMEELIGIBLE,
                    GetItemsResource.OFFERS_LISTINGS_DELIVERYINFO_SHIPPINGCHARGES,
                    GetItemsResource.OFFERS_LISTINGS_ISBUYBOXWINNER,
                    GetItemsResource.OFFERS_LISTINGS_LOYALTYPOINTS_POINTS,
                    GetItemsResource.OFFERS_LISTINGS_MERCHANTINFO,
                    GetItemsResource.OFFERS_LISTINGS_PRICE,
                    GetItemsResource.OFFERS_LISTINGS_PROGRAMELIGIBILITY_ISPRIMEEXCLUSIVE,
                    GetItemsResource.OFFERS_LISTINGS_PROGRAMELIGIBILITY_ISPRIMEPANTRY,
                    GetItemsResource.OFFERS_LISTINGS_PROMOTIONS,
                    GetItemsResource.OFFERS_LISTINGS_SAVINGBASIS,
                    GetItemsResource.OFFERS_SUMMARIES_HIGHESTPRICE,
                    GetItemsResource.OFFERS_SUMMARIES_LOWESTPRICE,
                    GetItemsResource.OFFERS_SUMMARIES_OFFERCOUNT,
                    GetItemsResource.PARENTASIN
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
        json_file_path = Path("jsons/item.json")
        json_file_path.parent.mkdir(parents=True, exist_ok=True)  # ディレクトリ作成
        if not json_file_path.exists():  # ファイルが存在しない場合
            json_file_path.write_text("[]", encoding="utf-8")  # 空のJSONファイルを作成

        with open("jsons/item.json","w",encoding="utf-8") as f:
            json.dump(items_dict, f, ensure_ascii=False, indent=2)
            print("item.json を更新しました。")

    except ApiException as e:
        print("PAAPI 呼び出しでエラーが発生しました:", e)


if __name__ == "__main__":
    main()
