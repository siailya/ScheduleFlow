from vk_api.keyboard import VkKeyboardColor, VkKeyboard


def StartKeyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать!', color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def DenyKeyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Отмена', color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()


def MenuKeyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('На сегодня', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('На завтра', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Общее на сегодня', color=VkKeyboardColor.DEFAULT)
    keyboard.add_button('Общее на завтра', color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()
    keyboard.add_button('Звонки', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('ДЗ', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Настройки', color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def ChooseClassNum():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('5', color=VkKeyboardColor.DEFAULT)
    keyboard.add_button('6', color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()
    keyboard.add_button('7', color=VkKeyboardColor.DEFAULT)
    keyboard.add_button('8', color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()
    keyboard.add_button('9', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('10', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('11', color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def ChooseClassLetter(g_class):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('А', color=VkKeyboardColor.DEFAULT)
    keyboard.add_button('Б', color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()
    keyboard.add_button('В', color=VkKeyboardColor.DEFAULT)
    if g_class:
        keyboard.add_button('Г', color=VkKeyboardColor.DEFAULT)
    return keyboard.get_keyboard()


def SettingsKeyboard(stat, parse_stat=0):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Сменить класс', color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()
    if stat == 1:
        keyboard.add_button('Выключить уведомления', color=VkKeyboardColor.NEGATIVE)
    elif stat == 0:
        keyboard.add_button('Включить уведомления', color=VkKeyboardColor.POSITIVE)
    if parse_stat == 1:
        keyboard.add_button('Не отслеживать расписания', color=VkKeyboardColor.NEGATIVE)
    elif parse_stat == 0:
        keyboard.add_button('Отслеживать расписания', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Назад', color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def HomeworkKeyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Показать ДЗ', color=VkKeyboardColor.DEFAULT)
    keyboard.add_line()
    keyboard.add_button('Добавить ДЗ', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Пожаловаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('Указать дату', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Выход', color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()
