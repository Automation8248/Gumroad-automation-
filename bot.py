import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import random
import requests
import glob
import google.generativeai as genai
from PIL import Image

# Download folder setup
DOWNLOAD_DIR = os.path.abspath("downloads")
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def setup_browser():
    print("Browser start ho raha hai...")
    options = uc.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    })
    
    # FIX: Yahan 'version_main=144' add kiya gaya hai taaki version match ho sake
    driver = uc.Chrome(options=options, version_main=144) 
    
    driver.set_window_size(1280, 800)
    return driver

def bypass_cloudflare_and_get_book(driver, history):
    base_url = "https://welib.st"
    print("Website open kar rahe hain...")
    driver.get(base_url)
    
    # Cloudflare check ke liye wait
    time.sleep(10) 
    
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            try:
                cb = driver.find_element(By.CSS_SELECTOR, ".ctp-checkbox-label, input[type='checkbox']")
                cb.click()
                print("Cloudflare checkbox clicked!")
                time.sleep(8)
                break
            except:
                pass
            finally:
                driver.switch_to.default_content()
    except:
        pass

    print("Books dhoondh rahe hain...")
    time.sleep(5)
    
    # FIX: Screenshot ke anusaar, book pages ke URL mein hamesha '/md5/' hota hai.
    # Hum sirf wahi links nikalenge jisme '/md5/' ho.
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/md5/']")
    book_urls = []
    
    for link in links:
        href = link.get_attribute('href')
        if href:
            book_urls.append(href)
            
    available_books = list(set([u for u in book_urls if u not in history]))
    
    if not available_books:
        print("Koi nayi book nahi mili! (URL /md5/ match nahi hua)")
        return None
        
    selected_book = random.choice(available_books)
    print(f"Random Book Selected: {selected_book}")
    
    # Book ke detail page par jaana
    driver.get(selected_book)
    time.sleep(6) # Page fully load hone ka wait
    
    return selected_book
    
def simulate_mouse_copy(driver):
    print("Simulating mouse movement...")
    actions = ActionChains(driver)
    
    try:
        title_el = driver.find_element(By.TAG_NAME, "h1")
        actions.move_to_element(title_el).pause(1).double_click().perform()
        time.sleep(1)
        original_title = title_el.text
    except:
        original_title = "Premium Book Edition"

    try:
        desc_el = driver.find_element(By.CSS_SELECTOR, "h1 + div, h1 + p, .description")
        actions.move_to_element(desc_el).pause(1).click().perform()
        time.sleep(1)
        original_desc = desc_el.text
    except:
        original_desc = "An amazing read for modern thinkers. Grab your copy now."
        
    try:
        img_el = driver.find_element(By.CSS_SELECTOR, "img.cover, .book-cover img")
        img_url = img_el.get_attribute('src')
        img_data = requests.get(img_url).content
        with open("original_cover.jpg", "wb") as f:
            f.write(img_data)
    except:
        print("Original image download fail hua.")
        
    return original_title, original_desc

def download_pdf(driver):
    print("Clicking PDF Download button...")
    try:
        btn = driver.find_element(By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download') or contains(text(), 'PDF')]")
        actions = ActionChains(driver)
        actions.move_to_element(btn).pause(1).click().perform()
        time.sleep(30) 
        
        files = glob.glob(f'{DOWNLOAD_DIR}/*.pdf')
        if files:
            return max(files, key=os.path.getctime)
    except Exception as e:
        print(f"Download button error: {e}")
    return None

def generate_gemini_text(title, desc):
    print("Generating AI Text via Gemini...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""Act as a professional copywriter. Book: '{title}'. Original Description: {desc}. 
Task 1: Generate a COMPLETELY NEW, catchy title in the same genre. 
Task 2: Write a 100% humanized, engaging product description to sell this ebook. 
Format strictly as:
Title: [New Title Here]
Description: [New Description Here]"""
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        new_title = title
        new_desc = text
        if "Title:" in text and "Description:" in text:
            parts = text.split("Description:")
            new_title = parts[0].replace("Title:", "").strip()
            new_desc = parts[1].strip()
        return new_title, new_desc
    except Exception as e:
        print(f"Gemini Text Error: {e}")
        return title, desc

def generate_gemini_image(original_img_path):
    print("Analyzing original cover and generating new image via Gemini...")
    try:
        if not os.path.exists(original_img_path):
            return "original_cover.jpg"

        # Step 1: Analyze the original image
        img = Image.open(original_img_path)
        vision_model = genai.GenerativeModel('gemini-1.5-flash')
        analysis_prompt = """Analyze this book cover. Identify the genre, tone, and visual symbolism. 
Then, write a highly detailed text-to-image prompt to create a completely NEW, minimal, professional 3D ebook cover for the same genre. 
Make sure the prompt specifies a clean layout, a strong central visual metaphor, and NO text or words in the image."""
        
        analysis_response = vision_model.generate_content([analysis_prompt, img])
        image_prompt = analysis_response.text
        print("Generated Image Prompt from Gemini:\n", image_prompt)

        # Step 2: Generate the new image using Google's Imagen via SDK
        # Note: 'imagen-3.0-generate-001' is the standard model for image generation in Gemini API
        result = genai.ImageGenerationModel("imagen-3.0-generate-001").generate_images(
            prompt=image_prompt,
            number_of_images=1,
            aspect_ratio="1:1"
        )
        
        for generated_image in result.images:
            generated_image.save("final_cover.jpg")
            return "final_cover.jpg"
            
    except Exception as e:
        print(f"Gemini Image Error: {e}")
    
    return "original_cover.jpg" # Fallback

def upload_gumroad(title, desc, pdf_path, cover_path):
    print("Uploading to Gumroad...")
    url = "https://api.gumroad.com/v2/products"
    data = {
        "access_token": os.getenv("GUMROAD_TOKEN"),
        "name": title,
        "description": desc,
        "price": 0
    }
    
    # Fallback checking
    if not os.path.exists(cover_path):
        with open("dummy_cover.jpg", "w") as f: f.write("dummy")
        cover_path = "dummy_cover.jpg"

    with open(pdf_path, 'rb') as pdf, open(cover_path, 'rb') as cover:
        files = {'file': pdf, 'preview': cover}
        res = requests.post(url, data=data, files=files)
        
    if res.status_code in [200, 201]:
        print("Gumroad par successfully publish ho gaya!")
    else:
        print("Gumroad Error:", res.text)

def main():
    history_file = "last_post.txt"
    history = []
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = f.read().splitlines()

    driver = setup_browser()
    try:
        book_url = bypass_cloudflare_and_get_book(driver, history)
        if not book_url: return
        
        orig_title, orig_desc = simulate_mouse_copy(driver)
        pdf_path = download_pdf(driver)
        
        if not pdf_path:
            print("PDF Download fail ho gaya. Exiting.")
            return
            
        new_title, new_desc = generate_gemini_text(orig_title, orig_desc)
        final_cover = generate_gemini_image("original_cover.jpg")
        
        upload_gumroad(new_title, new_desc, pdf_path, final_cover)
        
        with open(history_file, "a") as f:
            f.write(book_url + "\n")
            
    finally:
        driver.quit()
        for f in glob.glob(f'{DOWNLOAD_DIR}/*'): os.remove(f)
        for img in ["original_cover.jpg", "final_cover.jpg", "dummy_cover.jpg"]:
            if os.path.exists(img): os.remove(img)

if __name__ == "__main__":
    main()
