from multiprocessing.dummy import Process
from time import sleep

from bot.database.DataBases import SettingsBase
from bot.schedule.Classes import *
from bot.schedule.FromSite import DownloadScheduleFromSite
from bot.stuff.Logging import GetNewMainLogger, GetCustomLogger
from bot.stuff.Utilities import FORMAT, TZ


def GetScheduleDate(now):
    if Config.REDIRECT_DATE:
        return Config.REDIRECT_DATE
    hour = now.hour
    minute = now.minute
    weekday = now.weekday()
    if weekday == 6:
        return pendulum.tomorrow(TZ).__format__(FORMAT)
    elif weekday < 5:
        if (hour >= 10) and ((hour <= 23) and (minute <= 59)):
            return pendulum.tomorrow(TZ).__format__(FORMAT)
        return pendulum.today(TZ).__format__(FORMAT)
    else:
        if (hour >= 10) and ((hour <= 23) and (minute <= 59)):
            return now.add(days=2).__format__(FORMAT)
        return pendulum.today(TZ).__format__(FORMAT)


class UpdateSchedule:
    def __init__(self, date):
        self.date = date
        self.ScheduleBase = ScheduleBase()

    def UpdateMain(self):
        DownloadScheduleFromSite(self.date)

    def UpdateClasses(self):
        CropAllClasses(self.date)

    def UpdateAll(self):
        self.ScheduleBase.DeleteSchedule(self.date)
        if DownloadScheduleFromSite(self.date):
            update_process = Process(target=self.UpdateClasses)
            update_process.start()
            return True
        elif path.exists(Config.PATH + f'work/source/{self.date}.png'):
            update_process = Process(target=self.UpdateClasses)
            update_process.start()
            return True
        return False

    def CheckMainUpdates(self):
        if self.ScheduleBase.DeltaUpdateMain(self.date, pendulum.now(TZ)) >= 15:
            return True
        return False

    def CheckClassesUpdate(self):
        if self.ScheduleBase.DeltaUpdateClasses(self.date, pendulum.now(TZ)) >= 15:
            return True
        return False


def AutoUpdater():
    print('AutoUpdating started!')
    Logger = GetNewMainLogger('Updater')
    UpdateLogger = GetCustomLogger('UpdateLogger', 'UpdateLog')
    Logger.info('Запущено авто-обновление')
    Update = UpdateSchedule(GetScheduleDate(pendulum.now()))
    while True:
        try:
            if Update.CheckClassesUpdate() or Update.CheckMainUpdates():
                if SettingsBase().GetSettings()['auto_update']:
                    UpdateLogger.info(f'Обновление расписания на {GetScheduleDate(pendulum.now(TZ))}')
                    print(f'Update to {GetScheduleDate(pendulum.now(TZ))}')
                    Update.UpdateAll()
            sleep(900)
        except:
            print('Update are failed')
            sleep(30)