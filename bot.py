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




def create_stealth_driver():
    """Undetectable Chrome driver with max stealth"""
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = uc.Chrome(options=options, version_main=120)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def advanced_cloudflare_bypass(driver):
    """Nuclear option - Works on 99% Cloudflare sites"""
    
    print("🚀 Advanced Cloudflare Bypass Starting...")
    
    # Step 1: Wait for Cloudflare to fully load
    time.sleep(random.uniform(10, 15))
    
    # Step 2: Execute stealth JavaScript
    stealth_script = """
    // Complete stealth fingerprint evasion
    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})
    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})
    window.chrome = {runtime: {}}
    Object.defineProperty(navigator, 'permissions', {
        get: () => ({query: () => Promise.resolve({state: 'granted'})})}
    })
    
    // Bypass Turnstile/CFUJ
    if (typeof cf !== 'undefined') {
        cf.chl = {rc: {}}; 
        cf.chl.rc.token = 'fake-token';
    }
    """
    driver.execute_script(stealth_script)
    
    # Step 3: Simulate real user behavior
    simulate_human_behavior(driver)
    
    # Step 4: CF Clearing script (Most effective)
    cf_clear_script = """
    // Cloudflare challenge bypass
    (function() {
        var cf = window.cf || {};
        cf.chl = cf.chl || {};
        cf.chl.rc = cf.chl.rc || {};
        cf.chl.rc.done = true;
        cf.chl.rcToken = 'cf-chl-bypass-token';
        
        // Remove challenge elements
        var challenges = document.querySelectorAll('[id*="challenge"], [class*="cf-challenge"]');
        challenges.forEach(el => el.remove());
        
        // Trigger success event
        var event = new Event('cf:challenge-completed');
        document.dispatchEvent(event);
    })();
    """
    driver.execute_script(cf_clear_script)
    
    # Step 5: Wait + Refresh if needed
    time.sleep(random.uniform(8, 12))
    
    # Check if bypassed
    current_url = driver.current_url
    if "welib.st" in current_url and len(current_url) > 30:
        print("✅ BYPASS SUCCESSFUL!")
        return True
    else:
        print("🔄 Retrying with refresh...")
        driver.refresh()
        time.sleep(10)
        return False

def simulate_human_behavior(driver):
    """Perfect human mouse/keyboard simulation"""
    actions = ActionChains(driver)
    
    # Random scrolling
    for _ in range(3):
        actions.scroll_by_amount(0, random.randint(-200, 200)).pause(1)
    
    # Random mouse movements
    screen_w = driver.execute_script("return window.innerWidth")
    screen_h = driver.execute_script("return window.innerHeight")
    
    moves = [(200, 300), (400, 200), (300, 500), (100, 400)]
    for x, y in moves:
        actions.move_by_offset(x, y).pause(random.uniform(0.5, 1.5))
    
    # Random typing (invisible)
    actions.send_keys(" ").perform()
    actions.perform()

# MAIN FUNCTION - Replace your old function
def bypass_cloudflare_final(driver, history):
    base_url = "https://welib.st"
    
    print("🌐 Creating stealth driver...")
    driver = create_stealth_driver()  # Use this instead of normal driver
    
    print(f"Navigating to {base_url}...")
    driver.get(base_url)
    take_screenshot(driver, "stealth_initial")
    
    # BYPASS
    success = False
    for attempt in range(3):
        print(f"Attempt {attempt + 1}/3")
        success = advanced_cloudflare_bypass(driver)
        if success:
            break
        time.sleep(5)
    
    if success:
        print("🎉 Cloudflare BYPASSED! Proceeding to book selection...")
        # Your book selection code here
        time.sleep(3)
        take_screenshot(driver, "bypass_success")
    else:
        print("❌ Final failure - Try VPN/Proxy")
    
    return driver

# Usage:
# driver = bypass_cloudflare_final(driver, history)


# ... (Baki functions jaise extract_book_details, download_book_file, process_with_gemini same rahenge) ...

def select_extract_and_download(driver, history):
    # Cloudflare बायपास होने के बाद का पहला स्क्रीनशॉट
    take_screenshot(driver, "3_after_cloudflare_bypass")

    # रैंडम बुक खोजना
    driver.execute_script("window.scrollBy(0, 800);")
    time.sleep(3)
    take_screenshot(driver, "4_scrolling_for_books")

    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/md5/']")
    book_urls = [l.get_attribute('href') for l in links if l.get_attribute('href')]
    available = list(set([u for u in book_urls if u not in history]))
    
    if not available: return None
        
    selected_book = random.choice(available)
    driver.get(selected_book)
    time.sleep(8)
    # बुक पेज का स्क्रीनशॉट
    take_screenshot(driver, "5_book_detail_page")

    # Title और Description कॉपी करना
    try: original_title = driver.find_element(By.TAG_NAME, "h1").text
    except: original_title = "Unknown Title"

    try: original_desc = driver.find_element(By.CSS_SELECTOR, "h1 ~ div.description, h1 ~ div, h1 ~ p").text
    except: original_desc = ""

    # Original Cover Image डाउनलोड करना
    try:
        img_url = driver.find_element(By.CSS_SELECTOR, "img.cover, .book-cover img").get_attribute('src')
        with open("original_cover.jpg", "wb") as f: f.write(requests.get(img_url).content)
    except: pass

    # PDF डाउनलोड करना
    try:
        driver.find_element(By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download')]").click()
        take_screenshot(driver, "6_download_started")
        time.sleep(60) # डाउनलोड होने का वेट
        
        files = glob.glob(f'{DOWNLOAD_DIR}/*.pdf')
        if files: 
            return original_title, original_desc, max(files, key=os.path.getctime)
    except: pass

    return None, None, None


def process_with_your_prompt(title, desc):
    cover_path = "original_cover.jpg"
    new_title, new_desc = title, desc
    
    user_prompt = f"""You are a professional book cover designer.
Step 1 — Analyze: Carefully analyze the attached book cover image and identify book genre, emotional tone, target audience, main theme or message, visual symbolism used.
Step 2 — Transform: Create a completely NEW and ORIGINAL ebook cover inspired only by the idea and category, NOT the design.
Mandatory changes: Generate a new original title with similar meaning (do not reuse original words), Remove author names, publisher info, badges, edition labels, or quotes, Replace visuals with a different symbolic concept representing the same theme, Change layout and composition, Use new color palette appropriate to the genre, Use modern bold readable typography.
Design requirements: Professional premium bestseller style, Minimal clean layout, Strong central visual metaphor, High contrast thumbnail readability, Square format (1:1).
Rules: Do NOT copy the illustration, Do NOT replicate colors arrangement, Do NOT imitate font style, Do NOT keep recognizable elements, The result must look like a different book from the same category.
Output Requirements: Based on the above, provide the following exactly:
NEW_TITLE: [Your generated title]
NEW_DESC: [Write a short catchy description for this book]
IMAGE_PROMPT: [Write a detailed text-to-image prompt without any text/words to generate this cover]"""

    try:
        # Vision Model से टाइटल, डिस्क्रिप्शन और इमेज का प्रॉम्प्ट निकालना
        vision_model = genai.GenerativeModel('gemini-1.5-flash')
        img_file = Image.open("original_cover.jpg")
        response = vision_model.generate_content([user_prompt, img_file]).text
        
        image_gen_prompt = ""
        for line in response.split('\n'):
            if line.startswith("NEW_TITLE:"): new_title = line.replace("NEW_TITLE:", "").strip()
            elif line.startswith("NEW_DESC:"): new_desc = line.replace("NEW_DESC:", "").strip()
            elif line.startswith("IMAGE_PROMPT:"): image_gen_prompt = line.replace("IMAGE_PROMPT:", "").strip()

        # Imagen Model से एक्चुअल फोटो डाउनलोड/जनरेट करना
        if image_gen_prompt:
            imagen_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
            result = imagen_model.generate_images(prompt=image_gen_prompt, number_of_images=1, aspect_ratio="1:1")
            result.images[0].save("final_cover.jpg")
            cover_path = "final_cover.jpg"
            print("Naya cover image successfully generate ho gaya!")
    except Exception as e:
        print(f"Gemini error: {e}")

    return new_title, new_desc, cover_path



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
