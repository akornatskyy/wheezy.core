.SILENT: clean env po doctest-cover qa test doc release upload
.PHONY: clean env po doctest-cover qa test doc release upload

VERSION=2.7
PYPI=http://pypi.python.org/simple
DIST_DIR=dist

PYTHON=env/bin/python$(VERSION)
EASY_INSTALL=env/bin/easy_install-$(VERSION)
PYTEST=env/bin/py.test-$(VERSION)
NOSE=env/bin/nosetests-$(VERSION)
SPHINX=env/bin/python$(VERSION) env/bin/sphinx-build

all: clean po doctest-cover test release

debian:
	apt-get -y update
	apt-get -y dist-upgrade
	# How to Compile Python from Source
	# http://mindref.blogspot.com/2011/09/compile-python-from-source.html
	apt-get -y install libbz2-dev build-essential python \
		python-dev python-setuptools python-virtualenv \
		python-sphinx mercurial gettext

env:
	PYTHON_EXE=/usr/local/bin/python$(VERSION) ; \
	if [ ! -x $$PYTHON_EXE ]; then \
		PYTHON_EXE=/opt/local/bin/python$(VERSION) ; \
		if [ ! -x $$PYTHON_EXE ]; then \
			PYTHON_EXE=/usr/bin/python$(VERSION) ; \
		fi ; \
	fi ; \
	VIRTUALENV_USE_SETUPTOOLS=1; \
    export VIRTUALENV_USE_SETUPTOOLS; \
	virtualenv --python=$$PYTHON_EXE \
		--no-site-packages env
	if [ "$$(echo $(VERSION) | sed 's/\.//')" -ge 30 ]; then \
		/bin/echo -n 'Upgrading distribute...'; \
		$(EASY_INSTALL) -i $(PYPI) -U -O2 distribute \
			> /dev/null 2>/dev/null; \
		echo 'done.'; \
	fi
	$(EASY_INSTALL) -i $(PYPI) -O2 coverage nose pytest \
		pytest-pep8 pytest-cov mock
	# The following packages available for python < 3.0
	#if [ "$$(echo $(VERSION) | sed 's/\.//')" -lt 30 ]; then \
	#	$(EASY_INSTALL) sphinx; \
	#fi
	$(PYTHON) setup.py develop -i $(PYPI)

clean:
	find src/ -type d -name __pycache__ | xargs rm -rf
	find src/ -name '*.py[co]' -delete
	find src/wheezy/core/tests/i18n/ -name '*.mo' -delete
	rm -rf dist/ build/ MANIFEST src/*.egg-info .cache .coverage

release:
	$(PYTHON) setup.py -q bdist_egg

upload:
	REV=$$(hg head --template '{rev}') ; \
	sed -i "s/'0.1'/'0.1.$$REV'/" src/wheezy/core/__init__.py ; \
	if [ "$$(echo $(VERSION) | sed 's/\.//')" -eq 27 ]; then \
		$(PYTHON) setup.py -q egg_info --tag-build .$$REV \
			sdist register upload; \
		$(EASY_INSTALL) -i $(PYPI) sphinx; \
		$(PYTHON) env/bin/sphinx-build -D release=0.1.$$REV \
			-a -b html doc/ doc/_build/;\
		python setup.py upload_docs; \
	fi; \
	$(PYTHON) setup.py -q egg_info --tag-build .$$REV \
		bdist_egg --dist-dir=$(DIST_DIR) \
		rotate --match=$(VERSION).egg --keep=1 --dist-dir=$(DIST_DIR) \
		upload;

qa:
	if [ "$$(echo $(VERSION) | sed 's/\.//')" -eq 27 ]; then \
		env/bin/flake8 --max-complexity 9 demos doc src setup.py && \
		env/bin/pep8 doc src setup.py ; \
	fi

test:
	$(PYTEST) -q -x --pep8 --doctest-modules \
		src/wheezy/core

doctest-cover:
	$(NOSE) --stop --with-doctest --detailed-errors \
		--with-coverage --cover-package=wheezy.core

test-cover:
	$(PYTEST) -q --cov wheezy.core \
		--cov-report term-missing \
		src/wheezy/core/tests

doc:
	$(SPHINX) -a -b html doc/ doc/_build/

test-demos:
	$(PYTEST) -q -x --pep8 demos/

po:
	cd src/wheezy/core/tests ; \
	for l in `ls -d i18n/*/ | cut -d / -f 2`; do \
		/bin/echo -n "$$l => "; \
		msgfmt -v i18n/$$l/LC_MESSAGES/messages.po \
			-o i18n/$$l/LC_MESSAGES/messages.mo; \
	done
