"""A tiny module to read environment variables and tranform them.

Examples::
    >>> import envyronment as env
    >>> import os
    >>> os.environ["MY_INT"] = "42"
    >>> env.read("MY_INT", astype=int)
    42
    >>> env.read("MY_STR", default="default_value")
    'default_value'
    >>> env.read("MY_STR")
    Traceback (most recent call last):
        ...
    envyronment.MissingEnvironmentVariableError: Environment variable MY_STR is not set.
"""

import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

try:
    from dotenv import load_dotenv  # type: ignore[reportMissingImports]
except ImportError:
    """Could not import dotenv.load_dotenv."""
else:
    load_dotenv()

T = TypeVar("T")


class MissingEnvironmentVariableError(Exception):
    """Raised when an environment variable is missing."""


class _Missing:
    """Sentinel to represent a missing value."""


_MISSING = _Missing()


def read(
    name: str, default: T | _Missing = _MISSING, *, astype: Callable[..., T] = str, convert_default: bool = False
) -> T:
    """Read a value from the environment and call astype with the value as argument.

    The default value will be converted using astype if convert_default is True.
    A MissingEnvironmentVariableError will be raised if the environment variable is not set and no default is provided.

    Errors raised by astype will propagate to the caller.

    Note: astype must be able to accept a single str argument.
    """
    try:
        value = os.environ[name]
    except KeyError as exc:
        if isinstance(default, _Missing):
            raise MissingEnvironmentVariableError(f"Environment variable {name} is not set.") from exc
        if convert_default:
            return astype(default)
        return default
    return astype(value)


def to_bool(value: str) -> bool:
    """Convert a string to a boolean.

    Recognizes 'true', '1', 'yes', 'on' (case-insensitive) as True.
    Recognizes 'false', '0', 'no', 'off' (case-insensitive) as False.
    Raises ValueError for unrecognized values.
    """
    true_values = {"true", "1", "yes", "on"}
    false_values = {"false", "0", "no", "off"}

    value_lower = value.strip().lower()
    if value_lower in true_values:
        return True
    if value_lower in false_values:
        return False
    raise ValueError(f"Cannot convert '{value}' to bool. True values: {true_values}. False values: {false_values}.")


def to_json(value: str):
    """Convert a JSON string to a Python object.

    This can be used to convert to dict, list, etc., depending on the JSON structure.
    """
    return json.loads(value)


def to_list(value: str) -> list[str]:
    """Convert a comma-separated string to a list of strings."""
    return [item.strip() for item in value.split(",") if item.strip()]


def to_filepath(value: str | Path):
    """Convert the value to a Path and ensure the file and its parents exist."""
    path = Path(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)
    return path


def to_dirpath(value: str | Path):
    """Convert the value to a Path and ensure the directory exists.

    Prints a warning if the directory could not be created.
    """
    path = Path(value)
    path.mkdir(parents=True, exist_ok=True)
    return path
