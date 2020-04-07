from datetime import datetime
from os import path
from time import sleep

import pendulum

from bot.database.DataBases import ScheduleBase, SettingsBase
from bot.schedule.FromSite import DownloadScheduleFromSite, CheckAvailabilityOnSite
from bot.schedule.Updater import UpdateSchedule
from bot.schedule.Upload import UploadSchedule
from bot.stuff import Utilities
from bot.stuff.Config import Config


def CheckSchedule(schedule_date, cls='main'):
    if (cls != 'main' and path.exists(Config.PATH + f'work/schedules/{schedule_date}/{cls}.png')) or ScheduleBase().GetAttachment(schedule_date, cls):
        return True
    else:
        if UpdateSchedule(schedule_date).UpdateAll():
            return True

    if cls == 'main' and path.exists(Config.PATH + f'work/source/{schedule_date}.png'):
        return True
    else:
        if CheckAvailabilityOnSite(schedule_date):
            return True
    return False


def GetSchedule(schedule_date, cls='main', static=False):
    SB = ScheduleBase()
    if Config.STATIC and static:
        if datetime.strptime(schedule_date, '%d.%m.%Y').weekday() != 6:
            return SB.GetAttachment(Utilities.STATIC[datetime.strptime(schedule_date, '%d.%m.%Y').weekday()], cls)
        return None
    if SettingsBase().GetSettings(schedule_date)['main_replace'] == 1:
        cls = 'main'
    if CheckSchedule(schedule_date, cls):
        if SB.GetAttachment(schedule_date, cls):
            return SB.GetAttachment(schedule_date, cls)
        else:
            if cls == 'main':
                if not path.exists(Config.PATH + f'work/source/{schedule_date}.png'):
                    DownloadScheduleFromSite(schedule_date)
                UploadSchedule(Config.PATH + f'work/source/{schedule_date}.png', schedule_date, cls)
            else:
                counter = 0
                while not path.exists(Config.PATH + f'work/schedules/{schedule_date}/{cls}.png') and counter < 10:
                    sleep(1)
                    counter += 1
                UploadSchedule(Config.PATH + f'work/schedules/{schedule_date}/{cls}.png', schedule_date, cls)
            return SB.GetAttachment(schedule_date, cls)
    SB.DeleteSchedule(schedule_date)
    return None


def ScheduleInfo(schedule_date, cls='main'):
    info = f'Информация о расписании на {schedule_date}:\n' \
           f'Доступно: {"✅" if CheckSchedule(schedule_date, cls) else "⛔"}\n' \
           f'Доступно на сайте: {"✅" if CheckAvailabilityOnSite(schedule_date) else "⛔"}\n' \
           f'Загружено ВК: {"✅" if ScheduleBase().GetAttachment(schedule_date, cls) else "⛔"}\n' \
           f'Заменено общим: {"✅" if ScheduleBase().GetReplace(schedule_date) else "⛔"}\n'
    if cls == 'main':
        schedule_path = Config.PATH + f"work/source/{schedule_date}.png"
        info += f'Доступно локально: {"✅" if path.exists(schedule_path) else "⛔"}\n'
        if path.exists(Config.PATH + f"work/source/{schedule_date}.png"):
            info += f'Обновлено: {pendulum.from_timestamp(path.getmtime(schedule_path), tz=Utilities.TZ).__format__(Utilities.EXT_FORMAT)}'
        else:
            info += 'Обновлено: -'
    else:
        schedule_path = Config.PATH + f"work/schedules/{schedule_date}/{cls}.png"
        info += f'Доступно локально: {"✅" if path.exists(schedule_path) else "⛔"}\n'
        if path.exists(schedule_path):
            info += f'Обновлено: {pendulum.from_timestamp(path.getmtime(schedule_path), tz=Utilities.TZ).__format__(Utilities.EXT_FORMAT)}'
        else:
            info += 'Обновлено: -'
    return info
