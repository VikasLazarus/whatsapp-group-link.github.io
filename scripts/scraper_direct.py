import requests
import re
import pandas as pd
import os
import time
from bs4 import BeautifulSoup

# --- 1. SOURCE CONFIGURATION ---
TARGETS = {
    # We still need sources to find links, but the category name here acts as a "Fallback"
    "Indian Groups": [
        "https://whtsgroupslinks.com/indian-whatsapp-group-links/",
        "https://whtsgroupslinks.com/kerala-whatsapp-group-links/"
    ],
    "USA & International": [
        "https://whtsgroupslinks.com/usa-whatsapp-group-links/"
    ],
    "General Mix": [
        "https://whtsgroupslinks.com/active-whatsapp-group-links/"
    ]
}

# --- 2. AUTO-CATEGORY RULES ---
# If a group name contains these keywords, it gets moved to that category instantly.
AUTO_CATEGORIES = {
    "Cricket & Sports": ["cricket", "ipl", "match", "dream11", "football", "sport", "game"],
    "Jobs & Careers": ["job", "vacancy", "hiring", "work", "internship", "sarkari", "naukri"],
    "Tech & Coding": ["python", "java", "coding", "developer", "hack", "tech", "web", "design"],
    "Crypto & Trading": ["crypto", "btc", "bitcoin", "trading", "forex", "invest", "money", "earn"],
    "Funny & Memes": ["funny", "meme", "joke", "masti", "comedy", "video", "status"],
    "Education & Study": ["study", "student", "class", "exam", "college", "university", "notes"]
}

OUTPUT_FILE = "_data/whatsapp_links.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# Generic names to reject
BLOCKED_NAMES = ["Active WhatsApp Group", "WhatsApp Group Invite", "WhatsApp Group", "WhatsApp"]

def determine_category(group_name, fallback_category):
    """
    Analyzes the group name to find a better category.
    If no keyword matches, it returns the fallback (source) category.
    """
    name_lower = group_name.lower()
    
    for category, keywords in AUTO_CATEGORIES.items():
        for keyword in keywords:
            # Check if keyword is in the name (e.g. "ipl" in "IPL 2026 Fans")
            if keyword in name_lower:
                return category
                
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
            if meta_title:
                group_name = meta_title.get("content")
            
            if not group_name:
                h3_title = soup.find("h3")
                if h3_title:
                    group_name = h3_title.get_text(strip=True)

            if group_name:
                clean_name = group_name.strip()
                if clean_name in BLOCKED_NAMES:
                    return False, None
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
            if clean_link_match:
                candidates.append(clean_link_match.group(0))
    return list(set(candidates))

def main():
    print("--- STARTING SMART-CATEGORY SCRAPE ---")
    valid_data = []

    for source_cat, urls_list in TARGETS.items():
        print(f"\nScanning Source: {source_cat}...")
        
        for url in urls_list:
            try:
                response = requests.get(url, headers=HEADERS, timeout=15)
                if response.status_code == 200:
                    potential_links = extract_links_from_page(response.text)
                    print(f"  Found {len(potential_links)} links on {url}. Validating...")
                    
                    for link in potential_links:
                        is_active, real_name = validate_whatsapp_link(link)
                        
                        if is_active:
                            # --- MAGIC HAPPENS HERE ---
                            # We ignore the source category if the name matches a specific niche
                            final_category = determine_category(real_name, source_cat)
                            
                            valid_data.append({
                                "category": final_category,
                                "group_name": real_name,
                                "whatsapp_link": link,
                                "status": "Active"
                            })
                            print(f"    [OK] {real_name} -> Assigned to: {final_category}")
                        
                        time.sleep(1.5)
            except Exception as e:
                print(f"    Error: {e}")
            time.sleep(2)

    # SAVE LOGIC
    if valid_data:
        os.makedirs('_data', exist_ok=True)
        new_df = pd.DataFrame(valid_data)
        
        if os.path.exists(OUTPUT_FILE):
            try:
                old_df = pd.read_csv(OUTPUT_FILE)
                final_df = pd.concat([new_df, old_df])
            except:
                final_df = new_df
        else:
            final_df = new_df

        final_df = final_df.drop_duplicates(subset=['whatsapp_link'])
        final_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nSUCCESS: Saved {len(final_df)} Auto-Categorized links.")
    else:
        print("\nNo links found.")

if __name__ == "__main__":
    main()