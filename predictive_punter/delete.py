import sys

import racing_data

from . import Command, Sample


class DeleteCommand(Command):
    """Command line utility to delete all racing data in a specified date range"""

    def process_meet(self, meet):
        """Override the process_meet method to process associated races and then delete the meet"""

        for race in self.provider.find(racing_data.Race, {'meet_id': meet['_id']}, None):
            self.process_race(race)

        self.provider.delete(meet)

    def process_race(self, race):
        """Override the process_race method to process associated runners and then delete the race"""

        for runner in self.provider.find(racing_data.Runner, {'race_id': race['_id']}, None):
            self.process_runner(runner)

        self.provider.delete(race)

    def process_runner(self, runner):
        """Override the process_runner method to delete the runner and associated sample if necessary"""

        sample = self.provider.find_one(Sample, {'runner_id': runner['_id']}, None)
        if sample is not None:
            self.provider.delete(sample)

        self.provider.delete(runner)


def main():
    """Main entry point for delete console script"""

    DeleteCommand.main(sys.argv[1:])
