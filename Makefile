ASCII_DOCTOR_IMAGE := asciidoctor/docker-asciidoctor:latest

ifndef VERBOSE
V := @
endif

WITH_VENV := $(V). .venv/bin/activate &&
PYTHON_SRC := $(shell find jam/ -type f -name '*.py')

# Build python package
dist/%.tar.gz: $(PYTHON_SRC) pyproject.toml
	$(WITH_VENV) python -m build


# Use asciidoctor container to render to html
docs/%.html: %.adoc
	$(V)mkdir -pv docs
	$(V)docker run -v $(PWD):/documents/ $(ASCII_DOCTOR_IMAGE) asciidoctor -o $@ -r asciidoctor-diagram $<


all: build docs

# Creates python virtual environment
venv: .venv
.venv:
	$(V)mkdir -p .venv
		$(V)python -m venv .venv
	$(WITH_VENV) pip install --upgrade pip build twine
.PHONY: venv


# Install package in editable mode with optional dev dependencies
dev: venv
	$(WITH_VENV) pip install --editable .[dev]
.PHONY: dev


# Run test suite
test: dev
	$(WITH_VENV) pytest
.PHONY: test


# Build python package
build: venv dist/%.tar.gz
.PHONY: build


# Publish python package to PyPI
publish: venv
	$(WITH_VENV) twine upload dist/*
.PHONY: publish


# Publish python package to PyPI test
publish-test: venv
	$(WITH_VENV) twine upload -r testpypi dist/*
.PHONY: publish-test


# Builds README and copies assets to build/
docs: docs/README.html
	$(V)mkdir -pv docs/assets
	$(V)cp -rv assets/* docs/assets/
.PHONY: docs


# Uses nodemon to watch for README changes
# Executes docs target on change
docs-dev:
	$(V)nodemon -e adoc -w ./README.adoc -x make docs
.PHONY: docs-dev


# Delete intermediate build files
clean:
	$(V)rm -rf ./**/__pycache__
	$(V)rm -rf ./jam_tool.egg-info/
	$(V)rm -rf ./build
	$(V)rm -rf ./docs
.PHONY: clean


# Deletes build artifacts
fclean: | clean
	$(V)rm -rf ./dist
	$(V)rm -rf ./.venv
.PHONY: flean
