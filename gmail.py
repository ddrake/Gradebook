import smtplib
from email.mime.text import MIMEText


class Gmail():
    """Gmail using my account"""
    def __init__(self, subject="Test", body="Does it work?", recipients=[]):
        with open('gmail_credentials.txt', 'r') as f:
            content = f.read()
        lines = content.strip().split('\n')
        cred = dict([l.split(':') for l in lines])
        self.gmail_user = cred['gmail_user']
        self.gmail_password = cred['gmail_password']
        self.subject = subject
        self.body = body
        self.sender = self.gmail_user
        self.recipients = []

    def send(self):
        """send the email"""
        msg = self._make_email()
        self._send_via_gmail(msg)

    def _make_email(self):
        msg = MIMEText(self.body)
        msg['Subject'] = self.subject 
        msg['From'] = self.sender
        msg['To'] = ','.join(self.recipients)
        return msg

    def _send_via_gmail(self, msg):
        try:  
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(self.gmail_user, self.gmail_password)
            server.sendmail(self.gmail_user, self.recipients, msg.as_string())
            server.close()
        except smtplib.SMTPAuthenticationError as err:
            print(err)
        except:  
            print( 'Something went wrong...')
