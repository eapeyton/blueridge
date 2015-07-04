from subprocess import Popen, PIPE, STDOUT
from email.mime.text import MIMEText
import smtplib

class Emailer:

    def initSMTP(self):
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        self.SMTP = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        self.SMTP.starttls()
        self.SMTP.login("eric.peeton@gmail.com", self.getPasswordFromFile("gmail_passwd.txt"))

    def getPasswordFromFile(self, filename):
        process = Popen(['cat',filename], stdout=PIPE, stderr=PIPE)
        password = process.communicate()[0].decode('utf-8').strip()
        return password

    def setSMTP(self, SMTP):
        self.SMTP = SMTP

    def sendEmail(self, subject, content):
        to = ["ea.peyton@gmail.com"]
        from_ = "eric.peeton@gmail.com"
        delimiter = ", "

        msg = MIMEText(content, 'html')
        msg['Subject'] = subject
        msg['To'] = delimiter.join(to)
        msg['From'] = from_

        try:
            self.SMTP.sendmail(from_, to, msg.as_string())
        except AttributeError:
            self.initSMTP()
            self.SMTP.sendmail(from_, to, msg.as_string())

    def __del__(self):
        try:
            self.SMTP.quit()
        except AttributeError:
            pass

if __name__ == "__main__":
    emailer = Emailer()
    emailer.sendEmail("hello","goodbye")


