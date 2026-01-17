import requests
import re
import pandas as pd
import os
import time
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
TARGETS = {
    "Indian Groups": "https://whtsgroupslinks.com/indian-whatsapp-group-links/",
    "USA Groups": "https://whtsgroupslinks.com/usa-whatsapp-group-links/",
    "Funny & Memes": "https://whtsgroupslinks.com/funny-whatsapp-group-links/",
    "Girls & Friendship": "https://whtsgroupslinks.com/girls-whatsapp-group-links/"
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
        # We allow redirects because valid links often redirect slightly
        response = requests.get(link, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Check for specific error messages indicating a dead link
            page_text = soup.get_text().lower()
            if "revoked" in page_text or "doesn't exist" in page_text or "reset" in page_text:
                return False, None
            
            # 2. Extract Real Group Name from Meta Tags (Most Reliable)
            # Valid groups usually have the name in the 'og:title' tag
            meta_title = soup.find("meta", property="og:title")
            
            if meta_title:
                group_name = meta_title.get("content")
                
                # Filter out generic titles that appear when data is hidden/loading
                if group_name and "WhatsApp Group Invite" not in group_name and "WhatsApp" != group_name:
                    return True, group_name
                
                # If the name is generic but the link didn't fail, it's likely active but private
                # We return True but mark name as "Unknown Active Group"
                return True, "Active WhatsApp Group"
            
            # Fallback: specific h3 classes often hold the title
            h3_title = soup.find("h3")
            if h3_title:
                return True, h3_title.get_text(strip=True)

    except Exception as e:
        print(f"    ! Validation Error: {e}")
        return False, None

    return False, None

def extract_links_from_page(html, category):
    soup = BeautifulSoup(html, 'html.parser')
    candidates = []

    # Find all WhatsApp Links
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if "chat.whatsapp.com" in href:
            clean_link_match = re.search(r'https:\/\/chat\.whatsapp\.com\/[A-Za-z0-9]{20,}', href)
            if clean_link_match:
                candidates.append(clean_link_match.group(0))
    
    return list(set(candidates)) # Return unique links only

def main():
    print("--- STARTING VALIDATED SCRAPE ---")
    valid_data = []

    for category, url in TARGETS.items():
        print(f"Scraping Source: {category}...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                # 1. Get all potential links from the site
                potential_links = extract_links_from_page(response.text, category)
                print(f"  -> Found {len(potential_links)} potential links. Validating now...")
                
                # 2. Validate each link (Check if Active)
                for i, link in enumerate(potential_links):
                    print(f"    [{i+1}/{len(potential_links)}] Checking: {link}", end="\r")
                    
                    is_active, real_name = validate_whatsapp_link(link)
                    
                    if is_active:
                        valid_data.append({
                            "category": category,
                            "group_name": real_name, # The REAL name from WhatsApp