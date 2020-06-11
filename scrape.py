from bs4 import BeautifulSoup
import requests
from datetime import date
from progress.bar import Bar
from requests_html import HTMLSession

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


class Scrape:

    def __init__(self, url):
        response = requests.get(url, headers=headers)
        content = response.content
        self.soup = BeautifulSoup(content, 'lxml')
        self.url = url

    def amazon(self):
        soup = self.soup

        name = soup.find(id='productTitle')
        price = soup.find(id='newBuyBoxPrice')
        rating = soup.find(id='acrPopover')
        asin = soup.find('td', string='ASIN').next_sibling
        date = today.strftime("%d/%m/%Y")
        all = {}

        if name is not None:
            all['name'] = name.text.strip()
        else:
            all['name'] = None

        if price is not None:
            all['price'] = {date: price.text.replace(u'\xa0', u'')}
        else:
            all['price'] = {date: 'CDN$0'}

        if rating is not None:
            all['rating'] = rating.text.strip().replace(
                ' out of 5 stars', '/5')
        else:
            all['rating'] = '-1'

        if asin is not None:
            all['id'] = asin.text
        else:
            all['id'] = '-1'
        return all

    def bestbuy(self):
        soup = self.soup

        name = soup.find('h1', attrs={'class': 'productName_19xJx'})
        price = soup.find(
            'span', attrs={'class': 'screenReaderOnly_3anTj large_3aP7Z'})
        rating = soup.find('label', attrs={'class': 'ratings_I_BnL'})
        asin = soup.find('span', attrs={'itemprop': 'model'})
        date = today.strftime("%d/%m/%Y")
        all = {}

        if name is not None:
            all['name'] = name.text.strip()
        else:
            all['name'] = None

        if price is not None:
            all['price'] = {date: price.text}
        else:
            all['price'] = {date: 'CDN$0'}

        if rating is not None:
            all['rating'] = rating.text.strip().replace(
                ' out of 5 stars', '/5')
        else:
            all['rating'] = '-1'

        if asin is not None:
            all['id'] = asin.text
        else:
            all['id'] = '-1'
        return all

    def newegg(self):
        # requests-html needed to parse JavaScript (price)
        session = HTMLSession()
        r = session.get(self.url)
        r.html.render()

        soup = self.soup

        name = soup.find('span', {'style': 'display: inline;'})
        price = r.html.find('li.price-current', first=True).text.strip()
        rating = soup.find('span', attrs={'class': 'print'})
        asin = soup.find('dt', string='Model').next_sibling
        date = today.strftime("%d/%m/%Y")
        all = {}

        if name is not None:
            all['name'] = name.text.strip()
        else:
            all['name'] = None

        if price is not None:
            all['price'] = {date: price.replace(
                u'\xa0', u'').replace(' –', '')}
        else:
            all['price'] = {date: 'CDN$0'}

        if rating is not None:
            all['rating'] = rating.text.strip().replace(
                ' out of 5 stars', '/5')
        else:
            all['rating'] = '-1'

        if asin is not None:
            all['id'] = asin.text
        else:
            all['id'] = '-1'
        return all

    def thesource(self):
        soup = self.soup

        name = soup.find('h1', {'class': 'pdp-name'}).find('span')
        price = soup.find('div', {'class': 'pdp-sale-price'})
        asin = soup.find('span', {'class': 'identifier'})
        date = today.strftime("%d/%m/%Y")
        all = {}

        if name is not None:
            all['name'] = name.text.strip()
        else:
            all['name'] = None

        if price is not None:
            all['price'] = {date: price.text.strip().replace(
                u'\xa0', u'')}
        else:
            all['price'] = {date: 'CDN$0'}

        # potentially add rating scraping
        all['rating'] = '-1'

        if asin is not None:
            all['id'] = asin.text
        else:
            all['id'] = '-1'

        return all

    def canadacomputers(self):
        soup = self.soup

        name = soup.find(
            'h1', {'class': 'h3 product-title mb-2'}).find('strong')
        price = soup.find('span', {'class': 'h2-big'}).find('strong')
        asin = soup.find('p', {'class': 'm-0 text-small'})
        date = today.strftime("%d/%m/%Y")
        all = {}

        if name is not None:
            all['name'] = name.text.strip()
        else:
            all['name'] = None

        if price is not None:
            all['price'] = {date: price.text.strip().replace(
                u'\xa0', u'')}
        else:
            all['price'] = {date: 'CDN$0'}

        if asin is not None:
            all['id'] = asin.text.replace('Item Code:  ', '')
        else:
            all['id'] = '-1'

        return all

    def memoryexpress(self):
        soup = self.soup

        name = soup.find(
            'header', {'class': 'c-capr-header'}).find('h1')
        price = soup.find(
            'div', {'class': 'GrandTotal c-capr-pricing__grand-total'}).find('div')
        asin = soup.find(
            'article', {'class': 'l-capr-page'})['data-product-id']
        date = today.strftime("%d/%m/%Y")
        all = {}

        if name is not None:
            all['name'] = name.text.strip()
        else:
            all['name'] = None

        if price is not None:
            all['price'] = {date: price.text.strip().replace(
                'Only', '')}
        else:
            all['price'] = {date: 'CDN$0'}

        if asin is not None:
            all['id'] = asin
        else:
            all['id'] = '-1'

        return all

    def mikescomputershop(self):
        soup = self.soup

        name = soup.find('div', {'class': 'gd-1 Title'})
        price = soup.find('div', {'class': 'Price Special'})
        if price is None:
            price = soup.find('div', {'class': 'retail'})

        asin = soup.find(
            'dt', string='Product Model').next_element.next_element.next_element
        date = today.strftime("%d/%m/%Y")
        all = {}

        if name is not None:
            all['name'] = name.text.strip()
        else:
            all['name'] = None

        if price is not None:
            all['price'] = {date: price.text}
        else:
            all['price'] = {date: 'CDN$0'}

        if asin is not None:
            all['id'] = asin.text.strip()
        else:
            all['id'] = '-1'

        return all


if __name__ == '__main__':
    scraper = Scrape()
