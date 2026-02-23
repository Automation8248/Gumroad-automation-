import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import random
import urllib.parse
import requests
import glob
import google.generativeai as genai
from PIL import Image

# Folders Setup
DOWNLOAD_DIR = os.path.abspath("downloads")
SCREENSHOT_DIR = os.path.abspath("screenshot")
if not os.path.exists(DOWNLOAD_DIR): os.makedirs(DOWNLOAD_DIR)
if not os.path.exists(SCREENSHOT_DIR): os.makedirs(SCREENSHOT_DIR)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def take_screenshot(driver, name):
    filepath = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    driver.save_screenshot(filepath)
    print(f"Screenshot saved: {name}.png")

def setup_browser():
    options = uc.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    })
    # GitHub Actions Chrome version 144 ke liye fix
    driver = uc.Chrome(options=options, version_main=144) 
    driver.set_window_size(1280, 800)
    return driver

def bypass_cloudflare_and_get_book(driver, history):
    base_url = "https://welib.st"
    print(f"Opening {base_url}...")
    driver.get(base_url)
    
    # === STEP 1: VERIFICATION WAIT & TICK ===
    print("Verification page ka 7 second wait kar rahe hain...")
    time.sleep(7) #
    take_screenshot(driver, "1_before_tick")

    try:
        # Checkbox hamesha iframe mein hota hai
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            # Mouse ko physically move karke square box ke center par le jana
            actions = ActionChains(driver)
            # Center click logic for Cloudflare square box
            actions.move_to_element(iframe).pause(2).click().perform()
            print("Mouse se square box par TICK kar diya gaya hai!")
            break
            
        print("TICK ke baad redirect ke liye 7 second wait...")
        time.sleep(7) #
        take_screenshot(driver, "2_after_tick_redirect")

    except Exception as e:
        print(f"Verification error: {e}")

    # === STEP 2: RANDOM CATEGORY & BOOK SELECTION ===
    print("Page scroll karke category dhoondh rahe hain...")
    driver.execute_script("window.scrollBy(0, 800);")
    time.sleep(5)
    
    try:
        # Random category select karna
        categories = driver.find_elements(By.XPATH, "//a[contains(@href, '/category/') or contains(@href, '/topic/')]")
        if categories:
            random.choice(categories).click()
            time.sleep(7)
            print("Category open ho gayi.")
    except:
        pass

    # Random book select karna (MD5 pattern)
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/md5/']")
    book_urls = [l.get_attribute('href') for l in links if l.get_attribute('href')]
    available = [u for u in book_urls if u not in history]
    
    if not available:
        print("Koi nayi book nahi mili.")
        return None
        
    selected = random.choice(available)
    driver.get(selected)
    time.sleep(7)
    take_screenshot(driver, "3_book_page")
    return selected

# ... (Baki functions jaise extract_book_details, download_book_file, process_with_gemini same rahenge) ...

def main():
    history_file = "last_post.txt"
    history = []
    if os.path.exists(history_file):
        with open(history_file, "r") as f: history = f.read().splitlines()

    driver = setup_browser()
    try:
        book_url = bypass_cloudflare_and_get_book(driver, history)
        if book_url:
            # Complete workflow execution
            print(f"Processing book: {book_url}")
            # Add other logic calls here
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
