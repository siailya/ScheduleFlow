from time import sleep

from bot.Api import Vk
from bot.database.DataBases import ParseBase, UserBase
from bot.schedule.FromSite import CheckAvailabilityOnSite
from bot.stuff.Config import Config
from bot.stuff.Logging import GetCustomLogger, GetNewMainLogger

ParseLogger = GetCustomLogger('ParseLogger', 'ParseLog')
Logger = GetNewMainLogger('Parser')


def Parser():
    # TODO: автодобавление/удаление расписаний
    print('Parsing started!')
    Logger.info('Запущен процесс парсинга')
    PB = ParseBase()
    while True:
        try:
            Report = 'Наличие расписаний на сайте:\n'
            if PB.GetParseSchedules() and PB.CheckParseTime():
                PB.SetParseTime()
                for i in sorted(PB.GetParseSchedules()):
                    if CheckAvailabilityOnSite(i):
                        ParseLogger.info(f'Распсиание на {i} доступно')
                        Report += f'{i} - ✅\n'
                    else:
                        ParseLogger.info(f'Распсиание на {i} не доступно')
                        Report += f'{i} - ⛔\n'
                if Report:
                    Vk().ConsoleMessage(Report)
                    Vk().ManyMessagesSend(UserBase().TrackList(), Report)
            sleep(Config.PARSE_INTERVAL)
        except:
            print('Parse are failed')


def ParseFast():
    PB = ParseBase()
    Report = 'Наличие расписаний на сайте:\n'
    if PB.GetParseSchedules():
        for i in sorted(PB.GetParseSchedules()):
            if CheckAvailabilityOnSite(i):
                Report += f'{i} - ✅\n'
            else:
                Report += f'{i} - ⛔\n'
        if Report:
            return Report