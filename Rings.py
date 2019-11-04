from pendulum import now
from vk_api.utils import get_random_id


def ring_schedule(vk_api, send_id):
    msg_ring = 'Держи расписание звонков на сегодня 😉'
    if now().weekday() == 0 or now().weekday() == 6:
        schedule = 'photo-187161295_457240609'
        if now().weekday() == 6:
            msg_ring = 'Держи расписание звонков на завтра 😉'
        else:
            'Держи расписание звонков на сегодня 😉'
    else:
        schedule = 'photo-187161295_457240610'
        msg_ring = 'Держи расписание звонков на сегодня 😉'

    vk_api.messages.send(peer_id=send_id,
                         message=msg_ring,
                         random_id=get_random_id(),
                         attachment=schedule)