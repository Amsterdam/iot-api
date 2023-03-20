# This Makefile is based on the Makefile defined in the Python Best Practices repository:
# https://git.datapunt.amsterdam.nl/Datapunt/python-best-practices/blob/master/dependency_management/
.PHONY: help pip-tools install requirements update test init manifests deploy

UID:=$(shell id --user)
GID:=$(shell id --group)

dc = docker-compose
run = $(dc) run --rm -u ${UID}:${GID}
manage = $(run) dev python manage.py
pytest = $(run) test pytest $(ARGS)

ENV ?= local
manifests = kustomize build manifests/overlays/${ENV}

REGISTRY ?= localhost:5001
REPOSITORY ?= sensorenregister/api
VERSION ?= latest

help:                               ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

pip-tools:
	pip install -U pip-tools

install: pip-tools                  ## Install requirements and sync venv with expected state as defined in requirements.txt
	pip-sync requirements_dev.txt

requirements: pip-tools             ## Upgrade requirements (in requirements.in) to latest versions and compile requirements.txt
	pip-compile --resolver=backtracking --upgrade --output-file requirements.txt requirements.in
	pip-compile --resolver=backtracking --upgrade --output-file requirements_dev.txt requirements_dev.in

upgrade: requirements install       ## Run 'requirements' and 'install' targets

migrations:                         ## Make migrations
	$(manage) makemigrations $(ARGS)

migrate:                            ## Migrate
	$(manage) migrate

urls:
	$(manage) show_urls

build:
	$(dc) build

push: build
	$(dc) push

deploy:
	# Print for debugging purpose
	$(manifests)
	# Validate it works with a dry run
	$(manifests) | kubectl apply --dry-run=client -f -
	# Delete immutable job
	kubectl delete job -l component=migrate
	# Apply the new manifest
	$(manifests) | kubectl apply -f -

undeploy:
	$(manifests) | kubectl delete -f -

manifests:
	@$(manifests)

app:
	$(run) --service-ports app

shell:
	$(manage) shell_plus --print-sql

notebook:
	$(dc) run -e DJANGO_ALLOW_ASYNC_UNSAFE=true --rm --service-ports dev python manage.py shell_plus --notebook

dev: 						        ## Run the development app (and run extra migrations first)
	$(run) --service-ports dev

lintfix:                            ## Execute lint fixes
	$(run) test isort /app/src/$(APP) /app/tests/$(APP)
	$(run) test black /app/src/$(APP) /app/tests/$(APP)

lint:                               ## Execute lint checks
	$(run) test isort --diff --check /app/src/$(APP) /app/tests/$(APP)
	$(run) test black --diff --check /app/src/$(APP) /app/tests/$(APP)

test: lint                          ## Execute tests
	$(run) test pytest /app/tests/$(APP) $(ARGS)

qa: lint test                      ## Execute all QA tools

pdb:
	$(run) test pytest /app/tests/$(APP) --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb $(ARGS)

clean:                              ## Clean docker stuff
	$(dc) down -v --remove-orphans

bash:
	$(run) dev bash

bash-test:
	$(run) test bash
