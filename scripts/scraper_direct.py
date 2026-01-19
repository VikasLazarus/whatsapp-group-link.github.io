import requests
import re
import pandas as pd
import os
import time
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
ACTIVE_MODEL_NAME = None # Will be auto-detected

# Configure Gemini if key exists
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
else:
    print("WARNING: GEMINI_API_KEY not found. AI features will be disabled.")

# Valid Categories for AI to choose from
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

# Block generic group names to avoid spam
BLOCKED_NAMES = [
    "Active WhatsApp Group", "WhatsApp Group Invite", "WhatsApp Group", 
    "WhatsApp", "Group Invite", "Join Group"
]

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def get_working_model():
    """Finds a valid Gemini model automatically to prevent 404 errors."""
    global ACTIVE_MODEL_NAME
    if ACTIVE_MODEL_NAME: return ACTIVE_MODEL_NAME
    
    print("  ...Auto-detecting available AI models...")
    try:
        # List models and pick the first one that supports generating content
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name:
                    ACTIVE_MODEL_NAME = m.name
                    print(f"  -> Selected Model: {ACTIVE_MODEL_NAME}")
                    return ACTIVE_MODEL_NAME
    except Exception as e:
        print(f"  !! Model detection failed: {e}")
    
    return None

def ask_gemini_category(group_name, fallback_category):
    """Asks AI to categorize the group name."""
    if not GEMINI_KEY: return fallback_category

    model_name = get_working_model()
    if not model_name: return fallback_category

    try:
        model = genai.GenerativeModel(model_name)
        prompt = (
            f"Classify the WhatsApp group named '{group_name}' into exactly one of these categories: "
            f"{', '.join(VALID_CATEGORIES)}. "
            f"If it is unclear, return '{fallback_category}'. "
            "Return ONLY the category name string, no other text."
        )
        
        response = model.generate_content(prompt)
        ai_decision = response.text.strip()
        
        if ai_decision in VALID_CATEGORIES:
            return ai_decision
        return fallback_category

    except Exception as e:
        print(f"      [AI Error] {e}")
        return fallback_category

def validate_whatsapp_link(link):
    """Checks if link is active and extracts the real group name."""
    try:
        response = requests.get(link, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()
            
            # Check for revoked/invalid text
            if "revoked" in page_text or "doesn't exist" in page_text or "reset" in page_text:
                return False, None
            
            group_name = None
            
            # Try getting name from Meta tag (Best)
            meta_title = soup.find("meta", property="og:title")
            if meta_title: group_name = meta_title.get("content")
            
            # Try getting name from H3 tag (Fallback)
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
    """Finds all unique chat.whatsapp.com links on a page."""
    soup = BeautifulSoup(html, 'html.parser')
    candidates = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if "chat.whatsapp.com" in href:
            match = re.search(r'https:\/\/chat\.whatsapp\.com\/[A-Za-z0-9]{20,}', href)
            if match: candidates.append(match.group(0))
    return list(set(candidates))

# ==========================================
# 3. MAIN EXECUTION
# ==========================================

def main():
    print("--- STARTING AI SCRAPER ---")
    
    # Pre-check AI connection
    if GEMINI_KEY: get_working_model()
    
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
                        # 1. Validate & Get Name
                        is_active, real_name = validate_whatsapp_link(link)
                        
                        if is_active:
                            print(f"    Analyzing: {real_name}...", end="\r")
                            
                            # 2. Ask AI for Category
                            final_category = ask_gemini_category(real_name, source_cat)
                            
                            valid_data.append({
                                "category": final_category,
                                "group_name": real_name,
                                "whatsapp_link": link,
                                "status": "Active"
                            })
                            print(f"      [AI] {real_name} -> {final_category}")
                            
                            # Sleep to respect rate limits
                            time.sleep(4) 
                        
            except Exception as e:
                print(f"    Error reading {url}: {e}")
            time.sleep(2)

    # Save to CSV
    if valid_data:
        os.makedirs('_data', exist_ok=True)
        csv_path = "_data/whatsapp_links.csv"
        
        new_df = pd.DataFrame(valid_data)
        
        if os.path.exists(csv_path):
            try:
                old_df = pd.read_csv(csv_path)
                final_df = pd.concat([new_df, old_df])
            except: final_df = new_df
        else: final_df = new_df

        # Deduplicate by link
        final_df = final_df.drop_duplicates(subset=['whatsapp_link'])
        final_df.to_csv(csv_path, index=False)
        print(f"\nSUCCESS: Added {len(valid_data)} new links. Total in DB: {len(final_df)}")
    else:
        print("\nNo new valid links found.")

if __name__ == "__main__":
    main()