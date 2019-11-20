from os import remove, mkdir, path, rmdir
from pickle import dump
from shutil import copy, rmtree

import cv2
import numpy as np
import pendulum
import vk_api.vk_api
import vk_api.vk_api
from PIL import Image, ImageFilter
from pendulum import now
from transliterate import translit
from vk_api import VkUpload

from Constantes import Constantes as cst
from Utilities import get_schedule_date, get_picture, send_console, upload_class, create_sf


class ScheduleFlow:
    def __init__(self, class_name, save_name='res', d=get_schedule_date()):
        name = class_name.upper()
        if name[:-1] in '567891011' and name[-1] in 'АБВГ':
            trans = {'А': 'A',
                     'Б': 'B',
                     'В': 'V',
                     'Г': 'G'}
            name = name[:-1] + trans[name[-1]]

            self.d = d
            self.name = self.d + '.png'
            if not path.exists(f'source/{self.d}.png'):
                get_picture()
                copy(f'source/{self.d}.png', f'{self.d}.png')
            else:
                copy(f'source/{self.d}.png', f'{self.d}.png')

            self.img = Image.open(self.name)
            self.img.convert('RGB')
            self.color = (0, 0, 0)

            self.crop_for_class(name)
            self.img = Image.open(self.name)

            self.img_rgb = cv2.imread(self.name)
            self.img_gray = cv2.cvtColor(self.img_rgb, cv2.COLOR_BGR2GRAY)

            t_name = 'labels/' + name + '.jpg'
            template = Image.open(t_name)
            self.template_w, self.template_h = template.size

            self.x, self.y = self.brute_force(t_name)

            class_schedule = self.img.crop(self.find_box(name))
            w, h = class_schedule.size

            self.res = class_schedule.resize((int(w * 1.5), int(h * 1.5)),
                                             Image.ANTIALIAS).filter(
                ImageFilter.GaussianBlur(radius=0.1))
            s_name = self.d + '/' + save_name + '.png'
            self.res.save(s_name)
            remove(self.name)

    def brute_force(self, template_name):
        time = now().__format__("DD.MM HH:mm")
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
        with open(f'log/log_{time}.txt', encoding='u8', mode='a') as f:
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


def download_all(date=get_schedule_date()):
    vk = vk_api.VkApi(token=cst.token)
    upload = VkUpload(vk)
    attachments = {}
    time = now(tz="Europe/Moscow").__format__("DD.MM HH:mm")
    if not path.exists('log'):
        mkdir('log')
    with open(f'log/log_{time}.txt', encoding='u8', mode='w') as f:
        f.write(f'{pendulum.now(tz="Europe/Moscow").__format__("HH:mm DD.MM.YYYY")}\n'
                f'Загрузка на {get_schedule_date()}\n')
        f.close()
    e = 0
    d = date
    print(d)
    c = True
    if not path.exists(str(d)):
        mkdir(str(d))
    if not path.exists(f'source/{d}.png'):
        get_picture(d)

    o = ['А', 'Б', 'В', 'Г']
    for i in range(5, 12):
        if i in [5, 10, 11]:
            for j in range(4):
                cl = str(i) + o[j]
                try:
                    ScheduleFlow(cl, cl, d)
                    attachments.update({cl: upload_class(cl, upload, d)})
                except BaseException as k:
                    e += 1
                    print(translit(f'\nОшибка {k} ', language_code='ru', reversed=True))
                    with open(f'log/log_{time}.txt', encoding='u8', mode='a') as f:
                        f.write(f'\nОшибка {k} ')
                        f.close()
                print(translit(cl, language_code='ru', reversed=True))
                with open(f'log/log_{time}.txt', encoding='u8', mode='a') as f:
                    f.write(f'{cl}\n')
                    f.close()
        else:
            for j in range(3):
                cl = str(i) + o[j]
                try:
                    ScheduleFlow(cl, cl, d)
                    attachments.update({cl: upload_class(cl, upload, d)})
                except BaseException as k:
                    e += 1
                    print(translit(f'\nОшибка {k} ', language_code='ru', reversed=True))
                    with open(f'log/log_{time}.txt', encoding='u8', mode='a') as f:
                        f.write(f'\nОшибка {k} ')
                        f.close()
                print(translit(cl, language_code='ru', reversed=True))
                with open(f'log/log_{time}.txt', encoding='u8', mode='a') as f:
                    f.write(f'{cl}\n')
                    f.close()
        if e >= 20:
            try:
                rmdir(str(d))
                remove(f'{str(d)}.png')
            except:
                pass
            with open(f'log/log_{time}.txt', encoding='u8', mode='a') as f:
                f.write('Лимит ошибок!')
                c = False
            break

    if c:
        create_sf(d)
        with open(f'uploaded_photo/{d}.sf', 'wb') as f:
            dump(attachments, f)
            f.close()
        with open(f'log/log_{time}.txt', encoding='u8', mode='r') as f:
            log = f.read()
            send_console(f'Лог загрузки расписания на {str(d)}:\n\n{log}')
            f.close()
        if not cst.save_files:
            rmtree(f'{get_schedule_date()}', )
    else:
        send_console(f'Лог загрузки расписания на {str(d)}:\nОдни ошибки')


if __name__ == '__main__':
    download_all()
