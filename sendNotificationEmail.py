import optimatconfig as config

import smtplib

from os import listdir
import os.path
from email import Encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

mail_user = config.MAIL_SENDER
mail_pwd = config.MAIL_PASSWORD
mail_to = config.MAIL_RECIPIENT
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

mailServer = smtplib.SMTP(config.MAIL_SERVER, 587)
mailServer.ehlo()
mailServer.starttls()
mailServer.ehlo()
mailServer.login(mail_user, mail_pwd)
mailServer.sendmail(mail_user, mail_to, msg.as_string())
# Should be mailServer.quit(), but that crashes...
mailServer.close()
