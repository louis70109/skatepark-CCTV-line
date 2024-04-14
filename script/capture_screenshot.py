from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

url = 'https://www.youtube.com/watch?v=vPCkonkRRY0'

# Setup
options = Options()
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
driver.get(url)

# 等待一些時間以確保網頁加載完畢
time.sleep(10)

# 獲取當前網址，即含有token的URL
current_url = driver.current_url
print("Current URL:"+ current_url)
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
print(image_b64)