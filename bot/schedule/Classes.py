from os import remove, mkdir, path

import pendulum
from PIL import Image, ImageDraw, ImageFont
from pendulum import from_timestamp

from bot.database.DataBases import ScheduleBase
from bot.stuff import Utilities
from bot.stuff.Config import Config
from bot.stuff.Utilities import TZ


def OnlyHeaders(image):
    width, height = image.size
    result = Image.new('RGB', (width, height))
    for i in range(width):
        for j in range(height):
            color = image.getpixel((i, j))
            if color == (204, 204, 255):
                result.putpixel((i, j), color)
    return result


def FindParallels(image):
    res = []
    i = 0
    width, height = image.size
    while i < height and len(res) != 7:
        color = image.getpixel((100, i))
        if color == (204, 204, 255):
            res.append(i)
            i += 50
        i += 2
    return dict(zip((5, 6, 7, 8, 9, 10, 11), res))


def FindLetters(image, upper_parallel):
    res = []
    flag = False
    width, height = image.size
    for i in range(width):
        color = image.getpixel((i, upper_parallel))
        if color != (204, 204, 255):
            if flag:
                if len(res) >= 1:
                    if res[-1] + 1 != i:
                        res.append(i)
                else:
                    res.append(i)
                if len(res) == 5:
                    break
        else:
            flag = True
    return dict(zip(['А', 'Б', 'В', 'Г', 'Д'], res))


def FindClasses(image):
    marking = {}
    img = OnlyHeaders(image)
    parallels = FindParallels(img)
    letters = FindLetters(img, parallels[5])
    for cls in Utilities.CLASSES:
        num, letter = int(cls[:-1]), cls[-1:]
        marking.update({cls: ((letters[letter], letters[Utilities.NEXT_LETTER[letter]]), parallels[num])})
    marking.update({'parallels': parallels, 'letters': letters})
    return marking


def CropClass(image, cls, marking):
    x1, x2 = marking[cls][0]
    y1 = marking['parallels'][int(cls[:-1])]
    if cls[:-1] == '11':
        y2 = y1 + 200
    else:
        y2 = marking['parallels'][int(cls[:-1]) + 1]
    class_image = image.crop((x1 + 1, y1 - 2, x2 + 1, y2 - 2))
    width, height = class_image.size
    result = class_image.resize((int(width * 1.5), int(height * 1.5)), Image.ANTIALIAS)
    return result


def CropAllClasses(date):
    ScheduleBase().ClassesUpdate(date, pendulum.now(TZ))
    if not path.exists(Config.PATH + f'work/schedules/{date}'):
        mkdir(Config.PATH + f'work/schedules/{date}')
    try:
        img = Image.open(Config.PATH + f'work/source/{date}.png').convert('RGB')
        marking = FindClasses(img)
        for cls in Utilities.CLASSES:
            Watermarks(CropClass(img, cls, marking), date).save(Config.PATH + f'work/schedules/{date}/{cls}.png')
    except FileNotFoundError:
        remove(Config.PATH + f'work/schedules/{date}')


def DateWatermark(image, date):
    width, height = image.size
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(Config.PATH + 'bot/stuff/font.ttf', 20)
    update_text = f'{date}'
    text_width, text_height = draw.textsize(update_text, font=font)
    draw.text(((width - text_width) / 2, height - 40), update_text, fill='black', font=font)
    return image


def UpdateWatermark(image, date):
    full_image = Config.PATH + f'work/source/{date}.png'
    update_time = from_timestamp(path.getmtime(full_image), Utilities.TZ)
    width, height = image.size
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(Config.PATH + 'bot/stuff/font.ttf', 15)
    update_text = f'Обновлено {update_time.__format__("DD.MM.YYYY")} в {update_time.__format__("HH:mm")}'
    text_width, text_height = draw.textsize(update_text, font=font)
    draw.text(((width - text_width) / 2, height - 20), update_text, fill='gray', font=font)
    return image


def Watermarks(image, date):
    width, height = image.size
    result = Image.new('RGB', (width, height + 40), (255, 255, 255))
    result.paste(image)
    return DateWatermark(UpdateWatermark(result, date), date)
