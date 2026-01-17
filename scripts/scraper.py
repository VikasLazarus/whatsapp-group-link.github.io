import requests
import re
import pandas as pd
import os
import datetime
import time
import random
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
KEYWORDS = ["movies", "crypto", "students", "funny memes", "jobs"]
OUTPUT_FILE = "_data/whatsapp_links.csv"

# Real Browser Headers (Crucial for bypassing blocks)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/"
}

def extract_whatsapp_links(text):
    """Extracts chat.whatsapp.com links from text."""
    if not text: return []
    # Regex to find links like https://chat.whatsapp.com/ExAmPlE123
    return re.findall(r'https:\/\/chat\.whatsapp\.com\/[A-Za-z0-9]{20,}', text)

def scrape_duckduckgo(keyword):
    """Searches DuckDuckGo HTML version for whatsapp links."""
    print(f"  [DuckDuckGo] Searching for: {keyword}...")
    
    # We search for the keyword AND "chat.whatsapp.com" to ensure results have links
    query = f'"{keyword}" site:facebook.com OR site:twitter.com "chat.whatsapp.com"'
    url = "https://html.duckduckgo.com/html/"
    params = {'q': query}
    
    links_found = []
    try:
        response = requests.post(url, data=params, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all search results
            for result in soup.find_all('a', class_='result__a'):
                title = result.get_text()
                link = result.get('href')
                
                # Check snippet text for whatsapp links
                snippet_div = result.find_next('a', class_='result__snippet')
                snippet = snippet_div.get_text() if snippet_div else ""
                
                found_urls = extract_whatsapp_links(snippet + " " + title + " " + str(link))
                
                for wa_link in found_urls:
                    links_found.append({
                        "group_name": f"{keyword.capitalize()} Group",
                        "whatsapp_link": wa_link,
                        "date_added": datetime.date.today().isoformat(),
                        "status": "Active"
                    })
        else:
            print(f"  !! Blocked by DuckDuckGo (Status: {response.status_code})")
            
    except Exception as e:
        print(f"  !! Error DuckDuckGo: {e}")

    print(f"  -> Found {len(links_found)} links.")
    return links_found

def main():
    print("--- STARTING ROBUST SCRAPE ---")
    all_data = []

    for keyword in KEYWORDS:
        # 1. Scrape DuckDuckGo
        ddg_links = scrape_duckduckgo(keyword)
        all_data.extend(ddg_links)
        
        # Sleep to be polite
        time.sleep(random.uniform(3, 6))

    # SAVE RESULTS
    if all_data:
        # Ensure folder exists
        os.makedirs('_data', exist_ok=True)
        
        # Create DataFrame
        new_df = pd.DataFrame(all_data)
        
        # Load existing data to avoid duplicates
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
        print(f"\nSUCCESS: Database now contains {len(final_df)} unique links.")
        print(f"File saved to: {OUTPUT_FILE}")
    else:
        print("\nFAILURE: No links found from any source.")

if __name__ == "__main__":
    main()