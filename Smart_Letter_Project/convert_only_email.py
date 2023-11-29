import easyocr
from check_grammar import *
from difflib import SequenceMatcher
from make_image import *

def convert_only_email(email_part):#email
    #ocr
    #email
    reader_en = easyocr.Reader(['en'])
    raw_email = reader_en.readtext(email_part, detail=0, height_ths=1, width_ths=100)
    
    email = "".join(raw_email).replace(" ", "")#띄어쓰기 없애기

    #limit the email domain
    domains=["gmail.com", "naver.com", "daum.net", "hanmail.net", "kakao.com", "pusan.ac.kr"]
    domain=email.split("@")[1]#extract domain
    ratios=[SequenceMatcher(None, domain, s).ratio() for s in domains]
    ind=ratios.index(max(ratios))
    email=email.split("@")[0]+"@"+domains[ind]

    print(email)

    return email