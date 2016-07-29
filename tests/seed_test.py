import predictive_punter
import pytest


@pytest.fixture(scope='module')
def seed_command(database_uri):

    predictive_punter.SeedCommand.main(['-d', database_uri, '2016-2-1', '2016-2-2'])


def test_samples(database, seed_command):
    """The seed command should populate the database with the expected number of samples"""

    assert database['samples'].count() == database['runners'].count({'is_scratched': False})


def test_values(database, seed_command):
    """The seed command should set normalized query data values for all samples"""

    for sample in database['samples'].find():
        assert sample['normalized_query_data'] is not None
