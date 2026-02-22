"""
Ramadan 2026 - Production Server by Karas
Works locally & on Railway/Render/Fly.io
"""

from datetime import datetime
import os, json, time, threading, datetime as dt
import sqlite3
import smtplib
import base64
import http.server
import urllib.parse
import socketserver
import requests
import re
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visitors.db")
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "komo2026")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visitors (
        device_id TEXT PRIMARY KEY,
        ip TEXT,
        name TEXT,
        user_agent TEXT,
        first_seen DATETIME,
        last_seen DATETIME,
        last_page TEXT,
        visits_count INTEGER,
        is_blocked INTEGER DEFAULT 0,
        country TEXT DEFAULT 'Unknown',
        total_time_seconds INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS visits_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        ip TEXT,
        name TEXT,
        user_agent TEXT,
        page TEXT,
        time DATETIME,
        duration_seconds INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

init_db()

# Add new columns to existing dbs if needed
try:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("ALTER TABLE visitors ADD COLUMN is_blocked INTEGER DEFAULT 0")
    conn.execute("ALTER TABLE visitors ADD COLUMN country TEXT DEFAULT 'Unknown'")
    conn.execute("ALTER TABLE visitors ADD COLUMN total_time_seconds INTEGER DEFAULT 0")
    conn.execute("ALTER TABLE visits_log ADD COLUMN duration_seconds INTEGER DEFAULT 0")
    conn.commit()
    conn.close()
except:
    pass

SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "komonashat222@gmail.com")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "srckjctweknkuuwk")
RECEIVER_EMAIL = SENDER_EMAIL

def send_notification_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"📧 Email sent: {subject}", flush=True)
    except Exception as e:
        print(f"❌ Email error: {e}", flush=True)

def notify_async(subject, body):
    threading.Thread(target=send_notification_email, args=(subject, body), daemon=True).start()

def get_client_ip(headers, client_address):
    x_forwarded_for = headers.get('X-Forwarded-For')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return client_address[0]

def get_country_from_ip(ip):
    if ip in ['127.0.0.1', '::1', 'localhost'] or ip.startswith('192.168.'):
        return 'Local Network'
    try:
        req = requests.get(f'http://ip-api.com/json/{ip}?fields=country', timeout=2)
        if req.status_code == 200:
            return req.json().get('country', 'Unknown')
    except:
        pass
    return 'Unknown'


BASE = "https://a.alooytv7.xyz"
PORT = int(os.environ.get("PORT", 9002))
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity", "Referer": BASE}

# Stable entry points to find the current domain
GATEWAYS = [
    "https://fitnur.com/alooytv",
    "https://alooytv.com",
    "https://bx.alooytv6.xyz"
]

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
    ("إفراج",                           "efrag"),
    ("الكينج",                          "el-king"),
    ("وننسى اللي كان",                  "we-nensa-elly-kan"),
    ("الست موناليزا",                   "el-set-monaliza"),
    ("شرارة",                           "sharara"),
    ("بخمس أرواح",                      "be-5-arwah"),
    ("حمدية",                           "hamdiyya"),
    ("حامض حلو ج7",                     "hammed-helw-7"),
    ("بالحرام",                         "bil-haram"),
    ("رحمة ج2",                         "rahma-2"),
]

# In-memory cache
_cache = {"series": [], "last_updated": ""}

# ─── Self-Healing Domain Resolver ─────────────────────────────────────────────

def resolve_base():
    global BASE, HEADERS
    print("🔍 Resolving active domain...", flush=True)
    for g in GATEWAYS:
        try:
            r = requests.get(g, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
            if r.status_code == 200:
                # 1. Try redirect URL
                if "alooytv" in r.url and ".xyz" in r.url:
                    new_base = "/".join(r.url.split("/")[:3])
                    if new_base != BASE:
                        BASE = new_base
                        HEADERS["Referer"] = BASE
                        print(f"✨ Found new domain (redirect): {BASE}", flush=True)
                    return True
                
                # 2. Try scraping links (e.g. "رمضان عربي 2026" link)
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    h = a["href"]
                    if "alooytv" in h and (".xyz" in h or ".link" in h):
                        new_base = "/".join(h.split("/")[:3])
                        BASE = new_base
                        HEADERS["Referer"] = BASE
                        print(f"✨ Found new domain (link): {BASE}", flush=True)
                        return True
        except Exception:
            continue
    print(f"⚠️ Could not resolve new domain, staying with: {BASE}", flush=True)
    return False

# ─── Fetch ────────────────────────────────────────────────────────────────────

def fetch(url, retries=2, auto_resolve=True):
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            if r.status_code == 200:
                return r.text
            if r.status_code == 404 and auto_resolve:
                resolve_base() # Maybe the domain shifted
                url = url.replace(url.split("/")[2], BASE.split("/")[2]) # Update domain in URL
        except Exception:
            if i < retries - 1:
                if auto_resolve: resolve_base()
                time.sleep(2)
    return ""


# ─── Episode helpers ──────────────────────────────────────────────────────────

def get_episodes(slug):
    html = fetch(f"{BASE}/watch/{slug}.html")
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    episodes, seen = [], set()
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if "key=" in h and slug in h:
            full = h if h.startswith("http") else urljoin(BASE, h)
            if full in seen:
                continue
            seen.add(full)
            txt = a.get_text(strip=True)
            m = re.search(r'(\d+)', txt)
            ep_num = int(m.group(1)) if m else len(episodes) + 1
            episodes.append({"num": ep_num, "url": full, "title": f"الحلقة {ep_num}"})
    episodes.sort(key=lambda x: x["num"])
    return episodes


def get_video_url(episode_url):
    html = fetch(episode_url)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    # Direct <source src="...">
    for s in soup.find_all("source"):
        src = s.get("src", "")
        if src and (".mp4" in src or ".m3u8" in src):
            return src if src.startswith("http") else urljoin(BASE, src)
    # <video src="...">
    for v in soup.find_all("video"):
        src = v.get("src", "")
        if src:
            return src if src.startswith("http") else urljoin(BASE, src)
    # JS file: "..."
    for sc in soup.find_all("script"):
        t = sc.string or ""
        m = re.search(r'(?:file|src)["\s:]+["\']?(https?://[^"\'>\s]+\.(?:mp4|m3u8)[^"\'>\s]*)', t)
        if m:
            return m.group(1)
    # Fallback: any .mp4 URL in HTML
    m = re.search(r'(https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*)', html)
    return m.group(1) if m else None


# ─── Scraper ──────────────────────────────────────────────────────────────────

def scrape_all():
    global _cache
    # Load existing images from file or memory to avoid re-fetching
    existing = {s["link"]: s for s in _cache.get("series", [])}
    if not existing and os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            try:
                for s in json.load(f).get("series", []):
                    existing[s["link"]] = s
            except Exception:
                pass

    all_series = []
    for title, slug in KNOWN_SERIES:
        url = f"{BASE}/watch/{slug}.html"
        cached = existing.get(url, {})
        print(f"  ▶ {title}", flush=True)
        image = cached.get("image", "")
        if not image:
            try:
                html = fetch(url)
                if html:
                    soup = BeautifulSoup(html, "html.parser")
                    og = soup.find("meta", property="og:image")
                    if og:
                        src = og.get("content", "")
                        if src and "blank" not in src:
                            image = src if src.startswith("http") else urljoin(BASE, src)
                time.sleep(random.uniform(0.2, 0.5))
            except Exception as e:
                print(f"    [WARN] {e}", flush=True)
        all_series.append({"title": title, "slug": slug, "link": url, "image": image})

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {"last_updated": ts, "total": len(all_series), "series": all_series}
    _cache = data
    # Save to disk if possible
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    print(f"\n✅ Saved {len(all_series)} series", flush=True)
    return data


# ─── HTTP Handler ─────────────────────────────────────────────────────────────

class Handler(http.server.SimpleHTTPRequestHandler):

    def require_auth(self):
        auth_header = self.headers.get('Authorization')
        if auth_header:
            try:
                auth_type, encoded_creds = auth_header.split(' ', 1)
                if auth_type.lower() == 'basic':
                    creds = base64.b64decode(encoded_creds).decode('utf-8')
                    user, pw = creds.split(':', 1)
                    if user == ADMIN_USER and pw == ADMIN_PASS:
                        return False
            except Exception:
                pass
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Admin Dashboard"')
        self.end_headers()
        self.wfile.write(b'Unauthorized Access')
        return True


    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/" or parsed.path == "/index.html":
            index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "index.html")
            try:
                with open(index_path, "r", encoding="utf-8") as f:
                    html = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
            except Exception as e:
                self._json(500, {"error": str(e)})
            return

        if parsed.path == "/admin":
            if self.require_auth(): return
            dash_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.html")
            try:
                with open(dash_path, "r", encoding="utf-8") as f:
                    html = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
            except Exception as e:
                self._json(500, {"error": str(e)})
            return

        if parsed.path == "/api/data":
            device_id = (params.get("device_id") or [""])[0]
            if device_id:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("SELECT is_blocked FROM visitors WHERE device_id = ?", (device_id,))
                row = c.fetchone()
                conn.close()
                if row and row[0] == 1:
                    return self._json(403, {"error": "blocked"})

            body = json.dumps(_cache, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        elif parsed.path == "/api/episodes":
            slug = (params.get("slug") or [""])[0]
            if not slug:
                return self._json(400, {"error": "no slug"})
            print(f"  📋 Episodes: {slug}", flush=True)
            eps = get_episodes(slug)
            self._json(200, {"episodes": eps})

        elif parsed.path == "/api/stream":
            ep_url = urllib.parse.unquote((params.get("url") or [""])[0])
            if not ep_url:
                return self._json(400, {"error": "no url"})
            print(f"  🎬 Stream: {ep_url[-60:]}", flush=True)
            video_url = get_video_url(ep_url)
            if video_url:
                print(f"     ✅ {video_url[:80]}", flush=True)
                self._json(200, {"url": video_url})
            else:
                self._json(500, {"error": "video not found"})

        elif parsed.path == "/api/dashboard/devices":
            if self.require_auth(): return
            try:
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute("SELECT * FROM visitors ORDER BY last_seen DESC")
                rows = [dict(r) for r in c.fetchall()]
                conn.close()
                now = datetime.now()
                for r in rows:
                    try:
                        last = datetime.fromisoformat(r['last_seen'])
                        diff = (now - last).total_seconds()
                        r['status'] = 'Online' if diff <= 15 else 'Offline'
                    except:
                        r['status'] = 'Unknown'
                    
                    # Add formatted time
                    secs = r.get('total_time_seconds', 0) or 0
                    r['total_time_formatted'] = f"{secs // 60}m {secs % 60}s"
                self._json(200, {"devices": rows})
            except Exception as e:
                self._json(500, {"error": str(e)})

        elif parsed.path == "/api/dashboard/visits":
            if self.require_auth(): return
            try:
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                # Join with visitors to get country for the visit log
                c.execute('''
                    SELECT l.*, v.country 
                    FROM visits_log l
                    LEFT JOIN visitors v ON l.device_id = v.device_id
                    ORDER BY l.id DESC LIMIT 200
                ''')
                rows = [dict(r) for r in c.fetchall()]
                conn.close()
                for r in rows:
                    ds = r.get('duration_seconds', 0) or 0
                    r['duration_formatted'] = f"{ds // 60}m {ds % 60}s"
                self._json(200, {"visits": rows})
            except Exception as e:
                self._json(500, {"error": str(e)})

        else:
            super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        
        if path == "/api/heartbeat":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                device_id = data.get('device_id', 'unknown')
                name = data.get('name', '')
                user_agent = data.get('userAgent', '')
                page = data.get('page', '')
                ip = get_client_ip(self.headers, self.client_address)
                now = datetime.now()
                now_iso = now.isoformat()
                
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                
                c.execute("SELECT first_seen, last_seen, visits_count, is_blocked, country, total_time_seconds FROM visitors WHERE device_id = ?", (device_id,))
                row = c.fetchone()
                
                if row and row[3] == 1: # user is blocked
                    conn.close()
                    return self._json(403, {"error": "blocked"})
                
                if not row:
                    country = get_country_from_ip(ip)
                    # New device
                    c.execute('''INSERT INTO visitors (device_id, ip, name, user_agent, first_seen, last_seen, last_page, visits_count, country, total_time_seconds)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, 0)''', 
                              (device_id, ip, name, user_agent, now_iso, now_iso, page, country))
                    notify_async("🚨 جهاز جديد دخل الموقع", f"وقت الدخول: {now_iso}\nIP: {ip}\nالبلد: {country}\nDevice ID: {device_id}\nالصفحة: {page}\nالمتصفح: {user_agent}")
                    
                    c.execute('''INSERT INTO visits_log (device_id, ip, name, user_agent, page, time, duration_seconds)
                             VALUES (?, ?, ?, ?, ?, ?, 0)''', (device_id, ip, name, user_agent, page, now_iso))
                else:
                    first_seen, last_seen_iso, visits_count, is_blocked, country, total_time_seconds = row
                    if total_time_seconds is None: total_time_seconds = 0
                    
                    if country == 'Unknown' or not country:
                        country = get_country_from_ip(ip)

                    try:
                        last_seen_dt = datetime.fromisoformat(last_seen_iso)
                    except Exception:
                        last_seen_dt = now
                        
                    time_diff = (now - last_seen_dt).total_seconds()
                    visits_count_new = visits_count
                    
                    # Update duration for the last visit log
                    if 0 < time_diff < 30 * 60: # still in the same session
                        # Increase duration_seconds in visits_log, ensuring it starts from 0 if NULL
                        c.execute('''
                            UPDATE visits_log 
                            SET duration_seconds = COALESCE(duration_seconds, 0) + ? 
                            WHERE id = (SELECT id FROM visits_log WHERE device_id = ? ORDER BY id DESC LIMIT 1)
                        ''', (int(time_diff), device_id))
                        total_time_seconds += int(time_diff)
                    
                    if time_diff > 30 * 60: # 30 minutes offline means new visit
                        notify_async("🔙 جهاز رجع للموقع", f"وقت الدخول: {now_iso}\nIP: {ip}\nالبلد: {country}\nDevice ID: {device_id}\nالصفحة: {page}\nالمتصفح: {user_agent}\nمدة الغياب: {int(time_diff/60)} دقيقة")
                        visits_count_new += 1
                        c.execute('''INSERT INTO visits_log (device_id, ip, name, user_agent, page, time, duration_seconds)
                             VALUES (?, ?, ?, ?, ?, ?, 0)''', (device_id, ip, name, user_agent, page, now_iso))
                        
                    c.execute('''UPDATE visitors SET last_seen = ?, last_page = ?, ip = ?, user_agent = ?, visits_count = ?, country = ?, total_time_seconds = ? WHERE device_id = ?''',
                              (now_iso, page, ip, user_agent, visits_count_new, country, total_time_seconds, device_id))
                             
                conn.commit()
                conn.close()
                self._json(200, {"status": "ok"})
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error in heartbeat: {e}", flush=True)
                self._json(500, {"error": str(e)})
        elif path == "/api/admin/block":
            if self.require_auth(): return
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                device_id = data.get('device_id')
                block = data.get('block', True)
                
                if not device_id:
                    return self._json(400, {"error": "Missing device_id"})
                    
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("UPDATE visitors SET is_blocked = ? WHERE device_id = ?", (1 if block else 0, device_id))
                conn.commit()
                conn.close()
                self._json(200, {"status": "ok"})
            except Exception as e:
                self._json(500, {"error": str(e)})

        else:
            self.send_response(404)
            self._cors()
            self.end_headers()

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def auto_update(mins=30):
    while True:
        time.sleep(mins * 60)
        print(f"\n🔄 Auto-update...", flush=True)
        try:
            scrape_all()
        except Exception as e:
            print(f"[ERROR] {e}", flush=True)
        print(f"⏰ Next in {mins} min", flush=True)


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    print(f"\n🌙 Ramadan 2026 by Karas — Port {PORT}", flush=True)
    print("=" * 50, flush=True)
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"))
    resolve_base()
    scrape_all()
    threading.Thread(target=auto_update, args=(30,), daemon=True).start()
    with ReusableTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"\n🚀 http://localhost:{PORT}\n", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Stopped.")
