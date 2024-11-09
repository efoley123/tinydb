import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from unittest.mock import mock_open, patch
import os
import json

from tinydb.storages import Storage, JSONStorage, MemoryStorage, touch

# Define test documents
test_doc = {'key': 'value'}
test_doc_empty = {}


@pytest.fixture
def setup_json_storage(tmp_path):
    """Fixture to setup a JSONStorage instance with a temporary file."""
    file = tmp_path / "test.json"
    storage = JSONStorage(path=str(file))
    yield storage, file
    storage.close()


def test_memory_storage_read_write():
    """Test MemoryStorage read and write operations."""
    storage = MemoryStorage()
    assert storage.read() is None, "Initially, storage should be empty."

    storage.write(test_doc)
    assert storage.read() == test_doc, "Storage should return the written document."

    storage.write(test_doc_empty)
    assert storage.read() == test_doc_empty, "Storage should support writing an empty document."


def test_json_storage_write_and_read(setup_json_storage):
    """Test JSONStorage write and read operations."""
    storage, file = setup_json_storage
    storage.write(test_doc)
    assert storage.read() == test_doc, "Read content should match written content."

    # Test reading from file directly
    with open(file, 'r') as f:
        assert json.load(f) == test_doc, "Direct file read should match written content."


def test_json_storage_empty_read(setup_json_storage):
    """Ensure JSONStorage correctly handles reading an empty file."""
    storage, _ = setup_json_storage
    assert storage.read() is None, "Reading an empty file should return None."


def test_json_storage_unsupported_operation(setup_json_storage):
    """Test handling of unsupported operations in JSONStorage."""
    storage, _ = setup_json_storage
    storage._handle.close()  # Close the file to simulate unsupported operation

    with pytest.raises(IOError):
        storage.write(test_doc)


def test_touch_function_creates_file(tmp_path):
    """Ensure the touch function creates a file and necessary directories."""
    file_path = tmp_path / "nested" / "file.txt"
    assert not file_path.exists(), "File should not exist before touch."

    touch(str(file_path), create_dirs=True)
    assert file_path.exists(), "File should be created by touch."


def test_storage_abc():
    """Ensure that Storage ABC cannot be instantiated directly."""
    with pytest.raises(TypeError):
        Storage()


@patch("os.makedirs")
@patch("os.path.exists", return_value=False)
@patch("builtins.open", new_callable=mock_open)
def test_touch_with_mock(mock_open, mock_exists, mock_makedirs):
    """Test the touch function with mocks to ensure file and dirs are created."""
    touch("path/to/file.txt", create_dirs=True)
    mock_exists.assert_called_once()
    mock_makedirs.assert_called_once_with("path/to")
    mock_open.assert_called_once_with("path/to/file.txt", 'a')


def test_json_storage_with_invalid_path():
    """Test JSONStorage initialization with an invalid file path."""
    with pytest.raises(IOError):
        JSONStorage("/invalid/path/to/file.json")


@pytest.mark.parametrize("data,expected", [
    (test_doc, test_doc),
    (test_doc_empty, None)  # JSONStorage should return None for an empty file
])
def test_json_storage_write_read_cycle(setup_json_storage, data, expected):
    """Test JSONStorage write and read cycle with different data."""
    storage, _ = setup_json_storage
    storage.write(data)
    assert storage.read() == expected, "The read data should match the expected result after a write."


def test_memory_storage_close():
    """Test that MemoryStorage close method doesn't raise errors."""
    storage = MemoryStorage()
    try:
        storage.close()
    except Exception as e:
        pytest.fail(f"Closing MemoryStorage raised an exception: {e}")


def test_json_storage_mode_warning():
    """Test that JSONStorage raises a warning for unsafe access modes."""
    with pytest.warns(UserWarning):
        JSONStorage(path="dummy_path", access_mode='w')