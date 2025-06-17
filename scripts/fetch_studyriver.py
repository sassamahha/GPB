import os
import json
import datetime
import requests

URL = "https://studyriver.jp/wp-json/wp/v2/posts?per_page=100"


def main():
    resp = requests.get(URL)
    resp.raise_for_status()
    articles = resp.json()
    date_str = datetime.date.today().isoformat()
    os.makedirs('data', exist_ok=True)
    path = os.path.join('data', f"{date_str}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
