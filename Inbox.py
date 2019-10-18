from pickle import *
from random import randint
import vk_api.vk_api
from transliterate import translit
from Constantes import Constantes as cst
from Keyboards import *
from Process import *
import pendulum

class Inbox:
    def __init__(self, session, event, base, stat):
        self.base = base
        self.stat = stat
        self.vk = session
        self.upload = vk_api.VkUpload(self.vk)
        self.vk_api = self.vk.get_api()

        self.nums = [str(i) for i in range(5, 12)]
        self.literas = ['а', 'б', 'в', 'г']

        self.peer_id = event.obj.peer_id
        if self.peer_id == cst.console_id:
            self.console(event)
        elif self.peer_id in cst.admins:
            self.user(event, True)
        else:
            self.user(event)
        self.write_base()

    def user(self, event, a=False):
        u_id = self.peer_id
        msg = event.obj.text.lower()
        name, last = self.u_get(u_id)
        if u_id not in cst.admins:
            self.send_msg(cst.console_id, f'Сообщение от: @id{u_id}({name} {last}) ('
                                          f'{self.base[u_id][2]})\n'
                                           f'{event.obj.text}')
            print(translit(f'Сообщение от: @id{u_id}({name} {last})\n{event.obj.text}',
                           reversed=True))
        # Регистрация нового пользователя
        if u_id not in self.base.keys():
            self.base.update({u_id: [name, last, 'Ns', 0]})
            self.stat['users'] = self.stat.get('users', 0) + 1
            self.write_base()
            self.send_msg(u_id, f'Привет, {name}! Давай настроим бота под тебя. Тебе нужно просто '
                                f'указать свой класс')
            self.send_msg(cst.console_id, f'Новый юзер!\nВстречайте - @id{u_id}({name} {last})')
            Keyboards(self.vk_api).class_keyboard(u_id)
        else:
            # Выбор класса:
            if (msg in self.nums) and (self.base[u_id][3] == 0):
                self.base[u_id][2] = msg
                self.base[u_id][3] = 1
                self.write_base()
                if msg in ['5', '10', '11']:
                    Keyboards(self.vk_api).litera_keyboard(u_id, True)
                else:
                    Keyboards(self.vk_api).litera_keyboard(u_id, False)
            # Выбор литеры:
            elif (msg in self.literas) and (self.base[u_id][3] == 1):
                self.base[u_id][2] += msg
                self.base[u_id][3] = 2
                self.write_base()
                self.send_msg(u_id, f'Замечательно! Вы выбрали {self.base[u_id][2].upper()} класс! '
                                    f'Этот выбор всегда можно сменить в настройках')
                if a:
                    Keyboards(self.vk_api).admin_keyboard(u_id)
                else:
                    Keyboards(self.vk_api).menu_keyboard(u_id)
            # Пользование без класса:
            elif msg == 'без выбора класса':
                self.base[u_id][2] = ''
                self.base[u_id][3] = 2
                self.write_base()
                self.send_msg(u_id, '🙁 Без выбора класса не будет доступен весь функционал. Но '
                                    'его всегда можно выбрать в настройках 😉')
                Keyboards(self.vk_api).menu_keyboard(u_id, False)
            # Расписание
            elif self.base[u_id][3] == 2:
                if msg == 'расписание':
                    self.stat['requests'] = self.stat.get('requests', 0) + 1
                    self.write_base()
                    if path.exists(f'{get_date()}/{self.base[u_id][2].upper()}.png'):
                        self.photo(u_id, f'{get_date()}/{self.base[u_id][2].upper()}.png',
                                   f'Держи расписание '
                                   f'{self.base[u_id][2].upper()} '
                                   f'класса на {get_date()} ☺')
                    else:
                        self.send_msg(u_id, f'Сейчас попробую найти расписание на {get_date()} '
                                            f'😉\nЕсли прошло больше 10 секунд, то, скорее всего, '
                                            f'все идет по плану!')
                        SF()
                        try:
                            self.photo(u_id, f'{get_date()}/{self.base[u_id][2].upper()}.png',
                                       f'Держи расписание {self.base[u_id][2].upper()} '
                                       f'класса на {get_date()} ☺')
                        except:
                            self.send_msg(u_id, f'Что-то пошло не так 😲\nЯ не нашел расписание'
                                                f' {self.base[u_id][2].upper()} класса на '
                                                f'{get_date()} 😰')
                # Общее расписание
                elif msg == 'общее расписание':
                    self.stat['requests'] = self.stat.get('requests', 0) + 1
                    self.write_base()
                    if not path.exists(f'source/{get_date()}.png'):
                        get_picture(get_date(), '1')
                    self.photo(u_id, f'source/{get_date()}.png', f'Держи общее расписание'
                                                                 f' на {get_date()} 😊')
                elif msg == 'расписание звонков':
                    self.sch(u_id)
                elif msg == 'настройки':
                    Keyboards(self.vk_api).service_keyboard(u_id)
                elif msg == 'сменить класс':
                    Keyboards(self.vk_api).class_keyboard(u_id)
                    self.base[u_id][3] = 0
                elif msg == 'назад':
                    if a:
                        Keyboards(self.vk_api).admin_keyboard(u_id)
                    else:
                        Keyboards(self.vk_api).menu_keyboard(u_id)
                elif msg == 'пользователи':
                    if u_id in cst.admins:
                        u = 'Список юзеров:\n'
                        for i in self.base.keys():
                            if i < 2000000000:
                                u += f'@id{i}({self.base[i][0]} {self.base[i][1]}) - ' \
                                     f'{self.base[i][2].upper()}\n'
                            else:
                                u += f'Беседа {i} - {self.base[i].upper()}\n'
                        self.send_msg(u_id, u)
                    else:
                        self.send_msg(u_id, 'А ты точно администратор? 🙃\nДанная функция доступна '
                                            'только администраторам!')
                elif msg == 'статистика':
                    if u_id in cst.admins:
                        self.send_msg(u_id, f'Число запросов расписания: '
                                            f'{self.stat["requests"]}\nЧисло юзеров:'
                                            f' {self.stat["users"]}\n'
                                            f'Поблагодарили: {self.stat["thank"]}')
                    else:
                        self.send_msg(u_id, 'А ты точно администратор? 🙃\nДанная функция доступна '
                                            'только администраторам!')
                elif msg == 'обновить':
                    if u_id in cst.admins:
                        SF()
                        self.send_msg(u_id, 'Обновлено! Ошибки смотри в консоли')
                    else:
                        self.send_msg(u_id, 'А ты точно администратор? 🙃\nДанная функция доступна '
                                            'только администраторам!')
                elif 'общая рассылка лс' in msg:
                    if u_id in cst.admins:
                        ms = event.obj.text[18:]
                        for i in self.base.keys():
                            self.send_msg(i, ms)
                    else:
                        self.send_msg(u_id, 'А ты точно администратор? 🙃\nДанная функция доступна '
                                            'только администраторам!')
                elif 'рассылка класс' in msg:
                    if u_id in cst.admins:
                        cls, text = event.obj.text[15:].split('_')
                        print(cls)
                        for i in self.base.keys():
                            if self.base[i][2] == cls.lower():
                                self.send_msg(i, text)
                    else:
                        self.send_msg(u_id, 'А ты точно администратор? 🙃\nДанная функция доступна '
                                            'только администраторам!')
                elif msg == 'на завтра':
                    if u_id in cst.admins:
                        try:
                            self.send_msg(u_id, 'Проверяю расписание на завтра')
                            print(pendulum.tomorrow().date().__format__('DD.MM.YYYY'))
                            SF('all', get_date(pendulum.tomorrow().date().__format__('DD.MM.YYYY')))
                            self.send_msg(u_id, 'Расписание на завтра загружено!')
                        except:
                            self.send_msg(u_id, 'Ошибка! Скорее всего, расписания на завтра просто '
                                                'нет...')
                    else:
                        self.send_msg(u_id, 'А ты точно администратор? 🙃\nДанная функция доступна '
                                            'только администраторам!')
                elif msg in '😀😀😃😄😁😅😂🤣☺😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏' \
                            '✌🏽✌🏾✌🏿👍🏽👍🏾👍🏿🤲🏽🤲🏿🤲🏾👌🏽👌🏾👌🏿🙏🏽🙏🏾🙏🏿✊🏽✊🏾✊🏿👋🏽👋🏾👋🏿☝🏽☝🏾☝🏿👎🏽👎🏾👎🏿👏🏽👏🏾👏🏿🖐🏽🖐🏾🖐🏿👊🏽' \
                            '👊🏾👊🏿🤙🏽🤙🏾🤙🏿🤚🏽🤚🏾🤚🏿🤞🏽🤞🏾🤞🏿' \
                            '👺🤡💩👻💀☠👽👾🤖🎃😺😸😹😻😼😽' \
                            '🤝👍🏿👎🏿👊🏿✊🏾🤛🏾🤜🏾🤞🏾✌🏾🤟🏾🤘🏾👌🏿👈🏿👉🏿👆🏿👇🏿☝🏿✋🏿🤚🏾🖐🏾🖖🏾👋🏾🤙🏾💪🏾' \
                            '❤🧡💛💚💙💜💔❣💕💞💓💗💖💟💝💘':
                    self.send_msg(u_id, '😜😀😄😉😊😘😍😃😀😎✌🏻😺😸'[randint(0, 13)])
                elif 'спасибо' in msg or 'спс' in msg or 'пасиб' in msg or 'сенкс' in msg or 'thank' \
                        in msg or 'от души' in msg or 'благодарю' in msg:
                    self.stat['thank'] = self.stat.get('thank', 0) + 1
                    answ = ['Всегда пожалуйста 😉',
                            'Стараемся для вас! 😀',
                            'С любовью, ScheduleFlow 🥰',
                            'Пожалуйста! Обращайся еще 🤗',
                            'Всегда к вашим услугам 🙂',
                            'Рад быть полезным 😉']
                    self.send_msg(u_id, answ[randint(0, 5)])
                elif 'дарова' in msg:
                    self.send_msg(u_id, 'Ну дарова, карова')
                else:
                    if 13 >= len(msg) >= 2:
                        if len(msg) == 2 or len(msg) == 3:
                            cls = msg.upper()
                            if cls in cst.classes:
                                if path.exists(f'{get_date()}/{cls}.png'):
                                    self.photo(u_id, f'{get_date()}/{cls}.png',
                                               f'Держи расписание {cls} '
                                               f'класса на {get_date()} 😃')
                                else:
                                    self.send_msg(u_id, f'Не удалось найти расписание {cls} '
                                                        f'класса на {get_date()} 😰')
                        elif ',' in msg and '.' in msg:
                            cls, date = msg.replace(' ', '').split(',', maxsplit=1)
                            date += '.' + str(pendulum.now().year)
                            d, m, y = [int(i) for i in date.split('.')]
                            date = pendulum.date(y, m, d).__format__('DD.MM.YYYY')
                            cls = cls.upper()
                            if cls in cst.classes:
                                try:
                                    SF(cls, date)
                                    self.photo(u_id, f'{date}/{cls}.png', f'Держи расписание {cls} '
                                                                          f'класса на {date} 🤗')
                                except:
                                    self.send_msg(u_id, f'Произошла ошибка, либо даты {date} не '
                                                        f'бывает 😰\nСсылка на '
                                                        f'расписание на сайте: https://vk.cc/9UO0Pl')
                            else:
                                self.send_msg(u_id, f'Нет класса {cls} 😦')

    def console(self, event):
        # Keyboards(self.vk_api).conslole_keyboard()
        msg = event.obj.text.lower().replace('@', '')
        if msg == '[club187161295|scheduleflow] пользователи':
            u = 'Список юзеров:\n'
            for i in self.base.keys():
                if i < 2000000000:
                    u += f'@id{i}({self.base[i][0]} {self.base[i][1]}) - ' \
                         f'{self.base[i][2].upper()}\n'
                else:
                    u += f'Беседа {i} - {self.base[i][2].upper()}\n'
            self.send_msg(cst.console_id, u)
        elif msg == '[club187161295|scheduleflow] загрузить':
            if path.exists(f'{get_date()}'):
                self.send_msg(cst.console_id, 'Расписание уже находится в директории!')
            else:
                self.send_msg(cst.console_id, f'Попытка скачать расписание. Ход выполнения '
                                               f'отслеживается в консоли.')
                SF()
                self.send_msg(cst.console_id, f'Расписание на {get_date()} загружено! Ошибки '
                                               f'выше')
        elif msg == '[club187161295|scheduleflow] обновить':
            SF()
            self.send_msg(cst.console_id, f'Расписание на {get_date()} обновлено!')
        elif msg == '[club187161295|scheduleflow] статистика':
            self.send_msg(cst.console_id, f'Число запросов расписания: '
                                           f'{self.stat["requests"]}\nЧисло юзеров: '
                                           f'{self.stat["users"]}')
        elif msg == '[club187161295|scheduleflow] на завтра':
            try:
                self.send_msg(cst.console_id, 'Проверяю расписание на завтра')
                print(pendulum.tomorrow().date().__format__('DD.MM.YYYY'))
                SF('all', get_date(pendulum.tomorrow().date().__format__('DD.MM.YYYY')))
                self.send_msg(cst.console_id, 'Расписание на завтра загружено!')
            except:
                self.send_msg(cst.console_id, 'Ошибка! Скорее всего, расписания на завтра просто '
                                              'нет...')
        elif 'общая рассылка лс' in msg:
            ms = event.obj.text[18:]
            print(translit(ms))
            for i in self.base.keys():
                if i < 2000000000:
                    self.send_msg(i, ms)
        elif 'общая рассылка все' in msg:
            ms = event.obj.text[19:]
            print(translit(ms))
            for i in self.base.keys():
                self.send_msg(i, ms)

    def write_base(self):
        pt = 'data/base.pickle'
        with open(pt, 'wb') as fi:
            dump(self.base, fi)

        pt = 'data/stat.pickle'
        with open(pt, 'wb') as fi:
            dump(self.stat, fi)

    def open_base(self):
        pt = 'data/base.pickle'
        with open(pt, 'rb') as fi:
            self.base = load(fi)

        pt = 'data/stat.pickle'
        with open(pt, 'wb') as fi:
            self.stat = load(fi)

    def photo(self, send_id, root='img.png', msg=''):
        response = self.upload.photo_messages(root)[0]
        attachment = f'photo{response["owner_id"]}_{response["id"]}_{response["access_key"]}'
        self.vk_api.messages.send(peer_id=send_id,
                                  message=msg,
                                  random_id=get_random_id(),
                                  attachment=attachment)

    def sch(self, send_id):
        if pendulum.now().weekday() == 0:
            s = 'photo-187161295_457240000'
        elif pendulum.now().weekday() != 6:
            s = 'photo-187161295_457240001'
        else:
            s = 0
            self.send_msg(send_id, 'По воскресеньям не учимся 😉')
        if s:
            self.vk_api.messages.send(peer_id=send_id,
                                      message='Держи расписание звонков на сегодня 😉',
                                      random_id=get_random_id(),
                                      attachment=s)

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(peer_id=send_id,
                                  message=message,
                                  random_id=get_random_id())

    def u_get(self, uid):
        info = self.vk_api.users.get(user_ids=uid)[0]
        return info['first_name'], info['last_name']