import argparse
import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import gemini_bridge
import google.generativeai as genai
import shutil

# Setup Colorama
try:
    from colorama import Fore, Style, init
    init()
except ImportError:
    class Fore: RED = GREEN = YELLOW = CYAN = MAGENTA = ""
    class Style: RESET_ALL = BRIGHT = ""

def ensure_loot_dir(domain: str) -> str:
    """Creates a timestamped loot directory."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    clean_domain = "".join(c for c in domain if c.isalnum() or c in "._-")
    loot_dir = os.path.join("loot", f"{timestamp}_{clean_domain}")
    os.makedirs(loot_dir, exist_ok=True)
    return loot_dir

def download_file(url: str, directory: str):
    """Downloads a single file to the valid directory."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        filename = os.path.basename(urlparse(url).path)
        if not filename: filename = "index.html"
        
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): 
                f.write(chunk)
        
        print(f"{Fore.GREEN}[DOWNLOADED] {filename}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[FAIL] Could not download {url}: {e}{Style.RESET_ALL}")

def ai_filter_assets(assets: list, query: str) -> list:
    """
    Uses Gemini to filter the list of assets based on the user's query.
    """
    if not assets: return []
    
    print(f"{Fore.CYAN}[AI SCAN] Analyzing {len(assets)} potential assets against mission: '{query}'...{Style.RESET_ALL}")

    # Re-use Gemini Bridge Auth
    creds = gemini_bridge.authenticate_oauth()
    api_key = None
    if not creds:
        try:
             import google.auth
             creds, _ = google.auth.default()
        except: pass
        if not creds:
            api_key = gemini_bridge.load_env_file() or gemini_bridge.get_api_key(argparse.Namespace(api_key=None, key_file=None))
    
    if not creds and not api_key:
        print(f"{Fore.RED}[AUTH WARNING] AI Filter offline (No Auth). Downloading ALL assets.{Style.RESET_ALL}")
        return assets # Fallback: Download everything if no Brain

    if creds: genai.configure(credentials=creds)
    elif api_key: genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Construct a manifest for the AI
    # We send a text block of valid URLs
    asset_manifest = "\n".join(assets[:500]) # Limit to 500 to save tokens/time
    
    prompt = (
        f"MISSION: Select files from the list below that match the user's requirement: '{query}'.\n"
        "CRITERIA: valid image/document extensions only. Ignore tracking pixels or junk.\n"
        "OUTPUT: Return ONLY the raw URLs that match, one per line. No markdown, no explanations.\n\n"
        f"ASSET LIST:\n{asset_manifest}"
    )
    
    try:
        response = model.generate_content(prompt)
        filtered_urls = [line.strip() for line in response.text.split('\n') if line.strip()]
        print(f"{Fore.MAGENTA}[AI TARGETING] Locked on {len(filtered_urls)} viable targets.{Style.RESET_ALL}")
        return filtered_urls
    except Exception as e:
        print(f"{Fore.RED}[AI ERROR] {e}. Fallback: Downloading all.{Style.RESET_ALL}")
        return assets

import memory_core

def harvest(url: str, query: str):
    print(f"{Fore.MAGENTA}>>> HARVESTER AGENT DEPLOYED: {url}{Style.RESET_ALL}")
    
    try:
        # 1. Recon (Fetch HTML)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. Identify Assets (Images & Links)
        potential_assets = []
        
        # Images
        for img in soup.find_all('img'):
            src = img.get('src')
            if src: potential_assets.append(urljoin(url, src))
            
        # Linked Files (PDF, ZIP, etc. - simplistic heuristic, AI will refine)
        for a in soup.find_all('a'):
            href = a.get('href')
            if href:
                full_url = urljoin(url, href)
                # Quick extension check to avoid crawling nav links
                if any(full_url.lower().endswith(ext) for ext in ['.pdf', '.zip', '.docx', '.png', '.jpg', '.jpeg', '.svg', '.json']):
                    potential_assets.append(full_url)
        
        potential_assets = list(set(potential_assets)) # Dedup
        
        if not potential_assets:
            print(f"{Fore.YELLOW}[INTEL] No assets found on landing zone.{Style.RESET_ALL}")
            return

        # 3. AI Filtering
        targets = ai_filter_assets(potential_assets, query)
        
        if not targets:
            print(f"{Fore.YELLOW}[INTEL] No assets matched your specific query.{Style.RESET_ALL}")
            return

        # 4. Exfiltrate (Download)
        domain = urlparse(url).netloc
        loot_dir = ensure_loot_dir(domain)
        print(f"{Fore.CYAN}[EXFILTRATION] Saving to: {loot_dir}/{Style.RESET_ALL}")
        
        download_count = 0
        for target_url in targets:
            download_file(target_url, loot_dir)
            download_count += 1
            
        print(f"\n{Fore.GREEN}>>> MISSION COMPLETE. LOOT SECURED.{Style.RESET_ALL}")
        
        # LOG TO MEMORY
        memory_core.append_log("HARVESTER", f"Scraped {url}\nQuery: {query}\nAssets Secured: {download_count}\nLocation: {loot_dir}", "LOOT")

    except Exception as e:
        print(f"{Fore.RED}[FATAL] Mission Failed: {e}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description="Outlaw Exotix Harvester Agent")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("query", help="Search criteria (e.g. 'download images of cats')")
    args = parser.parse_args()
    
    harvest(args.url, args.query)

if __name__ == "__main__":
    main()
