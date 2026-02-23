import os, random, subprocess, fitz
from google import genai
import urllib.request, urllib.parse

# Naya Gemini Client Setup
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 1. Random PDF aur Category Selection
categories = [d for d in os.listdir('ebooks') if os.path.isdir(f"ebooks/{d}")]
category = random.choice(categories)
pdf_files = [f for f in os.listdir(f"ebooks/{category}") if f.endswith('.pdf')]
pdf_file = random.choice(pdf_files)
pdf_path = f"ebooks/{category}/{pdf_file}"

# 2. PDF Analysis aur Purana Cover Hatana
doc = fitz.open(pdf_path)
pdf_text = ""
for i in range(min(3, len(doc))): 
    pdf_text += doc[i].get_text()

doc.delete_page(0) # Page 1 delete kiya
new_pdf_path = f"coverless_{pdf_file}"
doc.save(new_pdf_path)

# 3. Gemini Se Title aur Description
title_prompt = f"Analyze this text and give a catchy 3-word title ONLY. Text: {pdf_text[:2000]}"
title_res = client.models.generate_content(model='gemini-2.0-flash', contents=title_prompt)
# Clean title: New lines aur symbols hatana zaroori hai
title = title_res.text.replace("*", "").replace("#", "").replace("\n", "").strip()

desc_prompt = f"Write a short Gumroad description. NO * or # symbols. Text: {pdf_text[:2000]}"
desc_res = client.models.generate_content(model='gemini-2.0-flash', contents=desc_prompt)
description = desc_res.text.replace("*", "").replace("#", "").strip()

# 4. New Cover Image Generation (URL Fix ke saath)
# Title ko URL friendly banana
clean_title_for_url = urllib.parse.quote(title)
image_url = f"https://image.pollinations.ai/prompt/ebook%20cover%20for%20{clean_title_for_url}"

os.makedirs("screenshots", exist_ok=True)
cover_path = "screenshots/new_cover.jpg"

# Header add kiya taaki download block na ho
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)
urllib.request.urlretrieve(image_url, cover_path)

# 5. Price aur Gumroad Upload
price = round(random.uniform(1.99, 4.00), 2)
print(f"Uploading: {title} at ${price}")

upload_cmd = [
    "curl", "-X", "POST", "https://api.gumroad.com/v2/products",
    "-F", f"access_token={os.environ['GUMROAD_TOKEN']}",
    "-F", f"name={title}",
    "-F", f"price={price}",
    "-F", f"description={description}",
    "-F", f"file=@{new_pdf_path}",
    "-F", f"thumbnail=@{cover_path}"
]
subprocess.run(upload_cmd)

print("All Problems Solved. Process Success!")
