#!/usr/bin/env bash

codecs="utf-16 utf-32 fake utf-8-sig"

function printy() {
  echo -e "\n======================================="
  echo "Testing $1"
  echo "======================================="
}

function testall() {
  printy "help"
  python3 ../subtproc --help

  printy "version"
  python3 ../subtproc --version

  for c in $codecs; do
    printy "with codec: $c"
    python3 ../subtproc ../tests/test_subtitle.srt -e "$c"
  done

  printy "Unsupported Subtitle"
  python3 ../subtproc ../tests/unsupported_subtitle.txt -e ascii

  printy "Nonexistent file"
  python3 ../subtproc ../tests/nonexistent_subtitle.srt
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
  python3 ../subtproc ../tests/test_subtitle.srt
fi
