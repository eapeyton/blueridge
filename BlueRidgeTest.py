import unittest
import os
import re
import BlueRidge
from mock import MagicMock,call

class TestBlueRidge(unittest.TestCase):

    def setUp(self):
        DummyResponse.count = 0
        BlueRidge.requests.Session.get = getStub
        self.br = BlueRidge.BlueRidge()
        self.mockDB = MagicMock()
        self.mockDB.has.return_value = False
        self.br.setDB(self.mockDB)
        self.testHTML = self.readTestResource('test_listings.html')
        self.br.parse(self.testHTML)
        
    def readTestResource(self, fileName):
        return open('test_resources' + os.sep + fileName, 'r').read()

    def testInitialize(self):
        br = BlueRidge.BlueRidge()

    def testGetCountReturnsNumberOfListings(self):
        self.assertEqual(self.br.getCount(), 65)

    def testGetPricesReturnsListOfPrices(self):
        prices = self.br.getPrices()
        firstFive = [4199, 3795, 3690, 3690, 3995]
        lastFive = [3599, 3995, 3995, 4275,  3800]
        self.assertEqual(prices[:5], firstFive)
        self.assertEqual(prices[-5:], lastFive)

    def testGetBedroomsReturnsListOfBedroomNumbers(self):
        bedrooms = self.br.getBedrooms()
        firstThree = [3, 1, 5]
        lastThree = [None, 1 , 3]
        self.assertEqual(bedrooms[:3], firstThree)
        self.assertEqual(bedrooms[-3:], lastThree)

    def testGetPricePerBedroom(self):
        pricesPerBR = self.br.getPricesPerBedroom()
        firstThree = [1399, 3795, 738]
        lastThree = [None, 4275, 1266]
        self.assertEqual(pricesPerBR[:3], firstThree)
        self.assertEqual(pricesPerBR[-3:], lastThree)

    def testGetPricePerBRLessThan(self):
        pids = self.br.getListingsLessThanPerBR(800)
        self.assertEqual(['5103222100', '5100264644'], pids)

        pids = self.br.getListingsLessThanPerBR(2000)
        firstThree = ['5099100613', '5103222100', '5103184176']
        lastThree = ['5093685533', '5074594406', '5091461362']
        self.assertEqual(pids[:3], firstThree)
        self.assertEqual(pids[-3:], lastThree)

    def testGetListOfPids(self):
        pids = self.br.getListOfPids()
        firstThree = ['5099100613', '5091956847', '5103222100']
        lastThree = ['5080906882', '5092464764', '5091461362']
        self.assertEqual(pids[:3], firstThree)
        self.assertEqual(pids[-3:], lastThree)

    def testGetAvailableDateOfPid(self):
        self.assertEqual("2015-07-15", self.br.getAvailableDate('test_listing1'))
        self.assertEqual("2015-08-01", self.br.getAvailableDate('test_listing2'))
        self.assertEqual("2015-07-01", self.br.getAvailableDate('test_listing3'))

    def testGetCountAvailableAfterDate(self):
        self.assertEqual(44, self.br.getCountAvailableAfter('2015-07-15'))

    def testListingsAvailableAfterDate(self):
        listings = self.br.getListingsAvailableAfter('2015-07-15')
        firstThree = ['5099100613','5091956847','5103184176']
        lastThree = ['5074594406','5092464764','5091461362']
        self.assertEqual(listings[:3], firstThree)
        self.assertEqual(listings[-3:], lastThree)

    def testListingsAvailableAfterDateAndLessThan(self):
        listings = self.br.getListingsAvailableAfterAndLessThan('2015-07-15', 2000)
        firstThree = ['5099100613','5103184176','5057174858']
        lastThree = ['5093685533','5074594406','5091461362']

        self.assertEqual(listings[:3], firstThree)
        self.assertEqual(listings[-3:], lastThree)

    def testGetLinksFromPids(self):
        links = self.br.getLinks(['123', '456', '111'])
        self.assertEqual(['http://sfbay.craigslist.org/sfc/apa/123.html',
                        'http://sfbay.craigslist.org/sfc/apa/456.html',
                        'http://sfbay.craigslist.org/sfc/apa/111.html'], links)

    def testGetAnchorLinksFromPids(self):
        anchorLinks = self.br.getAnchorLinksFromPids(['123', '456', '111'])
        self.assertEqual("""<a href=\"http://sfbay.craigslist.org/sfc/apa/123.html\">http://sfbay.craigslist.org/sfc/apa/123.html</a><br /><a href=\"http://sfbay.craigslist.org/sfc/apa/456.html\">http://sfbay.craigslist.org/sfc/apa/456.html</a><br /><a href=\"http://sfbay.craigslist.org/sfc/apa/111.html\">http://sfbay.craigslist.org/sfc/apa/111.html</a><br />""", anchorLinks)

    def testGetListingsAvailableAfterCallsDB(self):
        listings = self.br.getListingsAvailableAfter('2015-07-15')
        calls = [call("5099100613"), call("5091461362"), call("5072685563")]
        self.mockDB.has.assert_has_calls(calls, any_order=True)

    def testInsertListingToDB(self):
        listings = self.br.getListingsAvailableAfter('2015-07-15')
        calls = [call("5099100613", '2015-07-15'), call("5091461362", '2015-08-01'), call("5072685563", '2015-07-15')]
        self.mockDB.insert.assert_has_calls(calls, any_order=True)
        

def getStub(self, url, params=None, **kwargs):
    return DummyResponse(url)

class DummyResponse:
    count = 0

    def __init__(self, url):
        search = re.search('test_listing(\d+)', url)
        if search is None:
            testNum = DummyResponse.count % 3 + 1
            DummyResponse.count += 1
        else:
            testNum = search.group(1)
        self.text = open('test_resources' + os.sep + 'test_listing' + str(testNum) + '.html', 'r').read() 

        

if __name__ == '__main__':
    unittest.main()
