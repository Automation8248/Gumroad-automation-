import os
import json
import requests
import random
from datetime import datetime

# GitHub Config (Screenshot ke hisaab se)
GITHUB_USER = "Automation8248"
REPO_NAME = "Gumroad-automation-"
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL") 
HISTORY_FILE = "posted_history.json"
COOLDOWN_DAYS = 30

def load_history():
    """Pichli post ki history load karta hai"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_history(history):
    """Nayi post history ko save karta hai"""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def sync_dynamic_ebooks():
    base_path = "ebooks"
    history = load_history()
    now = datetime.now()
    
    valid_folders = []

    if not os.path.exists(base_path):
        print("❌ 'ebooks' folder nahi mila!")
        return

    # 1. Saare folders scan karo aur filter karo
    for folder_name in os.listdir(base_path):
        folder_dir = os.path.join(base_path, folder_name)

        if os.path.isdir(folder_dir):
            json_path = os.path.join(folder_dir, "info.json")
            
            if not os.path.exists(json_path):
                continue

            # COOLING PERIOD CHECK (30 Din)
            if folder_name in history:
                last_posted_date = datetime.fromisoformat(history[folder_name])
                days_passed = (now - last_posted_date).days
                
                if days_passed < COOLDOWN_DAYS:
                    print(f"⏳ Skipped '{folder_name}': Cooling period mein hai ({days_passed}/{COOLDOWN_DAYS} din hue hain).")
                    continue

            # PDF aur Image dhundna
            pdf_file, img_file = None, None
            for file in os.listdir(folder_dir):
                if file.lower().endswith('.pdf'):
                    pdf_file = file
                elif file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    img_file = file

            # Agar dono file mil gayi, toh ise valid list mein daal do
            if pdf_file and img_file:
                valid_folders.append({
                    "name": folder_name,
                    "pdf": pdf_file,
                    "img": img_file,
                    "json_path": json_path
                })
            else:
                print(f"⚠️ Skipped '{folder_name}': PDF ya Image missing hai.")

    # 2. Random Book Select Karna
    if not valid_folders:
        print("🛑 Koi nayi ebook available nahi hai. Sabhi 30-din ke cooldown mein hain!")
        return

    selected_ebook = random.choice(valid_folders)
    folder_name = selected_ebook["name"]

    # 3. JSON Data nikalna aur Webhook par bhejna
    with open(selected_ebook["json_path"], 'r') as f:
        data = json.load(f)

    raw_base = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/ebooks/{folder_name}"
    
    payload = {
        "title": data.get("title"),
        "price": data.get("price"),
        "description": data.get("description"),
        "pdf_url": f"{raw_base}/{selected_ebook['pdf']}",
        "image_url": f"{raw_base}/{selected_ebook['img']}"
    }

    try:
        response = requests.post(MAKE_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            print(f"✅ Success: Randomly selected '{folder_name}' successfully sent!")
            
            # History update karna aur save karna
            history[folder_name] = now.isoformat()
            save_history(history)
        else:
            print(f"❌ Error: Make.com ne data reject kar diya -> {response.text}")
    except Exception as e:
        print(f"❌ Request Error -> {e}")

if __name__ == "__main__":
    if not MAKE_WEBHOOK_URL:
        print("⚠️ MAKE_WEBHOOK_URL environment variable missing hai!")
    else:
        sync_dynamic_ebooks()
