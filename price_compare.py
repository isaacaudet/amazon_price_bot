from db import Database
from scrape import Scrape

# IDEA: a script that runs daily and compares the price of selected products at various vendors. To do so I would need a database to track the prices.
# The issue with my first one was I didn't have the JSON plugin to get meaningful metrics in SQL. I'll use a lot of what I established previously.

# INPUT: Either product name or serial code. Depends how easy it is to find on different vendors. If I have to go with product name, I could have it verify that you're adding the right product.
# OUTPUT: Script should be timed so as to notify me if prices lower.

db = Database()
while True:
    url = input('Enter a product URL: ')
    scrape = Scrape(url)
    data = scrape.bestbuy()
    print(data)
