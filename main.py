import os
import json
import random
import requests
from datetime import datetime, timedelta

# ==========================================
# ⚙️ GITHUB CONFIGURATION
# ==========================================
# Apni details yahan dalein
GITHUB_USER = "Automation8248"
REPO_NAME = "Gumroad-automation-"
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")
BRANCH = "main"

HISTORY_FILE = "history.json"
COOLING_DAYS = 30 # 30 din ka image-only cooling period

def load_history():
    """History file ko safe tarike se load karne ka logic"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                content = f.read().strip()
                # Agar file khali hai, toh {} return karein
                if not content:
                    return {}
                data = json.loads(content)
                # Check karna ki data Dictionary {} hai ya nahi
                return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            print("⚠️ Warning: history.json padhne mein error aaya. Nayi history ban rahi hai.")
            return {}
    else:
        print(f"⚠️ Warning: {HISTORY_FILE} nahi mili. Kya aapne file create kar li hai?")
        return {}

def save_history(history):
    """Update history ko save karne ka logic"""
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
        print("❌ Error: 'ebooks' folder khali hai.")
        return

    # 2. Random Folder Selection
    selected_folder = random.choice(all_folders)
    folder_path = os.path.join(base_path, selected_folder)
    print(f"📁 Selected Folder: {selected_folder}")
    
    # 3. Random Title, Description, and Link Selection
    try:
        with open(f"{folder_path}/title.json", 'r') as f:
            title_data = json.load(f)
            selected_title = random.choice(title_data['titles'])

        with open(f"{folder_path}/info.json", 'r') as f:
            info_data = json.load(f)
            selected_desc = random.choice(info_data['descriptions'])

        with open(f"{folder_path}/ebook.txt", 'r') as f:
            ebook_url = f.read().strip()

    except json.JSONDecodeError as e:
        print(f"❌ JSON ERROR in {selected_folder}: Aapki JSON file ka format galat hai. Error: {e}")
        return
    except FileNotFoundError as e:
        print(f"❌ FILE MISSING in {selected_folder}: {e.filename} file nahi mili.")
        return

    # 4. Filter and Select a Random Image Based on 30-Day Cooling Period
    img_folder = f"{folder_path}/images"
    try:
        # Is folder ke liye image history nikalna
        folder_history = history.get(selected_folder, {})
        last_used_images = folder_history.get("last_used_images", {})
        
        # Folder ki saari valid images ki list banana
        all_images = [img for img in os.listdir(img_folder) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not all_images:
            print(f"❌ Error: '{img_folder}' mein koi image nahi mili.")
            return

        # Filtering: Sirf wo images jo 30 din se zyada purani hon ya pehle use hi na hui hon
        unused_images = []
        for img in all_images:
            last_posted_str = last_used_images.get(img)
            if not last_posted_str:
                # Agar image pehle use hi nahi hui, toh use unused_images mein add karein
                unused_images.append(img)
            else:
                # Agar use ho chuki hai, toh timestamp check karein
                last_posted_time = datetime.fromisoformat(last_posted_str)
                if current_time - last_posted_time > timedelta(days=COOLING_DAYS):
                    # Agar image cooling period se bahar hai, toh add karein
                    unused_images.append(img)
        
        if not unused_images:
            print(f"🛑 Saare images currently {COOLING_DAYS} din ke image-only cooling period mein hain. Aaj koi post nahi hoga.")
            return

        # Final Random Image Selection from Unused list
        selected_img_name = random.choice(unused_images)
        print(f"📸 Selected Image: {selected_img_name}")
        
    except FileNotFoundError:
        print(f"❌ Error: '{img_folder}' folder nahi mila.")
        return
    
    # Raw GitHub URL for Pinterest
    image_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{folder_path}/images/{selected_img_name}"

    # 5. Payload for Make.com
    payload = {
        "title": selected_title,
        "description": selected_desc,
        "image_url": image_url,
        "ebook_url": ebook_url,
        "folder": selected_folder
    }

    # 6. Send to Make.com Webhook
    if not MAKE_WEBHOOK_URL:
        print("❌ Error: MAKE_WEBHOOK_URL secret set nahi hai GitHub mein.")
        return

    print("🚀 Data Make.com ko bhej raha hoon...")
    response = requests.post(MAKE_WEBHOOK_URL, json=payload)
    
    if response.status_code == 200:
        print(f"✅ Success! Pinterest post triggered for image: '{selected_img_name}'")
        # 7. Update image history with timestamp and save
        last_used_images[selected_img_name] = current_time.isoformat()
        # Naya structure dictionary ke andar dictionary save karega
        history[selected_folder] = {"last_used_images": last_used_images}
        save_history(history)
        print("📝 History updated.")
    else:
        print(f"❌ Make.com Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    run_random_ebook_post()
