import sys

from . import Command


class ScrapeCommand(Command):
    """Command line utility to scrape all racing data for a specified date range"""
    
    def __init__(self, *args, **kwargs):

        self.post_process_meet = self.post_process_race = self.post_process_runner = self.post_process_horse = self.process_jockey = self.process_trainer = self.process_performance = self.do_nothing

        super().__init__(*args, **kwargs)

    def do_nothing(self, entity):

        pass


def main():
    """Main entry point for scrape console script"""

    ScrapeCommand.main(sys.argv[1:])
