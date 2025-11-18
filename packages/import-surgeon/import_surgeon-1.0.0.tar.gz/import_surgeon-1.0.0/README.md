<div align="center">
  <img src="https://raw.githubusercontent.com/dhruv13x/import-surgeon/main/import-surgeon_logo.png" alt="import-surgeon logo" width="200"/>
</div>

<div align="center">

<!-- Package Info -->
[![PyPI version](https://img.shields.io/pypi/v/import-surgeon.svg)](https://pypi.org/project/import-surgeon/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
![Wheel](https://img.shields.io/pypi/wheel/import-surgeon.svg)
[![Release](https://img.shields.io/badge/release-PyPI-blue)](https://pypi.org/project/import-surgeon/)

<!-- Build & Quality -->
[![Build status](https://github.com/dhruv13x/import-surgeon/actions/workflows/publish.yml/badge.svg)](https://github.com/dhruv13x/import-surgeon/actions/workflows/publish.yml)
[![Codecov](https://codecov.io/gh/dhruv13x/import-surgeon/graph/badge.svg)](https://codecov.io/gh/dhruv13x/import-surgeon)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25%2B-brightgreen.svg)](https://github.com/dhruv13x/import-surgeon/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linting-ruff-yellow.svg)](https://github.com/astral-sh/ruff)
![Security](https://img.shields.io/badge/security-CodeQL-blue.svg)

<!-- Usage -->
![Downloads](https://img.shields.io/pypi/dm/import-surgeon.svg)
![OS](https://img.shields.io/badge/os-Linux%20%7C%20macOS%20%7C%20Windows-blue.svg)
[![Python Versions](https://img.shields.io/pypi/pyversions/import-surgeon.svg)](https://pypi.org/project/import-surgeon/)

<!-- License -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- Docs -->
[![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://your-docs-link)

</div>


---

import-surgeon 🩺⚙️

Precision Python import refactoring — safe, atomic, AST-exact, rollback-friendly.

---

🧠 Overview

import-surgeon is an Elite import refactoring engine for Python codebases.

It precisely updates imports and moves symbols across modules without breaking your code, using full LibCST AST guarantees, backup files, atomic writes, and optional auto-formatting.

> Think of it as
libcst + git-protection + atomic rollback-safe refactor surgery



Use it for:

✅ Package restructures
✅ Module renames
✅ Moving functions/classes between files
✅ Gradual API migrations
✅ Org-wide import cleanup
✅ CI-safe automated refactors

No regex. No AST guessing. No broken imports.


---

✨ Features

Capability	Description

Accurate import rewrites	LibCST powered symbol movement (AST-exact)
Dotted name rewrites	old.module.Foo → new.module.Foo if --rewrite-dotted
Atomic file updates	Guaranteed atomic writes + metadata restore
Auto backup & rollback	--no-backup optional; --rollback supported
Supports aliases	from A import Foo as Bar handled correctly
Respects relative imports	--force-relative + auto base-package detection
Batch migrations	YAML config for multi-module migrations
Safe in CI	--require-clean-git to prevent dirty changes
Git auto-commit	--auto-commit "msg"
Optional format	Black + isort applied after changes
Warnings for risky spots	Wildcards, dotted patterns, skipped rel imports
Progress bar	tqdm fallback built-in



---

📦 Installation

pip install import-surgeon

> Optional but recommended:



pip install black isort chardet tqdm


---

🛠 Usage

Basic dry-run (default)

import-surgeon --old-module utils --new-module core.utils --symbols load,save

Apply changes

import-surgeon --old-module old.pkg --new-module new.pkg --symbols Foo,Bar --apply

Rewrite dotted usages too

import-surgeon --apply --rewrite-dotted \
  --old-module old.mod --new-module new.mod --symbols Client

Use YAML migrations file

migrate.yml

migrations:
  - old_module: old.auth
    new_module: services.auth
    symbols: [User, Token]

Run:

import-surgeon --config migrate.yml --apply

Rollback a refactor

import-surgeon --rollback --summary-json summary.json


---

🧪 Example Output

✔️ New imports inserted
✔️ Old imports removed
✔️ Diff preview in dry-run
✔️ JSON report with file list, change lines & risks


---

🔒 Safety Guarantees

Dry run by default

File backups by default

Atomic writes (no corruption)

Git-clean check option

Per-file encoding detection

Refuses unsafe wildcard rewrites unless configured



---

🧠 CLI Options (summary)

Flag	Meaning

--old-module	Old module to move from
--new-module	New module to move to
--symbols	Comma-separated symbol list
--apply	Actually write changes
--no-backup	Skip file backups
--config FILE	YAML batch config
--rollback	Rollback via summary JSON
--rewrite-dotted	Rewrite dotted uses too
--format	Run isort + black
--auto-commit	Auto-commit in git repo
--require-clean-git	Ensure repo clean before write



---

🚦 Exit Codes

Code	Meaning

0	Success
1	Changes had errors
2	CLI/config error



---

📁 Project Structure

src/import_surgeon/
  cli.py


---

🧩 Roadmap

Symbol dependency graph warnings

VSCode / PyCharm integration

Preview UI with selectable edits

Interactive TUI surgeon console

NeoVim LSP hooks



---

🤝 Contributing

PRs welcome, especially for:

Editor plugins

Safety analyzers

Batch migration assistants

Code mod multi-tool integration



---

📜 License

MIT — commercial and open use welcome.


---

⭐ Support

Star the repo — every ⭐ funds more time for DevTools research 🙏

https://github.com/dhruv13x/import-surgeon


---

> 🩺 Your imports deserve precision surgery — not blind search-replace.
Run import-surgeon and refactor with confidence.




---
