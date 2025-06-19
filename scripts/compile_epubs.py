# scripts/compile_epubs.py
"""前月分の MD を EPUB に束ねる"""

import os, pathlib, datetime as dt, json, markdown, ebooklib
from ebooklib import epub
from dateutil import relativedelta, tz

TARGET_COUNT = int(os.getenv("TARGET_COUNT", "31"))
COVERS = {"l1": "assets/cover_l1.jpg", "l2": "assets/cover_l2.jpg", "l3": "assets/cover_l3.jpg"}

def md_to_html(md_text):
    return markdown.markdown(md_text, extensions=["extra"])

def build_epub(lang, level, md_paths, outdir):
    book = epub.EpubBook()
    book.set_identifier(f"rt2112-{lang}-{level}-{md_paths[0].stem}")
    book.set_title(f"Road to 2112 – {level.upper()} {lang.upper()} {md_paths[0].parent.parent.name}")
    book.set_language(lang)
    book.add_item(epub.EpubCover(file_name=COVERS[level], content=open(COVERS[level], "rb").read()))

    chapters = []
    for path in md_paths:
        front, body = path.read_text(encoding="utf-8").split("\n---\n", 1)[1].split("\n", 1)
        html = md_to_html(body)
        c = epub.EpubHtml(title=path.stem, file_name=f"{path.stem}.xhtml", content=html)
        book.add_item(c)
        chapters.append(c)

    book.toc = chapters
    book.spine = ["nav"] + chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    outdir.mkdir(exist_ok=True, parents=True)
    fn = outdir / f"Rt2112_{level}_{lang}_{dt.datetime.now():%Y%m}.epub"
    epub.write_epub(str(fn), book)
    print("📚  ", fn)

def main(stories_root="stories", outdir="dist"):
    tz_jst = tz.gettz("Asia/Tokyo")
    today = dt.datetime.now(tz_jst)
    start = (today - relativedelta.relativedelta(months=1)).replace(day=1, hour=0, minute=0, second=0)
    end = today.replace(day=1, hour=0, minute=0, second=0)

    if args.include_current:
        end = today    # ← 開発中の暫定措置。ローンチ次第削除。今月 23:59 まで含める

    for lang_dir in pathlib.Path(stories_root).iterdir():
        if not lang_dir.is_dir():
            continue
        for level_dir in lang_dir.iterdir():
            if not level_dir.is_dir():
                continue
            mds = sorted(p for p in level_dir.rglob("*.md")
                         if start <= dt.datetime.fromisoformat(json.loads(p.read_text().splitlines()[1])["created_at"]).astimezone(tz_jst) < end)
            if not mds:
                continue
            build_epub(lang_dir.name, level_dir.name, mds[:TARGET_COUNT], pathlib.Path(outdir))

if __name__ == "__main__":
    main()
