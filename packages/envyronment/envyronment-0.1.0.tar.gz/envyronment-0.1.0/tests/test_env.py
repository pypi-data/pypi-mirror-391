"""Tests for env.py module."""

import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


class EnvTests(unittest.TestCase):
    """Tests for env.py module."""

    def setUp(self):
        """Set up test environment."""
        self.env_module = importlib.import_module("env")

    def test_read_existing_variable(self):
        """Test reading an existing environment variable."""
        with patch.dict("os.environ", {"TEST_VAR": "123"}):
            result = self.env_module.read("TEST_VAR", astype=int)
            self.assertEqual(result, 123)

    def test_read_missing_variable_with_default(self):
        """Test reading a missing environment variable with a default value."""
        with patch.dict("os.environ", {}, clear=True):
            result = self.env_module.read("MISSING_VAR", default="default_value")
            self.assertEqual(result, "default_value")

    def test_read_missing_variable_without_default(self):
        """Test reading a missing environment variable without a default value."""
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(self.env_module.MissingEnvironmentVariableError):
                self.env_module.read("MISSING_VAR")

    def test_read_with_astype_error(self):
        """Test that errors from astype propagate."""
        with patch.dict("os.environ", {"TEST_VAR": "not_an_int"}):
            with self.assertRaises(ValueError):
                self.env_module.read("TEST_VAR", astype=int)


class EnvLoadDotenvTests(unittest.TestCase):
    """Tests for env.py module."""

    def setUp(self):
        """Set up test environment."""
        sys.modules.pop("env", None)  # Ensure our module isn't already imported

    def test_load_dotenv_called_if_available(self):
        """Test that load_dotenv() is called if python-dotenv is available."""
        fake_dotenv = types.SimpleNamespace()
        fake_dotenv.load_dotenv = Mock()

        with patch.dict(sys.modules, {"dotenv": fake_dotenv}):
            import env  # noqa: F401

        fake_dotenv.load_dotenv.assert_called_once()

    def test_no_dotenv_import(self):
        """Test that module still imports if python-dotenv is missing."""
        with patch.dict(sys.modules, {"dotenv": None}):
            import env  # noqa: F401
