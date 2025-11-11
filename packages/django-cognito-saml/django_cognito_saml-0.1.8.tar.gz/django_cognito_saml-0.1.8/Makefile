# Print this help message
help:
	@echo && awk '/^#/ {c=substr($$0,3); next} c && /^([a-zA-Z].+):/{ print "  \033[32m" $$1 "\033[0m",c }{c=0}' $(MAKEFILE_LIST) | column -s: -t | less -R

# Sort python files
isort:
	@echo "--- 🐍 Isorting 🐍 ---"
	uv run isort .

# Lint python files
ruff:
	@echo "--- 👏 Ruffing 👏 ---"
	uv run ruff .

# Format python files
black:
	@echo "--- 🎩 Blacking 🎩 ---"
	uv run black .

# Typecheck python files
mypy:
	@echo "--- ⚡ Mypying ⚡ ---"
	uv run mypy .

# Run tests in ci. Including setting up docker
# Run all tests locally
test:
	@echo "--- 💃 Testing 💃 ---"
	uv run pytest


# Test and lint in CI
ci: test lint


precommit:
	pre-commit run --all-files

# Run all linters
lint: isort ruff black mypy
