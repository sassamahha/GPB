import os
import json
import glob
import argparse
from typing import List

import openai


def load_articles():
    files = sorted(glob.glob('data/*.json'))
    if not files:
        raise FileNotFoundError('No data files found')
    with open(files[-1], 'r', encoding='utf-8') as f:
        return json.load(f)


def rewrite_article(title: str, body: str, level: str) -> str:
    """Rewrite article content for the given reading level using OpenAI."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set")
    openai.api_key = api_key

    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    level_str = level.upper()
    prompt = (
        f"You are a helpful assistant who rewrites Japanese articles for "
        f"reading level {level_str}. Summarize or rewrite the following text "
        f"in Japanese so it is appropriate for that level.\n\nTitle: {title}\n\n{body}"
    )
    messages: List[dict] = [
        {"role": "user", "content": prompt}
    ]
    resp = openai.ChatCompletion.create(
        model=model,
        messages=messages,
    )
    return resp["choices"][0]["message"]["content"].strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', default='l3')
    parser.add_argument('--json-latest', action='store_true')
    args = parser.parse_args()

    articles = load_articles()
    for i, article in enumerate(articles, 1):
        title = article.get('title', {}).get('rendered', '')
        body = article.get('content', {}).get('rendered', '')
        ym = os.path.strftime('%Y%m') if hasattr(os.path, 'strftime') else ''
        out_dir = os.path.join('stories', 'ja', args.level, f'vol{ym}')
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f'{i:02d}.md')
        story = rewrite_article(title, body, args.level)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n{story}\n")


if __name__ == '__main__':
    main()
