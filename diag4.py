"""Test the scraper's fetch + og:image on a single series."""
import requests, random, sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
sys.stdout.reconfigure(encoding='utf-8')

BASE = "https://bx.alooytv6.xyz"
UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]
s = requests.Session()
s.headers.update({
    "User-Agent": random.choice(UA),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
})

url = f"{BASE}/watch/badal-talef.html"
r = s.get(url, timeout=25)
print(f"Status: {r.status_code}")
print(f"Length: {len(r.text)}")

soup = BeautifulSoup(r.text, "html.parser")
og = soup.find("meta", property="og:image")
print(f"og:image: {og}")
if og:
    print(f"Content: {og.get('content')}")
