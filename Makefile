# Local ZMK firmware build helper.
#
# Uses `uv` to create/maintain a virtualenv and install manual_build/requirements.txt
# into it, then runs manual_build/build.py through that venv's interpreter.
#
# Run `make help` (or just `make`) for a list of targets.

VENV_DIR := manual_build/.venv
PYTHON   := $(VENV_DIR)/bin/python3
REQUIREMENTS := manual_build/requirements.txt

.DEFAULT_GOAL := help
.PHONY: help venv build list clean-venv clean-deps clean

help: ## Show this help
	@echo "Usage: make <target> [SHIELD=<name>] [NUM=<n>] [BOARD=<name>]"
	@echo
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo
	@echo "Examples:"
	@echo "  make build SHIELD=dongle_charybdis_right   # build one target by shield name"
	@echo "  make build NUM=1                           # build by index (see 'make list')"
	@echo "  make build                                 # interactive picker"
	@echo "  make list                                  # show all build.yaml targets"

venv: $(VENV_DIR)/.deps-installed ## Create the venv (if missing) and install dependencies into it

$(VENV_DIR)/pyvenv.cfg:
	uv venv $(VENV_DIR)

$(VENV_DIR)/.deps-installed: $(VENV_DIR)/pyvenv.cfg $(REQUIREMENTS)
	uv pip install --python $(PYTHON) -r $(REQUIREMENTS)
	touch $(VENV_DIR)/.deps-installed

build: venv ## Build firmware (SHIELD=<name>, NUM=<n>, or BOARD=<name>; omit for interactive picker)
	$(PYTHON) manual_build/build.py \
		$(if $(SHIELD),-s "$(SHIELD)") \
		$(if $(BOARD),-b "$(BOARD)") \
		$(if $(NUM),-n $(NUM))

list: venv ## List available build configurations from build.yaml
	$(PYTHON) manual_build/build.py -l

clean-deps: venv ## Remove the downloaded west workspace + build artifacts (forces a full re-fetch)
	$(PYTHON) manual_build/build.py --clean

clean-venv: ## Remove the venv itself
	rm -rf $(VENV_DIR)

clean: clean-deps clean-venv ## Remove venv, west workspace, and build artifacts
