import cv2
import numpy as np
from PIL import Image, ImageFilter
import pendulum
import requests

# =================================
# ToDo: Нихрена не надо, все работает
# =================================
k, x, y = 0, 0, 0


def cond_defin_vert(i, y, pixels):
    cond = (pixels[i, int(y) + 5][0] <= 100) and \
           (pixels[i, int(y) + 5][1] <= 120) and \
           (pixels[i, int(y) + 5][2] <= 150)
    return cond


def cond_defin_gor(x, i, pixels):
    cond = (pixels[int(x), i][0] == 204) and \
           (pixels[int(x), i][1] == 204) and \
           (pixels[int(x), i][2] == 255)
    return cond


def bruteforce(p):
    global k, x, y, threshold
    cond = False
    threshold = p
    while not cond:
        try:
            template = cv2.imread('10A.jpg', 0)
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            coord = list(list(zip(*loc[::-1]))[0])
            x, y = tuple(coord)
        except IndexError:
            k += 1
            threshold -= 0.05
        else:
            cond = True


def wnh():
    global name
    width = 0
    for i in range(x, x - 250, -1):
        width += 1
        if cond_defin_vert(i, y, pixels):
            break

    height = 0
    for i in range(y + 20, y + 500):
        height += 1
        if cond_defin_gor(x, i, pixels):
            break
    return [width, height]


def box(x, y):
    # global width, heigth, box, x0, y0, x1, y1
    x0 = x - wnh()[0] + 1
    x1 = x + wnh()[0] + 23
    y0 = y - 3
    y1 = y + wnh()[1]
    box = (x0, y0, x1, y1)
    return box


def GetDate():
    return str(pendulum.tomorrow().date().__format__('DD.MM.YYYY'))


def GetUrl(date=GetDate()):
    url = 'http://school37.com/news/data/upimages/' + date + '-001.png'
    return url


def GetPic(url=GetUrl(date=GetDate()), date=GetDate()):
    p = requests.get(url)
    out = open(str(date) + ".png", "wb")
    out.write(p.content)
    out.close()


name = GetDate() + '.png'
GetPic()
img_rgb = cv2.imread(name)
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
img = Image.open(name)
pixels = img.load()

bruteforce(1)
wnh()

w, h = img.crop(box(x, y)).size
res = img.crop(box(x, y)).resize((int(w * 2), int(h * 2)), Image.ANTIALIAS). \
    filter(ImageFilter.SHARPEN)

res.save('res.jpg')
res.show()
