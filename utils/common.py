import re
import os
import requests
from PIL import Image
from io import BytesIO
import google.generativeai as genai

def check_location_in_message(message):
    locations = [
        "臺北市", "臺中市", "臺南市", "高雄市", 
        "新北市", "桃園市", "新竹市", "苗栗縣", 
        "彰化縣", "南投縣", "雲林縣", "嘉義市", 
        "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", 
        "臺東縣", "澎湖縣"
    ]

    # 將訊息中的 "台" 替換為 "臺"
    corrected_message = re.sub("台", "臺", message)
    local = corrected_message.split("_")

    for location in locations:
        if re.search(local[0], location):
            return location
        else:
            location

    return locations[0]


def check_image_wet(url="https://github.com/louis70109/ideas-tree/blob/master/images/%E5%8F%B0%E5%8C%97_%E5%A4%A7%E7%9B%B4%E7%BE%8E%E5%A0%A4%E6%A5%B5%E9%99%90%E5%85%AC%E5%9C%92/default.png"):
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

    response = requests.get(url)
    if response.status_code == 200:
        image_data = response.content
        image = Image.open(BytesIO(image_data))

        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content([
            "Does following image looks moist? Reply Yes or No in traditional chinese",
            image
        ])
        return response.text
    return 'None'

