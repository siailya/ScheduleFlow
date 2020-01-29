from bot.database.DataBases import ScheduleBase
from bot.Api import Vk


def UploadSchedule(path_to_schedule, date, cls):
    SB = ScheduleBase()
    SB.NewSchedule(date)
    VK = Vk()
    attachment = VK.UploadAttachmentPhoto(path_to_schedule)
    SB.UploadedClass(date, cls, attachment)