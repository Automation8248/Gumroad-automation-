import os
import json
import random
import requests

# GitHub Environment Variables
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
BRANCH = "main"

def run_automation():
    # 1. Saare folders ki list (sirf wo jisme ebook data hai)
    all_folders = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')]
    selected_folder = random.choice(all_folders)

    # 2. Random Title (title.json se)
    with open(f"{selected_folder}/title.json", 'r') as f:
        title_data = json.load(f)
        selected_title = random.choice(title_data['titles'])

    # 3. Random Description (info.json se)
    with open(f"{selected_folder}/info.json", 'r') as f:
        info_data = json.load(f)
        selected_desc = random.choice(info_data['descriptions'])

    # 4. Ebook Link (ebook.txt se)
    with open(f"{selected_folder}/ebook.txt", 'r') as f:
        ebook_url = f.read().strip()

    # 5. Random Image
    img_folder = f"{selected_folder}/images"
    all_images = [img for img in os.listdir(img_folder) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
    selected_img_name = random.choice(all_images)
    
    # Raw Image URL for Pinterest
    image_url = f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{selected_folder}/images/{selected_img_name}"

    # 6. Make.com Payload
    payload = {
        "title": selected_title,
        "description": selected_desc,
        "image_url": image_url,
        "ebook_url": ebook_url
    }

    # Data send karein
    response = requests.post(MAKE_WEBHOOK_URL, json=payload)
    
    if response.status_code == 200:
        print(f"✅ Success! Posted: {selected_title} from {selected_folder}")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    run_automation()
