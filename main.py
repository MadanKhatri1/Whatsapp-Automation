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

def save_sent_contact(phone_number):
    """Add a phone number to the sent contacts list."""
    sent_contacts = load_sent_contacts()
    if phone_number not in sent_contacts:
        sent_contacts.append(phone_number)
        with open(SENT_CONTACTS_FILE, 'w') as f:
            json.dump(sent_contacts, f, indent=2)
        print(f"  📝 Added to sent list: {phone_number}")

def load_sent_contacts():
    """Load the list of contacts that have already been sent messages."""
    if os.path.exists(SENT_CONTACTS_FILE):
        try:
            with open(SENT_CONTACTS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load sent contacts file: {e}")
            return []
    return []

def is_already_sent(phone_number):
    """Check if message was already sent to this contact."""
    sent_contacts = load_sent_contacts()
    return phone_number in sent_contacts

def save_progress(current_index, total_contacts, success_count, failed_count, failed_contacts):
    """Save current progress to file."""
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
    print(f"💾 Progress saved at contact {current_index}/{total_contacts}")

def load_progress():
    """Load previous progress if exists."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load progress file: {e}")
            return None
    return None

def extract_contacts_from_pdf(pdf_file):
    """
    Extract phone numbers from PDF file.
    
    Args:
        pdf_file (str): Path to PDF file
    
    Returns:
        list: List of phone numbers found in PDF
    """
    phone_numbers = []
    
    try:
        print(f"📄 Reading PDF file: {pdf_file}")
        
        with open(pdf_file, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print(f"   Pages in PDF: {total_pages}")
            
            # Extract text from all pages
            full_text = ""
            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                full_text += page.extract_text()
            
            # Find phone numbers using regex patterns
            patterns = [
                r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
                r'\d{10}',
                r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, full_text)
                for match in matches:
                    cleaned = re.sub(r'[-.\s()]', '', match)
                    if 8 <= len(cleaned) <= 15 and cleaned not in phone_numbers:
                        phone_numbers.append(cleaned)
            
            print(f"   ✓ Found {len(phone_numbers)} phone numbers")
            
            if phone_numbers:
                print(f"\n   First few numbers found:")
                for i, num in enumerate(phone_numbers[:5], 1):
                    print(f"   {i}. {num}")
                if len(phone_numbers) > 5:
                    print(f"   ... and {len(phone_numbers) - 5} more")
            
    except Exception as e:
        print(f"   ❌ Error reading PDF: {e}")
        import traceback
        traceback.print_exc()
    
    return phone_numbers


def clear_search_box(driver):
    """Helper function to reliably clear the search box."""
    try:
        # Press Escape to close any open dialogs
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.5)
        
        # Find and clear search box
        search_box = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
        search_box.click()
        time.sleep(0.3)
        
        # Clear the search box thoroughly
        for _ in range(3):
            search_box.send_keys(Keys.CONTROL + "a")
            time.sleep(0.1)
            search_box.send_keys(Keys.DELETE)
            time.sleep(0.1)
            search_box.send_keys(Keys.BACKSPACE)
            time.sleep(0.1)
        
        time.sleep(0.5)
    except Exception as e:
        print(f"   Warning: Could not clear search box: {e}")


def send_to_contact(driver, wait, phone_number, message=None, image_files=None, image_folder=None):
    """
    Send message and/or images to a single contact.
    """
    results = {'message_sent': False, 'images_sent': 0, 'error': None}
    
    # Search for contact
    try:
        # Use the more reliable search box selector
        search_box = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
        ))
        search_box.click()
        time.sleep(0.5)
        
        # Clear previous search
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.DELETE)
        time.sleep(0.3)
        
        search_box.send_keys(phone_number)
        time.sleep(2.5)
        
        # Press Enter to search/open the contact
        search_box.send_keys(Keys.ENTER)
        time.sleep(3)
        
        # Check if we're in a chat (message box exists)
        try:
            # Try to find the message box - if it appears, contact exists and chat is open
            msg_box_check = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
                )
            )
            # Contact found and chat opened successfully
        except TimeoutException:
            # Contact not found or chat didn't open
            results['error'] = "Contact not found in WhatsApp"
            clear_search_box(driver)
            return results
            
    except (TimeoutException, NoSuchElementException) as e:
        results['error'] = f"Search box error: {str(e)}"
        return results
    
    # Send text message if provided
    if message:
        try:
            msg_box = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
            ))
            msg_box.click()
            time.sleep(0.5)
            
            # Split message into lines and send properly
            lines = message.split('\n')
            for i, line in enumerate(lines):
                msg_box.send_keys(line)
                if i < len(lines) - 1:  # Not the last line
                    msg_box.send_keys(Keys.SHIFT + Keys.ENTER)
            
            time.sleep(0.5)
            msg_box.send_keys(Keys.ENTER)
            results['message_sent'] = True
            time.sleep(2)
        except Exception as e:
            results['error'] = f"Message failed: {str(e)}"
            return results
    
    # Send images if provided
    if image_files and image_folder:
        success_count = 0
        
        for image_file in image_files:
            image_path = os.path.abspath(os.path.join(image_folder, image_file))
            
            try:
                # Click attach button
                attach_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//div[@title='Attach']")
                ))
                attach_button.click()
                time.sleep(1.5)
                
                # Click "Photos & videos" option
                photo_video_option = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[@aria-label='Photos & videos']")
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
                    (By.XPATH, "//span[@data-icon='send']")
                ))
                send_button.click()
                success_count += 1
                time.sleep(4)
                
            except Exception as e:
                try:
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(1)
                except:
                    pass
                continue
        
        results['images_sent'] = success_count
    
    return results


def send_whatsapp_from_pdf(pdf_file, message, image_folder=None, start_index=0, end_index=None, resume=False):
    """
    Send messages and/or images to contacts from PDF file.
    
    Args:
        pdf_file (str): Path to PDF file containing phone numbers
        message (str): Message to send to all contacts
        image_folder (str, optional): Path to folder with images to send
        start_index (int): Contact index to start from (0-indexed, default: 0)
        end_index (int, optional): Contact index to end at (0-indexed, default: None = all)
        resume (bool): If True, resume from last saved progress
    """
    driver = None
    success_count = 0
    failed_count = 0
    failed_contacts = []
    skipped_count = 0
    
    try:
        print(f"\n{'='*60}")
        print(f"📊 WHATSAPP BULK SENDER - PDF MODE (WITH DUPLICATE CHECK)")
        print(f"{'='*60}")
        
        # Load list of already sent contacts
        sent_contacts = load_sent_contacts()
        print(f"📋 Already sent to {len(sent_contacts)} contacts")
        
        # Extract phone numbers from PDF
        phone_numbers = extract_contacts_from_pdf(pdf_file)
        
        if not phone_numbers:
            print("❌ No phone numbers found in PDF!")
            return False
        
        # Check for previous progress
        previous_progress = load_progress()
        if resume and previous_progress:
            print(f"\n🔄 Found previous progress:")
            print(f"   Last processed: Contact {previous_progress['current_index']}/{previous_progress['total_contacts']}")
            print(f"   Success: {previous_progress['success_count']}, Failed: {previous_progress['failed_count']}")
            print(f"   Timestamp: {previous_progress['timestamp']}")
            
            use_progress = input("\n   Resume from this point? (yes/no): ").strip().lower()
            if use_progress == 'yes':
                start_index = previous_progress['current_index']
                success_count = previous_progress['success_count']
                failed_count = previous_progress['failed_count']
                failed_contacts = previous_progress['failed_contacts']
                print(f"   ✓ Resuming from contact #{start_index + 1}")
        
        # Filter by index range
        if end_index is not None:
            phone_numbers_to_process = phone_numbers[start_index:end_index]
        else:
            phone_numbers_to_process = phone_numbers[start_index:]
        
        total_contacts = len(phone_numbers_to_process)
        print(f"\n✓ Will process {total_contacts} contacts (from index {start_index})")
        print(f"📝 Message: \"{message[:50]}...\"" if len(message) > 50 else f"📝 Message: \"{message}\"")
        
        # Get image files if folder provided
        image_files = None
        if image_folder and os.path.exists(image_folder):
            image_files = [f for f in os.listdir(image_folder) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            print(f"📸 Found {len(image_files)} images to send")
        
        print(f"{'='*60}\n")
        
        # Ask for confirmation
        print(f"⚠️  You are about to send messages to {total_contacts} contacts.")
        confirm = input("Type 'yes' to continue: ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelled by user.")
            return False
        
        # Initialize Chrome driver
        print("\n🔧 Initializing Chrome driver...")
        options = webdriver.ChromeOptions()
        options.add_argument("--user-data-dir=./whatsapp_session")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        
        # Open WhatsApp Web
        print("🌐 Opening WhatsApp Web...")
        driver.get("https://web.whatsapp.com")
        
        print("📱 Please scan the QR code if prompted...")
        wait = WebDriverWait(driver, 60)
        
        # Wait for WhatsApp to load
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
            ))
            print("✓ WhatsApp Web loaded successfully!\n")
        except TimeoutException:
            print("❌ Timeout: Could not load WhatsApp Web.")
            return False
        
        time.sleep(2)
        
        # Process each contact
        for idx, phone in enumerate(phone_numbers_to_process, 1):
            actual_index = start_index + idx - 1
            print(f"\n[{actual_index + 1}/{len(phone_numbers)}] Processing: {phone}")
            
            # Check if already sent
            if is_already_sent(phone):
                print(f"  ⏭️  SKIPPED - Already sent to this number")
                skipped_count += 1
                continue
            
            try:
                results = send_to_contact(
                    driver, wait, phone,
                    message=message,
                    image_files=image_files,
                    image_folder=image_folder
                )
                
                if results['error']:
                    print(f"  ✗ Failed: {results['error']}")
                    failed_count += 1
                    failed_contacts.append({'phone': phone, 'error': results['error']})
                    print(f"  ⏭️  Skipping to next contact...")
                else:
                    msg_status = "✓" if results['message_sent'] else "✗"
                    img_status = f"{results['images_sent']} images" if image_files else "N/A"
                    print(f"  ✓ Success - Message: {msg_status}, Images: {img_status}")
                    success_count += 1
                    # Add to sent list
                    save_sent_contact(phone)
                
                # Save progress after each contact
                save_progress(actual_index + 1, len(phone_numbers), success_count, failed_count, failed_contacts)
                
            except Exception as e:
                print(f"  ❌ Unexpected error: {str(e)}")
                failed_count += 1
                failed_contacts.append({'phone': phone, 'error': str(e)})
                save_progress(actual_index + 1, len(phone_numbers), success_count, failed_count, failed_contacts)
                print(f"  ⏭️  Skipping to next contact...")
                continue
            
            # Small delay between contacts
            if idx < total_contacts:
                time.sleep(3)
            
            # Progress update every 10 contacts
            if idx % 10 == 0:
                print(f"\n📊 Progress: {actual_index + 1}/{len(phone_numbers)} processed ({success_count} success, {failed_count} failed, {skipped_count} skipped)")
        
        # Final summary
        print(f"\n\n{'='*60}")
        print(f"📊 FINAL SUMMARY")
        print(f"{'='*60}")
        print(f"Total in range: {total_contacts}")
        print(f"⏭️  Skipped (already sent): {skipped_count}")
        print(f"✓ Successful: {success_count}")
        print(f"✗ Failed: {failed_count}")
        total_attempted = success_count + failed_count
        if total_attempted > 0:
            print(f"Success rate: {(success_count/total_attempted*100):.1f}%")
        print(f"📝 Total unique contacts sent: {len(load_sent_contacts())}")
        print(f"{'='*60}")
        
        # Save failed contacts to file
        if failed_contacts:
            failed_df = pd.DataFrame(failed_contacts)
            failed_file = 'failed_contacts.csv'
            failed_df.to_csv(failed_file, index=False)
            print(f"\n⚠ Failed contacts saved to: {failed_file}")
        
        # Save all extracted numbers to CSV
        all_numbers_df = pd.DataFrame({'Phone': phone_numbers})
        all_numbers_file = 'extracted_numbers.csv'
        all_numbers_df.to_csv(all_numbers_file, index=False)
        print(f"📋 All extracted numbers saved to: {all_numbers_file}")
        
        # Save sent contacts list
        sent_df = pd.DataFrame({'Phone': load_sent_contacts()})
        sent_file = 'sent_contacts_list.csv'
        sent_df.to_csv(sent_file, index=False)
        print(f"✅ Sent contacts list saved to: {sent_file}")
        
        # Delete progress file on successful completion
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
            print(f"✓ Progress file cleared (job complete)")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Save progress before exiting
        if 'actual_index' in locals():
            save_progress(actual_index, len(phone_numbers), success_count, failed_count, failed_contacts)
            print(f"\n💾 Progress saved. Run with resume=True to continue from contact #{actual_index + 1}")
        
        return False
    
    finally:
        if driver:
            print("\n⏳ Keeping browser open for 10 seconds for verification...")
            time.sleep(10)
            driver.quit()
            print("✓ Browser closed.")


# Usage
if __name__ == "__main__":
    # Configuration
    pdf_file = "contacts.pdf"
    message = ""
    image_folder = "images/"
    
    # OPTION 1: Resume from where it crashed (automatically)
    
    send_whatsapp_from_pdf(
        pdf_file=pdf_file,
        message=message,
        image_folder=image_folder,
        resume=True  # This will prompt to resume from last crash
    )
    
    
    # OPTION 2: Start from specific person (e.g., person 193)
    """
    send_whatsapp_from_pdf(
        pdf_file=pdf_file,
        message=message,
        image_folder=image_folder,
        start_index=192,  # Person 193 (0-indexed, so 192)
        resume=False
    )
    """
    