from pickle import dump
import sqlite3


def write_base(base, stat):
    pt = 'data/base.pickle'
    with open(pt, 'wb') as fi:
        dump(base, fi)

    pt = 'data/stat.pickle'
    with open(pt, 'wb') as fi:
        dump(stat, fi)


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
            SELECT name, last, cls, id, requests FROM users
            WHERE name = '{name}' AND last = '{last}'
            """
    ).fetchall()
    return res