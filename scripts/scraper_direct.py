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
else:
    print("WARNING: GEMINI_API_KEY not found. AI features will be disabled.")

# The list of categories Gemini MUST choose from
VALID_CATEGORIES = [
    "Cricket & Sports", "Gaming & Esports", "Jobs & Careers", "Crypto & Money",
    "Movies & Web Series", "Funny, Memes & Viral", "Shayari & Love", 
    "Girls & Friendship", "Education & Students", "Tech, AI & Coding",
    "Kerala & Malayalam", "Tamil & Telugu", "North India (Hindi/Punjabi)",
    "Shopping & Deals", "News & Politics", "Religious & Spiritual",
    "International (USA/UK)"
]

# Source URLs to scrape
TARGETS = {
    "General Mix": ["https://whtsgroupslinks.com/active-whatsapp-group-links/"],
    "Indian Mix": ["https://whtsgroupslinks.com/indian-whatsapp-group-links/"],
    "USA Mix": ["https://whtsgroupslinks.com/usa-whatsapp-group-links/"],
    "Girls Mix": ["https://whtsgroupslinks.com/girls-whatsapp-group-links/"]
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

BLOCKED_NAMES = ["Active WhatsApp Group", "WhatsApp Group Invite", "WhatsApp Group", "WhatsApp", "Group Invite"]

# ==========================================
# 2. AI CLASSIFICATION FUNCTION (FIXED)
# ==========================================
def ask_gemini_category(group_name, fallback_category):
    """
    Sends the group name to Gemini and asks for a classification.
    """
    if not GEMINI_KEY:
        return fallback_category

    try:
        # FIX: Switched to 'gemini-pro' which is the most stable model ID
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = (
            f"Classify the WhatsApp group named '{group_name}' into exactly one of these categories: "
            f"{', '.join(VALID_CATEGORIES)}. "
            f"If it is unclear, return '{fallback_category}'. "
            "Return ONLY the category name string, no other text."
        )
        
        response = model.generate_content(prompt)
        ai_decision = response.text.strip()
        
        # Validation: Ensure AI returned a real category we know
        if ai_decision in VALID_CATEGORIES:
            return ai_decision
        
        # If AI returns the fallback or something weird, return fallback
        return fallback_category

    except Exception as e:
        print(f"      [AI Error] {e}")
        # If AI fails, use fallback so we don't lose the group
        return fallback_category

# ==========================================
# 3. SCRAPING & VALIDATION LOGIC
# ==========================================

def validate_whatsapp_link(link):
    """
    Visits the link to check if active and get Real Name.
    """
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
    print("--- STARTING PURE AI SCRAPE (GEMINI PRO) ---")
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
                        # 1. Check if link is alive
                        is_active, real_name = validate_whatsapp_link(link)
                        
                        if is_active:
                            print(f"    Analyzing: {real_name}...", end="\r")
                            
                            # 2. ASK GEMINI FOR CATEGORY
                            final_category = ask_gemini_category(real_name, source_cat)
                            
                            valid_data.append({
                                "category": final_category,
                                "group_name": real_name,
                                "whatsapp_link": link,
                                "status": "Active"
                            })
                            print(f"      [AI] {real_name} -> {final_category}")
                            
                            # Sleep 4s to stay within Gemini Pro free limits
                            time.sleep(4) 
                        
            except Exception as e:
                print(f"    Error: {e}")
            time.sleep(2)

    # SAVE LOGIC
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
        print(f"\nSUCCESS: AI processed {len(valid_data)} new links.")
    else:
        print("\nNo links found.")

if __name__ == "__main__":
    main()