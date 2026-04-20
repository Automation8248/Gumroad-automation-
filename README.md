# 🚀 Gumroad to Pinterest Auto-Poster

An intelligent, fully automated workflow that picks your Gumroad products (ebooks) and posts them directly to Pinterest. Built with Python, GitHub Actions, and Make.com.

## ✨ Key Features
* **Fully Automated:** Runs on a daily schedule using GitHub Actions (Zero manual work).
* **Humanized Randomization:** Dynamically selects a random Ebook, Title, Description, and Image for every post to keep the feed fresh.
* **Anti-Spam Smart History:** Includes a 3-day "Cooling Period". Once an ebook is posted, the script remembers it in `history.json` and won't post it again for 3 days to avoid triggering Pinterest spam filters.
* **Clean Aesthetic:** Designed to use clean, highly-converting descriptions without messy hashtags or symbols.
* **Scalable:** Want to add a new ebook? Just drop a new folder in the `ebooks/` directory, and the script will automatically detect and include it in the rotation.

---

## 📂 Repository Structure

Your repository must follow this exact structure for the automation to work:

```text
Gumroad-automation-/
│
├── .github/
│   └── workflows/
│       └── pinterest.yml     # GitHub Actions scheduling and permissions
│
├── main.py                   # The core Python logic
│
└── ebooks/                   # Main directory for all your products
    │
    ├── Ebook_01/             # Your first product folder
    │   ├── images/           # Contains vertical product images (.jpg, .png)
    │   ├── ebook.txt         # Contains ONLY your Gumroad product URL
    │   ├── info.json         # Contains a list of clean descriptions
    │   └── title.json        # Contains a list of clean titles
    │
    └── Ebook_02/             # Your second product folder
        ├── images/
        ├── ebook.txt
        ├── info.json
        └── title.json
