from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlite3
import time
import html5lib
import json
import os
from notify_run import Notify
from datetime import date


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')
today = date.today()

proxies = {
    'http': 'http://134.119.205.253:8080',
    'https': 'http://134.119.205.253:8080',
}


def db_connect(db_path=DEFAULT_PATH):
    """Returns database connection.

    Keyword Arguments:
        db_path {string} -- Path to database. (default: {DEFAULT_PATH})

    Returns:
        [Connection] -- Connection to database.
    """
    con = sqlite3.connect(db_path)
    return con


def create_task(con, task, ignore_count):
    sql = """ INSERT INTO monitors(id, data)
              VALUES(?,?);"""
    sql_se = """SELECT * FROM monitors WHERE id=?;"""
    cur = con.cursor()
    cur.execute(sql_se, [task[0]])
    entry = cur.fetchone()
    if not entry:
        cur.execute(sql, task)
    else:
        ignore_count += 1
    con.commit()
    return cur, ignore_count


def insert_row(con, data):
    sql_in = """INSERT INTO monitors (id, data)
            VALUES (?, ?);"""
    sql_se = """SELECT * FROM monitors WHERE id=?;"""
    sql_prices = """INSERT INTO prices (id, data)
                    VALUES (?, ?);"""
    sql_prices_se = """SELECT * FROM prices WHERE id=?;"""
    sql_prices_update = """UPDATE prices SET data=? WHERE id=?;"""
    sql_prod_update = """UPDATE monitors SET data=? WHERE id=?;"""
    prices = {}
    cur = con.cursor()
    cur.execute(sql_se, [data[0]])
    entry = cur.fetchone()

    if not entry:
        cur.execute(sql_in, [data[0], data[1]])
    else:
        db, scraped = compare_price(entry, json.loads(data[1]))
        if db + scraped != 0:

            # update price in table before checking prices.
            cur.execute(sql_prod_update, [data[1], data[0]])
            cur.execute(sql_prices_se, [data[0]])
            entry_prices = cur.fetchone()
            date = today.strftime("%d/%m/%Y")

            # check if ID is in prices tables
            if entry_prices:
                prices = json.loads(entry_prices[1])
                prices[date] = scraped
                cur.execute(sql_prices_update, [json.dumps(prices), data[0]])
                print('Price Appended.')
            else:
                db = json.loads(entry[1])
                db_price = list(db['price'].items())[0]
                prices[db_price[0]] = db_price[1]
                prices[date] = scraped
                cur.execute(sql_prices, [data[0], json.dumps(prices)])
    con.commit()
    return cur


def compare_price(db, scraped):
    db = json.loads(db[1])
    db_price = float(list(db['price'].values())[
                     0].replace('CDN$', '').replace(',', ''))
    scraped_price = float(list(scraped['price'].values())[0].replace(
        'CDN$', '').replace(',', ''))

    if db_price > scraped_price:
        print('PRICE DROP: ' + str(db_price) + ' --> ' + str(scraped_price))
        if (db_price - scraped_price) > 1:
            notify = Notify()
            notify.send(db['name'] + ' PRICE DROP: ' +
                        str(db_price) + ' --> ' + str(scraped_price))
        return db_price, scraped_price
    elif db_price > scraped_price:
        print('PRICE RAISE: ' + str(db_price) + ' --> ' + str(scraped_price))
        return db_price, scraped_price
    else:
        return 0, 0


def get_page_data(page_num, queue):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip',
        'DNT': '1',
        'Connection': 'close',
    }

    base_url = r'https://www.amazon.ca/s?k=monitor&page=' + str(page_num)
    response = requests.get(base_url, headers=headers)
    content = response.content
    soup = BeautifulSoup(content, 'html5lib')

    for d in soup.findAll(
        'div',
        attrs={
            'class': 'sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 s-result-item s-asin sg-col-4-of-28 sg-col-4-of-16 sg-col sg-col-4-of-20 sg-col-4-of-32'
        },
    ):
        name = d.find(
            'span', attrs={'class': 'a-size-base-plus a-color-base a-text-normal'}
        )
        price = d.find('span', attrs={'class': 'a-offscreen'})
        rating = d.find('span', attrs={'class': 'a-icon-alt'})
        url = d.find('a', href=True)
        asin = d['data-asin']
        date = today.strftime("%d/%m/%Y")
        all = {}

        if name is not None:
            all['name'] = name.text
        else:
            all['name'] = None

        if price is not None:

            all['price'] = {date: price.text.replace(u'\xa0', u'')}
        else:
            all['price'] = {date: 'CDN$0'}

        if rating is not None:
            all['rating'] = rating.text.replace(' out of 5 stars', '/5')
        else:
            all['rating'] = '-1'

        if url.text is not None:
            all['url'] = base_url + url['href']
        else:
            all['url'] = '-1'

        if asin is not None:
            all['id'] = asin
        else:
            all['id'] = '-1'
        queue.append(all)
    return queue


if __name__ == '__main__':
    cmd = input('COMMANDS: [ADD, UPDATE] -> ')
    sql_id = """SELECT * FROM monitors;"""
    ignore_count = 0
    if cmd == 'ADD' or cmd == 'add' or cmd == 'a':
        queue = []
        total_prods = 0
        start_time = time.time()

        for i in range(1, 4):
            get_page_data(i, queue)
            total_prods += len(queue)

        con = db_connect()
        if len(queue):
            for i, lst in enumerate(queue):
                cur, ignore_count = create_task(
                    con, [lst['id'], json.dumps(lst)], ignore_count)
            print(str(i+1) + ' entries found.')

            end_time = time.time()
            cur.execute(sql_id)
            db_length = len(cur.fetchall())
            running_time = float(end_time - start_time)
            print('DB LENGTH: ' + str(db_length))
            print('TOTAL PRODUCTS: ' + str(total_prods))
            print('RUNNING TIME: ' + f'{running_time:.2f}')
            if ignore_count > 0:
                print(str(ignore_count) + ' entries ignored.')
        else:
            print('API MALFUNCTION')

    elif cmd == 'UPDATE' or cmd == 'update' or cmd == 'u':
        sql_id = """SELECT * FROM monitors;"""
        start_time = time.time()
        queue = []
        total_prods = 0

        for i in range(1, 4):
            get_page_data(i, queue)
            total_prods += len(queue)

        con = db_connect()
        if len(queue):
            for i, lst in enumerate(queue):
                cur = insert_row(con, [lst['id'], json.dumps(lst)])
            print(str(i+1) + ' entries found.')

            end_time = time.time()
            cur.execute(sql_id)
            db_length = len(cur.fetchall())
            running_time = float(end_time - start_time)
            print('DB LENGTH: ' + str(db_length))
            print('TOTAL PRODUCTS SCRAPED: ' + str(total_prods))
            print('RUNNING TIME: ' + f'{running_time:.2f}')
            con.commit()

        else:
            print('API MALFUNCTION')
