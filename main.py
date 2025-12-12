from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import PyPDF2
import re
import os
import time
import json

# Progress tracking file
PROGRESS_FILE = "whatsapp_progress.json"
SENT_CONTACTS_FILE = "sent_contacts.json"

def initialize_chrome_driver():
    """Initialize Chrome driver with robust options."""
    print("🔧 Initializing Chrome driver...")
    
    options = webdriver.ChromeOptions()
    user_data_dir = os.path.abspath("whatsapp_session")
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"❌ Failed to initialize Chrome: {e}")
        raise

def save_sent_contact(phone_number):
    sent_contacts = load_sent_contacts()
    if phone_number not in sent_contacts:
        sent_contacts.append(phone_number)
        with open(SENT_CONTACTS_FILE, 'w') as f:
            json.dump(sent_contacts, f, indent=2)

def load_sent_contacts():
    if os.path.exists(SENT_CONTACTS_FILE):
        try:
            with open(SENT_CONTACTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def is_already_sent(phone_number):
    return phone_number in load_sent_contacts()

def save_progress(current_index, total_contacts, success_count, failed_count, failed_contacts):
    progress_data = {
        'current_index': current_index,
        'total_contacts': total_contacts,
        'success_count': success_count,
        'failed_count': failed_count,
        'failed_contacts': failed_contacts,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress_data, f, indent=2)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

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

def clear_search_box_robust(driver):
    """
    FIX: Clears search box AND presses Escape to close previous chat.
    This prevents sending messages to the wrong person.
    """
    try:
        # Press Escape multiple times to close any open chat or search
        # This ensures we don't accidentally type in the previous person's chat
        actions = ActionChains(driver)
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(0.5)
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(0.5)
    except:
        pass

def send_to_contact(driver, wait, phone_number, message=None, image_files=None, image_folder=None):
    results = {'message_sent': False, 'images_sent': 0, 'error': None}
    
    # ==========================================
    # STEP 1: SAFE SEARCH (THE FIX)
    # ==========================================
    try:
        # 1. Clear everything first (Close previous chat)
        clear_search_box_robust(driver)
        
        # 2. Find Search Box
        search_box = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
        ))
        search_box.click()
        
        # 3. Clear and Type Number
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.DELETE)
        time.sleep(0.5)
        search_box.send_keys(phone_number)
        
        # 4. CRITICAL FIX: Wait and check for "No results found"
        time.sleep(2.0)
        try:
            # Check if WhatsApp says "No results found"
            no_results = driver.find_elements(By.XPATH, "//*[contains(text(), 'No results found') or contains(text(), 'no results found')]")
            if len(no_results) > 0:
                results['error'] = "Contact not found (No results)"
                # Clean up: clear search and escape
                search_box.send_keys(Keys.CONTROL + "a")
                search_box.send_keys(Keys.DELETE)
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                return results
        except:
            pass
            
        # 5. Press Enter to open chat
        search_box.send_keys(Keys.ENTER)
        time.sleep(3) # Wait for chat to load
        
        # 6. Verify Chat is Open (Message box exists)
        # If we are still on the "WhatsApp Web" home screen, the message box won't be there
        try:
            msg_box_check = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
        except NoSuchElementException:
            results['error'] = "Chat failed to open"
            return results

    except Exception as e:
        results['error'] = f"Search error: {str(e)}"
        return results

    # ==========================================
    # STEP 2: SEND MESSAGE (PRESERVED)
    # ==========================================
    if message:
        try:
            msg_box = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
            ))
            msg_box.click()
            time.sleep(0.5)
            
            lines = message.split('\n')
            for i, line in enumerate(lines):
                msg_box.send_keys(line)
                if i < len(lines) - 1:
                    msg_box.send_keys(Keys.SHIFT + Keys.ENTER)
            
            time.sleep(0.5)
            msg_box.send_keys(Keys.ENTER)
            results['message_sent'] = True
            time.sleep(2)
        except Exception as e:
            results['error'] = f"Message failed: {str(e)}"
            return results

    # ==========================================
    # STEP 3: SEND IMAGES (YOUR EXACT CODE)
    # ==========================================
    if image_files and image_folder:
        success_count = 0
        for image_file in image_files:
            image_path = os.path.abspath(os.path.join(image_folder, image_file))
            try:
                # YOUR CODE STARTS HERE
                # Click attach button
                attach_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div/div/div[1]/div/span/button')
                ))
                attach_button.click()
                time.sleep(1.5)
                
                # Click "Photos & videos" option
                photo_video_option = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="app"]/div/div/span[6]/div/ul/div/div/div[2]/li/div')
                ))
                photo_video_option.click()
                time.sleep(1)
                
                # Upload image
                file_input = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[@accept='image/*,video/mp4,video/3gpp,video/quicktime']")
                ))
                file_input.send_keys(image_path)
                time.sleep(3)
                
                # Click send button
                send_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="app"]/div/div/div[3]/div/div[3]/div[2]/div/span/div/div/div/div[2]/div/div[2]/div[2]/span/div/div')
                ))
                # YOUR CODE ENDS HERE
                
                send_button.click()
                success_count += 1
                time.sleep(4)
                
            except Exception as e:
                print(f"    Image error: {e}")
                try:
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                except:
                    pass
                continue
        
        results['images_sent'] = success_count

    return results

def send_whatsapp_from_pdf(pdf_file, message, image_folder=None, start_index=0, resume=False):
    """Main execution function."""
    driver = None
    success_count = 0
    failed_count = 0
    
    try:
        print("🚀 WHATSAPP BULK SENDER STARTING...")
        phone_numbers = extract_contacts_from_pdf(pdf_file)
        
        if not phone_numbers:
            return False

        # Resume logic
        if resume:
            previous_progress = load_progress()
            if previous_progress:
                start_index = previous_progress['current_index']
                print(f"🔄 Resuming from index {start_index}")

        # Filter contacts
        contacts_to_process = phone_numbers[start_index:]
        
        # Prepare images
        image_files = []
        if image_folder and os.path.exists(image_folder):
            image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        # Init Driver
        driver = initialize_chrome_driver()
        driver.get("https://web.whatsapp.com")
        print("📱 Please Scan QR Code...")
        wait = WebDriverWait(driver, 300)
        
        # Wait for load
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")))
        print("✅ WhatsApp Loaded!")
        
        for idx, phone in enumerate(contacts_to_process, 1):
            actual_index = start_index + idx - 1
            print(f"\n[{actual_index + 1}/{len(phone_numbers)}] Processing: {phone}")

            if is_already_sent(phone):
                print("  ⏭️  Skipped (Already sent)")
                continue

            results = send_to_contact(driver, wait, phone, message, image_files, image_folder)
            
            if results['error']:
                print(f"  ❌ Failed: {results['error']}")
                failed_count += 1
            else:
                print(f"  ✅ Sent successfully")
                success_count += 1
                save_sent_contact(phone)

            save_progress(actual_index + 1, len(phone_numbers), success_count, failed_count, [])
            
            # --- 1 HOUR WAIT LOGIC (UPDATED TO 100) ---
            # If we have processed 100 contacts in this session, pause for 1 hour
            if idx > 0 and idx % 100 == 0 and idx < len(contacts_to_process):
                print("\n" + "="*50)
                print(f"⏳ 100 MESSAGES SENT. PAUSING FOR 1 HOUR.")
                print(f"   Current Time: {time.strftime('%H:%M:%S')}")
                print(f"   Will resume at: {time.strftime('%H:%M:%S', time.localtime(time.time() + 3600))}")
                print("="*50 + "\n")
                time.sleep(7200)  # Sleep for 3600 seconds (1 Hour)
            else:
                # Normal short delay between messages
                time.sleep(2)

    except Exception as e:
        print(f"❌ Critical Error: {e}")
    finally:
        if driver:
            time.sleep(5)
            driver.quit()

if __name__ == "__main__":
    pdf_file = "contacts.pdf"
    message = """कल्पना वाईबा 
महाधिवेशन  प्रतिनिधि - युवा विद्यार्थी"""   
    image_folder = "images/"
    
    send_whatsapp_from_pdf(
        pdf_file=pdf_file,
        message=message,
        image_folder=image_folder,
        resume=True
    )