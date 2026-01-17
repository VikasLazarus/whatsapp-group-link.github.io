import requests
import re
import pandas as pd
import os
import datetime
import time
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
# Map Category Names to URLs
TARGETS = {
    "Indian Groups": "https://whtsgroupslinks.com/indian-whatsapp-group-links/",
    "USA Groups": "https://whtsgroupslinks.com/usa-whatsapp-group-links/",
    "Funny & Memes": "https://whtsgroupslinks.com/funny-whatsapp-group-links/",
    "Girls & Friendship": "https://whtsgroupslinks.com/girls-whatsapp-group-links/"
}

OUTPUT_FILE = "_data/whatsapp_links.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_links(html, category):
    soup = BeautifulSoup(html, 'html.parser')
    found = []

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if "chat.whatsapp.com" in href:
            clean_link_match = re.search(r'https:\/\/chat\.whatsapp\.com\/[A-Za-z0-9]{20,}', href)
            if clean_link_match:
                link_text = a_tag.get_text(strip=True)
                name = link_text if len(link_text) > 3 else f"{category} Group"
                
                found.append({
                    "category": category,  # <--- NEW COLUMN
                    "group_name": name,
                    "whatsapp_link": clean_link_match.group(0),
                    "date_added": datetime.date.today().isoformat()
                })
    return found

def main():
    print("--- STARTING CATEGORIZED SCRAPE ---")
    all_data = []

    for category, url in TARGETS.items():
        print(f"Scraping [{category}]: {url}...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                links = extract_links(response.text, category)
                print(f"  -> Found {len(links)} links")
                all_data.extend(links)
            else:
                print(f"  !! Failed (Status: {response.status_code})")
            time.sleep(2)
        except Exception as e:
            print(f"  !! Error: {e}")

    # SAVE LOGIC
    if all_data:
        os.makedirs('_data', exist_ok=True)
        new_df = pd.DataFrame(all_data)
        
        # Load existing
        if os.path.exists(OUTPUT_FILE):
            try:
                old_df = pd.read_csv(OUTPUT_FILE)
                final_df = pd.concat([old_df, new_df])
            except:
                final_df = new_df
        else:
            final_df = new_df

        # Deduplicate
        final_df = final_df.drop_duplicates(subset=['whatsapp_link'])
        
        # Save
        final_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nSUCCESS: Saved {len(final_df)} links to {OUTPUT_FILE}")
    else:
        print("\nNo links found.")

if __name__ == "__main__":
    main()