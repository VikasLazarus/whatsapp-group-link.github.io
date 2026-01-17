import requests
import re
import pandas as pd
import os
import time
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
# Now you can put multiple URLs inside the square brackets []
TARGETS = {
    "Indian Groups": [
        "https://whtsgroupslinks.com/indian-whatsapp-group-links/",
        "https://whtsgroupslinks.com/kerala-whatsapp-group-links/",
        "https://whtsgroupslinks.com/tamil-whatsapp-group-links/"
    ],
    "USA & UK Groups": [
        "https://whtsgroupslinks.com/usa-whatsapp-group-links/",
        "https://whtsgroupslinks.com/uk-whatsapp-group-links/"
    ],
    "Funny & Entertainment": [
        "https://whtsgroupslinks.com/funny-whatsapp-group-links/",
        "https://whtsgroupslinks.com/movies-whatsapp-group-links/"
    ],
    "Girls & Friendship": [
        "https://whtsgroupslinks.com/girls-whatsapp-group-links/"
    ]
}

OUTPUT_FILE = "_data/whatsapp_links.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def validate_whatsapp_link(link):
    """
    Visits the WhatsApp invite link to check if it's active.
    Returns: (is_active, real_group_name)
    """
    try:
        response = requests.get(link, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()
            
            # Check for dead link indicators
            if "revoked" in page_text or "doesn't exist" in page_text or "reset" in page_text:
                return False, None
            
            # Extract Real Group Name
            meta_title = soup.find("meta", property="og:title")
            if meta_title:
                group_name = meta_title.get("content")
                if group_name and "WhatsApp Group Invite" not in group_name and "WhatsApp" != group_name:
                    return True, group_name
                return True, "Active WhatsApp Group"
            
            h3_title = soup.find("h3")
            if h3_title:
                return True, h3_title.get_text(strip=True)

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
    print("--- STARTING MULTI-SOURCE SCRAPE ---")
    valid_data = []

    # Loop through each Category
    for category, urls_list in TARGETS.items():
        print(f"\nProcessing Category: {category}...")
        
        # Loop through each URL in that Category
        for url in urls_list:
            print(f"  Scraping URL: {url}...")
            try:
                response = requests.get(url, headers=HEADERS, timeout=15)
                if response.status_code == 200:
                    potential_links = extract_links_from_page(response.text)
                    print(f"    Found {len(potential_links)} potential links. Validating...")
                    
                    for i, link in enumerate(potential_links):
                        # Validate Link
                        is_active, real_name = validate_whatsapp_link(link)
                        
                        if is_active:
                            valid_data.append({
                                "category": category, # Assigns the main category name
                                "group_name": real_name,
                                "whatsapp_link": link,
                                "status": "Active"
                            })
                            print(f"      [OK] {real_name}")
                        else:
                            print(f"      [X] Dead Link", end="\r")
                            
                        # Important: Sleep to prevent blocking
                        time.sleep(1.5)
                else:
                    print(f"    !! Failed to load (Status: {response.status_code})")
            except Exception as e:
                print(f"    !! Error scraping {url}: {e}")
            
            # Sleep between different URL pages
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
        print(f"\nSUCCESS: Saved {len(final_df)} ACTIVE links to {OUTPUT_FILE}")
    else:
        print("\nNo active links found.")

if __name__ == "__main__":
    main()