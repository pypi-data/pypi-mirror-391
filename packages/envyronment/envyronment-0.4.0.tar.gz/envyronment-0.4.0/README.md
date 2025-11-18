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
    pip install "envyronment[dotenv]"
    ```
    *(the `[dotenv]` extra is optional — include it to enable `.env` file loading)*

2. Import and use
    ```python
    import envyronment as env

    some_value = env.read("SOME_VALUE", 42, astype=int)
    ```

## Example usage
```python
import os

import envyronment as env

os.environ.update(
    {
        "GREENHOUSE_NAME": "dr. greenthumb's greenhouse",
        "ENABLE_PHOTOSYNTHESIS": "yes",
        "GARDEN_TOOLS": "shovel,rake,watering_can",
        "GARDEN_PLAN": '{"flowers": ["rose", "tulip"], "vegetables": ["carrot", "tomato"]}',
        "PLANT_LOG": "/var/log/garden/plants.log",
        "GREENHOUSE_DIR": "/srv/greenhouse",
        "GREENHOUSE_STATE": "open",
    }
)


def to_upper(value: str) -> str:
    """Convert a string to an uppercase string."""
    return value.upper()


# str, required, no astype provided, so str(value) is used, value="dr. greenthumb's greenhouse"
greenhouse_name = env.read("GREENHOUSE_NAME")

# int, optional, by default 42, value=42
max_plants = env.read("MAX_PLANTS", 42, astype=int)

# bool, optional, by default False, value=True
enable_photosynthesis = env.read("ENABLE_PHOTOSYNTHESIS", default=False, astype=env.to_bool)

# list[str], required, ["shovel", "rake", "watering_can"]
garden_tools = env.read("GARDEN_TOOLS", astype=env.to_list)

# dict (due to input format), required, value={"flowers": ["rose", "tulip"], "vegetables": ["carrot", "tomato"]}
garden_plan = env.read("GARDEN_PLAN", astype=env.to_json)

# Path, optional, parent directories created, no error if it already existed, value=/var/log/garden/plants.log
# ⚠️ Default value is a string because `convert_default=True` to ensure the path is created whether default or the env value is used.
plant_log = env.read("PLANT_LOG", "/tmp/log/garden/plants.log", astype=env.to_filepath, convert_default=True)

# Path, required, parent directories created, no error if it already existed, value=/src/greenhouse
greenhouse = env.read("GREENHOUSE_DIR", astype=env.to_dirpath)

# str, optional, by default CLOSED, uses custom converter defined above, value="OPEN"
greenhouse_state = env.read("GREENHOUSE_STATE", "CLOSED", astype=to_upper)
```
## License

This project is licensed under the MIT License — see the [`LICENSE`](https://github.com/shifqu/envyronment/blob/main/LICENSE) file for details.