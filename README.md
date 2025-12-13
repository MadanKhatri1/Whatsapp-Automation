# 🚀 WhatsApp Automation Suite

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-WebDriver-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A powerful and intelligent **WhatsApp Web automation toolkit** built with Python and Selenium WebDriver. This project enables bulk messaging with advanced features like session persistence, progress tracking, and error recovery.

## ✨ Key Features

### 📨 Bulk Messaging System
- **PDF Contact Extraction**: Automatically extracts phone numbers from PDF files using regex patterns
- **Smart Message Sending**: Send personalized text messages to hundreds of contacts
- **Image Attachment Support**: Bulk send images (JPG, PNG, JPEG) along with messages
- **Multi-line Message Support**: Preserve formatting with line breaks using Shift+Enter

### 👥 Group Creation Automation
- **Bulk Group Creation**: Create multiple WhatsApp groups automatically
- **Batch Member Addition**: Add contacts to groups in configurable batches
- **Welcome Messaging**: Automatically send welcome messages and images to new groups
- **Crash Prevention**: Smart refresh logic to manage memory usage during large batch operations

### 🔄 Advanced Progress Management
- **Resume Capability**: Pause and resume campaigns without losing progress
- **Duplicate Prevention**: Tracks sent contacts to avoid duplicate messages
- **Real-time Progress Tracking**: JSON-based progress logging with timestamps
- **Failed Contact Tracking**: Identifies and logs contacts that couldn't be reached

### 🛡️ Robust Error Handling
- **Contact Validation**: Detects "No results found" errors before sending
- **Chat Verification**: Ensures chat window opens successfully before message dispatch
- **Safe Search Method**: Clears previous chats using ESC key to prevent wrong-recipient errors
- **Graceful Fallback**: Continues operation even if individual contacts fail

### 💾 Session Persistence
- **QR Code Once**: Scan QR code only on first run
- **Session Retention**: Stores WhatsApp Web session for repeated use
- **Anti-Detection**: Configured to avoid automation detection by WhatsApp

## 📋 Table of Contents

- [Installation](#-installation)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [Configuration](#%EF%B8%8F-configuration)
- [Features Deep Dive](#-features-deep-dive)
- [Troubleshooting](#-troubleshooting)
- [Best Practices](#-best-practices)
- [Contributing](#-contributing)
- [License](#-license)

## 🔧 Installation

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
- **Google Chrome** - Latest version recommended

### Step 1: Clone the Repository

```bash
git clone https://github.com/MadanKhatri1/WhatsApp-Automation.git
cd WhatsApp-Automation
```

### Step 2: Install Dependencies

```bash
pip install selenium pandas PyPDF2 fpdf
```

**Required Python packages:**
- `selenium` - Web automation framework
- `pandas` - Data manipulation (optional, for advanced contact management)
- `PyPDF2` - PDF parsing for contact extraction
- `fpdf` - PDF generation for creating sample contact lists


## 🚀 Quick Start

### 1. Prepare Your Contacts

Create a PDF file (`contacts.pdf`) containing phone numbers. The script supports multiple formats:
- `+977-9812345678`
- `9812345678`
- `+1 (555) 123-4567`

Example PDF content:
```
Contact List:
+977-9812345678
9876543210
+91 9988776655
```

### 2. Add Images (Optional)

Place images you want to send in the `images/` folder:
```
images/
├── image_1.jpg
├── image_2.jpg
└── banner.png
```

### 3. Run the Main Script

```bash
python main.py
```

#### First-time Setup:
1. A Chrome window will open with WhatsApp Web
2. **Scan the QR code** with your phone
3. Wait for WhatsApp to load
4. Script will start sending messages automatically

#### Subsequent Runs:
- Session is saved, no QR scan needed
- Script starts immediately

## 📖 Usage Guide

### Bulk Messaging with Images

```python
from main import send_whatsapp_from_pdf

# Configure your campaign
pdf_file = "contacts.pdf"
message = """Hello! 👋
This is an automated message.
Visit our website for more info."""
image_folder = "images/"

# Start sending
send_whatsapp_from_pdf(
    pdf_file=pdf_file,
    message=message,
    image_folder=image_folder,
    resume=True  # Enable resume functionality
)
```

### Text-Only Messages

```python
send_whatsapp_from_pdf(
    pdf_file="contacts.pdf",
    message="Simple text message",
    resume=True
)
```

### Resume Interrupted Campaign

```python
# If script stopped midway, just run again with resume=True
send_whatsapp_from_pdf(
    pdf_file="contacts.pdf",
    message="Your message",
    resume=True  # Automatically resumes from last checkpoint
)
```

### Create WhatsApp Group

```python
# Edit group_creation.py with your details
GROUP_NAME_PREFIX = "Community Update Group"
MESSAGE_TO_SEND = "Welcome!"

# Run the script
python group_creation.py
```

### Generate Sample Contacts PDF

```python
# Run the script to create a sample contact.pdf
python create_pdf.py
```

## 📁 Project Structure

```
WhatsApp-Automation/
├── main.py                    # Main bulk messaging script
├── group_creation.py          # Group creation automation
├── create_pdf.py              # Helper to generate sample PDF contacts
├── contact.pdf                # Generated contact list
├── contacts.pdf               # Contact list input (your data)
├── images/                    # Images to send
│   ├── image_1.jpg
│   └── image_2.jpg
├── whatsapp_session/          # Browser session storage (auto-created)
├── whatsapp_progress.json     # Progress tracking (auto-created)
├── sent_contacts.json         # Sent contacts log (auto-created)
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## ⚙️ Configuration

### Chrome Driver Options

The script uses these Chrome options for stability:

```python
options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={user_data_dir}")  # Session persistence
options.add_argument("--no-sandbox")                       # Linux compatibility
options.add_argument("--disable-dev-shm-usage")            # Prevent crashes
options.add_argument("--disable-gpu")                      # Stability
options.add_argument("--start-maximized")                  # Full window
options.add_argument("--disable-notifications")            # No popups
options.add_experimental_option("excludeSwitches", ["enable-automation"])
```

### Customizing Wait Times

Adjust timing in `main.py` for different network speeds:

```python
# Search wait time (line 145)
time.sleep(2.0)  # Increase for slower connections

# Chat load wait (line 161)
time.sleep(3)    # Increase if chats load slowly

# Message send wait (line 195)
time.sleep(2)    # Wait after sending message

# Image send wait (line 238)
time.sleep(4)    # Wait after sending image
```

### Phone Number Regex Patterns

Modify patterns in `extract_contacts_from_pdf()` to match your region:

```python
patterns = [
    r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
    r'\d{10}'  # 10-digit numbers
]
```

## 🔍 Features Deep Dive

### 1. PDF Contact Extraction

**How it works:**
- Opens PDF using `PyPDF2`
- Extracts all text from all pages
- Uses regex patterns to find phone numbers
- Cleans and validates numbers (8-15 digits)
- Removes duplicates

**Supported formats:**
- ✅ `+977-9812345678`
- ✅ `9812345678`
- ✅ `+1 (555) 123-4567`
- ✅ `555.123.4567`

### 2. Progress Tracking System

**Progress File (`whatsapp_progress.json`):**
```json
{
  "current_index": 45,
  "total_contacts": 100,
  "success_count": 42,
  "failed_count": 3,
  "failed_contacts": [],
  "timestamp": "2024-12-12 19:30:45"
}
```

**Sent Contacts File (`sent_contacts.json`):**
```json
[
  "9812345678",
  "9876543210"
]
```

### 3. Safe Search Method

**Problem Solved:** Previous versions would sometimes send messages to the wrong contact if the search box wasn't cleared properly.

**Solution:**
1. Press `ESC` multiple times to close any open chat
2. Clear search box completely
3. Type new phone number
4. Verify "No results found" doesn't appear
5. Press Enter to open chat
6. Verify message box exists before sending

### 4. Image Attachment Workflow

**Standard WhatsApp Web XPath selectors:**
1. Attach button: Click to open attachment menu
2. Photos & Videos option: Select media type
3. File input: Upload image file
4. Send button: Dispatch the image

**Process:**
- Supports: `.jpg`, `.jpeg`, `.png`
- Sends images one by one
- 4-second wait between images
- Error recovery with ESC key

### 5. Session Management

**First Run:**
- Creates `whatsapp_session/` directory
- Opens WhatsApp Web
- User scans QR code
- Session is saved in browser profile

**Subsequent Runs:**
- Loads saved session
- No QR scan needed
- Instant login

## 🐛 Troubleshooting

### Issue: "ChromeDriver version mismatch"

**Solution:**
```bash
# Check your Chrome version
google-chrome --version

# Download matching ChromeDriver
# Visit: https://chromedriver.chromium.org/downloads
```

### Issue: "Contact not found" for valid numbers

**Causes:**
- Contact not saved in your WhatsApp
- Number format doesn't match WhatsApp's expectations
- Network delay

**Solutions:**
1. Ensure contacts are saved in your phone
2. Try different number formats: `+977XXXXXXXXXX` vs `XXXXXXXXXX`
3. Increase wait time in line 145: `time.sleep(3.0)`

### Issue: Messages sent to wrong person

**Fix:** This was addressed in the `clear_search_box_robust()` function. If still occurring:
1. Increase ESC key presses in line 115-118
2. Add longer delays between operations

### Issue: Script crashes on Linux

**Common Cause:** Shared memory issues

**Solution:**
```python
# Already included in code:
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
```

### Issue: Images not sending

**Checklist:**
- ✅ Images exist in `images/` folder
- ✅ File extensions are `.jpg`, `.jpeg`, or `.png`
- ✅ Image paths are correct
- ✅ Sufficient wait time (4 seconds)
- ✅ Internet connection stable

**Debug:**
```python
# Add print statements
print(f"Attempting to send: {image_path}")
print(f"File exists: {os.path.exists(image_path)}")
```

### Issue: Session keeps expiring

**Solutions:**
1. Don't open WhatsApp Web in another browser
2. Don't logout from WhatsApp Web manually
3. Ensure `whatsapp_session/` folder isn't deleted
4. Check folder permissions

### Issue: "selenium.common.exceptions.TimeoutException"

**Causes:**
- Slow internet connection
- WhatsApp Web UI changes
- Element not loading

**Solutions:**
1. Increase WebDriverWait timeout:
   ```python
   wait = WebDriverWait(driver, 600)  # 10 minutes
   ```
2. Check WhatsApp Web is accessible in normal browser
3. Update Selenium: `pip install --upgrade selenium`

## ✅ Best Practices

### 1. Respect WhatsApp's Limits

- **Don't spam**: Add delays between messages (configured at 2-4 seconds)
- **Avoid bulk at once**: Send to max 50-100 contacts per session. The script automatically pauses for 1 hour after 100 messages to prevent bans.
- **Monitor for blocks**: WhatsApp may temporarily block your number for suspicious activity

### 2. Test First

```python
# Create test.pdf with 2-3 contacts
# Run a small batch first
send_whatsapp_from_pdf(
    pdf_file="test_contacts.pdf",
    message="Test message",
    resume=False
)
```

### 3. Backup Your Data

```bash
# Before running large campaigns
cp whatsapp_progress.json whatsapp_progress_backup.json
cp sent_contacts.json sent_contacts_backup.json
```

### 4. Monitor Progress

```python
# Check progress file periodically
import json
with open('whatsapp_progress.json', 'r') as f:
    progress = json.load(f)
    print(f"Progress: {progress['current_index']}/{progress['total_contacts']}")
    print(f"Success: {progress['success_count']}, Failed: {progress['failed_count']}")
```

### 5. Network Stability

- Use wired connection if possible
- Avoid running on mobile hotspots
- Ensure stable internet throughout the campaign

### 6. Phone Requirements

- Keep your phone connected to internet
- Don't use WhatsApp on phone while script is running
- Ensure phone has sufficient battery

## 🔐 Security & Privacy

### Data Handling

- **Local Only**: All data stays on your machine
- **No Cloud**: No data sent to external servers
- **Session Security**: Browser session encrypted by Chrome

### Sensitive Files

These files should **never** be committed to Git:

```
whatsapp_session/     # Contains your login session
sent_contacts.json    # Your contact data
whatsapp_progress.json # Your campaign data
contacts.pdf          # Your contact list
```

Already configured in `.gitignore`:
```gitignore
whatsapp_session/
.directory
```

### Recommended: Add to `.gitignore`

```gitignore
sent_contacts.json
whatsapp_progress.json
contacts.pdf
images/
*.pdf
```

## ⚖️ Legal & Ethical Use

### Disclaimer

This tool is for **educational and personal use only**. Users must:

- ✅ Have consent from recipients
- ✅ Comply with WhatsApp Terms of Service
- ✅ Follow local data protection laws (GDPR, etc.)
- ✅ Respect privacy and anti-spam regulations

### Prohibited Uses

- ❌ Spam or unsolicited messages
- ❌ Phishing or fraudulent activities
- ❌ Scraping or data harvesting
- ❌ Violating WhatsApp's terms

**The authors are not responsible for misuse of this software.**

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs

1. Check existing issues first
2. Create detailed bug report with:
   - Python version
   - Selenium version
   - Chrome & ChromeDriver versions
   - Error messages
   - Steps to reproduce

### Feature Requests

Open an issue with:
- Clear description of feature
- Use case examples
- Why it would be useful

### Pull Requests

1. Fork the repository
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open Pull Request

### Code Style

- Follow PEP 8 guidelines
- Add comments for complex logic
- Update README for new features
- Test thoroughly before submitting

## 🎯 Roadmap

Future enhancements planned:

- [ ] **GUI Interface**: Tkinter/PyQt desktop application
- [ ] **Excel Support**: Read contacts from Excel/CSV files
- [ ] **Scheduling**: Schedule messages for future delivery
- [ ] **Templates**: Message templates with variable substitution
- [ ] **Analytics Dashboard**: Success/failure statistics
- [ ] **Multi-language**: Support for multiple languages
- [ ] **Webhook Integration**: Trigger campaigns via API
- [ ] **Contact Segmentation**: Group contacts by tags

## 📊 Statistics

Based on typical usage:

- **Contacts per hour**: ~100-150 (with images)
- **Contacts per hour**: ~200-300 (text only)
- **Success rate**: ~95% (for valid contacts)
- **Session stability**: 24+ hours without re-login

## 🙏 Acknowledgments

- **Selenium** - Web automation framework
- **WhatsApp** - Messaging platform API
- **PyPDF2** - PDF parsing library
- Open source community for inspiration

## 📧 Support

Having issues? Here's how to get help:

1. **Check Documentation**: Read this README thoroughly
2. **Search Issues**: [GitHub Issues](https://github.com/MadanKhatri1/WhatsApp-Automation/issues)
3. **Create Issue**: If problem persists, create a new issue
4. **Community**: Discuss on GitHub Discussions

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Madan Khatri

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🌟 Show Your Support

If this project helped you, please consider:

- ⭐ **Star this repository**
- 🐛 **Report bugs** to help improve
- 💡 **Share ideas** for new features
- 🔀 **Contribute code** via pull requests
- 📢 **Share with others** who might benefit

---

<div align="center">

**Made with ❤️ by [Madan Khatri](https://github.com/MadanKhatri1)**

*Automating communication, one message at a time* 🚀

</div>
