from pendulum import today, tomorrow, date, now


def get_schedule_date():
    hr = now(tz='Europe/Moscow').time().hour
    mt = now(tz='Europe/Moscow').time().minute
    yr = tomorrow().year
    mtt = tomorrow().month
    td = now().weekday()
    if td == 6:
        return tomorrow().date().__format__('DD.MM.YYYY')
    elif td in [0, 1, 2, 3, 4]:
        if (hr >= 14) and ((hr <= 23) and (mt <= 59)):
            return tomorrow().date().__format__('DD.MM.YYYY')
        else:
            return today().date().__format__('DD.MM.YYYY')
    else:
        if (hr >= 14) and ((hr <= 23) and (mt <= 59)):
            if tomorrow().day + 1 in [30, 31]:
                if mtt in [1, 3, 5, 7, 8, 10, 12]:
                    if tomorrow().day + 1 == 31:
                        return date(yr, mtt + 1, 1).__format__('DD.MM.YYYY')
                    else:
                        return date(yr, mtt, 31).__format__('DD.MM.YYYY')
                else:
                    if tomorrow().day + 1 == 30:
                        return date(yr, mtt + 1, 1).__format__('DD.MM.YYYY')
                    else:
                        return date(yr, mtt, 30).__format__('DD.MM.YYYY')
            else:
                return date(yr, mtt, tomorrow().day + 1).__format__('DD.MM.YYYY')
        else:
            return today().date().__format__('DD.MM.YYYY')

