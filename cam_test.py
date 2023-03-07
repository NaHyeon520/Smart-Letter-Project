import cv2
#print(cv2.__version__)
#import matplotlib.pyplot as plt

cap= cv2.VideoCapture(0)
if cap.isOpened():
    
    while True:
        ret,frame = cap.read()
        
        if ret:
            cv2.imshow('camera', frame)

            if cv2.waitKey(1) != -1:
                cv2.imwrite('photo.jpg', frame)
                break
            
        else:
            print('no frame')
            break
else:
    print('no camera!')
cap.release()
cv2.destroyAllWindows()