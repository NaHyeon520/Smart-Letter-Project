#convert_to_text에서 호출됨
import requests
import json

def check_grammar(text):
    #text 리스트의 한 원소마다 검사기 돌리기
    #text=text.split('\n')
    checked_text=[]
    #print(text)
    for line in text:
        
        line=line.replace(" ", "")#오류 방지를 위해 띄어쓰기 전부 제거
        #print(line)
        response = requests.post('http://164.125.7.61/speller/results', data={'text1': line})
        data = response.text.split('data = [', 1)[-1].rsplit('];', 1)[0]
        #print(data)
        if(data.find('맞춤법과 문법 오류를 찾지')>0):
            #print("no error")
            checked_text.append(line)
            continue
        data = json.loads(data)
        diff=0
        for err in data['errInfo']:
            candWord=err['candWord'].split("|")[0]#대치어가 여러개일 경우 일단 제일 첫번째거 쓰도록 함. 
            line=line[0:err['start']+diff]+candWord+line[err['end']+diff:]
            #print(text)
            diff=diff+(len(candWord)-len(line[err['start']:err['end']]))
            #print(diff)
        checked_text.append(line)
    return checked_text

#print(check_grammar("내용입니다 . 졸업할 수 윗젯지?"))