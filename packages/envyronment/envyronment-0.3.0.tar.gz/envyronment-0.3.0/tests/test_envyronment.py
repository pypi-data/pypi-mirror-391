"""Tests for env.py module."""

import importlib
import json
import sys
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch


class EnvTests(unittest.TestCase):
    """Tests for envyronment.py module."""

    def setUp(self):
        """Set up test environment."""
        self.env_module = importlib.import_module("envyronment")

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

    def test_to_bool(self):
        """Test the to_bool function."""
        true_values = ["true", "1", "yes", "on"]
        false_values = ["false", "0", "no", "off"]

        for val in true_values:
            self.assertTrue(self.env_module.to_bool(val))
            self.assertTrue(self.env_module.to_bool(val.upper()))

        for val in false_values:
            self.assertFalse(self.env_module.to_bool(val))
            self.assertFalse(self.env_module.to_bool(val.upper()))

        with self.assertRaises(ValueError):
            self.env_module.to_bool("maybe")

    def test_to_json(self):
        """Test the to_json function."""
        valid_json = '{"key": "value", "number": 123}'
        result = self.env_module.to_json(valid_json)
        self.assertEqual(result, {"key": "value", "number": 123})

        invalid_json = '{"key": "value", "number": 123'  # Missing closing brace
        with self.assertRaises(json.JSONDecodeError):
            self.env_module.to_json(invalid_json)

    def test_to_list(self):
        """Test the to_list function."""
        csv_string = "apple,banana,cherry, dragon fruit"
        result = self.env_module.to_list(csv_string)
        self.assertEqual(result, ["apple", "banana", "cherry", "dragon fruit"])

    def test_to_filepath(self):
        """Test the to_filepath function."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "testfile.txt"
            self.assertFalse(filepath.exists())  # Should not exist yet
            filepath_str = str(filepath)
            result = self.env_module.to_filepath(filepath_str)
            self.assertIsInstance(result, Path)
            self.assertEqual(str(result), filepath_str)
            self.assertTrue(filepath.is_file())

            # Try again to ensure it also works if the file exists
            result = self.env_module.to_filepath(filepath_str)
            self.assertIsInstance(result, Path)
            self.assertEqual(str(result), filepath_str)
            self.assertTrue(filepath.is_file())

            # Ensure parent directories are created
            nested_filepath = Path(tmpdir) / "nested" / "dir" / "file.txt"
            nested_filepath_str = str(nested_filepath)
            self.assertFalse(nested_filepath.exists())  # Should not exist yet
            result_nested = self.env_module.to_filepath(nested_filepath_str)
            self.assertIsInstance(result_nested, Path)
            self.assertEqual(str(result_nested), nested_filepath_str)
            self.assertTrue(nested_filepath.is_file())

    def test_to_dirpath(self):
        """Test the to_dirpath function."""
        with TemporaryDirectory() as tmpdir:
            dirpath = Path(tmpdir) / "testdir"
            dirpath_str = str(dirpath)
            self.assertFalse(dirpath.exists())  # Should not exist yet
            result_dir = self.env_module.to_dirpath(dirpath_str)
            self.assertIsInstance(result_dir, Path)
            self.assertEqual(str(result_dir), dirpath_str)
            self.assertTrue(dirpath.is_dir())

            # Try again to ensure it also works if the directory exists
            result_dir = self.env_module.to_dirpath(dirpath_str)
            self.assertIsInstance(result_dir, Path)
            self.assertEqual(str(result_dir), dirpath_str)
            self.assertTrue(dirpath.is_dir())

            # Ensure parent directories are created
            nested_dirpath = Path(tmpdir) / "nested" / "dir" / "subdir"
            nested_dirpath_str = str(nested_dirpath)
            self.assertFalse(nested_dirpath.exists())  # Should not exist yet
            result_nested_dir = self.env_module.to_dirpath(nested_dirpath_str)
            self.assertIsInstance(result_nested_dir, Path)
            self.assertEqual(str(result_nested_dir), nested_dirpath_str)
            self.assertTrue(nested_dirpath.is_dir())


class EnvLoadDotenvTests(unittest.TestCase):
    """Tests for env.py module."""

    def setUp(self):
        """Set up test environment."""
        sys.modules.pop("envyronment", None)  # Ensure our module isn't already imported

    def test_load_dotenv_called_if_available(self):
        """Test that load_dotenv() is called if python-dotenv is available."""
        fake_dotenv = types.SimpleNamespace()
        fake_dotenv.load_dotenv = Mock()

        with patch.dict(sys.modules, {"dotenv": fake_dotenv}):
            import envyronment  # noqa: F401

        fake_dotenv.load_dotenv.assert_called_once()

    def test_no_dotenv_import(self):
        """Test that module still imports if python-dotenv is missing."""
        with patch.dict(sys.modules, {"dotenv": None}):
            import envyronment  # noqa: F401
