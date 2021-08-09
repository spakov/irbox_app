# Path to pylint
PYLINT ?= pylint

# Path to pydoc
PYDOC ?= pydoc

# Directories to ignore for linting
IGNORE_DIRS := .git static templates venv

.DEFAULT_GOAL := all
.PHONY: all
all: lint doc

.PHONY: lint
lint:
	@# Find all .py files not in IGNORE_DIRS
	$(PYLINT) -j3 $$(find . \( $(shell for i in $(IGNORE_DIRS); do echo "-path ./$$i -o "; done) -false \) -prune -o \( -name '*.py' -print \))

.PHONY: doc
doc:
	$(PYDOC) -w ./

.PHONY: clean
clean:
	@# Remove all .pyc and .html files
	rm $$(find . \( $(shell for i in $(IGNORE_DIRS); do echo "-path ./$$i -o "; done) -false \) -prune -o \( -name '*.pyc' -print \) -o \( -name '*.html' -print \))
