#######################################
### Dev targets
#######################################
dev-dep:
	sudo apt-get install python3-virtualenv python3-pil.imagetk python3-tk libspeex-dev swig libpulse-dev libspeexdsp-dev portaudio19-dev

dev-pyenv:
	virtualenv -p /usr/bin/python3 env
	env/bin/pip3 install -r requirements.txt --upgrade --force-reinstall
	env/bin/pip3 install -r test_requirements.txt --upgrade --force-reinstall
	env/bin/python setup.py develop

docker_build:
	docker build -t tuxeatpi_brain -f Dockerfile .

docker_run:
	docker run --net=host --rm -v `pwd`/config.yaml:/config.yaml tuxeatpi_brain -c /config.yaml

docker_irun:
	docker run -it --rm -v `pwd`/config.yaml:/config.yaml --entrypoint=sh tuxeatpi_brain

#######################################
### Documentation
#######################################
doc-update-refs:
	rm -rf doc/source/refs/
	sphinx-apidoc -M -f -e -o doc/source/refs/ tuxeatpi_brain

doc-generate:
	cd doc && make html
	touch doc/build/html/.nojekyll

#######################################
### Test targets
#######################################

test-run: test-syntax test-pytest

test-syntax:
	env/bin/pycodestyle --max-line-length=100 tuxeatpi_brain
	env/bin/pylint --rcfile=.pylintrc -r no tuxeatpi_brain

test-pytest:
	rm -rf .coverage nosetest.xml nosetests.html htmlcov
	env/bin/pytest --html=pytest/report.html --self-contained-html --junit-xml=pytest/junit.xml --cov=tuxeatpi_brain/ --cov-report=term --cov-report=html:pytest/coverage/html --cov-report=xml:pytest/coverage/coverage.xml -p no:pytest_wampy tests
	coverage combine || true
	coverage report --include='*/tuxeatpi_brain/*'
	# CODECLIMATE_REPO_TOKEN=${CODECLIMATE_REPO_TOKEN} codeclimate-test-reporter
