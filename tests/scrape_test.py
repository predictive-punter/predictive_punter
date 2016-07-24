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

    predictive_punter.ScrapeCommand.main(['-b', '-d', database_uri, '2016-2-1', '2016-2-2'])


def count_distinct(collection, key, exclude=None):
    """Get the number of distinct values for key in the specified database collection"""

    values = collection.distinct(key)
    if exclude is not None and exclude in values:
        values.remove(exclude)
    return len(values)


def test_meets(database, scrape_command):
    """The scrape command should populate the database with the expected number of meets"""

    assert database['meets'].count() == database['meets_backup'].count() == 5


def test_races(database, scrape_command):
    """The scrape command should populate the database with the expected number of races"""

    assert database['races'].count() == database['races_backup'].count() == 8 + 8 + 8 + 7 + 8


def test_runners(database, scrape_command):
    """The scrape command should populate the database with the expected number of runners"""

    assert database['runners'].count() == database['runners_backup'].count() == 11 + 14 + 14 + 15 + 10 + 17 + 11 + 15 + 8 + 9 + 11 + 9 + 11 + 10 + 13 + 16 + 10 + 6 + 11 + 11 + 9 + 9 + 14 + 10 + 9 + 11 + 13 + 18 + 11 + 10 + 14 + 10 + 15 + 13 + 12 + 11 + 11 + 14 + 16


def test_horses(database, scrape_command):
    """The scrape command should populate the database with the expected number of horses"""

    assert database['horses'].count() == database['horses_backup'].count() == count_distinct(database['runners'], 'horse_url', 'https://www.punters.com.au')


def test_jockeys(database, scrape_command):
    """The scrape command should populate the database with the expected number of jockeys"""

    assert database['jockeys'].count() == database['jockeys_backup'].count() == count_distinct(database['runners'], 'jockey_url', 'https://www.punters.com.au/')


def test_trainers(database, scrape_command):
    """The scrape command should populate the database with the expected number of trainers"""

    assert database['trainers'].count() == database['trainers_backup'].count() == count_distinct(database['runners'], 'trainer_url', 'https://www.punters.com.au/')


def test_performances(database, scrape_command):
    """The scrape command should populate the database with the expected number of performances"""

    assert database['performances'].count() >= database['runners'].count({'is_scratched': False})
    assert database['performances_backup'].count() == database['performances'].count()
