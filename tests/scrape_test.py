import predictive_punter
import pymongo
import pytest


@pytest.fixture(scope='module')
def database(database_uri):

    database_name = database_uri.split('/')[-1]
    database_client = pymongo.MongoClient(database_uri)
    database_client.drop_database(database_name)
    return database_client.get_default_database()


@pytest.fixture(scope='module')
def database_uri():

    return 'mongodb://localhost:27017/predictive_punter_test'


@pytest.fixture(scope='module')
def scrape_command(database_uri):

    predictive_punter.ScrapeCommand.main(['-d', database_uri, '2016-2-1', '2016-2-2'])


def test_meets(database, scrape_command):
    """The scrape command should populate the database with the expected number of meets"""

    assert database['meets'].count() == 5


def test_races(database, scrape_command):
    """The scrape command should populate the database with the expected number of races"""

    assert database['races'].count() == 8 + 8 + 8 + 7 + 8


def test_runners(database, scrape_command):
    """The scrape command should populate the database with the expected number of runners"""

    assert database['runners'].count() == 11 + 14 + 14 + 15 + 10 + 17 + 11 + 15 + 8 + 9 + 11 + 9 + 11 + 10 + 13 + 16 + 10 + 6 + 11 + 11 + 9 + 9 + 14 + 10 + 9 + 11 + 13 + 18 + 11 + 10 + 14 + 10 + 15 + 13 + 12 + 11 + 11 + 14 + 16
