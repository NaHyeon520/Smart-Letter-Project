import cv2
import pytesseract

'''
cam = cv2.VideoCapture(0)
cam.set(3,1280) #CV_CAP_PROP_FRAME_WIDTH
cam.set(4,720) #CV_CAP_PROP_FRAME_HEIGHT
#cam.set(5,0) #CV_CAP_PROP_FPS
 
while True:
    ret_val, img = cam.read() # 캠 이미지 불러오기
 
    cv2.imshow("Cam Viewer",img) # 불러온 이미지 출력하기
    if cv2.waitKey(1) == 27:
        break  # esc to quit
 
'''
pytesseract.pytesseract.tesseract_cmd='C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
#img=cv2.imread('photo.jpg')
img=cv2.imread('processed.png')
#img=cv2.imread('handtest.png')
img=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print(pytesseract.image_to_string(img, lang='kor'))
#print(pytesseract.image_to_string(img,lang='kor+eng'))
#cv2.imshow('res',img)
#cv2.waitKey(0)

'''
f= open("gt.txt", "r",encoding='UTF8')
outfile=open("tesseract_test.txt", "wb")

for i in range(50):
    line=f.readline()
    temp=line.split('\t')
    #print(temp[0])
    res=pytesseract.image_to_string(temp[0], lang='kor')+"--->\n"+temp[1]
    outfile.write(res.encode('utf-8'))
    #outfile.write("\t".encode('utf-8'))
    #if i==4:
       # break
        #'''