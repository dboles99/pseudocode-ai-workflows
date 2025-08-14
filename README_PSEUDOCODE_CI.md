# Pseudocode CI Pipeline (with Coverage & Spellcheck)

This CI enforces pseudocode style, converts pseudocode to Python, runs tests, and checks code spelling.

## Local usage
```bash
pip install -r requirements.txt
make spellcheck
make lint
make convert
make coverage  # requires >=80% coverage
```

## CI steps
1. **codespell**: basic spellcheck of pseudocode/comments (ignores .docx, common domain words list can be extended).
2. **pseudo_lint.py**: ensures PURPOSE/INPUTS/OUTPUTS, REQUIRES/ENSURES, flags ambiguous words, checks PARALLEL blocks.
3. **pseudo2py_plus_v2.py**: converts `.pseudo` → Python.
4. **pytest + coverage**: runs tests with a coverage threshold (80% by default).

Artifacts include the generated Python file and coverage data.
