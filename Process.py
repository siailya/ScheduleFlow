import cv2
import numpy as np
import pendulum
import requests
from PIL import Image, ImageFilter


def get_today_date():
    return str(pendulum.tomorrow().date().__format__('DD.MM.YYYY'))


def get_picture():
    date = get_today_date()
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
            self.name = get_today_date() + '.png'
            get_picture()
            # Открытие в OpenCV для поика шаблона
            self.img_rgb = cv2.imread(self.name)
            self.img_gray = cv2.cvtColor(self.img_rgb, cv2.COLOR_BGR2GRAY)

            self.img = Image.open(self.name)  # Открытие в PIL
            self.img.convert('RGB')
            self.color = (0, 0, 0)

            t_name = 'labels/' + name + '.jpg'
            template = Image.open(t_name)
            self.template_w, self.template_h = template.size

            self.x, self.y = self.brute_force(
                t_name)  # Точки найденного шаблона

            class_schedule = self.img.crop(self.find_box(name))
            w, h = class_schedule.size

            self.res = class_schedule.resize(
                (int(w * 2), int(h * 2)), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
            sname = save_name + '.jpg'
            self.res.save(sname)

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
                threshold -= 0.0005
            else:
                cond = True
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
            crop_y1 = y
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
        crop_x0 = x - 1

        # Поиск правой точки:
        delta_x2 = self.x + self.template_w
        x, y = int(delta_x2), int(self.y)
        color = self.img.getpixel((x, y))
        while color == self.color:
            x += 1
            color = self.img.getpixel((x, y))
        crop_x1 = x + 1

        return tuple([crop_x0, crop_y0, crop_x1, crop_y1])


if __name__ == '__main__':
    c = input('Введите номер класса')
    if c == 'all':
        a = input(
            'Вы хотите сохранить расписания всех классов в текущую директорию? y/n')
        if a == 'y':
            o = ['А', 'Б', 'В', 'Г']
            for i in range(5, 12):
                if i in [5, 10, 11]:
                    for j in range(4):
                        cl = str(i) + o[j]
                        ScheduleFlow(cl, cl)
                else:
                    for j in range(3):
                        cl = str(i) + o[j]
                        ScheduleFlow(cl, cl)
    elif c[:-1] in '567891011' and c[-1] in 'АБВГ':
        ScheduleFlow(c, c)
    else:
        print('Ошибка! такого класса не существует!')
