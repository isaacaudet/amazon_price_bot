from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlite3
import time
import html5lib
import json
import os


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "database.sqlite3")

proxies = {
    "http": "http://134.119.205.253:8080",
    "https": "http://134.119.205.253:8080",
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


def create_task(con, task):
    sql = """ INSERT INTO monitors(id, data)
              VALUES(?,?)"""
    cur = con.cursor()
    cur.execute(sql, task)
    con.commit()
    return cur


def insert_row(con, data):
    sql_in = """INSERT INTO monitors (id, data) 
            VALUES (?, ?);"""
    sql_se = """SELECT * FROM monitors WHERE id= ?"""
    cur = con.cursor()
    cur.execute(sql_se, [data[0]])
    entry = cur.fetchone()

    if not entry:
        cur.execute(sql_in, [data[0], data[1]])
        con.commit()
    else:
        # entry = entry[data[0]]
        print('In db. Comparing price.')
        compare_price(entry, json.loads(data[1]))
    return cur


def compare_price(db, scraped):
    db = json.loads(db[1])
    # print(scraped)
    # print(type(scraped))
    # print('--------------------------')

    # print(scraped)

    db_price = float(db['price'].replace('CDN$', ''))
    scraped_price = float(scraped['price'].replace('CDN$', ''))

    if db_price > scraped_price:
        print('PRICE DROP: ' + db['price'] + '-->' + scraped['price'])
    elif db_price > scraped_price:
        print('PRICE RAISE: ' + scraped['price'] + '-->' + db['price'])
    else:
        print('No price change.')

def get_page_data(page_num, queue):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip",
        "DNT": "1",  # Do Not Track Request Header
        "Connection": "close",
    }

    base_url = r"https://www.amazon.ca/s?k=monitor&page=" + str(page_num)
    response = requests.get(base_url, headers=headers)
    content = response.content
    soup = BeautifulSoup(content, "html5lib")

    for d in soup.findAll(
        "div",
        attrs={
            "class": "sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 s-result-item s-asin sg-col-4-of-28 sg-col-4-of-16 sg-col sg-col-4-of-20 sg-col-4-of-32"
        },
    ):
        name = d.find(
            "span", attrs={"class": "a-size-base-plus a-color-base a-text-normal"}
        )
        price = d.find("span", attrs={"class": "a-offscreen"})
        rating = d.find("span", attrs={"class": "a-icon-alt"})
        url = d.find("a", href=True)
        asin = d["data-asin"]
        all = {}

        if name is not None:
            all["name"] = name.text
        else:
            all["name"] = None

        if price is not None:
            all["price"] = price.text.replace(u"\xa0", u"")
        else:
            all["price"] = "CDN$0"

        if rating is not None:
            all["rating"] = rating.text.replace(" out of 5 stars", "/5")
        else:
            all["rating"] = "-1"

        if url.text is not None:
            all["url"] = base_url + url["href"]
        else:
            all["url"] = "-1"

        if asin is not None:
            all["id"] = asin
        else:
            all["id"] = "-1"
        queue.append(all)
    return queue


if __name__ == "__main__":
    cmd = input("COMMANDS: [ADD, UPDATE]-> ")

    if cmd == "ADD" or cmd == "add" or cmd == "a":
        queue = []
        total_prods = 0
        start_time = time.time()

        for i in range(1, 3):
            get_page_data(i, queue)
            total_prods += len(queue)

        con = db_connect()
        if len(queue):
            for i, lst in enumerate(queue):
                cur = create_task(con, [lst["id"], json.dumps(lst)])
            print("List " + str(i) + " has " + str(len(lst)) + " entries.")
            end_time = time.time()
            try:
                print("DB LENGTH: " + str(cur.lastrowid))
            except NameError:
                print('NameError: EMPTY LISTS')
                pass
            print("TOTAL PRODUCTS: " + str(total_prods))
            print("RUNNING TIME: " + str(end_time - start_time))

    if cmd == "UPDATE" or cmd == "update" or cmd == "u":
        sql_id = """SELECT MAX(id) FROM monitors"""
        start_time = time.time()
        queue = []
        total_prods = 0

        for i in range(2, 4):
            get_page_data(i, queue)
            total_prods += len(queue)

        con = db_connect()
        if len(queue):
            for i, lst in enumerate(queue):
                cur = insert_row(con, [lst["id"], json.dumps(lst)])
            print("List " + str(i) + " has " + str(len(lst)) + " entries.")

            end_time = time.time()
            if not cur.lastrowid or cur.lastrowid == 0:
                cur.execute(sql_id)
                con.commit()
            print("DB LENGTH: " + str(cur.lastrowid))
            print("TOTAL PRODUCTS SCRAPED: " + str(total_prods))
            print("RUNNING TIME: " + str(end_time - start_time))
        else:
            print('API MALFUNCTION')
    # qcount = 0 # the count in queue used to track the elements in queue
    # products=[] # List to store name of the product
    # prices=[] # List to store price of the product
    # ratings=[] # List to store ratings of the product
    # no_pages = 9 # no of pages to scrape in the website (provide it via arguments)
