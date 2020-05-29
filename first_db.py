from bs4 import BeautifulSoup
import requests
import sqlite3
import os
import json

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')


def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con


def create_task(con, task):
    sql = ''' INSERT INTO products(name,count,rating,vendor)
              VALUES(?,?,?,?) '''
    c = con.cursor()
    c.execute(sql, task)
    con.commit()
    return c


def insert_row(con, data):
    sql_in = """INSERT INTO monitors (id, data)
            VALUES (?, ?);"""
    sql_se = """SELECT * FROM monitors WHERE id=?"""
    sql_prices = """INSERT INTO prices (id, data)
                    VALUES (?, ?);"""
    sql_prices_se = """SELECT * FROM prices WHERE id=?"""
    sql_prices_update = """UPDATE prices SET data=? WHERE id=?"""
    sql_prod_update = """UPDATE monitors SET data=? WHERE id=?"""
    prices = {}
    cur = con.cursor()
    cur.execute(sql_se, [data[0]])
    entry = cur.fetchone()

    if not entry:
        cur.execute(sql_in, [data[0], data[1]])
        con.commit()
    else:
        db, scraped = compare_price(entry, json.loads(data[1]))
        if db + scraped != 0:
            # update price in table before checking prices.
            cur.execute(sql_prod_update, [data[1], data[0]])
            con.commit()
            # check if ID is in prices tables
            cur.execute(sql_prices_se, [data[0]])
            entry = cur.fetchone()

            if entry:
                prices = json.loads(entry[1])
            date = today.strftime("%d/%m/%Y")
            prices[date] = scraped
            cur.execute(sql_prices_update, [json.dumps(prices), data[0]])
            con.commit()
    return cur


if __name__ == '__main__':
    task_1 = ('AMD RYZEN 9', 10, 5, 'www.amazon.ca')
    con = db_connect()
    cur = con.cursor()

    sql_prices = """INSERT INTO prices (id, data)
                VALUES (?, ?);"""
    cur.execute(sql_prices, ['B07XB68G5N', json.dumps({"28/05/2020": 68.88})])
    con.commit()
