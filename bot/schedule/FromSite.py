import pendulum
import requests
from PIL import Image, ImageDraw, ImageFont
from pendulum import now

from bot.database.DataBases import ScheduleBase
from bot.stuff.Config import Config
from bot.stuff.Utilities import TZ


def CheckAvailabilityOnSite(schedule_date):
    name = schedule_date + ".png"
    url = 'https://амтэк35.рф/wp-content/uploads/' + name
    request = requests.get(url)
    return True if request.status_code == 200 else False


def DownloadScheduleFromSite(schedule_date):
    if CheckAvailabilityOnSite(schedule_date):
        name = schedule_date + ".png"
        url = 'https://амтэк35.рф/wp-content/uploads/' + name
        p = requests.get(url)
        out = open(Config.PATH + f'work/source/{name}', "wb")
        out.write(p.content)
        out.close()
        UpdateTimeMainWatermark(schedule_date)
        ScheduleBase().MainUpdate(schedule_date, pendulum.now(TZ))
        return True
    return False


def UpdateTimeMainWatermark(schedule_date):
    image = Image.open(Config.PATH + f'work/source/{schedule_date}.png')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(Config.PATH + 'bot/stuff/font.ttf', 30)
    draw.text((30, 30), f'Обновлено {now().__format__("DD.MM.YYYY")} в {now().__format__("HH:mm")}', fill='black', font=font)
    image.save(Config.PATH + f'work/source/{schedule_date}.png')


if __name__ == '__main__':
    DownloadScheduleFromSite('28.12.2019')

    CheckAvailabilityOnSite('28.12.2019')
