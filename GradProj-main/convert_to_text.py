import easyocr
from check_grammar import *
from difflib import SequenceMatcher

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
    #check grammar of each sentence in info
    refined_text=check_grammar(info)

    #insert newline
    text='\n'.join(refined_text)

    # return (email, title, text) -->tuple!!
    return (email, title, text)

#print(convert_to_text("processed.png"))