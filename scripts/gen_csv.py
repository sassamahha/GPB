import csv
import json
import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', required=True)
    parser.add_argument('--level', required=True)
    args = parser.parse_args()

    with open('tmp/selected.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)

    os.makedirs('csv', exist_ok=True)
    path = os.path.join('csv', f"{args.lang}_{args.level}.csv")
    with open(path, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = ['Title', 'Subtitle', 'On Sale Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for art in articles:
            row = {
                'Title': art.get('title', {}).get('rendered', ''),
                'Subtitle': art.get('excerpt', {}).get('rendered', ''),
                'On Sale Date': ''
            }
            writer.writerow(row)


if __name__ == '__main__':
    main()
