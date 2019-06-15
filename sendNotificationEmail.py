
from configparser import ConfigParser


import smtplib

from os import listdir
import os.path
from email import Encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

config = ConfigParser()
config.read('config.ini')

logging.basicConfig(filename='optimat_alarm.log', level=logging.INFO)

try:
    mail_user = self.config.get('main', 'MAIL_SENDER')
    mail_pwd = self.config.get('main', 'MAIL_PASSWORD')
    mail_to = self.config.get('main', 'MAIL_RECIPIENT')
    MAIL_SERVER = self.config.get('main', 'MAIL_SERVER')

    msg = MIMEMultipart()
    mp4files = [f for f in listdir('alarmimages/') if f.endswith('.mp4')]
    msg['From'] = mail_user
    msg['To'] = mail_to
    msg['Subject'] = 'Alarm, Bewegung detektiert!'
    msg.attach(MIMEText("Hello Master! Hier das File.."))

    part = MIMEBase('application', 'octet-stream')

    part.set_payload(open('alarmimages/'+mp4files[0], 'rb').read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' %
                    os.path.basename('alarmimages/'+mp4files[0]))
    msg.attach(part)

    mailServer = smtplib.SMTP(MAIL_SERVER, 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(mail_user, mail_pwd)
    mailServer.sendmail(mail_user, mail_to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()
except Exception:
    logging.exception("Could not send alarm email video")
