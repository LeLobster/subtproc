#!/usr/bin/env bash

codecs="utf-16 utf-32 fake utf-8-sig"

function printy() {
  echo -e "\n======================================="
  echo "Testing $1"
  echo "======================================="
}

cd ../subtproc/subtproc || exit

if [ "$1" = "--yeslint" ]; then
    pylint ./*.py
else
    echo -e "\nIf you want to include pylint run make linttest"
fi

printy "help"
./main.py --help

for c in $codecs; do
  printy "with codec: $c"
  ./main.py ../tests/test_subtitle.srt -e "$c"
done

printy "Unsupported Subtitle"
./main.py ../tests/unsupported_subtitle.txt -e ascii

printy "Nonexistent file"
./main.py ../tests/nonexistent_subtitle.srt
