.DEFAULT_GOAL := help

PYTHON_INTERPRETER = python
SHELL=/bin/bash -e
SRC ?= src
TESTS ?= tests
CONDA_ENV ?= igz-cicd-flow
CONDA_PY_VER ?= 3.9
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

#################################################################################
# COMMANDS                                                                      #
#################################################################################

.PHONY: help
help: ## Display available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: all
all:
	$(error please pick a target)

.PHONY: clean
clean: ## Delete all compiled Python files
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf build
	rm -rf dist

.PHONY: fmt
fmt: clean ## Format the code (using black and isort)
	@echo "Running black fmt..."
	$(PYTHON_INTERPRETER) -m black $(SRC) .
	$(PYTHON_INTERPRETER) -m isort $(SRC) .

.PHONY: lint
lint: fmt-check flake8 ## Run lint on the code

.PHONY: fmt-check
fmt-check: clean ## Format and check the code (using black and isort)
	@echo "Running black+isort fmt check..."
	$(PYTHON_INTERPRETER) -m black --check --diff $(SRC) .
	$(PYTHON_INTERPRETER) -m isort --check --diff $(SRC) .

.PHONY: flake8
flake8: ## Run flake8 lint
	@echo "Running flake8 lint..."
	$(PYTHON_INTERPRETER) -m flake8 $(SRC) .

.PHONY: conda-env
conda-env: ## Create a conda environment (may require changing on Windows)
	@if ! conda env list | grep -q $(CONDA_ENV); then \
		echo "Creating new conda environment $(CONDA_ENV)..."; \
		CONDA_SUBDIR=osx-64 conda create -n $(CONDA_ENV) -y python=$(CONDA_PY_VER) ipykernel pip protobuf=3.20.3; \
		conda config --env --set subdir osx-64; \
	fi
	@echo "Installing dependencies"
	$(CONDA_ACTIVATE) $(CONDA_ENV); pip install -r requirements-mlrun.txt
	$(CONDA_ACTIVATE) $(CONDA_ENV); pip install -r requirements.txt -r requirements-dev.txt
    
.PHONY: install-requirements
install-requirements: ## Install all requirements needed for development
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt -r requirements-dev.txt

.PHONY: test
test: ## Run unit tests via pytest
	@echo "Running unit tests via pytest..."
	$(PYTHON_INTERPRETER) -m pytest $(TESTS)

.PHONY: deploy
deploy: ## Deploy MLOps Sandbox cluster
	@echo "Deploying..."
	k3d cluster create --config k8s/k3d-cluster-mlrun.yaml
	tilt up

.PHONY: start
start: ## Start MLOps Sandbox cluster
	@echo "Starting..."
	k3d cluster start k3d-mlrun

.PHONY: stop
stop: ## Stop MLOps Sandbox cluster
	@echo "Stopping..."
	k3d cluster stop k3d-mlrun

.PHONY: delete
delete: ## Delete MLOps Sandbox cluster
	@echo "Stopping..."
	k3d cluster delete k3d-mlrun