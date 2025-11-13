# envyronment
A tiny module to read environment variables and tranform them.

When load_dotenv is available, this is called at import time.

---
[![Code style: Ruff](https://img.shields.io/badge/style-ruff-8b5000)](https://github.com/astral-sh/ruff)
[![Typing: Pyright](https://img.shields.io/badge/typing-pyright-725a42
)](https://github.com/RobertCraigie/pyright-python)
[![Linting: Pylint](https://img.shields.io/badge/typing-pylint-755147
)](https://github.com/pylint-dev/pylint)
[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://opensource.org/license/mit)
[![CI Validation](https://github.com/shifqu/envyronment/actions/workflows/ci.yml/badge.svg)](https://github.com/shifqu/envyronment/actions/workflows/ci.yml)

---

## Features

- ✅ Simple, typed API
- ✅ Loads `.env` if installed with extra `dotenv`
- ✅ Flexible casting via `astype=...`
- ✅ Propagates errors raised in the `astype` callable
- ✅ Zero dependencies required, `python-dotenv` optionally installed

## Requirements

- Python **3.10+** (only **3.13** is tested)

## Quick start

1. Install the package
    ```bash
    pip install envyronment
    ```
    or
    ```bash
    pip install envyronment[dotenv]  # Ensure python-dotenv is also installed
    ```

2. Import and use
    ```python
    import envyronment as env

    ascii_asterisk = env.read("ASCII_ASTERISK", 42, astype=int)  # typed as int, 42 by default
    debug = env.read("DEBUG", astype=bool)  # typed as bool, required
    ```

## License

This project is licensed under the MIT License — see the [`LICENSE`](https://github.com/shifqu/envyronment/blob/main/LICENSE) file for details.