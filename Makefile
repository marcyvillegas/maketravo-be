.RECIPEPREFIX := >

.PHONY: test

test:
>PYTHONPATH=. .venv/bin/pytest src/tests -v