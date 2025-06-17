import os
import json
import glob
import argparse


def load_articles():
    files = sorted(glob.glob('data/*.json'))
    if not files:
        raise FileNotFoundError('No data files found')
    with open(files[-1], 'r', encoding='utf-8') as f:
        return json.load(f)


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
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n{body}\n")


if __name__ == '__main__':
    main()
