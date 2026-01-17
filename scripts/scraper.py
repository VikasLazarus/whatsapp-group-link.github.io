import praw
import re
import pandas as pd
import os
import datetime

# 1. SETUP CREDENTIALS
reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
    user_agent="GroupLinkScraper/1.0",
)

# 2. CONFIGURATION
KEYWORDS = ["whatsapp group link", "whatsapp chat invite"]
SUBREDDITS = "all"
LIMIT = 100 

def extract_links(text):
    if not text: return []
    return re.findall(r'https:\/\/chat\.whatsapp\.com\/[A-Za-z0-9]{20,}', text)

def main():
    print("--- STARTING SCRAPE ---")
    all_links = []
    
    for keyword in KEYWORDS:
        try:
            print(f"Searching: {keyword}")
            for post in reddit.subreddit(SUBREDDITS).search(keyword, sort="new", limit=LIMIT):
                found = extract_links(post.title + " " + post.selftext)
                for link in found:
                    all_links.append({
                        "group_name": post.title[:50].replace("|", "") + "...", # Clean title
                        "whatsapp_link": link,
                        "date_added": datetime.date.today().isoformat(),
                        "status": "Active"
                    })
        except Exception as e:
            print(f"Error: {e}")

    if all_links:
        # 3. SAVE TO _DATA FOLDER
        df = pd.DataFrame(all_links)
        df = df.drop_duplicates(subset=['whatsapp_link'])
        
        # Ensure directory exists
        os.makedirs('_data', exist_ok=True)
        
        # Save file (Overwrite old one to keep site fresh)
        df.to_csv('_data/whatsapp_links.csv', index=False)
        print(f"SUCCESS: Saved {len(df)} links to _data/whatsapp_links.csv")
    else:
        print("No new links found.")

if __name__ == "__main__":
    main()