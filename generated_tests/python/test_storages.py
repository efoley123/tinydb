import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from unittest.mock import mock_open, patch
from tinydb.storages import JSONStorage, MemoryStorage, Storage, touch
import os
import io

# Test for touch function
def test_touch_creates_file():
    with patch("os.path.exists", return_value=False), \
        patch("os.makedirs") as mock_makedirs, \
        patch("builtins.open", mock_open()) as mocked_file:
        touch("/fake/path/db.json", create_dirs=True)
        mocked_file.assert_called_once_with("/fake/path/db.json", 'a')
        mock_makedirs.assert_called_once_with("/fake/path")

def test_touch_without_create_dirs():
    with patch("os.path.exists", return_value=True), \
        patch("builtins.open", mock_open()) as mocked_file:
        touch("/fake/path/db.json", create_dirs=False)
        mocked_file.assert_called_once_with("/fake/path/db.json", 'a')

# Test for JSONStorage
@pytest.fixture
def json_storage(tmp_path):
    path = tmp_path / "test.json"
    storage = JSONStorage(str(path))
    yield storage
    storage.close()

def test_json_storage_write_and_read(json_storage):
    test_data = {"key": "value"}
    json_storage.write(test_data)
    assert json_storage.read() == test_data

def test_json_storage_write_raises_ioerror_with_invalid_mode():
    with pytest.raises(IOError):
        json_storage = JSONStorage("/fake/path", access_mode='w')
        json_storage.write({"key": "value"})

def test_json_storage_close():
    with patch("builtins.open", mock_open()) as mocked_file:
        storage = JSONStorage("/fake/path")
        storage.close()
        mocked_file().close.assert_called_once()

def test_json_storage_empty_file_returns_none():
    with patch("builtins.open", mock_open(read_data="")) as mocked_file, \
         patch("os.path.getsize", return_value=0):
        storage = JSONStorage("/fake/path")
        assert storage.read() is None

# Test for MemoryStorage
def test_memory_storage_write_and_read():
    storage = MemoryStorage()
    test_data = {"key": "value"}
    storage.write(test_data)
    assert storage.read() == test_data

def test_memory_storage_is_isolated():
    storage1 = MemoryStorage()
    storage2 = MemoryStorage()
    data1 = {"data": 1}
    data2 = {"data": 2}
    storage1.write(data1)
    storage2.write(data2)
    assert storage1.read() != storage2.read()

# Custom Storage subclass to test abstract base class enforcement
def test_storage_abc_enforcement():
    with pytest.raises(TypeError):
        class InvalidStorage(Storage):
            pass
        InvalidStorage()

# Mocking os for touch function failure scenarios
def test_touch_with_os_makedirs_exception():
    with patch("os.path.exists", return_value=False), \
         patch("os.makedirs", side_effect=Exception("Mocked exception")):
        with pytest.raises(Exception):
            touch("/fake/path/db.json", create_dirs=True)

def test_json_storage_with_unsupported_operation():
    with pytest.raises(IOError):
        with patch("builtins.open", mock_open()) as mocked_file:
            mocked_file().write.side_effect = io.UnsupportedOperation
            storage = JSONStorage("/fake/path", access_mode='r')
            storage.write({"key": "value"})