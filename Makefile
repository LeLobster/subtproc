PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/share/man/man1
DOCDIR ?= $(PREFIX)/share/doc/ddgr

.PHONY: all install uninstall

all:

install:
	echo "Installing"

uninstall:
	echo "Uninstalling"

test:
	./tests/run.sh

linttest:
	./tests/run.sh --yeslint

testall:
	./tests/run.sh --yeslint --testall
