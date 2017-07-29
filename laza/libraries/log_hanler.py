# -*-Coding: utf-8 -*-
__author__ = 'widnyana putra <wid@widnyana.web.id>'

import logging


class LogHandler(object):

    _level = logging.DEBUG


    def __init__(self, filename=None, level=_level, loggername='log'):
        self.log = logging.getLogger(loggername)
        self.log.setLevel(level)

        if filename:
            _filehandler = logging.FileHandler(filename)
        else:
            _filehandler = logging.FileHandler('envato.log')

        _filehandler.setLevel(self._level)
        _formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        _filehandler.setFormatter(_formatter)

        self.log.addHandler(_filehandler)

        self._parent = 'all'

        self._string = "[{0}]\t{1}"
        self._handler = _filehandler


    @property
    def filehandler(self):
        return self._handler

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value=None):
        if value:
            self._parent = value

    def error(self, message=''):
        self.log.error(self._string.format(self._parent, message))

    def info(self, message=''):
        self.log.info(self._string.format(self._parent, message))

    def debug(self, message=''):
        self.log.debug(self._string.format(self._parent, message))

    def warn(self, message=''):
        self.log.warning(self._string.format(self._parent, message))
