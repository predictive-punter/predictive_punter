def test_none_values(sample):
    """The fixed_query_data property should return a list that does not contain any None values"""

    assert len([value for value in sample.fixed_query_data if value is None]) == 0


def test_types(sample):
    """The fixed_query_data property should return a list of floats"""

    assert isinstance(sample.fixed_query_data, list)
    for item in sample.fixed_query_data:
        assert isinstance(item, float)
