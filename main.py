import os
import json
import random
import requests
from datetime import datetime, timedelta

# ==========================================
# ⚙️ GITHUB CONFIGURATION
# ==========================================
GITHUB_USER = "Automation8248"
REPO_NAME = "Gumroad-automation-"
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")
BRANCH = "main"

HISTORY_FILE = "history.json"
COOLING_DAYS = 3

def load_history():
    """History file ko safe tarike se load karne ka logic"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                # Agar file khali hai, toh json.load error dega jisko niche handle kiya hai
                file_content = f.read().strip()
                if not file_content:
                    print("⚠️ Warning: history.json khali hai. Nayi history ban rahi hai.")
                    return {}
                    
                data = json.loads(file_content)
                
                # Check karna ki data Dictionary {} hai ya nahi
                if isinstance(data, dict):
                    return data
                else:
                    print("⚠️ Warning: history.json ka format galat (List/String) tha. Nayi history ban rahi hai.")
                    return {}
        except json.JSONDecodeError:
            print("⚠️ Warning: history.json padhne mein error aaya. Nayi history ban rahi hai.")
            return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def run_random_ebook_post():
    base_path = "ebooks"
    history = load_history()
    current_time = datetime.now()

    # 1. Main folder check
    if not os.path.exists(base_path):
        print(f"❌ Error: '{base_path}' folder nahi mila. Kripya pehle folder banayein.")
        return
        
    all_folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    
    if not all_folders:
        print("❌ Error: 'ebooks' folder khali hai. Ebook_01 jaise folders add karein.")
        return

    # 2. History Check (Cooling Period Logic)
    available_folders = []
    for folder in all_folders:
        last_posted_str = history.get(folder)
        if last_posted_str:
            last_posted_time = datetime.fromisoformat(last_posted_str)
            if current_time - last_posted_time < timedelta(days=COOLING_DAYS):
                print(f"⏳ Skipping '{folder}': Abhi 3 din ka cooling period chal raha hai.")
                continue
        available_folders.append(folder)

    if not available_folders:
        print("🛑 Saare folders cooling period mein hain. Aaj koi naya post nahi hoga.")
        return

    # 3. Random Folder Selection
    selected_folder = random.choice(available_folders)
    folder_path = os.path.join(base_path, selected_folder)
    print(f"📁 Selected Folder: {selected_folder}")

    try:
        # 4. Random Title Selection
        with open(f"{folder_path}/title.json", 'r') as f:
            title_data = json.load(f)
            selected_title = random.choice(title_data['titles'])

        # 5. Random Description Selection
        with open(f"{folder_path}/info.json", 'r') as f:
            info_data = json.load(f)
            selected_desc = random.choice(info_data['descriptions'])

        # 6. Ebook URL Extract
        with open(f"{folder_path}/ebook.txt", 'r') as f:
            ebook_url = f.read().strip()

    except json.JSONDecodeError as e:
        print(f"❌ JSON ERROR in {selected_folder}: Aapki JSON file ka format galat hai (shayad koi comma miss ho gaya hai). Error: {e}")
        return
    except FileNotFoundError as e:
        print(f"❌ FILE MISSING in {selected_folder}: {e.filename} file nahi mili.")
        return

    # 7. Random Image Selection
    img_folder = f"{folder_path}/images"
    try:
        all_images = [img for img in os.listdir(img_folder) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not all_images:
            print(f"❌ Error: '{img_folder}' mein koi image nahi mili.")
            return
        selected_img_name = random.choice(all_images)
    except FileNotFoundError:
        print(f"❌ Error: '{img_folder}' folder nahi mila.")
        return
    
    # Raw GitHub URL for Pinterest
    image_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{folder_path}/images/{selected_img_name}"

    # 8. Payload for Make.com
    payload = {
        "title": selected_title,
        "description": selected_desc,
        "image_url": image_url,
        "ebook_url": ebook_url
    }

    # 9. Send to Make.com Webhook
    if not MAKE_WEBHOOK_URL:
        print("❌ Error: MAKE_WEBHOOK_URL secret set nahi hai GitHub mein.")
        return

    print("🚀 Data Make.com ko bhej raha hoon...")
    response = requests.post(MAKE_WEBHOOK_URL, json=payload)
    
    if response.status_code == 200:
        print(f"✅ Success! Pinterest post triggered for: '{selected_title}'")
        # Update history and save
        history[selected_folder] = current_time.isoformat()
        save_history(history)
        print("📝 History updated successfully.")
    else:
        print(f"❌ Make.com Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    run_random_ebook_post()
