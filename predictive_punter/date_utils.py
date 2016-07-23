from datetime import timedelta


def dates(date_from, date_to):
    """Iterate over all dates from date_from to date_to (inclusive)"""

    next_date = date_from
    while next_date <= date_to:
        yield next_date
        next_date += timedelta(days=1)
