.PHONY: sanity

# The judges will run this command
sanity:
	@echo "Running sanity checks..."
	@mkdir -p artifacts
	@python -m backend.sanity_check
	@echo "make sanity sequence completed."