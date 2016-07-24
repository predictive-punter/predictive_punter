import concurrent.futures
from datetime import datetime
from getopt import getopt

import cache_requests
from lxml import html
import punters_client
import pymongo
import racing_data
import redis
import requests

from .date_utils import *


class Command:
    """Common functionality for command line utilities"""

    @classmethod
    def main(cls, args):
        """Main entry point for console script"""

        config = cls.parse_args(args)
        command = cls(**config)
        command.process_dates(config['date_from'], config['date_to'])

    @classmethod
    def parse_args(cls, args):
        """Return a dictionary of configuration values based on the provided command line arguments"""
        
        config = {
            'backup_database':  False,
            'database_uri':     'mongodb://localhost:27017/predictive_punter',
            'date_from':        datetime.now(),
            'date_to':          datetime.now(),
            'redis_uri':        'redis://localhost:6379/predictive_punter'
        }

        opts, args = getopt(args, 'bd:r:', ['backup-database', 'database-uri=', 'redis-uri='])

        for opt, arg in opts:

            if opt in ('-b', '--backup-database'):
                config['backup_database'] = True

            elif opt in ('-d', '--database-uri'):
                config['database_uri'] = arg

            elif opt in ('-r', '--redis-uri'):
                config['redis_uri'] = arg

        if len(args) > 0:
            config['date_from'] = config['date_to'] = datetime.strptime(args[-1], '%Y-%m-%d')
            if len(args) > 1:
                config['date_from'] = datetime.strptime(args[0], '%Y-%m-%d')

        return config

    def __init__(self, *args, **kwargs):

        database_client = pymongo.MongoClient(kwargs['database_uri'])
        self.database = database_client.get_default_database()

        self.backup_database_name = None
        if kwargs['backup_database'] == True:
            self.backup_database_name = self.database.name + '_backup'

        http_client = None
        try:
            http_client = cache_requests.Session(connection=redis.fromurl(kwargs['redis_uri']))
        except BaseException:
            try:
                http_client = cache_requests.Session()
            except BaseException:
                http_client = requests.Session()

        html_parser = html.fromstring

        scraper = punters_client.Scraper(http_client, html_parser)
        
        self.provider = racing_data.Provider(self.database, scraper)

    def backup_database(self):
        """Backup the database if backup_database is available"""
        
        if self.backup_database_name is not None:
            self.database.client.drop_database(self.backup_database_name)
            self.database.client.admin.command('copydb', fromdb=self.database.name, todb=self.backup_database_name)

    def restore_database(self):
        """Restore the database if backup_database is available"""

        if self.backup_database_name is not None:
            self.database.client.drop_database(self.database.name)
            self.database.client.admin.command('copydb', fromdb=self.backup_database_name, todb=self.database.name)

    def process_collection(self, collection, target):
        """Asynchronously process all items in collection via target"""

        with concurrent.futures.ThreadPoolExecutor() as executor:

            futures = [executor.submit(target, item) for item in collection]

            for future in concurrent.futures.as_completed(futures):
                if future.exception() is not None:
                    raise future.exception()

    def process_dates(self, date_from, date_to):
        """Process all racing data for the specified date range"""

        for date in dates(date_from, date_to):
            self.process_date(date)

    def process_date(self, date):
        """Process all racing data for the specified date"""

        try:
            self.process_collection(self.provider.get_meets_by_date(date), self.process_meet)

        except BaseException:
            self.restore_database()
            raise

        else:
            self.backup_database()

    def process_meet(self, meet):
        """Process the specified meet"""

        self.process_collection(meet.races, self.process_race)

    def process_race(self, race):
        """Process the specified race"""

        self.process_collection(race.runners, self.process_runner)

    def process_runner(self, runner):
        """Process the specified runner"""

        self.process_horse(runner.horse)

        runner.jockey
        runner.trainer

    def process_horse(self, horse):
        """Process the specified horse"""

        horse.performances
