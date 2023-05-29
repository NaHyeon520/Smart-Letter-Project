import cv2
import matplotlib.pyplot as plt
import numpy as np
import easyocr


def image_preprocess(img):
    # 흑백으로 변환
    img_ori = cv2.imread(img)
    height, width, channel = img_ori.shape
    img_gray = cv2.cvtColor(img_ori, cv2.COLOR_BGR2GRAY)

    # 가우시안 블러링
    # 5 * 5 크기의 가우시안 마스크를 영상에 적용.
    img_blurred = cv2.GaussianBlur(img_gray, ksize=(5, 5), sigmaX=0)

    # 이진화(adaptive threshold기법)
    img_thresh = cv2.adaptiveThreshold(
        img_blurred,
        maxValue=255.0,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY,
        blockSize=19,
        C=9
    )

    # 윤곽 찾기
    contours, _ = cv2.findContours(
        img_thresh,
        mode=cv2.RETR_LIST,
        method=cv2.CHAIN_APPROX_SIMPLE
    )

    # 윤곽을 토대로 사각형 그리기
    temp_result = np.zeros((height, width, channel), dtype=np.uint8)

    contours_dict = []  # 각 윤곽선에서 사각형 영역과 중심좌표를 알아내어 저장할 리스트

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)  # 끝점에서 사각형 영역을 뽑아낸다
        cv2.rectangle(temp_result, pt1=(x, y), pt2=(x+w, y+h),
                      color=(255, 255, 255), thickness=2)  # 윤곽선을 사각형으로 그려서 표현

        # insert to dict
        contours_dict.append({
            'contour': contour,  # 실제 윤곽선
            'x': x,             # 윤곽선의 왼쪽 상단 x좌표
            'y': y,             # 윤곽선의 왼쪽 상단 y좌표
            'w': w,             # 윤곽선의 너비
            'h': h,             # 윤곽선의 높이
            'cx': x + (w / 2),  # 윤곽선의 중심 x좌표
            'cy': y + (h / 2)   # 윤곽선의 중심 y좌표
        })  # 리스트에 추가

    # contours_dict 안에서 가장 넓은 높이와 너비를 가진 사각형 추출

    a = sorted(contours_dict, key=lambda k: k['w']*k['h'], reverse=True)

    biggest_rec = a[0]
    temp_result = np.zeros((height, width, channel), dtype=np.uint8)

    img_cropped = cv2.getRectSubPix(  # 편지지만큼 잘라냄
        img_gray,
        patchSize=(int(biggest_rec['w']), int(biggest_rec['h'])),
        center=(int(biggest_rec['cx']), int(biggest_rec['cy']))
    )

    # adaptive threshold
    img_thresh = cv2.adaptiveThreshold(
        img_cropped,
        maxValue=255.0,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY,
        blockSize=19,
        C=9
    )
    # plt.imshow(img_thresh,cmap='gray')
    # plt.show()

    ###여기서 인식하지 말고 img_thresh를 extract_infos 로 전달
    #plt.imsave('processed.png', img_thresh)
    return img_thresh
    #return 'processed.png'


""" plt.imsave('processed.png', img_thresh)

    reader = easyocr.Reader(['ko'])
    filename = "processed.png"
    result = reader.readtext(filename, detail=0)
    return result
"""