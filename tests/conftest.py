from datetime import datetime

import cache_requests
from lxml import html
import punters_client
import pymongo
import pytest
import racing_data
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

    return racing_data.Provider(database, scraper)


@pytest.fixture(scope='session')
def runner(provider):

    for meet in provider.get_meets_by_date(datetime(2016, 2, 1)):
        if meet['track'] == 'Kilmore':

            for race in meet.races:
                if race['number'] == 5:

                    for runner in race.runners:
                        if runner['number'] == 1:

                            return runner
