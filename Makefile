
test: install
	@rm -rf **/*.pyc
	@pyenv/bin/nosetests --with-coverage --cover-package=jsongraph --cover-erase

install: pyenv/bin/python

pyenv/bin/python:
	virtualenv pyenv
	pyenv/bin/pip install --upgrade pip
	pyenv/bin/pip install wheel nose coverage unicodecsv python-dateutil
	pyenv/bin/pip install -e .

upload: clean install
	pyenv/bin/python setup.py sdist bdist_wheel upload

clean:
	rm -rf pyenv jsongraph.egg-info dist build
