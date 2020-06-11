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
from progress.bar import Bar
from db import Database

# IDEA: a script that runs daily and compares the price of selected products at various vendors. To do so I would need a database to track the prices.
# The issue with my first one was I didn't have the JSON plugin to get meaningful metrics in SQL. I'll use a lot of what I established previously.

# INPUT: Either product name or serial code. Depends how easy it is to find on different vendors. If I have to go with product name, I could have it verify that you're adding the right product.
# OUTPUT: Script should be timed so as to notify me if prices lower.

database = Database()
while True:
    action = input('Enter a command [INSERT, UPDATE]:')
    if action.lower() in ('i', 'insert'):
        item = input('Serial Number or Name? [S, N]')
        if item.lower() == 's':
            # serial number lookup function
        elif item.lower() == 'n':
            # name lookup function
