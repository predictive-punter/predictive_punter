import concurrent.futures
from datetime import datetime
from getopt import getopt
import logging
import time

import cache_requests
from lxml import html
import punters_client
import pymongo
import racing_data
import redis
import requests

from . import Provider
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
            'logging_level':    logging.INFO,
            'redis_uri':        'redis://localhost:6379/0'
        }

        opts, args = getopt(args, 'bd:qr:v', ['backup-database', 'database-uri=', 'quiet', 'redis-uri=', 'verbose'])

        for opt, arg in opts:

            if opt in ('-b', '--backup-database'):
                config['backup_database'] = True

            elif opt in ('-d', '--database-uri'):
                config['database_uri'] = arg

            elif opt in ('-q', '--quiet'):
                config['logging_level'] = logging.WARNING

            elif opt in ('-r', '--redis-uri'):
                config['redis_uri'] = arg

            elif opt in ('-v', '--verbose'):
                config['logging_level'] = logging.DEBUG

        if len(args) > 0:
            config['date_from'] = config['date_to'] = datetime.strptime(args[-1], '%Y-%m-%d')
            if len(args) > 1:
                config['date_from'] = datetime.strptime(args[0], '%Y-%m-%d')

        return config

    def __init__(self, *args, **kwargs):

        logging.basicConfig(level=kwargs['logging_level'])

        database_client = pymongo.MongoClient(kwargs['database_uri'])
        self.database = database_client.get_default_database()
        self.do_database_backups = kwargs['backup_database']

        http_client = None
        try:
            http_client = cache_requests.Session(connection=redis.from_url(kwargs['redis_uri']))
        except BaseException:
            try:
                http_client = cache_requests.Session()
            except BaseException:
                http_client = requests.Session()

        html_parser = html.fromstring

        scraper = punters_client.Scraper(http_client, html_parser)
        
        self.provider = Provider(self.database, scraper)

    def backup_database(self):
        """Backup the database if backup_database is available"""

        for backup_name in [collection for collection in self.database.collection_names(False) if '_backup' in collection]:
            self.database.drop_collection(backup_name)

        for collection_name in [collection for collection in self.database.collection_names(False) if '_backup' not in collection]:
            backup_name = collection_name + '_backup'
            self.database[collection_name].aggregate([{'$out': backup_name}])

    def restore_database(self):
        """Restore the database if backup_database is available"""

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

                futures = {process_item(item): item for item in collection}

                for future in concurrent.futures.as_completed(futures):
                    if future.exception() is not None:
                        logging.critical('An exception occurred while processing {item}'.format(item=futures[future]))
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
            logging.critical('An exception occurred while processing date {date:%Y-%m-%d}'.format(date=date))
            if self.do_database_backups:
                log_time('restoring database from backup', self.restore_database)
            raise

        else:
            if self.do_database_backups:
                log_time('backing up the database', self.backup_database)

            racing_data.Runner.jockey_career_cache.clear()
            racing_data.Runner.jockey_last_12_months_cache.clear()
            racing_data.Runner.jockey_on_firm_cache.clear()
            racing_data.Runner.jockey_on_good_cache.clear()
            racing_data.Runner.jockey_on_heavy_cache.clear()
            racing_data.Runner.jockey_on_soft_cache.clear()
            racing_data.Runner.jockey_on_synthetic_cache.clear()
            racing_data.Runner.jockey_on_turf_cache.clear()

    def process_meet(self, meet):
        """Process the specified meet"""

        self.process_collection(meet.races, self.process_race)

    def process_race(self, race):
        """Process the specified race"""

        self.process_collection(race.runners, self.process_runner)

    def process_runner(self, runner):
        """Process the specified runner"""

        if runner.horse is not None:
            log_time('processing {horse}'.format(horse=runner.horse), self.process_horse, runner.horse)

        if runner.jockey is not None:
            log_time('processing {jockey}'.format(jockey=runner.jockey), self.process_jockey, runner.jockey)

        if runner.trainer is not None:
            log_time('processing {trainer}'.format(trainer=runner.trainer), self.process_trainer, runner.trainer)

    def process_horse(self, horse):
        """Process the specified horse"""

        horse.performances

    def process_jockey(self, jockey):
        """Process the specified jockey"""

        pass

    def process_trainer(self, trainer):
        """Process the specified trainer"""

        pass
