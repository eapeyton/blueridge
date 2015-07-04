import sqlite3

class ListingDB:

    def __init__(self, connection=None):
        if connection is None:
            self.conn = sqlite3.connect('listings.db')
        else:
            self.conn = connection
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS listings(pid TEXT PRIMARY KEY, availableDate TEXT)")
        self.conn.commit()

    def insert(self, pid, availDate):
        values = (pid, availDate)
        self.cursor.execute("INSERT INTO listings VALUES (?, ?)", values)
        self.conn.commit()

    def has(self, pid):
        self.cursor.execute("SELECT * FROM listings WHERE pid = ?", (pid,))
        res = self.cursor.fetchone()
        if res is None:
            return False
        else:
            return True

    def __del__(self):
        self.conn.close()
        


