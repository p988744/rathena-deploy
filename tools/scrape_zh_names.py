#!/usr/bin/env python3
"""
scrape_zh_names.py — 從 rd.fharr.com 抓取 twRO 繁體中文道具名稱
輸出：tools/output/zh_item_names.tsv（item_id\t中文名稱）

用法：
    pip install requests
    python3 tools/scrape_zh_names.py
"""

import re
import time
import json
import os
import requests

BASE_URL = "https://rd.fharr.com/db/itemlist"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
DELAY = 1.0        # 每次請求間隔秒數
RETRY_DELAY = 30   # 遭遇 rate limit 時等待秒數
MAX_RETRIES = 3    # 每個請求最多重試次數
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "zh_item_names.tsv")

# 優先抓取裝備、卡片（對玩家最重要），再抓消耗品與雜物
# 裝備 → 卡片 → 飾品影子裝備 → 消耗品 → 雜貨
NTYPES = [
    # 近距武器
    101, 102, 103, 104, 105, 106, 107, 108,
    110, 111, 112, 113, 114, 115, 116,
    117, 118, 119, 120, 121, 122, 123, 131,
    # 防具上半/下半
    201, 202, 203, 204, 205, 206, 207,
    208, 211, 212, 213, 214, 215, 216,
    # 飾品
    221, 222, 223, 224, 225, 226, 227, 229,
    # 影子裝備
    231, 232, 233, 234, 235, 236,
    # 卡片
    301, 302, 303, 304, 305, 306, 307, 308, 309, 351,
    # 其他裝備/道具
    401, 402, 403, 404, 405, 406, 407, 408, 409,
    # 消耗品/雜貨（nType=1 頁數最多，放最後）
    2, 3, 7, 8, 11, 18, 19, 20, 21, 22, 1,
]

ITEM_PATTERN = re.compile(
    r'<h4 class="mb-1 mt-3"><a href="https://rd\.fharr\.com/db/item/(\d+)/">([^<]+)</a></h4>'
)


def fetch_page(url: str):
    """抓取一頁，遇到 rate limit 自動等待重試，失敗回傳 None"""
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 429:
                wait = RETRY_DELAY * (attempt + 1)
                print(f"  ⏳ Rate limited，等待 {wait}s...", flush=True)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"  ⚠ 請求失敗 (attempt {attempt+1}/{MAX_RETRIES}): {e}", flush=True)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return None


def scrape_type(ntype: int) -> dict[int, str]:
    """抓取某個 nType 的所有頁面，回傳 {id: 中文名稱}"""
    result = {}
    page = 1
    consecutive_empty = 0

    while True:
        url = f"{BASE_URL}?nType={ntype}&page={page}"
        html = fetch_page(url)

        if html is None:
            print(f"  ✗ nType={ntype} page={page} 連線失敗，跳過", flush=True)
            break

        items = ITEM_PATTERN.findall(html)

        if not items:
            consecutive_empty += 1
            if consecutive_empty >= 2:
                break  # 連續兩頁空白 → 真的沒有更多資料
            # 第一頁空白可能是暫時 rate limit，休息後重試
            if page == 1:
                print(f"  ⚠ nType={ntype} 第一頁無資料，跳過", flush=True)
                break
        else:
            consecutive_empty = 0
            for item_id, name in items:
                result[int(item_id)] = name

        print(f"  nType={ntype:3d} page={page:4d} → {len(items)} 筆（累計 {len(result)} 筆）", flush=True)
        page += 1
        time.sleep(DELAY)

    return result


def load_existing() -> dict[int, str]:
    """讀取已有的輸出檔，方便斷點續抓"""
    existing = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            next(f, None)  # 跳過 header
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) == 2:
                    try:
                        existing[int(parts[0])] = parts[1]
                    except ValueError:
                        pass
        print(f"📂 載入已有資料 {len(existing)} 筆", flush=True)
    return existing


def save(all_items: dict[int, str]):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("item_id\tzh_name\n")
        for item_id in sorted(all_items):
            f.write(f"{item_id}\t{all_items[item_id]}\n")

    json_file = OUTPUT_FILE.replace(".tsv", ".json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"💾 已儲存 {len(all_items)} 筆 → {OUTPUT_FILE}", flush=True)


def main():
    all_items = load_existing()

    print(f"開始抓取 {len(NTYPES)} 種道具分類（delay={DELAY}s）...")
    for ntype in NTYPES:
        items = scrape_type(ntype)
        before = len(all_items)
        all_items.update(items)
        added = len(all_items) - before
        print(f"  ✓ nType={ntype}: +{added} 筆（新增），累計 {len(all_items)} 筆\n", flush=True)

        # 每抓完一個分類就存檔（斷點保護）
        save(all_items)

    print(f"\n✅ 完成！共 {len(all_items)} 筆道具名稱")
    print(f"   TSV: {OUTPUT_FILE}")
    print(f"   JSON: {OUTPUT_FILE.replace('.tsv', '.json')}")


if __name__ == "__main__":
    main()
