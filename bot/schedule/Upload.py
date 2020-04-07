from bot.Api import Vk
from bot.database.DataBases import ScheduleBase


def UploadSchedule(path_to_schedule, date, cls):
    SB = ScheduleBase()
    SB.NewSchedule(date)
    VK = Vk()
    attachment = VK.UploadAttachmentPhoto(path_to_schedule)
    SB.UploadedClass(date, cls, attachment)