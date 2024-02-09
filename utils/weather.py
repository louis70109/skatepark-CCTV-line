import requests
import os
from datetime import datetime


def get_weather_data(location):
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": os.getenv('OPEN_API'),
        "format": "JSON",
        "locationName": location
    }
    headers = {
        "accept": "application/json"
    }

    response = requests.get(url, params=params, headers=headers)
    # 將回應的JSON內容轉換為Python字典
    data = response.json()

    return data


def simplify_data(data):
    location_data = data['records']['location'][0]
    weather_elements = location_data['weatherElement']

    simplified_data = {
        'location': location_data['locationName'],
    }

    for element in weather_elements:
        element_name = element['elementName']
        for time in element['time']:
            # 使用完整的開始時間作為鍵
            start_time = time['startTime']
            if start_time not in simplified_data:
                simplified_data[start_time] = {}

            parameter = time['parameter']
            parameter_str = parameter['parameterName']
            if 'parameterUnit' in parameter:
                parameter_str += f" {parameter['parameterUnit']}"

            # 尋找或創建對應時間的字典
            end_time = time['endTime']
            if end_time not in simplified_data[start_time]:
                simplified_data[start_time][end_time] = {}

            simplified_data[start_time][end_time][element_name] = parameter_str

    return simplified_data


def get_current_weather(simplified_data):
    try:
        # 獲取當前的日期和時間
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 遍歷所有的時間段
        for start_time in simplified_data:
            if start_time == 'location':
                continue
            for end_time in simplified_data[start_time]:
                # 如果當前時間在這個時間段內，則返回對應的天氣資訊
                if start_time <= now <= end_time:
                    return simplified_data[start_time][end_time]
                else:
                    # 如果沒有找到符合的時間段，則返回第一個天氣資訊
                    return simplified_data[start_time][end_time]
    except Exception as e:
        print(f"An error occurred: {e}")

    # 如果沒有找到任何天氣資訊，則返回None
    return None


# 使用範例
# weather_data = get_weather_data("臺北市")
# # print(weather_data)
# simplified_data = simplify_data(weather_data)
# # print(simplified_data)
# # 使用範例
# current_weather = get_current_weather(simplified_data)
# print(current_weather)
