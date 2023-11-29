from flask import Flask, redirect, url_for, render_template, request, flash, Response
import cv2
import datetime
import time
import os
import sys
import numpy as np
from threading import Thread
from sendmail import *
from convert_to_text import *
from extract_infos import *
from convert_to_text_en import *
from extract_infos_en import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib

global capture, rec_frame, grey, switch, neg, face, rec, out, result, p, captured_img, img_path, temp_result
capture = 0
grey = 0
switch = 1

captur = 0
gre = 0
switc = 1
global shot_taken
# make shots directory to save pics
try:
    os.mkdir('./shots')
except OSError as error:
    pass


# , static_url_path='', static_folder='/static')
app = Flask(__name__, template_folder='./templates')

camera = cv2.VideoCapture(0)

result = None


def gen_frames():  # generate frame by frame from camera
    global out, capture, rec_frame, shot_taken, p
    while True:
        success, frame = camera.read()
        if success:
            if (grey) or (gre):
                # make frame green
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if (capture) or (captur):  # capture frame
                capture = 0
                #global img_path
                now = datetime.datetime.now()
                p = os.path.sep.join(
                    ['shots', "shot_{}.png".format(str(now).replace(":", ''))])
                # img_path=p
                cv2.imwrite(p, frame)
                global captured_img
                captured_img = p  # save the img as a global variable
                shot_taken = 1
                # frame에 사진 찍은거 띄우기

            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass

        else:
            pass


"""def take_picture():
    success, frame = camera.read()
    now = datetime.datetime.now()
    imgname="shot_{}.png".format(str(now).replace(":", ''))
    imgname=imgname.replace(" ", "-")
    print(imgname)
    p = os.path.sep.join(
    ['shots', imgname])
    global img_path
    img_path='/files/'+imgname#절대경로해도 안됨
    print(img_path)
    cv2.imwrite(p, frame)
    global captured_img
    captured_img=p #save the img as a global variable"""


@app.route('/')
def index():
    global shot_taken
    shot_taken = 0  # 사진이 찍힌 상태를 판별할 플래그
    return render_template('index.html', img="http://127.0.0.1:4000/video_feed")


@app.route('/en')
def index_en():
    return render_template('en.html', img="http://127.0.0.1:4000/video_feed")


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/requests', methods=['POST', 'GET'])  # make responsable buttons
def tasks():
    global switch, camera, result, shot_taken, captured_img, img_path, temp_result, p
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            #global capture
            #capture = 1
            # shot_taken=1
            success, frame = camera.read()
            now = datetime.datetime.now()
            p = os.path.sep.join(
                ['shots', "shot_{}.png".format(str(now).replace(":", ''))])
            p = p.replace(" ", "-")
            cv2.imwrite(p, frame)

            # 여기서 글자 탐지, 네모 친 이미지를 static에 저장, return
            temp_result = extract_infos(p)
            return render_template('index.html', img="./static/rect.png")

        elif request.form.get('grey') == 'Grey':
            global grey
            grey = not grey
        elif request.form.get('start') == 'Start':  # stop or start the camera
            if (switch == 1):
                switch = 0
                camera.release()
                cv2.destroyAllWindows()
            else:
                camera = cv2.VideoCapture(0)
                switch = 1
            return render_template('index.html', img="http://127.0.0.1:4000/video_feed")
        elif request.form.get('ok') == 'OK':
            # 찍힌 사진이 없는 경우 prompt띄우기
            result = convert_to_text(temp_result)
            print(result)
            return render_template('index.html', email=result[0], title=result[1], text=result[2], img="./static/rect.png")
        """elif request.form.get('upload') == 'Upload': ###여기 다시 보기!!!!!
            print("upload pushed")
            file = request.files['upload']
            file.save(file.filename)
            #result = convert_to_text(file)
            #print(result)
            res=test.gray(file)
            print(res)"""
    elif request.method == 'GET':
        return render_template('index.html')
        # return redirect(url_for('tasks'))

    return render_template('index.html', img="http://127.0.0.1:4000/video_feed")
    """if shot_taken==1:
        return render_template('index.html', img="http://127.0.0.1:4000/video_feed")
    else:
        return render_template('index.html', img="http://127.0.0.1:4000/video_feed")"""

    """#아래 코드 없어도 되는지 확인
    if result is not None:
        return render_template('index.html', email=result[0], title=result[1], text=result[2]) #여기서는 result안줘도 되나?
    else:
        return render_template('index.html')"""


@app.route('/uploader', methods=['GET', 'POST'])
def uploader_file():
    if request.method == 'POST':
        f = request.files['file']
        #filename= url_for('static', filename='my_image.jpg')

        f.save("./static/"+f.filename)  # 경로를 static안으로 설정
        #global result
        #result = convert_to_text(f.filename)
        # print(result)
        #global captured_img
        # captured_img="./static/"+f.filename

        # 여기서 글자 탐지, 네모 친 이미지를 static에 저장, return
        global temp_result
        temp_result = extract_infos("./static/"+f.filename)

        global p
        p="./static/"+f.filename

        return render_template('index.html', img="./static/rect.png")
        # return render_template('index.html', img="http://127.0.0.1:4000/video_feed")


@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        global p

        # Get the form data from the request object
        recipient = request.form['email']
        subject = request.form['title']
        message = request.form['text']
        attach_image = request.form['attach']

        # Set base email info
        msg = MIMEMultipart()
        msg['Subject'] = subject
        #msg['From'] = 'bik48154815@gmail.com'
        msg['From'] = 'no-reply@gmail.com'
        msg['To'] = recipient

        # Set contents
        msg.attach(MIMEText(message))

        # Create a MIME text object with the message
        msg = MIMEMultipart()
        msg['Subject'] = subject
        content = MIMEText(message)
        msg.attach(content)
        if attach_image == 'yes':
            with open(p, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment',
                               filename=os.path.basename(p))
                msg.attach(img)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login('bik48154815@gmail.com', 'cknscchqmsgvalch')
            #smtp.sendmail('bik48154815@gmail.com', recipient, msg.as_string())
            smtp.sendmail('no-reply@gmail.com', recipient, msg.as_string())

        # Return a response to the client
        # return 'Email sent successfully'
        # 성공메세지 출력하기
        return render_template('index.html', img="http://127.0.0.1:4000/video_feed")
    
@app.route('/request', methods=['POST', 'GET'])  # make responsable buttons
def task():
    global switc, camera, resul, shot_take, captured_im, img_pat, temp_resul, p
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            success, fram = camera.read()
            now = datetime.datetime.now()
            p = os.path.sep.join(
                ['shots', "shot_{}.png".format(str(now).replace(":", ''))])
            p = p.replace(" ", "-")
            cv2.imwrite(p, fram)

            # 여기서 글자 탐지, 네모 친 이미지를 static에 저장, return
            temp_resul = extract_infos(p)
            return render_template('en.html', img="./static/rect.png")

        elif request.form.get('grey') == 'Grey':
            global grey
            grey = not grey
        elif request.form.get('start') == 'Start':  # stop or start the camera
            if (switc == 1):
                switc = 0
                camera.release()
                cv2.destroyAllWindows()
            else:
                camera = cv2.VideoCapture(0)
                switc = 1
            return render_template('en.html', img="http://127.0.0.1:4000/video_feed")
        elif request.form.get('ok') == 'OK':
            # 찍힌 사진이 없는 경우 prompt띄우기
            resul = convert_to_text_en(temp_resul)
            print(resul)
            return render_template('en.html', email=resul[0], title=resul[1], text=resul[2], img="./static/rect.png")
        """elif request.form.get('upload') == 'Upload': ###여기 다시 보기!!!!!
            print("upload pushed")
            file = request.files['upload']
            file.save(file.filename)
            #result = convert_to_text(file)
            #print(result)
            res=test.gray(file)
            print(res)"""
    elif request.method == 'GET':
        return render_template('en.html')
        # return redirect(url_for('tasks'))

    return render_template('en.html', img="http://127.0.0.1:4000/video_feed")

@app.route('/uploaderen', methods=['GET', 'POST'])
def uploader_file_en():
    if request.method == 'POST':
        f = request.files['file']
        #filename= url_for('static', filename='my_image.jpg')

        f.save("./static/"+f.filename)  # 경로를 static안으로 설정
        #global result
        #result = convert_to_text(f.filename)
        # print(result)
        #global captured_img
        # captured_img="./static/"+f.filename

        # 여기서 글자 탐지, 네모 친 이미지를 static에 저장, return
        global temp_result
        temp_result = extract_infos_en("./static/"+f.filename)
        
        global p
        p="./static/"+f.filename

        return render_template('en.html', img="./static/rect.png")
        # return render_template('index.html', img="http://127.0.0.1:4000/video_feed")

@app.route('/send_email_en', methods=['POST'])
def send_email_en():
    if request.method == 'POST':
        global p

        # Get the form data from the request object
        recipient = request.form['email']
        subject = request.form['title']
        message = request.form['text']
        attach_image = request.form['attach']

        # Set base email info
        msg = MIMEMultipart()
        msg['Subject'] = subject
        #msg['From'] = 'bik48154815@gmail.com'
        msg['From'] = 'no-reply@gmail.com'
        msg['To'] = recipient

        # Set contents
        msg.attach(MIMEText(message))

        # Create a MIME text object with the message
        msg = MIMEMultipart()
        msg['Subject'] = subject
        content = MIMEText(message)
        msg.attach(content)
        if attach_image == 'yes':
            with open(p, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment',
                               filename=os.path.basename(p))
                msg.attach(img)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login('bik48154815@gmail.com', 'cknscchqmsgvalch')
            #smtp.sendmail('bik48154815@gmail.com', recipient, msg.as_string())
            smtp.sendmail('no-reply@gmail.com', recipient, msg.as_string())

        # Return a response to the client
        # return 'Email sent successfully'
        # 성공메세지 출력하기
        return render_template('en.html', img="http://127.0.0.1:4000/video_feed")
    
if __name__ == '__main__':
    app.run('127.0.0.1', port=4000, debug=True)

camera.release()
cv2.destroyAllWindows()
