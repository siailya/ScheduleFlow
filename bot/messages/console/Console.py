from multiprocessing import Process

import pendulum

import bot.stuff.Utilities
from bot.Api import Vk, DialogFlow
from bot.database.DataBases import ConsoleBase, UserBase, StatisticsBase, ParseBase, ScheduleBase, HomeworkBase
from bot.messages.console.ConsoleTemp import ConsoleTemp
from bot.messages.console.Keyboard import *
from bot.schedule.DisrtibuteSchedule import SendAllClasses
from bot.schedule.GetSchedule import GetSchedule
from bot.schedule.Parser import ParseFast
from bot.schedule.Updater import UpdateSchedule
from bot.stuff import Utilities
from bot.stuff.Config import Config
from bot.stuff.Logging import GetCustomLogger
from bot.stuff.Utilities import FORMAT, TZ

Logger = GetCustomLogger('ConsoleLogger', 'ConsoleLog')


def GetTodayDate():
    if Config.REDIRECT_DATE:
        return Config.REDIRECT_DATE
    return pendulum.now(TZ).__format__(FORMAT)


def GetScheduleDate():
    if Config.REDIRECT_DATE:
        return Config.REDIRECT_DATE
    hour = pendulum.now(TZ).hour
    minute = pendulum.now(TZ).minute
    weekday = pendulum.now(TZ).weekday()
    if weekday == 6:
        return pendulum.tomorrow(TZ).__format__(FORMAT)
    elif weekday < 5:
        if (hour >= 10) and ((hour <= 23) and (minute <= 59)):
            return pendulum.tomorrow(TZ).__format__(FORMAT)
        return pendulum.today(TZ).__format__(FORMAT)
    else:
        if (hour >= 10) and ((hour <= 23) and (minute <= 59)):
            return pendulum.now().add(days=2).__format__(FORMAT)
        return pendulum.today(TZ).__format__(FORMAT)


def GetScheduleTomorrow(schedule_date=pendulum.tomorrow(TZ)):
    if Config.REDIRECT_DATE:
        return Config.REDIRECT_DATE
    return schedule_date.__format__(FORMAT) if schedule_date.weekday() != 6 else schedule_date.add(days=1).__format__(FORMAT)


def UserInfo(info):
    if info:
        return f'Информация о пользователе @id{info["id"]}({info["name"]} {info["last"]}):\n' \
               f'Класс: {info["cls"]}\n' \
               f'Запросов: {info["requests"]}\n' \
               f'Получено расписаний: {info["received"]}\n' \
               f'Отправлено сообщений: {info["msg_send"]}\n' \
               f'Получено сообщений: {info["msg_received"]}'
    return 'Пользователь не найден в базе!'


def ScheduleFlowInfo():
    statistics = StatisticsBase().GetMainStatistics()
    return f'Запросов: {statistics["requests"]}\n' \
           f'Юзеров в базе: {statistics["total_users"]}\n' \
           f'Юзеров с уведомлениями: {statistics["total_notifications"]}\n' \
           f'Получено расписаний: {statistics["schedule_received"]}\n\n' \
           f'Отправлено сообщений: {statistics["msg_send"]}\n' \
           f'Получено сообщений: {statistics["msg_received"]}\n' \
           f'Всего сообщений: {statistics["total_msg"]}\n\n' \
           f'Запуск: {Utilities.INIT_TIME}\n' \
           f'Uptime: {Utilities.INIT_TIME.diff(pendulum.now(TZ)).in_words(locale="ru")}'


def Distribution():
    return f'Выполнить рассылку для {"всех" if ConsoleTemp.Distribute == "all" else ConsoleTemp.Distribute} с текстом "{ConsoleTemp.Text}"?\n\nВведите "Да, выполнить"'


def SendManyUsers(user_ids, message):
    Vk().ManyMessagesSend(user_ids, message)


class Console:
    def __init__(self, event):
        self.Vk = Vk()
        self.ConsoleBase = ConsoleBase()
        self.SettingsBase = SettingsBase()
        self.UserBase = UserBase()
        self.Settings = Settings()
        if event.obj.message['text']:
            Logger.info(f'{event.obj.message["from_id"]} - {event.obj.message["text"]}')
            self.originalText = event.obj.message['text']
            lowerText = event.obj.message['text'].lower()

            if lowerText == 'setstat':
                self.ConsoleBase.ChangeState(0)
                self.Vk.MessageSend(Config.CONSOLE, 'Меню', keyboard=MainMenu())
            if lowerText == 'raiseexc':
                raise ValueError
            if lowerText == 'params':
                self.Vk.ConsoleMessage(f'now - {pendulum.now()}\n'
                                       f'today - {GetTodayDate()}\n'
                                       f'tomorrow_schedule - {GetScheduleTomorrow(pendulum.tomorrow(TZ))}')

            if self.ConsoleBase.GetState() == 0:
                self.CommandHandler(lowerText)
            elif self.ConsoleBase.GetState() == 1:
                self.SettingsHandler(lowerText.replace('@', ''))
            elif self.ConsoleBase.GetState() == 2:
                self.ConsoleBase.ChangeState(0)
                if lowerText == 'да, выполнить':
                    if ConsoleTemp.Distribute == 'all':
                        all_ids = self.UserBase.AllUsers()
                        SendProcess = Process(target=SendManyUsers, args=(all_ids, ConsoleTemp.Text))
                        SendProcess.start()
                        Logger.info('Запущена общая рассылка')
                        self.Vk.ConsoleMessage('Рассылка запущена!')
                    elif ConsoleTemp.Distribute.upper() in bot.stuff.Utilities.CLASSES:
                        ids = self.UserBase.DistributeClassUsers(ConsoleTemp.Distribute.upper())
                        SendProcess = Process(target=SendManyUsers, args=(ids, ConsoleTemp.Text))
                        SendProcess.start()
                        Logger.info(f'Запущена рассылка по {ConsoleTemp.Distribute.upper()} классу')
                        self.Vk.ConsoleMessage('Рассылка запущена!')
                    elif ConsoleTemp.Distribute in '5 6 7 8 9 10 11':
                        ids = self.UserBase.DistributeParallelUsers(int(ConsoleTemp.Distribute))
                        SendProcess = Process(target=SendManyUsers, args=(ids, ConsoleTemp.Text))
                        SendProcess.start()
                        Logger.info(f'Запущена рассылка по {ConsoleTemp.Distribute} параллели')
                        self.Vk.ConsoleMessage('Рассылка запущена!')
            elif self.ConsoleBase.GetState() == 3:
                self.ConsoleBase.ChangeState(0)
                if lowerText == 'да, выполнить':
                    if GetSchedule(ConsoleTemp.Date, 'main'):
                        send_process = Process(target=SendAllClasses, args=(ConsoleTemp.Date,))
                        send_process.start()
                        self.Vk.ConsoleMessage(f'Рассылка расписания на {ConsoleTemp.Date} запущена!')
                    else:
                        self.Vk.ConsoleMessage(f'Расписание на {ConsoleTemp.Date} не найдено!\nРассылка отменена!')
                else:
                    self.Vk.ConsoleMessage(f'Рассылка отменена!')

    def CommandHandler(self, message: str):
        if message.replace('@', '') == Config.PREFIX + 'настройки':
            self.Vk.MessageSend(Config.CONSOLE, keyboard=Settings(), message='Меню настроек')
            self.ConsoleBase.ChangeState(1)
        elif 'статистика' in message.lower():
            self.Vk.ConsoleMessage(ScheduleFlowInfo())
        elif 'обновить на сегодня' in message.lower():
            date = GetTodayDate()
            self.ScheduleUpdate(date)
        elif 'обновить на завтра' in message.lower():
            date = GetScheduleTomorrow(pendulum.tomorrow(TZ))
            self.ScheduleUpdate(date)
        elif message.replace('@', '') == Config.PREFIX + 'проверить наличие':
            self.Vk.ConsoleMessage(ParseFast())
        elif message[:11] == 'обновить на':
            date_arg = DialogFlow().SendRequest(message).lstrip('update')
            year, month, day = list(map(int, date_arg.split('-')))
            date = pendulum.date(year, month, day).__format__(Utilities.FORMAT)
            self.ScheduleUpdate(date)
        elif message[:14] == 'общая рассылка':
            ConsoleTemp.Distribute = 'all'
            ConsoleTemp.Text = message[15:]
            self.Vk.ConsoleMessage(Distribution())
            self.ConsoleBase.ChangeState(2)
        elif message[:18] == 'рассылка по классу':
            ConsoleTemp.Distribute = message[19:].split(' ')[0]
            ConsoleTemp.Text = ' '.join(message[19:].split(' ')[1:]).capitalize()
            self.Vk.ConsoleMessage(Distribution())
            self.ConsoleBase.ChangeState(2)
        elif message[:21] == 'рассылка по параллели':
            ConsoleTemp.Distribute = message[22:].split(' ')[0]
            ConsoleTemp.Text = ' '.join(message[12:].split(' ')[1:]).capitalize()
            self.Vk.ConsoleMessage(Distribution())
            self.ConsoleBase.ChangeState(2)
        elif message[:19] == 'рассылка расписания':
            if '_' not in message:
                date = GetScheduleTomorrow(pendulum.tomorrow(TZ))
            else:
                date = message.lstrip('рассылка расписания_')

            if GetSchedule(date, '11А'):
                ConsoleTemp.Date = date
                self.ConsoleBase.ChangeState(3)
                self.Vk.ConsoleMessage(f'Введите "Да, выполнить" для подтверждения рассылки расписания на {date}')
                self.Vk.MessageSend(Config.CONSOLE, 'Расписание:', attachment=GetSchedule(date, '11А'))
            else:
                self.Vk.ConsoleMessage(f'Расписания на {date} нет!')
        elif message[:4] == 'инфо':
            if message[5:].replace(' ', '').isdigit():
                uid = int(message[5:].replace(' ', ''))
                info = self.UserBase.GetUserInfo(uid)
                self.Vk.ConsoleMessage(UserInfo(info))
            else:
                name, last = self.originalText[5:].split(' ')
                info = self.UserBase.GetUserInfoByName(name, last)
                self.Vk.ConsoleMessage(UserInfo(info))
        elif message[:6] == 'замена':
            replace_date = message[7:].replace('общим на ', '')
            ScheduleBase().Replace(replace_date)
            self.Vk.ConsoleMessage(f'Замена общим на {replace_date} активирована!')
        elif message[:13] == 'отмена замены':
            replace_date = message[14:].lstrip('общим на ')
            ScheduleBase().UnReplace(replace_date)
            ScheduleBase().DeleteSchedule(replace_date)
            self.Vk.ConsoleMessage(f'Замена общим на {replace_date} отменена!')
        elif 'не отслеживать' in message.lower():
            date = message.lower().lstrip('не отслеживать')
            ParseBase().DeleteFromParse(date)
            self.Vk.ConsoleMessage(f'Расписание на {date} не отслеживается')
        elif 'отслеживать' in message.lower():
            date = message.lower().lstrip('отслеживать ')
            ParseBase().AddToParse(date)
            self.Vk.ConsoleMessage(f'Отслеживается расписание на {date}')
        elif 'список отслеживания' in message.lower():
            self.Vk.ConsoleMessage('Список отслеживаемых расписаний:\n' + '\n'.join(sorted(ParseBase().GetParseSchedules())))
        elif 'удалить дз' in message.lower():
            cls, date = message.lower().lstrip('удалить дз').upper().replace(',', '').split(' ')
            HomeworkBase().DeleteHomework(date, cls)
            self.Vk.ConsoleMessage('ДЗ удалено!')
        elif 'редирект' in message.lower():
            date = message.lstrip('редирект на')
            if date != 'сброс':
                Config.REDIRECT_DATE = date
            else:
                Config.REDIRECT_DATE = 0
        elif 'sql' in message:
            self.Vk.ConsoleMessage(f'{self.UserBase.SQL(message[4:])}')

    def ScheduleUpdate(self, date):
        self.Vk.ConsoleMessage(f'Обновление расписания на {date}')
        answer = UpdateSchedule(date).UpdateAll()
        if answer:
            Logger.info(f'Обновлено расписание на {date}')
            self.Vk.ConsoleMessage('Расписание обновлено!')
        else:
            Logger.info(f'Расписание на {date} не обновлено')
            self.Vk.ConsoleMessage('Расписание не найдено!')

    def SettingsHandler(self, message: str):
        if message == Config.PREFIX + 'выход':
            self.Vk.MessageSend(Config.CONSOLE, keyboard=MainMenu(), message='Основное меню')
            self.ConsoleBase.ChangeState(0)
            return None

        elif message == Config.PREFIX + 'онлайн' and not self.SettingsBase.GetSettings()['offline']:
            self.SettingsBase.ChangeSettings(parameters={'offline': 1})
            Logger.info('Включен онлайн бота')
        elif message == Config.PREFIX + 'оффлайн' and self.SettingsBase.GetSettings()['offline']:
            self.SettingsBase.ChangeSettings(parameters={'offline': 0})
            Logger.info('Выключен онлайн бота')

        elif message == Config.PREFIX + 'рассылка вкл' and self.SettingsBase.GetSettings()['auto_distribution']:
            self.SettingsBase.ChangeSettings(parameters={'auto_distribution': 0})
            Logger.info('Авто-рассылка включена')
        elif message == Config.PREFIX + 'рассылка выкл' and not self.SettingsBase.GetSettings()['auto_distribution']:
            self.SettingsBase.ChangeSettings(parameters={'auto_distribution': 1})
            Logger.info('Авто-рассылка выключена')

        elif message == Config.PREFIX + 'обновление вкл' and self.SettingsBase.GetSettings()['auto_update']:
            self.SettingsBase.ChangeSettings(parameters={'auto_update': 0})
            Logger.info('Авто-обновление включено')
        elif message == Config.PREFIX + 'обновление выкл' and not self.SettingsBase.GetSettings()['auto_update']:
            self.SettingsBase.ChangeSettings(parameters={'auto_update': 1})
            Logger.info('Авто-обновление выключено')

        elif message == Config.PREFIX + 'замена общим вкл' and self.SettingsBase.GetSettings()['main_replace']:
            self.SettingsBase.ChangeSettings(parameters={'main_replace': 0})
            ScheduleBase().Replace(GetScheduleDate())
            Logger.info('Замена общим включена')
        elif message == Config.PREFIX + 'замена общим выкл' and not self.SettingsBase.GetSettings()['main_replace']:
            self.SettingsBase.ChangeSettings(parameters={'main_replace': 1})
            ScheduleBase().UnReplace(GetScheduleDate())
            Logger.info('Замена общим выключена')

        elif message == Config.PREFIX + 'дневник вкл' and self.SettingsBase.GetSettings()['diary']:
            self.SettingsBase.ChangeSettings(parameters={'diary': 0})
            Logger.info('Дневник включен')
        elif message == Config.PREFIX + 'дневник выкл' and not self.SettingsBase.GetSettings()['diary']:
            self.SettingsBase.ChangeSettings(parameters={'diary': 1})
            Logger.info('Дневник выключен')

        elif message == Config.PREFIX + 'сброс':
            self.SettingsBase.ChangeSettings(
                parameters={'auto_update': 1, 'main_replace': 0, 'offline': 0, 'diary': 0, 'auto_distribution': 0})

        self.Vk.MessageSend(Config.CONSOLE, keyboard=Settings(), message='Меню настроек')
