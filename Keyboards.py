from random import randint

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from Constantes import Constantes as cst


class Keyboards:
    def __init__(self, api):
        self.vk_api = api

    def start_keyboard(self, send_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Начать!', color=VkKeyboardColor.DEFAULT)
        self.vk_api.messages.send(peer_id=send_id, random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),
                                  message='Жми кнопку "Начать"')

    def menu_keyboard(self, send_id, c=True):
        keyboard = VkKeyboard(one_time=False)
        if c:
            keyboard.add_button('На сегодня', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('На завтра', color=VkKeyboardColor.DEFAULT)
            keyboard.add_line()
        keyboard.add_button('Общее на сегодня', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Общее на завтра', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Звонки', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Настройки', color=VkKeyboardColor.PRIMARY)
        if send_id in cst.grt_btn:
            keyboard.add_line()
            keyboard.add_button(f'Спасибо {cst.smiles_answer[randint(0, 13)]}', color=VkKeyboardColor.POSITIVE)
        self.vk_api.messages.send(peer_id=send_id, random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),
                                  message='Меню')

    def class_keyboard(self, send_id):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('5', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('6', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('7', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('8', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('9', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('10', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('11', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Без выбора класса', color=VkKeyboardColor.NEGATIVE)
        self.vk_api.messages.send(peer_id=send_id, random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),
                                  message='Выбери номера класса')

    def litera_keyboard(self, send_id, g):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('А', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Б', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('В', color=VkKeyboardColor.DEFAULT)
        if g:
            keyboard.add_button('Г', color=VkKeyboardColor.DEFAULT)
        self.vk_api.messages.send(peer_id=send_id, random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),
                                  message='Отлично! Теперь выбери литеру класса')

    def service_keyboard(self, send_id, stat, msg='Панель настройки'):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Сменить класс', color=VkKeyboardColor.DEFAULT)
        if stat == 1:
            keyboard.add_button('Выключить уведомления', color=VkKeyboardColor.DEFAULT)
        elif stat == 0:
            keyboard.add_button('Включить уведомления', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Помощь', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Назад', color=VkKeyboardColor.PRIMARY)
        self.vk_api.messages.send(peer_id=send_id, random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),
                                  message=msg)

    def conslole_keyboard(self):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Статистика', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Полная статистика', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Обновить', color=VkKeyboardColor.PRIMARY)
        self.vk_api.messages.send(peer_id=cst.console_id, random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),
                                  message='Консольное меню')

    def test_menu_keyboard(self, send_id, c=True):
        keyboard = VkKeyboard(one_time=False)
        if c:
            keyboard.add_button('На сегодня', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('На завтра', color=VkKeyboardColor.DEFAULT)
            keyboard.add_line()
        keyboard.add_button('Общее расписание', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Расписание звонков', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Настройки', color=VkKeyboardColor.PRIMARY)
        self.vk_api.messages.send(peer_id=send_id, random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),
                                  message='Тестовые возможности открыты!')
