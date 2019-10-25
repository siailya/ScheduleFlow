from os import remove, mkdir, path, rmdir
from pickle import dump
from shutil import move, copy

import cv2
import numpy as np
import pendulum
import requests
import vk_api.vk_api
import vk_api.vk_api
from PIL import Image, ImageFilter
from pendulum import now
from transliterate import translit
from vk_api import VkUpload
from vk_api.utils import get_random_id

from Constantes import Constantes as cst
from Utilities import get_schedule_date


def get_picture(r=''):
    if not r:
        date = get_schedule_date()
        url = 'http://school37.com/news/data/upimages/' + date + '.png'
        p = requests.get(url)
        out = open(str(date) + ".png", "wb")
        out.write(p.content)
        out.close()
    else:
        if not path.exists('source'):
            mkdir('source')
        if path.exists('source'):
            date = get_schedule_date()
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
            self.name = get_schedule_date() + '.png'
            if not path.exists(f'source/{get_schedule_date()}.png'):
                get_picture('y')
                copy(f'source/{get_schedule_date()}.png', f'{get_schedule_date()}.png')
            else:
                copy(f'source/{get_schedule_date()}.png', f'{get_schedule_date()}.png')

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
            s_name = get_schedule_date() + '/' + save_name + '.png'
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
        with open(f'log/log_{now().__format__("DD.MM HH:mm")}.txt', encoding='u8', mode='a') as f:
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
        # tmp.save(f'tmp/{class_name}.png')


def send_console(s):
    vk = vk_api.VkApi(token=cst.token)
    vk_apis = vk.get_api()
    vk_apis.messages.send(peer_id=cst.console_id, message=s, random_id=get_random_id())


def upload_class(cls, upload):
    response = upload.photo_messages(f'{get_schedule_date()}/{cls}.png')[0]
    attachment = f'photo{response["owner_id"]}_{response["id"]}_{response["access_key"]}'
    return attachment


def download_all():
    vk = vk_api.VkApi(token=cst.token)
    upload = VkUpload(vk)
    attachments = {}
    with open(f'log/log_{now().__format__("DD.MM HH:mm")}.txt', encoding='u8', mode='w') as f:
        f.write(f'{pendulum.now().__format__("HH:mm DD.MM.YYYY")}\n')
    e = 0
    d = get_schedule_date()
    if not path.exists(str(get_schedule_date())):
        mkdir(str(get_schedule_date()))

    o = ['А', 'Б', 'В', 'Г']
    for i in range(5, 12):
        if i in [5, 10, 11]:
            for j in range(4):
                cl = str(i) + o[j]
                try:
                    ScheduleFlow(cl, cl, d)
                    attachments.update({cl: upload_class(cl, upload)})
                except BaseException as k:
                    e += 1
                    print(translit(f'\nОшибка {k} ', language_code='ru', reversed=True))
                    with open(f'log/log_{now().__format__("DD.MM HH:mm")}.txt', encoding='u8', mode='a') as f:
                        f.write(f'\nОшибка {k} ')
                print(translit(cl, language_code='ru', reversed=True))
                with open(f'log/log_{now().__format__("DD.MM HH:mm")}.txt', encoding='u8', mode='a') as f:
                    f.write(f'{cl}\n')
        else:
            for j in range(3):
                cl = str(i) + o[j]
                try:
                    ScheduleFlow(cl, cl, d)
                    attachments.update({cl: upload_class(cl, upload)})
                except BaseException as k:
                    e += 1
                    print(translit(f'\nОшибка {k} ', language_code='ru', reversed=True))
                    with open(f'log/log_{now().__format__("DD.MM HH:mm")}.txt', encoding='u8', mode='a') as f:
                        f.write(f'\nОшибка {k} ')
                print(translit(cl, language_code='ru', reversed=True))
                with open(f'log/log_{now().__format__("DD.MM HH:mm")}.txt', encoding='u8', mode='a') as f:
                    f.write(f'{cl}\n')
        if e >= 20:
            rmdir(str(get_schedule_date()))
            remove(f'{str(get_schedule_date())}.png')
            with open(f'log/log_{now().__format__("DD.MM HH:mm")}.txt', encoding='u8', mode='a') as f:
                f.write('Лимит ошибок!')
            break

    with open(f'uploaded_photo/{get_schedule_date()}.sf', 'wb') as f:
        dump(attachments, f)

    with open(f'log/log_{now().__format__("DD.MM HH:mm")}.txt', encoding='u8', mode='r') as f:
        send_console(f'Лог загрузки расписания на {str(get_schedule_date())}:\n\n{f.read()}')


if __name__ == '__main__':
    download_all()
