.PHONY: clean venv requirements.txt tox test build_requirements
DEPS:=api/requirements.txt
DEPS_DEV:=api/requirements_dev.txt
PIP=`. venv/bin/activate; which pip`

dc = docker-compose
run = $(dc) run --rm
manage = $(run) api python manage.py

help:                               ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

pip-tools:
	pip install pip-tools

install: pip-tools                  ## Install requirements and sync venv with expected state as defined in requirements.txt
	pip-sync api/requirements_dev.txt

requirements: pip-tools             ## Upgrade requirements (in requirements.in) to latest versions and compile requirements.txt
	pip-compile --upgrade --output-file api/requirements.txt api/requirements.in
	pip-compile --upgrade --output-file api/requirements_dev.txt api/requirements_dev.in

upgrade: requirements install       ## Run 'requirements' and 'install' targets

migrations:                         ## Make migrations
	$(manage) makemigrations $(ARGS)

migrate:                            ## Migrate
	$(manage) migrate

urls:
	$(manage) show_urls

build:
	$(dc) build

tox:
	cd src && tox ${ARGS}

isort:
	isort -ac -rc -sg "api/src/*migrations/*.py" -sg "src/tests/*" -s .tox .

docker_up:
	$(dc) up -d

app:
	$(run) --service-ports api

shell:
	$(manage) shell_plus --print-sql

test:                           	## Execute tests
	$(run) api pytest $(APP) $(ARGS)

pyclean:
	@find . -name *.pyc -delete
	@rm -rf venv

clean:                              ## Clean docker stuff
	$(dc) down -v --remove-orphans

venv: pyclean
	virtualenv -p python3.6 venv
	$(PIP) install -U "pip"
	$(PIP) install -r $(DEPS) $(DEPS_DEV)

bash:
	$(dc) run --rm api bash

env:
	env | sort
