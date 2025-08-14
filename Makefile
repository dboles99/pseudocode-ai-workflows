.PHONY: lint convert test coverage spellcheck all

lint:
	python pseudo_lint.py enhanced_v2_example.pseudo

convert:
	python pseudo2py_plus_v2.py enhanced_v2_example.pseudo enhanced_v2_example.py

test:
	pytest -q

coverage:
	pytest -q --cov=. --cov-report=term-missing --cov-fail-under=80

spellcheck:
	codespell -S .git,**/*.docx -L the,tehse,behaviour -q 3

all: spellcheck lint convert coverage
