<div align="center">
  <img src="https://raw.githubusercontent.com/dhruv13x/pyinitgen/main/pyinitgen_logo.png" alt="pyinitgen logo" width="200"/>
</div>

<div align="center">

<!-- Package Info -->
[![PyPI version](https://img.shields.io/pypi/v/pyinitgen.svg)](https://pypi.org/project/pyinitgen/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
![Wheel](https://img.shields.io/pypi/wheel/pyinitgen.svg)
[![Release](https://img.shields.io/badge/release-PyPI-blue)](https://pypi.org/project/pyinitgen/)

<!-- Build & Quality -->
[![Build status](https://github.com/dhruv13x/pyinitgen/actions/workflows/publish.yml/badge.svg)](https://github.com/dhruv13x/pyinitgen/actions/workflows/publish.yml)
[![Codecov](https://codecov.io/gh/dhruv13x/pyinitgen/graph/badge.svg)](https://codecov.io/gh/dhruv13x/pyinitgen)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25%2B-brightgreen.svg)](https://github.com/dhruv13x/pyinitgen/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linting-ruff-yellow.svg)](https://github.com/astral-sh/ruff)
![Security](https://img.shields.io/badge/security-CodeQL-blue.svg)

<!-- Usage -->
![Downloads](https://img.shields.io/pypi/dm/pyinitgen.svg)
![OS](https://img.shields.io/badge/os-Linux%20%7C%20macOS%20%7C%20Windows-blue.svg)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyinitgen.svg)](https://pypi.org/project/pyinitgen/)

<!-- License -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- Docs -->
[![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://your-docs-link)

</div>

---

# pyinitgen

Automated __init__.py generator for Python packages
Ensures every directory in your project is a proper Python package — no more mysterious ModuleNotFoundError surprises.

Perfect for:

Large refactors

Monorepos / multi-package architectures

Auto-generated project structures

Migration from namespace-less directories

CI environments ensuring package integrity



---

🚀 Features

Feature	Description

📂 Recursive scan	Walks directory tree intelligently
🛠️ Auto-creates __init__.py	Only where missing — safe & precise
🧠 Excludes system/runtime dirs	__pycache__, .git, .venv, etc.
👀 Dry-Run Mode	See what will be created first
🎯 Project-safe	Avoids touching non-Python folders
✨ Emoji status (optional)	Fancy terminal UX
🔒 Zero destructive actions	Never overwrites content



---

📦 Installation

pip install pyinitgen


---

🧠 Usage

✅ Default — scan current directory

pyinitgen

📁 Scan a specific project root

pyinitgen --base-dir src/

🔍 Preview changes (no write)

pyinitgen --dry-run

🗣️ Verbose mode

pyinitgen --verbose

🤐 Quiet mode

pyinitgen --quiet

🛑 Disable emojis

pyinitgen --no-emoji


---

📝 Example Output

Scanning: src/utils
Created src/utils/__init__.py
✅ Operation complete. Scanned 43 dirs, created 8 new __init__.py files.


---

🧩 Why this tool?

Problem	Solution

Large Python codebases without -inits	Auto insert all required files
ModuleNotFoundError during import	Ensures folders become packages
Hand-creating 50+ __init__.py files	One command 🤖
Accidental file writes?	Only creates missing files



---

⚙️ CLI Help

pyinitgen --help


---

🛡️ Safe by Design

Never touches existing files

Ignores system & irrelevant dirs by default

Supports dry-run to preview



---

💡 Tip

Use in CI to guarantee package consistency:

pyinitgen --dry-run


---

🤝 Contributing

PRs welcome — improve detection logic, add custom exclusion rules, enhance output UX.

👉 Repo: https://github.com/dhruv13x/pyinitgen


---

📜 License

MIT


---

🧭 Related Tools in the Suite

Tool	Purpose

importdoc	Import issue diagnosis
import-surgeon	Safe import refactoring
pypurge	Clean caches, venv junk
pyinitgen	Generate missing __init__.py ✅ (this project)



---

⭐ Support

If you like this tool:

⭐ Star the GitHub repo

🐍 Use it in CI & projects

📦 Recommend to Python dev friends



---