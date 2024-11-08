import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
import os
import tempfile
from unittest.mock import mock_open, patch
from tinydb.storages import JSONStorage, MemoryStorage, touch

def test_touch_creates_file():
    with tempfile.TemporaryDirectory() as tmpdirname:
        file_path = os.path.join(tmpdirname, 'testfile.db')
        touch(file_path, create_dirs=False)
        assert os.path.isfile(file_path)

def test_touch_creates_file_with_directories():
    with tempfile.TemporaryDirectory() as tmpdirname:
        dir_path = os.path.join(tmpdirname, "newdir")
        file_path = os.path.join(dir_path, 'testfile.db')
        touch(file_path, create_dirs=True)
        assert os.path.isfile(file_path)

def test_touch_existing_file():
    with tempfile.NamedTemporaryFile() as tmpfile:
        touch(tmpfile.name, create_dirs=False)
        assert os.path.isfile(tmpfile.name)

@pytest.mark.parametrize("data,expected", [
    ({}, None),
    ({"key": "value"}, {"key": "value"})
])
def test_memory_storage_read_write(data, expected):
    storage = MemoryStorage()
    storage.write(data)
    assert storage.read() == expected

def test_memory_storage_isolation():
    storage1 = MemoryStorage()
    storage2 = MemoryStorage()
    storage1.write({"key": "value"})
    assert storage1.read() != storage2.read()

def test_json_storage_read_write(tmpdir):
    file_path = tmpdir.join("test.json")
    storage = JSONStorage(str(file_path))
    data = {"key": "value"}
    storage.write(data)
    assert storage.read() == data

def test_json_storage_empty_file(tmpdir):
    file_path = tmpdir.join("empty.json")
    file_path.write("")
    storage = JSONStorage(str(file_path))
    assert storage.read() is None

def test_json_storage_invalid_json(tmpdir):
    file_path = tmpdir.join("invalid.json")
    file_path.write("{not valid json}")
    storage = JSONStorage(str(file_path))
    with pytest.raises(ValueError):
        storage.read()

def test_json_storage_unsupported_mode():
    with pytest.raises(IOError):
        JSONStorage("dummy_path", access_mode='w')

def test_json_storage_write_error(monkeypatch):
    monkeypatch.setattr("builtins.open", mock_open(read_data="{}"))
    storage = JSONStorage("dummy_path")
    with pytest.raises(IOError):
        storage.write({"key": "value"})

def test_json_storage_close(tmpdir):
    file_path = tmpdir.join("test.json")
    storage = JSONStorage(str(file_path))
    storage.close()
    with pytest.raises(ValueError):
        storage._handle.read()

def test_touch_without_create_dirs_raises_error(tmpdir):
    non_existing_path = os.path.join(tmpdir, "does_not_exist", "test.db")
    with pytest.raises(FileNotFoundError):
        touch(non_existing_path, create_dirs=False)

@pytest.fixture
def mock_storage_class(monkeypatch):
    class MockStorage:
        def __init__(self, *args, **kwargs):
            pass

        def read(self):
            return {"mock": "data"}

        def write(self, data):
            pass

    monkeypatch.setattr('tinydb.storages.Storage', MockStorage)
    return MockStorage

def test_using_mock_storage(mock_storage_class):
    storage = mock_storage_class()
    assert storage.read() == {"mock": "data"}