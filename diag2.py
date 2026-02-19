"""Diagnose HTML structure of a series detail page."""
import requests, sys, re
sys.stdout.reconfigure(encoding='utf-8')

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
url = "https://bx.alooytv6.xyz/watch/badal-talef.html"
r = requests.get(url, headers={"User-Agent": ua, "Accept": "text/html,*/*", "Accept-Encoding": "identity"}, timeout=25)

print(f"Status: {r.status_code}")
print(f"Content-Length: {len(r.text)}")

# Search for video_thumb in raw text
if "video_thumb" in r.text:
    # Find the surrounding context
    idx = r.text.find("video_thumb")
    print(f"\nFound video_thumb at index {idx}")
    print(f"Context: ...{r.text[max(0,idx-200):idx+200]}...")
else:
    print("\nvideo_thumb NOT found in response")

# Search for uploads/
count = r.text.count("uploads/")
print(f"\n'uploads/' occurrences: {count}")
for m in re.finditer(r'uploads/[^\s\'"<>]+', r.text):
    print(f"  {m.group()[:100]}")

# Show first 2000 chars
print("\n--- First 2000 chars ---")
print(r.text[:2000])
