import errno
import logging
import os


class GetLoggerMixin:
    __loggername__ = f'{__name__}.GetLoggerMixin'

    @classmethod
    def _logger(cls, name=''):
        loggername = cls.__loggername__
        if name:
            loggername = f'{loggername}.{name}'
        return logging.getLogger(loggername)
