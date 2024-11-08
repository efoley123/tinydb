import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
import os
import json
from unittest.mock import mock_open, patch
from tinydb.storages import Storage, JSONStorage, MemoryStorage, touch

# Test JSONStorage

def test_jsonstorage_init_creates_file(mocker):
    mocker.patch("tinydb.storages.touch")
    JSONStorage("dummy_path.json")
    tinydb.storages.touch.assert_called_once_with("dummy_path.json", False)

def test_jsonstorage_read_empty_file(mocker):
    mocker.patch("builtins.open", mock_open(read_data=""))
    storage = JSONStorage("dummy_path.json")
    assert storage.read() is None

def test_jsonstorage_read_valid_data(mocker):
    test_data = {"data": "test"}
    mocker.patch("builtins.open", mock_open(read_data=json.dumps(test_data)))
    storage = JSONStorage("dummy_path.json")
    assert storage.read() == test_data

def test_jsonstorage_write(mocker):
    mock_file = mock_open()
    mocker.patch("builtins.open", mock_file)
    mocker.patch("os.fsync")
    storage = JSONStorage("dummy_path.json")
    test_data = {"data": "test"}
    storage.write(test_data)
    mock_file().write.assert_called_once_with(json.dumps(test_data))
    mock_file().flush.assert_called_once()
    os.fsync.assert_called_once()

def test_jsonstorage_close(mocker):
    mock_file = mock_open()
    mocker.patch("builtins.open", mock_file)
    storage = JSONStorage("dummy_path.json")
    storage.close()
    mock_file().close.assert_called_once()

# Test MemoryStorage

def test_memorystorage_read_write():
    storage = MemoryStorage()
    test_data = {"data": "test"}
    assert storage.read() is None
    storage.write(test_data)
    assert storage.read() == test_data

# Test touch function

def test_touch_existing_file(tmp_path):
    file_path = tmp_path / "test.db"
    file_path.touch()
    touch(str(file_path), False)
    assert file_path.exists()

def test_touch_non_existing_file(tmp_path):
    file_path = tmp_path / "not_exists.db"
    touch(str(file_path), True)
    assert file_path.exists()

def test_touch_create_dirs(tmp_path):
    dir_path = tmp_path / "new_dir"
    file_path = dir_path / "test.db"
    touch(str(file_path), True)
    assert file_path.exists()

# Error cases

def test_jsonstorage_init_invalid_mode_raises_warning(mocker):
    mocker.patch("warnings.warn")
    JSONStorage("dummy_path.json", access_mode='w')
    warnings.warn.assert_called()

def test_jsonstorage_write_unsupported_operation(mocker):
    mock_file = mock_open()
    mocker.patch("builtins.open", mock_file)
    mock_file().write.side_effect = io.UnsupportedOperation
    storage = JSONStorage("dummy_path.json")
    with pytest.raises(IOError):
        storage.write({"data": "test"})

def test_jsonstorage_read_invalid_json(mocker):
    mocker.patch("builtins.open", mock_open(read_data="invalid_json"))
    storage = JSONStorage("dummy_path.json")
    with pytest.raises(json.JSONDecodeError):
        storage.read()