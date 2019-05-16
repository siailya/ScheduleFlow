import requests
import pendulum
import os

url = 'http://school37.com/news/data/upimages/'

now_time = pendulum.now().hour
today_date = pendulum.today().date().__format__('DD.MM.YYYY')
day_of_week = pendulum.today().day
tomorrow_date = pendulum.tomorrow().date().__format__('DD.MM.YYYY')
a = '.02.2019'

for i in range(29):
    url = 'http://school37.com/news/data/upimages/'
    url += str(i) + a + '-001.png'
    source = requests.get(url)
    out = open(f"{str(i) + a}.png", 'wb')
    out.write(source.content)
    out.close()
    if os.stat(f"{str(i) + a}.png").st_size < 1000:
        os.remove(f"{str(i) + a}.png")
    print(url)