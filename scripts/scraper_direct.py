import requests
import re
import pandas as pd
import os
import time
from bs4 import BeautifulSoup

# ==========================================
# 1. EXTENSIVE AUTO-CATEGORIES
# ==========================================
# The script checks these keywords in the group name.
# If a match is found, the group is moved to that category immediately.
AUTO_CATEGORIES = {
    # --- HIGH TRAFFIC NICHES ---
    "Cricket & Sports": [
        "cricket", "ipl", "match", "dream11", "football", "sport", "game", 
        "virat", "dhoni", "csk", "rcb", "mi", "messi", "ronaldo", "wwe", "kabaddi"
    ],
    "Gaming & Esports": [
        "pubg", "bgmi", "free fire", "ff", "fortnite", "minecraft", "gta", 
        "gamer", "gaming", "streamer", "ludo", "tournament", "esports", "ps5", "xbox"
    ],
    "Jobs & Careers": [
        "job", "vacancy", "hiring", "work", "internship", "sarkari", "naukri", 
        "resume", "hr", "company", "part time", "full time", "career", "placement"
    ],
    "Crypto & Money": [
        "crypto", "btc", "bitcoin", "eth", "trading", "forex", "invest", "money", 
        "earn", "profit", "binance", "stock", "share market", "bank", "finance", "loan"
    ],

    # --- ENTERTAINMENT ---
    "Movies & Web Series": [
        "movie", "netflix", "series", "web series", "cinema", "film", "bollywood", 
        "hollywood", "tollywood", "prime", "kdrama", "drama", "actor", "actress"
    ],
    "Funny, Memes & Viral": [
        "funny", "meme", "joke", "masti", "comedy", "video", "status", "viral", 
        "reel", "troll", "laugh", "bakchodi", "fun", "entertainment"
    ],
    "Shayari & Love": [
        "shayari", "love", "heart", "poetry", "sad", "romantic", "quote", 
        "status", "broken", "couple", "ishq", "mohabbat", "bf", "gf"
    ],
    "Girls & Friendship": [
        "girl", "boy", "friend", "dosti", "chat", "meet", "dating", "single", 
        "women", "lady", "aunt", "bhabhi", "friendship", "partner"
    ],

    # --- EDUCATION & TECH ---
    "Education & Students": [
        "study", "student", "class", "exam", "college", "university", "notes", 
        "upsc", "neet", "jee", "gk", "current affairs", "school", "book", "pdf", "library"
    ],
    "Tech, AI & Coding": [
        "python", "java", "coding", "developer", "hack", "tech", "web", "design", 
        "software", "android", "app", "chatgpt", "ai", "robot", "cyber", "linux"
    ],

    # --- REGIONAL (INDIA) ---
    "Kerala & Malayalam": [
        "kerala", "malayalam", "mallu", "kochi", "trivandrum", "kl"
    ],
    "Tamil & Telugu": [
        "tamil", "chennai", "telugu", "hyderabad", "tollywood", "kollywood", "thala", "thalapathy"
    ],
    "North India (Hindi/Punjabi)": [
        "hindi", "punjab", "delhi", "haryana", "up", "bihar", "marathi", "mumbai", "gujarat"
    ],

    # --- LIFESTYLE & INTERESTS ---
    "Shopping & Deals": [
        "deal", "offer", "sale", "discount", "amazon", "flipkart", "loot", 
        "coupon", "price", "shop", "buy", "sell"
    ],
    "YouTubers & Influencers": [
        "youtube", "subscriber", "sub4sub", "channel", "vlog", "influencer", 
        "instagram", "follower", "like", "share", "tiktok"
    ],
    "News & Politics": [
        "news", "politics", "bjp", "congress", "modi", "media", "update", "info", "reporter"
    ],
    "Religious & Spiritual": [
        "islam", "muslim", "allah", "quran", "hindu", "ram", "shiva", "bhakti", 
        "jesus", "bible", "christian", "prayer", "god", "ji"
    ],
    "Food & Travel": [
        "food", "recipe", "cook", "travel", "tour", "trip", "visa", "flight", "hotel"
    ],

    # --- GLOBAL ---
    "International (USA/UK)": [
        "usa", "uk", "america", "london", "canada", "australia", "dubai", "uae", "global", "world"
    ]
}

# ==========================================
# 2. SOURCE CONFIGURATION
# ==========================================
# If a group matches NO keywords above, it falls back to these categories based on source URL.
TARGETS = {
    "General Mix": [ 
        "https://whtsgroupslinks.com/active-whatsapp-group-links/",
        
       "https://whtsgroupslinks.com/",
       "https://whatsupgrouplink.com/",
       "https://www.wa-contact-extractor.com/post/active-whatsapp-group-links",
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
    "Indian Mix": [
        "https://whtsgroupslinks.com/indian-whatsapp-group-links/"
    ],
    "International Mix": [
        "https://whtsgroupslinks.com/usa-whatsapp-group-links/"
    ],
    "Girls Mix": [
        "https://whtsgroupslinks.com/girls-whatsapp-group-links/"
    ]
}

# ==========================================
# 3. SETTINGS
# ==========================================
OUTPUT_FILE = "_data/whatsapp_links.csv"

# Real Browser Headers to avoid getting blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# Generic names to REJECT (Anti-Spam)
BLOCKED_NAMES = [
    "Active WhatsApp Group",
    "WhatsApp Group Invite",
    "WhatsApp Group",
    "WhatsApp",
    "Group Invite",
    "Join Group"
]

# ==========================================
# 4. FUNCTIONS
# ==========================================

def determine_category(group_name, fallback_category):
    """
    Analyzes the group name against AUTO_CATEGORIES.
    Returns the specific category if a keyword matches.
    Otherwise returns the fallback_category.
    """
    if not group_name:
        return fallback_category
        
    name_lower = group_name.lower()
    
    for category, keywords in AUTO_CATEGORIES.items():
        for keyword in keywords:
            # Check if keyword exists in the group name
            if keyword in name_lower:
                return category
                
    return fallback_category

def validate_whatsapp_link(link):
    """
    Visits the link to check if it works and gets the REAL name.
    """
    try:
        response = requests.get(link, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()
            
            # Check for dead link indicators
            if "revoked" in page_text or "doesn't exist" in page_text or "reset" in page_text:
                return False, None
            
            group_name = None
            
            # Method A: Meta Tag (Best Quality)
            meta_title = soup.find("meta", property="og:title")
            if meta_title:
                group_name = meta_title.get("content")
            
            # Method B: Fallback to H3 tag
            if not group_name:
                h3_title = soup.find("h3")
                if h3_title:
                    group_name = h3_title.get_text(strip=True)

            # Final Name Check
            if group_name:
                clean_name = group_name.strip()
                
                # Reject if name is in the Blocked List
                if clean_name in BLOCKED_NAMES:
                    return False, None
                
                return True, clean_name

    except Exception:
        return False, None
        
    return False, None

def extract_links_from_page(html):
    """
    Finds all 'chat.whatsapp.com' links in the HTML source.
    """
    soup = BeautifulSoup(html, 'html.parser')
    candidates = []
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if "chat.whatsapp.com" in href:
            clean_link_match = re.search(r'https:\/\/chat\.whatsapp\.com\/[A-Za-z0-9]{20,}', href)
            if clean_link_match:
                candidates.append(clean_link_match.group(0))
                
    return list(set(candidates)) # Return unique links only

def main():
    print("--- STARTING ULTIMATE SCRAPER ---")
    valid_data = []

    # Loop through Source Categories
    for source_cat, urls_list in TARGETS.items():
        print(f"\nScanning Source: {source_cat}...")
        
        # Loop through URLs in that source
        for url in urls_list:
            print(f"  Reading Page: {url}")
            try:
                response = requests.get(url, headers=HEADERS, timeout=15)
                
                if response.status_code == 200:
                    potential_links = extract_links_from_page(response.text)
                    print(f"    -> Found {len(potential_links)} candidates. Validating...")
                    
                    for i, link in enumerate(potential_links):
                        # Validate and Get Name
                        is_active, real_name = validate_whatsapp_link(link)
                        
                        if is_active:
                            # Classify the Group
                            final_category = determine_category(real_name, source_cat)
                            
                            valid_data.append({
                                "category": final_category,
                                "group_name": real_name,
                                "whatsapp_link": link,
                                "status": "Active"
                            })
                            print(f"      [OK] {real_name} -> {final_category}")
                        else:
                            # Optional: Print rejected links (comment out to reduce noise)
                            # print(f"      [X] Dead or Generic")
                            pass
                        
                        # Sleep to prevent blocking (Crucial!)
                        time.sleep(1.5)
                else:
                    print(f"    !! Failed to load (Status: {response.status_code})")
            
            except Exception as e:
                print(f"    !! Error: {e}")
            
            # Sleep between pages
            time.sleep(2)

    # ==========================================
    # 5. SAVE TO CSV
    # ==========================================
    if valid_data:
        # Create folder
        os.makedirs('_data', exist_ok=True)
        
        new_df = pd.DataFrame(valid_data)
        
        # Merge with existing data
        if os.path.exists(OUTPUT_FILE):
            try:
                old_df = pd.read_csv(OUTPUT_FILE)
                final_df = pd.concat([new_df, old_df])
            except:
                final_df = new_df
        else:
            final_df = new_df

        # Remove duplicates (Keep the newest version)
        final_df = final_df.drop_duplicates(subset=['whatsapp_link'])
        
        # Save
        final_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nSUCCESS: Database updated. Total Active Links: {len(final_df)}")
    else:
        print("\nNo active links found in this run.")

if __name__ == "__main__":
    main()