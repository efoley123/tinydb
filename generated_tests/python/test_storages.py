import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from unittest.mock import patch, mock_open
from tinydb.storages import Storage, JSONStorage, MemoryStorage, touch
import os
import json
from io import UnsupportedOperation


@pytest.fixture
def mock_storage_path(tmp_path):
    return tmp_path / "test.db"


def test_touch_creates_file_and_directories():
    with patch("os.path.exists", return_value=False), \
         patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", mock_open()) as mock_file:
        touch("/fake/path/test.db", create_dirs=True)
        
    mock_makedirs.assert_called_once_with("/fake/path")
    mock_file.assert_called_once_with("/fake/path/test.db", 'a')


def test_touch_does_not_create_directories_when_not_needed():
    with patch("os.path.exists", return_value=True), \
         patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", mock_open()) as mock_file:
        touch("/fake/path/test.db", create_dirs=False)
        
    mock_makedirs.assert_not_called()
    mock_file.assert_called_once_with("/fake/path/test.db", 'a')


def test_json_storage_init_creates_file_if_not_exists(mock_storage_path):
    with patch("tinydb.storages.touch") as mock_touch:
        JSONStorage(str(mock_storage_path), create_dirs=True)
        
    mock_touch.assert_called_once_with(str(mock_storage_path), create_dirs=True)


def test_json_storage_write_and_read(mock_storage_path):
    data = {"key": "value"}
    storage = JSONStorage(str(mock_storage_path))
    storage.write(data)
    assert storage.read() == data
    storage.close()


def test_json_storage_write_unsupported_operation_raises_ioerror(mock_storage_path):
    storage = JSONStorage(str(mock_storage_path), access_mode='r')
    with pytest.raises(IOError):
        storage.write({"key": "value"})


def test_memory_storage_write_and_read():
    storage = MemoryStorage()
    data = {"key": "value"}
    storage.write(data)
    assert storage.read() == data


@pytest.mark.parametrize("data", [None, {}, {"key": "value"}])
def test_memory_storage_handles_different_data_types(data):
    storage = MemoryStorage()
    storage.write(data)
    assert storage.read() == data


def test_json_storage_write_io_error(mock_storage_path):
    data = {"key": "value"}
    storage = JSONStorage(str(mock_storage_path))
    with patch.object(storage._handle, "write", side_effect=UnsupportedOperation()):
        with pytest.raises(IOError):
            storage.write(data)


def test_json_storage_close():
    with patch("builtins.open", mock_open()) as mocked_file:
        storage = JSONStorage("/fake/path.json")
        storage.close()
        mocked_file().close.assert_called_once()


def test_json_storage_flush_and_truncate_on_write(mock_storage_path):
    data = {"key": "value"}
    storage = JSONStorage(str(mock_storage_path))
    with patch.object(storage._handle, "flush") as mock_flush, \
         patch.object(storage._handle, "truncate") as mock_truncate:
        storage.write(data)
        mock_flush.assert_called_once()
        mock_truncate.assert_called_once()


def test_abstract_storage_implementation_raises_not_implemented_error():
    class CustomStorage(Storage):
        pass

    with pytest.raises(TypeError):
        CustomStorage()