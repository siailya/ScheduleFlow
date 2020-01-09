from pendulum import today

from bot.Api import Vk
from bot.database.DataBases import UserBase
from bot.schedule.GetSchedule import GetSchedule
from bot.stuff import Utilities
from bot.stuff.Utilities import GetScheduleTomorrow


def ClassSend(cls, date):
    ids = UserBase().DistributeClassUsers(cls)
    msg = 'Держи расписание на завтра!'
    if today().weekday() == 5:
        msg = 'держи расписание на понедельник!'
    schedule = GetSchedule(date, cls)
    Vk().ManyMessagesSend(ids, msg, attachment=schedule)


def SendAllClasses(date=GetScheduleTomorrow()):
    for i in Utilities.CLASSES:
        ClassSend(i, date)