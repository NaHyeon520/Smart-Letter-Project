#email, title, info 각각 잘라낸 이미지를 리턴, convert_to_text에서 사용
import cv2 
import numpy as np
import easyocr
from image_preprocess import *
from PIL import ImageDraw, Image

def extract_infos(img):#얘가 preprocess 함수 호출
    processed_img=image_preprocess(img)

    img = Image.fromarray(processed_img)
    draw = ImageDraw.Draw(img)

    reader = easyocr.Reader(['ko'])
    textbox = reader.detect(processed_img, height_ths=1, width_ths=100)
    hor_list=textbox[0]

    #email
    email_coord=hor_list[0][0]
    w=email_coord[1]-email_coord[0]
    h=email_coord[3]-email_coord[2]
    #cx=x+(w/2)
    cx=email_coord[0]+(w/2)
    cy=email_coord[2]+(h/2)
    email = cv2.getRectSubPix(
                processed_img, ##array면 안될 듯
                patchSize=(w,h), 
                center=(cx, cy)
        )
    
    draw.rectangle(((email_coord[0], email_coord[2]), (email_coord[0]+w, email_coord[2]+h)), outline='red', width=2)

    #title
    title_coord=hor_list[0][1]
    w=title_coord[1]-title_coord[0]
    h=title_coord[3]-title_coord[2]
    #cx=x+(w/2)
    cx=title_coord[0]+(w/2)
    cy=title_coord[2]+(h/2)
    title = cv2.getRectSubPix(
                processed_img, 
                patchSize=(w,h), 
                center=(cx, cy)
        )
    
    draw.rectangle(((title_coord[0], title_coord[2]), (title_coord[0]+w, title_coord[2]+h)), outline='red', width=2)

    #info
    info_coords=hor_list[0][2:]
    x_mins = np.array(info_coords).T[0] 
    x_maxs = np.array(info_coords).T[1] 
    y_mins = np.array(info_coords).T[2] 
    y_maxs = np.array(info_coords).T[3] 
    #제일 작은 x_min,y_min / 제일 큰 x_max,y_max
    info_x_start=min(x_mins)
    info_x_end=max(x_maxs)
    info_y_start=min(y_mins)
    info_y_end=max(y_maxs)
    w=info_x_end-info_x_start
    h=info_y_end-info_y_start
    #cx=x+(w/2)
    cx=info_x_start+(w/2)
    cy=info_y_start+(h/2)
    info = cv2.getRectSubPix(
                processed_img, 
                patchSize=(w,h), 
                center=(cx, cy)
        )
    draw.rectangle(((info_x_start, info_y_start), (info_x_start+w, info_y_start+h)), outline='red', width=2)

    #각 부분에 네모 그린 이미지 저장
    img.save('./static/rect.png')
    return (email, title, info)