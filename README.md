> Looking for my portfolio? 👉 **https://dboles99.github.io**

![CI](https://github.com/dboles99/pseudocode-ai-workflows/actions/workflows/pseudocode-ci.yml/badge.svg)

ðŸ“„ Download the paper (DOCX):  
https://github.com/dboles99/pseudocode-ai-workflows/releases/download/v1.0.0/pseudocode_ai_imrad_WITH_APPENDICES_PLUS_V2_CI_QG.docx

ðŸ“„ **Paper**: see the v1.0.0 release assets.

ðŸ“š **Wiki:** https://github.com/dboles99/pseudocode-ai-workflows/wiki/Paper-IMRaD

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


![build](https://img.shields.io/github/actions/workflow/status/dboles99/pseudocode-ai-workflows/ci.yml?branch=main)
![coverage](https://img.shields.io/badge/coverage-80%2B%25-brightgreen)
![license](https://img.shields.io/github/license/dboles99/pseudocode-ai-workflows)
![release](https://img.shields.io/github/v/release/dboles99/pseudocode-ai-workflows)

