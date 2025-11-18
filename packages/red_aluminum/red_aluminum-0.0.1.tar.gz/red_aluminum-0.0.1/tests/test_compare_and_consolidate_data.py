"""
@Author = 'Michael Stanley'

============ Change Log ============
11/12/2025 = Created.

============ License ============
Copyright (C) 2025 Michael Stanley

MIT License
"""
from red_aluminum import compare_and_consolidate_data


def test_two_empty_dicts():
    new_data = {}
    old_data = {}

    consolidated_data = compare_and_consolidate_data(new_data=new_data, previous_data=old_data)

    assert isinstance(consolidated_data, dict)
    assert len(consolidated_data) == 0


def test_old_empty_new_full():
    foo_key = "foo"
    foo_value = "Lorem ipsum"
    bar_key = "bar"
    bar_value = "dolor sit amet"
    baz_key = "baz"
    baz_value = "consectetur adipiscing elit"

    new_data = {
        foo_key: foo_value,
        bar_key: bar_value,
        baz_key: baz_value
    }
    old_data = {}

    consolidated_data = compare_and_consolidate_data(new_data=new_data, previous_data=old_data)

    assert isinstance(consolidated_data, dict)
    assert len(consolidated_data) == 3
    assert consolidated_data[foo_key] == foo_value
    assert consolidated_data[bar_key] == bar_value
    assert consolidated_data[baz_key] == baz_value


def test_old_empty_new_partial():
    foo_key = "foo"
    foo_value = "Lorem ipsum"
    bar_key = "bar"
    bar_value = "dolor sit amet"
    baz_key = "baz"
    baz_value = "consectetur adipiscing elit"


    new_data = {
        foo_key: foo_value,
        bar_key: bar_value,
        baz_key: baz_value
    }
    old_data = {
        
    }

    consolidated_data = compare_and_consolidate_data(new_data=new_data, previous_data=old_data)

    assert isinstance(consolidated_data, dict)
    assert len(consolidated_data) == 3
    assert consolidated_data[foo_key] == foo_value
    assert consolidated_data[bar_key] == bar_value
    assert consolidated_data[baz_key] == baz_value


def test_old_full_new_partial():
    foo_key = "foo"
    foo_value_1 = "Lorem ipsum"
    foo_value_2 = "quisque faucibus ex"
    bar_key = "bar"
    bar_value_1 = "dolor sit amet"
    bar_value_2 = "sapien vitae pellentesque"
    baz_key = "baz"
    baz_value_1 = "consectetur adipiscing elit"
    baz_value_2 = ""


    new_data = {
        foo_key: foo_value_2,
        bar_key: bar_value_2,
        baz_key: baz_value_2
    }
    old_data = {
        foo_key: foo_value_1,
        bar_key: bar_value_1,
        baz_key: baz_value_1
    }

    consolidated_data = compare_and_consolidate_data(new_data=new_data, previous_data=old_data)

    assert isinstance(consolidated_data, dict)
    assert len(consolidated_data) == 3
    assert consolidated_data[foo_key] == foo_value_2
    assert consolidated_data[bar_key] == bar_value_2
    assert consolidated_data[baz_key] == baz_value_1


def test_old_full_new_full():
    foo_key = "foo"
    foo_value_1 = "Lorem ipsum"
    foo_value_2 = "quisque faucibus ex"
    bar_key = "bar"
    bar_value_1 = "dolor sit amet"
    bar_value_2 = "sapien vitae pellentesque"
    baz_key = "baz"
    baz_value_1 = "consectetur adipiscing elit"
    baz_value_2 = "sem placerat in"


    new_data = {
        foo_key: foo_value_2,
        bar_key: bar_value_2,
        baz_key: baz_value_2
    }
    old_data = {
        foo_key: foo_value_1,
        bar_key: bar_value_1,
        baz_key: baz_value_1
    }

    consolidated_data = compare_and_consolidate_data(new_data=new_data, previous_data=old_data)

    assert isinstance(consolidated_data, dict)
    assert len(consolidated_data) == 3
    assert consolidated_data[foo_key] == foo_value_2
    assert consolidated_data[bar_key] == bar_value_2
    assert consolidated_data[baz_key] == baz_value_2
