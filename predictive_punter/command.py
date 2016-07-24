import concurrent.futures
from datetime import datetime
from getopt import getopt
import time

import cache_requests
from lxml import html
import punters_client
import pymongo
import racing_data
import redis
import requests

from .date_utils import *
from .profiling_utils import *


class Command:
    """Common functionality for command line utilities"""

    @classmethod
    def main(cls, args):
        """Main entry point for console script"""

        config = cls.parse_args(args)
        command = cls(**config)
        log_time('processing dates from {date_from:%Y-%m-%d} to {date_to:%Y-%m-%d}'.format(date_from=config['date_from'], date_to=config['date_to']), command.process_dates, config['date_from'], config['date_to'])

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
        self.do_database_backups = kwargs['backup_database']

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
        
        if self.do_database_backups:

            for backup_name in [collection for collection in self.database.collection_names(False) if '_backup' in collection]:
                self.database.drop_collection(backup_name)

            for collection_name in [collection for collection in self.database.collection_names(False) if '_backup' not in collection]:
                backup_name = collection_name + '_backup'
                self.database[collection_name].aggregate([{'$out': backup_name}])

    def restore_database(self):
        """Restore the database if backup_database is available"""

        if self.do_database_backups:

            for collection_name in [collection for collection in self.database.collection_names(False) if '_backup' not in collection]:
                self.database.drop_collection(collection_name)

            for backup_name in [collection for collection in self.database.collection_names(False) if '_backup' in collection]:
                collection_name = backup_name.replace('_backup', '')
                self.database[backup_name].aggregate([{'$out': collection_name}])

    def process_collection(self, collection, target):
        """Asynchronously process all items in collection via target"""

        if len(collection) > 0:

            with concurrent.futures.ThreadPoolExecutor() as executor:

                def process_item(item, retry_count=0, max_retries=5):
                    try:
                        return executor.submit(log_time, 'processing {item}'.format(item=item), target, item)
                    except RuntimeError:
                        if retry_count < max_retries:
                            time.sleep(1)
                            return process_item(item, retry_count + 1, max_retries)
                        else:
                            raise

                futures = [process_item(item) for item in collection]

                for future in concurrent.futures.as_completed(futures):
                    if future.exception() is not None:
                        raise future.exception()

    def process_dates(self, date_from, date_to):
        """Process all racing data for the specified date range"""

        for date in dates(date_from, date_to):
            log_time('processing date {date:%Y-%m-%d}'.format(date=date), self.process_date, date)

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
