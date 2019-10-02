import cv2
import numpy as np
import pendulum
import requests
from os import remove, mkdir, path
from PIL import Image, ImageFilter


def get_tomorrow_date():
    # return str(pendulum.tomorrow().date().__format__('DD.MM.YYYY'))
    return str(pendulum.date(2019, 10, 1).__format__('DD.MM.YYYY'))


def get_picture():
    date = get_tomorrow_date()
    url = 'http://school37.com/news/data/upimages/' + date + '-001.png'
    p = requests.get(url)
    out = open(str(date) + ".png", "wb")
    out.write(p.content)
    out.close()


class ScheduleFlow:
    def __init__(self, class_name, save_name='res'):
        name = class_name.upper()
        if name[:-1] in '567891011' and name[-1] in 'АБВГ':
            trans = {'А': 'A',
                     'Б': 'B',
                     'В': 'V',
                     'Г': 'G'}
            name = name[:-1] + trans[name[-1]]
            self.name = get_tomorrow_date() + '.png'
            get_picture()
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
            s_name = get_tomorrow_date() + '/' + save_name + '.jpg'
            self.res.save(s_name)
            remove(self.name)

    # Функция для поика надписи класса
    # Брутфорс - потому что ищется грубым перебором
    # Я пока не придумал способ лучше
    def brute_force(self, template_name):
        # Поиск координат класса по шаблону
        # Код самого Темплейт-метчинга я где-то нашел, но тут 1 строка
        cond = False
        threshold = 1  # Максимальная точность. Но найросеть в принципе не выдает 100-процентную
        # точность, поэтому будем уменьшать ее:
        # Открытие самого шаблона, по которому ищем класс
        template = cv2.imread(template_name, 0)
        # Последовательно уменьшаю threshold по 0,0005 (около
        while not cond and threshold > 0:
            # 0,005%, поэтому итераций очень много)
            try:
                res = cv2.matchTemplate(
                    self.img_gray, template, cv2.TM_CCOEFF_NORMED)
                # Выполняем поиск
                # Преобразование карты в массив для обработки и
                loc = np.where(res >= threshold)
                # поиска подходящих значений
                # Получаем координаты верхнего левого угла
                coord = list(list(zip(*loc[::-1]))[0])
                x, y = tuple(coord)
            except IndexError:  # Если подходящих значений не оказалось, уменьшаем и прокручиваем
                # опять
                threshold -= 0.0008
            else:
                cond = True
        print(x, y)
        return x, y

    # Функция поиска левой, верхней, правой и нижней координаты класса
    def find_box(self, class_name):
        crop_y0 = self.y - 3
        self.color = self.img.getpixel((int(self.x), int(self.y)))

        # Поиск нижней точки:
        # Для верхних:
        if class_name not in ['11', '5', '11A', '11B', '11V', '11G', '5G']:
            delta_y = self.y + 120
            x, y = int(self.x), int(delta_y)
            color = self.img.getpixel((x, y))
            while color != self.color:
                y += 1
                color = self.img.getpixel((x, y))
            crop_y1 = y - 20
        # Для нижних
        else:
            delta_y = self.y + 240
            x, y = int(self.x), int(delta_y)
            color = self.img.getpixel((x, y))
            while color == (255, 255, 255):
                y -= 1
                color = self.img.getpixel((x, y))
            crop_y1 = y

        # Поиск левой точки:
        delta_x1 = self.x
        x, y = int(delta_x1), int(self.y)
        color = self.img.getpixel((x, y))
        while color == self.color:
            x -= 1
            color = self.img.getpixel((x, y))
        crop_x0 = x

        # Поиск правой точки:
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
        crop_num = {'5': 0, '6': 180, '7': int(180 * 2.1), '8': int(180 * 3.1), '9': int(180 * 4.1),
                    '10': int(180 * 5.25), '11': int(180 * 6.4)}
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
        tmp.save(class_name + '1111' + '.jpg')


if __name__ == '__main__':
    if not path.exists(get_tomorrow_date()):
        mkdir(get_tomorrow_date())
    c = input('Введите номер класса, либо команду "all" для загрузки всех расписаний\n')
    if c == 'all':
        a = input(
            f'Вы хотите сохранить расписания всех классов в директорию "{get_tomorrow_date()}" y/n\n')
        if a == 'y':
            o = ['А', 'Б', 'В', 'Г']
            for i in range(5, 12):
                if i in [5, 10, 11]:
                    for j in range(4):
                        cl = str(i) + o[j]
                        try:
                            ScheduleFlow(cl, cl)
                        except:
                            print('Ошибка', end=' ')
                        print(cl)
                else:
                    for j in range(3):
                        cl = str(i) + o[j]
                        try:
                            ScheduleFlow(cl, cl)
                        except:
                            print('Ошибка', end=' ')
                        print(cl)
    elif c[:-1] in '567891011' and c[-1] in 'АБВГ':
        try:
            ScheduleFlow(c, c)
        except:
            print('Ошибка')
    else:
        print('Ошибка! такого класса не существует!')