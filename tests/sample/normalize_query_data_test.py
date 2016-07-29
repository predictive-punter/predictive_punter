def test_len(sample):
    """The normalized_query_data property should return a list of the same length as raw_query_data"""

    assert len(sample.normalized_query_data) == len(sample['raw_query_data'])


def test_none_values(sample):
    """The normalized_query_data property should return a list that does not contain any None values"""

    assert len([value for value in sample.normalized_query_data if value is None]) == 0


def test_types(sample):
    """The normalizeed_query_data property should return a list of floats"""

    assert isinstance(sample.normalized_query_data, list)
    for item in sample.normalized_query_data:
        assert isinstance(item, float)
