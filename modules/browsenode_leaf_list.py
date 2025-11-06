# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import argparse
from dotenv import load_dotenv
from typing import List, Dict, Set, Tuple
from pathlib import Path
# PAAPI5 SDKをインポートできるようにパスを追加
sys.path.append(str(Path(__file__).resolve().parent.parent / "paapi5-python-sdk-example"))
from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models.get_browse_nodes_request import GetBrowseNodesRequest
from paapi5_python_sdk.models.get_browse_nodes_resource import GetBrowseNodesResource
from paapi5_python_sdk.models.partner_type import PartnerType
from paapi5_python_sdk import configuration as paapi_config
from paapi5_python_sdk.rest import ApiException

MAX_IDS_PER_REQUEST = 10
RESOURCES = [
    GetBrowseNodesResource.CHILDREN,
]

# .envファイルを読み込む
load_dotenv()

# ===== 認証情報を設定してください =====
ACCESS_KEY = os.getenv("PAAPI_ACCESS_KEY")
SECRET_KEY = os.getenv("PAAPI_SECRET_KEY")
PARTNER_TAG = os.getenv("PAAPI_ASSOCIATE_TAG2")

def chunked(seq: List[str], size: int):
    for i in range(0, len(seq), size):
        yield seq[i:i+size]

def get_children_and_meta(
    api: DefaultApi,
    ids: List[str],
    sleep_base: float = 5,
) -> Dict[str, Dict]:
    """
    各IDについて:
      - children（子ID一覧）
      - display_name / context_free_name
    を取り出して返す。存在しないIDは children=[] とする。
    429 の場合は指数バックオフ。
    """
    out: Dict[str, Dict] = {}
    for batch in chunked(ids, MAX_IDS_PER_REQUEST):
        print(f"Fetching BrowseNode IDs: {batch}")
        req = GetBrowseNodesRequest(
            browse_node_ids=batch,
            partner_tag=PARTNER_TAG,
            partner_type=PartnerType.ASSOCIATES,
            resources=RESOURCES,
        )

        backoff = 5.0
        while True:
            try:
                resp = api.get_browse_nodes(req)
                break
            except ApiException as e:
                # 自動リトライ（429）
                if e.status == 429:
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 16)
                    continue
                # その他は即時例外
                raise

        # まず全IDを空で用意しておく（応答に含まれないIDもケア）
        for nid in batch:
            out.setdefault(nid, {"children": [], "display_name": None, "context_free_name": None})

        nodes = (resp.browse_nodes_result and resp.browse_nodes_result.browse_nodes) or []
        for n in nodes:
            nid = n.id
            children_ids = [c.id for c in (n.children or [])]
            out[nid] = {
                "children": children_ids,
                "display_name": getattr(n, "display_name", None),
                "context_free_name": getattr(n, "context_free_name", None),
            }

        time.sleep(sleep_base)

    return out

def crawl_leaves(
    api: DefaultApi,
    start_ids: List[str],
    sleep_base: float = 0.2,
    max_visit: int = 50,
) -> Tuple[List[str], Dict[str, Dict]]:
    """
    幅優先で巡回し、children が空（null/[]想定）のノードを leaf として収集。
    戻り値: (leaf_id_list, meta_map)
    """
    to_visit: Set[str] = set(start_ids)
    visited: Set[str] = set()
    leaves: Set[str] = set()
    meta_map: Dict[str, Dict] = {}

    while to_visit:
        if len(visited) >= max_visit:
            break

        # 一度に処理する件数（リクエスト3回分程度）
        batch = list(to_visit)[: MAX_IDS_PER_REQUEST * 3]
        to_visit.difference_update(batch)

        cm = get_children_and_meta(api, batch, sleep_base=sleep_base)
        meta_map.update(cm)

        for nid, info in cm.items():
            visited.add(nid)
            children = info.get("children", []) or []
            if len(children) == 0:
                leaves.add(nid)
            else:
                for cid in children:
                    if cid not in visited:
                        to_visit.add(cid)

    return sorted(leaves), meta_map

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--with-meta", action="store_true", help="IDに display_name/context_free_name を付けて出力")
    p.add_argument("--out", default="", help="結果をJSON保存するパス（未指定なら標準出力）")
    p.add_argument("--sleep-base", type=float, default=5, help="リクエスト間スリープ秒（429対策の基本ウェイト）")
    p.add_argument("--max-visit", type=int, default=50, help="訪問上限ノード数（暴走防止）")
    args = p.parse_args()

    host = "webservices.amazon.co.jp"
    region = "us-west-2"
    default_api = DefaultApi(
        access_key=ACCESS_KEY, secret_key=SECRET_KEY, host=host, region=region
    )

    leaf_ids, meta_map = crawl_leaves(
        default_api,
        start_ids=["212921287051"],
        sleep_base=args.sleep_base,
        max_visit=args.max_visit,
    )

    if args.with_meta:
        # [{id, display_name, context_free_name}] で出力
        result = [
            {
                "id": nid,
                "display_name": meta_map.get(nid, {}).get("display_name"),
                "context_free_name": meta_map.get(nid, {}).get("context_free_name"),
            }
            for nid in leaf_ids
        ]
    else:
        result = leaf_ids

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Saved: {args.out}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
