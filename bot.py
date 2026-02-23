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
    
    # 1. Page load hone ka initial wait
    time.sleep(random.uniform(5, 8)) 
    take_screenshot(driver, "1_initial_verification_page")

    # === CLOUD FLARE BYPASS - MULTI-STRATEGY ===
    print("🔍 Cloudflare verification detect aur bypass kar rahe hain...")
    
    # Strategy 1: Cloudflare page detect karna
    cloudflare_indicators = [
        "checking your browser", "verify you are human", "cloudflare", "challenge-platform",
        "just a moment", "please wait while we verify", "cf-browser-verification"
    ]
    
    page_source = driver.page_source.lower()
    is_cloudflare = any(indicator in page_source for indicator in cloudflare_indicators)
    
    if is_cloudflare:
        print("✅ Cloudflare page detect hua - Bypass starting...")
        cloudflare_bypass(driver)
    else:
        print("ℹ️ Normal page - Direct navigation continue...")
    
    time.sleep(random.uniform(3, 6))
    take_screenshot(driver, "2_cloudflare_bypass_complete")

def cloudflare_bypass(driver):
    """Advanced Cloudflare bypass with multiple strategies"""
    
    strategies = [
        # Strategy A: Direct checkbox click
        lambda: click_direct_checkbox(driver),
        # Strategy B: Iframe-based click  
        lambda: click_iframe_checkbox(driver),
        # Strategy C: Canvas fingerprint bypass
        lambda: execute_canvas_bypass(driver),
        # Strategy D: Multiple random clicks
        lambda: random_mouse_actions(driver),
        # Strategy E: Turnstile specific
        lambda: handle_turnstile(driver)
    ]
    
    for i, strategy in enumerate(strategies, 1):
        print(f"Strategy {i}: Executing...")
        try:
            if strategy():
                print(f"✅ Strategy {i} SUCCESSFUL!")
                time.sleep(random.uniform(8, 12))  # Wait for redirect
                return True
        except Exception as e:
            print(f"Strategy {i} failed: {str(e)[:50]}")
            time.sleep(2)
    
    print("❌ All strategies failed - Manual intervention needed")
    return False

def click_direct_checkbox(driver):
    """Direct checkbox detection and click"""
    checkboxes = [
        "//input[@type='checkbox']",
        "//div[contains(@class, 'checkbox')]",
        "//span[contains(@class, 'checkmark')]",
        "//div[@data-sitekey]",
        "//iframe[contains(@src, 'turnstile')]"
    ]
    
    for xpath in checkboxes:
        try:
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            actions = ActionChains(driver)
            actions.move_to_element(element).pause(random.uniform(1, 3)).click().perform()
            print("✅ Direct checkbox clicked!")
            return True
        except:
            continue
    return False

def click_iframe_checkbox(driver):
    """Iframe-based checkbox click"""
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    
    for i, iframe in enumerate(iframes[:5]):  # Max 5 iframes
        try:
            driver.switch_to.frame(iframe)
            
            # Iframe mein checkbox dhoondhna
            checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox'] | //div[contains(@class, 'cf')]")
            
            actions = ActionChains(driver)
            actions.move_to_element(checkbox).pause(random.uniform(2, 4)).click().perform()
            
            driver.switch_to.default_content()
            print(f"✅ Iframe #{i} checkbox clicked!")
            return True
            
        except:
            driver.switch_to.default_content()
            continue
    return False

def execute_canvas_bypass(driver):
    """Canvas fingerprint bypass script"""
    canvas_script = """
    // Disable canvas fingerprinting
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function() {
        const args = arguments;
        if (args.length === 0) {
            args = [{mime: 'image/png'}];
        }
        return originalToDataURL.apply(this, args);
    };
    
    const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
    CanvasRenderingContext2D.prototype.getImageData = function() {
        const imageData = originalGetImageData.apply(this, arguments);
        const data = imageData.data;
        for (let i = 0; i < data.length; i += 4) {
            data[i] ^= 0x80;  // Add noise
        }
        return imageData;
    };
    """
    driver.execute_script(canvas_script)
    print("✅ Canvas fingerprint bypassed!")
    return True

def random_mouse_actions(driver):
    """Human-like random mouse movements"""
    actions = ActionChains(driver)
    
    # Random screen movements (human-like)
    screen_width = driver.execute_script("return window.innerWidth")
    screen_height = driver.execute_script("return window.innerHeight")
    
    for _ in range(random.randint(3, 6)):
        x = random.randint(100, screen_width - 100)
        y = random.randint(100, screen_height - 100)
        actions.move_by_offset(x, y).pause(random.uniform(0.5, 1.5))
    
    # Final click on center
    actions.move_by_offset(200, 200).pause(2).click().perform()
    print("✅ Random human-like mouse actions completed!")
    return True

def handle_turnstile(driver):
    """Cloudflare Turnstile specific handling"""
    try:
        # Turnstile challenge solve attempt
        driver.execute_script("""
            // Turnstile auto-solve attempt
            if (window.turnstile) {
                window.turnstile.render(document.querySelector('[data-sitekey]'), {
                    callback: function(token) { console.log('Turnstile solved:', token); }
                });
            }
        """)
        time.sleep(5)
        print("✅ Turnstile handled!")
        return True
    except:
        return False

# Usage remains same
# bypass_cloudflare_and_get_book(driver, history)


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
