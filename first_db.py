from bs4 import BeautifulSoup
import requests
import sqlite3
import os

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
  
if __name__ == '__main__':
  task_1 = ('AMD RYZEN 9', 10, 5, 'www.amazon.ca')     
  con = db_connect()
  c = create_task(con, task_1)
  print(c.lastrowid)
  con.close()