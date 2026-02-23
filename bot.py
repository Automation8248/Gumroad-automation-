import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import random
import urllib.parse
import requests
import glob
import google.generativeai as genai
from PIL import Image

# --- Folders Setup ---
DOWNLOAD_DIR = os.path.abspath("downloads")
SCREENSHOT_DIR = os.path.abspath("screenshot") # Screenshot Folder

if not os.path.exists(DOWNLOAD_DIR): os.makedirs(DOWNLOAD_DIR)
if not os.path.exists(SCREENSHOT_DIR): os.makedirs(SCREENSHOT_DIR)

# Gemini API Setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def take_screenshot(driver, name):
    filepath = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    driver.save_screenshot(filepath)
    print(f"Screenshot saved: {name}.png")

def setup_browser():
    print("Browser start ho raha hai...")
    options = uc.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.notifications": 2
    })
    driver = uc.Chrome(options=options, version_main=144)
    driver.set_window_size(1280, 800)
    return driver

def bypass_cloudflare_and_get_book(driver, history):
    base_url = "https://welib.st"
    print(f"Opening {base_url}...")
    driver.get(base_url)
    
    time.sleep(12) 
    take_screenshot(driver, "1_initial_page_load")

    # --- Cloudflare Bypass (Mouse Center Click) ---
    print("Cloudflare check kar rahe hain...")
    time.sleep(10)
    
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            try:
                actions = ActionChains(driver)
                actions.move_to_element(iframe).pause(2).click().perform()
                print("Mouse se Cloudflare box ke center par click kar diya!")
                time.sleep(10)
                break 
            except:
                continue
    except Exception as e:
        print(f"Cloudflare interaction error: {e}")
    
    take_screenshot(driver, "2_after_cloudflare_click")

    # --- Scroll & Categories ---
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 700);")
        time.sleep(2)
    
    take_screenshot(driver, "3_scrolled_to_categories")

    try:
        cat_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/category/') or contains(@href, '/topic/')]")
        if not cat_links:
             cat_links = driver.find_elements(By.CSS_SELECTOR, ".card a")

        if cat_links:
            random_cat = random.choice(cat_links)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", random_cat)
            time.sleep(1)
            random_cat.click()
            time.sleep(8)
            take_screenshot(driver, "4_category_page_opened")
    except Exception as e:
        print(f"Category selection error: {e}")

    # --- Book Selection ---
    driver.execute_script("window.scrollBy(0, 500);")
    time.sleep(3)
    take_screenshot(driver, "5_looking_for_books")

    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/md5/']")
    book_urls = [link.get_attribute('href') for link in links if link.get_attribute('href')]
    available_books = list(set([u for u in book_urls if u not in history]))
    
    if not available_books:
        print("Koi nayi book nahi mili.")
        take_screenshot(driver, "error_no_books_found")
        return None
        
    selected_book = random.choice(available_books)
    driver.get(selected_book)
    time.sleep(8) 
    take_screenshot(driver, "6_book_detail_page")
    
    return selected_book

def extract_book_details(driver):
    actions = ActionChains(driver)
    try:
        title_el = driver.find_element(By.TAG_NAME, "h1")
        actions.move_to_element(title_el).pause(0.5).perform()
        original_title = title_el.text
    except: original_title = "Unknown Title"

    try:
        desc_el = driver.find_element(By.CSS_SELECTOR, "h1 ~ div.description, h1 ~ div, h1 ~ p")
        actions.move_to_element(desc_el).pause(0.5).perform()
        original_desc = desc_el.text
    except: original_desc = "A profound read recommended for you."
        
    try:
        img_el = driver.find_element(By.CSS_SELECTOR, "img.cover, .book-cover img")
        img_data = requests.get(img_el.get_attribute('src'), headers={"User-Agent": "Mozilla/5.0"}).content
        with open("original_cover.jpg", "wb") as f: f.write(img_data)
    except: pass
        
    return original_title, original_desc

def download_book_file(driver):
    try:
        download_btns = driver.find_elements(By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download')]")
        for btn in download_btns:
            if btn.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(1)
                ActionChains(driver).move_to_element(btn).pause(0.5).click().perform()
                break
        
        take_screenshot(driver, "7_clicked_download")
        time.sleep(60) 
        
        files = glob.glob(f'{DOWNLOAD_DIR}/*.*')
        if files: return max(files, key=os.path.getctime)
    except: pass
    return None

def process_with_gemini(title, desc):
    try:
        text_model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Act as a professional book marketer.\nOriginal Title: '{title}'\nOriginal Description: '{desc}'\nTask 1: Create a NEW, catchy title for this book.\nTask 2: Write a compelling, humanized description to sell it.\nFormat Output exactly like this:\nNEW_TITLE: [Your Title Here]\nNEW_DESC: [Your Description Here]"
        resp = text_model.generate_content(prompt).text
        
        new_title, new_desc = title, desc
        for line in resp.split('\n'):
            if line.startswith("NEW_TITLE:"): new_title = line.replace("NEW_TITLE:", "").strip()
            elif line.startswith("NEW_DESC:"): new_desc = line.replace("NEW_DESC:", "").strip()
    except: new_title, new_desc = title, desc

    cover_path = "original_cover.jpg"
    if os.path.exists("original_cover.jpg"):
        try:
            img_model = genai.GenerativeModel('gemini-1.5-flash')
            img_file = Image.open("original_cover.jpg")
            vision_prompt = "Analyze the genre and theme of this book cover. Then create a prompt for a completely new, professional, minimalist 3D ebook cover for the same genre. Do not use any text in the new image prompt."
            image_prompt = img_model.generate_content([vision_prompt, img_file]).text
            
            imagen_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
            result = imagen_model.generate_images(prompt=image_prompt, number_of_images=1, aspect_ratio="1:1")
            result.images[0].save("final_cover.jpg")
            cover_path = "final_cover.jpg"
        except: pass

    return new_title, new_desc, cover_path

def upload_to_gumroad(title, desc, file_path, cover_path):
    url = "https://api.gumroad.com/v2/products"
    data = {
        "access_token": os.getenv("GUMROAD_TOKEN"),
        "name": title,
        "description": desc,
        "price": 0
    }
    try:
        with open(file_path, 'rb') as f, open(cover_path, 'rb') as c:
            files = {'file': f, 'preview': c}
            res = requests.post(url, data=data, files=files)
            if res.status_code in [200, 201]: return True
    except: pass
    return False

def main():
    history_file = "last_post.txt"
    history = []
    if os.path.exists(history_file):
        with open(history_file, "r") as f: history = f.read().splitlines()

    driver = setup_browser()
    try:
        book_url = bypass_cloudflare_and_get_book(driver, history)
        if not book_url: return
        
        orig_title, orig_desc = extract_book_details(driver)
        downloaded_file = download_book_file(driver)
        if not downloaded_file: return

        new_title, new_desc, final_cover = process_with_gemini(orig_title, orig_desc)
        success = upload_to_gumroad(new_title, new_desc, downloaded_file, final_cover)
        
        if success:
            with open(history_file, "a") as f: f.write(book_url + "\n")

    finally:
        driver.quit()
        for f in glob.glob(f'{DOWNLOAD_DIR}/*'): os.remove(f)
        if os.path.exists("original_cover.jpg"): os.remove("original_cover.jpg")
        if os.path.exists("final_cover.jpg"): os.remove("final_cover.jpg")

if __name__ == "__main__":
    main()
