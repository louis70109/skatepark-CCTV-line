from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = 'https://heocctv2.gov.taipei/channel68'

# Setup
options = Options()
options.add_argument("--headless=new")
options.page_load_strategy = 'none'
driver = webdriver.Chrome(options=options)

# Go to page
driver.get(url)

# Wait for a specific element to be present or a certain condition to be met
# Adjust the timeout and other parameters according to your needs
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/img')))

# Stop loading page until response
driver.execute_script('window.stop();')

# Take a screenshot and save it in the folder
driver.save_screenshot('save.png')

# Close the browser
driver.close()
