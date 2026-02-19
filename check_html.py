"""Check what the actual HTML from the genre page contains."""
import requests
import random
import sys
sys.stdout.reconfigure(encoding='utf-8')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

url = "https://bx.alooytv6.xyz/genre/ramadan-arabi-2026.html"
headers = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

r = requests.get(url, headers=headers, timeout=30)
print(f"Status: {r.status_code}")
print(f"Content-Length: {len(r.text)}")

# Save full html for inspection
with open("genre_page.html", "w", encoding="utf-8") as f:
    f.write(r.text)
print("Saved full HTML to genre_page.html")

# Count /watch/ occurrences
count = r.text.count("/watch/")
print(f"/watch/ occurrences in HTML: {count}")

# Show first occurrence context
idx = r.text.find("/watch/")
if idx >= 0:
    print(f"Context around first /watch/: {r.text[max(0,idx-100):idx+200]}")
