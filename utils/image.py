import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

class SkateParkImage:
    def __init__(self):
        self.url_dict = {
            "台北_南港極限運動場": "https://cctv.bote.gov.taipei:8501/mjpeg/363",
            "台北_內湖極限公園": "https://cctv.bote.gov.taipei:8501/mjpeg/117",
            "台北_彩虹輪公園": "https://cctv.bote.gov.taipei:8501/mjpeg/053",
            "台北_大直美堤極限公園": "https://heocctv2.gov.taipei/channel68",
            "新北_永和綠寶石極限運動體驗場": "https://cctvatis3.ntpc.gov.tw/C000121",
            "台中": None,
            # "台中 拾七": "https://ocam.live/url.php?url=https%3A%2F%2Ftcnvr5.taichung.gov.tw%3A7001%2Fmedia%2F00-0F-7C-14-BE-F0.mpjpeg%3Fresolution%3D240p%26auth%3DcHVibGljdmlld2VyOjYxMGYyN2E2ZmVlZjA6ZTIxYzNjZTU4ZmUzMzAyYTdmMWM0YTJhMDkzY2ZiZjc",
            # "台中 高鐵": "https://ocam.live/url.php?url=https%3A%2F%2Ftcnvr5.taichung.gov.tw%3A7001%2Fmedia%2F00-1D-54-00-78-C6.mpjpeg%3Fresolution%3D240p%26auth%3DcHVibGljdmlld2VyOjYxMGYyODU5Mzk2NjA6NTg1NzFhODJkMGQ3MThkODMwM2MwZjRiN2ZlY2ZlNjk",
            # "台中 屋馬": "https://ocam.live/url.php?url=https%3A%2F%2Ftcnvr5.taichung.gov.tw%3A7001%2Fmedia%2F00-0F-7C-16-C9-AE.mpjpeg%3Fresolution%3D240p%26auth%3DcHVibGljdmlld2VyOjYxMGYyOGFiZWU0MDA6ZTk5NTZhMGYyNjEwMmVjODU1NzFmNmI1NzBkYmIwYTU",
            # "台中 豐富公園": "https://ocam.live/url.php?url=https%3A%2F%2Ftcnvr3.taichung.gov.tw%3A7001%2Fmedia%2F00-0F-7C-17-97-CA.mpjpeg%3Fresolution%3D240p%26auth%3DcHVibGljdmlld2VyOjYxMGYyOTc0ZTE1ZDg6MWY1OTFiOWZmNmNmYWQ2M2E1ZWRmYWNiZTZjZTVjYjk",
            # "台中_中正公園": "https://tcnvr3.taichung.gov.tw:7001/media/00-0F-7C-18-21-DC.mpjpeg?resolution=240p&auth=cHVibGljdmlld2VyOjYxMGYzYjI2ZDcwYjA6YjEzYmU3MGQ4YmFlMzk0NDIyOTZmNjk0ZGFkOWE5MzA"

        }
        self.url = "https://heocctv2.gov.taipei/channel68"

    def get_name_list(self):
        text = []
        for key, _value in self.url_dict.items():
            text.append(key)
        return text

    def get_image(self, location):
        if self.url_dict.get(location) is not None:
            print(location)
            self.url = self.url_dict[location]
        # Setup
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15"
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument(f'--user-agent={user_agent}')
        options.add_argument("window-size=720,640")
        options.page_load_strategy = 'none'
        driver = webdriver.Chrome(options=options)
        # Go to page
        driver.get(self.url)

        driver.get(self.url)

        # 等待一些時間以確保網頁加載完畢
        time.sleep(10)

        # 獲取當前網址，即含有token的URL
        current_url = driver.current_url
        logger.info("Current URL:"+ current_url)
        # Wait for a specific element to be present or a certain condition to be met
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/img')))

        # Stop loading page until response
        driver.execute_script('window.stop();')

        # Take a screenshot and save it in the folder
        image_b64 = driver.get_screenshot_as_base64()

        # Close the browser
        driver.close()
        return image_b64
