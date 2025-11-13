"""A tiny module to read environment variables and tranform them."""

import os
from collections.abc import Callable
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


def read(name: str, default: T | _Missing = _MISSING, *, astype: Callable[..., T] = str) -> T:
    """Read a value from the environment and call astype with the value as argument.

    If the default is returned, it will be returned as provided.
    A MissingEnvironmentVariableError will be raised if the environment variable is not set and no default is provided.

    Errors raised by astype will propagate to the caller.

    Note: astype must be able to accept a single str argument.
    """
    try:
        value = os.environ[name]
    except KeyError as exc:
        if isinstance(default, _Missing):
            raise MissingEnvironmentVariableError(f"Environment variable {name} is not set.") from exc
        return default
    return astype(value)
