from pendulum import now, yesterday


def get_id_by_class(base, cls):
    cur = base.cursor()
    res = cur.execute(
        f"""
        SELECT id FROM users
        WHERE cls = '{cls}' AND notifications = 1
        """
    ).fetchall()
    return res


def get_by_parallel(base, par):
    cur = base.cursor()
    res = cur.execute(
        f"""
            SELECT id FROM users
            WHERE cls_num = '{par}'
            """
    ).fetchall()
    return res


def get_all_ids(base):
    cur = base.cursor()
    res = cur.execute(
        f"""
        SELECT id from users
        """
    ).fetchall()
    return res


def get_by_id(base, id):
    cur = base.cursor()
    res = cur.execute(
        f"""
        SELECT name, last, cls, requests FROM users
        WHERE id = {id}
        """
    ).fetchall()
    return res


def del_by_id(base, id):
    cur = base.cursor()
    res = cur.execute(
        f"""
            DELETE FROM users
            WHERE id = {id}
            """
    ).fetchall()
    base.commit()
    return res


def get_by_name(base, name, last):
    cur = base.cursor()
    res = cur.execute(
        f"""
            SELECT name, last, cls, id, requests, gratitudes FROM users
            WHERE name = '{name}' AND last = '{last}'
            """
    ).fetchall()
    return res


def add_new_day(base):
    cur = base.cursor()
    res = cur.execute(
        f"""
        SELECT * from stat WHERE date = '{now(tz="Europe/Moscow").__format__("YYYY-MM-DD")}'
        """
    ).fetchall()
    if res:
        pass
    else:
        yesterday_res = cur.execute(
            f"""
            SELECT * from stat WHERE date = '{yesterday(tz="Europe/Moscow").__format__("YYYY-MM-DD")}'
            """
        ).fetchall()[0]
        res = cur.execute(
            f"""
            INSERT INTO stat (date, users, requests, gratitudes)

            VALUES (?, ?, ?, ?)
            """,
            (now(tz="Europe/Moscow").__format__("YYYY-MM-DD"), yesterday_res[2], yesterday_res[1],
             yesterday_res[3])).fetchall()
        print('Создана новая графа!')
        base.commit()


def get_state(base, id):
    cur = base.cursor()
    res = cur.execute(
        f"""
        SELECT state FROM users
        WHERE id = {id}
        """
    ).fetchall()
    return res[0][0]


def set_state(base, id, state):
    cur = base.cursor()
    res = cur.execute(
        f"""
        UPDATE users
        SET state = {state}
        WHERE id = {id}
        """
    ).fetchall()
    base.commit()
    return res


def get_notifications(base, id):
    cur = base.cursor()
    res = cur.execute(
        f"""
        SELECT notifications FROM users
        WHERE id = {id}
        """
    ).fetchall()
    return res[0][0]


def set_notifications(base, id, notif):
    cur = base.cursor()
    res = cur.execute(
        f"""
        UPDATE users
        SET notifications = {notif}
        WHERE id = {id}
        """
    ).fetchall()
    base.commit()
    return res


def new_user(base, id, name, last):
    cur = base.cursor()
    res = cur.execute(
        f"""
        INSERT INTO users (id, name, last)
        
        VALUES (?, ?, ?)
        """,
        (id, name, last)).fetchall()
    res = cur.execute(
        f"""
        UPDATE stat
        SET users = users + 1
        WHERE date = '{now(tz="Europe/Moscow").__format__("YYYY-MM-DD")}'
        """,
        ).fetchall()
    base.commit()


def set_class_num(base, id, num):
    cur = base.cursor()
    res = cur.execute(
        f"""
            UPDATE users
            SET cls_num = {num}
            WHERE id = {id}
            """
    ).fetchall()
    base.commit()


def set_class_lit(base, id, lit):
    cur = base.cursor()
    c_num = cur.execute(
        f"""
            SELECT cls_num FROM users
            WHERE id = {id}
            """
    ).fetchall()[0][0]
    res = cur.execute(
        f"""
            UPDATE users
            SET cls_lit = '{lit}', cls = '{c_num}{lit}'
            WHERE id = {id}
            """
    ).fetchall()
    base.commit()


def get_cls(base, id):
    cur = base.cursor()
    c_num = cur.execute(
        f"""
        SELECT cls FROM users
        WHERE id = {id}
        """
    ).fetchall()[0][0]
    return c_num


def increase_requests(base, id):
    cur = base.cursor()
    res = cur.execute(
        f"""
        UPDATE stat
        SET requests = requests + 1
        WHERE date = '{now(tz="Europe/Moscow").__format__("YYYY-MM-DD")}'
        """
    ).fetchall()
    res = cur.execute(
        f"""
        UPDATE users
        SET requests = requests + 1
        WHERE id = {id}
        """
    ).fetchall()
    base.commit()


def increase_gratitude(base, id):
    cur = base.cursor()
    res = cur.execute(
        f"""
        UPDATE stat
        SET gratitudes = gratitudes + 1
        WHERE date = '{now(tz="Europe/Moscow").__format__("YYYY-MM-DD")}'
        """
    ).fetchall()
    res = cur.execute(
        f"""
        UPDATE users
        SET gratitudes = gratitudes + 1
        WHERE id = {id}
        """
    ).fetchall()
    base.commit()


def increase_users(base):
    cur = base.cursor()
    res = cur.execute(
        f"""
        UPDATE stat
        SET users = users + 1
        WHERE date = '{now(tz="Europe/Moscow").__format__("YYYY-MM-DD")}'
        """
    ).fetchall()
    base.commit()


def decrease_users(base):
    cur = base.cursor()
    res = cur.execute(
        f"""
        UPDATE stat
        SET users = users - 1
        WHERE date = '{now(tz="Europe/Moscow").__format__("YYYY-MM-DD")}'
        """
    ).fetchall()
    base.commit()