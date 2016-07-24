from datetime import timedelta


def dates(date_from, date_to):
    """Iterate over all dates from date_from to date_to (inclusive)"""

    time_delta = timedelta(days=1)
    if date_from > date_to:
        time_delta *= -1

    next_date = date_from
    while (date_from <= date_to and next_date <= date_to) or (date_from > date_to and next_date >= date_to):
        yield next_date
        next_date += time_delta
