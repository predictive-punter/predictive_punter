import predictive_punter


def test_indexes(provider):
    """The provider should create all necessary database indexes during initialisation"""

    expected_indexes = {
        predictive_punter.Sample:   [
            [('runner_id', 1)]
        ]
    }

    for entity_type in expected_indexes:
        collection = provider.get_database_collection(entity_type)
        index_keys = [index['key'] for index in collection.index_information().values()]
        for expected_index in expected_indexes[entity_type]:
            assert expected_index in index_keys
