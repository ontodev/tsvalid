###Configuration
#
# These are standard options to make Make sane:
# <http://clarkgrubb.com/makefile-style-guide#toc2>

MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:
.SECONDARY:

all: test

.PHONY: test
test:
	tox

.PHONY: install
install:
	pip install .[test,docs]

.PHONY: pypi
pypi: test
	echo "Uploading to pypi. Make sure you have twine installed.."
	python setup.py sdist
	twine upload dist/*

.PHONY: lint
lint:
	tox -e lint

.PHONY: mypy
mypy:
	tox -e mypy

.PHONY: sphinx
sphinx:
	cd sphinx &&\
	make clean html

.PHONY: deploy-docs
deploy-docs:
	cp -r sphinx/_build/html/* docs/
