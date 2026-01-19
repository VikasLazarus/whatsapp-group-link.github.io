import requests
import re
import pandas as pd
import os
import datetime
import time
from bs4 import BeautifulSoup

# --- CONFIGURATION SECTION ---
# Add the specific pages you want to scrape here.
# You can add as many as you want, separated by commas.
TARGET_URLS = [
    "https://whtsgroupslinks.com/active-whatsapp-group-links/",
    "https://whtsgroupslinks.com/girls-whatsapp-group-links/",
    "https://whtsgroupslinks.com/indian-whatsapp-group-links/"
]

OUTPUT_FILE = "_data/whatsapp_links.csv"

# Real Browser Headers (To look like a human visitor)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_whatsapp_links(html_content):
    """Finds WhatsApp links and tries to guess the group name."""
    soup = BeautifulSoup(html_content, 'html.parser')
    found_groups = []

    # Look for all links on the page
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        
        # If it's a WhatsApp chat link
        if "chat.whatsapp.com" in href:
            # Clean the link
            clean_link_match = re.search(r'https:\/\/chat\.whatsapp\.com\/[A-Za-z0-9]{20,}', href)
            
            if clean_link_match:
                clean_link = clean_link_match.group(0)
                
                # Get the text inside the link tag (e.g., "Join Funny Group")
                link_text = a_tag.get_text(strip=True)
                
                # If link text is empty, try the previous header or just use a default
                if len(link_text) > 3:
                    group_name = link_text
                else:
                    group_name = "WhatsApp Group"

                found_groups.append({
                    "group_name": group_name,
                    "whatsapp_link": clean_link,
                    "date_added": datetime.date.today().isoformat(),
                    "status": "Active"
                })

    return found_groups

def main():
    print("--- STARTING DIRECT SCRAPE ---")
    all_data = []

    for url in TARGET_URLS:
        print(f"Visiting: {url}...")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                links = extract_whatsapp_links(response.text)
                print(f"  -> Extracted {len(links)} links.")
                all_data.extend(links)
            else:
                print(f"  !! Failed to load (Status: {response.status_code})")
                
        except Exception as e:
            print(f"  !! Error: {e}")
            
        # Wait 2 seconds between pages so we don't crash their server (or get blocked)
        time.sleep(2)

    # SAVE RESULTS
    if all_data:
        # Create _data folder if it doesn't exist
        os.makedirs('_data', exist_ok=True)
        
        # Prepare new data
        new_df = pd.DataFrame(all_data)
        
        # Load existing data (history) so we don't lose old links
        if os.path.exists(OUTPUT_FILE):
            try:
                old_df = pd.read_csv(OUTPUT_FILE)
                final_df = pd.concat([old_df, new_df])
            except:
                final_df = new_df
        else:
            final_df = new_df

        # Remove exact duplicates (same link)
        final_df = final_df.drop_duplicates(subset=['whatsapp_link'])
        
        # Save to CSV
        final_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nSUCCESS: Database updated. Total unique links: {len(final_df)}")
    else:
        print("\nNo links found on these pages.")

if __name__ == "__main__":
    main()