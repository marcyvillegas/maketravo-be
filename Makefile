.RECIPEPREFIX := >

.PHONY: test

test:
>PYTHONPATH=. .venv/bin/pytest src/tests -v

test-logs:
>PYTHONPATH=. .venv/bin/pytest --log-cli-level=DEBUG -v