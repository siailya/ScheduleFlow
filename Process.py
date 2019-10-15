from os import remove, mkdir, path, rmdir
from shutil import move

import cv2
import numpy as np
import pendulum
import requests
import vk_api.vk_api
from PIL import Image, ImageFilter
from pendulum import *
from transliterate import translit
from vk_api.utils import get_random_id

from Constantes import Constantes as cst


def get_date(date=''):
    if not date:
        hr = now(tz='Europe/Moscow').time().hour
        mt = now(tz='Europe/Moscow').time().minute
        yr = tomorrow().year
        mtt = tomorrow().month
        td = now().weekday()
        if td == 6:
            return tomorrow().date().__format__('DD.MM.YYYY')
        elif td in [0, 1, 2, 3, 4]:
            if (hr >= 14) and ((hr <= 23) and (mt <= 59)):
                return tomorrow().date().__format__('DD.MM.YYYY')
            else:
                return today().date().__format__('DD.MM.YYYY')
        else:
            if ((hr >= 14) and (mt <= 30)) and ((hr <= 23) and (mt <= 59)):
                if tomorrow().day + 1 in [30, 31]:
                    if mtt in [1, 3, 5, 7, 8, 10, 12]:
                        if tomorrow().day + 1 == 31:
                            return pendulum.date(yr, mtt + 1, 1).__format__('DD.MM.YYYY')
                        else:
                            return pendulum.date(yr, mtt, 31).__format__('DD.MM.YYYY')
                    else:
                        if tomorrow().day + 1 == 30:
                            return pendulum.date(yr, mtt + 1, 1).__format__('DD.MM.YYYY')
                        else:
                            return pendulum.date(yr, mtt, 30).__format__('DD.MM.YYYY')
                else:
                    return pendulum.date(yr, mtt, tomorrow().day + 1).__format__('DD.MM.YYYY')
            else:
                return today().date().__format__('DD.MM.YYYY')
    else:
        return date


def get_picture(d, r=''):
    if not r:
        date = get_date(d)
        url = 'http://school37.com/news/data/upimages/' + date + '.png'
        p = requests.get(url)
        out = open(str(date) + ".png", "wb")
        out.write(p.content)
        out.close()
    else:
        if not path.exists('source'):
            mkdir('source')
        if path.exists('source'):
            date = get_date(d)
            name = date + ".png"
            if not path.exists(f'source/{name}'):
                url = 'http://school37.com/news/data/upimages/' + date + '.png'
                p = requests.get(url)
                out = open(name, "wb")
                out.write(p.content)
                out.close()
                move(name, f'source/{name}')


class ScheduleFlow:
    def __init__(self, class_name, save_name='res', d=''):
        name = class_name.upper()
        if name[:-1] in '567891011' and name[-1] in 'АБВГ':
            trans = {'А': 'A',
                     'Б': 'B',
                     'В': 'V',
                     'Г': 'G'}
            name = name[:-1] + trans[name[-1]]

            self.d = d
            self.name = get_date(d) + '.png'
            get_picture(d)
            self.img = Image.open(self.name)  # Открытие в PIL
            self.img.convert('RGB')
            self.color = (0, 0, 0)

            self.crop_for_class(name)
            self.img = Image.open(self.name)

            # Открытие в OpenCV для поика шаблона
            self.img_rgb = cv2.imread(self.name)
            self.img_gray = cv2.cvtColor(self.img_rgb, cv2.COLOR_BGR2GRAY)

            t_name = 'labels/' + name + '.jpg'
            template = Image.open(t_name)
            self.template_w, self.template_h = template.size

            self.x, self.y = self.brute_force(
                t_name)  # Точки найденного шаблона

            class_schedule = self.img.crop(self.find_box(name))
            w, h = class_schedule.size

            self.res = class_schedule.resize(
                (int(w * 2), int(h * 2)), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
            s_name = get_date(d) + '/' + save_name + '.jpg'
            self.res.save(s_name)
            remove(self.name)

    def brute_force(self, template_name):
        cond = False
        threshold = 0.7
        e = 0
        template = cv2.imread(template_name, 0)
        while (not cond) and (threshold > 0) and (e <= 30):
            try:
                res = cv2.matchTemplate(self.img_gray, template, cv2.TM_CCOEFF_NORMED)
                loc = np.where(res >= threshold)
                coord = list(list(zip(*loc[::-1]))[0])
                x, y = tuple(coord)
                e += 1
            except:
                threshold -= 0.1
                e += 1
            else:
                if y < 110:
                    cond = True
                else:
                    e += 1
                    threshold -= 0.1
        print(f'y = {y}; e = {e}; th = {threshold};', end=' ')
        with open('log.txt', encoding='u8', mode='a') as f:
            f.write(f'y = {y}; e = {e}; th = {threshold} ')
        return x, y

    def find_box(self, class_name):
        crop_y0 = self.y - 3
        self.color = self.img.getpixel((int(self.x), int(self.y)))

        if class_name not in ['11', '5', '11A', '11B', '11V', '11G', '5G']:
            delta_y = self.y + 120
            x, y = int(self.x), int(delta_y)
            color = self.img.getpixel((x, y))
            while color != self.color:
                y += 1
                color = self.img.getpixel((x, y))
            crop_y1 = y - 20
        else:
            delta_y = self.y + 240
            x, y = int(self.x), int(delta_y)
            color = self.img.getpixel((x, y))
            while color == (255, 255, 255):
                y -= 1
                color = self.img.getpixel((x, y))
            crop_y1 = y

        delta_x1 = self.x
        x, y = int(delta_x1), int(self.y)
        color = self.img.getpixel((x, y))
        while color == self.color:
            x -= 1
            color = self.img.getpixel((x, y))
        crop_x0 = x

        delta_x2 = self.x + self.template_w
        x, y = int(delta_x2), int(self.y)
        color = self.img.getpixel((x, y))
        while color == self.color:
            x += 1
            color = self.img.getpixel((x, y))
        crop_x1 = x + 1

        return tuple([crop_x0, crop_y0, crop_x1, crop_y1])

    def crop_for_class(self, class_name):
        lit = class_name[-1]
        num = class_name[:-1]
        crop_lit = {'A': 0, 'B': 280, 'V': 560, 'G': 840}
        crop_num = {
            '5': 0,
            '6': 180,
            '7': int(180 * 2),
            '8': int(180 * 3),
            '9': int(180 * 4),
            '10': int(180 * 5),
            '11': int(180 * 6)}
        crop_x = 400
        if class_name not in ['5G', '11A', '11B', '11V', '11G']:
            crop_y = 280
        else:
            crop_y = 450
        x0 = int(crop_lit[lit])
        x1 = int(x0 + crop_x)
        y0 = int(175 + crop_num[num])
        y1 = int(y0 + crop_y)
        tmp = self.img.crop((x0, y0, x1, y1))
        tmp.save(self.name)
        tmp.save(f'tmp/{class_name}.jpg')


def send_console(s):
    vk = vk_api.VkApi(token=cst.token)
    vk_apis = vk.get_api()
    vk_apis.messages.send(peer_id=cst.console_id, message=s, random_id=get_random_id())


def SF(cls='all', d=''):
    with open('log.txt', encoding='u8', mode='w') as f:
        f.write(f'{pendulum.now().__format__("HH:mm DD.MM.YYYY")}\n')
    e = 0
    d = get_date(d)
    if not path.exists(get_date(d)):
        mkdir(get_date(d))
    if cls == 'all':
        o = ['А', 'Б', 'В', 'Г']
        for i in range(5, 12):
            if i in [5, 10, 11]:
                for j in range(4):
                    cl = str(i) + o[j]
                    try:
                        ScheduleFlow(cl, cl, d)
                    except BaseException as k:
                        e += 1
                        print(translit(f'\nОшибка {k} ', language_code='ru', reversed=True))
                        with open('log.txt', encoding='u8', mode='a') as f:
                            f.write(f'\nОшибка {k} ')
                    print(translit(cl, language_code='ru', reversed=True))
                    with open('log.txt', encoding='u8', mode='a') as f:
                        f.write(f'{cl}\n')
            else:
                for j in range(3):
                    cl = str(i) + o[j]
                    try:
                        ScheduleFlow(cl, cl, d)
                    except BaseException as k:
                        e += 1
                        print(translit(f'\nОшибка {k} ', language_code='ru', reversed=True))
                        with open('log.txt', encoding='u8', mode='a') as f:
                            f.write(f'\nОшибка {k} ')
                    print(translit(cl, language_code='ru', reversed=True))
                    with open('log.txt', encoding='u8', mode='a') as f:
                        f.write(f'{cl}\n')
            if e >= 20:
                rmdir(get_date(d))
                remove(f'{get_date(d)}.png')
                with open('log.txt', encoding='u8', mode='a') as f:
                    f.write('Лимит ошибок!')
                break
        with open('log.txt', encoding='u8', mode='r') as f:
            send_console(f'Лог загрузки расписания на {get_date(d)}:\n\n{f.read()}')
    elif cls[:-1] in '567891011' and cls[-1] in 'АБВГ':
        try:
            ScheduleFlow(cls, cls, d)
        except BaseException:
            print('Error')
    else:
        print('Error! No such class!')


if __name__ == '__main__':
    SF()
