import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

import os

def send_111mail(email, title, info, send_pic=False):#info: string converted from image
    print("send_mail called")
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login('bik48154815@gmail.com', 'cknscchqmsgvalch')

    msg = MIMEMultipart()
    msg['Subject'] = title
    content = MIMEText(info)
    msg.attach(content)

    '''
    if send_pic==True:
        filepath = "c:/Users/user/Desktop/GradProj-main/GradProj-main/0307.png"#제일 최신거 첨부하도록
        with open(filepath, 'rb') as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())  
            encoders.encode_base64(part) 
            part.add_header('Content-Disposition', 'attachment', filename=filepath)
            msg.attach(part)
    '''
    #addr = '4725hmc@gmail.com'
    # addr = "gbh4815@naver.com"#receiver
    #addr="hgcho@pusan.ac.kr"
    #addr='rlaskgus520@gmail.com'
    msg["To"] = email
    smtp.sendmail("bik48154815@gmail.com", email, msg.as_string())
    print("send success")
    smtp.quit()

def send_mail(email, title, info, send_pic=False):
    print(email, title, info)
    # Create a MIME text object with the message
    msg = MIMEText(info)

    # Set the sender and recipient of the email
    msg['From'] = 'r.seitzhan.r@gmail.com'
    msg['To'] = email
    msg['Subject'] = title

    # Connect to the SMTP server and send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        # smtp.login('r.seitzhan.r@gmail.com', 'm55brd69')
        smtp.login('bik48154815@gmail.com', 'cknscchqmsgvalch')
        smtp.sendmail('r.seitzhan.r@gmail.com', email, msg.as_string())

    # Return a response to the client
    return 'Email sent successfully'
