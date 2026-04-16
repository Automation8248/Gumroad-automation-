import os
import json
import requests

# Config
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL") # GitHub Secrets se aayega
REPO_BASE_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main"

def sync_ebooks():
    ebooks_dir = "ebooks"
    
    # Ebooks folder ke andar har sub-folder ko scan karna
    for folder in os.listdir(ebooks_dir):
        folder_path = os.path.join(ebooks_dir, folder)
        
        if os.path.isdir(folder_path):
            info_file = os.path.join(folder_path, "info.json")
            
            if os.path.exists(info_file):
                with open(info_file, 'r') as f:
                    data = json.load(f)
                
                # Files ke URLs generate karna
                # Maan lete hain file ka naam hamesha book.pdf aur cover.jpg hoga
                pdf_url = f"{REPO_BASE_URL}/ebooks/{folder}/book.pdf"
                img_url = f"{REPO_BASE_URL}/ebooks/{folder}/cover.jpg"

                payload = {
                    "title": data.get("title"),
                    "price": data.get("price"),
                    "description": data.get("description"),
                    "file_url": pdf_url,
                    "image_url": img_url
                }

                # Make.com ko data bhejna
                response = requests.post(MAKE_WEBHOOK_URL, json=payload)
                
                if response.status_code == 200:
                    print(f"✅ Success: {data.get('title')} sent to Make.com")
                else:
                    print(f"❌ Failed: {data.get('title')} - {response.text}")

if __name__ == "__main__":
    sync_ebooks()
