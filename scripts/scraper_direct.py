import requests
import re
import pandas as pd
import os
import time
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
TARGETS = {
    "Indian Groups": [
        
       "https://whtsgroupslinks.com/",
       "https://whatsupgrouplink.com/",
       "https://www.wa-contact-extractor.com/post/active-whatsapp-group-links[citation:3]",
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
    "USA & UK Groups": [
        "https://whtsgroupslinks.com/usa-whatsapp-group-links/"
    ],
    "Funny & Entertainment": [
        "https://whtsgroupslinks.com/funny-whatsapp-group-links/"
    ],
     "pakistani Groups": [
        "https://whtsgroupslinks.com/funny-whatsapp-group-links/"
    ],
     "Tamil Groups": [
        "https://whtsgroupslinks.com/funny-whatsapp-group-links/"
    ]
}

OUTPUT_FILE = "_data/whatsapp_links.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# List of generic names to BLOCK
BLOCKED_NAMES = [
    "Active WhatsApp Group",
    "WhatsApp Group Invite",
    "WhatsApp Group",
    "WhatsApp"
]

def validate_whatsapp_link(link):
    """
    Visits the link. Returns (True, Name) ONLY if the name is specific.
    """
    try:
        response = requests.get(link, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()
            
            # 1. Check for dead link indicators
            if "revoked" in page_text or "doesn't exist" in page_text or "reset" in page_text:
                return False, None
            
            # 2. Extract Real Group Name
            group_name = None
            meta_title = soup.find("meta", property="og:title")
            
            if meta_title:
                group_name = meta_title.get("content")
            
            # Fallback if meta tag is empty
            if not group_name:
                h3_title = soup.find("h3")
                if h3_title:
                    group_name = h3_title.get_text(strip=True)

            # 3. STRICT NAME FILTER
            if group_name:
                # Remove extra spaces and check against blocklist
                clean_name = group_name.strip()
                
                if clean_name in BLOCKED_NAMES:
                    return False, None # Reject generic names
                
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
    print("--- STARTING STRICT NAME SCRAPE ---")
    valid_data = []

    for category, urls_list in TARGETS.items():
        print(f"\nProcessing Category: {category}...")
        
        for url in urls_list:
            print(f"  Scraping URL: {url}...")
            try:
                response = requests.get(url, headers=HEADERS, timeout=15)
                if response.status_code == 200:
                    potential_links = extract_links_from_page(response.text)
                    print(f"    Found {len(potential_links)} potential links. Validating...")
                    
                    for i, link in enumerate(potential_links):
                        is_active, real_name = validate_whatsapp_link(link)
                        
                        if is_active:
                            valid_data.append({
                                "category": category,
                                "group_name": real_name,
                                "whatsapp_link": link,
                                "status": "Active"
                            })
                            print(f"      [OK] {real_name}")
                        else:
                            # Useful for debugging: see what got rejected
                            # print(f"      [X] Rejected/Dead") 
                            pass
                            
                        time.sleep(1.5)
                else:
                    print(f"    !! Failed to load (Status: {response.status_code})")
            except Exception as e:
                print(f"    !! Error scraping {url}: {e}")
            
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
        print(f"\nSUCCESS: Saved {len(final_df)} NAMED links to {OUTPUT_FILE}")
    else:
        print("\nNo valid links found.")

if __name__ == "__main__":
    main()