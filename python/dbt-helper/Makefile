# Set up an environment to develop dbt-helper.
.PHONEY: setup
setup:
	pip3 install --no-cache-dir --force-reinstall -r requirements/requirements-dev.txt

# Check all the conding style.
.PHONY: lint
lint: lint-shell lint-python

# Check the conding style for the shell scripts.
.PHONY: lint-shell
lint-shell:
	shellcheck ./dev/*.sh

# Check the conding style for the python files.
.PHONY: lint-python
lint-python:
	bash ./dev/lint_python.sh

# Run the unit tests.
.PHONEY: test
test:
	pytest -v -s --cache-clear tests/

# Check if there is any unsafe dependency with safety.
.PHONEY: safety
safety:
	bash ./dev/safety.sh

# Generate examples of dbt-helper.
generate-examples:
	bash ./examples/run_examples.sh

# Generate Python API docs of dbt-helper
generate-docs:
	bash ./dev/generate_docs.sh