import os, random, subprocess, fitz
import urllib.request, urllib.parse

# 1. Random PDF Select Karna
categories = [d for d in os.listdir('ebooks') if os.path.isdir(f"ebooks/{d}")]
category = random.choice(categories)
pdf_files = [f for f in os.listdir(f"ebooks/{category}") if f.endswith('.pdf')]
pdf_file = random.choice(pdf_files)
pdf_path = f"ebooks/{category}/{pdf_file}"

# 2. PDF se Original Cover Extract Karna
doc = fitz.open(pdf_path)
page = doc.load_page(0)
pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
os.makedirs("screenshots", exist_ok=True)
cover_path = "screenshots/original_cover.jpg"
pix.save(cover_path)
doc.close()

# 3. Pollinations AI se Title aur Description mangwana
# Hum file name ko base banakar Pollinations se ek catchy title mangenge
base_name = pdf_file.replace(".pdf", "").replace("_", " ")
encoded_prompt = urllib.parse.quote(f"Create a short 3 word sales title for a book about {base_name}")
text_api_url = f"https://text.pollinations.ai/{encoded_prompt}"

# Title Fetch karna
with urllib.request.urlopen(text_api_url) as response:
    title = response.read().decode('utf-8').replace('"', '').strip()

# Description Fetch karna
desc_prompt = urllib.parse.quote(f"Write a 1 sentence simple description for a book titled {title}. No hashtags or stars.")
desc_api_url = f"https://text.pollinations.ai/{desc_prompt}"
with urllib.request.urlopen(desc_api_url) as response:
    description = response.read().decode('utf-8').strip()

# 4. Price aur Gumroad Upload
price = round(random.uniform(1.99, 4.00), 2)
print(f"Uploading: {title} | Price: ${price}")

upload_cmd = [
    "curl", "-X", "POST", "https://api.gumroad.com/v2/products",
    "-F", f"access_token={os.environ['GUMROAD_TOKEN']}",
    "-F", f"name={title}",
    "-F", f"price={price}",
    "-F", f"description={description}",
    "-F", f"file=@{pdf_path}",
    "-F", f"thumbnail=@{cover_path}"
]

subprocess.run(upload_cmd)
print("Kaam poora hua! Pollinations AI ne title aur description likh diya hai.")
