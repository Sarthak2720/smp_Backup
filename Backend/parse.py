import os
import random
import sys
import threading
import time
import logging
import re 
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from selenium import webdriver
from selenium.common import StaleElementReferenceException, TimeoutException,NoSuchElementException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
import PyPDF2
import io
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask_cors import CORS
import subprocess
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from flask_cors import CORS
from flask import send_file, jsonify
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

driver = None
whatsapp_logged_in = False  # Flag to track if WhatsApp is logged in
telegram_logged_in = False  # Flag to track if Telegram is logged in
manual_logout = False  # Flag to track manual logout status
# Function to capture WhatsApp QR code
streamlit_process = None

def start_streamlit():
    global streamlit_process
    if streamlit_process is None:
        streamlit_process = subprocess.Popen(
            ["streamlit", "run", "../chatbot.py", "--", data_passed],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Wait a few seconds to ensure Streamlit starts
        time.sleep(5)

@app.route('/start-chatbot', methods=['GET'])
def start_chatbot():
    threading.Thread(target=start_streamlit).start()
    return jsonify({"message": "Chatbot is starting...", "url": "http://localhost:8501"})

def capture_qr_code():
    try:
        qr_code_xpath = "//canvas[contains(@aria-label, 'Scan this QR code to link a device!')]"
        qr_code_element = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, qr_code_xpath))
        )
        qr_code_path = "../whatsapp_qr_code.png"
        qr_code_element.screenshot(qr_code_path)
        return qr_code_path
    except Exception as e:
        print(f"Error capturing QR code: {e}")
        return None
    
def capture_telegram_qr_code():
    try:
        qr_code_xpath = "//canvas[contains(@class, 'qr-canvas')]"
        qr_code_element = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, qr_code_xpath))
        )
        qr_code_path = "../telegram_qr_code.png"
        qr_code_element.screenshot(qr_code_path)
        return qr_code_path
    except Exception as e:
        print(f"Error capturing Telegram QR code: {e}")
        return None
    
# Function to continuously check login status
def check_login_status():
    global whatsapp_logged_in, manual_logout
    while True:
        if manual_logout:  # Stop checking if the user logs out manually
            break
        try:
            # Check if the chat list element is present (indicating login success)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Chat list' and @role='grid']"))
            )
            whatsapp_logged_in = True
            print("WhatsApp Web logged in successfully!")
            time.sleep(5)  # Periodic check for active session
        except:
            whatsapp_logged_in = False
            time.sleep(5)
            
def check_telegram_login_status():
    global telegram_logged_in, manual_logout
    while True:
        if manual_logout:  # Stop checking if the user logs out manually
            break
        try:
            # Check if the chat list element is present (indicating login success)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//ul[@class='chatlist']"))
            )
            telegram_logged_in = True
            print("Telegram Web logged in successfully!")
            time.sleep(5)  # Periodic check for active session
        except:
            telegram_logged_in = False
            time.sleep(5)

# Initialize WebDriver and open WhatsApp Web only once
def initialize_driver():
    global driver
    if driver is None:
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        # Uncomment for headless mode:
        # chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        driver.get('https://web.whatsapp.com/')
        print("WhatsApp Web opened successfully")

        # Start a background thread to monitor login status
        threading.Thread(target=check_login_status, daemon=True).start()



def initialize_telegram_driver():
    global driver
    if driver is None:
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        # Uncomment for headless mode:
        # chrome_options.add_argument("--headless")
        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://web.telegram.org/k')
        print("Telegram Web opened successfully")

        # Start a background thread to monitor Telegram login status
        threading.Thread(target=check_telegram_login_status, daemon=True).start()



@app.route('/get-whatsapp-qr', methods=['GET'])
def get_whatsapp_qr():
    global driver
    initialize_driver()  # Only initializes if not already done
    if driver is None:
        return jsonify({"error": "Failed to initialize WhatsApp Web."}), 500

    try:
        qr_code_path = capture_qr_code()
        if qr_code_path:
            return send_file(qr_code_path, mimetype='image/png')
        else:
            return jsonify({"error": "Failed to capture QR code."}), 500
    except Exception as e:
        print(f"Error in get-whatsapp-qr route: {e}")
        return jsonify({"error": "Failed to retrieve QR code."}), 500

@app.route('/get-telegram-qr', methods=['GET'])
def get_telegram_qr():
    global driver
    initialize_telegram_driver()  # Only initializes if not already done
    if driver is None:
        return jsonify({"error": "Failed to initialize Telegram Web."}), 500

    try:
        qr_code_path = capture_telegram_qr_code()
        if qr_code_path:
            return send_file(qr_code_path, mimetype='image/png')
        else:
            return jsonify({"error": "Failed to capture QR code."}), 500
    except Exception as e:
        print(f"Error in get-telegram-qr route: {e}")
        return jsonify({"error": "Failed to retrieve QR code."}), 500

@app.route('/check-whatsapp-login', methods=['GET'])
def check_whatsapp_login():
    # Send the login status to the frontend
    return jsonify({"loggedIn": whatsapp_logged_in}), 200


@app.route('/check-telegram-login', methods=['GET'])
def check_telegram_login():
    # Send the login status to the frontend
    return jsonify({"loggedIn": telegram_logged_in}), 200

@app.route('/logout', methods=['POST'])
def logout():
    global manual_logout, driver, whatsapp_logged_in, telegram_logged_in
    try:
        manual_logout = True  # Set the manual logout flag
        whatsapp_logged_in = False  # Reset the login status
        telegram_logged_in = False  # Reset the login status
        if driver:
            driver.quit()  # Close the WebDriver
            driver = None
        return jsonify({"message": "Logged out successfully!"}), 200
    except Exception as e:
        print(f"Error during logout: {e}")
        return jsonify({"error": "Failed to logout."}), 500
    
@app.route('/reset-session', methods=['POST'])
def reset_session():
    global manual_logout, driver, whatsapp_logged_in, telegram_logged_in
    try:
        manual_logout = False  # Allow session restart
        whatsapp_logged_in = False  # Reset login status
        telegram_logged_in = False  # Reset login status
        if driver is not None:
            driver.quit()  # Reset the WebDriver
        # Reinitialize the WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://web.telegram.org/k')
        print("Telegram Web restarted successfully")
        # Restart the login status thread
        threading.Thread(target=check_telegram_login_status, daemon=True).start()
        return jsonify({"message": "Session reset successfully!"}), 200
    except Exception as e:
        print(f"Error resetting session: {e}")
        return jsonify({"error": "Failed to reset session."}), 500

# Platform configurations for login
PLATFORM_CONFIG = {
    "facebook": {
        "url": "https://www.facebook.com/",
        "username_field": {"by": By.ID, "value": "email"},
        "password_field": {"by": By.ID, "value": "pass"},
        "login_button": {"by": By.NAME, "value": "login"},
        "success_indicator": {"by": By.XPATH, "value": "//div[contains(@class, 'x1n2onr6')]"},
    },
    "instagram": {
        "url": "https://www.instagram.com/accounts/login/",
        "username_field": {"by": By.NAME, "value": "username"},
        "password_field": {"by": By.NAME, "value": "password"},
        "login_button": {"by": By.XPATH, "value": "//button[@type='submit']"},
        "success_indicator": {"by": By.XPATH, "value": "//button[contains(@class, '_acan') and contains(@class, '_acap') and contains(@class, '_acas') and contains(@class, '_aj1-') and contains(@class, '_ap30') and text()='Save info']"},
    },
    "twitter": {
        "url": "https://x.com/i/flow/login",
        "username_field": {"by": By.NAME, "value": "text"},
        "password_field": {"by": By.NAME, "value": "password"},
        "login_button": {"by": By.XPATH, "value": "//button[@role='button']"},
        "success_indicator": {"by": By.XPATH, "value": "//a[@aria-label='Home' and @role='link']"},
    },
    "gmail": {
        "url": "https://accounts.google.com/signin",
        "username_field": {"by": By.NAME, "value": "identifier"},
        "password_field": {"by": By.NAME, "value": "Passwd"},
        "login_button": {"by": By.ID, "value": "identifierNext"},
        "success_indicator": {"by": By.XPATH, "value": "//div[@aria-label='Main menu']"},
    },  
}




@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    platform = data.get('platform')
    username = data.get('username')
    password = data.get('password')

    if not platform or platform not in PLATFORM_CONFIG:
        return jsonify({'success': False, 'message': f'Platform {platform} not supported'}), 400

    if platform.lower() != 'whatsapp' and platform.lower() != 'telegram' and (not username or not password):
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    try:
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)

        if platform.lower() == 'telegram':
            driver.get('https://web.telegram.org/k')
            # Add logic to handle Telegram login if needed
            prefs = {"profile.default_content_setting_values.notifications": 2}
            chrome_options.add_experimental_option("prefs", prefs)

            success = True  # Assume success for now
        else:
            config = PLATFORM_CONFIG[platform]
            driver.get(config["url"])

            if platform.lower() == "twitter":
                # Twitter-specific login flow
                username_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((config["username_field"]["by"], config["username_field"]["value"]))
                )
                username_field.send_keys(username)
                username_field.send_keys(webdriver.Keys.RETURN)  # Submit the username

                password_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((config["password_field"]["by"], config["password_field"]["value"]))
                )
                password_field.send_keys(password)
                password_field.send_keys(webdriver.Keys.RETURN)  # Submit the password

                try:
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((config["success_indicator"]["by"], config["success_indicator"]["value"]))
                    )
                    success = True
                except TimeoutException:
                    success = False
            else:
                # General platform login flow
                username_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((config["username_field"]["by"], config["username_field"]["value"]))
                )
                username_field.send_keys(username)

                password_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((config["password_field"]["by"], config["password_field"]["value"]))
                )
                password_field.send_keys(password)

                login_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((config["login_button"]["by"], config["login_button"]["value"]))
                )
                login_button.click()

                try:
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((config["success_indicator"]["by"], config["success_indicator"]["value"]))
                    )
                    success = True
                except TimeoutException:
                    success = False

                try:
                    WebDriverWait(driver, 5).until(EC.alert_is_present())
                    alert = Alert(driver)
                    alert.accept()
                except TimeoutException:
                    pass

        driver.quit()

        if success:
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
def random_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))

def parse_whatsapp_chats(username,accused_data,case_data):
    try:
        print("Starting WhatsApp chat parsing...")

        try:
            # Click the settings button
            print("Attempting to find and click the settings button for syncing.")
            settings_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Settings' and @role='button']"))
            )
            settings_button.click()
            print("Clicked the settings button.")

            # Locate the potential sync button
            print("Attempting to locate the sync button.")
            buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'x1c4vz4f') and contains(@class, 'xs83m0k') "
                   "and contains(@class, 'xdl72j9') and contains(@class, 'x1g77sc7') "
                   "and contains(@class, 'x78zum5') and contains(@class, 'xozqiw3') "
                   "and contains(@class, 'x1oa3qoh') and contains(@class, 'x12fk4p8') "
                   "and contains(@class, 'xexx8yu') and contains(@class, 'x4uap5') "
                   "and contains(@class, 'x18d9i69') and contains(@class, 'xkhd6sd') "
                   "and contains(@class, 'xeuugli') and contains(@class, 'x2lwn1j') "
                   "and contains(@class, 'x1nhvcw1') and contains(@class, 'xdt5ytf') "
                   "and contains(@class, 'x1qjc9v5')]//button")

            sync_button_found = False
            for button in buttons:
                try:
                    # Check the text inside the button's div
                    div = button.find_element(By.XPATH, ".//div[contains(@class, 'x1lkfr7t') and contains(@class, 'xdbd6k5') "
                                                        "and contains(@class, 'x1fcty0u') and contains(@class, 'xw2npq5')]")
                    if div.text.strip() == "Syncing older messages":
                        print("Found the correct sync button.")
                        button.click()
                        sync_button_found = True
                        break
                except Exception as e:
                    # Ignore and continue if the div or text is not found
                    continue

            if sync_button_found:
                print("Waiting for the progress bar to reach 100%...")
                WebDriverWait(driver, 240).until(
                    lambda d: d.find_element(By.XPATH, "//progress[@class='_ak0k']").get_attribute("value") == "100"
                )
                print("Progress bar reached 100%.")

                # Click the OK button
                print("Attempting to click the 'OK' button.")
                ok_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'x889kno') and contains(@class, 'x1a8lsjc')]"))
                )
                ok_button.click()
                print("Clicked 'OK' on the popup.")
            else:
                print("No sync button with the text 'Sync older messages' was found. Skipping sync steps.")
            
            # Wait for and click the "Chats" div
            print("Waiting for the 'Chats' div to be clickable.")
            chats_div = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Chats' and @role='button']"))
                )
            chats_div.click()
            print("Clicked on the 'Chats' div to open chats.")

            # Capture screenshots and save to PDF
        except TimeoutException as e:
            print(f"Error: Timeout while waiting for an element. Details: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        # Generate the PDF regardless of sync button presence
        chat_screenshots = take_chat_screenshots(driver)
        if chat_screenshots:
            pdf_stream = generate_pdf(chat_screenshots,accused_data,case_data, "WhatsApp", "All Chats")
            if pdf_stream is not None:
                print(f"PDF size: {len(pdf_stream.getvalue())} bytes")
                return pdf_stream  # Return the PDF stream instead of sending the file directly
            else:
                print("Failed to generate PDF.")
                return None
        else:
            print("No chat screenshots taken.")
            return None

    except Exception as e:
        print(f"Error parsing WhatsApp chats: {e}")
        return None
    
def parse_telegram_chats(contact_name, accused_name, case_number, platform):
    try:
        print(f"Starting Telegram chat parsing for contact: {contact_name}")

        try:
            # Click the search bar
            print("Attempting to find and click the search bar.")
            search_bar = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='text']"))
            )
            search_bar.click()
            print("Clicked the search bar.")

            # Enter the contact name
            print(f"Entering contact name: {contact_name}")
            search_bar.send_keys(contact_name)
            time.sleep(3)  # Wait for search results to load

            print("searching for chatlist")
            chat_list = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='search-container']/div[2]/div[2]/div/div[1]/div/div[1]/ul"
                ))
            )
            print("Chat list loaded successfully.")
            
            
            # Extract unique identifiers from search results
            print("Extracting unique identifiers from search results.")
            try:
                # Locate all contact elements in the search results
                contact_elements = chat_list.find_elements(By.XPATH, ".//a[@data-peer-id]")
                
                print(f"Found {len(contact_elements)} contacts.")

                # Extract datapeerid from each contact's href
                datapeerids = []
                for contact in contact_elements:
                    contact_href = contact.get_attribute("data-peer-id")
                    datapeerid = contact_href.split('#')[-1]
                    datapeerids.append(datapeerid)
                    print(f"Extracted datapeerid: {datapeerid}")

            except TimeoutException:
                print("No contacts found in search results.")
                return jsonify({"error": "No contacts found."}), 404

            # Iterate through each datapeerid and process the chat
            all_chat_screenshots = []
            for datapeerid in datapeerids:
                try:
                    # Construct the direct chat URL using datapeerid
                    chat_url = f"https://web.telegram.org/k/#{datapeerid}"
                    print(f"Navigating to chat URL: {chat_url}")
                    driver.get(chat_url)

                    # Wait for the chat to load
                    print("Waiting for the chat to load.")
                    time.sleep(5)  # Wait for the chat to load  
                    print("Chat loaded successfully.")

                    # Capture screenshots of the chat
                    chat_screenshots = telegram_chat_screenshot(driver)
                    if chat_screenshots:
                        all_chat_screenshots.extend(chat_screenshots)
                        print(f"Captured {len(chat_screenshots)} screenshots for datapeerid: {datapeerid}")
                    else:
                        print(f"No screenshots taken for datapeerid: {datapeerid}")

                except TimeoutException as e:
                    print(f"Timeout while processing datapeerid {datapeerid}: {e}")
                    continue
                except Exception as e:
                    print(f"An error occurred while processing datapeerid {datapeerid}: {e}")
                    continue

            # Generate PDF from all captured screenshots
            if all_chat_screenshots:
                pdf_stream = generate_pdf(all_chat_screenshots,accused_name=accused_name,case_number=case_number,platform=platform,option='Parse Individual Chat')
                if pdf_stream is not None:
                    print(f"PDF size: {len(pdf_stream.getvalue())} bytes")  
                    return pdf_stream  # Return the PDF stream
                else:
                    print("Failed to generate PDF.")
                    return jsonify({"error": "Failed to generate PDF."}), 500
            else:
                print("No chat screenshots taken.")
                return jsonify({"error": "No chat screenshots were taken."}), 404

        except TimeoutException as e:
            print(f"Error: Timeout while waiting for an element. Details: {e}")
            return jsonify({"error": "Timeout while waiting for elements."}), 500
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return jsonify({"error": "An unexpected error occurred."}), 500

    except Exception as e:
        print(f"Error parsing Telegram chats: {e}")
        return jsonify({"error": "Internal server error."}), 500
    
def generate_pdf(screenshots, accused_name, case_number, platform, option):
    """
    Generates a PDF from the provided screenshots with embedded extracted texts and clickable links.

    :param screenshots: List of dictionaries with 'filename', 'text', and 'links' keys.
    :param accused_name: Name of the accused.
    :param case_number: Case number.
    :param platform: Platform name.
    :param option: Option selected.
    :param datetime_str: Datetime string.
    :return: BytesIO buffer containing the PDF data.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    parsing_date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    # Optional: Add a title or header page
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 50, "Chat Analysis Report")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 70, f"Accused: {accused_name}")
    # c.drawCentredString(width / 2, height - 150, f"Username : {username}")
    c.drawCentredString(width / 2, height - 90, f"Case Number: {case_number}")
    c.drawCentredString(width / 2, height - 110, f"Platform: {platform}")
    c.drawCentredString(width / 2, height - 130, f"Option: {option}")
    c.drawCentredString(width / 2, height - 150, f"Generated on: {parsing_date_time}")
    c.showPage()

    for item in screenshots:
        screenshot = item['filename']
        extracted_text = item['text']
        links = item.get('links', [])
        try:
            # Add extracted text
            text_object = c.beginText(50, height - 50)
            text_object.setFont("Helvetica", 12)
            for line in extracted_text.split('\n'):
                if line.strip():
                    text_object.textLine(line)
                    c.setFillColorRGB(1, 1, 1)  # White background for text
            c.drawText(text_object)

            # Add screenshot below the text
            img = Image.open(screenshot)
            img_width, img_height = img.size
            scale = min((width - 100) / img_width, (height - 200) / img_height)  # Adjusted for space
            img_width = int(img_width * scale)
            img_height = int(img_height * scale)
            x_position = (width - img_width) / 2
            y_position = height - img_height - 150  # Leave space for links
            c.drawImage(screenshot, x_position, y_position, width=img_width, height=img_height)

            # Add links at the bottom
            if links:
                c.setFont("Helvetica-Bold", 12)
                c.setFillColorRGB(0, 0, 0)  # White background
                c.drawString(50, 100, "Links:")
                c.setFont("Helvetica", 10)
                for idx, link in enumerate(links, start=1):
                    link_y = 80 - (idx * 15)  # Adjust vertical spacing as needed
                    c.drawString(50, link_y, f"{idx}. {link}")
                    # Make the link clickable
                    c.linkURL(link, (50, link_y - 2, width - 50, link_y + 12), relative=0)  # Bounding box for the link

            c.showPage()
            logging.info(f"Added {screenshot} and extracted text to PDF.")

        except Exception as e:
            logging.error(f"Error adding {screenshot} to PDF: {e}")
            continue

    c.save()
    buffer.seek(0)
    return buffer

def take_chat_screenshots(driver):
    screenshots = []
    try:
        # Wait for the chat list to load
        chat_list = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Chat list' and @role='grid']"))
        )
        print("Chat list loaded successfully.")

        # Get all chat elements
        chat_elements = chat_list.find_elements(By.XPATH, ".//div[@role='listitem']")
        print(f"Found {len(chat_elements)} chats.")

        for i, chat in enumerate(chat_elements):
            try:
                # Scroll the chat into view and click it
                driver.execute_script("arguments[0].scrollIntoView(true);", chat)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, ".//div[@role='listitem']")))
                chat.click()
                random_delay(2, 3)

                # Wait for the chat container to load
                chat_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[contains(@class, 'x10l6tqk') and contains(@class, 'x13vifvy') and contains(@class, 'x17qophe') and contains(@class, 'xyw6214') and contains(@class, 'x9f619') and contains(@class, 'x78zum5') and contains(@class, 'xdt5ytf') and contains(@class, 'xh8yej3') and contains(@class, 'x5yr21d') and contains(@class, 'x6ikm8r') and contains(@class, 'x1rife3k') and contains(@class, 'xjbqb8w') and contains(@class, 'x1ewm37j')]")
                    )
                )
                print(f"Chat container loaded for chat {i + 1}.")
                random_delay(2, 3)

                # Handle Media
                # media_elements = chat_container.find_elements(By.XPATH, ".//img[@src] | .//video")
                # if media_elements:
                #     for idx, media in enumerate(media_elements):
                #         try:
                #             driver.execute_script("arguments[0].scrollIntoView(true);", media)
                #             media.click()
                #             random_delay(2, 3)

                #             # Wait for media modal to appear
                #             media_modal = WebDriverWait(driver, 10).until(
                #                 EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
                #             )
                #             media_screenshot = f'chat_{i + 1}_media_{idx + 1}.png'
                #             media_modal.screenshot(media_screenshot)
                #             screenshots.append(media_screenshot)
                #             print(f"Media screenshot taken: {media_screenshot}")

                #             # Close the media modal
                #             close_button = WebDriverWait(driver, 10).until(
                #                 EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @aria-label='Close']"))
                #             )
                #             close_button.click()
                #             random_delay(1, 2)
                #         except Exception as e:
                #             print(f"Error handling media {idx + 1} in chat {i + 1}: {e}")
                #             continue

                # Check if the chat is scrollable
                scroll_height = driver.execute_script("return arguments[0].scrollHeight;", chat_container)
                client_height = driver.execute_script("return arguments[0].clientHeight;", chat_container)

                if scroll_height <= client_height:
                    # Chat is unscrollable, take a single screenshot
                    screenshot_filename = f'chat_screenshot_{i + 1}.png'
                    driver.save_screenshot(screenshot_filename)
                    screenshots.append(screenshot_filename)
                    print(f"Screenshot taken for unscrollable chat: {screenshot_filename}")
                else:
                    # Chat is scrollable, take screenshots from bottom to top
                    while True:
                        # Take a screenshot of the current view
                        screenshot_filename = f'chat_screenshot_{i + 1}_{len(screenshots)}.png'
                        driver.save_screenshot(screenshot_filename)
                        screenshots.append(screenshot_filename)
                        print(f"Screenshot taken: {screenshot_filename}")

                        # Scroll up by a fixed amount
                        current_scroll_position = driver.execute_script("return arguments[0].scrollTop;", chat_container)
                        driver.execute_script("arguments[0].scrollTop -= arguments[1];", chat_container, 500)
                        random_delay(2, 3)  # Wait for content to load

                        # Check if we reached the top
                        new_scroll_position = driver.execute_script("return arguments[0].scrollTop;", chat_container)
                        if new_scroll_position == 0 or new_scroll_position == current_scroll_position:
                            print("Reached the top of the chat.")
                            screenshot_filename = f'chat_screenshot_{i + 1}_{len(screenshots)}.png'
                            driver.save_screenshot(screenshot_filename)
                            screenshots.append(screenshot_filename)
                            print(f"Screenshot taken: {screenshot_filename}")
                            break

                # Go back to the chat list
                driver.back()
                random_delay(2, 4)  # Wait for the chat list to reload
                print("Back to chat list, moving to the next chat.")

            except Exception as e:
                print(f"Error with chat {i + 1}: {e}")
                continue  # Proceed to the next chat even if there's an error with the current one

    except Exception as e:
        print(f"An error occurred: {e}")

    return screenshots

def telegram_chat_screenshot(driver):
    screenshots = []
    try:
        # Locate the chat messages container (Update the XPath based on actual DOM)
        print("Locating the Telegram chat messages container.")
        chat_container = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='column-center']/div/div/div[3]/div[2]"))
        )   
        print("Telegram chat messages container located successfully.")

        # Get initial scroll height
        scroll_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)
        client_height = driver.execute_script("return arguments[0].clientHeight", chat_container)
        print(f"Initial scrollHeight: {scroll_height}, clientHeight: {client_height}")

        # Define scroll step (pixels to scroll each time)
        scroll_step = client_height // 2

        while True:
            # Take a screenshot of the current view
            screenshot_filename = f'telegram_chat_screenshot_{len(screenshots) + 1}.png'
            driver.save_screenshot(screenshot_filename)
            print(f"Screenshot taken: {screenshot_filename}")

            # Extract visible text after taking the screenshot
            visible_text = extract_visible_text_telegram(driver, chat_container)
            screenshots.append({
                'filename': screenshot_filename,
                'text': visible_text
            })

            # Scroll up by the scroll_step
            print("Scrolling up the Telegram chat.")
            driver.execute_script("arguments[0].scrollBy(0, -arguments[1]);", chat_container, scroll_step)
            random_delay(5, 8)  # Wait for messages to load

            # Calculate new scroll position
            new_scroll_position = driver.execute_script("return arguments[0].scrollTop;", chat_container)
            print(f"New scrollTop position: {new_scroll_position}")

            # If we've reached the top, break the loop
            if new_scroll_position <= 0:
                # Take an additional screenshot at the top
                screenshot_filename = f'telegram_chat_screenshot_{len(screenshots) + 1}.png'
                driver.save_screenshot(screenshot_filename)
                print(f"Final screenshot taken at the top: {screenshot_filename}")

                visible_text = extract_visible_text_telegram(driver, chat_container)
                screenshots.append({
                    'filename': screenshot_filename,
                    'text': visible_text
                })
                break

    except TimeoutException:
        print("Failed to locate the Telegram chat messages container.")
    except NoSuchElementException:
        print("Telegram chat messages container not found.")
    except Exception as e:
        print(f"An error occurred during Telegram chat screenshot: {e}")

    return screenshots

def extract_visible_text_telegram(driver, chat_container):
    """
    Extracts the text of all visible messages currently within the Telegram chat container.

    :param driver: Selenium WebDriver instance.
    :param chat_container: WebElement representing the Telegram chat container.
    :return: Concatenated string of visible message texts.
    """
    visible_texts = []
    try:
        # Locate all message text elements within the chat container.
        # Update the XPath based on Telegram's current DOM structure.
        messages = chat_container.find_elements(
            By.XPATH,
            ".//div[contains(@class, 'message') and contains(@class, 'spoilers-container')]"

        )
        print(f"Found {len(messages)} messages in the chat container.")
        print({message.text for message in messages})   
        for message in messages:
            try:
                # Verify if the message is visible in the viewport
                if message.is_displayed():
                    # Extract the text content of the message
                    text_content = message.text.strip()
                    if text_content:
                        visible_texts.append(text_content)
            except StaleElementReferenceException:
                print("StaleElementReferenceException encountered. Skipping this message.")
                continue
            except Exception as e:
                print(f"Error extracting text from a message: {e}")
                continue

    except Exception as e:
        print(f"Error extracting visible text from Telegram chat: {e}")

    # Join all extracted texts with newline characters for better readability in the PDF
    return "\n".join(visible_texts)

@app.route('/parse', methods=['POST'])
def parse_data():
    try:
        # Parse request data
        data = request.get_json()
        platform = data.get('platform')
        option = data.get('option')
        accused_name = data.get('accusedName')  # New field
        case_data = data.get('caseNumber')        # New field

        # Validate required fields
        if not platform or not option:
            return jsonify({'message': 'Missing required fields'}), 400

        # Username and password are only required for non-WhatsApp and non-Telegram platforms
        if platform.lower() not in ['whatsapp', 'telegram']:
            username = data.get('username')
            password = data.get('password')
            if not username or not password:
                return jsonify({'message': 'Username and password are required for this platform.'}), 400
        else:
            username = None
            password = None

        # Define platform scripts
        platform_scripts = {
            "facebook": {
                "Parse Followers": 'sih_facebook.py',
                "Parse Posts": 'sih_facebook_posts.py',
                "Parse Chats": 'sih_facebook_chats.py',
                "Parse All": 'sih_facebook_all.py',
            },
            "instagram": {
                "Parse Account Information": 'instagram_account_script.py',
                "Parse Followers": 'instagram_followers_script.py',
                "Parse Posts": 'instagram_posts_script.py',
                "Parse Chats": 'C:\\Users\\sarth\\Desktop\\sih\\the_masked_program\\Backend\\instagram_chats_script.py',
            },
            "twitter": {
                "Parse Followers": 'twitter_followers_scraping.py',
                "Parse Posts": 'twitter_posts_scraping.py',
                "Parse Chats": 'twitter_chats_scraping.py',
            },
            "gmail": {
                "Parse Followers": '/gmail_followers.py',
                "Parse Posts": '/gmail_posts.py',
                "Parse Chats": '/gmail_chats.py',
            }
        }

        # Handle "Parse All" option first
        if option == 'Parse All':
            options_to_parse = ["Parse Followers", "Parse Posts", "Parse Chats", "Parse Account Information"]
            pdf_writer = PyPDF2.PdfWriter()  # Create a PDF writer to merge all PDFs

            plat = platform.lower()
            scripts = platform_scripts.get(plat)
            if not scripts:
                return jsonify({"error": "Unsupported platform for parsing."}), 400

            for option_to_parse in options_to_parse:
                script_path = scripts.get(option_to_parse)
                if script_path:
                    print(f"Running script for {option_to_parse} for {platform}...")
                    # Build the command with additional parameters
                    command = ['python', script_path]
                    if username:
                        command.extend(['--username', username])
                    if password:
                        command.extend(['--password', password])
                    if accused_name:
                        command.extend(['--accusedName', accused_name])
                    if case_data:
                        command.extend(['--caseData', case_data])

                    process = subprocess.run(command, capture_output=True)

                    if process.returncode != 0:
                        error_message = process.stderr.decode()
                        print(f"Script error: {error_message}")
                        return jsonify({'message': error_message}), 400

                    # Assuming each script returns a PDF as output
                    pdf_data = io.BytesIO(process.stdout)  # Convert to byte stream
                    try:
                        pdf_reader = PyPDF2.PdfReader(pdf_data)  # Read the PDF
                        # Merge the PDF
                        for page in range(len(pdf_reader.pages)):
                            pdf_writer.add_page(pdf_reader.pages[page])
                    except Exception as pdf_e:
                        print(f"Error reading PDF from script: {pdf_e}")
                        continue

            # Prepare the combined PDF in memory
            combined_pdf = io.BytesIO()
            pdf_writer.write(combined_pdf)
            combined_pdf.seek(0)  # Go to the beginning of the combined PDF

            # Send the combined PDF file as a response
            return send_file(
                combined_pdf,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'{platform}_Parse_All.pdf'
            )

        # Handle specific parsing options
        if platform.lower() == 'whatsapp' and option == 'Parse Chats':
            pdf_buffer = parse_whatsapp_chats(username,accused_name,case_data)
            if pdf_buffer:
                return send_file(
                    pdf_buffer,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name="whatsapp_chats.pdf"
                )
            else:
                return jsonify({'message': 'Failed to generate PDF.'}), 500

        elif platform.lower() == 'telegram' and option == 'Parse Chats':
            pdf_buffer = parse_telegram_all_chats(accused_name,case_data)
            if pdf_buffer:
                return send_file(
                    pdf_buffer,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name="telegram_chats.pdf"
                )
            else:
                return jsonify({'message': 'Failed to generate PDF.'}), 500

        elif platform.lower() == 'telegram' and option == 'Parse Individual Chat':
            contact_name = data.get('contactName')
            if not contact_name:
                return jsonify({"error": "Contact name is required for individual chat parsing."}), 400
            pdf_buffer = parse_telegram_chats(contact_name, accused_name, case_data, platform)
            if isinstance(pdf_buffer, io.BytesIO):
                return send_file(
                    pdf_buffer,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'telegram_chat_{contact_name.replace(" ", "_")}.pdf'
                )
            elif pdf_buffer == "Contact not found.":
                return jsonify({"error": "Person not found."}), 404
            else:
                return jsonify({"error": "Failed to parse Telegram chat."}), 500

        else:
            # Parse the selected individual option (if not "Parse All")
            plat = platform.lower()
            scripts = platform_scripts.get(plat)
            if scripts and option in scripts:
                script_path = scripts[option]
                command = ['python', script_path]
                if username:
                    command.extend(['--username', username])
                if password:
                    command.extend(['--password', password])
                if accused_name:
                    command.extend(['--accusedName', accused_name])
                if case_data:
                    command.extend(['--caseData', case_data])

                process = subprocess.run(command, capture_output=True)

                if process.returncode != 0:
                    error_message = process.stderr.decode()
                    print(f"Script error: {error_message}")
                    return jsonify({'message': error_message}), 400

                # Send the individual PDF file as a response
                pdf_data = io.BytesIO(process.stdout)  # Assuming the output is a PDF
                return send_file(
                    pdf_data,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'{platform}_{option.replace(" ", "")}.pdf'
                )
            else:
                return jsonify({'success': False, 'message': 'Invalid option selected.'}), 400

    except Exception as e:
        print(f"Error in /parse route: {e}")
        return jsonify({'message': str(e)}), 500
    
# Implement the parse_telegram_all_chats function in parse.py
def generate_metadata_pdf(accused_name, case_number, platform, option, parsing_datetime):
    """
    Generates a PDF page with metadata information.

    Returns:
        BytesIO: In-memory PDF containing the metadata.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, height - 100, "Report Details")

    # Metadata Details
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, f"Accused Name: {accused_name}")
    c.drawString(100, height - 150, f"Case Number: {case_number}")
    c.drawString(100, height - 170, f"Platform: {platform.capitalize()}")
    c.drawString(100, height - 190, f"Option Selected: {option}")
    c.drawString(100, height - 210, f"Parsing Date & Time: {parsing_datetime}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def parse_telegram_all_chats(accused_name,case_data):
    try:
        print("Starting Telegram all chats parsing...")

        # Initialize Telegram driver
        # initialize_telegram_driver()
        
        
        # Wait for the chat list to load
        chat_list = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='folders-container']//div//ul[@class='chatlist']"))
        )   
        print("Telegram chat list loaded successfully.")

        # Get all chat elements
        chat_elements = chat_list.find_elements(By.XPATH,"//a[contains(@class, 'row') and contains(@class, 'no-wrap') and contains(@class, 'row-with-padding') and contains(@class, 'row-clickable') and contains(@class, 'hover-effect') and contains(@class, 'rp') and contains(@class, 'chatlist-chat') and contains(@class, 'chatlist-chat-bigger') and contains(@class, 'row-big')]")
        print(f"Found {len(chat_elements)} chats.")

        screenshots = []
        for i, chat in enumerate(chat_elements):
            try:
                chat.click()  # Open the chat
                random_delay(2, 4)  # Fixed delay before taking the screenshot

                # Check if the button exists inside the chat container
                try:
                    button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//div[contains(@class, 'chat-input-container') and contains(@class, 'chat-input-main-container')]//button[contains(@class, 'btn-circle') and contains(@class, 'btn-corner') and contains(@class, 'z-depth-1') and contains(@class, 'bubbles-corner-button') and contains(@class, 'chat-secondary-button') and contains(@class, 'bubbles-go-down') and contains(@class, 'rp') and contains(@class, 'is-broadcast')]")
                        )
                    )
                    print("Button found. Clicking it...")
                    button.click()
                    print("Button clicked. Waiting for 5 seconds.")
                    time.sleep(10)  # Wait 5 seconds after clicking the button
                except TimeoutException:
                    print("Button not found. Proceeding with screenshot capture.")
                    time.sleep(10)  # Wait 5 seconds if button is not found
                    
                chat_container = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='column-center']//div//div//div//div[@class='scrollable scrollable-y']"))
                )
                # Take a screenshot of the open chat
                scroll_height = driver.execute_script("return arguments[0].scrollHeight;", chat_container)
                client_height = driver.execute_script("return arguments[0].clientHeight;", chat_container)

                if scroll_height <= client_height:
                    # Chat is unscrollable, take a single screenshot
                    screenshot_filename = f'chat_screenshot_{i + 1}.png'
                    driver.save_screenshot(screenshot_filename)
                    screenshots.append(screenshot_filename)
                    print(f"Screenshot taken for unscrollable chat: {screenshot_filename}")
                else:
                    # Chat is scrollable, take screenshots from bottom to top
                    while True:
                        # Take a screenshot of the current view
                        screenshot_filename = f'chat_screenshot_{i + 1}_{len(screenshots)}.png'
                        driver.save_screenshot(screenshot_filename)
                        screenshots.append(screenshot_filename)
                        print(f"Screenshot taken: {screenshot_filename}")

                        # Scroll up by a fixed amount
                        current_scroll_position = driver.execute_script("return arguments[0].scrollTop;", chat_container)
                        driver.execute_script("arguments[0].scrollTop -= arguments[1];", chat_container, 500)
                        random_delay(2, 3)  # Wait for content to load

                        # Check if we reached the top
                        new_scroll_position = driver.execute_script("return arguments[0].scrollTop;", chat_container)
                        if new_scroll_position == 0 or new_scroll_position == current_scroll_position:
                            print("Reached the top of the chat.")
                            screenshot_filename = f'chat_screenshot_{i + 1}_{len(screenshots)}.png'
                            driver.save_screenshot(screenshot_filename)
                            screenshots.append(screenshot_filename)
                            print(f"Screenshot taken: {screenshot_filename}")
                            break

                # Go back to the chat list
                driver.back()
                random_delay(2, 4)  # Wait for the chat list to reload
                print("Back to chat list, moving to the next chat.")
                # Ensure the chat list is visible before moving to the next chat
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='folders-container']//div//ul[@class='chatlist']"))
                )
                print("Back to the chat list. Proceeding to the next chat.")

            except Exception as e:
                print(f"Error with chat {i + 1}: {e}")
                continue  # Move to the next chat even if there's an error with the current one

        if screenshots:
            pdf_buffer = generate_pdf(screenshots,accused_name,case_data, "WhatsApp", "All Chats")
            if pdf_buffer:
                return pdf_buffer
            else:
                print("Failed to generate PDF.")
                return None
        else:
            print("No chat screenshots taken.")
            return None

    except Exception as e:
        print(f"Error parsing Telegram all chats: {e}")
        return None
    
@app.route('/parse-individual-chat', methods=['POST'])
def parse_individual_chat():
    data = request.get_json()
    platform = data.get('platform')
    contact_name = data.get('contactName')
    accused_name = data.get('accusedName')
    case_number = data.get('caseNumber')
    
    
    if not platform or not contact_name:
        return jsonify({"error": "Platform and contact name are required."}), 400

    if platform.lower() != 'whatsapp' and platform.lower() != 'telegram':
        return jsonify({"error": "Unsupported platform."}), 400

    if platform.lower() == 'whatsapp':
        pdf_buffer = parse_whatsapp_individual_chat(contact_name,accused_name,case_number,platform)
    elif platform.lower() == 'telegram':
        pdf_buffer = parse_telegram_chats(contact_name, accused_name, case_number, platform)

    if pdf_buffer:
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{contact_name}_chat.pdf'
        ), 200
    else:
        return jsonify({"error": "Failed to parse chat data."}), 500

def parse_whatsapp_individual_chat(contact_name,accused_name,case_number,platform):
    
        print(f"Starting WhatsApp individual chat parsing for contact: {contact_name}")

        # Initialize WhatsApp driver
        initialize_driver()
        current_driver = driver

        if not whatsapp_logged_in:
            print("WhatsApp is not logged in. Cannot parse chats.")
            return None

        # Search for the contact
        try:
            # Locate the search field
            search_field = WebDriverWait(current_driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@contenteditable='true'][@data-tab='3']")
                )
            )
            print("Search field located successfully.")

            # Click the search field and enter the contact name
            search_field.click()
            search_field.clear()
            search_field.send_keys(contact_name)
            random_delay(2, 2)  # Fixed 2-second delay

            # Wait for search results to load
            search_list = WebDriverWait(current_driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[aria-label="Search results."]')
                )
            )
            
            search_results = search_list.find_elements(By.XPATH, './/div[@role="listitem" and div[contains(@class, "x1n2onr6")]]')
            
            print(f"Found {len(search_results)} matching chats.")
            all_screenshots = []
            # Iterate through each search result
            for idx, chat in enumerate(search_results, start=1):
                try:
                    chat.click()
                    random_delay(2, 2)  # Fixed 2-second delay

                    time.sleep(2)
                    # Modify contact name to include chat index for uniqueness
                    unique_contact_name = f"{contact_name}_chat_{idx}"
                    # Capture screenshots while scrolling to the top
                    chat_screenshots = capture_full_chat(current_driver)
                    if chat_screenshots:
                        all_screenshots.extend(chat_screenshots)
                        print(f"Captured screenshots for chat: {unique_contact_name}")
                    else:
                        print(f"No chat screenshots taken for chat: {unique_contact_name}")

                except Exception as e:
                    print(f"Error processing chat {idx} ({contact_name}): {e}")
                    continue
            if all_screenshots:
                pdf_buffer = generate_pdf(all_screenshots,accused_name=accused_name,case_number=case_number,platform=platform,option='Parse Individual Chat')
                if pdf_buffer:
                    print("Combined PDF generated successfully.")
                    return pdf_buffer  # Return the PDF buffer for download
                else:
                    print("Failed to generate combined PDF.")
                    return None
            else:
                print("No screenshots captured for any chats.")
                return None

        except TimeoutException:
            print(f"Error: Could not find the contact name '{contact_name}'. Ensure the contact_name exists in your chats.")
            return None
        except StaleElementReferenceException as e:
            print(f"StaleElementReferenceException: {e}")
            print("Re-attempting to find the search field and continue.")
            return parse_whatsapp_individual_chat(contact_name)  # Retry the search contact function
        return None
    
    
def capture_full_chat(driver):
    screenshots = []
    try:
        # Define the directory to save screenshots
        screenshot_dir = "screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        # Locate the chat container
        chat_container = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@id='main']/div[3]/div/div[2]")  # Update XPath as needed
            )
        )
        print("Chat container located successfully.")
        random_delay(2, 4)

        # Determine the next screenshot number based on existing files
        existing_screenshots = [
            f for f in os.listdir(screenshot_dir)
            if f.startswith("chat_screenshot_") and f.endswith(".png")
        ]
        next_number = len(existing_screenshots) + 1

        # Take initial screenshot
        screenshot_path = os.path.join(screenshot_dir, f"chat_screenshot_{next_number}.png")
        driver.save_screenshot(screenshot_path)
        visible_text, links = extract_visible_text_whatsapp(driver, chat_container)  # Updated line
        print(visible_text)        
        screenshots.append({
            'filename': screenshot_path,
            'text': visible_text,
            'links': links  # Added links field
        })
        print(f"Captured screenshot: {screenshot_path}")
        next_number += 1        

        

        # Get the initial scroll height
        last_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)
        scroll_attempts = 0
        max_scroll_attempts = 20  # Adjust as needed

        while scroll_attempts < max_scroll_attempts:
            # Scroll up by the height of the container
            driver.execute_script("arguments[0].scrollTop = 0;", chat_container)

            # Take a 2-second delay before taking the next screenshot
            time.sleep(2)

            # Take screenshot after scrolling
            screenshot_path = os.path.join(screenshot_dir, f"chat_screenshot_{next_number}.png")
            driver.save_screenshot(screenshot_path)
            visible_text, links = extract_visible_text_whatsapp(driver, chat_container)  # Updated line
            screenshots.append({
                'filename': screenshot_path,
                'text': visible_text,
                'links': links  # Added links field
            })
            print(f"Captured screenshot after scrolling: {screenshot_path}")
            next_number += 1

            # # Handle Media in the new view
            # media_elements = chat_container.find_elements(By.XPATH, ".//img | .//video")
            # for idx, media in enumerate(media_elements, start=1):
            #     try:
            #         driver.execute_script("arguments[0].scrollIntoView(true);", media)
            #         media.click()
            #         random_delay(2, 3)

            #         # Wait for media modal to appear
            #         media_modal = WebDriverWait(driver, 10).until(
            #             EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            #         )
            #         media_screenshot = os.path.join(screenshot_dir, f'chat_media_{next_number}_{idx}.png')
            #         media_modal.screenshot(media_screenshot)
            #         screenshots.append({
            #             'filename': media_screenshot,
            #             'text': f"Media screenshot {idx}",
            #             'links': []
            #         })
            #         print(f"Media screenshot taken: {media_screenshot}")

            #         # Close the media modal
            #         close_button = WebDriverWait(driver, 10).until(
            #             EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @aria-label='Close']"))
            #         )
            #         close_button.click()
            #         random_delay(1, 2)
            #     except Exception as e:
            #         print(f"Error handling media {idx}: {e}")
            #         continue

            # Get the new scroll height after scrolling
            new_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)
            print(f"Previous height: {last_height}, New height: {new_height}")

            if new_height == last_height:
                # Reached the top of the chat
                print("Reached the top of the chat.")
                break

            last_height = new_height
            scroll_attempts += 1

    except TimeoutException as te:
        print(f"Timeout while capturing chat screenshots: {te}")
    except Exception as e:
        print(f"Error capturing chat screenshots: {e}")

    return screenshots

def extract_visible_text_whatsapp(driver, chat_container):
    """
    Extracts the text of all messages currently visible in the WhatsApp chat_container,
    and identifies any URLs present in the text.

    :param driver: Selenium WebDriver instance.
    :param chat_container: WebElement representing the WhatsApp chat container.
    :return: Tuple containing concatenated message texts and a list of URLs.
    """
    visible_texts = []
    links = []  # List to store extracted URLs
    try:
        # Locate all message text elements within the chat container.
        # Targeting span elements with specific classes.
        messages = chat_container.find_elements(By.XPATH, ".//span[@dir='ltr' and contains(@class, 'selectable-text') and contains(@class, 'copyable-text')]")

        for message in messages:
            # Get the element's position relative to the viewport
            rect = driver.execute_script("""
                const rect = arguments[0].getBoundingClientRect();
                return {top: rect.top, bottom: rect.bottom};
            """, message)

            viewport_height = driver.execute_script("return window.innerHeight;")

            # Check if the message is within the visible viewport
            if 0 <= rect['top'] < viewport_height or 0 <= rect['bottom'] <= viewport_height:
                # Extract the text content of the message
                text_content = message.text.strip()
                if text_content:
                    visible_texts.append(text_content)

                    # Find URLs using regex and add to links list
                    found_links = re.findall(r'(https?://\S+)', text_content)
                    links.extend(found_links)
    except Exception as e:
        print(f"Error extracting WhatsApp text: {e}")

    return "\n".join(visible_texts), links  # Return both text and links

@app.route('/parse-individual-whatsapp-chat', methods=['POST'])
def parse_individual_whatsapp_chat_route():
    data = request.get_json()
    platform = data.get('platform')
    contact_name = data.get('contactName')

    if not platform or not contact_name:
        return jsonify({'message': 'Missing platform or contact name.'}), 400

    if platform.lower() != 'whatsapp':
        return jsonify({'message': 'Individual chat parsing is only supported for WhatsApp.'}), 400

    pdf_buffer = parse_whatsapp_individual_chat(contact_name)
    if pdf_buffer:
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"combined_{contact_name}_chats.pdf"
        )
    else:
        return jsonify({'message': 'Failed to parse individual WhatsApp chat.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
