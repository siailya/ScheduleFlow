from pendulum import date, now


class Constantes:
    classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '7А',
               '7Б', '7В', '8А', '8Б', '8В', '9А', '9Б', '9В',
               '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В',
               '11Г']
    console_id = 2000000002
    admins = [223632391, 222383631, 66061219]
    token = ''
    group_id = '187161295'
    ver = '1.5'
    smiles = '😀😀😃😄😁😅😂🤣☺😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏✌🏽✌🏾✌🏿👍🏽👍🏾👍🏿🤲🏽🤲🏿🤲🏾👌' \
             '🏽👌🏾👌🏿🙏🏽🙏🏾🙏🏿✊🏽✊🏾✊🏿👋🏽👋🏾👋🏿☝🏽☝🏾☝🏿👎🏽👎🏾👎🏿👏🏽👏🏾👏🏿🖐🏽🖐🏾🖐🏿👊🏽👊🏾👊🏿🤙🏽🤙🏾🤙🏿🤚🏽🤚🏾🤚🏿🤞🏽🤞🏾🤞🏿👺🤡💩👻💀☠👽👾🤖🎃😺😸' \
             '😹😻😼😽🤝👍🏿👎🏿👊🏿✊🏾🤛🏾🤜🏾🤞🏾✌🏾🤟🏾🤘🏾👌🏿👈🏿👉🏿👆🏿👇🏿☝🏿✋🏿🤚🏾🖐🏾🖖🏾👋🏾🤙🏾💪🏾❤🧡💛💚💙💜💔❣💕💞💓💗💖💟💝💘'
    answers = ['Всегда пожалуйста 😉',
               'Стараемся для вас! 😀',
               'С любовью, ScheduleFlow 🥰',
               'Пожалуйста! Обращайся еще 🤗',
               'Всегда к вашим услугам 🙂',
               'Рад быть полезным 😉']
    smiles_answer = '😜😀😄😉😊😘😍😃😀😎✌🏻😺😸'
    error = 'Произошла ошибка! Мы постараемся выяснить в чем дело в кратчайшие сроки. ' \
            'Простите за неудобства 😔'
    stickers = ['Я тоже люблю стикеры 😉',
                'Отвечаю только смайликом на смайлик!',
                'Я не вижу, что там за стикер 😟\nНадеюсь, там улыбающийся котик',
                'А у меня нет стикеров 😟']
    pics = ['Если там мем, то мы оценим всей администрацией и отпишемся о результатах 😉',
            'Картинка в стиле мем жанра постирония?',
            'Боты не видят картинок 😟']
    music = ['Люблю Славу КПСС',
             'Качает, согласен',
             'Эх, ща бы на Макса Коржа...']
    uni = ['Люблю мандарины',
           f'До Нового Года '
           f'{(date(2020, 1, 1) - date(now().year, now().month, now().day)).in_days()} '
           f'дней/дня/день',
           'Считается, что среднестатистический человек смеется 15 раз в день. Мои разработчики '
           'явно психи',
           'В составе жевательной резинки присутствует каучук. А еще ацетон, бензин, пенопласт, '
           'керосин и даже хлорметан (шучу)',
           'Если оленям дать бананы, то они с удовольствием их съедят. Мои разработчики - олени',
           'Интересный факт № 33 У женщин в среднем IQ выше, чем у мужчин.',
           'Почему вода мокрая?',
           'Каждое ли чётное число, большее 2, можно представить в виде суммы двух простых чисел?',
           'Существует ли треугольник с целочисленными сторонами, медианами и площадью?',
           f'Сейчас {now().__format__("HH:mm")}, {now().__format__("DD.MM.YYYY")}',
           'Почему самолет не машет крыльями?']
