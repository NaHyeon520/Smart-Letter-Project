import requests
import json
import io
import base64
from PIL import Image
import googletrans

def make_image(text_to_draw):
    REST_API_KEY = '7f865fe282a0277d4f81c5f29d1d1723'

    # 이미지 생성하기 요청
    def t2i(text, batch_size=1):
        r = requests.post(
            'https://api.kakaobrain.com/v1/inference/karlo/t2i',
            json = {
                'prompt': {
                    'text': text,
                    'batch_size': batch_size
                }
            },
            headers = {
                'Authorization': f'KakaoAK {REST_API_KEY}',
                'Content-Type': 'application/json'
            }
        )
        # 응답 JSON 형식으로 변환
        response = json.loads(r.content)
        return response

    # Base64 디코딩 및 변환
    def stringToImage(base64_string, mode='RGBA'):
        imgdata = base64.b64decode(str(base64_string))
        img = Image.open(io.BytesIO(imgdata)).convert(mode)
        return img

    # 프롬프트에 사용할 제시어
    #text = "a white siamese cat"
    #text_to_draw = "샴 고양이"
    translator = googletrans.Translator()

    text = translator.translate(text_to_draw, dest='en')
    #print(f"샴고양이 => {text.text}")

    # 이미지 생성하기 REST API 호출
    response = t2i(text.text, 1)

    # 응답의 첫 번째 이미지 생성 결과 출력하기
    result = stringToImage(response.get("images")[0].get("image"), mode='RGB')
    #result.show()
    result.save("./static/created.png")
    #created_img_name="created.png"
    return #created_img_name