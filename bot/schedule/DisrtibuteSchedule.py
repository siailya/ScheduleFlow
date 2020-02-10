from time import sleep

import pendulum

from bot.Api import Vk
from bot.database.DataBases import UserBase, SettingsBase
from bot.schedule.GetSchedule import GetSchedule
from bot.schedule.Updater import UpdateSchedule
from bot.stuff import Utilities
from bot.stuff.Config import Config
from bot.stuff.Utilities import FORMAT, TZ


def GetScheduleDate(now):
    if Config.REDIRECT_DATE:
        return Config.REDIRECT_DATE
    hour = now.hour
    minute = now.minute
    weekday = now.weekday()
    if weekday == 6:
        return now.add(days=1).__format__(FORMAT)
    elif weekday < 5:
        if (hour >= 10) and ((hour <= 23) and (minute <= 59)):
            return now.add(days=1).__format__(FORMAT)
        return now.__format__(FORMAT)
    else:
        if (hour >= 10) and ((hour <= 23) and (minute <= 59)):
            return now.add(days=2).__format__(FORMAT)
        return now.__format__(FORMAT)


def GetScheduleTomorrow(schedule_date=pendulum.tomorrow(TZ)):
    if Config.REDIRECT_DATE:
        return Config.REDIRECT_DATE
    return schedule_date.__format__(FORMAT) if schedule_date.weekday() != 6 else schedule_date.add(days=1).__format__(FORMAT)


def ClassSend(cls, date):
    ids = UserBase().DistributeClassUsers(cls)
    for i in ids:
        UserBase().IncreaseParameters(i, received=True, messages_received=True)
    msg = f'Держи расписание на {date}!'
    schedule = GetSchedule(date, cls)
    if schedule:
        Vk().ManyMessagesSend(ids, msg, attachment=schedule)


def ClassTimeSend(cls, date, time):
    ids = UserBase().DistributeSchedule(cls, time)
    if ids:
        for i in ids:
            UserBase().IncreaseParameters(i, received=True, messages_received=True)
        msg = f'Держи расписание на {date}!'
        schedule = GetSchedule(date, cls)
        if schedule:
            Vk().ManyMessagesSend(ids, msg, attachment=schedule)


def SendAllClasses(date=GetScheduleTomorrow()):
    UpdateSchedule(date).UpdateAll()
    for i in Utilities.CLASSES:
        ClassSend(i, date)


def SendAllTime(date, time):
    Vk().ConsoleMessage(f'Выполняется автоматическая рассылка расписания на {date}...')
    UpdateSchedule(date).UpdateAll()
    for i in Utilities.CLASSES:
        ClassTimeSend(i, date, time)


def NextDistributeWait(now):
    if now.weekday() != 6:
        if now.hour < 7:
            return now.diff(pendulum.datetime(now.year, now.month, now.day, 7, 0, tz=TZ)).in_seconds(), 7
        elif now.hour < 13:
            return now.diff(pendulum.datetime(now.year, now.month, now.day, 13, 0, tz=TZ)).in_seconds(), 13
        elif now.hour < 17:
            return now.diff(pendulum.datetime(now.year, now.month, now.day, 17, 0, tz=TZ)).in_seconds(), 17
        elif now.hour < 20:
            return now.diff(pendulum.datetime(now.year, now.month, now.day, 20, 0, tz=TZ)).in_seconds(), 20
        elif now.hour < 23:
            return now.diff(pendulum.datetime(now.year, now.month, now.day, 23, 0, tz=TZ)).in_seconds(), 23
        else:
            tm = now.add(days=1)
            return now.diff(pendulum.datetime(tm.year, tm.month, tm.day, 7, 0, tz=TZ)).in_seconds(), 7
    else:
        tm = now.add(days=1)
        return now.diff(pendulum.datetime(tm.year, tm.month, tm.day, 7, 0, tz=TZ)).in_seconds(), 7


def AutoDistribution():
    print('Auto-Distribution started!')
    while True:
        try:
            sleep_time, time = NextDistributeWait(pendulum.now(TZ))
            print('Wait to distribute', sleep_time)
            sleep(sleep_time)
            if SettingsBase().GetSettings(pendulum.now().__format__(FORMAT))['auto_distribution']:
                SendAllTime(GetScheduleDate(pendulum.now()), time)
            sleep(10)
        except:
            print('Distribute Error!')
            sleep(30)
