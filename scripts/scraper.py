import requests
import re
import pandas as pd
import os
import datetime
import time
import random

# --- CONFIGURATION ---
KEYWORDS = ["whatsapp group link", "whatsapp chat invite", "active whatsapp"]
# Search specific subreddits that allow links
SUBREDDITS = ["WhatsAppGroupLinks", "groups", "whatsapp", "TelegramGroupLinks"] 
OUTPUT_FILE = "_data/whatsapp_links.csv"

# Real browser headers to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_links(text):
    if not text: return []
    # Regex for WhatsApp invite links
    return re.findall(r'https:\/\/chat\.whatsapp\.com\/[A-Za-z0-9]{20,}', text)

def scrape_subreddit(subreddit):
    print(f"Checking r/{subreddit}...")
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=50"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            return posts
        elif response.status_code == 429:
            print("  !! Rate limited (429). Sleeping for 10s...")
            time.sleep(10)
    except Exception as e:
        print(f"  Error: {e}")
    return []

def search_reddit(keyword):
    print(f"Searching for '{keyword}'...")
    # Search URL with .json
    url = f"https://www.reddit.com/search.json?q={keyword}&sort=new&limit=50"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get("data", {}).get("children", [])
    except Exception as e:
        print(f"  Error: {e}")
    return []

def main():
    print("--- STARTING NO-API SCRAPE ---")
    all_links = []
    
    # 1. Scrape specific subreddits
    for sub in SUBREDDITS:
        posts = scrape_subreddit(sub)
        for post in posts:
            post_data = post.get("data", {})
            found = extract_links(post_data.get("title", "") + " " + post_data.get("selftext", ""))
            
            for link in found:
                all_links.append({
                    "group_name": post_data.get("title")[:50].replace("|", "").strip() + "...",
                    "whatsapp_link": link,
                    "date_added": datetime.date.today().isoformat(),
                    "status": "Active"
                })
        time.sleep(random.uniform(2, 5)) # Sleep to look human

    # 2. Search for keywords
    for keyword in KEYWORDS:
        posts = search_reddit(keyword)
        for post in posts:
            post_data = post.get("data", {})
            found = extract_links(post_data.get("title", "") + " " + post_data.get("selftext", ""))
            
            for link in found:
                all_links.append({
                    "group_name": post_data.get("title")[:50].replace("|", "").strip() + "...",
                    "whatsapp_link": link,
                    "date_added": datetime.date.today().isoformat(),
                    "status": "Active"
                })
        time.sleep(random.uniform(2, 5))

    # 3. Save Data
    if all_links:
        # Create _data folder if not exists
        os.makedirs('_data', exist_ok=True)
        
        # Load existing file if it exists (to avoid deleting old links)
        if os.path.exists(OUTPUT_FILE):
            try:
                old_df = pd.read_csv(OUTPUT_FILE)
                new_df = pd.DataFrame(all_links)
                combined_df = pd.concat([old_df, new_df])
            except:
                combined_df = pd.DataFrame(all_links)
        else:
            combined_df = pd.DataFrame(all_links)

        # Remove duplicates
        combined_df = combined_df.drop_duplicates(subset=['whatsapp_link'])
        
        # Save
        combined_df.to_csv(OUTPUT_FILE, index=False)
        print(f"SUCCESS: Total links in database: {len(combined_df)}")
    else:
        print("No new links found.")

if __name__ == "__main__":
    main()