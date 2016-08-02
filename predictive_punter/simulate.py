import sys

from . import Command


class SimulateCommand(Command):
    """Command line utility to simulate predictions for all races in a specified date range"""
    
    def process_race(self, race):
        """Extend the process_race method to generate predictions if necessary"""

        super().process_race(race)

        race.predictions


def main():
    """Main entry point for simulate console script"""

    SimulateCommand.main(sys.argv[1:])
