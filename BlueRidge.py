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
        self.bedrooms = self.getBedrooms()
        self.pricesPer = self.getPricesPerBedroom()

    def getCount(self):
        return len(self.rows)

    def getPrices(self):
        prices = [int(row.find('span', class_='price').string.replace('$','')) for row in self.rows]
        return prices

    def getBedrooms(self):
        bedrooms = []
        for row in self.rows:
            brSpan = row.find('span', class_='housing')

            if brSpan is None:
                bedrooms.append(None)
            else:
                count = int(re.search("(\d+)br", str(brSpan.text)).group(1))
                bedrooms.append(count)
        
        return bedrooms

    def getPricesPerBedroom(self):
        pricesPerBR = []
        for i in range(0, len(self.prices)):
            if self.bedrooms[i] is None:
                pricesPerBR.append(None)
            else:
                pricesPerBR.append(int(self.prices[i])/int(self.bedrooms[i]))
        return pricesPerBR

    def getListOfPids(self):
        return [row['data-pid'] for row in self.rows]

    def getListingsLessThanPerBR(self, maxPrice):
        indices = []
        for index, pricePer in enumerate(self.pricesPer):
            if pricePer is not None and pricePer <=  maxPrice:
                indices.append(index)
        
        pids = []
        for index in indices:
            row = self.rows[index]
            pid = row['data-pid']
            #if not self.db.has(pid):
            pids.append(pid)
            #    self.db.insert(pid, None)
        return pids

    def getAvailableDate(self, pid):
        listingHTML = self.requestPage(self.generateLink(pid))
        soup = BeautifulSoup(listingHTML)
        date = soup.find('span', class_="housing_movein_now property_date")['date']
        return date

    def getCountAvailableAfter(self, date):
        return len(self.getListingsAvailableAfter(date))

    def getListingsAvailableAfter(self, date):
        listings = []
        pids = self.getListOfPids()
        for pid in pids:
            if not self.db.has(pid):
                if self.goSlow:
                    time.sleep(random.randint(1,3))
                listingDate = self.getAvailableDate(pid)
                if listingDate >= date and listingDate <= '2016-01-01':
                    listings.append(pid)
                self.db.insert(pid, listingDate)
        return listings

    def getListingsAvailableAfterAndLessThan(self, date, maxPrice):
        #TODO: Fix because both methods are now inserting into the database
        pids = self.getListOfPids()
        listingsSet = set(self.getListingsLessThanPerBR(maxPrice)) & set(self.getListingsAvailableAfter(date))
        listings = [listing for listing in pids if listing in listingsSet]
        return listings

    def generateLink(self, pid):
        return "http://sfbay.craigslist.org/sfc/apa/" + pid + ".html"

    def requestPage(self, url):
        try:
            return self.session.get(url).text
        except AttributeError:
            self.initSession()
            return self.session.get(url).text

    def getLinks(self, pids):
        return [self.generateLink(pid) for pid in pids]

    def getAnchorLinksFromPids(self, pids):
        links = self.getLinks(pids)
        anchorLinks = ""
        for link in links:
            anchorLink = "<a href=\"%s\">%s</a><br />" % (link, link)
            anchorLinks += anchorLink
        return anchorLinks

if __name__ == '__main__':
    br = BlueRidge()
    br.goSlow = True
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = 'http://sfbay.craigslist.org/search/sfc/apa?s=200&nh=149&nh=4&nh=12&nh=10&nh=18&nh=21&nh=27&nh=1&bedrooms=2'
    listingsPage = br.requestPage(url)
    br.parse(listingsPage)
    listings = br.getListingsLessThanPerBR(2000)
    #listings = br.getListingsAvailableAfterAndLessThan('2015-07-15', 2000)
    if listings:
        content = br.getAnchorLinksFromPids(listings)
        with open('listings3.html', 'w') as htmlFile:
            htmlFile.write(content)
        #emailer = Emailer()
        #emailer.sendEmail("Listings less 2000 per BR", content)
        #emailer.sendEmail("Listings available after July 15th and less 2000 per BR", content)
    else:
        pass
        #emailer = Emailer()
        #emailer.sendEmail("Blue Ridge Heartbeat", str(datetime.datetime.now()))

            


                
            
        
        
