from pendulum import now
from vk_api.utils import get_random_id


def ring_schedule(vk_api, send_id):
    if now().weekday() == 0 or now().weekday() == 6:
        schedule = 'photo-187161295_457240609'
        if now().weekday() == 6:
            msg = 'Держи расписание звонков на завтра 😉'
        else:
            'Держи расписание звонков на сегодня 😉'
    else:
        schedule = 'photo-187161295_457240610'
        msg = 'Держи расписание звонков на сегодня 😉'

    vk_api.messages.send(peer_id=send_id,
                         message=msg,
                         random_id=get_random_id(),
                         attachment=schedule)