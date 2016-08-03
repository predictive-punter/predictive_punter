import sys

from . import Command, Predictor


class SimulateCommand(Command):
    """Command line utility to simulate predictions for all races in a specified date range"""

    def process_date(self, date):
        """Extend the process_date method to clear predictor locks after each date"""

        super().process_date(date)

        Predictor.predictor_cache.clear()
        Predictor.predictor_locks.clear()
        self.provider.query_locks.clear()
    
    def process_race(self, race):
        """Extend the process_race method to generate predictions if necessary"""

        super().process_race(race)

        race.predictions


def main():
    """Main entry point for simulate console script"""

    SimulateCommand.main(sys.argv[1:])
