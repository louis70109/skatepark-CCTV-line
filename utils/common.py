import re
from datetime import datetime

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
