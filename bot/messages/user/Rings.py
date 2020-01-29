import pendulum


def GetRings(date):
    d = pendulum.from_format(date, 'DD.MM.YYYY')
    if d.day_of_week in [1, 7]:
        return 'photo-187161295_457240609'
    else:
        return 'photo-187161295_457240610'