import sys

from . import Command


class ScrapeCommand(Command):
    """Command line utility to scrape all racing data for a specified date range"""
    pass


def main():
    """Main entry point for scrape console script"""

    ScrapeCommand.main(sys.argv[1:])
