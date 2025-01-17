from bs4 import BeautifulSoup
import requests
from datetime import date
from progress.bar import Bar
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import time
# class for scraping various vendors for ID/SN
# Vendor List:  amazon
#               bestbuy
#               newegg
#               thesource
#               canadacomputers
#               memoryexpress
#               mikescomputershop

today = date.today()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip',
    'DNT': '1',
    'Connection': 'close',
}
options = Options()
options.headless = True


class Scrape:

    # def __init__(self, url):
    def get_content(self, url):
        response = requests.get(url, headers=headers)
        content = response.content
        self.soup = BeautifulSoup(content, 'lxml')
        self.url = url

    def sn_lookup(self, url):
        response = requests.get(url, headers=headers)
        content = response.content
        self.soup = BeautifulSoup(content, 'lxml')
        self.url = url

    def amazon(self):
        soup = self.soup
        name = soup.find(id='productTitle')
        price = soup.find(id='newBuyBoxPrice')
        asin = soup.find('td', string='ASIN').next_sibling
        date = today.strftime("%d/%m/%Y")
        all = {}

        if asin is not None:
            all['id'] = asin.text
        else:
            all['id'] = '-1'

        if name is not None:
            all['name'] = name.text.strip()
        else:
            all['name'] = None

        if price is not None:
            all['price'] = {date: price.text.replace(u'\xa0', u'')}
        else:
            all['price'] = {date: 'CDN$0'}

        return all

    def bestbuy(self, sn=None):

        if sn is None:
            self.get_content(self.url)
            soup = self.soup
            name = soup.find('h1', attrs={'class': 'productName_19xJx'})
            price = soup.find(
                'span', attrs={'class': 'screenReaderOnly_3anTj large_3aP7Z'})
            asin = soup.find('span', attrs={'itemprop': 'model'})
            date = today.strftime("%d/%m/%Y")
            all = {}

            if asin is not None:
                all['id'] = asin.text
            else:
                all['id'] = '-1'

            if name is not None:
                all['name'] = name.text.strip()
            else:
                all['name'] = None

            if price is not None:
                all['price'] = {date: price.text}
            else:
                all['price'] = {date: 'CDN$0'}

            return all

        else:
            # use Selenium to parse JavaScript search page and retrieve price of first element
            url = 'https://www.bestbuy.ca/en-ca/search?search=' + sn
            driver = webdriver.Firefox(options=options)
            driver.get(url)

            try:
                price = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[3]/span/div"))).text
                print(price)
            finally:
                driver.quit()

            return price

    def newegg(self, sn=None):
        if sn is None:
            # requests-html needed to parse JavaScript (price)
            session = HTMLSession()
            r = session.get(self.url)
            r.html.render()
            soup = self.soup

            name = soup.find('span', {'style': 'display: inline;'})
            price = r.html.find('li.price-current', first=True).text.strip()
            # rating = soup.find('span', attrs={'class': 'print'})
            asin = soup.find('dt', string='Model').next_sibling
            date = today.strftime("%d/%m/%Y")
            all = {}

            if asin is not None:
                all['id'] = asin.text
            else:
                all['id'] = '-1'

            if name is not None:
                all['name'] = name.text.strip()
            else:
                all['name'] = None

            if price is not None:
                all['price'] = {date: price.replace(
                    u'\xa0', u'').replace(' –', '')}
            else:
                all['price'] = {date: 'CDN$0'}

            return all

        else:
            # scrape search results using HTMLSession
            url = 'https://www.newegg.ca/p/pl?d=' + sn
            session = HTMLSession()
            r = session.get(url)
            r.html.render()

            try:
                price = r.html.find('li.price-current',
                                    first=True).text.strip().replace(' –', '')
                print(price)
            except Exception:
                price = 0

            return price

    def thesource(self, sn=None):
        if sn is None:
            self.get_content(self.url)
            soup = self.soup
            name = soup.find('h1', {'class': 'pdp-name'}).find('span')
            price = soup.find('div', {'class': 'pdp-sale-price'})
            asin = soup.find('span', {'class': 'identifier'})
            date = today.strftime("%d/%m/%Y")
            all = {}

            if asin is not None:
                all['id'] = asin.text
            else:
                all['id'] = '-1'

            if name is not None:
                all['name'] = name.text.strip()
            else:
                all['name'] = None

            if price is not None:
                all['price'] = {date: price.text.strip().replace(
                    u'\xa0', u'')}
            else:
                all['price'] = {date: 'CDN$0'}

            return all

        else:
            url = 'https://www.thesource.ca/en-ca/search?text=' + sn
            session = HTMLSession()
            r = session.get(url)
            r.html.render()

            try:
                price = r.html.find('div.sale-price',
                                    first=True).text
            except Exception:
                print('The Source: Price not found.')
                price = 0

            return price

    def canadacomputers(self, sn=None):
        if sn is None:
            self.get_content(self.get_content)
            soup = self.soup
            name = soup.find(
                'h1', {'class': 'h3 product-title mb-2'}).find('strong')
            price = soup.find('span', {'class': 'h2-big'}).find('strong')
            asin = soup.find('p', {'class': 'm-0 text-small'})
            date = today.strftime("%d/%m/%Y")
            all = {}

            if asin is not None:
                all['id'] = asin.text.replace('Item Code:  ', '')
            else:
                all['id'] = '-1'

            if name is not None:
                all['name'] = name.text.strip()
            else:
                all['name'] = None

            if price is not None:
                all['price'] = {date: price.text.strip().replace(
                    u'\xa0', u'')}
            else:
                all['price'] = {date: 'CDN$0'}

            return all

        else:
            url = 'https://www.canadacomputers.com/search/results_details.php?language=en&keywords=' + sn
            self.get_content(url)
            soup = self.soup

            try:
                price = soup.find(
                    id='product-list').find('div', {'class': 'row mx-0'}).find('strong').text
                print(price)
            except Exception:
                price = 0
                print(price)

            return price

    def memoryexpress(self, sn=None):
        if sn is None:
            self.get_content(self.url)
            soup = self.soup
            name = soup.find(
                'header', {'class': 'c-capr-header'}).find('h1')
            price = soup.find(
                'div', {'class': 'GrandTotal c-capr-pricing__grand-total'}).find('div')
            asin = soup.find(
                'article', {'class': 'l-capr-page'})['data-product-id']
            date = today.strftime("%d/%m/%Y")
            all = {}

            if asin is not None:
                all['id'] = asin
            else:
                all['id'] = '-1'

            if name is not None:
                all['name'] = name.text.strip()
            else:
                all['name'] = None

            if price is not None:
                all['price'] = {date: price.text.strip().replace(
                    'Only', '')}
            else:
                all['price'] = {date: 'CDN$0'}

            return all

        else:
            url = 'https://www.memoryexpress.com/Search/Products?Search=' + sn
            self.get_content(url)
            soup = self.soup

            try:
                price = soup.find(
                    'div', {'class': 'c-shca-icon-item__summary-list'}).find('span').text.strip()
                print(price)
            except Exception:
                price = 0
                print(price)

            return price

    def mikescomputershop(self, sn=None):
        if sn is None:
            self.get_content(self.url)
            soup = self.soup
            name = soup.find('div', {'class': 'gd-1 Title'})
            price = soup.find('div', {'class': 'Price Special'})
            if price is None:
                price = soup.find('div', {'class': 'retail'})
            asin = soup.find(
                'dt', string='Product Model').next_element.next_element.next_element
            date = today.strftime("%d/%m/%Y")
            all = {}

            if asin is not None:
                all['id'] = asin.text.strip()
            else:
                all['id'] = '-1'

            if name is not None:
                all['name'] = name.text.strip()
            else:
                all['name'] = None

            if price is not None:
                all['price'] = {date: price.text}
            else:
                all['price'] = {date: 'CDN$0'}

            return all

        else:
            url = 'https://www.mikescomputershop.com/catalog/?q=' + sn
            driver = webdriver.Firefox(options=options)
            driver.get(url)

            try:
                price = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div/div/ul/li/div"))).text
            finally:
                driver.quit()

            return price


if __name__ == '__main__':
    scraper = Scrape()
