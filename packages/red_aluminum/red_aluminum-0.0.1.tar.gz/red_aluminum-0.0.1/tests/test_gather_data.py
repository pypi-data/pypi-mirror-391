"""
@Author = 'Michael Stanley'

============ Change Log ============
11/10/2025 = Created.

============ License ============
Copyright (C) 2025 Michael Stanley

MIT License
"""
from red_aluminum import gather_data

import pytest
from pathlib import Path
from wmul_test_utils import make_namedtuple, assert_has_only_these_calls


@pytest.fixture(scope="function")
def setup_gather_data(mocker):
    def read_file_data(file_item: Path):
        name_reversed = file_item.stem[::-1]
        return f"{name_reversed}{name_reversed}"
    
    mock_read_file_data = mocker.Mock(side_effect=read_file_data)
    
    mocker.patch("red_aluminum.read_file_data", mock_read_file_data)

    return make_namedtuple(
        "setup_gather_data",
        mock_read_file_data=mock_read_file_data
    )


def test_read_empty_folder(setup_gather_data, fs):
    mock_read_file_data = setup_gather_data.mock_read_file_data

    folder = Path("/temp/")
    fs.create_dir(folder)

    result = gather_data(folder=folder)

    assert isinstance(result, dict)
    assert not result
    
    mock_read_file_data.assert_not_called()


def test_read_folder_one_text_file(setup_gather_data, fs):
    mock_read_file_data = setup_gather_data.mock_read_file_data

    folder = Path("/temp/")
    fs.create_dir(folder)

    file_1_stem = "foo"
    file_1 = folder / f"{file_1_stem}.txt"
    file_1_contents = "Lorem Ipsum"
    fs.create_file(file_1, contents=file_1_contents)

    result = gather_data(folder=folder)

    assert result
    assert result[file_1_stem] == "oofoof"

    assert len(result) == 1

    mock_read_file_data.assert_called_once_with(file_item=file_1)


def test_read_folder_two_text_files(setup_gather_data, fs, mocker):
    mock_read_file_data = setup_gather_data.mock_read_file_data

    folder = Path("/temp/")
    fs.create_dir(folder)

    file_1_stem = "foo"
    file_1 = folder / f"{file_1_stem}.txt"
    file_1_contents = "Lorem Ipsum"
    fs.create_file(file_1, contents=file_1_contents)

    file_2_stem = "bar"
    file_2 = folder / f"{file_2_stem}.txt"
    file_2_contents = "dolor sit amet"
    fs.create_file(file_2, contents=file_2_contents)

    result = gather_data(folder=folder)

    assert result
    assert result[file_1_stem] == "oofoof"
    assert result[file_2_stem] == "rabrab"

    assert len(result) == 2

    expected_calls = [
        mocker.call(file_item=file_1),
        mocker.call(file_item=file_2)
    ]

    assert_has_only_these_calls(mock=mock_read_file_data, calls=expected_calls, any_order=True)


def test_read_folder_one_non_text_file(setup_gather_data, fs):
    mock_read_file_data = setup_gather_data.mock_read_file_data

    folder = Path("/temp/")
    fs.create_dir(folder)

    file_1_stem = "foo"
    file_1 = folder / f"{file_1_stem}.bat"
    file_1_contents = "Lorem Ipsum"
    fs.create_file(file_1, contents=file_1_contents)

    result = gather_data(folder=folder)

    assert isinstance(result, dict)
    assert not result
    
    mock_read_file_data.assert_not_called()


def test_read_folder_many_mixed_file(setup_gather_data, fs, mocker):
    mock_read_file_data = setup_gather_data.mock_read_file_data

    folder = Path("/temp/")
    fs.create_dir(folder)

    file_1_stem = "foo"
    file_1 = folder / f"{file_1_stem}.bat"
    file_1_contents = "Lorem Ipsum"
    fs.create_file(file_1, contents=file_1_contents)

    file_2_stem = "bar"
    file_2 = folder / f"{file_2_stem}.txt"
    file_2_contents = "dolor sit amet"
    fs.create_file(file_2, contents=file_2_contents)

    file_3_stem = "baz"
    file_3 = folder / f"{file_3_stem}.txt"
    file_3_contents = "consectetur adipiscing"
    fs.create_file(file_3, contents=file_3_contents)

    file_4_stem = "elit"
    file_4 = folder / f"{file_4_stem}.docx"
    file_4_contents = "quisque faucibus ex"
    fs.create_file(file_4, contents=file_4_contents)

    result = gather_data(folder=folder)

    assert result
    assert not file_1_stem in result
    assert result[file_2_stem] == "rabrab"
    assert result[file_3_stem] == "zabzab"
    assert not file_4_stem in result

    assert len(result) == 2

    expected_calls = [
        mocker.call(file_item=file_2),
        mocker.call(file_item=file_3)
    ]

    assert_has_only_these_calls(mock=mock_read_file_data, calls=expected_calls, any_order=True)
