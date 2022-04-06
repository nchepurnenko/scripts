import os
import csv
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def load_data_from_csv(filename):
  
    with open(filename, 'r', encoding='utf-8') as csvfile:
        rows = csv.DictReader(csvfile)
        yield from rows

# csv format: name,lname,email,password,to        
csv_file = 'mailuser.csv'
users = load_data_from_csv(csv_file)
sender_email = 'mail_admin@domain.com'
smtp_server = "0.0.0.0:587"
for user in users:
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user['to']
    msg['Subject'] = u"Учетные данные для Яндекс почты"
    message = u"Добрый день! Ваши учетные данные для входа в Яндекс-почту.\n" + \
                u"Логин: " + user['email'] + "\n" + \
                u"Пароль: " + user['password'] + "\n" + \
                u"Ссылка: https://mail.yandex.ru/ \n"

    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP(smtp_server)
    server.starttls()
    server.sendmail(msg['From'],msg['To'],msg.as_string())
    server.quit()
