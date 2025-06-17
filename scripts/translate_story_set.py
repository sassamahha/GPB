import argparse
import os
import glob


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', required=True)
    parser.add_argument('--lang', required=True)
    args = parser.parse_args()

    base = os.path.join('stories', 'ja', args.level)
    for fpath in glob.glob(os.path.join(base, '*.md')):
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read()
        out_dir = os.path.join('stories', args.lang, args.level)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, os.path.basename(fpath))
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text)


if __name__ == '__main__':
    main()
