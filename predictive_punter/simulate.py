import sys

from . import Command


class SimulateCommand(Command):
    """Command line utility to simulate predictions for all races in a specified date range"""

    def post_process_race(self, race):
        """Generate predictions for the race after the race has been processed"""

        race.predictions


def main():
    """Main entry point for simulate console script"""

    SimulateCommand.main(sys.argv[1:])
