.PHONY: clean-pyc clean-build docs clean

# PYTHON = python
PYTHON = python3

UNAME := $(shell uname)

ifeq ($(UNAME), Linux)
	OPEN = xdg-open
endif
ifeq ($(UNAME), Mac)
	OPEN = open
endif

help:
	@echo "Configured for $(PYTHON). Comment the Makefile a different install."
	@echo "clean         - remove all build, test, coverage and Python artifacts"
	@echo "clean-build   - remove build artifacts"
	@echo "clean-pyc     - remove Python file artifacts"
	@echo "clean-test    - remove test and coverage artifacts"
	@echo "lint          - check style with flake8"
	@echo "test          - run tests quickly with the default Python"
	@echo "test-all      - run tests on every Python version with tox"
	@echo "coverage      - check code coverage quickly with the default Python"
	@echo "docs          - generate Sphinx HTML documentation, including API docs"
	@echo "release       - package and upload a release"
	@echo "dist          - package"
	@echo "install       - install the package to the active Python's site-packages"
	@echo "develop       - install the package as a WIP"
	@echo "install-local - install the package to the local active Python's site-packages"
	@echo "develop-local - install the package as a WIP locally"
	@echo "phc           - install the phc functions"

clean: clean-build clean-pyc clean-test clean-vim

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr tmp/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-vim:
	find ./ -type f -name "\.*sw[klmnop]" -delete

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8 persispy tests --exclude=".ropeproject"

test:
	$(PYTHON) setup.py test
	$(PYTHON) -m doctest ./persispy/*.py -v

test-all:
	tox

coverage:
	$(PYTHON) -m coverage run --source persispy setup.py test
	$(PYTHON) -m coverage report -m
	$(PYTHON) -m coverage html
	$(OPEN) htmlcov/index.html

docs:
	rm -f docs/source/persispy.rst
	rm -f docs/source/modules.rst
	sphinx-apidoc -o docs/source/ persispy
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(OPEN) docs/build/html/index.html

release: clean
	$(PYTHON) setup.py sdist upload
	$(PYTHON) setup.py bdist_wheel upload

dist: clean
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel
	ls -l dist

install: clean
	$(PYTHON) setup.py install

develop: clean
	$(PYTHON) setup.py develop

install-local: clean
	$(PYTHON) setup.py install --user

develop-local: clean
	$(PYTHON) setup.py develop --user

phc: clean
ifeq ($(PYTHON), python3)
	apt-get install python3-dev gnat openmpi*
	git clone https://github.com/callmetaste/PHCpack tmp
	cd tmp/src/Objects && \
	make phcpy2c3.so
	cd tmp/src/Python/PHCpy3 && \
	python3 setup.py install
else
	apt-get install python-dev gnat openmpi*
	git clone https://github.com/callmetaste/PHCpack tmp
	cd tmp/src/Objects && \
	make phcpy2c2.so
	cd tmp/Python/PHCpy2 && \
	python setup.py install
endif

plot: clean
	apt-get install texlive-latex-extra libffi-dev
	apt-get install $(PYTHON)-cffi $(PYTHON)-cairocffi
