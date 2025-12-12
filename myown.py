from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time



option = webdriver.ChromeOptions()
option.add_argument("--user-data-dir=./whatsapp_session")
driver = webdriver.Chrome(options=option)
driver.maximize_window()


driver.get("https://web.whatsapp.com")

wait = WebDriverWait(driver, 60)

search_box = wait.until(EC.presence_of_element_located(By.XPATH,"//div[@contenteditable='true'][@data-tab='3']"))

search_box.click()
time.sleep(0.5)
search_box.send_keys("977 976-1445644")
time.sleep(2)
search_box.send_keys(Keys.ENTER)