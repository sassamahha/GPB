#!/usr/bin/env python3
# scripts/story_from_article.py
"""
◆ 役割
1. tmp_article.json（fetch_latest.py が取得した WP 記事）を読み込む
2. 中学生向け L3 物語を“文学的”に生成（9 パターン × 西暦 2035-2112）
3. その L3 をベースに L2／L1 へ精緻リライト
4. stories/ja/<level>/YYYY/MM/ に
   YYYYMMDD_NN.md（フロントマター付き）で保存
"""

import json, pathlib, datetime as dt, textwrap, random
from dateutil import tz
from openai import OpenAI

# ----------------------------------------------------------------------
# モデル設定 ── Large 相当（mini→large へ格上げ）
MODEL_NAME = "gpt-4o-mini"        
TEMPERATURE_L3 = 0.75       
TEMPERATURE_L2 = 0.50
TEMPERATURE_L1 = 0.40

client = OpenAI()   

# ----------------------------------------------------------------------
PATTERNS = {
    1: ("価値転倒型", "“当たり前”が逆転",
        "記事の技術や制度が普及し過ぎて〈失われる価値〉が生まれる。例：無限エネルギー→努力不要→努力の尊さが消える"),
    2: ("隠れ継承者型", "血筋/遺産の再発見",
        "スタートアップ買収・大学研究ニュースをヒントに〈無名の継承者〉が鍵を握る"),
    3: ("誤解と再認識型", "認識違い→理解",
        "予測ミス・バイアスを題材に〈誤用→学び〉の転換を描く"),
    4: ("ループ脱出型", "同じ失敗→突破",
        "気候・宇宙ミッションなど〈繰り返し試験〉を物語化し突破の瞬間を描く"),
    5: ("選択の代償型", "取捨選択と代償",
        "エネルギー/医療等で “A か B” の選択がもたらす代償を強調"),
    6: ("共同変身型", "AI/他者と共進化",
        "人間と AI が互いを進化させるコラボ研究を軸にする"),
    7: ("失われた感覚探索型", "五感・感情の欠損",
        "VR・スマート素材で〈失った感覚〉を取り戻す旅を描く"),
    8: ("未来の忘却型", "過去 > 未来の穴",
        "歴史を忘れた未来都市を〈過去の遺物〉で救う"),
    9: ("ドラえもん型", "便利→悪用→因果応報",
        "便利ガジェットの “ちょっとした悪用”→しっぺ返し→教訓"),
}

# ----------------------------------------------------------------------
def chat(system_msg: str, user_msg: str, temperature: float = 0.6) -> str:
    """OpenAI ChatCompletion ラッパー"""
    res = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": system_msg},
                  {"role": "user",   "content": user_msg}],
        temperature=temperature,
    )
    return res.choices[0].message.content.strip()


def save_story(text: str, level: str, date_slug: str, counter: int,
               meta: dict) -> None:
    """stories/ja/<level>/YYYY/MM/ に保存"""
    today = dt.datetime.now(tz.gettz("Asia/Tokyo"))
    outdir = pathlib.Path("stories/ja", level, today.strftime("%Y/%m"))
    outdir.mkdir(parents=True, exist_ok=True)
    filename = f"{date_slug}_{counter:02d}.md"
    path = outdir / filename
    front = {
        "title": text.splitlines()[0].lstrip("# ").strip(),
        "created_at": today.isoformat(),
        **meta,                    # ← パターン / 年代メタ
    }
    path.write_text(
        "---\n" + json.dumps(front, ensure_ascii=False) + "\n---\n\n" + text + "\n",
        encoding="utf-8",
    )
    print(" ✓", path)


# ----------------------------------------------------------------------
def main() -> None:
    # 0) 元記事読み込み ---------------------------------------------------
    post    = json.load(open("tmp_article.json", encoding="utf-8"))
    title   = post["title"]["rendered"]
    content = post["content"]["rendered"][:1800]  # 文字数制限

    # 0-α) パターン & 年代を抽選
    pattern_id, (pattern_name, pattern_axis, pattern_desc) = random.choice(list(PATTERNS.items()))
    year = random.randint(2035, 2112)

    # 0-β) 同日ファイル連番カウント（L3 フォルダ基準）
    today      = dt.datetime.now(tz.gettz("Asia/Tokyo"))
    date_slug  = today.strftime("%Y%m%d")
    counter = (
        len(list(pathlib.Path("stories/ja/l3", today.strftime("%Y/%m")).glob(f"{date_slug}_*.md")))
        + 1
    )

    # ------------------------------------------------------------ L3 生成
    sys_l3 = (
    "あなたは、人間と知能をもつロボットが共生する未来を舞台に、"
    "情緒的で文学性豊かな日本語で物語を書くプロの SF 作家です。"
   )
    prompt_l3 = textwrap.dedent(f"""
        以下の情報をもとに、西暦 {year} 年、人間とロボットがともに暮らす社会を舞台にした  
    **{pattern_name}（{pattern_axis}）** の “少し不思議” なショートストーリーを書いてください。

        ## 制約（厳守）
         - 文字数：900〜1000字
         - 舞台：人間と知能をもつロボットが共生する未来社会（必須）
         - 登場人物：**最低 1 人の人間と 1 体のロボット** を出し、両者の心情と相互作用を描く
         - 文体：吉川英治や宮沢賢治のように流麗で情緒的  
         - 感情・心理描写を深く掘り下げ、**詩的比喩を最低 2 回** 用いる
         - 主人公が困難→意外な展開→成長→ハッピーエンド
         - “少し不思議” な未来ガジェットや出来事を 1 つ以上盛り込む
         - 会話はライトノベル風に親しみやすく、全角カギ括弧「」を使用
         - ふりがなは ( ) で
         - 宗教・病気・政治などセンシティブ要素は避ける
         - 元記事の固有名詞は架空名に置換
         - 出力形式：Markdown（1 行目に H2 タイトル）

        ## パターン説明
        {pattern_desc}

        ## 元記事
        「{title}」
        {content}
    """)
    story_l3 = chat(sys_l3, prompt_l3, temperature=TEMPERATURE_L3)

    meta_common = {"pattern_id": pattern_id, "pattern_name": pattern_name, "year": year}
    save_story(story_l3, "l3", date_slug, counter, meta_common)

    # ------------------------------------------------------------ L2 生成
    sys_l2 = "あなたは小学5〜6年向け物語をわかりやすい日本語で書くプロの児童文学作家です。"
    prompt_l2 = textwrap.dedent(f"""
        以下の物語を、小学校5〜6年生が共感できるよう、次のルールで文章を書き直してください。

        ## 前提
        - 物語の内容は変えず、文章を変えること。

        ## 書き方ルール（厳守）
        - タイトルを高学年向けにわかりやすく書き換える
        - **漢字は教育漢字（小1〜6配当）のみ**を使用し、*必ず* 〈ふりがな〉を ( ) で付ける
        - 以下の NG ワードは使わず、例のように易しい言葉へ置換  
            | NG      | 置き換え例 |  
            |---------|-----------|  
            | 無力感  | ちからが でない きもち |  
            | 不安定  | ふらふら |  
            | 莫大    | とても おおきい |  
        - 一文平均 20 字以内
        - 人物の気持ちの変化を具体的に描写
        - 構成「導入→問題→意外な展開→解決→学び」を維持
        - 会話文中心で読みやすく
        - 固有名詞／センシティブ表現は禁止
        - 出力は Markdown、1 行目に H2 タイトル
        
        元の物語：
        ---
        {story_l3}
        ---
    """)
    story_l2 = chat(sys_l2, prompt_l2, temperature=TEMPERATURE_L2)
    save_story(story_l2, "l2", date_slug, counter, meta_common)

    # ------------------------------------------------------------ L1 生成
    sys_l1 = "あなたは小学1〜2年向け絵本の脚色が得意な作家です。"
    prompt_l1 = textwrap.dedent(f"""
        以下の物語を、小学校1〜2年生が音読やひとり読書がしやすいよう、以下のルールで文章を書き直してください。

        ## 前提
        - 物語の内容は変えず、文章を変えること。

        ## 書き方ルール（厳守）
        - **タイトルも本文も すべてひらがなとカタカナ**で書くこと（漢字は禁止）
        - 一文は **15 文字以内**。句読点「、。」を必ず入れ区切り、一文ごとに改行すること。
          例：  
            ×「ある秋の午後、風が気持ちよかった。」  
            ○「あきの かぜが きもちいい。」  
        - 感情をわかりやすく（例:「かなしいな」「うれしいよ」）
        - 会話文を全体の 40% 以上に
        - 構成「はじまり→もんだい→びっくり→かいけつ→きづき」を維持
        - 固有名詞・センシティブ表現は禁止
        - 出力は Markdown、1 行目に H2 タイトル

        元の物語：
        ---
        {story_l3}
        ---
    """)
    story_l1 = chat(sys_l1, prompt_l1, temperature=TEMPERATURE_L1)
    save_story(story_l1, "l1", date_slug, counter, meta_common)


if __name__ == "__main__":
    main()
