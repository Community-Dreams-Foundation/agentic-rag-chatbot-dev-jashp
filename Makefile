# Makefile
PYTHON := $(shell command -v python3 2> /dev/null || command -v python 2> /dev/null)

.PHONY: sanity

# The judges will run this command to generate the required artifact
sanity:
	@echo "Using Python: $(PYTHON)"
	@mkdir -p artifacts
	@$(PYTHON) scripts/generate_sanity_output.py