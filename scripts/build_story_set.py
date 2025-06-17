import argparse
import os
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', required=True)
    args = parser.parse_args()
    with open('tmp/selected.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    out_dir = os.path.join('stories', 'ja', args.level)
    os.makedirs(out_dir, exist_ok=True)
    for i, art in enumerate(articles, 1):
        path = os.path.join(out_dir, f'{i:02d}.md')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(art.get('content', {}).get('rendered', ''))

if __name__ == '__main__':
    main()
