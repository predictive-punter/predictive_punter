import csv
import sys
import threading

from . import Command, Prediction, Predictor


class PredictCommand(Command):
    """Command line utility to output the best predictions for all races in a specified date range"""

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.writer_lock = threading.RLock()
        self.writer = csv.writer(sys.stdout)

        self.write_row([
            'Date',
            'Track',
            'Race',
            'Start Time',
            'Bet Type',
            '1st',
            '2nd',
            '3rd',
            '4th',
            'Minimum Dividend'
            ])

    def process_date(self, date):
        """Extend the process_date method to clear predictor locks after each date"""

        super().process_date(date)

        Predictor.predictor_cache.clear()
        Predictor.predictor_locks.clear()
        self.provider.query_locks.clear()
    
    def process_race(self, race):
        """Extend the process_race method to generate predictions if necessary"""

        super().process_race(race)

        for key in race.best_predictions:
            if race.best_predictions[key] is not None and len(race.best_predictions[key]) > 0:

                row = [
                    race.meet['date'].astimezone(self.provider.local_timezone).date(),
                    race.meet['track'],
                    race['number'],
                    race['start_time'].astimezone(self.provider.local_timezone).time(),
                    key.upper().replace('_', ' ')
                ]

                if key == 'multi':
                    row.extend([
                        ','.join([str(number) for number in sorted(race.best_predictions[key])]),
                        None,
                        None,
                        None,
                        None
                        ])
                else:
                    for place in range(Prediction.BET_TYPES[key]):
                        row.append(','.join([str(number) for number in sorted(race.best_predictions[key][0]['picks'][place])]))
                    for count in range(4 - Prediction.BET_TYPES[key]):
                        row.append(None)
                    row.append(race.best_predictions[key][1])

                self.write_row(row)

    def write_row(self, row):
        """Write the specified row to output"""

        with self.writer_lock:
            self.writer.writerow(row)
            sys.stdout.flush()


def main():
    """Main entry point for predict console script"""

    PredictCommand.main(sys.argv[1:])
