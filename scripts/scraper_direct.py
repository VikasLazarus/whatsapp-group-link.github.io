import requests
import re
import pandas as pd
import os
import datetime
import time
from bs4 import BeautifulSoup

# --- CONFIGURATION SECTION ---
TARGET_URLS = [
    "https://whtsgroupslinks.com/active-whatsapp-group-links/",
    "https://whtsgroupslinks.com/girls-whatsapp-group-links/",
    "https://whtsgroupslinks.com/indian-whatsapp-group-links/"
]

OUTPUT_FILE = "_data/whatsapp_links.csv"

# Real Browser Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def validate_and_get_name(whatsapp_link):
    """
    Visits the WhatsApp link to:
    1. Check if it's active (not revoked).
    2. Get the REAL group name from the page title.
    """
    try:
        # Visit the link
        response = requests.get(whatsapp_link, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()

            # --- CHECK 1: IS IT INACTIVE? ---
            # If these words appear, the link is dead.
            if "revoked" in page_text or "doesn't exist" in page_text or "reset" in page_text:
                return False, None

            # --- CHECK 2: GET REAL NAME ---
            # Try to get name from Meta Tag (Best method)
            group_name = None
            meta_title = soup.find("meta", property="og:title")
            
            if meta_title:
                raw_name = meta_title.get("content", "")
                # Clean up "WhatsApp Group Invite" text if present
                group_name = raw_name.replace("WhatsApp Group Invite", "").strip()
            
            # Fallback: Try H3 tag if meta failed
            if not group_name:
                h3 = soup.find("h3")
                if h3:
                    group_name = h3.get_text(strip=True)

            # If name is still empty or generic, verify it's at least active
            if not group_name:
                group_name = "Active WhatsApp Group"

            return True, group_name

    except Exception as e:
        print(f"    ! Error checking link: {e}")
        return False, None

    return False, None

def extract_links_from_html(html_content):
    """Finds links in HTML but doesn't add them until validated."""
    soup = BeautifulSoup(html_content, 'html.parser')
    candidates = []

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if "chat.whatsapp.com" in href:
            clean_link_match = re.search(r'https:\/\/chat\.whatsapp\.com\/[A-Za-z0-9]{20,}', href)
            if clean_link_match:
                candidates.append(clean_link_match.group(0))
    
    # Remove duplicates immediately
    return list(set(candidates))

def main():
    print("--- STARTING VALIDATED SCRAPE ---")
    all_data = []

    for url in TARGET_URLS:
        print(f"Visiting Source: {url}...")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                # 1. Find all candidate links
                candidate_links = extract_links_from_html(response.text)
                print(f"  -> Found {len(candidate_links)} potential links. Validating active status...")

                # 2. Check each link one by one
                for i, link in enumerate(candidate_links):
                    # Validate
                    is_active, real_name = validate_and_get_name(link)

                    if is_active:
                        print(f"    [{i+1}/{len(candidate_links)}] Active: {real_name}")
                        all_data.append({
                            "group_name": real_name,
                            "whatsapp_link": link,
                            "date_added": datetime.date.today().isoformat(),
                            "status": "Active"
                        })
                    else:
                        # Optional: Print dead links to see progress
                        # print(f"    [{i+1}/{len(candidate_links)}] Inactive/Revoked")
                        pass

                    # IMPORTANT: Sleep to avoid WhatsApp blocking your IP
                    time.sleep(1.5)

            else:
                print(f"  !! Failed to load source (Status: {response.status_code})")
                
        except Exception as e:
            print(f"  !! Error: {e}")
            
        time.sleep(2)

    # SAVE RESULTS
    if all_data:
        os.makedirs('_data', exist_ok=True)
        new_df = pd.DataFrame(all_data)
        
        # Load history
        if os.path.exists(OUTPUT_FILE):
            try:
                old_df = pd.read_csv(OUTPUT_FILE)
                final_df = pd.concat([old_df, new_df])
            except:
                final_df = new_df
        else:
            final_df = new_df

        # Remove duplicates
        final_df = final_df.drop_duplicates(subset=['whatsapp_link'])
        
        # Save
        final_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nSUCCESS: Database updated. Total Active Links: {len(final_df)}")
    else:
        print("\nNo active links found.")

if __name__ == "__main__":
    main()