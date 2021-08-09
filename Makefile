# Path to pylint
PYLINT ?= pylint --rcfile=.pylintrc

# Directories to ignore
IGNORE_DIRS := .git static templates venv

# Documentation output directory
DOC_OUTPUT := doc

.DEFAULT_GOAL := all
.PHONY: all
all: lint doc

.PHONY: lint
lint:
	@# Find all .py files not in IGNORE_DIRS
	$(PYLINT) -j3 $$(find . \( $(shell for i in $(IGNORE_DIRS); do echo "-path ./$$i -o "; done) -false \) -prune -o \( -name '*.py' -print \))

.PHONY: doc
doc:
	pdoc3 -o $(DOC_OUTPUT) --html .

.PHONY: clean
clean:
	@# Remove all .pyc and .html files
	rm -rv $$(find . \( $(shell for i in $(IGNORE_DIRS); do echo "-path ./$$i -o "; done) -false \) -prune -o \( -name '*.pyc' -print \) -o \( -name '*.html' -print \)) $(DOC_OUTPUT)
