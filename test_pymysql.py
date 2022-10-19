# -*- coding: utf-8 -*-
# Created By Shing At 2022/10/19
import threading
import time

import pymysql


class SqlEngine:
    def __init__(self):
        # pymysql.connections.DEBUG = True
        self.connection = pymysql.Connection(**{
            'autocommit': True,
            'charset': 'utf8mb4',
            'host': '10.162.138.13',
            'port': 3306,
            'user': 'root',
            'password': 'sany_root',
            'db': 'sany_scada'
        })

    def my_cursor(self):
        try:
            print('start ping')
            self.connection.ping()
            print('ping finished')
            return self.connection.cursor()
        except:
            raise

    def query(self, sql):
        with self.my_cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        print(rows)
        return rows


if __name__ == '__main__':
    sql_engine = SqlEngine()
    print(sql_engine.connection)
    sql = 'select * from mon_turbine_status_history order by id limit 1'
    t1 = threading.Thread(target=sql_engine.query, args=(sql,))
    t2 = threading.Thread(target=sql_engine.query, args=(sql,))
    t1.start()

    time.sleep(1)
    print('\n\n----------------start thread2')
    t2.start()

    t1.join()
    t2.join()
