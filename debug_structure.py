import requests
from bs4 import BeautifulSoup
import sys

# Set up encoding to avoid crashes
sys.stdout.reconfigure(encoding='utf-8')

def safe_print(s):
    try:
        print(s)
    except Exception:
        print(str(s).encode('utf-8', errors='replace').decode('utf-8'))

print("Fetching genre page...")
try:
    r = requests.get('https://bx.alooytv6.xyz/genre/ramadan-arabi-2026.html', 
                     headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
    soup = BeautifulSoup(r.text, 'html.parser')

    print(f"Page title: {soup.title.string if soup.title else 'No title'}")

    # 1. Inspect Series Cards
    cards = soup.select('.film-poster')
    print(f"Found {len(cards)} elements with class .film-poster")
    
    if len(cards) > 0:
        first_card = cards[0]
        safe_print(f"First card HTML:\n{first_card.prettify()[:500]}")
        
        img = first_card.find('img')
        if img:
            print("Image tag found in card:")
            safe_print(img.attrs)
        else:
            print("No img tag found in card")
    else:
        # Fallback inspection if .film-poster is empty
        print("Checking for other common card classes...")
        for cls in ['.f-poster', '.poste', '.item', '.movie-poster', '.film-detail', '.flw-item']:
            count = len(soup.select(cls))
            print(f"Selector '{cls}': found {count}")
            if count > 0:
                 safe_print(soup.select(cls)[0].prettify()[:300])

    # 2. Inspect formatting in extract_series_from_genre
    # The scraper uses:
    # for card in soup.select(".film-poster"):
    #     a_tag = card.find("a", href=True)
    #     img_tag = card.find("img")
    
    # 3. Check Detail Page
    print("\nFetching detail page...")
    r2 = requests.get('https://bx.alooytv6.xyz/watch/badal-talef.html',
                      headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
    soup2 = BeautifulSoup(r2.text, 'html.parser')
    
    # Check for poster image in detail page
    poster_selectors = [".film-poster img", ".detail-poster img", ".dp-i-c-poster img", ".poster img", ".m-i-d-poster img"]
    found_poster = False
    for sel in poster_selectors:
        p = soup2.select_one(sel)
        if p:
            print(f"Found poster in detail page using '{sel}':")
            safe_print(p.attrs)
            found_poster = True
            break
    
    if not found_poster:
        print("No poster found with standard selectors. Listing all large images:")
        for img in soup2.find_all('img'):
            src = img.get('src') or img.get('data-src') or ''
            if 'thumb' in src or 'poster' in src or 'uploads' in src:
                safe_print(f"Potential poster: {src}")

except Exception as e:
    safe_print(f"Error: {e}")
