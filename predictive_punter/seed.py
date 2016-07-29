import sys

from . import Command


class SeedCommand(Command):
    """Command line utility to pre-seed query data for all active runners in a specified date range"""
    
    def process_runner(self, runner):
        """Extend the process_runner method to generate a sample if necessary"""

        super().process_runner(runner)

        if runner['is_scratched'] == False:
            runner.sample.normalized_query_data


def main():
    """Main entry point for seed console script"""

    ScrapeCommand.main(sys.argv[1:])
