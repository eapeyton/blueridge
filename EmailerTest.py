import unittest
from mock import MagicMock
import md5
import Emailer
from email.mime.text import MIMEText

class TestEmailer(unittest.TestCase):

    def setUp(self):
        self.emailer = Emailer.Emailer()

    def testGetPasswordFromFile(self):
        passwd = self.emailer.getPasswordFromFile("gmail_passwd.txt")
        m = md5.new()
        m.update(passwd)
        self.assertEqual("\x1b\x89\x08_\x90k\xd0\t'J\x16\x99Q&\x14A", m.digest())

    def testSetSMTP(self):
        mockSMTP = MagicMock()
        self.emailer.setSMTP(mockSMTP)
        self.assertEqual(self.emailer.SMTP, mockSMTP)

    def testSendEmail(self):
        mockSMTP = MagicMock()
        self.emailer.setSMTP(mockSMTP)
        subject = "Well my home is in the Blue Ridge Mountains"
        content = "And I ain't comin' back here anymore"
        self.emailer.sendEmail(subject, content)

        expMsg = MIMEText(content, 'html')
        expTo = "ea.peyton@gmail.com"
        expFrom = "eric.peeton@gmail.com"
        expMsg['Subject'] = subject
        expMsg['To'] = expTo
        expMsg['From'] = expFrom
        mockSMTP.sendmail.assert_called_with(expFrom, [expTo], expMsg.as_string())


if __name__ == '__main__':
    unittest.main()
