import os
import json
import glob

TARGET_COUNT = int(os.getenv('TARGET_COUNT', 30))


def main():
    pool = []
    for path in glob.glob('data/*.json'):
        with open(path, 'r', encoding='utf-8') as f:
            db = json.load(f)
            articles = [a for a in db if a.get('generated_at', '') >= '18:45 JST']
            kids = [a for a in db if a.get('category') == 'kids']
            pool.extend(articles + kids)
    pool.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    selected = pool[:TARGET_COUNT]
    os.makedirs('tmp', exist_ok=True)
    with open('tmp/selected.json', 'w', encoding='utf-8') as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
