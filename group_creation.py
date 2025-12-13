from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import PyPDF2
import re
import os
import time

# --- CONFIGURATION ---
PDF_FILE = "contact.pdf"
GROUP_NAME_PREFIX = "Community Update Group"
BATCH_SIZE = 1
MESSAGE_TO_SEND = "Welcome to the Community Update Group!"
IMAGE_FOLDER = "images"
IMAGE_FILES = ["image_2.jpg"]

def initialize_chrome_driver():
    print("🔧 Initializing Chrome driver...")
    options = webdriver.ChromeOptions()
    user_data_dir = os.path.abspath("whatsapp_session")
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu") 
    
    driver = webdriver.Chrome(options=options)
    return driver

def extract_contacts_from_pdf(pdf_file):
    phone_numbers = []
    try:
        print(f"📄 Reading PDF file: {pdf_file}")
        with open(pdf_file, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            full_text = ""
            for page in pdf_reader.pages:
                full_text += page.extract_text()
            
            patterns = [r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}', r'\d{10}']
            for pattern in patterns:
                matches = re.findall(pattern, full_text)
                for match in matches:
                    cleaned = re.sub(r'[-.\s()]', '', match)
                    if 8 <= len(cleaned) <= 15 and cleaned not in phone_numbers:
                        phone_numbers.append(cleaned)
        print(f"  ✓ Found {len(phone_numbers)} phone numbers")
    except Exception as e:
        print(f"  ❌ Error reading PDF: {e}")
    return phone_numbers

def search_and_open_group(driver, wait, group_name):
    """Specifically searches for the group and uses ENTER to open it."""
    print(f"🔍 Searching for group: {group_name}")
    try:
        # 1. Locate search bar using your existing logic/context
        search_box = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id='side']/div[1]/div/div[2]/div/div/div[1]/p")
        ))
        search_box.click()
        time.sleep(1)
        
        # 2. Clear and Type
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.BACKSPACE)
        time.sleep(0.5)
        
        for char in group_name:
            search_box.send_keys(char)
            time.sleep(0.05)
        
        time.sleep(3) # Let search results populate
        
        # 3. Press Enter to open the first result (Fixes the 'closing' issue)
        search_box.send_keys(Keys.ENTER)
        time.sleep(3)
        return True
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False

def send_message_and_images(driver, wait, group_name, message_text=None, image_files=None, image_folder=None):
    print(f"\n📤 Sending content to group: {group_name}")
    results = {'message_sent': False, 'images_sent': 0}
    
    try:
        print("    ⏳ Waiting for chat to stabilize...")
        time.sleep(5)
        
        # Send text message (Your original XPATHs)
        if message_text:
            print("    💬 Sending text message...")
            message_box = None
            for attempt in range(5):
                try:
                    message_box = wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//*[@id='main']/footer/div[1]/div/span/div/div/div/div[3]/div[1]")
                    ))
                    break
                except:
                    print(f"      ⏳ Attempt {attempt + 1}/5 to find message box...")
                    time.sleep(2)
            
            if message_box:
                message_box.click()
                time.sleep(1)
                message_box.send_keys(message_text)
                time.sleep(0.5)
                message_box.send_keys(Keys.ENTER)
                results['message_sent'] = True
                print("    ✅ Message sent successfully")
                time.sleep(3)

        # Send images (Your original XPATHs)
        if image_files and image_folder:
            print(f"    🖼️ Sending {len(image_files)} images...")
            success_count = 0
            for image_file in image_files:
                image_path = os.path.abspath(os.path.join(image_folder, image_file))
                if not os.path.exists(image_path): continue
                try:
                    attach_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div/div/div[1]/div/span/button')))
                    attach_button.click()
                    time.sleep(2)
                    photo_video_option = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/span[6]/div/ul/div/div/div[2]/li/div')))
                    photo_video_option.click()
                    time.sleep(1.5)
                    file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@accept='image/*,video/mp4,video/3gpp,video/quicktime']")))
                    file_input.send_keys(image_path)
                    time.sleep(4)
                    send_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[3]/div/div[3]/div[2]/div/span/div/div/div/div[2]/div/div[2]/div[2]/span/div/div')))
                    send_button.click()
                    success_count += 1
                    time.sleep(5)
                except: pass
            results['images_sent'] = success_count
    except Exception as e:
        print(f"    ❌ Error: {e}")
    return results

def create_single_group(driver, wait, batch_contacts, group_name):
    # This remains exactly as your working version
    print(f"\n🔨 Creating Group: {group_name}...")
    try:
        new_chat_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='app']/div/div/div[3]/div/div[4]/header/header/div/span/div/div[2]/span/button")))
        new_chat_btn.click()
        time.sleep(2)
        new_group_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='app']/div/div/span[6]/div/ul/div/div[1]/li/div")))
        new_group_btn.click()
        time.sleep(3)
        input_box = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='app']/div/div/div[3]/div/div[3]/div[1]/div/span/div/span/div/div/div[1]/div/div/div[2]/input")))
        
        added_count = 0
        for phone in batch_contacts:
            input_box.send_keys(phone)
            time.sleep(2)
            try:
                driver.find_element(By.XPATH, "//*[contains(text(), 'No results found')]")
                input_box.send_keys(Keys.CONTROL + "a", Keys.DELETE)
            except NoSuchElementException:
                input_box.send_keys(Keys.ENTER)
                added_count += 1
                time.sleep(0.5)
        
        if added_count == 0: return False
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='app']/div/div/div[3]/div/div[3]/div[1]/div/span/div/span/div/div/span/div/div"))).click()
        time.sleep(2)
        subject_box = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='app']/div/div/div[3]/div/div[3]/div[1]/div/span/div/span/div/div/div[1]/div[2]/div/div[2]/div[1]/div/div/p")))
        subject_box.send_keys(group_name)
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='app']/div/div/div[3]/div/div[3]/div[1]/div/span/div/span/div/div/div[3]/div/div/div[1]/div/h3/span"))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='app']/div/div/div[3]/div/div[3]/div[1]/div/span/div/span/div/div/div[2]/div[2]/div/div/div/div[1]/div[3]/div/input"))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='app']/div/div/div[3]/div/div[3]/div[1]/div/span/div/span/div/header/div/div[1]/div/span/button/div/div/div[1]/span"))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='app']/div/div/div[3]/div/div[3]/div[1]/div/span/div/span/div/div/span/div/div/div"))).click()
        time.sleep(10)
        return True
    except: return False

def main_group_creator():
    phone_numbers = extract_contacts_from_pdf(PDF_FILE)
    if not phone_numbers: return
    batches = [phone_numbers[i:i + BATCH_SIZE] for i in range(0, len(phone_numbers), BATCH_SIZE)]
    driver = initialize_chrome_driver()
    driver.get("https://web.whatsapp.com")
    wait = WebDriverWait(driver, 300)
    
    # Initial Wait
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")))
    
    for i, batch in enumerate(batches):
        group_name = f"{GROUP_NAME_PREFIX}"
        
        # 1. Create the Group
        if create_single_group(driver, wait, batch, group_name):
            
            # 2. REFRESH TO PREVENT CRASH
            print("🔄 Refreshing page to clear memory and prevent crash...")
            driver.refresh()
            
            # 3. Wait for reload
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")))
            time.sleep(5)
            
            # 4. Search and Open the Group
            if search_and_open_group(driver, wait, group_name):
                # 5. Send Content
                send_message_and_images(driver, wait, group_name, MESSAGE_TO_SEND, IMAGE_FILES, IMAGE_FOLDER)
        
        if i < len(batches) - 1:
            print("⏳ 60s Batch Cooldown...")
            time.sleep(60)

    driver.quit()

if __name__ == "__main__":
    main_group_creator()