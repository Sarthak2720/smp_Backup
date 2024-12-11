import io
import sys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from PIL import Image
from reportlab.pdfgen import canvas
import time
import os
import argparse
from reportlab.lib.pagesizes import letter


def save_screenshots_to_pdf(screenshot_paths,accused_name,case_data,username):
    # Create an in-memory PDF
    pdf_buffer = io.BytesIO()
    
    c = canvas.Canvas(pdf_buffer)
    c = canvas.Canvas(pdf_buffer,pagesize=letter)
    width, height = letter
    parsing_date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    if accused_name or case_data:
        text_object = c.beginText(50, height - 50)
        text_object.setFont("Helvetica-Bold", 14)
        if accused_name:
            text_object.textLine(f"Accused Name: {accused_name}")
        if case_data:
            text_object.textLine(f"Case Data: {case_data}")
            text_object.textLine(f"Platform: Facebook")
            text_object.textLine(f"Options: Followers and Followings")
            text_object.textLine(f"Date and Time of Parsing: {parsing_date_time}")
            text_object.textLine(f"Username: {username}")
            
        c.drawText(text_object)
        c.showPage()
        
    for screenshot in screenshot_paths:
        image = Image.open(screenshot)
        image = image.convert("RGB")  # Ensure consistent color
        c.setPageSize(image.size)
        c.drawImage(screenshot, 0, 0)
        c.showPage()
    c.save()
    pdf_buffer.seek(0)  # Reset buffer pointer for reading
    return pdf_buffer

def take_full_page_screenshots(driver, base_save_path, overlap_percentage=0.3):  # Increased overlap to 30%
    # Capture the total height and viewport height
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    scroll_pause_time = 2  # Pause to allow content to load

    # Calculate overlap in pixels
    overlap = int(viewport_height * overlap_percentage)
    screenshot_paths = []
    offset = 0
    i = 0

    while offset < total_height:
        # Capture screenshot
        screenshot_path = os.path.join(base_save_path, f"screenshot_{i + 1}.png")
        driver.save_screenshot(screenshot_path)
        screenshot_paths.append(screenshot_path)

        # Update offset with increased overlap
        offset += (viewport_height - overlap)
        
        # Scroll down slightly past the last captured view
        driver.execute_script(f"window.scrollTo(0, {offset});")
        time.sleep(scroll_pause_time)

        # Update total height in case dynamic content loads
        total_height = driver.execute_script("return document.body.scrollHeight")

        i += 1

        # Stop if we've reached or exceeded the updated page height
        if offset >= total_height:
            break

    return screenshot_paths

def main(username, password,accused_name,case_data):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    screenshots_directory = os.path.join(current_directory, "screenshots")
    os.makedirs(screenshots_directory, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get('https://www.facebook.com/login')
        time.sleep(2)

        user_field = driver.find_element(By.ID, "email")
        pass_field = driver.find_element(By.ID, "pass")
        user_field.send_keys(username)
        pass_field.send_keys(password)
        pass_field.send_keys(Keys.RETURN)

        time.sleep(5)  # Wait for login

        # Navigate to the user's posts page
        driver.get("https://www.facebook.com/me")
        time.sleep(5)

        # Take screenshots of the posts page
        screenshot_paths = take_full_page_screenshots(driver, screenshots_directory)
        pdf_buffer = save_screenshots_to_pdf(screenshot_paths,accused_name,case_data,username)
        sys.stdout.buffer.write(pdf_buffer.getvalue())

    finally:
        driver.quit()

    # Convert screenshots to a single PDF in memory
    

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