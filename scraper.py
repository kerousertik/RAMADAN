"""
Ramadan 2026 – مسلسلات عربية فقط
Fetches images from series pages. Run with --serve to auto-update.
"""
import json, time, sys, os, re, random, threading
import http.server, socketserver, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

BASE = "https://bx.alooytv6.xyz"
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# عربي فقط
KNOWN_SERIES = [
    ("بنت النعمان",                      "bint-al-noaman"),
    ("الخروج إلى البئر",                 "al-khuroog-ila-al-ber"),
    ("ثعالب الصحراء",                    "thaealib-al-sahara"),
    ("سجون الشيطان",                     "sojun-alshaytan"),
    ("عمارة السعادة",                    "omaret-el-saada"),
    ("بدل تالف",                         "badal-talef"),
    ("أنا وهي وهيا",                     "ana-wa-heya-wa-haya"),
    ("رامز ليفل الوحش",                  "ramez-level-el-wahsh"),
    ("روج أسود",                         "rouge-eswed"),
    ("السرايا الصفرا",                   "el-saraya-el-safra"),
    ("شمس الأصيل",                      "shams-el-aseel"),
    ("يا أنا يا هي ج2",                  "ya-ana-ya-heya-2"),
    ("اليتيم",                          "al-yateem"),
    ("السوق الحرة",                     "al-souq-al-hurra"),
    ("مناعة",                           "mannaa"),
    ("لوبي الغرام",                      "lubby-al-gharam"),
    ("عيلة الملك",                      "elet-al-malek"),
    ("النويلاتي",                        "al-noelati"),
    ("اسأل روحك",                       "esaal-rouhak"),
    ("بنات العم ج2 : انتقام الموتى",     "banat-al-am-2"),
    ("عرش الشيطان",                     "arsh-al-shaytan"),
    ("المصيدة",                         "el-masyada"),
    ("المداح ج6: أسطورة النهاية",        "al-maddah-6-ostorat-al-nehaya"),
    ("قطر صغنطوط",                      "atr-soghantoot"),
    ("عين سحرية",                       "ein-sehreya"),
    ("كان يا مكان",                     "kan-ya-makan"),
    ("حكاية نرجس",                      "hekayet-narges"),
    ("أولاد الراعي",                     "awlad-el-raaey"),
    ("حد أقصى",                         "had-aqsa"),
    ("بيبو",                            "bibo"),
    ("توابع",                           "tawabea"),
    ("رأس الأفعى",                      "ras-al-afaa"),
    ("درش",                             "darsh"),
    ("بابا وماما جيران",                 "baba-w-mama-giran"),
    ("اللون الأزرق",                    "al-lawn-al-azraq"),
    ("سعادة المجنون",                   "saadaet-al-magnoun"),
    ("صحاب الأرض",                     "sohab-al-ard"),
    ("سوا سوا",                         "sawa-sawa"),
    ("عرض وطلب",                        "aard-w-talab"),
    ("على قد الحب",                     "ala-add-el-hob"),
    ("كلهم بيحبوا مودي",                 "kollohom-beehebbo-moody"),
    ("علي كلاي",                        "ali-clay"),
    ("فخر الدلتا",                      "fakhr-el-delta"),
    ("فرصة أخيرة",                      "forsa-akhira"),
    ("فن الحرب",                        "fan-al-harb"),
    ("اتنين غيرنا",                     "etnen-gherna"),
    ("أب ولكن",                         "ab-wa-laken"),
    ("مطبخ المدينة",                    "matbakh-al-madinah"),
    ("مولانا",                          "mawlana"),
    ("ن النسوة",                        "noon-el-neswa"),
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]


def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
    })
    return s


session = make_session()


def fetch(url, retries=4):
    global session
    for attempt in range(retries):
        try:
            r = session.get(url, timeout=25)
            if r.status_code in (521, 522, 523, 524):
                wait = 6 + attempt * 4 + random.uniform(1, 3)
                print(f"  [CF-{r.status_code}] retrying in {wait:.1f}s...")
                session = make_session()
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.text
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response else 0
            if attempt < retries - 1:
                time.sleep(5 + attempt * 5)
                session = make_session()
            else:
                raise
        except requests.exceptions.RequestException:
            if attempt < retries - 1:
                time.sleep(5 + attempt * 4)
            else:
                raise
    raise RuntimeError(f"Failed: {url}")


def get_image(html):
    soup = BeautifulSoup(html, "html.parser")
    og = soup.find("meta", property="og:image")
    if og:
        src = og.get("content", "")
        if src and "blank" not in src:
            return src if src.startswith("http") else urljoin(BASE, src)
    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        if "video_thumb" in src:
            return src if src.startswith("http") else urljoin(BASE, src)
    return ""


def get_description(html):
    soup = BeautifulSoup(html, "html.parser")
    for sel in [".description", ".film-description", ".dp-i-c-des", "[itemprop='description']"]:
        d = soup.select_one(sel)
        if d:
            txt = d.get_text(strip=True)
            if txt and len(txt) > 10:
                return txt[:300]
    og = soup.find("meta", property="og:description")
    if og:
        return og.get("content", "")[:300]
    return ""


def scrape_all():
    existing = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            try:
                old = json.load(f)
                for s in old.get("series", []):
                    existing[s["link"]] = s
            except Exception:
                pass

    all_series = []

    for title, slug in KNOWN_SERIES:
        url = f"{BASE}/watch/{slug}.html"
        cached = existing.get(url, {})

        print(f"  ▶ {title}")

        image = cached.get("image", "")
        description = cached.get("description", "")

        if not image:
            try:
                html = fetch(url)
                image = get_image(html)
                if not description:
                    description = get_description(html)
                time.sleep(random.uniform(0.25, 0.6))
            except Exception as e:
                print(f"    [WARN] {e}")

        all_series.append({
            "title": title,
            "link": url,
            "image": image,
            "description": description,
            "quality": cached.get("quality", "HD"),
        })

    return {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(all_series),
        "series": all_series,
    }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Saved {data['total']} series to data.json")
    print(f"   Last updated: {data['last_updated']}")


def run_scraper():
    print("\n🌙 رمضان 2026 — Scraper")
    print("=" * 50)
    data = scrape_all()
    save_data(data)
    return data


def auto_update_loop(interval_minutes=30):
    while True:
        try:
            run_scraper()
        except Exception as e:
            print(f"\n[ERROR] {e}")
        print(f"\n⏰ Next update in {interval_minutes} minutes...")
        time.sleep(interval_minutes * 60)


def serve(port=8000):
    directory = os.path.dirname(os.path.abspath(__file__))
    run_scraper()
    updater = threading.Thread(target=auto_update_loop, args=(30,), daemon=True)
    updater.start()
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler

    class QuietHandler(handler):
        def log_message(self, format, *args):
            pass  # Silence request logs

    with socketserver.TCPServer(("", port), QuietHandler) as httpd:
        print(f"\n🚀 http://localhost:{port}")
        print(f"   Auto-updates every 30 min\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Stopped.")


if __name__ == "__main__":
    if "--serve" in sys.argv:
        port = 8000
        for i, arg in enumerate(sys.argv):
            if arg == "--port" and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
        serve(port)
    else:
        run_scraper()
