import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class SkateParkImage:
    def __init__(self):
        self.url_dict = {
            "南港極限運動場": "https://cctv.bote.gov.taipei:8501/mjpeg/363",
            "內湖極限公園": "https://cctv.bote.gov.taipei:8501/mjpeg/117",
            "大直美堤極限公園": "https://heocctv2.gov.taipei/channel68",
            "永和綠寶石極限運動體驗場": "https://cctvatis3.ntpc.gov.tw/C000121"
        }
        self.url = "大直美堤極限公園"
    
    def get_name_list(self):
        text = []
        for key, _value in self.url_dict.items():
            text.append(key)
        return text
    
    def get_image(self, location):
        if self.url_dict.get(location) != None:
            self.url = self.url_dict[location]
        # Setup
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("window-size=1024,768")
        options.page_load_strategy = 'none'
        driver = webdriver.Chrome(options=options)

        # Go to page
        driver.get(self.url)

        driver.get(self.url)

        # 等待一些時間以確保網頁加載完畢
        time.sleep(10)

        # 獲取當前網址，即含有token的URL
        current_url = driver.current_url
        print("Current URL:", current_url)
        # Wait for a specific element to be present or a certain condition to be met
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/img')))

        # Stop loading page until response
        driver.execute_script('window.stop();')

        # Take a screenshot and save it in the folder
        image_b64 = driver.get_screenshot_as_base64()
        
        # Close the browser
        driver.close()
        return image_b64
