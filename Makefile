
test: install
	@rm -rf **/*.pyc
	@env/bin/nosetests --with-coverage --cover-package=jsongraph --cover-erase

testxml: install
	@env/bin/nosetests --with-xunit --xunit-file=test_output.xml

install: env/bin/python

env/bin/python:
	virtualenv env
	env/bin/pip install --upgrade pip
	env/bin/pip install wheel nose coverage unicodecsv python-dateutil
	env/bin/pip install -e .

upload: clean install
	env/bin/python setup.py sdist bdist_wheel upload

clean:
	rm -rf env
