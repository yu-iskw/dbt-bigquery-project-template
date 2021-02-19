# Set up an environment to use the project.
.PHONY: setup
setup:
	pip3 install --no-cache-dir --force-reinstall -r requirements.txt
	# The project is not probably set in the beginning, but the command below works.
	dbt deps --profiles-dir ./profiles --profile default --target dev

# Lint all together.
.PHONY: lint
lint: lint-yaml lint-shell lint-docker

# Lint YAML files.
.PHONY: lint-yaml
lint-yaml:
	bash ./ci/lint_yaml.sh
	bash ./ci/check_dbt_sources.sh

# Lint shell scripts.
.PHONY: lint-shell
lint-shell:
	bash ./ci/lint_bash.sh

# Lint docker files.
.PHONY: lint-docker
lint-docker:
	bash ./ci/lint_dockerfiles.sh