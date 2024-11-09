import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
import os
import json
from unittest.mock import mock_open, patch
from tinydb.storages import JSONStorage, MemoryStorage, Storage, touch

# JSONStorage Tests

def test_json_storage_init_creates_file(tmpdir):
    """Test JSONStorage initializes and creates file if not exists."""
    fpath = tmpdir.join("test.json")
    with patch("os.path.exists", return_value=False), \
         patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", mock_open()):
        JSONStorage(str(fpath), create_dirs=True)
    mock_makedirs.assert_called_once()

def test_json_storage_write_and_read(tmpdir):
    """Test writing to and reading from a JSON storage."""
    fpath = str(tmpdir.join("test.json"))
    data = {"key": "value"}
    storage = JSONStorage(fpath)
    storage.write(data)
    assert storage.read() == data
    storage.close()

def test_json_storage_write_unsupported_operation(tmpdir):
    """Test JSONStorage.write() raises IOError on unsupported operation."""
    fpath = str(tmpdir.join("test.json"))
    storage = JSONStorage(fpath, access_mode="r")  # Read-only mode
    with pytest.raises(IOError):
        storage.write({"key": "value"})

def test_json_storage_close(tmpdir):
    """Test JSONStorage.close() method."""
    fpath = str(tmpdir.join("test.json"))
    storage = JSONStorage(fpath)
    with patch.object(storage._handle, "close") as mock_close:
        storage.close()
    mock_close.assert_called_once()

def test_json_storage_nonexisting_read(tmpdir):
    """Test JSONStorage.read() from a non-existing file."""
    fpath = str(tmpdir.join("nonexisting.json"))
    storage = JSONStorage(fpath)
    assert storage.read() is None
    storage.close()

# MemoryStorage Tests

def test_memory_storage_write_and_read():
    """Test writing to and reading from a memory storage."""
    storage = MemoryStorage()
    data = {"key": "value"}
    storage.write(data)
    assert storage.read() == data

def test_memory_storage_empty_read():
    """Test reading from an empty memory storage."""
    storage = MemoryStorage()
    assert storage.read() is None

# General Storage Tests

def test_storage_abstractmethod():
    """Test Storage class raises TypeError when not all abstract methods are implemented."""
    class IncompleteStorage(Storage):
        def read(self):
            pass
    
    with pytest.raises(TypeError):
        IncompleteStorage()

# touch function tests

def test_touch_existing_file(tmpdir):
    """Test touch does not modify an existing file."""
    fpath = tmpdir.join("existing_file")
    fpath.write("data")
    touch(str(fpath), create_dirs=False)
    assert fpath.read() == "data"

def test_touch_nonexisting_file(tmpdir):
    """Test touch creates a new file if it does not exist."""
    fpath = tmpdir.join("new_file")
    touch(str(fpath), create_dirs=False)
    assert fpath.check(file=1)

def test_touch_create_dirs(tmpdir):
    """Test touch creates missing directories when requested."""
    base_dir = tmpdir.mkdir("base_dir")
    new_dir = base_dir.join("new_dir")
    new_file = new_dir.join("new_file")
    touch(str(new_file), create_dirs=True)
    assert new_file.check(file=1)
    assert new_dir.check(dir=1)

def test_touch_no_create_dirs_missing(tmpdir):
    """Test touch does not create missing directories when not requested."""
    new_dir = tmpdir.join("missing_dir")
    new_file = new_dir.join("new_file")
    with pytest.raises(FileNotFoundError):
        touch(str(new_file), create_dirs=False)