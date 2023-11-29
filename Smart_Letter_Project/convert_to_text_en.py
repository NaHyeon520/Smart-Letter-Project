import easyocr
from difflib import SequenceMatcher

def convert_to_text_en(temp_result):#email, title, info부분 각각 매개변수로 따로 받기
    #ocr
    #email
    reader_en = easyocr.Reader(['en'])
    raw_email = reader_en.readtext(temp_result[0], detail=0, height_ths=1, width_ths=100)
    
    email = "".join(raw_email).replace(" ", "")#띄어쓰기 없애기

    #limit the email domain
    domains=["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "icloud.com", "comcast.net", "verizon.net", "att.net", "sbcglobal.net", "cox.net"]
    domain=email.split("@")[1]#extract domain
    ratios=[SequenceMatcher(None, domain, s).ratio() for s in domains]
    ind=ratios.index(max(ratios))
    email=email.split("@")[0]+"@"+domains[ind]

    print(email)

    #title
    raw_title = reader_en.readtext(temp_result[1], detail=0, height_ths=1, width_ths=100)
    title=" ".join(raw_title)
    print(title)

    #info
    info = reader_en.readtext(temp_result[2], detail=0, height_ths=1, width_ths=100)
    print(info)
    #insert newline
    text='\n'.join(info)

    # return (email, title, text) -->tuple!!
    return (email, title, text)

#print(convert_to_text("processed.png"))