import easyocr
#import torch
#print(torch.cuda.is_available())
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import cv2 
import random 
import matplotlib.pyplot as plt

reader = easyocr.Reader(['ko'])#, recog_network='custom_model', gpu=False)
#filename = "photo.jpg"
filename = "processed.png"
result = reader.readtext(filename, detail=0)
print(result)
'''
img_ori=cv2.imread(filename)
img = Image.fromarray(img_ori)
draw = ImageDraw.Draw(img)
#np.random.seed(42)
#COLORS = np.random.randint(0, 255, size=(255, 3),dtype="uint8")
for i in result :
    x = i[0][0][0] 
    y = i[0][0][1] 
    w = i[0][1][0] - i[0][0][0] 
    h = i[0][2][1] - i[0][1][1]

    #color_idx = random.randint(0,255) 
    #color = [int(c) for c in COLORS[color_idx]]
    draw.rectangle(((x, y), (x+w, y+h)), outline=tuple((0,0,0)), width=2)
    #draw.text((int((x + x + w) / 2) , y-2),str(i[1]), font=font, fill=tuple(color),)
plt.imshow(img, cmap='gray')
plt.show()

'''

'''
f= open("gt.txt", "r",encoding='UTF8')
outfile=open("easyocr_test.txt", "wb")

for i in range(50):
    line=f.readline()
    temp=line.split('\t')
    #print(temp[0])
    res=reader.readtext(temp[0], detail=0)#+'\t'+temp[1]
    sentence=''.join(res)
    #print(res)
    outfile.write(sentence.encode('utf-8'))
    outfile.write('\t'.encode('utf-8'))
    outfile.write(temp[1].encode('utf-8'))
   # if i==4:
       # break
        #'''