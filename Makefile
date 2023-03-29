# This Makefile is based on the Makefile defined in the Python Best Practices repository:
# https://git.datapunt.amsterdam.nl/Datapunt/python-best-practices/blob/master/dependency_management/
.PHONY: help pip-tools install requirements update test init manifests deploy

UID:=$(shell id --user)
GID:=$(shell id --group)

dc = docker-compose
run = $(dc) run --rm -u ${UID}:${GID}
manage = $(run) dev python manage.py
pytest = $(run) test pytest $(ARGS)

ENVIRONMENT ?= local
HELM_UPGRADE = helm upgrade backend $(HELM_ARGS)
HELM_ARGS = manifests/helm/application \
	-f manifests/helm/values.yaml \
	-f manifests/helm/env/${ENVIRONMENT}.yaml \
	--set image.tag=${VERSION}

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

migrate:
	$(manage) migrate

import:
	$(manage) import_api

urls:
	$(manage) show_urls

build:
	$(dc) build

push: build
	$(dc) push

deploy: manifests
	# kubectl delete deploy,service,ingress,cronjob,job,cm,secretproviderclass --all
	# Jobs are immutable
	# attempt to fix this with a helm hook that deletes itself
	# kubectl delete networkpolicy.projectcalico -l app=sensorenregister
	kubectl delete job -l 'component in (migrate, certificate)'
	helm upgrade --install --atomic backend $(HELM_ARGS)

manifests:
	@helm template backend $(HELM_ARGS) $(ARGS)

deploy/kustomize:
	# Modify some settings with environment values
	cd manifests/kustomize/overlays/${ENVIRONMENT}; \
	kustomize edit set image "*/sensorenregister/api=${REGISTRY}/${REPOSITORY}:${VERSION}";

	# Generate the combined manifests
	kustomize build manifests/kustomize/overlays/${ENVIRONMENT} > generated.yaml;

	# Print for debugging purpose
	cat generated.yaml
	# Validate it works with a dry run
	kubectl apply --dry-run=client -f generated.yaml
	# Delete immutable job
	kubectl delete job -l component=migrate
	# Apply the new manifest
	kubectl apply -f generated.yaml

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
	$(run) test pytest --junitxml=junit-results.xml --cov=. --cov-report=xml /app/tests/$(APP) $(ARGS)

k6:
	$(run) k6

qa: lint test                      ## Execute all QA tools

pdb:
	$(run) test pytest /app/tests/$(APP) --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb $(ARGS)

clean:                              ## Clean docker stuff
	$(dc) down -v --remove-orphans

bash:
	$(run) dev bash

bash-test:
	$(run) test bash
