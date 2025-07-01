#!/usr/bin/env python3
"""前月分の MD を EPUB に束ねる"""

import argparse
import os, pathlib, datetime as dt, json, markdown, ebooklib
from ebooklib import epub
from dateutil import relativedelta, tz

TARGET_COUNT = int(os.getenv("TARGET_COUNT", "31"))
COVERS = {
    "l1": "assets/cover_l1.jpg",
    "l2": "assets/cover_l2.jpg",
    "l3": "assets/cover_l3.jpg",
}

def md_to_html(md_text: str) -> str:
    return markdown.markdown(md_text, extensions=["extra"])

def build_epub(lang: str, level: str, md_paths: list[pathlib.Path], outdir: pathlib.Path):
    book = epub.EpubBook()
    book.set_identifier(f"rt2112-{lang}-{level}-{md_paths[0].stem}")
    book.set_title(f"Road to 2112 – {level.upper()} {lang.upper()} {md_paths[0].parent.parent.name}")
    book.set_language(lang)

    # cover
    with open(COVERS[level], "rb") as fh:
        book.set_cover(COVERS[level], fh.read())

    chapters = []
    for path in md_paths:
        _, body = path.read_text(encoding="utf-8").split("\n---\n", 1)
        html = md_to_html(body.lstrip())
        chap = epub.EpubHtml(title=path.stem, file_name=f"{path.stem}.xhtml", content=html)
        book.add_item(chap)
        chapters.append(chap)

    book.toc = chapters
    book.spine = ["nav"] + chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    outdir.mkdir(parents=True, exist_ok=True)
    fn = outdir / f"Rt2112_{level}_{lang}_{dt.datetime.now():%Y%m}.epub"
    epub.write_epub(str(fn), book)
    print("📚 ", fn)


def main(stories_root: str = "stories", outdir: str = "dist"):
    # ── CLI option -------------------------------------------------------
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-current", action="store_true",
                        help="also include stories from the current month")
    args = parser.parse_args()

    # ── 対象期間 ---------------------------------------------------------
    tz_jst = tz.gettz("Asia/Tokyo")
    today  = dt.datetime.now(tz_jst)
    start  = (today - relativedelta.relativedelta(months=1)).replace(day=1, hour=0, minute=0, second=0)
    end    = today.replace(day=1, hour=0, minute=0, second=0)
    if args.include_current:
        end = today

    # ── 走査 ------------------------------------------------------------
    for lang_dir in pathlib.Path(stories_root).iterdir():
        if not lang_dir.is_dir():
            continue
        for level_dir in lang_dir.iterdir():
            if not level_dir.is_dir():
                continue

            mds = []
            for p in level_dir.rglob("*.md"):
                created = json.loads(p.read_text(encoding="utf-8").splitlines()[1])["created_at"]
                created_dt = dt.datetime.fromisoformat(created).astimezone(tz_jst)
                if start <= created_dt < end:
                    mds.append(p)

            if mds:
                mds.sort()
                build_epub(lang_dir.name, level_dir.name, mds[:TARGET_COUNT], pathlib.Path(outdir))

if __name__ == "__main__":
    main()
