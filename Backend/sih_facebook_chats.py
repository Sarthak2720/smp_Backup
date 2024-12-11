import io
import os
import sys
import time
import random
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import argparse
import re
def random_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))

def login(driver, username, password):
    driver.get("https://www.facebook.com/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(username)
    driver.find_element(By.NAME, "pass").send_keys(password)
    driver.find_element(By.NAME, "pass").send_keys(Keys.RETURN)
    time.sleep(5)

def navigate_to_messenger(driver):
    driver.get("https://www.facebook.com/messages/t/")
    random_delay(4, 5)  # Random delay after loading the Messenger page

def extract_urls(text):
    """
    Extracts all URLs from the given text.

    :param text: String containing the text to search for URLs.
    :return: List of extracted URLs.
    """
    url_pattern = re.compile(r'(https?://\S+)')
    return url_pattern.findall(text)

def extract_visible_text_facebook(driver, chat_container):
    """
    Extracts the text of all messages currently visible in the Facebook chat_container.

    :param driver: Selenium WebDriver instance.
    :param chat_container: WebElement representing the Facebook chat container.
    :return: Concatenated string of visible message texts.
    """
    visible_texts = []
    try:
        # Locate all message text elements within the chat container.
        # Update the XPath based on Facebook's current DOM structure.
        messages = chat_container.find_elements(
            By.XPATH,
            ".//div[contains(@dir, 'auto')]"  # Replace with the actual class
        )

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
    except Exception as e:
        print(f"Error extracting Facebook text: {e}")

    return "\n".join(visible_texts)

def take_chat_screenshots(driver):
    """
    Takes screenshots of each chat by scrolling through the messages and extracts visible text.

    :param driver: Selenium WebDriver instance.
    :return: List of dictionaries containing screenshot filenames and extracted texts.
    """
    screenshots = []
    try:
        # Wait for the chat list to load
        chat_list = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Chats']"))
        )
        print("Chat list loaded successfully.")

        # Capture the first chat that automatically opens
        try:
            time.sleep(8)
            chat_container = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "(//div[contains(@class, 'x78zum5') and contains(@class, 'xdt5ytf') and contains(@class, 'x1iyjqo2') and contains(@class, 'x6ikm8r') and contains(@class, 'x1odjw0f') and contains(@class, 'xish69e') and contains(@class, 'x16o0dkt')])[2]"))
            )
            print("First chat container loaded successfully.")
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

            # Check if the chat container is scrollable
            scroll_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)
            client_height = driver.execute_script("return arguments[0].clientHeight", chat_container)

            if scroll_height > client_height:
                chat_container_height = client_height

                while True:
                    # Take a screenshot of the current view of the chat
                    screenshot_filename = f'chat_screenshot_{len(screenshots) + 1}.png'
                    driver.save_screenshot(screenshot_filename)
                    print(f"Screenshot taken: {screenshot_filename}")

                    # Extract visible text after taking the screenshot
                    visible_text = extract_visible_text_facebook(driver, chat_container)

                    screenshots.append({
                        'filename': screenshot_filename,
                        'text': visible_text
                    })

                    # Scroll up by the height of the chat container
                    driver.execute_script("arguments[0].scrollTop -= arguments[1];", chat_container, chat_container_height)
                    random_delay(5, 8)  # Wait for the messages to load

                    # Check if we can still scroll
                    current_scroll_position = driver.execute_script("return arguments[0].scrollTop;", chat_container)
                    if current_scroll_position == 0:
                        # Take an additional screenshot at the top before breaking
                        screenshot_filename = f'chat_screenshot_{len(screenshots) + 1}.png'
                        driver.save_screenshot(screenshot_filename)
                        print(f"Screenshot taken at the top: {screenshot_filename}")

                        visible_text = extract_visible_text_facebook(driver, chat_container)
                        screenshots.append({
                            'filename': screenshot_filename,
                            'text': visible_text
                        })
                        break
            else:
                # If the chat is not scrollable, take a single screenshot
                screenshot_filename = f'chat_screenshot_{len(screenshots) + 1}.png'
                driver.save_screenshot(screenshot_filename)
                print(f"Screenshot taken: {screenshot_filename}")

                visible_text = extract_visible_text_facebook(driver, chat_container)
                screenshots.append({
                    'filename': screenshot_filename,
                    'text': visible_text
                })

        except TimeoutException:
            print("Failed to locate or capture the first chat.")

        # After capturing the first chat, move on to other chats
        chat_elements = chat_list.find_elements(By.XPATH, "//a[contains(@class, 'x1i10hfl') and contains(@class, 'x1qjc9v5') and contains(@class, 'xjbqb8w') and contains(@class, 'xjqpnuy') and contains(@class, 'xa49m3k') and contains(@class, 'xqeqjp1') and contains(@class, 'x2hbi6w') and contains(@class, 'x13fuv20') and contains(@class, 'xu3j5b3') and contains(@class, 'x1q0q8m5') and contains(@class, 'x26u7qi') and contains(@class, 'x972fbf') and contains(@class, 'xcfux6l') and contains(@class, 'x1qhh985') and contains(@class, 'xm0m39n') and contains(@class, 'x9f619') and contains(@class, 'x1ypdohk') and contains(@class, 'xdl72j9') and contains(@class, 'x2lah0s') and contains(@class, 'xe8uvvx') and contains(@class, 'xdj266r') and contains(@class, 'x11i5rnm') and contains(@class, 'xat24cr') and contains(@class, 'x1mh8g0r') and contains(@class, 'x2lwn1j') and contains(@class, 'xeuugli') and contains(@class, 'xexx8yu') and contains(@class, 'x4uap5') and contains(@class, 'x18d9i69') and contains(@class, 'xkhd6sd') and contains(@class, 'x1n2onr6') and contains(@class, 'x16tdsg8') and contains(@class, 'x1hl2dhg') and contains(@class, 'xggy1nq') and contains(@class, 'x1ja2u2z') and contains(@class, 'x1t137rt') and contains(@class, 'x1o1ewxj') and contains(@class, 'x3x9cwd') and contains(@class, 'x1e5q0jg') and contains(@class, 'x13rtm0m') and contains(@class, 'x1q0g3np') and contains(@class, 'x87ps6o') and contains(@class, 'x1lku1pv') and contains(@class, 'x1a2a7pz') and contains(@class, 'x1lliihq')]")
        print(f"Found {len(chat_elements)} other chats.")

        for chat in chat_elements:
            chat.click()  # Open the chat
            random_delay(4, 5)  # Wait for the chat to load
            time.sleep(8)

            # Locate the chat message container
            chat_container = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "(//div[contains(@class, 'x78zum5') and contains(@class, 'xdt5ytf') and contains(@class, 'x1iyjqo2') and contains(@class, 'x6ikm8r') and contains(@class, 'x1odjw0f') and contains(@class, 'xish69e') and contains(@class, 'x16o0dkt')])[2]"))
            )
            print("Chat container loaded successfully.")

            # Check if the chat container is scrollable
            scroll_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)
            client_height = driver.execute_script("return arguments[0].clientHeight", chat_container)

            if scroll_height > client_height:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", chat_container)
                random_delay(2, 3)

                while True:
                    # Take a screenshot of the current view
                    screenshot_filename = f'chat_screenshot_{len(screenshots) + 1}.png'
                    driver.save_screenshot(screenshot_filename)
                    print(f"Screenshot taken: {screenshot_filename}")

                    # Extract visible text after taking the screenshot
                    visible_text = extract_visible_text_facebook(driver, chat_container)

                    screenshots.append({
                        'filename': screenshot_filename,
                        'text': visible_text
                    })

                    # Scroll up by the height of the chat container
                    driver.execute_script("arguments[0].scrollTop -= arguments[1];", chat_container, chat_container_height)
                    random_delay(5, 8)  # Wait for the messages to load

                    # Check if we can still scroll
                    current_scroll_position = driver.execute_script("return arguments[0].scrollTop;", chat_container)
                    if current_scroll_position == 0:
                        # Take an additional screenshot at the top before breaking
                        screenshot_filename = f'chat_screenshot_{len(screenshots) + 1}.png'
                        driver.save_screenshot(screenshot_filename)
                        print(f"Screenshot taken at the top: {screenshot_filename}")

                        visible_text = extract_visible_text_facebook(driver, chat_container)
                        screenshots.append({
                            'filename': screenshot_filename,
                            'text': visible_text
                        })
                        break
            else:
                # If the chat is not scrollable, take a single screenshot
                screenshot_filename = f'chat_screenshot_{len(screenshots) + 1}.png'
                driver.save_screenshot(screenshot_filename)
                print(f"Screenshot taken: {screenshot_filename}")

                visible_text = extract_visible_text_facebook(driver, chat_container)
                screenshots.append({
                    'filename': screenshot_filename,
                    'text': visible_text
                })

    except TimeoutException:
        print("Failed to load the chat list.")
    except NoSuchElementException:
        print("No chat elements found.")

    return screenshots


def generate_pdf(screenshots,accused_name, case_data,username):
    """
    Generates a PDF from the provided screenshots with embedded extracted texts.

    :param screenshots: List of dictionaries with 'filename' and 'text' keys.
    :return: None (saves the PDF to a file).
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    reverse_screenshots = list(reversed(screenshots))  # To maintain chronological order
    parsing_date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    
    if accused_name or case_data:
        text_object = c.beginText(50, height - 50)
        text_object.setFont("Helvetica-Bold", 14)
        if accused_name:
            text_object.textLine(f"Accused Name: {accused_name}")
        if case_data:
            text_object.textLine(f"Case Data: {case_data}")
            text_object.textLine(f"Platform: Facebook")
            text_object.textLine(f"Options: Chats")
            text_object.textLine(f"Date and Time of Parsing: {parsing_date_time}")
            text_object.textLine(f"Username: {username}")
        c.drawText(text_object)
        c.showPage()

    for item in reverse_screenshots:
        screenshot = item['filename']
        extracted_text = item['text']

        try:
            # Draw the extracted text at the top of the page
            text_object = c.beginText(50, height - 50)  # 50 pixels from the top-left corner
            text_object.setFont("Helvetica", 10)
            for line in extracted_text.split('\n'):
                if line.strip():
                    text_object.textLine(line)
            c.drawText(text_object)
            
            c.setFillColorRGB(1, 1, 1)  # RGB for black
            

            # Overlay the screenshot image below the text
            img = Image.open(screenshot)
            img_width, img_height = img.size
            scale = min((width - 100) / img_width, (height - 150) / img_height)  # Leave margins
            img_width = int(img_width * scale)
            img_height = int(img_height * scale)
            x_position = (width - img_width) / 2
            y_position = 50  # Position image 50 pixels from the bottom
            c.drawImage(screenshot, x_position, y_position, width=img_width, height=img_height)
            urls = extract_urls(extracted_text)

            if urls:
                # Position below the image
                link_y_position = y_position - img_height - 60  # Adjust as needed

                for url in urls:
                    # Draw the URL text
                    c.setFont("Helvetica-Oblique", 10)
                    c.drawString(50, link_y_position, url)

                    # Make the URL clickable
                    c.linkURL(url, (50, link_y_position - 2, 300, link_y_position + 10), relative=0)

                    # Update the Y position for the next link
                    link_y_position -= 15    
            c.showPage()
            print(f"Added {screenshot} to PDF with extracted text.")

        except Exception as e:
            print(f"Error adding {screenshot} to PDF: {e}")
            continue

    c.save()
    buffer.seek(0)
    return buffer
    
def parse_arguments():
    parser = argparse.ArgumentParser(description='Instagram Followers Parsing Script')
    parser.add_argument('--username', type=str, required=True, help='Instagram Username')
    parser.add_argument('--password', type=str, required=True, help='Instagram Password')
    parser.add_argument('--accusedName', type=str, help='Name of the Accused')
    parser.add_argument('--caseData', type=str, help='Case Data Information')
    return parser.parse_args()
 
    
if __name__ == "__main__":
    args = parse_arguments()
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    # chrome_options.add_argument("--headless")  # Uncomment to run in headless mode
    chrome_options.add_argument("--disable-popup-blocking")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        login(driver, username=args.username, password=args.password)
        navigate_to_messenger(driver)
        chat_screenshots = take_chat_screenshots(driver)

        if chat_screenshots:
            pdf_buffer=generate_pdf(chat_screenshots,accused_name=args.accusedName,case_data=args.caseData,username = args.username)
            print("PDF saved locally as facebook_chats.pdf")
            sys.stdout.buffer.write(pdf_buffer.getvalue())
            # Optional: Cleanup screenshot files
            for item in chat_screenshots:
                try:
                    os.remove(item['filename'])
                    print(f"Deleted screenshot: {item['filename']}")
                except Exception as e:
                    print(f"Error deleting {item['filename']}: {e}")
        else:
            print("No chat screenshots were taken.", file=sys.stderr)
            sys.exit(1)
    finally:
        driver.quit()