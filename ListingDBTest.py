import unittest
from mock import MagicMock
from ListingDB import ListingDB

class ListingDBTest(unittest.TestCase):

    def setUp(self):
        mockConn = MagicMock()
        self.mockCursor = MagicMock()
        mockConn.cursor.return_value = self.mockCursor

        self.db = ListingDB(mockConn)

    def testInit(self):
        self.mockCursor.execute.assert_called_with("CREATE TABLE IF NOT EXISTS listings(pid TEXT PRIMARY KEY, availableDate TEXT)")

    def testInsertListing(self):
        values = ("9999999", "2015-07-15")
        self.db.insert(values[0], values[1])
        self.mockCursor.execute.assert_called_with("INSERT INTO listings VALUES (?, ?)", values)

    def testHasListing(self):
        pid = "123"
        hasListing = self.db.has(pid)
        self.mockCursor.execute.assert_called_with("SELECT * FROM listings WHERE pid = ?", (pid,))

if __name__ == "__main__":
    unittest.main()
