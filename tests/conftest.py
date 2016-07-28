from datetime import datetime, timedelta

import cache_requests
from lxml import html
import predictive_punter
import punters_client
import pymongo
import pytest
import redis
import requests


@pytest.fixture(scope='session')
def database(database_uri):

    database_name = database_uri.split('/')[-1]
    database_client = pymongo.MongoClient(database_uri)
    database_client.drop_database(database_name)
    return database_client.get_default_database()


@pytest.fixture(scope='session')
def database_uri():

    return 'mongodb://localhost:27017/predictive_punter_test'


@pytest.fixture(scope='session')
def provider(database):

    http_client = None
    try:
        http_client = cache_requests.Session(connection=redis.fromurl('redis://localhost:6379/predictive_punter_test'))
    except BaseException:
        try:
            http_client = cache_requests.Session()
        except BaseException:
            http_client = requests.Session()

    html_parser = html.fromstring

    scraper = punters_client.Scraper(http_client, html_parser)

    return predictive_punter.Provider(database, scraper)


@pytest.fixture(scope='session')
def race(provider):

    for meet in provider.get_meets_by_date(datetime(2016, 2, 1)):
        if meet['track'] == 'Kilmore':

            for race in meet.races:
                if race['number'] == 5:

                    return race


@pytest.fixture(scope='session')
def runner(race):

    for runner in race.runners:
        if runner['number'] == 1:

            return runner


@pytest.fixture(scope='session')
def sample(provider, runner):

    return provider.get_sample_by_runner(runner)


@pytest.fixture(scope='session')
def future_race(provider):

    meet = provider.get_meets_by_date(datetime.now() + timedelta(days=1))[0]
    return meet.races[0]
