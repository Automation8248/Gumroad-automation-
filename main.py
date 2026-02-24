import os, random, subprocess, fitz, json
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

# Browser identity setup
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# 3. Pollinations AI se Title aur Description (Clean Format)
base_name = pdf_file.replace(".pdf", "").replace("_", " ").replace("-", " ")
title_prompt = urllib.parse.quote(f"Give ONLY one catchy 3-word title for {base_name}. No numbers.")
title_url = f"https://text.pollinations.ai/{title_prompt}"

req_title = urllib.request.Request(title_url, headers=headers)
with urllib.request.urlopen(req_title) as response:
    raw_title = response.read().decode('utf-8').split('\n')[0]
    title = "".join(filter(lambda x: not x.isdigit(), raw_title)).replace(".", "").strip()

desc_prompt = urllib.parse.quote(f"Write a professional 1 sentence sales description for {title}. No symbols.")
desc_url = f"https://text.pollinations.ai/{desc_prompt}"

req_desc = urllib.request.Request(desc_url, headers=headers)
with urllib.request.urlopen(req_desc) as response:
    description = response.read().decode('utf-8').replace("*", "").replace("#", "").strip()

# 4. Price Set Karna ($1.99 to $4.00)
price = round(random.uniform(1.99, 4.00), 2)
price_in_cents = int(price * 100)

print(f"Starting Upload for: {title} at ${price}")

# 5. Gumroad API Call - Sabse Professional Tarika
# Isme hum 'published=true' aur saari files ek saath bhej rahe hain
upload_cmd = [
    "curl", "-s", "-X", "POST", "https://api.gumroad.com/v2/products",
    "-H", f"Authorization: Bearer {os.environ['GUMROAD_TOKEN']}",
    "-F", f"name={title}",
    "-F", f"price={price_in_cents}",
    "-F", f"description={description}",
    "-F", "countries[]=ALL",
    "-F", "is_physical=false",
    "-F", "published=true", 
    "-F", f"product[file]=@{pdf_path}",
    "-F", f"product[thumbnail]=@{cover_path}"
]

result = subprocess.run(upload_cmd, capture_output=True, text=True)

# 6. Result Check Karna
if "success\":true" in result.stdout.lower():
    print(f"Success! '{title}' ab aapke Gumroad product section mein LIVE hai.")
else:
    print("Kuch gadbad hui hai. Gumroad Response niche dekhein:")
    print(result.stdout)
