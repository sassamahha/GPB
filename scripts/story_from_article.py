#!/usr/bin/env python3
# scripts/story_from_article.py
"""
◆ 役割
1. tmp_article.json（fetch_latest.py が取得した WP 記事）を読み込む
2. 中学生向け L3 物語を“文学的”に生成
3. その L3 をベースに L2／L1 へ精緻リライト
   └ レベル別プロンプトは『📌 推奨する改善策』に沿って厳密定義
4. stories/ja/<level>/YYYY/MM/ に
   YYYYMMDD_NN.md（フロントマター付き）で保存
"""

import json, pathlib, datetime as dt, textwrap
from dateutil import tz
from openai import OpenAI

client = OpenAI()                       # OPENAI_API_KEY は環境変数でセット

# ----------------------------------------------------------------------
def chat(system_msg: str, user_msg: str, temperature: float = 0.6) -> str:
    """OpenAI ChatCompletion ラッパー"""
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_msg},
                  {"role": "user",   "content": user_msg}],
        temperature=temperature,
    )
    return res.choices[0].message.content.strip()


def save_story(text: str, level: str, date_slug: str, counter: int) -> None:
    """stories/ja/<level>/YYYY/MM/ に保存"""
    today = dt.datetime.now(tz.gettz("Asia/Tokyo"))
    outdir = pathlib.Path("stories/ja", level, today.strftime("%Y/%m"))
    outdir.mkdir(parents=True, exist_ok=True)
    filename = f"{date_slug}_{counter:02d}.md"
    path = outdir / filename
    front = {
        "title": text.splitlines()[0].lstrip("# ").strip(),
        "created_at": today.isoformat(),
    }
    path.write_text(
        "---\n" + json.dumps(front, ensure_ascii=False) + "\n---\n\n" + text + "\n",
        encoding="utf-8",
    )
    print(" ✓", path)


# ----------------------------------------------------------------------
def main() -> None:
    # 0) 元記事読み込み ---------------------------------------------------
    post     = json.load(open("tmp_article.json", encoding="utf-8"))
    title    = post["title"]["rendered"]
    content  = post["content"]["rendered"][:1800]  # 文字数制限
    today    = dt.datetime.now(tz.gettz("Asia/Tokyo"))
    date_slug = today.strftime("%Y%m%d")

    # 同日ファイル連番カウント（L3 フォルダ基準）
    counter = (
        len(
            list(
                pathlib.Path("stories/ja/l3", today.strftime("%Y/%m")).glob(
                    f"{date_slug}_*.md"
                )
            )
        )
        + 1
    )

    # 1) L3 生成（母体・文学的バージョン）------------------------------
    sys_l3 = "あなたは日本語で情緒的で文学性豊かな文章を書くプロの作家です。"
    prompt_l3 = textwrap.dedent(
        f"""
        以下の情報をもとに、中学生が強く共感できるショートストーリーを書いてください。

        ## 書き方ルール（厳守）
        - 文字数：900〜1000字程度
        - 文体：吉川英治や宮沢賢治のように流麗で情緒的
        - 感情や心理描写を深く掘り下げ、詩的表現を用いる
        - 主人公が困難→意外な展開→成長→ハッピーエンド
        - 会話はライトノベル風に読みやすいが文学的情緒は保つ
        - 全角カギ括弧「」を会話に使用し、ふりがなは ( ) で
        - 宗教・病気・政治などセンシティブ要素は避け、固有名詞は架空化
        - 出力は Markdown。1 行目に H2 タイトル

        ## INPUT
        「{title}」
        {content}
        """
    )
    story_l3 = chat(sys_l3, prompt_l3, temperature=0.7)
    save_story(story_l3, "l3", date_slug, counter)

    # 2) L2 リライト ----------------------------------------------------
    sys_l2 = "あなたは小学5〜6年向け物語を平易な日本語で書くプロの児童文学作家です。"
    prompt_l2 = textwrap.dedent(
        f"""
        以下の物語を、小学校5〜6年生が共感できるよう、次のルールで全面的に書き直してください。

        ## 書き方ルール（厳守）
        - タイトルを高学年向けにわかりやすく書き換える
        - **漢字は教育漢字（小1〜6配当）** のみ使用し、 *必ず* 〈ふりがな〉 を ( ) で付ける
            例：**未来(みらい)**、**友達(ともだち)** 
        - 以下の NG ワードは使わず、例のように易しい言葉へ置換 
            | NG      | 置き換え例 |  
            |---------|-----------|  
            | 無力感  | ちからが でない きもち |  
            | 不安定  | ふらふら |  
            | 莫大    | とても おおきい |  
        - 一文平均20字以内
        - 人物の気持ちの変化を具体的に描写
        - 構成「導入→問題→意外な展開→解決→学び」を維持
        - 会話文中心で読みやすく
        - 固有名詞／センシティブ表現は禁止
        - 出力は Markdown、1行目に H2 タイトル
        - 以下のフォーマット例を厳守 
            ```
            ## たからものを まもれ！
            はじめに……
            ```

        元の物語：
        ---
        {story_l3}
        ---
        """
    )
    story_l2 = chat(sys_l2, prompt_l2, temperature=0.5)
    save_story(story_l2, "l2", date_slug, counter)

    # 3) L1 リライト ----------------------------------------------------
    sys_l1 = "あなたは小学1〜2年向け絵本の脚色が得意な作家です。"
    prompt_l1 = textwrap.dedent(
        f"""
        以下の物語を、小学校1〜2年生が音読しやすいよう、以下のルールで全面的に書き直してください。

        ## 書き方ルール（厳守）
        - **タイトルも本文も すべてひらがなとカタカナ**で書くこと。漢字は禁止
            NG: 未来 → OK: みらい
        - 一文は **15文字以内**。句読点「、。」を必ず入れ区切る 
        - 例： 
            ×「ある秋の午後、風が気持ちよかった。」(漢字・17文字) 
            ○「あきの かぜが きもちいい。」  
        - 感情をわかりやすく（例:「かなしいな」「うれしいよ」）
        - 会話文を全体の 40% 以上に
        - 構成「はじまり→もんだい→びっくり→かいけつ→きづき」を維持
        - 固有名詞・センシティブ表現は禁止
        - 出力は Markdown、1行目に H2 タイトル

        元の物語：
        ---
        {story_l3}
        ---
        """
    )
    story_l1 = chat(sys_l1, prompt_l1, temperature=0.4)
    save_story(story_l1, "l1", date_slug, counter)


if __name__ == "__main__":
    main()
