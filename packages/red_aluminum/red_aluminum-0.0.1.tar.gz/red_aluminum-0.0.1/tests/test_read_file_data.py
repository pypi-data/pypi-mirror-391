"""
@Author = 'Michael Stanley'

============ Change Log ============
11/11/2025 = Created.

============ License ============
Copyright (C) 2025 Michael Stanley

MIT License
"""
from red_aluminum import read_file_data

from pathlib import Path


def test_no_file(fs):
    folder = Path("/temp")
    fs.create_dir(folder)
    file_item = folder / "foo.txt"

    result = read_file_data(file_item=file_item)

    assert isinstance(result, str)
    assert not result


def test_single_line_file(fs):
    folder = Path("/temp")
    fs.create_dir(folder)
    file_contents = "Lorem ipsum"
    file_item = folder / "foo.txt"
    fs.create_file(file_item, contents=file_contents)

    result = read_file_data(file_item=file_item)

    assert result == file_contents


def test_multi_line_file(fs):
    folder = Path("/temp")
    fs.create_dir(folder)
    file_contents = "Lorem ipsum\ndolor sit amet\n consectetur adipiscing"
    file_item = folder / "foo.txt"
    fs.create_file(file_item, contents=file_contents)

    result = read_file_data(file_item=file_item)

    expected_result = "Lorem ipsum dolor sit amet  consectetur adipiscing"

    assert result == expected_result
