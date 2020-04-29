import logging
from datetime import datetime

logger = logging.getLogger('stocker')


class Timer:
    def __init__(self, timeout):
        self.timeout = timeout
        self.start_time = None

    def start(self):
        self.start_time = datetime.now()

    def is_timeout(self):
        now_time = datetime.now()
        timedelta = now_time - self.start_time
        if self.timeout == 0:
            logger.debug('{} second(s) spent. Running indefinitely...'.format(timedelta.seconds))
        elif timedelta.seconds >= self.timeout:
            logger.debug('{}/{}: timeout'.format(timedelta.seconds, self.timeout))
            return True
        else:
            logger.debug('{}/{}: keep going...'.format(timedelta.seconds, self.timeout))
