import os
import json
import random
import requests

# GitHub Environment Variables
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")
REPO_NAME = os.getenv("GITHUB_REPOSITORY") # e.g. "username/repo"
BRANCH = "main"

def run_automation():
    # 1. Saare folders ki list nikalna (bot.py aur .github ko chhod kar)
    all_folders = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')]
    selected_folder = random.choice(all_folders)

    # 2. Ebook Link (ebook.txt se)
    with open(f"{selected_folder}/ebook.txt", 'r') as f:
        ebook_url = f.read().strip()

    # 3. Random Description (info.json se)
    with open(f"{selected_folder}/info.json", 'r') as f:
        info_data = json.load(f)
        selected_desc = random.choice(info_data['descriptions'])

    # 4. Random Image
    img_folder = f"{selected_folder}/images"
    all_images = os.listdir(img_folder)
    selected_img_name = random.choice(all_images)
    
    # GitHub Raw Image URL (Pinterest ko public URL chahiye hota hai)
    # Format: https://raw.githubusercontent.com/USER/REPO/BRANCH/FOLDER/images/IMAGE_NAME
    image_url = f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{selected_folder}/images/{selected_img_name}"

    # 5. Data ko Make.com par bhejna
    payload = {
        "title": selected_folder.replace("_", " "), # Folder name ko title ki tarah use karein
        "description": selected_desc,
        "image_url": image_url,
        "ebook_url": ebook_url
    }

    response = requests.post(MAKE_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        print(f"Success: Posted from {selected_folder}")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    run_automation()
