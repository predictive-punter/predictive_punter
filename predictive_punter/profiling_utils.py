from datetime import datetime
import logging


def log_time(message, target, *target_args, **target_kwargs):

    start_time = datetime.now()
    logging.info('Started {message} at {start_time}'.format(message=message, start_time=start_time))

    output = target(*target_args, **target_kwargs)

    elapsed_time = datetime.now() - start_time
    logging.info('Finished {message} in {elapsed_time}'.format(message=message, elapsed_time=elapsed_time))

    return output
