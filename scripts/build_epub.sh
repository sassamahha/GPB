#!/bin/bash
set -e
lang=$1
level=$2
outdir="stories/$lang/$level"
mkdir -p epub
outfile="epub/${lang}_${level}.epub"
zip -r "$outfile" "$outdir" >/dev/null
