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

# # Setting up the Chrome driver
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def random_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))


def handle_suspicious_activity_modal(driver, gmail):
    try:
        # Check for the Gmail verification prompt
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "challenge_response")))
        driver.find_element(By.NAME, "challenge_response").send_keys(gmail)
        driver.find_element(By.NAME, "challenge_response").send_keys(Keys.RETURN)
        random_delay(2, 4)
    except TimeoutException:
        print("No suspicious activity prompt found.")
        return False
    except NoSuchElementException:
        print("Suspicious activity modal element not found.")
        return False
    return True


def login(driver, username, password):
    driver.get("https://twitter.com/login")
    try:
        # Enter username and proceed to the next step
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "text")))
        driver.find_element(By.NAME, "text").send_keys(username)
        driver.find_element(By.NAME, "text").send_keys(Keys.RETURN)
        random_delay(2, 4)

        # Handle suspicious activity prompt if it appears
        # if handle_suspicious_activity_modal(driver, gmail):
        #     print("Handled suspicious activity prompt.")

        # Enter password
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "password")))
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(5)
    except TimeoutException:
        print("Loading took too much time! - Login element not found")
    except NoSuchElementException:
        print("No such element - Login element not found")


def navigate_to_profile(driver,username):
    driver.get(f"https://twitter.com/{username}")
    random_delay(3, 5)

def open_post_and_take_screenshots(driver):
    screenshots = []
    try:
        # Wait until the timeline is fully loaded
        timeline = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']"))
        )
        print("Timeline loaded successfully.")

        last_position = driver.execute_script("return window.scrollY;")
        screenshots_count = 0
        
        while True:
            # Take a screenshot of the profile
            screenshot_filename = f"profile_screenshot_{len(screenshots) + 1}.png"
            driver.save_screenshot(screenshot_filename)
            screenshots.append(screenshot_filename)
            print(f"Screenshot taken: {screenshot_filename}")
            screenshots_count += 1

            # Scroll down a small amount (adjust the value as needed for overlap)
            driver.execute_script("window.scrollBy(0, 500);")
            random_delay(2, 3)  # Optional delay to mimic human behavior

            # Check if we've reached the bottom of the page
            new_position = driver.execute_script("return window.scrollY;")
            if new_position == last_position:
                print("Reached the bottom of the page.")
                break
            last_position = new_position

    except TimeoutException:
        print("Failed to load the timeline.")
    except NoSuchElementException:
        print("No timeline found.")

    return screenshots


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
            text_object.textLine(f"Platform: Twitter")
            text_object.textLine(f"Options: Posts")
            text_object.textLine(f"Date and Time of Parsing: {parsing_date_time}")
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
        # dismiss_suspicious_activity_modal(driver)  # Dismiss any suspicious activity popup

        # Navigate to the user's profile
        navigate_to_profile(driver, username)

        # dismiss_notification_modal(driver)

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