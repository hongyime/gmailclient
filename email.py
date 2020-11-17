import os
import datetime
from datetime import datetime
import smtplib, ssl
from email import encoders 
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

try:
    with open('message.txt', 'r') as f:
        message = f.read()

    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context)
    server.ehlo()
    server.login('email', 'password') #replace
    msg = MIMEMultipart()
    msg['From'] = "from who name" #replace
    msg['To'] = "send to email" #replace
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    subject =  date_time + ' logs'
    msg['Subject'] = subject
    msg.attach(MIMEText(message, "plain"))

    text = msg.as_string()
    server.sendmail('from who email', 'send to email', text) #replace
    server.quit()

except Exception as e:
    print(e)