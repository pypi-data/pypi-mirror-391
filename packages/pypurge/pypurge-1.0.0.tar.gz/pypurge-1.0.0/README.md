<div align="center">
  <img src="https://raw.githubusercontent.com/dhruv13x/pypurge/main/pypurge_logo.png" alt="pypurge logo" width="200"/>
</div>

<div align="center">

<!-- Package Info -->
[![PyPI version](https://img.shields.io/pypi/v/pypurge.svg)](https://pypi.org/project/pypurge/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
![Wheel](https://img.shields.io/pypi/wheel/pypurge.svg)
[![Release](https://img.shields.io/badge/release-PyPI-blue)](https://pypi.org/project/pypurge/)

<!-- Build & Quality -->
[![Build status](https://github.com/dhruv13x/pypurge/actions/workflows/publish.yml/badge.svg)](https://github.com/dhruv13x/pypurge/actions/workflows/publish.yml)
[![Codecov](https://codecov.io/gh/dhruv13x/pypurge/graph/badge.svg)](https://codecov.io/gh/dhruv13x/pypurge)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25%2B-brightgreen.svg)](https://github.com/dhruv13x/pypurge/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linting-ruff-yellow.svg)](https://github.com/astral-sh/ruff)
![Security](https://img.shields.io/badge/security-CodeQL-blue.svg)

<!-- Usage -->
![Downloads](https://img.shields.io/pypi/dm/pypurge.svg)
![OS](https://img.shields.io/badge/os-Linux%20%7C%20macOS%20%7C%20Windows-blue.svg)
[![Python Versions](https://img.shields.io/pypi/pyversions/pypurge.svg)](https://pypi.org/project/pypurge/)

<!-- License -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- Docs -->
[![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://your-docs-link)

</div>


---

# 🧹 pypurge — Safe & Powerful Python Project Cleaner

**pypurge** is a production-grade Python cleanup utility designed to safely remove auto-generated files, caches, virtualenv leftovers, test artifacts, temporary files, and clutter — **without putting your system at risk.**

Think of it as a **precision broom for Python projects**.  
No more `find . -name __pycache__ -delete` or risky scripts — **clean confidently, with safety rails.**

---

## ✅ Key Features

- 🔐 **Safety-first design** — prevents accidental root-level deletion
- 🎯 **Python-specific cleanup**
  - `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `build/`, `dist/`, etc.
- 🧠 **Smart preview mode** — shows counts, groups & disk usage before deleting
- 🪪 **Stale lock & lockfile protection** — avoids multi-process conflicts
- 🕒 **Age-based filtering** — delete only items older than N days
- 📦 **Atomic backup mode** — zip backup with SHA256 manifest
- 🧪 Cleans testing & packaging leftovers
- 🧹 Optional **virtualenv purge**
- 💬 Colored interactive interface (or JSON for automation)
- 🛑 Root & dangerous directory protection
- ⚙️ Configurable via JSON (`.pypurge.json`)
- 🤖 Works safely in CI & scripts

---

## 📦 Installation

```bash
pip install pypurge

Or in development mode:

pip install -e .


---

🚀 Usage

Clean current project interactively

pypurge

Preview everything — no deletions

pypurge --preview

Clean without prompt (CI-safe)

pypurge --yes

Clean a specific folder

pypurge myproject/

Backup before deleting 🛟

pypurge --backup

Clean virtual environments too

pypurge --clean-venv

Delete only files older than 7 days

pypurge --older-than 7

Allow root / system scans (⚠️ expert mode)

pypurge --allow-root --allow-broad-root


---

✨ Example Output

=== Preview: grouped cleanup summary for .
Group                         Items   Size        Paths (truncated)
----------------------------------------------------------------------
Python Caches                 84      12.4MB
Testing/Linting/...           36      4.2MB
Build/Packaging               12      2.1MB

📁 Python Caches — 84 items, 12.4MB
  src/app/__pycache__/       — 340KB
  tests/__pycache__/         — 290KB
  ...
... and 60 more


---

⚙️ Configuration

Create a .pypurge.json in your project root:

{
  "exclude_patterns": ["re:.*migrations.*"],
  "dir_groups": {
    "CustomGroup": ["temp_run", "scratch"]
  }
}


---

🔒 Safety Rules

By default pypurge REFUSES to run in:

/

$HOME

/usr, /etc, /bin, /sbin


Unless you explicitly pass:

--allow-broad-root

Running as root also requires:

--allow-root


---

🤝 Trusted Publishing & CI

This project uses PyPI Trusted Publishing (OIDC) + GitHub Actions for secure releases.

Push tag to publish:

git tag v0.1.0
git push origin v0.1.0


---

🧠 Requirements

Python >= 3.10

No runtime dependencies



---

🪪 License

MIT © Dhruv


---

⭐ Support the Project

If this tool saved you from rm -rf nightmares…
Give it a ⭐ on GitHub — it helps a lot!


---