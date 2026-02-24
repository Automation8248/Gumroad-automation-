import os, random, subprocess, fitz
import urllib.request, urllib.parse

# 1. Random PDF Select Karna
categories = [d for d in os.listdir('ebooks') if os.path.isdir(os.path.join('ebooks', d))]
category = random.choice(categories)
pdf_files = [f for f in os.listdir(os.path.join('ebooks', category)) if f.endswith('.pdf')]
pdf_file = random.choice(pdf_files)
pdf_path = os.path.abspath(os.path.join('ebooks', category, pdf_file))

# 2. Cover Extract Karna
doc = fitz.open(pdf_path)
page = doc.load_page(0)
pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
os.makedirs("screenshots", exist_ok=True)
cover_path = os.path.abspath("screenshots/cover.jpg")
pix.save(cover_path)
doc.close()

# 3. AI Title/Description (Simplified)
headers = {'User-Agent': 'Mozilla/5.0'}
clean_name = pdf_file.replace(".pdf", "").replace("_", " ")
title_url = f"https://text.pollinations.ai/{urllib.parse.quote('1 short catchy title for ' + clean_name)}"

req = urllib.request.Request(title_url, headers=headers)
with urllib.request.urlopen(req) as res:
    title = res.read().decode('utf-8').replace('"', '').strip()[:40]

# 4. Final LIVE Upload Command (Fixed Warnings)
price = int(round(random.uniform(1.99, 4.00), 2) * 100)
print(f"Bookvex is uploading: {title} at price cents {price}")

# Sab kuch --form mein convert kar diya hai taaki warning na aaye
upload_cmd = [
    "curl", "-X", "POST", "https://api.gumroad.com/v2/products",
    "--form", f"access_token={os.environ['GUMROAD_TOKEN']}",
    "--form", f"name={title}",
    "--form", f"price={price}",
    "--form", "published=true",
    "--form", f"product[file]=@{pdf_path}",
    "--form", f"product[thumbnail]=@{cover_path}"
]

result = subprocess.run(upload_cmd, capture_output=True, text=True)

# Debugging ke liye response print karega
print("Gumroad API Response:", result.stdout)

if "success\":true" in result.stdout.lower():
    print("Mubarak ho! Product ab list ho gaya hai.")
else:
    print("Abhi bhi list nahi hua. Response check karein.")
