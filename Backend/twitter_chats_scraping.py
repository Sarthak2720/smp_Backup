import io
import sys
import time
import random
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import logging
import  argparse
import re
import getpass
# Configure logging
logging.basicConfig(
    filename='twitter_chats.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
def random_delay(min_delay=1, max_delay=3):
    """
    Introduces a random delay between min_delay and max_delay seconds.
    """
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)
def login(driver, username, password):
    """
    Logs into Twitter using the provided credentials.
    """
    driver.get("https://twitter.com/login")
    try:
        # Enter username and proceed to the next step
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "text")))
        username_field = driver.find_element(By.NAME, "text")
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)
        logging.info("Entered username.")
        random_delay(2, 4)
       
        # Enter password
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "password")))
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        logging.info("Entered password.")
        random_delay(5, 7)
    except TimeoutException:
        logging.error("Loading took too much time! - Login element not found.")
    except NoSuchElementException:
        logging.error("No such element - Login element not found.")
        
def navigate_to_direct_messages(driver):
    """
    Navigates to Twitter's Direct Messages inbox.
    """
    driver.get("https://twitter.com/messages")
    random_delay(3, 5)
    try:
        # Wait until the messages are loaded
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='DmActivityViewport']")))
        logging.info("Navigated to Direct Messages successfully.")
    except TimeoutException:
        logging.error("Failed to load Direct Messages inbox.")
import re

def extract_urls(text):
    """
    Extracts all URLs from the given text.

    :param text: String containing text with potential URLs.
    :return: List of extracted URLs.
    """
    # Regular expression pattern for URLs
    url_pattern = re.compile(r'(https?://\S+)')
    return url_pattern.findall(text)

def extract_visible_text(driver, chat_container):
    visible_texts = []
    try:
        # Find all message elements within the chat container
        messages = chat_container.find_elements(By.XPATH, ".//div[@data-testid='cellInnerDiv']")
        for message in messages:
            # Get the element's position relative to the viewport
            rect = driver.execute_script("""
                const rect = arguments[0].getBoundingClientRect();
                return {top: rect.top, bottom: rect.bottom};
            """, message)
            viewport_height = driver.execute_script("return window.innerHeight;")
            # Check if the message is within the visible viewport
            if 0 <= rect['top'] < viewport_height or 0 <= rect['bottom'] <= viewport_height:
                text_content = message.text.strip()
                if text_content:
                    visible_texts.append(text_content)  # Append the text content
    except Exception as e:
        logging.error(f"Error extracting text: {e}")
    return "\n".join(visible_texts)

def take_chat_screenshots(driver):
    """
    Takes screenshots of all chats in Instagram's direct messages and extracts visible text,
    ensuring the top-most chat content is also captured.
    """
    screenshots = []
    try:
        # Wait for chat list to load
        chat_list = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='tablist']"))
        )
        print("Chat list loaded successfully.")

        # Locate all chat elements
        chat_elements = chat_list.find_elements(By.XPATH, "//div[@data-testid='conversation']")
        print(f"Found {len(chat_elements)} chats.")

        for idx, chat in enumerate(chat_elements, start=1):
            try:
                # Click on each chat
                chat.click()
                print(f"Clicked on chat {idx}.")
                random_delay(2, 4)

                # Wait for chat container to load
                chat_container = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@data-testid='DmActivityViewport']"))
                )
                print(f"Chat container for chat {idx} located successfully.")

                scroll_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)
                client_height = driver.execute_script("return arguments[0].clientHeight", chat_container)

                # Handle scrolling chats
                if scroll_height > client_height:
                    print(f"Chat {idx} requires scrolling.")
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", chat_container)
                    random_delay(2, 4)

                    while True:
                        # Capture and save screenshots
                        screenshot_path = f'chat_{idx}_screenshot_{len(screenshots) + 1}.png'
                        driver.save_screenshot(screenshot_path)

                        # Extract visible text
                        extracted_text = extract_visible_text(driver, chat_container)
                        print(f"Extracted text from chat {idx}.")

                        screenshots.append({
                            'filename': screenshot_path,
                            'text': extracted_text
                        })

                        # Scroll up
                        driver.execute_script("arguments[0].scrollTop -= arguments[1];", chat_container, client_height)
                        random_delay(2, 4)

                        # Check if at the top
                        current_scroll_position = driver.execute_script("return arguments[0].scrollTop;", chat_container)
                        if current_scroll_position <= 0:
                            # Capture the top-most screenshot
                            screenshot_path = f'chat_{idx}_screenshot_top.png'
                            driver.save_screenshot(screenshot_path)

                            extracted_text = extract_visible_text(driver, chat_container)
                            print(f"Captured top-most content of chat {idx}.")

                            screenshots.append({
                                'filename': screenshot_path,
                                'text': extracted_text
                            })
                            break
                else:
                    print(f"Chat {idx} fits in one screen; no scrolling required.")

                    screenshot_path = f'chat_{idx}_screenshot.png'
                    driver.save_screenshot(screenshot_path)

                    extracted_text = extract_visible_text(driver, chat_container)
                    print(f"Extracted text from chat {idx}.")

                    screenshots.append({
                        'filename': screenshot_path,
                        'text': extracted_text
                    })

                # Return to chat list
                driver.back()
                print(f"Returned to chat list after processing chat {idx}.")
                random_delay(2, 4)

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error processing chat {idx}: {e}")
                driver.back()
                random_delay(2, 4)
                continue

    except TimeoutException:
        print("Failed to load the chat list.")
    except NoSuchElementException:
        print("No chat elements found.")

    return screenshots


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
def generate_pdf(screenshots,accused_name, case_data,username):
    """
    Generates a PDF from the provided screenshots with embedded extracted texts.
    :param screenshots: List of dictionaries with 'filename' and 'text' keys.
    :return: None (saves the PDF to a file).
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    parsing_date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    if accused_name or case_data:
        text_object = c.beginText(50, height - 50)
        text_object.setFont("Helvetica-Bold", 14)
        if accused_name:
            text_object.textLine(f"Accused Name: {accused_name}")
        if case_data:
            text_object.textLine(f"Case Data: {case_data}")
            text_object.textLine(f"Platform: Twitter")
            text_object.textLine(f"Options: Chats")
            text_object.textLine(f"Date and Time of Parsing: {parsing_date_time}")
            text_object.textLine(f"Username: {username}")
        c.drawText(text_object)
        c.showPage()
        
        
    reverse_screenshots = list(reversed(screenshots))  # To maintain chronological order
    for item in reverse_screenshots:
        screenshot = item['filename']
        extracted_text = item['text']
        try:
            # Set the fill color to white for the text
            c.setFillColorRGB(1, 1, 1)  # RGB for white
            # Draw the extracted text first (hidden behind the image)
            text_object = c.beginText(50, height - 50)  # Position text 50 pixels from the top-left corner
            text_object.setFont("Helvetica", 10)
            for line in extracted_text.split('\n'):
                if line.strip():  # Avoid adding empty lines
                    text_object.textLine(line)
            c.drawText(text_object)
            # Reset fill color to default (black) if needed
            c.setFillColorRGB(0, 0, 0)  # RGB for black
            # Overlay the screenshot image on top of the text
            img = Image.open(screenshot)
            img_width, img_height = img.size
            scale = min((width - 100) / img_width, (height - 100) / img_height)  # Leave 50 pixels margin on each side
            img_width = int(img_width * scale)
            img_height = int(img_height * scale)
            x_position = (width - img_width) / 2
            y_position = (height - img_height) / 2
            c.drawImage(screenshot, x_position, y_position, width=img_width, height=img_height)
            urls = extract_urls(extracted_text)
            if urls:
                hyperlink_y_start = y_position - 20  # 20 pixels below the screenshot
                hyperlink_x = x_position
                link_spacing = 15  # Space between links

                for url in urls:
                    c.setFillColorRGB(0, 0, 1)  # Blue color for hyperlinks
                    c.setFont("Helvetica-Oblique", 10)
                    c.drawString(hyperlink_x, hyperlink_y_start, url)
                    # Add hyperlink annotation
                    c.linkURL(url, (hyperlink_x, hyperlink_y_start, hyperlink_x + len(url)*6, hyperlink_y_start + 12), relative=0)
                    hyperlink_y_start -= link_spacing  # Move down for next lin
                    
            c.showPage()
            logging.info(f"Added {screenshot} to PDF with extracted text.")
        except Exception as e:
            logging.error(f"Error adding {screenshot} to PDF: {e}")
            continue
    c.save()
    buffer.seek(0)
    return buffer
   
def cleanup_screenshots(screenshots):
    """
    Deletes the individual screenshot files to save disk space.
    :param screenshots: List of dictionaries with 'filename' and 'text' keys.
    :return: None
    """
    for item in screenshots:
        try:
            os.remove(item['filename'])
            logging.info(f"Removed screenshot file: {item['filename']}")
        except Exception as e:
            logging.error(f"Error removing {item['filename']}: {e}")
            
def main(username, password, accused_name, case_data):
    # Setting up the Chrome driver with WebDriver Manager
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    # Optional: Run Chrome in headless mode
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        # Log in to Twitter
        login(driver, username, password)
        # Navigate to Direct Messages
        navigate_to_direct_messages(driver)
        # Take screenshots of chats along with extracted text
        chat_screenshots = take_chat_screenshots(driver)
        logging.info(f"Total screenshots taken: {len(chat_screenshots)}")
        # Generate PDF from chat screenshots and extracted texts
        if chat_screenshots:
            pdf_buffer = generate_pdf(chat_screenshots, accused_name, case_data, username)
            
            sys.stdout.buffer.write(pdf_buffer.getvalue())

            # Cleanup screenshot files
            cleanup_screenshots(chat_screenshots)
            return pdf_buffer
        else:
            logging.warning("No chat screenshots were taken.")
            sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        driver.quit()
        logging.info("WebDriver session closed.")
        
def parse_arguments():
    parser = argparse.ArgumentParser(description='Instagram Followers Parsing Script')
    parser.add_argument('--username', type=str, required=True, help='Instagram Username')
    parser.add_argument('--password', type=str, required=True, help='Instagram Password')
    parser.add_argument('--accusedName', type=str, help='Name of the Accused')
    parser.add_argument('--caseData', type=str, help='Case Data Information')
    return parser.parse_args()
if __name__ == "__main__":
    args = parse_arguments()
    main(
        username=args.username,
        password=args.password,
        accused_name=args.accusedName,
        case_data=args.caseData
    )