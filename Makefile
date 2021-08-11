# Path to pylint and options
PYLINT ?= pylint --rcfile=.pylintrc

# Path to pdoc3 and options
PDOC3 := pdoc3 --force

# Directories to ignore
IGNORE_DIRS := .git static templates venv

# Documentation output directory
DOC_OUTPUT := doc

# List of modules for which to generate documentation
DOC_MODULES := irbox_app app irbox

.DEFAULT_GOAL := all
.PHONY: all
all: lint doc

.PHONY: lint
lint:
	@# Find all .py files not in IGNORE_DIRS
	$(PYLINT) -j3 $$(find . \( $(shell for i in $(IGNORE_DIRS); do echo "-path ./$$i -o "; done) -false \) -prune -o \( -name '*.py' -print \))

.PHONY: doc
doc:
	$(PDOC3) -o $(DOC_OUTPUT) --html $(DOC_MODULES)

.PHONY: clean
clean:
	@# Remove all .pyc and .html files
	rm -rv $$(find . \( $(shell for i in $(IGNORE_DIRS); do echo "-path ./$$i -o "; done) -false \) -prune -o \( -name '*.pyc' -print \) -o \( -name '*.html' -print \)) $(DOC_OUTPUT) || exit 0
