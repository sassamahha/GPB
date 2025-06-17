import os
import glob
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--from', dest='from_level', required=True)
    parser.add_argument('--to', required=True)
    args = parser.parse_args()
    targets = args.to.split(',')
    base_dir = os.path.join('stories', 'ja', args.from_level)
    for path in glob.glob(os.path.join(base_dir, '**', '*.md'), recursive=True):
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        for level in targets:
            out = path.replace(args.from_level, level)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, 'w', encoding='utf-8') as fw:
                fw.write(text)


if __name__ == '__main__':
    main()
