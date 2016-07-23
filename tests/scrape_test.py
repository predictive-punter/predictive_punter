import subprocess

import pymongo


def test_meets():
    """The scrape command should populate the database with the expected number of meets"""

    database_uri = 'mongodb://localhost:27017/predictive_punter_test'
    database_name = database_uri.split('/')[-1]
    database_client = pymongo.MongoClient(database_uri)
    database_client.drop_database(database_name)

    subprocess.check_call('scrape -d {database_uri} 2016-2-1 2016-2-2'.format(database_uri=database_uri), shell=True)

    database = database_client.get_default_database()

    assert database['meets'].count() == 5
