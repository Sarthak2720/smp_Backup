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
import argparse
import logging
import re

# Configure logging
# logging.basicConfig(
#     filename='instagram_chats.log',
#     filemode='a',
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     level=print
# )

def random_delay(min_delay=1, max_delay=3):
    """
    Introduces a random delay between min_delay and max_delay seconds.
    """
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

def login(driver, username, password):
    """
    Logs into Instagram using the provided credentials.
    """
    driver.get("https://www.instagram.com/accounts/login/")
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username")))
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        print("Entered username and password.")
        random_delay(5, 7)
    except TimeoutException:
        print("Login elements not found within the timeout period.")
    except NoSuchElementException:
        print("Login elements not found on the page.")

def navigate_to_direct_messages(driver):
    """
    Navigates to Instagram's Direct Messages inbox.
    """
    driver.get("https://www.instagram.com/direct/inbox/")
    random_delay(3, 5)
    try:
        # Handle "Turn On" notifications if present
        try:
            turn_on_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Turn On']"))
            )
            turn_on_button.click()
            print("Clicked on 'Turn On' button.")
            random_delay(2, 4)
        except TimeoutException:
            print("'Turn On' button not found. Continuing.")

        # Wait until the chats are loaded
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Chats']"))
        )
        print("Navigated to Direct Messages successfully.")
    except TimeoutException:
        print("Failed to load Direct Messages inbox.")
        
def extract_urls(text):
    """
    Extracts all URLs from the given text.

    :param text: String containing the text to search for URLs.
    :return: List of extracted URLs.
    """
    url_pattern = re.compile(r'(https?://\S+)')
    return url_pattern.findall(text)

def extract_chat_text(driver, chat_container):
    """
    Extracts the text of all messages currently visible in the chat_container.

    :param driver: Selenium WebDriver instance.
    :param chat_container: WebElement representing the chat container.
    :return: Concatenated string of visible message texts.
    """
    visible_texts = []
    try:
        # Find all message elements within the chat container
        messages = chat_container.find_elements(By.XPATH, "//div[contains(@class, 'xdj266r') and contains(@class, 'x11i5rnm') and contains(@class, 'xat24cr') and contains(@class, 'x1mh8g0r') and contains(@class, 'xexx8yu') and contains(@class, 'x4uap5') and contains(@class, 'x18d9i69') and contains(@class, 'xkhd6sd') and contains(@class, 'x6ikm8r') and contains(@class, 'x10wlt62')]")
        for message in messages:
            try:
                sender = message.find_element(By.XPATH, "//div[contains(@class, 'xexx8yu') and contains(@class, 'x4uap5') and contains(@class, 'x18d9i69') and contains(@class, 'xkhd6sd') and contains(@class, 'x1gslohp') and contains(@class, 'x11i5rnm') and contains(@class, 'x12nagc') and contains(@class, 'x1mh8g0r') and contains(@class, 'x1yc453h') and contains(@class, 'x126k92a') and contains(@class, 'xyk4ms5')]").text
                text = message.find_element(By.XPATH, ".//span[contains(@class, 'x1iyjqo2')]").text
                visible_texts.append(f"{sender}: {text}")
            except NoSuchElementException:
                continue
    except Exception as e:
        print(f"Error extracting text: {e}")
    return "\n".join(visible_texts)

def take_chat_screenshots(driver):
    """
    Takes screenshots of each chat by scrolling through the messages and extracts visible text.

    :param driver: Selenium WebDriver instance.
    :return: List of dictionaries containing screenshot filenames and extracted texts.
    """
    screenshots = []
    try:
        chat_list = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Chats'][@role='list']"))
        )
        print("Chat list loaded successfully.")

        chat_elements = chat_list.find_elements(By.XPATH, "//div[@role='listitem']")
        print(f"Found {len(chat_elements)} chats.")

        for idx, chat in enumerate(chat_elements, start=1):
            try:
                chat.click()
                print(f"Clicked on chat {idx}.")
                random_delay(2, 3)

                chat_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "(//div[contains(@class, 'x78zum5') and contains(@class, 'xdt5ytf') and contains(@class, 'x1iyjqo2') and contains(@class, 'xs83m0k') and contains(@class, 'x1xzczws') and contains(@class, 'x6ikm8r') and contains(@class, 'x1odjw0f') and contains(@class, 'x1n2onr6') and contains(@class, 'xh8yej3') and contains(@class, 'x16o0dkt')])[2]")
                    )
                )
                print(f"Chat container for chat {idx} located successfully.")
                random_delay(2,2)

                # Scroll to load messages
                scroll_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)
                client_height = driver.execute_script("return arguments[0].clientHeight", chat_container)

                if scroll_height > client_height:
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", chat_container)
                    random_delay(2, 3)

                    while True:
                        screenshot_filename = f'chat_{idx}_screenshot_{len(screenshots) + 1}.png'
                        driver.save_screenshot(screenshot_filename)

                        # Extract visible text
                        extracted_text = extract_chat_text(driver, chat_container)
                        print(f"Extracted text from chat {idx}.")

                        screenshots.append({
                            'filename': screenshot_filename,
                            'text': extracted_text
                        })
                        print(f"Screenshot taken: {screenshot_filename} | Extracted Text: {extracted_text[:50]}...")

                        # Scroll up by the client height to capture new messages
                        driver.execute_script("arguments[0].scrollTop -= arguments[1];", chat_container, client_height)
                        random_delay(2, 3)

                        current_scroll_position = driver.execute_script("return arguments[0].scrollTop;", chat_container)
                        if current_scroll_position <= 0:
                            print(f"Reached the top of chat {idx}.")
                            break
                else:
                    screenshot_filename = f'chat_{idx}_screenshot_{len(screenshots) + 1}.png'
                    driver.save_screenshot(screenshot_filename)

                    # Extract visible text
                    extracted_text = extract_chat_text(driver, chat_container)
                    print(f"Extracted text from chat {idx}.")

                    screenshots.append({
                        'filename': screenshot_filename,
                        'text': extracted_text
                    })
                    print(f"Screenshot taken: {screenshot_filename} | Extracted Text: {extracted_text[:50]}...")

                driver.back()
                print(f"Returned to chat list after processing chat {idx}.")
                random_delay(2, 3)

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error processing chat {idx}: {e}")
                driver.back()
                random_delay(2, 2)
                continue

    except TimeoutException:
        print("Failed to load the chat list.")
    except NoSuchElementException:
        print("No chat elements found.")

    return screenshots

def generate_pdf(screenshots,accused_name, case_data,username):
    """
    Generates a PDF from the provided screenshots with embedded extracted texts.

    :param screenshots: List of dictionaries with 'filename' and 'text' keys.
    :return: BytesIO buffer containing the PDF data.
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
            text_object.textLine(f"Platform: Instagram")
            text_object.textLine(f"Options: Chats")
            text_object.textLine(f"Date and Time of Parsing: {parsing_date_time}")
            text_object.textLine(f"Username: {username}")

        c.drawText(text_object)
        c.showPage()

    
    for item in screenshots:
        screenshot = item['filename']
        extracted_text = item['text']

        try:
            # Add extracted text
            text_object = c.beginText(50, height - 50)
            text_object.setFont("Helvetica", 12)
            for line in extracted_text.split('\n'):
                if line.strip():
                    text_object.textLine(line)
            c.drawText(text_object)

            # Add screenshot below the text
            img = Image.open(screenshot)
            img_width, img_height = img.size
            scale = min((width - 100) / img_width, (height - 150) / img_height)
            img_width = int(img_width * scale)
            img_height = int(img_height * scale)
            x_position = (width - img_width) / 2
            y_position = height - img_height - 100
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
            print(f"Added {screenshot} and extracted text to PDF.")

        except Exception as e:
            print(f"Error adding {screenshot} to PDF: {e}")
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
            print(f"Removed screenshot file: {item['filename']}")
        except Exception as e:
            print(f"Error removing {item['filename']}: {e}")

def main(username, password,accused_name,case_data):
    """
    Main function to execute the Instagram chat screenshot and PDF generation.

    :param username: Instagram username.
    :param password: Instagram password.
    :return: None
    """
    # Setting up the Chrome driver with WebDriver Manager
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    # Optional: Run Chrome in headless mode
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Log in to Instagram
        login(driver, username, password)
        # Navigate to Direct Messages
        navigate_to_direct_messages(driver)
        # Take screenshots of chats along with extracted text
        chat_screenshots = take_chat_screenshots(driver)
        print(f"Total screenshots taken: {len(chat_screenshots)}")

        # Generate PDF from chat screenshots and extracted texts
        if chat_screenshots:
            pdf_buffer = generate_pdf(chat_screenshots, accused_name, case_data,username)
            # Save PDF to a file
            pdf_filename = "instagram_chats.pdf"
            sys.stdout.buffer.write(pdf_buffer.getvalue())
        else:
            print("No chat screenshots were taken.", file=sys.stderr)
            sys.exit(1)


    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        driver.quit()
        print("WebDriver session closed.")

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
