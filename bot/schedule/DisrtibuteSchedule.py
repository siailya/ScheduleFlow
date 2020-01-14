import pendulum
from pendulum import today

from bot.Api import Vk
from bot.database.DataBases import UserBase
from bot.schedule.GetSchedule import GetSchedule
from bot.stuff import Utilities
from bot.stuff.Config import Config
from bot.stuff.Utilities import FORMAT, TZ


def GetScheduleTomorrow(schedule_date=pendulum.tomorrow(TZ)):
    if Config.REDIRECT_DATE:
        return Config.REDIRECT_DATE
    return schedule_date.__format__(FORMAT) if schedule_date.weekday() != 6 else schedule_date.add(days=2).__format__(FORMAT)


def ClassSend(cls, date):
    ids = UserBase().DistributeClassUsers(cls)
    for i in ids:
        UserBase().IncreaseParameters(i, received=True, messages_receive=True)
    msg = 'Держи расписание на завтра!'
    if today().weekday() == 5:
        msg = 'держи расписание на понедельник!'
    schedule = GetSchedule(date, cls)
    Vk().ManyMessagesSend(ids, msg, attachment=schedule)


def SendAllClasses(date=GetScheduleTomorrow()):
    for i in Utilities.CLASSES:
        ClassSend(i, date)