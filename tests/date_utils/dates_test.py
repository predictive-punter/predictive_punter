from datetime import datetime

from predictive_punter import date_utils


def test_forward():
    """The dates iterator should generate the expected dates when date_from < date_to"""

    expected_dates = [
        datetime(2016, 2, 1),
        datetime(2016, 2, 2),
        datetime(2016, 2, 3)
    ]

    actual_dates = [date for date in date_utils.dates(datetime(2016, 2, 1), datetime(2016, 2, 3))]

    assert actual_dates == expected_dates


def test_reverse():
    """The dates iterator should generate the expected dates when date_from > date_to"""

    expected_dates = [
        datetime(2016, 2, 3),
        datetime(2016, 2, 2),
        datetime(2016, 2, 1)
    ]

    actual_dates = [date for date in date_utils.dates(datetime(2016, 2, 3), datetime(2016, 2, 1))]

    assert actual_dates == expected_dates
