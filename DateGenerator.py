import pendulum
import requests


class URL:

    @staticmethod
    def __init__(self):
        now_time = pendulum.now().hour
        today_date = pendulum.today().date().__format__('DD.MM.YYYY')
        day_of_week = pendulum.today().day
        tomorrow_date = pendulum.tomorrow().date().__format__('DD.MM.YYYY')

        url = 'http://school37.com/news/data/upimages/'
        url += today_date + '-001.png'

        p = requests.get(url)
        out = open(str(today_date) + ".jpg", "wb")
        out.write(p.content)
        out.close()


    @staticmethod
    def GetDate(self):
        return pendulum.today().date().__format__('DD.MM.YYYY')