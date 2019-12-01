from os import remove, mkdir, path
from pickle import dump
from shutil import copy

import cv2
import numpy as np
import pendulum
import vk_api.vk_api
import vk_api.vk_api
from PIL import Image, ImageFilter
from pendulum import now
from vk_api import VkUpload

from Constantes import Constantes as cst
from Utilities import get_picture, upload_class, send_console, upload_pic

log_time = now(tz="Europe/Moscow").__format__("DD.MM HH:mm")


class ScheduleFlow:
    def __init__(self, cls_name, schedule_date):
        class_name = cls_name.upper()
        trans = {'А': 'A',
                 'Б': 'B',
                 'В': 'V',
                 'Г': 'G'}
        class_name = class_name[:-1] + trans[class_name[-1]]

        self.schedule_date = schedule_date
        self.name = self.schedule_date + '.png'

        self.img = Image.open(f'source/{self.name}')
        self.img.convert('RGB')
        self.color = (0, 0, 0)

        self.crop_for_class(class_name)
        self.img = Image.open(self.name)

        self.img_rgb = cv2.imread(self.name)
        self.img_gray = cv2.cvtColor(self.img_rgb, cv2.COLOR_BGR2GRAY)

        template_name = 'labels/' + class_name + '.jpg'
        template = Image.open(template_name)
        self.template_w, self.template_h = template.size

        self.x, self.y = self.brute_force(template_name)

        class_schedule = self.img.crop(self.find_box(class_name))
        w, h = class_schedule.size

        self.res = class_schedule.resize((int(w * 1.5), int(h * 1.5)),
                                         Image.ANTIALIAS).filter(
            ImageFilter.GaussianBlur(radius=0.1))
        s_name = self.schedule_date + '/' + cls_name + '.png'
        self.res.save(s_name)

    def brute_force(self, template_name):
        cond = False
        threshold = 0.7
        e, x, y = 0, 0, 0
        template = cv2.imread(template_name, 0)
        while (not cond) and (threshold > 0) and (e < 9):
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
        print(f'y = {y}; e = {e}; th = {threshold:.1f};', end=' ')
        with open(f'log/log_{log_time}.txt', encoding='u8', mode='a') as f:
            f.write(f'y = {y}; e = {e}; th = {threshold:.1f}; ')
        return x, y

    def find_box(self, class_name):
        crop_y0 = self.y - 3
        self.color = self.img.getpixel((int(self.x), int(self.y)))

        if class_name not in ['11A', '11B', '11V', '11G', '5G']:
            delta_y = self.y + 120
            x, y = int(self.x), int(delta_y)
            color = self.img.getpixel((x, y))
            while color != self.color:
                y += 1
                color = self.img.getpixel((x, y))
            crop_y1 = y - 15
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
        crop_x0 = x + 2

        delta_x2 = self.x + self.template_w
        x, y = int(delta_x2), int(self.y)
        color = self.img.getpixel((x, y))
        while color == self.color:
            x += 1
            color = self.img.getpixel((x, y))
        crop_x1 = x - 1

        return tuple([crop_x0, crop_y0, crop_x1, crop_y1])

    def crop_for_class(self, class_name):
        lit = class_name[-1]
        num = class_name[:-1]
        crop_lit = {'A': 0, 'B': 280, 'V': 560, 'G': 840}
        crop_num = {
            '5': 0,
            '6': 180,
            '7': int(175 * 2),
            '8': int(175 * 3),
            '9': int(175 * 4),
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
        tmp.save(f'tmp/{class_name}.png')


def download_all(date):
    if not path.exists(date):
        mkdir(date)

    picture = False
    if not path.exists(f'source/{date}.png'):
        get_picture(date)
        if path.exists(f'source/{date}.png'):
            picture = True
    else:
        picture = True

    if picture:
        f = open(f'log/log_{log_time}.txt', encoding='u8', mode='w+')
        f.write(f'{pendulum.now(tz="Europe/Moscow").__format__("HH:mm DD.MM.YYYY")}\n'
                f'Загрузка на {date}\n')
        f.close()

        errors = 0
        for i in cst.classes:
            try:
                ScheduleFlow(i, date)
                print(i)
                with open(f'log/log_{log_time}.txt', encoding='u8', mode='a') as f:
                    f.write(f'{i}\n')
            except:
                errors += 1
                print(f'{i} - ошибка!')
                with open(f'log/log_{log_time}.txt', encoding='u8', mode='a') as f:
                    f.write(f'{i} - ошибка!\n')
                copy('labels/error.png', f'{date}/{i}.png')

        if errors >= 10:
            with open(f'log/log_{log_time}.txt', encoding='u8', mode='w') as f:
                f.write('Одни ошибки!')

        with open(f'log/log_{log_time}.txt', encoding='u8', mode='r') as f:
            send_console(f'Лог обработки расписания на {date}:\n {f.read()}')

        if path.exists(f'{date}.png'):
            remove(f'{date}.png')

        vk = vk_api.VkApi(token=cst.token)
        upload = VkUpload(vk)

        uploaded_classes = {}
        for i in cst.classes:
            uploaded_classes.update({i: upload_class(i, upload, date)})
            print(i, end=' ')
        if picture:
            uploaded_classes.update({'main': upload_pic(f'source/{date}.png', upload)})

        with open(f'uploaded_photo/{date}.sf', 'wb') as f:
            dump(uploaded_classes, f)
    else:
        send_console(f'🆘 Общее расписание на {date} не найдено!')
        remove(f'source/{date}.png')
        remove(date)


if __name__ == '__main__':
    download_all('04.12.2019')
