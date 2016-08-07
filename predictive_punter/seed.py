import sys

from . import Command


class SeedCommand(Command):
    """Command line utility to pre-seed query data for all active runners in a specified date range"""

    def post_process_runner(self, runner):
        """Normalize the runner's query data after processing the runner's associated entities"""

        if runner['is_scratched'] == False:
            runner.sample.normalized_query_data


def main():
    """Main entry point for seed console script"""

    SeedCommand.main(sys.argv[1:])
