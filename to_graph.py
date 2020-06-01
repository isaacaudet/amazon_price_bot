import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import os
import json

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')
sql_prices_se = """SELECT * FROM prices WHERE id=?"""


def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con


def historical_price(con, asin):
    cur = con.cursor()
    cur.execute(sql_prices_se, [asin])
    entry = cur.fetchone()

    if entry:
        prices = json.loads(entry[1])
        x, y = zip(*prices.items())
        plt.plot(x, y)
        plt.show()
    else:
        print('Invalid ID')


if __name__ == "__main__":
    con = db_connect()
    asin = input('Enter ID: ')
    historical_price(con, asin)
