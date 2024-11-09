import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
import os
import json
from unittest.mock import mock_open, patch
from tinydb.storages import JSONStorage, MemoryStorage, Storage, touch

# Helper functions
def setup_function(function):
    """
    Setup for tests that require a file.
    """
    touch('temp_test_file.json', create_dirs=True)

def teardown_function(function):
    """
    Teardown for tests that require a file.
    """
    if os.path.exists('temp_test_file.json'):
        os.remove('temp_test_file.json')
    if os.path.exists('temp_dir'):
        os.rmdir('temp_dir')

# Tests for touch function
def test_touch_create_file():
    file_path = 'temp_test_file.json'
    touch(file_path, False)
    assert os.path.exists(file_path)

def test_touch_create_dirs():
    file_path = 'temp_dir/temp_test_file.json'
    touch(file_path, True)
    assert os.path.exists(file_path)

# Tests for JSONStorage
@pytest.fixture
def json_storage(tmp_path):
    file_path = tmp_path / "data.json"
    return JSONStorage(path=str(file_path), create_dirs=True)

def test_json_storage_read_write(json_storage):
    data = {'key': 'value'}
    json_storage.write(data)
    assert json_storage.read() == data

def test_json_storage_write_error(tmp_path):
    file_path = tmp_path / "data.json"
    with pytest.raises(IOError):
        js = JSONStorage(path=str(file_path), access_mode='r')
        js.write({'key': 'value'})

def test_json_storage_empty_file(tmp_path):
    file_path = tmp_path / "empty.json"
    file_path.touch()
    js = JSONStorage(path=str(file_path))
    assert js.read() is None

# Tests for MemoryStorage
def test_memory_storage_read_write():
    storage = MemoryStorage()
    data = {'key': 'value'}
    storage.write(data)
    assert storage.read() == data

def test_memory_storage_initial_state():
    storage = MemoryStorage()
    assert storage.read() is None

# Edge case tests
def test_json_storage_unsupported_operation(tmp_path, mocker):
    file_path = tmp_path / "data.json"
    mocker.patch('builtins.open', mock_open())
    mocker.patch('os.fsync', side_effect=io.UnsupportedOperation)
    storage = JSONStorage(path=str(file_path))
    
    with pytest.raises(IOError):
        storage.write({'key': 'value'})

@pytest.mark.parametrize("access_mode", ['w', 'a', 'x'])
def test_json_storage_warning_on_dangerous_access_mode(tmp_path, access_mode):
    file_path = tmp_path / "data.json"
    with pytest.warns(UserWarning):
        JSONStorage(path=str(file_path), access_mode=access_mode)

# Tests for abstract Storage class
def test_storage_class_abstract_methods():
    with pytest.raises(TypeError):
        Storage()

# Test for touch function with existing file
def test_touch_existing_file():
    file_path = 'temp_test_file.json'
    touch(file_path, False)
    initial_mod_time = os.path.getmtime(file_path)
    touch(file_path, False)
    assert os.path.getmtime(file_path) == initial_mod_time

# Test for JSONStorage with incorrect encoding
def test_json_storage_incorrect_encoding(tmp_path):
    file_path = tmp_path / "data.json"
    js = JSONStorage(path=str(file_path), encoding='utf-8')
    data = {'key': '🔑'}
    js.write(data)
    
    with pytest.raises(UnicodeDecodeError):
        JSONStorage(path=str(file_path), encoding='ascii').read()

# Test for JSONStorage close method
def test_json_storage_close_method(json_storage):
    json_storage.close()
    with pytest.raises(ValueError):
        json_storage._handle.read()

# Setup and Teardown using pytest fixtures for file-based tests
@pytest.fixture(scope="function")
def file_setup_teardown(tmp_path):
    file_path = tmp_path / "temp_test_file.json"
    yield file_path  # This is where the test function will execute
    if file_path.exists():
        file_path.unlink()

# Using the setup and teardown fixture
def test_with_file_setup_teardown(file_setup_teardown):
    touch(str(file_setup_teardown), create_dirs=False)
    assert file_setup_teardown.exists()