import requests
import re
import pandas as pd
import os
import time
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# 1. SETUP AI & CONFIGURATION
# ==========================================

# Configure Gemini AI
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# Define valid categories for the AI to choose from
VALID_CATEGORIES = [
    "Cricket & Sports", "Gaming & Esports", "Jobs & Careers", "Crypto & Money",
    "Movies & Web Series", "Funny, Memes & Viral", "Shayari & Love", 
    "Girls & Friendship", "Education & Students", "Tech, AI & Coding",
    "Kerala & Malayalam", "Tamil & Telugu", "North India (Hindi/Punjabi)",
    "Shopping & Deals", "News & Politics", "Religious & Spiritual"
]

# Keep your existing keyword list for the "First Pass" (It's faster)
AUTO_CATEGORIES = {
    "Cricket & Sports": ["cricket", "ipl", "match", "dream11", "football", "sport", "game", "virat", "dhoni"],
    "Gaming & Esports": ["pubg", "bgmi", "free fire", "ff", "fortnite", "minecraft", "gta", "gamer"],
    "Jobs & Careers": ["job", "vacancy", "hiring", "work", "internship", "sarkari", "naukri"],
    "Crypto & Money": ["crypto", "btc", "bitcoin", "eth", "trading", "forex", "invest", "money"],
    "Movies & Web Series": ["movie", "netflix", "series", "web series", "cinema", "film"],
    "Funny, Memes & Viral": ["funny", "meme", "joke", "masti", "comedy", "video", "status"],
    "Education & Students": ["study", "student", "class", "exam", "college", "university", "notes", "upsc"],
    "Tech, AI & Coding": ["python", "java", "coding", "developer", "hack", "tech", "web", "ai"],
    "Kerala & Malayalam": ["kerala", "malayalam", "mallu", "kochi"],
    "Tamil & Telugu": ["tamil", "chennai", "telugu", "hyderabad"],
    "Girls & Friendship": ["girl", "boy", "friend", "dosti", "chat", "meet", "dating"]
}

# Source URLs
TARGETS = {
    "General Mix": ["https://whtsgroupslinks.com/active-whatsapp-group-links/",
    
       "https://whtsgroupslinks.com/",
       "https://whatsupgrouplink.com/",
       "https://www.wa-contact-extractor.com/post/active-whatsapp-group-links",
       "https://wgrouplinks.com/",
       "https://indiansinlondonuk.com/whatsapp-groups/",
       "https://topwhatsappgrouplinks.wordpress.com/",
       "https://sites.google.com/view/whatsapp-group-link-join-only",
       "https://about.me/whatsapp_grouplinks",
       "https://www.prmoment.in/pr-insight/your-guide-to-pr-focused-whatsapp-channels-in-india",
       "https://wagroupjoin.com/",
       "https://grouplinks.org/",
       "https://wgroupjoin.com/",
       "https://web.whatsapp.com/",
       "https://groups.whatsapp.com/",
       "https://grouplinkz.com/",
       "https://whatsappgroup4u.com/",
       "https://grouplinku.com/",
       "https://webgruplink.com/",
       "https://webwagrouplinks.com/",
       "https://wagroupinvite.com/",
       "https://joingroups.in/",
       "https://joinwhatsappgrouplinks.com/",
       "https://webwagroupinvites.com/",
       "https://groupsor.link/"
  ],
    "Indian Mix": ["https://whtsgroupslinks.com/indian-whatsapp-group-links/"],
    "USA Mix": ["https://whtsgroupslinks.com/usa-whatsapp-group-links/"]
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

BLOCKED_NAMES = ["Active WhatsApp Group", "WhatsApp Group Invite", "WhatsApp Group", "WhatsApp" , "Features"]

# ==========================================
# 2. THE AI FUNCTION
# ==========================================
def ask_ai_for_category(group_name):
    """
    Uses Gemini Flash (Free Tier) to categorize tricky group names.
    """
    if not GEMINI_KEY:
        return None # Fallback if no key found

    try:
        # We use 'gemini-1.5-flash' because it's fast and free
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = (
            f"Categorize the WhatsApp group named '{group_name}' into exactly one of these categories: "
            f"{', '.join(VALID_CATEGORIES)}. "
            "If it fits none, return 'General Mix'. "
            "Return ONLY the category name, nothing else."
        )
        
        response = model.generate_content(prompt)
        ai_category = response.text.strip()
        
        # Safety check: ensure AI returned a real category
        if ai_category in VALID_CATEGORIES:
            return ai_category
            
    except Exception as e:
        print(f"      [AI Error] {e}")
        time.sleep(1) # Backoff if rate limited
    
    return None

# ==========================================
# 3. CORE LOGIC
# ==========================================
def determine_category(group_name, fallback_category):
    # 1. First Pass: Fast Keyword Match (Zero Cost)
    name_lower = group_name.lower()
    for category, keywords in AUTO_CATEGORIES.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category

    # 2. Second Pass: AI Analysis (Smart Fallback)
    # Only call AI if keywords failed AND we have an API key
    if GEMINI_KEY:
        print(f"      ...Keywords failed. Asking AI about '{group_name}'...")
        ai_result = ask_ai_for_category(group_name)
        if ai_result:
            print(f"      [AI DECISION] '{group_name}' -> {ai_result}")
            return ai_result
        # Sleep to respect free tier rate limits (15 RPM)
        time.sleep(4) 

    return fallback_category

def validate_whatsapp_link(link):
    try:
        response = requests.get(link, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()
            
            if "revoked" in page_text or "doesn't exist" in page_text or "reset" in page_text:
                return False, None
            
            group_name = None
            meta_title = soup.find("meta", property="og:title")
            if meta_title: group_name = meta_title.get("content")
            
            if not group_name:
                h3_title = soup.find("h3")
                if h3_title: group_name = h3_title.get_text(strip=True)

            if group_name:
                clean_name = group_name.strip()
                if clean_name in BLOCKED_NAMES: return False, None
                return True, clean_name
    except Exception:
        return False, None
    return False, None

def extract_links_from_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    candidates = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if "chat.whatsapp.com" in href:
            clean_link_match = re.search(r'https:\/\/chat\.whatsapp\.com\/[A-Za-z0-9]{20,}', href)
            if clean_link_match: candidates.append(clean_link_match.group(0))
    return list(set(candidates))

def main():
    print("--- STARTING AI-POWERED SCRAPE ---")
    valid_data = []

    for source_cat, urls_list in TARGETS.items():
        print(f"\nScanning Source: {source_cat}...")
        for url in urls_list:
            try:
                response = requests.get(url, headers=HEADERS, timeout=15)
                if response.status_code == 200:
                    potential_links = extract_links_from_page(response.text)
                    print(f"  Found {len(potential_links)} candidates. Validating...")
                    
                    for link in potential_links:
                        is_active, real_name = validate_whatsapp_link(link)
                        
                        if is_active:
                            final_category = determine_category(real_name, source_cat)
                            
                            valid_data.append({
                                "category": final_category,
                                "group_name": real_name,
                                "whatsapp_link": link,
                                "status": "Active"
                            })
                            print(f"      [OK] {real_name} -> {final_category}")
                        
                        time.sleep(1.5)
            except Exception as e:
                print(f"    Error: {e}")
            time.sleep(2)

    # SAVE LOGIC (Unchanged)
    if valid_data:
        os.makedirs('_data', exist_ok=True)
        new_df = pd.DataFrame(valid_data)
        if os.path.exists("_data/whatsapp_links.csv"):
            try:
                old_df = pd.read_csv("_data/whatsapp_links.csv")
                final_df = pd.concat([new_df, old_df])
            except: final_df = new_df
        else: final_df = new_df

        final_df = final_df.drop_duplicates(subset=['whatsapp_link'])
        final_df.to_csv("_data/whatsapp_links.csv", index=False)
        print(f"\nSUCCESS: Database updated with AI categorization.")
    else:
        print("\nNo links found.")

if __name__ == "__main__":
    main()