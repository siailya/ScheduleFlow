from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from bot.database.DataBases import SettingsBase


def MainMenu():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Обновить на сегодня', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Обновить на завтра', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Статистика', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Настройки', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Проверить наличие', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Список отслеживания', color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def Settings():
    Keyboard = VkKeyboard(one_time=False, inline=False)
    Parameters = SettingsBase().GetSettings()
    if Parameters['offline']:
        Keyboard.add_button('Оффлайн', color=VkKeyboardColor.NEGATIVE)
    else:
        Keyboard.add_button('Онлайн', color=VkKeyboardColor.POSITIVE)

    if Parameters['auto_distribution']:
        Keyboard.add_button('Рассылка вкл', color=VkKeyboardColor.POSITIVE)
    else:
        Keyboard.add_button('Рассылка выкл', color=VkKeyboardColor.NEGATIVE)
    Keyboard.add_line()

    if Parameters['auto_update']:
        Keyboard.add_button('Обновление вкл', color=VkKeyboardColor.POSITIVE)
    else:
        Keyboard.add_button('Обновление выкл', color=VkKeyboardColor.NEGATIVE)

    if Parameters['diary']:
        Keyboard.add_button('Дневник вкл', color=VkKeyboardColor.POSITIVE)
    else:
        Keyboard.add_button('Дневник выкл', color=VkKeyboardColor.NEGATIVE)
    Keyboard.add_line()

    if Parameters['main_replace']:
        Keyboard.add_button('Замена общим вкл', color=VkKeyboardColor.POSITIVE)
    else:
        Keyboard.add_button('Замена общим выкл', color=VkKeyboardColor.NEGATIVE)
    Keyboard.add_line()

    Keyboard.add_button('Выход', color=VkKeyboardColor.PRIMARY)
    Keyboard.add_button('Сброс', color=VkKeyboardColor.PRIMARY)

    return Keyboard.get_keyboard()