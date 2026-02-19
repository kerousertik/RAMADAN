"""Debug: Does the live fetch decode correctly and find og:image?"""
import requests, sys
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
url = "https://bx.alooytv6.xyz/watch/badal-talef.html"

r = requests.get(url, headers={
    "User-Agent": ua,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ar,en-US;q=0.9",
}, timeout=25)

print(f"Status: {r.status_code}")
print(f"Encoding: {r.encoding}")
print(f"Apparent encoding: {r.apparent_encoding}")
print(f"Content-Type: {r.headers.get('content-type')}")

# Use r.text (requests auto-decodes), also try r.content.decode
text = r.text
print(f"Text length: {len(text)}")
print(f"'video_thumb' in text: {'video_thumb' in text}")
print(f"'og:image' in text: {'og:image' in text}")

soup = BeautifulSoup(text, "html.parser")

# Try og:image
og = soup.find("meta", property="og:image")
print(f"\nog:image meta tag found: {og}")
if og:
    print(f"og:image content: {og.get('content')}")

# Try all meta tags
print("\nAll meta tags with 'image' in name or property:")
for m in soup.find_all("meta"):
    if "image" in str(m.get("property", "")) or "image" in str(m.get("name", "")):
        print(f"  {m}")
