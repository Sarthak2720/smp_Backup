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
from selenium.webdriver.common.action_chains import ActionChains
import argparse

def random_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))


def login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    time.sleep(5)


def navigate_to_user_profile(driver, username):
    driver.get(f"https://www.instagram.com/{username}/")
    random_delay(3, 5)


def open_post_and_take_screenshots(driver):
    screenshots = []

    try:
        # Click on the first post
        first_post = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div[1]/div[1]/a"))
        )
        first_post.click()
        random_delay(3, 5)

        # Continue taking screenshots and clicking the next button
        while True:
            # Take a screenshot of the current post
            post_screenshot = f'post_screenshot_{len(screenshots) + 1}.png'
            driver.save_screenshot(post_screenshot)
            screenshots.append(post_screenshot)
            print(f"Screenshot taken: {post_screenshot}")

            # Try to find and click the "Next" button
            next_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, '_aaqg') and contains(@class,'_aaqh')]//button[@class='_abl-' and @type='button']")
                )
            )
            next_button.click()
            random_delay(3, 5)
    except (TimeoutException, NoSuchElementException):
        print("No more posts or failed to navigate to the next post.")
    return screenshots




def dismiss_suspicious_activity_modal(driver):
    try:
        # Wait for the modal to appear
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@role, 'dialog')]"))
        )

        # Check for the dismiss button within the modal
        dismiss_button = driver.find_element(By.XPATH,
                                             "//button[contains(text(), 'Dismiss')] | //button[contains(text(), 'Close')]")
        dismiss_button.click()  # Click the dismiss button
        print("Dismissed suspicious activity modal.")

    except TimeoutException:
        print("No suspicious activity modal detected.")
    except NoSuchElementException:
        print("Dismiss button not found.")


def dismiss_notification_modal(driver):
    try:
        # Wait for the notification modal to appear
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class,'_a9-v')]"))
        )

        # Find and click the dismiss button
        dismiss_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
        dismiss_button.click()  # Click the "Not Now" button
        print("Dismissed notification modal.")

    except TimeoutException:
        print("No notification modal detected.")
    except NoSuchElementException:
        print("Dismiss button not found.")

def generate_pdf(screenshots, accused_name, case_data,username):
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
            text_object.textLine(f"Options: Posts")
            text_object.textLine(f"Date and Time of Parsing: {parsing_date_time})")
            text_object.textLine(f"Username: {username}")

        c.drawText(text_object)
        c.showPage()

    for screenshot in screenshots:
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

def main(username, password, accused_name, case_data):
    # Setting up the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        # Initialize the WebDriver and log in
        login(driver, username, password)  # Log in to Instagram
        dismiss_suspicious_activity_modal(driver)  # Dismiss any suspicious activity popup

        # Navigate to the user's profile
        navigate_to_user_profile(driver, username)

        dismiss_notification_modal(driver)

        # Take screenshots of posts
        post_screenshots = open_post_and_take_screenshots(driver)
        pdf_buffer = generate_pdf(post_screenshots, accused_name, case_data,username)

        # Write PDF to standard output (or save to file)
        sys.stdout.buffer.write(pdf_buffer.getvalue())
        # Generate PDF from post screenshots
       
    finally:
        driver.quit()


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