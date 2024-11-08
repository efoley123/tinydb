import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from unittest.mock import mock_open, patch
from tinydb.storages import Storage, JSONStorage, MemoryStorage, touch
import os
import json
import io

# Fixture for temporary files
@pytest.fixture
def temp_file(tmp_path):
    return tmp_path / "temp_file.json"

# Test for touch function
def test_touch_creates_file(temp_file):
    touch(str(temp_file), False)
    assert temp_file.exists()

def test_touch_creates_file_with_dirs(temp_file):
    deep_file = temp_file / "deep" / "deep_file.json"
    touch(str(deep_file), True)
    assert deep_file.exists()

# Mock base class to test abstract methods
class MockStorage(Storage):
    def read(self):
        pass
    
    def write(self, data):
        pass

# Test Storage base class
def test_storage_cannot_instantiate_directly():
    with pytest.raises(TypeError):
        Storage()

def test_mock_storage_can_instantiate():
    assert MockStorage() is not None

# Tests for JSONStorage
def test_jsonstorage_init_creates_file(mocker, temp_file):
    m_open = mock_open()
    mocker.patch("builtins.open", m_open)
    mocker.patch("os.path.exists", return_value=False)
    mocker.patch("os.makedirs")
    JSONStorage(str(temp_file), True)
    m_open.assert_called_once_with(str(temp_file), mode='r+', encoding=None)

def test_jsonstorage_write_and_read(temp_file):
    data = {"key": "value"}
    storage = JSONStorage(str(temp_file))
    storage.write(data)
    assert storage.read() == data

def test_jsonstorage_write_unsupported_operation_raises_ioerror(temp_file):
    storage = JSONStorage(str(temp_file), access_mode='r')
    with pytest.raises(IOError):
        storage.write({"key": "value"})

# Test for MemoryStorage
def test_memorystorage_write_and_read():
    storage = MemoryStorage()
    data = {"key": "value"}
    storage.write(data)
    assert storage.read() == data

def test_memorystorage_isolation():
    storage1 = MemoryStorage()
    storage2 = MemoryStorage()
    data1 = {"key1": "value1"}
    data2 = {"key2": "value2"}
    storage1.write(data1)
    storage2.write(data2)
    assert storage1.read() != storage2.read()

# Edge Cases
def test_jsonstorage_read_empty_file_returns_none(temp_file):
    temp_file.write_text("")  # Ensure file is empty
    storage = JSONStorage(str(temp_file))
    assert storage.read() is None

def test_jsonstorage_read_invalid_json_raises_jsonerror(temp_file):
    temp_file.write_text("invalid json")
    storage = JSONStorage(str(temp_file))
    with pytest.raises(json.JSONDecodeError):
        storage.read()

def test_jsonstorage_close(mocker, temp_file):
    m_open = mock_open()
    mocker.patch("builtins.open", m_open)
    storage = JSONStorage(str(temp_file))
    storage.close()
    m_open().close.assert_called_once()

def test_jsonstorage_flush_and_truncate_on_write(temp_file):
    data = {"key": "a" * 100}  # Long enough data
    storage = JSONStorage(str(temp_file))
    storage.write(data)  # This should flush and truncate the file
    storage.write({"key": "shorter data"})  # Shorter data to ensure truncate works
    with open(str(temp_file), 'r') as file:
        content = file.read()
        assert "a" not in content  # Check that the file was truncated after writing shorter data