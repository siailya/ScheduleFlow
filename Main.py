from multiprocessing import Process

import requests
from vk_api.bot_longpoll import VkBotEventType

from bot.Api import Vk
from bot.events.Events import MessagesDeny, MemberLeave, MemberJoin, Comment
from bot.messages.NewMessage import NewMessage
from bot.schedule.DisrtibuteSchedule import AutoDistribution
from bot.schedule.Updater import AutoUpdater
from bot.stuff.Config import Config as Config
from bot.stuff.Logging import GetMainLogger, GetCustomLogger

Vk = Vk()
Logger = GetMainLogger()
EventLogger = GetCustomLogger('EventLog', 'EventLog')
ExceptionLogger = GetCustomLogger('Exception', 'ExceptionLog')


def MainBot():
    Logger.info(f'Бот запущен! Версия: {Config.VERSION}')
    Logger.info('Старт прослушивания сервера!')
    print('LongPooling started!')
    while True:
        if not Config.DEBUGGING:
            try:
                for event in Vk.LongPool.listen():
                    try:
                        EventLogger.info(f'from: {event.obj.message["peer_id"]}; text: {event.obj.message["text"]};\n{event.obj.message}')
                    except Exception as e:
                        ExceptionLogger.warning(f'Exception {e} caused')
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        try:
                            NewMessage(event)
                        except Exception as e:
                            print(e)
                            Vk.ConsoleMessage(f'Ошибка: {e} caused by {event.obj.message}')
                            Logger.warning('Exception!')
                            ExceptionLogger.warning(f'Exception {e} caused by {event.obj.message}')
                    elif event.type == VkBotEventType.MESSAGE_DENY:
                        MessagesDeny(event)
                    elif event.type == VkBotEventType.GROUP_JOIN:
                        MemberJoin(event)
                    elif event.type == VkBotEventType.GROUP_LEAVE:
                        MemberLeave(event)
                    elif event.type == VkBotEventType.WALL_REPLY_NEW:
                        Comment(event)
            except requests.exceptions.ReadTimeout:
                Vk.ConsoleMessage('LongPool перезапущен!')
                Logger.warning('LongPool is restarted')
                ExceptionLogger.warning('LongPool is restarted')
        else:
            for event in Vk.LongPool.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    NewMessage(event)


if __name__ == '__main__':
    ListenProcess = Process(target=MainBot)
    UpdateProcess = Process(target=AutoUpdater)
    DistributeProcess = Process(target=AutoDistribution)
    # ParseProcess = Process(target=Parser)
    print('Initialization...')
    ListenProcess.start()
    UpdateProcess.start()
    DistributeProcess.start()
    # ParseProcess.start()