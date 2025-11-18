"""
@Author = 'Michael Stanley'

============ Change Log ============
11/11/2025 = Created.

============ License ============
Copyright (C) 2025 Michael Stanley

MIT License
"""
from red_aluminum import convert_data_for_output

def test_empty_dict():
    data = {}
    result = convert_data_for_output(data=data)
    
    assert isinstance(result, str)
    assert not result


def test_single_entry_dict():
    key_1 = "foo"
    value_1 = "Lorem ipsum dolor"
    data = {key_1 : value_1}
    result = convert_data_for_output(data=data)
    
    expected_result = f"{key_1} = {value_1}"

    assert result == expected_result


def test_three_entry_dict():
    key_1 = "foo"
    value_1 = "Lorem ipsum dolor"
    key_2 = "bar"
    value_2 = "sit amet consectetur"
    key_3 = "baz"
    value_3 = "adipiscing elit quisque"
    data = {
        key_1 : value_1,
        key_2 : value_2,
        key_3 : value_3
    }
    result = convert_data_for_output(data=data)
    
    expected_result = f"{key_2} = {value_2}\n{key_3} = {value_3}\n{key_1} = {value_1}"

    assert result == expected_result
