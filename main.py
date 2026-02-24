import os, random, subprocess, fitz
import urllib.request, urllib.parse

# 1. Random PDF aur Category Selection
categories = [d for d in os.listdir('ebooks') if os.path.isdir(os.path.join('ebooks', d))]
category = random.choice(categories)
pdf_files = [f for f in os.listdir(os.path.join('ebooks', category)) if f.endswith('.pdf')]
pdf_file = random.choice(pdf_files)
pdf_path = os.path.abspath(os.path.join('ebooks', category, pdf_file))

# 2. PDF se Original Cover Extract Karna
doc = fitz.open(pdf_path)
page = doc.load_page(0)
pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
os.makedirs("screenshots", exist_ok=True)
cover_path = os.path.abspath("screenshots/original_cover.jpg")
pix.save(cover_path)
doc.close()

# Identity setup
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# 3. Pollinations AI se Title aur Description mangwana
base_name = pdf_file.replace(".pdf", "").replace("_", " ").replace("-", " ")
title_prompt = urllib.parse.quote(f"Create a short 3 word sales title for a book about {base_name}")
title_url = f"https://text.pollinations.ai/{title_prompt}"

req_title = urllib.request.Request(title_url, headers=headers)
with urllib.request.urlopen(req_title) as response:
    title = response.read().decode('utf-8').replace('"', '').replace("*", "").strip()

desc_prompt = urllib.parse.quote(f"Write a 1 sentence simple sales description for {title}. No symbols.")
desc_url = f"https://text.pollinations.ai/{desc_prompt}"
req_desc = urllib.request.Request(desc_url, headers=headers)
with urllib.request.urlopen(req_desc) as response:
    description = response.read().decode('utf-8').replace("*", "").strip()

# 4. Price aur Gumroad Upload
price = round(random.uniform(1.99, 4.00), 2)
print(f"Uploading: {title} | Price: ${price}")

# Curl Command with Fixed Paths
upload_cmd = [
    "curl", "-X", "POST", "https://api.gumroad.com/v2/products",
    "-F", f"access_token={os.environ['GUMROAD_TOKEN']}",
    "-F", f"name={title}",
    "-F", f"price={price}",
    "-F", f"description={description}",
    "-F", f"file=@{pdf_path}",
    "-F", f"thumbnail=@{cover_path}"
]

# Run upload
result = subprocess.run(upload_cmd, capture_output=True, text=True)
print(result.stdout)

if "success\":true" in result.stdout.lower():
    print("403 & File Error Solved! Upload Successful.")
else:
    print("Check logs for errors.")
