from bs4 import BeautifulSoup
import sys
import re
from Emailer import Emailer
import time
import random
import datetime
import requests
import logging
from ListingDB import ListingDB

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

class BlueRidge:
    def __init__(self):
        self.goSlow = False
        self.db = ListingDB()

    def setDB(self, DB):
        self.db = DB

    def initSession(self):
        self.session = requests.session()
        headers =   {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding':'gzip,deflate,sdch',
                    'User-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
                    'Connection':'keep-alive'}
        self.session.headers.update(headers)

    def parse(self, listingsHTML):
        self.soup = BeautifulSoup(listingsHTML)
        self.rows = self.soup.findAll('p', class_='row')
        self.prices = self.getPrices()
        self.titles = self.getTitles()

    def getCount(self):
        return len(self.rows)

    def getPrices(self):
        prices = []
        for row in self.rows:
            price_span = row.find('span', class_='price')
            if price_span:
                prices.append(int(price_span.string.replace('$','')))
            else:
                prices.append(-1)
        return prices

    def getTitles(self):
        return [row.find('a', class_='hdrlnk').string for row in self.rows]

    def getListOfPids(self):
        return [row['data-pid'] for row in self.rows]

    def getListingsLessThan(self, maxPrice):
        indices = []
        for index, price in enumerate(self.prices):
            if price is not None and price <=  maxPrice:
                indices.append(index)
        
        listings = [] 
        for index in indices:
            row = self.rows[index]
            pid = row['data-pid']
            if not self.db.has(pid):
                listings.append((pid, self.titles[index], self.prices[index]))
                self.db.insert(pid, None)
        return listings

    def generateLink(self, pid):
        return "http://sfbay.craigslist.org/sfc/fuo/" + pid + ".html"

    def requestPage(self, url):
        try:
            return self.session.get(url).text
        except AttributeError:
            self.initSession()
            return self.session.get(url).text

    def getLinks(self, pids):
        return [self.generateLink(pid) for pid in pids]

    def getAnchorLinksFromPids(self, listings):
        anchorLinks = ""
        for listing in listings:
            if listing[2] == -1:
                price = ''
            else:
                price = '- ${}'.format(listing[2])
            anchorLink = "<a href=\"{}\">{} {}</a><br />".format(self.generateLink(listing[0]).encode('utf-8'), listing[1].encode('utf-8'), price)
            anchorLinks += anchorLink
        return anchorLinks

if __name__ == '__main__':
    rr = BlueRidge()
    rr.goSlow = True
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = 'http://sfbay.craigslist.org/search/sfc/fuo?sort=date&query=sofa%7Ccouch'
    listingsPage = rr.requestPage(url)
    rr.parse(listingsPage)
    listings = rr.getListingsLessThan(1000)
    if listings:
        content = rr.getAnchorLinksFromPids(listings)
        #with open('couches1.html', 'w') as htmlFile:
        #    htmlFile.write(content)
        emailer = Emailer()
        emailer.sendEmail("New Craigslist Couch/Sofa Listings", content)
    else:
        pass
        #emailer = Emailer()
        #emailer.sendEmail("Blue Ridge Heartbeat", str(datetime.datetime.now()))

            


                
            
        
        
