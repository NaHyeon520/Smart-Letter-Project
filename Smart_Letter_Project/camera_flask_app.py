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
from make_image import *
from convert_only_email import *
import smtplib

global capture, rec_frame, grey, switch, neg, face, rec, out, result, p, captured_img, img_path, temp_result, create_img_flag
global no_convert
choose_convert=0
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
                # make frame grey
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


@app.route('/')
def index():
    #global shot_taken
    #shot_taken = 0  # 사진이 찍힌 상태를 판별할 플래그
    return render_template('index.html', img="http://127.0.0.1:4000/video_feed")


@app.route('/en')
def index_en():
    return render_template('en.html', img="http://127.0.0.1:4000/video_feed")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/about_en')
def about_en():
    return render_template('about_en.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/requests', methods=['POST', 'GET'])  # make responsable buttons
def tasks():
    global switch, camera, result, captured_img, temp_result, p, create_img_flag, no_convert
    if request.method == 'POST':
        #if request.form.get('mode') == 'image':
            #no_convert=1
        if request.form.get('click') == 'Capture':
            success, frame = camera.read()
            now = datetime.datetime.now()
            p = os.path.sep.join(
                ['shots', "shot_{}.png".format(str(now).replace(":", ''))])
            p = p.replace(" ", "-")
            cv2.imwrite(p, frame)
            # text detection
            temp_result = extract_infos(p)
            no_convert=request.form.get('mode')
            print(no_convert)
            ##make image test
            #make_image("test")
            ##

            return render_template('index.html', img="./static/rect.png")#, created_img="./static/created.png")

        elif request.form.get('grey') == 'Grey':
            global grey
            grey = not grey
        elif request.form.get('start') == 'Start':  # stop or start the camera
            if (switch == 1):
                switch = 0
                camera.release()
                cv2.destroyAllWindows()
                create_img_flag=0
            else:
                camera = cv2.VideoCapture(0)
                switch = 1
            return render_template('index.html', img="http://127.0.0.1:4000/video_feed")
        elif request.form.get('ok') == 'OK':  
            if no_convert=='image': #손편지 그대로 전송하기 선택 시
                print("image chosen")
                result=convert_only_email(temp_result[0])
                return render_template('index.html', email=result, img="./static/rect_email.png")
            else:
                result = convert_to_text(temp_result)
                print(result)
                create_img_flag=result[3]
                #info='\n'.join(result[2])
                if create_img_flag==1:
                    return render_template('index.html', email=result[0], title=result[1], text=result[2], img="./static/rect.png", create_text="생성된 "+result[4]+" 이미지:", created_img="./static/created.png")
                else:
                    return render_template('index.html', email=result[0], title=result[1], text=result[2], img="./static/rect.png")
    elif request.method == 'GET':
        return render_template('index.html')

    return render_template('index.html', img="http://127.0.0.1:4000/video_feed")


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
        global p, create_img_flag, result

        # Get the form data from the request object
        recipient = request.form['email']
        subject = request.form['title']
        message = request.form['text']
        attach_image = request.form['attach']
        #print(message.split('\n'))

        # Set base email info
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = 'bik48154815@gmail.com'
        msg['From'] = 'no-reply@gmail.com'
        msg['To'] = recipient
        '''
        # 손편지 그대로 전송하려는 경우
        msg.attach(MIMEText('<html><body><p><img src="cid:0"></p></body></html>', 'html', 'utf-8'))
        with open(p, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment',
                                filename=os.path.basename(p))
            img.add_header('Content-ID', '<0>')
            msg.attach(img)
        '''#임시로 주석 처리
        #### & 있을 경우 생성된 이미지를 해당 라인에 첨부
        if create_img_flag==1:
            #msg_html=MIMEText('<html><head><body><img src="./static/created.png"></body></head></html>')
            #msg.attach(msg_html)
            message_in_line=message.split('\n')
            msg.attach(MIMEText('<html><body>' +'\n'.join(message_in_line[:result[5]])+
            '<p><img src="cid:0" width="100px" height="100px"></p>' + '\n'.join(message_in_line[result[5]+1:])+
            '</body></html>', 'html', 'utf-8'))
            with open("./static/created.png", 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment',
                                filename=os.path.basename("./static/created.png"))
                img.add_header('Content-ID', '<0>')
                msg.attach(img)
        else:
            msg.attach(MIMEText(message))
        

        # Create a MIME text object with the message
        #msg = MIMEMultipart()
        #msg['Subject'] = subject
        #content = MIMEText(message)
        #msg.attach(content)
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

#english version
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
