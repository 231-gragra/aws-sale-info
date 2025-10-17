import os
import sys
import json
from dotenv import load_dotenv
from datetime import date, datetime
from pathlib import Path
from decimal import Decimal
# PAAPI5 SDKをインポートできるようにパスを追加
sys.path.append(str(Path(__file__).resolve().parent.parent / "paapi5-python-sdk-example"))
from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models.get_browse_nodes_request import GetBrowseNodesRequest
from paapi5_python_sdk.models.get_browse_nodes_resource import GetBrowseNodesResource
from paapi5_python_sdk.models.partner_type import PartnerType
from paapi5_python_sdk.rest import ApiException

# .envファイルを読み込む
load_dotenv()

# ===== 認証情報を設定してください =====
ACCESS_KEY = os.getenv("PAAPI_ACCESS_KEY")
SECRET_KEY = os.getenv("PAAPI_SECRET_KEY")
PARTNER_TAG = os.getenv("PAAPI_ASSOCIATE_TAG")
SEARCH_KINDLE_EVENT_ID = os.getenv("PAAPI_KINDLE_EVENT_ID")

def get_browse_nodes():
    host = "webservices.amazon.co.jp"
    region = "us-west-2"
    default_api = DefaultApi(
        access_key=ACCESS_KEY, secret_key=SECRET_KEY, host=host, region=region
    )
    browse_node_ids = [SEARCH_KINDLE_EVENT_ID]
    languages_of_preference = ["ja_JP"]
    get_browse_node_resources = [
        GetBrowseNodesResource.ANCESTOR,
        GetBrowseNodesResource.CHILDREN,
    ]
    try:
        get_browse_node_request = GetBrowseNodesRequest(
            partner_tag=PARTNER_TAG,
            partner_type=PartnerType.ASSOCIATES,
            marketplace="www.amazon.co.jp",
            languages_of_preference=languages_of_preference,
            browse_node_ids=browse_node_ids,
            resources=get_browse_node_resources,
            sort_by
        )
    except ValueError as exception:
        print("Error in forming GetBrowseNodesRequest: ", exception)
        return

    try:
        """ Sending request """
        response = default_api.get_browse_nodes(get_browse_node_request)
        if response.errors is not None:
            print("\nPrinting Errors:\nPrinting First Error Object from list of Errors")
            print("Error code", response.errors[0].code)
            print("Error message", response.errors[0].message)
        return response.browse_nodes_result.browse_nodes

    except ApiException as exception:
        print("Error calling PA-API 5.0!")
        print("Status code:", exception.status)
        print("Errors :", exception.body)
        print("Request ID:", exception.headers["x-amzn-RequestId"])

    except TypeError as exception:
        print("TypeError :", exception)

    except ValueError as exception:
        print("ValueError :", exception)

    except Exception as exception:
        print("Exception :", exception)
        
def parse_response(browse_nodes_response_list):
    mapped_response = {}
    for browse_node in browse_nodes_response_list:
        mapped_response[browse_node.id] = browse_node
    return mapped_response

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
        items = get_browse_nodes()
        items_dict = [to_plain(it) for it in items]
        # jsons/item.jsonがない場合は自動で作成
        json_file_path = Path("jsons/sale_list.json")
        json_file_path.parent.mkdir(parents=True, exist_ok=True)  # ディレクトリ作成
        if not json_file_path.exists():  # ファイルが存在しない場合
            json_file_path.write_text("[]", encoding="utf-8")  # 空のJSONファイルを作成

        with open("jsons/sale_list.json","w",encoding="utf-8") as f:
            json.dump(items_dict, f, ensure_ascii=False, indent=2)
            print("sale_list.json を更新しました。")

    except ApiException as e:
        print("PAAPI 呼び出しでエラーが発生しました:", e)


if __name__ == "__main__":
    main()