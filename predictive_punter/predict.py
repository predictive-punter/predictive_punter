import csv
import sys
import threading

from . import Command, Prediction


class PredictCommand(Command):
    """Command line utility to predict the outcomes of of races"""

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.writer = csv.writer(sys.stdout)
        self.writer_lock = threading.RLock()

        self.write_row([
            'Date',
            'Track',
            'Race',
            'Time',
            '1st',
            '2nd',
            '3rd',
            '4th',
            'Estimator',
            'Weighted',
            'Score',
            'Train Samples',
            'Test Samples'
            ])

    def process_date(self, date):
        """Extend the process_date method to clear predictor caches at the end of each day"""

        super().process_date(date)

        Prediction.estimator_cache.clear()
        Prediction.estimator_locks.clear()
    
    def process_race(self, race):
        """Extend the process_race method to generate a sample if necessary"""

        super().process_race(race)

        for prediction in race.predictions:

            row = [
                race.meet['date'].astimezone(self.provider.local_timezone).date(),
                race.meet['track'],
                race['number'],
                race['start_time'].astimezone(self.provider.local_timezone).time(),
            ]

            for place in range(4):
                row.append(','.join([str(value) for value in sorted(prediction['picks'][place])]) if len(prediction['picks'][place]) > 0 else None)

            row.extend([
                prediction['estimator_type'],
                prediction['use_sample_weights'],
                prediction['score'],
                prediction['train_samples'],
                prediction['test_samples']
                ])

            self.write_row(row)

    def write_row(self, row):
        """Write the specified row to output"""

        with self.writer_lock:
            self.writer.writerow(row)
            sys.stdout.flush()


def main():
    """Main entry point for predict console script"""

    PredictCommand.main(sys.argv[1:])
