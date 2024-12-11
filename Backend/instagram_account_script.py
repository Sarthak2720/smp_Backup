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
import os
import argparse

# Your Instagram credentials
# username = 'dhwanijain86'
# password = 'm12veenanagar'

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


def take_profile_screenshot(driver, save_path='profile_screenshot.png'):
    try:
        # Scroll to ensure that the profile info is visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[2]/div/div/div[1]/div/a/h2')))  # Make sure the profile info is loaded
        profile_info = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[2]/div/div/div[1]/div/a/h2')
        driver.execute_script("arguments[0].scrollIntoView(true);", profile_info)
        random_delay(2, 4)

        # Take a screenshot of the profile page
        driver.save_screenshot(save_path)
        print(f"Profile screenshot taken: {save_path}")
    except (TimeoutException, NoSuchElementException):
        print("Failed to take profile screenshot.")
        return None

    return os.path.abspath(save_path)  # Return the absolute path


def generate_pdf(screenshot,accused_name, case_data,username):
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
            text_object.textLine(f"Options: Profile Information")
            text_object.textLine(f"Date and Time of Parsing: {parsing_date_time}")
            text_object.textLine(f"Username: {username}")
            c.drawText(text_object)
        
        
        c.drawText(text_object)
        c.showPage()

    
    if screenshot:
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


def main(username, password,accused_name,case_data):
    # Setting up the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        # Initialize the WebDriver and log in
        login(driver, username, password)  # Log in to Instagram

        # Navigate to the user's profile
        navigate_to_user_profile(driver, username)

        # Take screenshot of the profile information
        profile_screenshot = take_profile_screenshot(driver)

        # Generate PDF from profile screenshot
        if profile_screenshot:
            pdf_buffer = generate_pdf(profile_screenshot,accused_name,case_data)
            sys.stdout.buffer.write(pdf_buffer.getvalue())
        else:
            print("No profile screenshot was taken.")

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
