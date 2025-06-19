#!/usr/bin/env python3
# scripts/fetch_latest.py
"""
Fetch the latest StudyRiver post **in Japanese** and cache it as tmp_article.json.
If no JP post is found, exit 78 so GitHub Actions marks the job as neutral.

判定ロジック
-------------
1. REST API で最新 50 件を取得
2. 「かな文字が 5 文字以上 **かつ** 日本語スクリプト比率 > 15 %」の
   最初の 1 件を “Japanese” とみなす
3. すでに stories/ja/** に存在する slug はスキップ
4. 公開日が “今日(JST)” でなければスキップ
"""

import argparse
import json
import pathlib
import sys
import datetime as dt
import requests
import regex as re
from dateutil import tz

# ----------------------------------------
# CONFIG
API_URL = (
    "https://studyriver.jp/wp-json/wp/v2/posts"
    "?per_page=50&_fields=link,title,content,date,slug"
)
KANA_RE   = re.compile(r"\p{Script=Hiragana}|\p{Script=Katakana}")
KANJI_RE  = re.compile(r"[一-龯]")
KANA_MIN  = 5       # かな文字が 5 文字以上
JP_RATIO  = 0.15    # JP スクリプト率 15 % 以上
TMP_JSON  = "tmp_article.json"
# ----------------------------------------


def is_japanese(text: str,
                kana_min: int = KANA_MIN,
                ratio_threshold: float = JP_RATIO) -> bool:
    """Return True if text is Japanese-dominant."""
    if not text:
        return False
    kana_cnt  = len(KANA_RE.findall(text))
    kanji_cnt = len(KANJI_RE.findall(text))
    jp_ratio  = (kana_cnt + kanji_cnt) / len(text)
    return kana_cnt >= kana_min and jp_ratio > ratio_threshold


def jst_now() -> dt.datetime:
    """Return current time in Asia/Tokyo tzinfo."""
    return dt.datetime.now(dt.UTC).astimezone(tz.gettz("Asia/Tokyo"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore date/duplication guards (local testing).",
    )
    args = parser.parse_args()

    # 1. fetch latest 50 posts
    try:
        posts = requests.get(API_URL, timeout=10).json()
    except requests.RequestException as exc:
        print("[error] Cannot fetch WP API:", exc)
        sys.exit(1)

    # 2. pick the first Japanese-dominant post
    chosen = None
    for p in posts:
        raw = (p["title"]["rendered"] or "") + (p["content"]["rendered"] or "")
        if is_japanese(raw):
            chosen = p
            break

    if not chosen:
        print("[skip] No Japanese post found")
        sys.exit(78)

    slug       = chosen["slug"]
    today_str  = jst_now().strftime("%Y-%m-%d")
    jp_post_dt = dt.datetime.fromisoformat(
        chosen["date"].replace("Z", "+00:00")
    ).astimezone(tz.gettz("Asia/Tokyo"))

    # 3. duplication guard
    if (
        not args.force
        and any(True for _ in pathlib.Path("stories/ja").rglob(f"*/{slug}.md"))
    ):
        print("[skip] slug already processed:", slug)
        sys.exit(78)

    # 4. today check
    if jp_post_dt.strftime("%Y-%m-%d") != today_str and not args.force:
        print("[skip] Latest Japanese post is not from today")
        sys.exit(78)

    # 5. save to tmp_article.json
    pathlib.Path(TMP_JSON).write_text(
        json.dumps(chosen, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("[OK] fetched:", chosen["title"]["rendered"])


if __name__ == "__main__":
    main()
