import sqlite3

import pendulum

from bot.stuff import Utilities
from bot.stuff.Config import Config
from bot.stuff.Utilities import FORMAT, TZ


def GetTodayDate():
    if Config.REDIRECT_DATE:
        return Config.REDIRECT_DATE
    return pendulum.now(TZ).__format__(FORMAT)


class UserBase:
    def __init__(self):
        self.UserBase = sqlite3.connect(Config.PATH + 'data/Users.db')
        self.cur = self.UserBase.cursor()

    def AllUsers(self):
        users = self.cur.execute(f"""
                                 SELECT id FROM users
                                 """).fetchall()
        if users:
            return [uid[0] for uid in users]
        return None

    def DistributeClassUsers(self, users_class):
        class_users = self.cur.execute(
                            f"""
                            SELECT id FROM users
                            WHERE cls = '{users_class}' AND ("7" = 1 OR "13" = 1 OR "17" = 1 OR "20" = 1 OR "23" = 1)
                            """).fetchall()
        if class_users:
            return [i[0] for i in class_users]
        return None

    def DistributeParallelUsers(self, parallel):
        parallel_users = self.cur.execute(f"""
                               SELECT id FROM users
                               WHERE cls_num = '{parallel}'
                               """).fetchall()
        if parallel_users:
            return [i[0] for i in parallel_users]
        return None

    def DistributeSchedule(self, users_class, time):
        res = self.cur.execute(f"""
                              SELECT id FROM users
                              WHERE cls = '{users_class}' AND "{time}" = 1
                              """).fetchall()
        if res:
            return [i[0] for i in res]
        return None

    def CheckUserInBase(self, user_id):
        all_users = self.AllUsers()
        if user_id in all_users:
            return True
        return False

    def GetUserState(self, user_id):
        res = self.cur.execute(f"""
                               SELECT state FROM users
                               WHERE id = {user_id}
                               """).fetchall()
        if res:
            return res[0][0]
        return None

    def GetUserInfo(self, user_id):
        cur = self.UserBase.cursor()
        res = cur.execute(f"""
                          SELECT
                              id, name, last, cls, cls_num, cls_lit,
                              requests, received,
                              msg_send, msg_received,
                              hw_date, hw_add, hw_check,
                              "7", "13", "17", "20", "23"
                          FROM users
                          WHERE id = {user_id}
                          """).fetchall()
        if res:
            return dict(zip(('id', 'name', 'last', 'cls', 'cls_num', 'cls_lit',
                             'requests', 'received',
                             'msg_send', 'msg_received',
                             'hw_date', 'hw_add', 'hw_check',
                             '7', '13', '17', '20', '23'),
                            res[0]))
        return None

    def GetUserInfoByName(self, name, last):
        res = self.cur.execute(f"""
                          SELECT
                              id, name, last, cls, cls_num, cls_lit,
                              requests, received,
                              msg_send, msg_received,
                              hw_date, hw_add, hw_check,
                              "7", "13", "17", "20", "23"
                          FROM users
                          WHERE name = '{name}' AND last = '{last}'
                          """).fetchall()
        if res:
            return dict(zip(('id', 'name', 'last', 'cls', 'cls_num', 'cls_lit',
                             'requests', 'received',
                             'msg_send', 'msg_received',
                             'hw_date', 'hw_add', 'hw_check',
                             '7', '13', '17', '20', '23'),
                            res[0]))
        return None

    def IncreaseParameters(self, user_id, requests=False, received=False, messages_send=False, messages_received=False, hw_check=False, hw_add=False):
        cur = self.cur
        if requests:
            cur.execute(f"""
                        UPDATE users
                        SET requests = requests + 1
                        WHERE id = {user_id}
                        """)
        if received:
            cur.execute(f"""
                        UPDATE users
                        SET received = received + 1
                        WHERE id = {user_id}
                        """)
        if messages_send:
            cur.execute(f"""
                        UPDATE users
                        SET msg_send = msg_send + 1
                        WHERE id = {user_id}
                        """)
        if messages_received:
            cur.execute(f"""
                        UPDATE users
                        SET msg_received = msg_received + 1
                        WHERE id = {user_id}
                        """)
        if hw_check:
            cur.execute(f"""
                        UPDATE users
                        SET hw_check = hw_check + 1
                        WHERE id = {user_id}
                        """)
        if hw_add:
            cur.execute(f"""
                        UPDATE users
                        SET hw_add = hw_add + 1
                        WHERE id = {user_id}
                        """)
        self.UserBase.commit()

    def AddNewUser(self, user_id, user_name, user_last):
        self.cur.execute(f"""
                         INSERT INTO users (id, name, last)
                         VALUES (?, ?, ?)
                         """, (user_id, user_name, user_last))
        self.UserBase.commit()

    def DeleteUser(self, user_id):
        self.cur.execute(f"""
                         DELETE FROM users
                         WHERE id = {user_id}
                         """)
        self.UserBase.commit()

    def SetUserParameters(self, user_id, state=None, cls_lit=None, cls_num=None, hw_date=None, n_7=None, n_13=None, n_17=None, n_20=None, n_23=None):
        if state or state == 0:
            self.cur.execute(f"""
                              UPDATE users
                              SET state = {state}
                              WHERE id = {user_id}
                              """)
        if cls_num:
            self.cur.execute(f"""
                             UPDATE users
                             SET cls_num = {cls_num}
                             WHERE id = {user_id}
                             """)
        if cls_lit:
            cls_num = self.cur.execute(f"""
                                       SELECT cls_num FROM users
                                       WHERE id = {user_id}
                                       """).fetchall()[0][0]
            self.cur.execute(f"""
                             UPDATE users
                             SET cls_lit = '{cls_lit}', cls = '{cls_num}{cls_lit}'
                             WHERE id = {user_id}
                             """)
        if hw_date:
            self.cur.execute(f"""
                             UPDATE users
                             SET hw_date = '{hw_date}'
                             WHERE id = {user_id}
                             """)
        if n_7 or n_7 == 0:
            self.cur.execute(f"""
                             UPDATE users
                             SET "7" = {n_7}
                             WHERE id = {user_id}
                             """)
        if n_13 or n_13 == 0:
            self.cur.execute(f"""
                             UPDATE users
                             SET "13" = {n_13}
                             WHERE id = {user_id}
                             """)
        if n_17 or n_17 == 0:
            self.cur.execute(f"""
                             UPDATE users
                             SET "17" = {n_17}
                             WHERE id = {user_id}
                             """)
        if n_20 or n_20 == 0:
            self.cur.execute(f"""
                             UPDATE users
                             SET "20" = {n_20}
                             WHERE id = {user_id}
                             """)
        if n_23 or n_23 == 0:
            self.cur.execute(f"""
                             UPDATE users
                             SET "23" = {n_23}
                             WHERE id = {user_id}
                             """)
        self.UserBase.commit()


class ConsoleBase:
    def __init__(self):
        self.ConsoleBase = sqlite3.connect(Config.PATH + 'data/Console.db')

    def GetState(self):
        cur = self.ConsoleBase.cursor()
        res = cur.execute(f"""
                    SELECT state
                    FROM console
                    """).fetchall()
        if res:
            if res[0]:
                return res[0][0]
        return None

    def ChangeState(self, state):
        cur = self.ConsoleBase.cursor()
        res = cur.execute(f"""
                          UPDATE console
                          SET state = {state}
                          """).fetchall()
        self.ConsoleBase.commit()


class StatisticsBase:
    def __init__(self):
        self.UserBase = sqlite3.connect(Config.PATH + 'data/Users.db')

    def GetMainStatistics(self):
        cur = self.UserBase.cursor()
        res = cur.execute(f"""
                          SELECT
                          COUNT(*) as total_users,
                          SUM(requests) as requests,
                          SUM(received) as schedule_received,
                          SUM(msg_send) as msg_send,
                          SUM(msg_received) as msg_received,
                          SUM(msg_send) + SUM(msg_received) as total_msg
                          FROM users
                          """).fetchall()
        res2 = cur.execute(f"""SELECT COUNT(*) as total_notifications FROM users WHERE "7" = 1 OR "13" = 1 OR "17" = 1 OR "20" = 1 OR "23" = 1""").fetchall()[0]
        res = list(res[0])
        res.append(res2[0])
        return dict(zip(('total_users', 'requests', 'schedule_received', 'msg_send', 'msg_received', 'total_msg', 'total_notifications'), res))


class ScheduleBase:
    def __init__(self):
        self.SchedulesBase = sqlite3.connect(Config.PATH + 'data/Schedules.db')

    def MainUpdate(self, schedule_date, now):
        self.NewUpdateDay(schedule_date)
        cur = self.SchedulesBase.cursor()
        cur.execute(f"""
                    UPDATE updates
                    SET main_update = {now.timestamp()}
                    WHERE date = '{schedule_date}'
                    """).fetchall()
        self.SchedulesBase.commit()

    def ClassesUpdate(self, schedule_date, now):
        self.NewUpdateDay(schedule_date)
        cur = self.SchedulesBase.cursor()
        cur.execute(f"""
                    UPDATE updates
                    SET classes_update = {now.timestamp()}
                    WHERE date = '{schedule_date}'
                    """).fetchall()
        self.SchedulesBase.commit()

    def NewUpdateDay(self, schedule_date):
        cur = self.SchedulesBase.cursor()
        res = cur.execute(f"""
                          SELECT * FROM updates
                          WHERE date = '{schedule_date}'
                          """).fetchall()
        if res:
            return True
        cur.execute(f"""
                    INSERT INTO updates (date, main_update, classes_update)
                    VALUES (?, ?, ?)
                    """, (schedule_date, pendulum.now(tz=Utilities.TZ).timestamp(), pendulum.now(tz=Utilities.TZ).timestamp()))
        self.SchedulesBase.commit()
        return True

    def DeltaUpdateMain(self, schedule_date, now):
        cur = self.SchedulesBase.cursor()
        res = cur.execute(f"""
                          SELECT main_update FROM updates
                          WHERE date = '{schedule_date}'
                          """).fetchall()[0][0]
        return pendulum.from_timestamp(res, tz=Utilities.TZ).diff(now).in_minutes()

    def DeltaUpdateClasses(self, schedule_date, now):
        cur = self.SchedulesBase.cursor()
        res = cur.execute(f"""
                          SELECT classes_update FROM updates
                          WHERE date = '{schedule_date}'
                          """).fetchall()[0][0]
        return pendulum.from_timestamp(res, tz=Utilities.TZ).diff(now).in_minutes()

    def UploadedClass(self, schedule_date, cls, link):
        cur = self.SchedulesBase.cursor()
        res = cur.execute(f"""
                          UPDATE '{schedule_date}'
                          SET link = '{link}'
                          WHERE class = '{cls}'
                          """).fetchall()
        self.SchedulesBase.commit()

    def GetAttachment(self, schedule_date, cls):
        cur = self.SchedulesBase.cursor()
        try:
            res = cur.execute(f"""
                              SELECT link
                              FROM '{schedule_date}'
                              WHERE class = '{cls}'
                              """).fetchall()
        except sqlite3.OperationalError:
            self.NewSchedule(schedule_date)
            return None
        if res:
            return res[0][0]

    def NewSchedule(self, schedule_date):
        cur = self.SchedulesBase.cursor()
        cur.execute(f"""
                     CREATE TABLE IF NOT EXISTS '{schedule_date}'(
                        class string,
                        link string
                     );
                     """).fetchall()
        self.SchedulesBase.commit()
        res = cur.execute(f"""SELECT * FROM '{schedule_date}'""").fetchall()
        if not res:
            for i in Utilities.CLASSES:
                cur.execute(f"""
                            INSERT INTO '{schedule_date}' (class, link)
                            VALUES (?, ?)
                            """, (i, ''))
            cur.execute(f"""
                        INSERT INTO '{schedule_date}' (class, link)
                        VALUES ('main', '')
                        """)

        res = cur.execute(f"""SELECT * FROM settings WHERE date = '{schedule_date}'""")
        if not res:
            cur.execute(f"""
                        INSERT INTO settings (date, main_replace)
                        VALUES (?, ?)
                        """, (schedule_date, 0))
        self.SchedulesBase.commit()

    def DeleteSchedule(self, schedule_date):
        cur = self.SchedulesBase.cursor()
        cur.execute(f"""DROP TABLE IF EXISTS '{schedule_date}'""")
        self.SchedulesBase.commit()

    def UpdateSchedule(self, schedule_date):
        cur = self.SchedulesBase.cursor()
        try:
            res = cur.execute(f"""SELECT * FROM '{schedule_date}'""").fetchall()
            if res:
                cur.execute(f"""DROP TABLE IF EXISTS '{schedule_date}'""")
                self.NewSchedule(schedule_date)
        except sqlite3.OperationalError:
            self.NewSchedule(schedule_date)
        self.SchedulesBase.commit()

    def Replace(self, schedule_date):
        cur = self.SchedulesBase.cursor()
        cur.execute(f"""
                    UPDATE settings
                    SET main_replace = 1
                    WHERE date = '{schedule_date}'
                    """)
        self.SchedulesBase.commit()

    def UnReplace(self, schedule_date):
        cur = self.SchedulesBase.cursor()
        cur.execute(f"""
                    UPDATE settings
                    SET main_replace = 0
                    WHERE date = '{schedule_date}'
                    """)
        self.SchedulesBase.commit()

    def GetReplace(self, schedule_date):
        cur = self.SchedulesBase.cursor()
        res = cur.execute(f"""
                          SELECT main_replace
                          FROM settings
                          WHERE date = '{schedule_date}'
                          """).fetchall()
        if res:
            main_replace = res[0][0]
            return True if main_replace else False
        return False


class SettingsBase:
    def __init__(self):
        self.SettingsBase = sqlite3.connect(Config.PATH + 'data/Settings.db')

    def GetSettings(self, date=GetTodayDate()):
        cur = self.SettingsBase.cursor()
        res = cur.execute(f"""
                          SELECT auto_update, main_replace, offline, diary, auto_distribution
                          FROM settings
                          WHERE date = '{date}'
                          """).fetchall()
        if res:
            return dict(zip(['auto_update', 'main_replace', 'offline', 'diary', 'auto_distribution'], list(res[0])))
        self.NewDay()
        return self.GetSettings()

    def NewDay(self, date=GetTodayDate()):
        cur = self.SettingsBase.cursor()
        dates = cur.execute(f"""SELECT date FROM settings""").fetchall()[0]
        if date not in dates:
            res = cur.execute(f"""
                              INSERT INTO settings (date, auto_update, main_replace, offline, diary, auto_distribution)
                              VALUES(?, ?, ?, ?, ?, ?)
                              """,
                              (date, 1, 0, 0, 0, 1))
            self.SettingsBase.commit()

    def ChangeSettings(self, date=GetTodayDate(), parameters=None):
        if parameters is None:
            parameters = {}
        cur = self.SettingsBase.cursor()
        res = cur.execute(f"""
                          UPDATE settings
                          SET auto_update = {parameters.get('auto_update', self.GetSettings(date)['auto_update'])},
                          main_replace = {parameters.get('main_replace', self.GetSettings(date)['main_replace'])},
                          offline = {parameters.get('offline', self.GetSettings(date)['offline'])},
                          diary = {parameters.get('diary', self.GetSettings(date)['diary'])},
                          auto_distribution = {parameters.get('auto_distribution', self.GetSettings(date)['auto_distribution'])}
                          WHERE date = '{date}'
                          """)
        self.SettingsBase.commit()


class ParseBase:
    def __init__(self):
        self.ParseBase = sqlite3.connect(Config.PATH + 'data/Parse.db')

    def GetParseSchedules(self):
        cur = self.ParseBase.cursor()
        res = cur.execute(f"""SELECT * FROM parse""").fetchall()
        if res:
            return [_[0] for _ in res]
        return None

    def AddToParse(self, to_parse):
        cur = self.ParseBase.cursor()
        cur.execute(f"""INSERT INTO parse (to_parse) VALUES ('{to_parse}')""").fetchall()
        self.ParseBase.commit()

    def DeleteFromParse(self, to_parse):
        cur = self.ParseBase.cursor()
        cur.execute(f"""DELETE FROM parse WHERE to_parse = '{to_parse}'""").fetchall()
        self.ParseBase.commit()

    def SetParseTime(self):
        cur = self.ParseBase.cursor()
        cur.execute(f"""
                    UPDATE parse
                    SET time = '{pendulum.now(tz=Utilities.TZ).timestamp()}'
                    """).fetchall()
        self.ParseBase.commit()

    def GetParseTime(self):
        cur = self.ParseBase.cursor()
        res = cur.execute(f"""
                    SELECT time
                    FROM parse
                    """).fetchall()
        if res:
            return res[0][0]
        return None

    def CheckParseTime(self):
        last_parse = pendulum.from_timestamp(float(self.GetParseTime()), tz=Utilities.TZ)
        if last_parse.diff(pendulum.now(tz=Utilities.TZ)).in_minutes() >= Config.PARSE_INTERVAL:
            return True
        return False


class HomeworkBase:
    def __init__(self):
        self.HomeworkBase = sqlite3.connect(Config.PATH + 'data/Homework.db')

    def NewDay(self, date):
        cur = self.HomeworkBase.cursor()
        cur.execute(f"""
                     CREATE TABLE IF NOT EXISTS '{date}'(
                        class string,
                        homework string
                     );
                     """).fetchall()
        self.HomeworkBase.commit()
        res = cur.execute(f"""SELECT * FROM '{date}'""").fetchall()
        if not res:
            for i in Utilities.CLASSES:
                cur.execute(f"""
                            INSERT INTO '{date}' (class, homework)
                            VALUES (?, ?)
                            """, (i, ''))
        self.HomeworkBase.commit()

    def AddHomework(self, date, cls, hw):
        cur = self.HomeworkBase.cursor()
        hw2 = self.GetHomework(date, cls) + '\n' + '•' + hw
        cur.execute(f"""
                    UPDATE '{date}'
                    SET homework = '{hw2}'
                    WHERE class = '{cls}'
                    """)
        self.HomeworkBase.commit()

    def GetHomework(self, date, cls):
        cur = self.HomeworkBase.cursor()
        self.NewDay(date)
        res = cur.execute(f"""
                    SELECT homework
                    FROM '{date}'
                    WHERE class = '{cls}'
                    """).fetchall()
        if res:
            if res[0][0]:
                return res[0][0]
        return '(Пусто)'

    def DeleteHomework(self, date, cls):
        cur = self.HomeworkBase.cursor()
        cur.execute(f"""
                    DELETE FROM '{date}'
                    WHERE class = '{cls}'
                    """)
        self.HomeworkBase.commit()


if __name__ == '__main__':
    print(len(UserBase().DistributeClassUsers('11А')))