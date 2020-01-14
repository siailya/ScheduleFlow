import logging

import pendulum

from bot.stuff.Config import Config
from bot.stuff import Utilities


class Logger:
    def __init__(self):
        self.name = 'logger'
        self.file = 'Log'
        self.path = Config.PATH + f'log/{self.file}.log'

    def getLogger(self, name):
        self.name = name
        return self

    def info(self, message):
        with open(self.path, 'a') as log:
            log.write(f'{pendulum.now(tz=Utilities.TZ).__format__("DD.MM.YYYY HH:mm:ss")}: {message}\n')

    def warning(self, message):
        with open(self.path, 'a') as log:
            log.write(f'{pendulum.now(tz=Utilities.TZ).__format__("DD.MM.YYYY HH:mm:ss")} ВАЖНО!: {message}\n')

    def setFile(self, file):
        self.file = file
        self.path = Config.PATH + f'log/{self.file}.log'


def GetMainLogger():
    logger = Logger().getLogger('MainLogger')
    logger.setFile('MainLog')
    return logger


def GetNewMainLogger(name):
    logger = Logger().getLogger(name)
    logger.setFile('MainLog')
    return logger


def GetCustomLogger(name, file):
    logger = Logger().getLogger(name)
    logger.setFile(file)
    return logger
