import csv
import sys
import threading

from . import Command


class PredictCommand(Command):
    """Command line utility to predict the outcome of all races in a specified date range"""

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.writer = csv.writer(sys.stdout)
        self.writer_lock = threading.RLock()
        self.write_row([
            'Date',
            'Track',
            'Race',
            'Start Time',
            '1st',
            '2nd',
            '3rd',
            '4th',
            'Score'
            ])

    def process_race(self, race):
        """Extend the process_race method to output a prediction for the race"""

        super().process_race(race)

        prediction = race.prediction
        if prediction is not None:

            row = [
                race.meet['date'].astimezone(self.provider.local_timezone).date(),
                race.meet['track'],
                race['number'],
                race['start_time'].astimezone(self.provider.local_timezone).time()
            ]
            for place in range(4):
                row.append(','.join([str(number) for number in prediction[0][place]]) if len(prediction[0][place]) > 0 else None)
            row.append(prediction[1])

            self.write_row(row)

    def write_row(self, row):
        """Write the provided row to the standard output via the CSV writer"""

        with self.writer_lock:
            self.writer.writerow(row)
            sys.stdout.flush()


def main():
    """Main entry point for predict console script"""

    PredictCommand.main(sys.argv[1:])
