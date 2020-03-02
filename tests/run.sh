#!/usr/bin/env bash

codecs="utf-16 utf-32 fake utf-8-sig"

function printy() {
  echo -e "\n======================================="
  echo "Testing $1"
  echo "======================================="
}

function testall() {
  printy "help"
  ./main.py --help

  printy "version"
  ./main.py --version

  for c in $codecs; do
    printy "with codec: $c"
    ./main.py ../tests/test_subtitle.srt -e "$c"
  done

  printy "Unsupported Subtitle"
  ./main.py ../tests/unsupported_subtitle.txt -e ascii

  printy "Nonexistent file"
  ./main.py ../tests/nonexistent_subtitle.srt
}

cd ../subtproc/subtproc || exit

if [ "$1" = "--yeslint" ]; then
  shift
  pylint ./*.py
else
  echo -e "\nIf you want to include pylint run 'make linttest'"
fi

if [ "$1" = "--testall" ]; then
  testall
else
  echo -e "execute with --testall to run all tests"
  printy "with codec: default"
  ./main.py ../tests/test_subtitle.srt
fi
