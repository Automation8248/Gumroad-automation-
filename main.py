import os, random, subprocess, fitz
from google import genai
import urllib.request, urllib.parse

# Naya Gemini Client Setup
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 1. Random PDF Select Karna
categories = [d for d in os.listdir('ebooks') if os.path.isdir(f"ebooks/{d}")]
category = random.choice(categories)
pdf_file = random.choice([f for f in os.listdir(f"ebooks/{category}") if f.endswith('.pdf')])
pdf_path = f"ebooks/{category}/{pdf_file}"

# 2. PDF Analyze Karna aur Purana Cover Hatana
doc = fitz.open(pdf_path)
pdf_text = ""
for i in range(min(3, len(doc))): # Pehle 3 page padhega
    pdf_text += doc[i].get_text()

doc.delete_page(0) # Old cover hataya
new_pdf_path = f"coverless_{pdf_file}"
doc.save(new_pdf_path)

# 3. Naye package se Title aur Description Likhwana
title_prompt = f"Analyze this ebook text and give a catchy 3-5 word title. Text: {pdf_text[:3000]}"
title_response = client.models.generate_content(model='gemini-pro', contents=title_prompt)
title = title_response.text.replace("*", "").replace("#", "").strip()

desc_prompt = f"Analyze this text and write a short Gumroad sales description for this ebook. STRICTLY DO NOT use any * or # symbols. Text: {pdf_text[:3000]}"
desc_response = client.models.generate_content(model='gemini-pro', contents=desc_prompt)
description = desc_response.text.replace("*", "").replace("#", "").strip()

# 4. AI Cover Generate & Download (Bina request library)
safe_title = urllib.parse.quote(title)
image_url = f"https://image.pollinations.ai/prompt/Professional ebook cover for {safe_title} high quality without text"

os.makedirs("screenshots", exist_ok=True) # Error se bachne ke liye direct folder create karega
cover_path = "screenshots/new_cover_screenshot.jpg"
urllib.request.urlretrieve(image_url, cover_path)

# 5. Price Set aur Gumroad Upload
price = round(random.uniform(1.99, 4.00), 2)
print(f"Uploading: {title} | Price: ${price}")

upload_command = [
    "curl", "-X", "POST", "https://api.gumroad.com/v2/products",
    "-F", f"access_token={os.environ['GUMROAD_TOKEN']}",
    "-F", f"name={title}",
    "-F", f"price={price}",
    "-F", f"description={description}",
    "-F", f"file=@{new_pdf_path}",
    "-F", f"thumbnail=@{cover_path}"
]
subprocess.run(upload_command)

print("Process Complete!")
