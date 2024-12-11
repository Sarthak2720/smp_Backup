from curses import window
import io
import sys
import time
import random
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
# Your Twitter credentials
# username = 'DhwaniJain87055'
# password = 'm12veenanagar'
# gmail = 'dhwanijain2601@gmail.com'  # Replace with your Gmail

# Setting up the Chrome driver
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def random_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))


def handle_suspicious_activity_modal(driver, gmail):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "challenge_response")))
        driver.find_element(By.NAME, "challenge_response").send_keys(gmail)
        driver.find_element(By.NAME, "challenge_response").send_keys(Keys.RETURN)
        random_delay(2, 4)
    except TimeoutException:
        print("No suspicious activity prompt found.")
    except NoSuchElementException:
        print("Suspicious activity modal element not found.")


def login(driver, username, password):
    driver.get("https://twitter.com/login")
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "text")))
        driver.find_element(By.NAME, "text").send_keys(username)
        driver.find_element(By.NAME, "text").send_keys(Keys.RETURN)
        random_delay(2, 4)

        # handle_suspicious_activity_modal(driver, gmail)

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "password")))
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(5)
    except TimeoutException:
        print("Loading took too much time! - Login element not found")
    except NoSuchElementException:
        print("No such element - Login element not found")


def navigate_to_followers(driver,username):
    driver.get(f'https://twitter.com/{username}/followers')
    random_delay(3, 5)

def navigate_to_following(driver,username):
    driver.get(f'https://twitter.com/{username}/following')
    random_delay(3, 5)

def take_followers_screenshots(driver):
    screenshots = []
    try:
        # Wait for the followers page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Timeline: Followers']"))
        )
        print("Followers page loaded successfully.")
        random_delay(4,5)
        # Initial scroll position
        last_position = driver.execute_script("return window.scrollY;")
        while True:
            # Take screenshot
            screenshot_filename = f'followers_screenshot_{len(screenshots) + 1}.png'
            driver.save_screenshot(screenshot_filename)
            screenshots.append(screenshot_filename)
            print(f"Screenshot taken: {screenshot_filename}")

            # Scroll down by a smaller amount (e.g., 500px)
            driver.execute_script("window.scrollBy(0, 500);")
            random_delay(2, 4)  # Optional delay to mimic human behavior

            # Check if we've reached the bottom of the page
            new_position = driver.execute_script("return window.scrollY;")
            if new_position == last_position:
                print("Reached the bottom of the page.")
                break
            last_position = new_position

    except TimeoutException:
        print("Failed to load the followers timeline.")
    except NoSuchElementException:
        print("Followers element not found.")

    return screenshots


def take_following_screenshots(driver):
    screenshots = []
    try:
        # Wait for the following page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Timeline: Following']"))
        )
        print("Following page loaded successfully.")
        random_delay(4,5)
        # Initial scroll position
        last_position = driver.execute_script("return window.scrollY;")
        while True:
            # Take screenshot
            screenshot_filename = f'following_screenshot_{len(screenshots) + 1}.png'
            driver.save_screenshot(screenshot_filename)
            screenshots.append(screenshot_filename)
            print(f"Screenshot taken: {screenshot_filename}")

            # Scroll down by a smaller amount (e.g., 500px)
            driver.execute_script("window.scrollBy(0, 500);")
            random_delay(2, 4)  # Optional delay to mimic human behavior

            # Check if we've reached the bottom of the page
            new_position = driver.execute_script("return window.scrollY;")
            if new_position == last_position:
                print("Reached the bottom of the page.")
                break
            last_position = new_position

    except TimeoutException:
        print("Failed to load the following timeline.")
    except NoSuchElementException:
        print("Following element not found.")

    return screenshots


def generate_combined_pdf(followers_screenshots, followings_screenshots,accused_name,case_data,username):
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
            text_object.textLine(f"Options: Followers and Followings")
            text_object.textLine(f"Date and Time of Parsing: {parsing_date_time}")
            text_object.textLine(f"Username: {username}")
        c.drawText(text_object)
        c.showPage()

    # Add followers screenshots
    if followers_screenshots:
        c.drawString(100, height - 50, "Followers")  # Add a title for the section
        for screenshot in followers_screenshots:
            img = Image.open(screenshot)
            img_width, img_height = img.size
            scale = min(width / img_width, height / img_height)
            img_width = int(img_width * scale)
            img_height = int(img_height * scale)
            c.drawImage(screenshot, 0, height - img_height, width=img_width, height=img_height)
            c.showPage()

    # Add followings screenshots
    if followings_screenshots:
        c.drawString(100, height - 50, "Followings")  # Add a title for the section
        for screenshot in followings_screenshots:
            img = Image.open(screenshot)
            img_width, img_height = img.size
            scale = min(width / img_width, height / img_height)
            img_width = int(img_width * scale)
            img_height = int(img_height * scale)
            c.drawImage(screenshot, 0, height - img_height, width=img_width, height=img_height)
            c.showPage()

    c.save()
    buffer.seek(0)
    return buffer

# if __name__ == "__main__":
#     try:
#         login(driver, username, password, gmail)

#         navigate_to_followers(driver)
#         followers_screenshots = take_followers_screenshots(driver)
#         if followers_screenshots:
#             generate_pdf(followers_screenshots, filename='followers.pdf')
#             print("Saved followers screenshots to followers.pdf")
#         else:
#             print("No followers screenshots were taken.")

#         navigate_to_following(driver)
#         following_screenshots = take_following_screenshots(driver)
#         if following_screenshots:
#             generate_pdf(following_screenshots, filename="following.pdf")
#             print("Saved following screenshots to following.pdf")
#         else:
#             print("No following screenshots were taken.")
#     finally:
#         driver.quit()

def main(username, password, accused_name, case_data):
    # Setting up the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        # Add Chrome options if needed
        login(driver, username, password)  # Log in to Instagram
        navigate_to_followers(driver,username)  # Navigate to followers page
        followers_screenshots = take_followers_screenshots(driver)  # Capture followers screenshots

        navigate_to_following(driver,username)  # Navigate to followings page
        followings_screenshots = take_following_screenshots(driver)  # Capture followings screenshots

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