#!/usr/bin/env python3
import os, pathlib, json, sys
from openai import OpenAI

client = OpenAI()

# ───────────────────────────────────────────────────────────────
LANGS = [l.strip().lower() for l in os.getenv("TRANSLATE_LANGS", "").split(",") if l.strip()]
LANGS = [l for l in LANGS if l != "ja"]     # JP→JP を除外

LANG_NAMES = {
    "en": "English",
    "es": "Spanish",
    "pt": "Portuguese",
    "hi": "Hindi",
    "id": "Indonesian",
    "zh-hant": "Traditional Chinese",
}

# 言語ごとの会話フォーマット指定
DIALOGUE_RULES = {
    # English – “double-quotes” +改行
    "en": (
        'Use standard English fiction style: '
        'each spoken line is enclosed in double quotes (") and every new speaker starts a new line, e.g.\n'
        '"Hey, Tom."\n'
        '"Have you thought about the future?"'
    ),

    # Spanish – 行頭ダッシュ
    "es": (
        'Use Spanish novel style: each spoken line begins with an em dash (—), '
        'no closing dash, new speaker on a new paragraph, e.g.\n'
        '—Hola, Javier.\n'
        '—¿Has pensado en el futuro?'
    ),

    # Portuguese – 行頭ダッシュ
    "pt": (
        'Use Portuguese fiction style: dialogue lines start with an em dash (—) '
        'and each new speaker begins a new paragraph.'
    ),

    # Hindi – “double-quotes” を使用
    "hi": (
        'Use modern Hindi novel style: dialogue lines in Hindi quotation marks “ ” '
        'with a new line for each speaker, e.g.\n'
        '“अरे, रोहन! क्या तुमने भविष्य के बारे में सोचा है?”'
    ),

    # Indonesian – “double-quotes” を使用
    "id": (
        'Use Indonesian prose style: dialogue enclosed in double quotes (") '
        'and each speaker on a new line.'
    ),

    # Traditional Chinese – 「全形二重カギ括弧」
    "zh-hant": (
        '使用中文小說格式：對話行以全形書名號「 」包住，每位說話者換行，例如：\n'
        '「嘿，宇晨，你想過未來嗎？」\n'
        '「當然想過！」'
    ),
}

# ───────────────────────────────────────────────────────────────
def translate_md(src: pathlib.Path, lang: str):
    raw = src.read_text(encoding="utf-8")
    front, body = raw.split("\n---\n", 1)
    md_body = body.lstrip()

    tgt_name  = LANG_NAMES.get(lang, lang.upper())
    dialogue  = DIALOGUE_RULES.get(lang, "Use the natural dialogue punctuation conventions of the target language.")

    system_msg = (
        f"You are a professional literary translator. "
        f"Translate EVERYTHING into {tgt_name} only. Keep Markdown structure. "
        "Localize all Japanese personal names to culturally common names in the target language, "
        "keeping consistency for each character. "
        + dialogue
    )
    user_msg = f"[LANG={lang}]\n\n{md_body}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0.2,
    ).choices[0].message.content.strip()

    tgt_path = pathlib.Path("stories", lang, *src.parts[2:])
    tgt_path.parent.mkdir(parents=True, exist_ok=True)
    tgt_path.write_text(front + "\n---\n\n" + res + "\n", encoding="utf-8")
    print(" →", tgt_path)

# ───────────────────────────────────────────────────────────────
def main():
    if not LANGS:
        print("TRANSLATE_LANGS not set")
        sys.exit(1)

    ja_root = pathlib.Path("stories/ja")
    if not ja_root.exists():
        print("No JP stories yet")
        return

    for md in ja_root.rglob("*.md"):
        rel = md.relative_to(ja_root)
        for lang in LANGS:
            tgt = pathlib.Path("stories", lang, rel)
            if not tgt.exists():
                translate_md(md, lang)

if __name__ == "__main__":
    main()
