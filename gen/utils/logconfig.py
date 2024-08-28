'''
This file performs logging for the application.
'''
import logging
import os
from logging.handlers import RotatingFileHandler


RCD_LOG_FILE = os.environ.get('RCD_LOG_FILE', '/rcd/logs/generator.log')

class CustomFormatter(logging.Formatter):
    '''
    Implementations of custom logging format for rcd logs.
    '''
    grey = '\x1b[38;21m'
    yellow = '\x1b[33;21m'
    red = '\x1b[31;21m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'
    fmt = '%(asctime)s | %(name)-22s | %(threadName)-15s | %(levelname)-8s | %(message)s'

    FORMATS = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: grey + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logging(level: int):
    '''
    Sets up the logging level for the logger.
    '''
    file_handler = RotatingFileHandler(
        RCD_LOG_FILE, mode='a', maxBytes=5000000, backupCount=5)  # 5MB with 5 backups
    file_handler.setLevel(level)
    file_handler.setFormatter(CustomFormatter())

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(CustomFormatter())

    logging.basicConfig(level=level, handlers=[stream_handler, file_handler])
