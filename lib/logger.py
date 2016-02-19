import sys
import logging


class Logger:
    logger = None

    def __init__(self, module="platform", level=logging.DEBUG):
        self.logger = logging.getLogger(module)
        self.logger.setLevel(level)

        ch = logging.StreamHandler()
        ch.setLevel(level)

        fmter = logging.Formatter('[%(name)s]: %(message)s')
        ch.setFormatter(fmter)
        self.logger.addHandler(ch)

    def log(self, msg):
        self.logger.info(msg)


