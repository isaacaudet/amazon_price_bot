from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlite3
import time
import html5lib
import json
import os
proxies = {
  'http': 'http://134.119.205.253:8080',
  'https': 'http://134.119.205.253:8080',
}

def get_page_data(page_num, queue):
    headers = { 
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
'Accept-Language' : 'en-US,en;q=0.5',
'Accept-Encoding' : 'gzip', 
'DNT' : '1', # Do Not Track Request Header 
'Connection' : 'close'
}

    url = r'https://www.amazon.ca/s?k=monitor&page=' + str(page_num)
    response = requests.get(url, headers=headers)
    content = response.content
    soup = BeautifulSoup(content, 'html5lib')

    for d in soup.findAll('div',attrs={'class': 'sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 s-result-item s-asin sg-col-4-of-28 sg-col-4-of-16 sg-col sg-col-4-of-20 sg-col-4-of-32'}):
        name = d.find('span', attrs={'class': 'a-size-base-plus a-color-base a-text-normal'})
        price = d.find('span', attrs={'class': 'a-offscreen'})
        rating = d.find('span', attrs={'class': 'a-icon-alt'})        

        all = []

        if name is not None:
            all.append(name.text)
        else:
            all.append('unknown-product')
        if price is not None:
            all.append(price.text.replace(u'\xa0', u''))
        else:
            all.append('$0')
        if rating is not None:
            all.append(rating.text.replace(' out of 5 stars', '/5'))
        else:
            all.append('-1')
        queue.append(all)
    return queue


if __name__ == '__main__':
    q = []
    startTime = time.time()
    get_page_data(3, q)
    print(q)
    
    # qcount = 0 # the count in queue used to track the elements in queue
    # products=[] # List to store name of the product
    # prices=[] # List to store price of the product
    # ratings=[] # List to store ratings of the product
    # no_pages = 9 # no of pages to scrape in the website (provide it via arguments)
