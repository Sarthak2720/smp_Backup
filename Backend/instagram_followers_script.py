import io
import sys
import time
from fileinput import filename

from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from selenium.common.exceptions import TimeoutException
from PIL import Image
import random
import argparse


# Setting up the Chrome driver
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def random_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))

def login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    time.sleep(5)

def navigate_to_followers(driver, username):
    try:
        # Navigate to the user's profile
        driver.get(f'https://www.instagram.com/{username}/')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print(f"Profile page loaded for {username}.")
        
        # Wait for the followers link and click it
        followers_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "followers"))
        )
        followers_link.click()
        print("Followers link clicked.")
        random_delay(2, 4)  # Add random delay for stability
    except NoSuchElementException:
        print("Followers link not found. Verify UI structure or username.")
    except TimeoutException:
        print("Timeout while waiting for the followers link.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def take_followers_screenshots(driver):
    screenshots = []
    try:
        scroll_boxii = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
        )
        print("Followers modal loaded successfully.")
        scroll_box = scroll_boxii.find_element(By.XPATH, ".//div[contains(@class, 'xyi19xy')]")
    except TimeoutException:
        print("Failed to load the followers modal.")
        return screenshots

    last_height = driver.execute_script("return arguments[0].scrollTop", scroll_box)
    max_scroll_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)

    while True:
        # Take a screenshot
        screenshot_filename = f'followers_screenshot_{len(screenshots) + 1}.png'
        driver.save_screenshot(screenshot_filename)
        screenshots.append(screenshot_filename)
        print(f"Screenshot taken: {screenshot_filename}")

        # Scroll down and wait for content to load
        driver.execute_script("arguments[0].scrollTop += arguments[0].clientHeight;", scroll_box)
        time.sleep(4)  # Wait for new content to load

        # Check if the scroll has reached the bottom
        new_height = driver.execute_script("return arguments[0].scrollTop", scroll_box)
        if new_height == last_height:  # Bottom of the scroll
            break
        last_height = new_height

    return screenshots


def take_followings_screenshots(driver):
    screenshots = []
    try:
        scroll_boxi = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
        )
        print("Followings modal loaded successfully.")
        scroll_box = scroll_boxi.find_element(By.XPATH, ".//div[contains(@class, 'xyi19xy')]")
    except TimeoutException:
        print("Failed to load the followings modal.")
        return screenshots

    last_height = driver.execute_script("return arguments[0].scrollTop", scroll_box)
    max_scroll_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)

    while True:
        # Take a screenshot
        screenshot_filename = f'followings_screenshot_{len(screenshots) + 1}.png'
        driver.save_screenshot(screenshot_filename)
        screenshots.append(screenshot_filename)
        print(f"Screenshot taken: {screenshot_filename}")

        # Scroll down and wait for content to load
        driver.execute_script("arguments[0].scrollTop += arguments[0].clientHeight;", scroll_box)
        time.sleep(4)  # Wait for new content to load

        # Check if the scroll has reached the bottom
        new_height = driver.execute_script("return arguments[0].scrollTop", scroll_box)
        if new_height == last_height:  # Bottom of the scroll
            break
        last_height = new_height

    return screenshots


# def take_followers_screenshots(driver):
#     screenshots = []
#     try:
#         scroll_box = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
#         )
#         print("Followers modal loaded successfully.")
#         scroll_box = scroll_box.find_element(By.XPATH, ".//div[contains(@class, 'xyi19xy')]")
#     except TimeoutException:
#         print("Failed to load the followers modal.")
#         return screenshots
#     except NoSuchElementException:
#         print("Scrollable area not found.")
#         return screenshots

#     last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)

#     while True:
#         screenshot_filename = f'followers_screenshot_{len(screenshots) + 1}.png'
#         driver.save_screenshot(screenshot_filename)
#         screenshots.append(screenshot_filename)
#         print(f"Screenshot taken: {screenshot_filename}")

#         # Vary the scroll speed
#         scroll_delay = random.uniform(2, 4)
#         driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
#         random_delay(scroll_delay, scroll_delay + 2)

#         new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)
#         if new_height == last_height:
#             break
#         last_height = new_height

#     return screenshots


def navigate_to_followings(driver, username):
    driver.get(f'https://www.instagram.com/{username}')
    time.sleep(5)
    followings_link = driver.find_element(By.PARTIAL_LINK_TEXT, "following")
    followings_link.click()
    time.sleep(2)
    
# def take_followings_screenshots(driver):
#     screenshots = []
#     try:
#         scroll_box = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
#         )
#         print("Followings modal loaded successfully.")
#         scroll_box = scroll_box.find_element(By.XPATH, ".//div[contains(@class, 'xyi19xy')]")
#     except TimeoutException:
#         print("Failed to load the followings modal.")
#         return screenshots
#     except NoSuchElementException:
#         print("Scrollable area not found.")
#         return screenshots

#     last_height = driver.execute_script("return arguments[0].scrollTop", scroll_box)
#     max_scroll_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)

#     while True:
#         # Take a screenshot
#         screenshot_filename = f'followings_screenshot_{len(screenshots) + 1}.png'
#         driver.save_screenshot(screenshot_filename)
#         screenshots.append(screenshot_filename)
#         print(f"Screenshot taken: {screenshot_filename}")

#         # Scroll down slightly and refetch the scroll_box to avoid stale element exception
#         try:
#             scroll_step = 200  # Amount to scroll down in each step
#             driver.execute_script("arguments[0].scrollTop += arguments[1];", scroll_box, scroll_step)
#             time.sleep(2)  # Wait for the content to load
#             scroll_box = driver.find_element(By.XPATH, "//div[@role='dialog']")
#         except StaleElementReferenceException:
#             scroll_box = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
#             )
#             print("Refetched scroll_box to avoid stale element exception.")

#         # Check if we have reached the bottom
#         new_height = driver.execute_script("return arguments[0].scrollTop", scroll_box)
#         if new_height + scroll_step >= max_scroll_height:  # Close to the bottom
#             break
#         last_height = new_height

#     # Final screenshot for the last part
#     screenshot_filename = f'followings_screenshot_{len(screenshots) + 1}_final.png'
#     driver.save_screenshot(screenshot_filename)
#     screenshots.append(screenshot_filename)
#     print(f"Final Screenshot taken: {screenshot_filename}")

#     return screenshots



def navigate_to_profile(driver,username):
    # Navigate back to the profile page
    driver.get(f'https://www.instagram.com/{username}/')  # Replace with the actual URL

def dismiss_suspicious_activity_modal(driver):
    try:
        # Wait for the modal to appear
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@role, 'dialog')]"))
        )

        # Optionally wait before dismissing
        random_delay(2, 4)

        # Check for the dismiss button within the modal
        dismiss_button = driver.find_element(By.XPATH,
                                             "//button[contains(text(), 'Dismiss')] | //button[contains(text(), 'Close')]")
        dismiss_button.click()  # Click the dismiss button
        print("Dismissed suspicious activity modal.")

    except TimeoutException:
        print("No suspicious activity modal detected.")
    except NoSuchElementException:
        print("Dismiss button not found.")

def generate_combined_pdf(followers_screenshots, followings_screenshots, accused_name, case_data,username):
    """
    Generates a combined PDF from followers and followings screenshots with additional case information.

    :param followers_screenshots: List of follower screenshot filenames.
    :param followings_screenshots: List of following screenshot filenames.
    :param accused_name: Name of the accused.
    :param case_data: Additional case data.
    :return: BytesIO buffer containing the PDF data.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    parsing_date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    # Add Accused Name and Case Data at the beginning of the PDF
    if accused_name or case_data:
        text_object = c.beginText(50, height - 50)
        text_object.setFont("Helvetica-Bold", 14)
        if accused_name:
            text_object.textLine(f"Accused Name: {accused_name}")
        if case_data:
            text_object.textLine(f"Case Data: {case_data}")
            text_object.textLine(f"Platform: Instagram")
            text_object.textLine(f"Options: Followers and Followings")
            text_object.textLine(f"Date and Time of Parsing: {parsing_date_time}")
            text_object.textLine(f"Username: {username}")
            
        c.drawText(text_object)
        c.showPage()

    # Add Followers Screenshots
    for idx, screenshot in enumerate(followers_screenshots, start=1):
        try:
            # Add screenshot image
            img = Image.open(screenshot)
            img_width, img_height = img.size
            scale = min((width - 100) / img_width, (height - 150) / img_height)
            img_width = int(img_width * scale)
            img_height = int(img_height * scale)
            x_position = (width - img_width) / 2
            y_position = height - img_height - 100
            c.drawImage(screenshot, x_position, y_position, width=img_width, height=img_height)

            # Add caption or additional information if needed
            c.setFont("Helvetica", 12)
            c.drawString(50, y_position - 20, f"Followers Screenshot {idx}")

            c.showPage()
        except Exception as e:
            print(f"Error adding {screenshot} to PDF: {e}")
            continue

    # Add Followings Screenshots
    for idx, screenshot in enumerate(followings_screenshots, start=1):
        try:
            # Add screenshot image
            img = Image.open(screenshot)
            img_width, img_height = img.size
            scale = min((width - 100) / img_width, (height - 150) / img_height)
            img_width = int(img_width * scale)
            img_height = int(img_height * scale)
            x_position = (width - img_width) / 2
            y_position = height - img_height - 100
            c.drawImage(screenshot, x_position, y_position, width=img_width, height=img_height)

            # Add caption or additional information if needed
            c.setFont("Helvetica", 12)
            c.drawString(50, y_position - 20, f"Followings Screenshot {idx}")

            c.showPage()
        except Exception as e:
            print(f"Error adding {screenshot} to PDF: {e}")
            continue

    c.save()
    buffer.seek(0)
    return buffer

def main(username, password,accused_name,case_data):
    # Setting up the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        # Add Chrome options if needed
        login(driver, username, password)  # Log in to Instagram
        dismiss_suspicious_activity_modal(driver)  # Dismiss any suspicious activity popup
        navigate_to_followers(driver, username)  # Pass username
        followers_screenshots = take_followers_screenshots(driver)  # Capture followers screenshots

        navigate_to_followings(driver, username)  # Pass username
        followings_screenshots = take_followings_screenshots(driver)  # Capture followings screenshots

        # Generate combined PDF
        pdf_buffer = generate_combined_pdf(followers_screenshots, followings_screenshots,accused_name,case_data,username)

        # Write PDF to standard output (or save to file)
        sys.stdout.buffer.write(pdf_buffer.getvalue())

    finally:
        driver.quit()  # Ensure the driver is closed after execution

def parse_arguments():
    parser = argparse.ArgumentParser(description='Instagram Followers Parsing Script')
    parser.add_argument('--username', type=str, required=True, help='Instagram Username')
    parser.add_argument('--password', type=str, required=True, help='Instagram Password')
    parser.add_argument('--accusedName', type=str, help='Name of the Accused')
    parser.add_argument('--caseData', type=int, help='Case Data Information')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    main(
        username=args.username,
        password=args.password,
        accused_name=args.accusedName,
        case_data=args.caseData
    )
