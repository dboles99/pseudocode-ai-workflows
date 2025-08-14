![CI](https://github.com/dboles99/pseudocode-ai-workflows/actions/workflows/pseudocode-ci.yml/badge.svg)

# pseudocode-ai-workflows

Research->code pipeline: pseudocode -> Python/PowerShell with contracts (REQUIRES/ENSURES), timeouts, retries, CI, tests, and an APA 7.0 paper.

## Features
- Pseudocode specs + examples (`pseudocode/`)
- Python implementations and tools (`src/python/`), PowerShell wrapper (`src/powershell/`)
- Tests (`tests/`) and GitHub Actions CI (codespell + pytest + coverage)
- Large assets tracked via Git LFS (DOCX, PNG)
- Final paper (DOCX) under `paper/` (also attach to a Release for nice downloads)

## Structure

~~~text
.github/workflows/    # CI
assets/images/        # figures
paper/                # final paper (DOCX) + drafts/
pseudocode/           # *.pseudo specs
src/python/           # converters, examples, linter
src/powershell/       # PseudoToPy.ps1
tests/                # unit tests
~~~
