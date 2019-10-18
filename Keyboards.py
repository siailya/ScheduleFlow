from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from Constantes import Constantes as cst


class Keyboards:
    def __init__(self, api):
        self.vk_api = api

    def menu_keyboard(self, send_id, c=True):
        keyboard = VkKeyboard(one_time=False)
        if c:
            keyboard.add_button('Расписание', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Общее расписание', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Расписание звонков', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Настройки', color=VkKeyboardColor.PRIMARY)
        self.vk_api.messages.send(peer_id=send_id, random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),
                                  message='Меню')

    def admin_keyboard(self, send_id):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Расписание', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Общее расписание', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Расписание звонков', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Пользователи', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Статистика', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Обновить', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('На завтра', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Настройки', color=VkKeyboardColor.DEFAULT)
        self.vk_api.messages.send(peer_id=send_id, random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),
                                  message='Админ-меню')

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
        keyboard.add_line()
        keyboard.add_button('Без выбора класса', color=VkKeyboardColor.NEGATIVE)
        self.vk_api.messages.send(peer_id=send_id, random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),
                                  message='Отлично! Теперь выбери литеру класса')

    def service_keyboard(self, send_id):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Сменить класс', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Назад', color=VkKeyboardColor.PRIMARY)
        self.vk_api.messages.send(peer_id=send_id, random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),
                                  message='Панель настройки')

    def conslole_keyboard(self):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Пользователи', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Загрузить', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Статистика', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Обновить', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('На завтра', color=VkKeyboardColor.PRIMARY)
        self.vk_api.messages.send(peer_id=cst.console_id, random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard(),
                                  message='Консольное меню')
