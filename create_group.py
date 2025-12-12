from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ---- SETTINGS ----
GROUP_NAME = "My Automated Group"
MEMBERS = ["Friend1", "Friend2"]  # contact names in your WhatsApp

# ---- OPEN BROWSER ----
service = Service("chromedriver")  # path to chromedriver
driver = webdriver.Chrome(service=service)
driver.get("https://web.whatsapp.com")

print("Scan the QR code...")
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, "//div[@id='pane-side']"))
)
print("Logged in successfully!")

# ---- CLICK NEW CHAT BUTTON ----
new_chat_btn = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//div[@title='New chat']"))
)
new_chat_btn.click()

# ---- CLICK NEW GROUP ----
new_group_btn = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//div[@title='New group']"))
)
new_group_btn.click()

# ---- ADD MEMBERS ----
for member in MEMBERS:
    search_box = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@role='textbox']"))
    )
    search_box.clear()
    search_box.send_keys(member)
    time.sleep(1)

    # select contact from list
    person = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f"//span[@title='{member}']"))
    )
    person.click()

# ---- CLICK NEXT ----
next_btn = driver.find_element(By.XPATH, "//span[@data-icon='arrow-forward']")
next_btn.click()

# ---- SET GROUP NAME ----
group_name_box = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']"))
)
group_name_box.send_keys(GROUP_NAME)

# ---- CREATE GROUP ----
create_btn = driver.find_element(By.XPATH, "//span[@data-icon='checkmark']")
create_btn.click()

print("Group created successfully!")
