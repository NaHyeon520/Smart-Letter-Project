import easyocr
from check_grammar import *
from difflib import SequenceMatcher
from make_image import *

def convert_to_text(temp_result):#email, title, info부분 각각 매개변수로 따로 받기
    #ocr
    #email
    reader_en = easyocr.Reader(['en'])
    raw_email = reader_en.readtext(temp_result[0], detail=0, height_ths=1, width_ths=100)
    
    email = "".join(raw_email).replace(" ", "")#띄어쓰기 없애기

    #limit the email domain
    domains=["gmail.com", "naver.com", "daum.net", "hanmail.net", "kakao.com", "pusan.ac.kr"]
    domain=email.split("@")[1]#extract domain
    ratios=[SequenceMatcher(None, domain, s).ratio() for s in domains]
    ind=ratios.index(max(ratios))
    email=email.split("@")[0]+"@"+domains[ind]

    print(email)

    #title
    reader_ko = easyocr.Reader(['ko'])
    raw_title = reader_ko.readtext(temp_result[1], detail=0, height_ths=1, width_ths=100)
    
    #check grammar of title
    title=check_grammar(raw_title)
    title=" ".join(title)
    print(title)

    #info
    info = reader_ko.readtext(temp_result[2], detail=0, height_ths=1, width_ths=100)
    print(info)
    image_index=-1
    for i in range(len(info)):
        if info[i][0]=='&':
            image_index=i
    print(image_index)

    #check grammar of each sentence in info
    refined_text=check_grammar(info)

    #&로 시작하는 문장이 있을 때->이미지 생성 함수로 전달
    create_img_flag=0#&로 시작하는 문장이 있으면 1, html에서 사진 출력할지말지 결정해야하기 때문에 존재
    create_img_name=""
    if image_index>-1:
        make_image(refined_text[image_index][1:])
        create_img_flag=1
        create_img_name=refined_text[image_index][1:]
        # &로 시작하는 부분은 다른 텍스트로 대체
        refined_text[image_index]="[이 부분은 아래의 "+refined_text[image_index][1:]+" 이미지로 대체됩니다]"

    #insert newline
    text='\n'.join(refined_text)
    #text=refined_text

    # return (email, title, text) -->tuple!!
    return (email, title, text, create_img_flag, create_img_name, image_index)

#print(convert_to_text("processed.png"))