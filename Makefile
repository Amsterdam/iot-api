.PHONY: clean venv requirements.txt tox test build_requirements
DEPS:=api/requirements/req-dev.txt
PIP=`. venv/bin/activate; which pip`

pyclean:
	@find . -name *.pyc -delete

clean: pyclean
	@rm -rf venv

venv: clean
	virtualenv -p python3 venv
	$(PIP) install -U "pip"
	$(PIP) install -r $(DEPS)

build_requirements: venv
	$(PIP) freeze -r api/requirements/req-base.txt > api/requirements.txt

requirements.txt: | build_requirements clean
	@echo "Fresh requirements"

test:
	py.test

tox:
	cd src && tox ${ARGS}

isort:
	isort -ac -rc -sg "api/src/*migrations/*.py" -sg "src/tests/*" -s .tox .

docker_up:
	docker-compose up -d
