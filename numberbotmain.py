import requests
import time
import json
import os
import uuid
import threading
import random
import re
import html
import zipfile
import io
import base64
import sqlite3
import pyotp
from collections import Counter 
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from datetime import datetime 
from urllib.parse import urljoin

# ==========================================
# Configuration (Token & Owner ID)
# ==========================================
TOKEN = "8894363143:AAGtlDrwTiXOEPnJWVlpcj7jjGdnjYiWkbY"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/"

OWNER_ID = 6995426618
BOT_USERNAME = "@currentboosterotp_bot"
DB_FILE = "bot_data.json"

# ==========================================
# Premium Emoji Database
# ==========================================
PEM = {
    "ok": '<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>',
    "no": '<tg-emoji emoji-id="5420130255174145507">❌</tg-emoji>',
    "warn": '<tg-emoji emoji-id="5336944168944047463">⚠️</tg-emoji>',
    "admin": '<tg-emoji emoji-id="5353032893096567467">📊</tg-emoji>',
    "user": '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>',
    "file": '<tg-emoji emoji-id="5352721946054268944">📁</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="5352597830089347330">🚀</tg-emoji>',
    "graph": '<tg-emoji emoji-id="5352877703043258544">📊</tg-emoji>',
    "money": '<tg-emoji emoji-id="5348469219761626211">💸</tg-emoji>',
    "gift": '<tg-emoji emoji-id="5420396762189831222">🎁</tg-emoji>',
    "msg": '<tg-emoji emoji-id="5337302974806922068">💬</tg-emoji>',
    "gear": '<tg-emoji emoji-id="5420155432272438703">⚙️</tg-emoji>',
    "link": '<tg-emoji emoji-id="5420517437885943844">🔗</tg-emoji>',
    "trash": '<tg-emoji emoji-id="5422557736330106570">🗑</tg-emoji>',
    "upload": '<tg-emoji emoji-id="5353001161878182134">📤</tg-emoji>',
    "world": '<tg-emoji emoji-id="5336972142066047577">🌐</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5353022963132174959">🔐</tg-emoji>',
    "phone": '<tg-emoji emoji-id="5337132498965010628">📱</tg-emoji>',
    "num": '<tg-emoji emoji-id="5352862640592949843">🔢</tg-emoji>',
    "pin": '<tg-emoji emoji-id="5352922460897452503">📍</tg-emoji>',
    "star": '<tg-emoji emoji-id="5352552689983067014">✨</tg-emoji>',
    "hi": '<tg-emoji emoji-id="5353027129250453493">👋</tg-emoji>'
}

GLOBAL_BODY_EMOJIS = {
    "➖": "5870818207383686839", "🚫": "5334807341109908955", "😒": "5334763399299506604",
    "🖥": "5334880948259427772", "🌐": "5334590977837403844", "🌟": "5337102391244263212",
    "🕓": "5336983442125001376", "⌛": "5337172996211648018", "💬": "5337302974806922068",
    "🔐": "5337255927735163754", "🍏": "5337132498965010628", "❔": "5336850036145823599",
    "⚠️": "5336944168944047463", "🔥": "5337267511261960341", "💸": "5348469219761626211",
    "🥚": "5348390922507817684", "👨‍⚖": "5334763399299506604", "🐁": "5348494358205207761",
    "🧻": "5348486915026884464", "⚗": "5346311574221000149", "🛴": "5348075478634766440",
    "📊": "5353032893096567467", "🔢": "5352862640592949843", "👤": "5352861489541714456",
    "📁": "5352721946054268944", "🚀": "5352597830089347330", "💎": "5352838545826420397",
    "📍": "5352922460897452503", "👋": "5353027129250453493", "✅": "5352694861990501856",
    "1️⃣": "5352651766288652742", "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093",
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385",
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207",
    "🔤": "5352727417842606016", "📣": "5352980533150259581", "📤": "5353001161878182134",
    "✨": "5352552689983067014", "🔹": "5352638632278660622", "🎙": "5355102594886833928",
    "💴": "5352985330628730418", "📅": "5352585194295564660", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "📱": "5337132498965010628", "🔗": "5420517437885943844",
    "❌": "5420130255174145507", "⚙️": "5420155432272438703", "🫂": "5420145051336485498",
    "➕": "5420323438508155202", "🗑": "5422557736330106570", "🎁": "5420396762189831222",
    "➤": "5420618897898381296", "🏢": "5420156334215565595", "💳": "5190899075968441286",
    "📝": "5192739271886282680", "🛡": "5190447043545438788", "🤝": "5192805934073685937",
    "💰": "5190576863226933563", "👀": "5190645917711114179", "🕹": "5193100774988617665",
    "🟢": "5192812028632274956", "🧪": "5190781475468915802", "🎨": "5190751148704833975",
    "📂": "5257969839313526622", "🌍": "5780471598922337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "5352862640592949843", "📈": "5352877703043258544",
    "🔔": "5352980533150259581", "🏦": "5348469219761626211", "🧾": "5192739271886282680",
    "👨‍⚖️": "5334763399299506604", "🔍": "5463352748751753567",
    "🔑": "5197288647275071607"
}

DEFAULT_CUSTOM_MESSAGES = {
    "start": {"text": "╔═══════════╗\n       📊 NUMBER BOT\n╚═══════════╝\n🚀 Welcome to Number & OTP Service\n━━━━━━━━━━━━\n✅ Choose an option below\nto continue using the bot.\n━━━━━━━━━━━━\n💎 Premium OTP Service", "buttons": []},
    "get_number": {"text": f"{PEM['pin']} Select a service:", "buttons": []},
    "new_number": {"text": "{flag} NEW NUMBER", "buttons": []},
    "select_country": {"text": f"📌 Select a country for {{service}}:", "buttons": []}, 
    "search_number": {"text": "╔═══════════╗\n     🔍 <b>SEARCH NUMBER</b>\n╚═══════════╝\n✅ Enter 3 to 9 digits  \nto search for a number.\n━━━━━━━━━━━━━\n📝 Example:\n➥ 880\n➥ 9227373\n━━━━━━━━━━━━━\n🔍 Fast Number Lookup System", "buttons": []},
    "traffic": {"text": f"{PEM['graph']} <b>Traffic Overview</b>\n\n{PEM['ok']} Available Numbers: {{avail}}\n{PEM['rocket']} Assigned Numbers: {{assigned}}", "buttons": []},
    "refer": {"text": f"➖➖➖➖➖➖➖\n« {PEM['gift']} REFER & EARN »\n➖➖➖➖➖➖➖\n{PEM['link']} YOUR LINK:\n<code>{{ref_link}}</code>\n➖➖➖➖➖➖➖\n{PEM['user']} TOTAL REFERS: <b>{{total_ref}}</b>\n➖➖➖➖➖➖➖\n{PEM['money']} PER REFER: <b>{{ref_reward}} TK</b>\n➖➖➖➖➖➖➖", "buttons": []},
    "withdrawal": {"text": "➖➖➖➖➖➖➖\n《 😒 WITHDRAWAL 》\n➖➖➖➖➖➖➖\n👋 Total Otp: {total_otp}\n➖➖➖➖➖➖➖\n🫂 Total Reffer :{total_ref}\n➖➖➖➖➖➖➖\n📅 BALANCE: {bal}৳\n➖➖➖➖➖➖➖\n🔐 MINIMUM: {min_w} ৳\n➖➖➖➖➖➖➖\nSELECT METHOD:", "buttons": []},
    "support": {"text": f"{PEM['msg']} Contact us for any help:", "buttons": []}
}

# ==========================================
# Local Persistent Database (No Firebase Required)
# ==========================================
# This replaces the old Firebase/local database dependency with a small
# JSON-backed local database. It works on Railway and other hosts
# without Firebase credentials or the firebase-admin package.

LOCAL_DB_FILE = "bot_database.db"
LEGACY_LOCAL_JSON = "local_db.json"

class Increment:
    def __init__(self, amount): self.amount = amount

SERVER_TIMESTAMP = object()
USER_COLUMNS = {"user_id","username","profile_name","balance","total_otps","total_refers","total_earnings","ref_income","ref_otp_commissions","total_withdrawals","total_deposits","total_numbers","activity_count","banned","verified","referred_by","ref_paid","created_at","updated_at","last_activity_at","last_activity_type"}

class LocalDocumentSnapshot:
    def __init__(self, doc_id, data):
        self.id=str(doc_id); self._data=dict(data) if isinstance(data,dict) else {}; self.exists=bool(data is not None)
    def to_dict(self): return dict(self._data)

class LocalDocumentReference:
    def __init__(self, store, collection_name, doc_id): self.store=store; self.collection_name=str(collection_name); self.doc_id=str(doc_id)
    def get(self): return self.store._get_doc(self.collection_name,self.doc_id)
    def set(self, values, merge=False): self.store._set_doc(self.collection_name,self.doc_id,values,merge); return self
    def update(self, values):
        if not self.get().exists: raise KeyError(self.doc_id)
        self.store._set_doc(self.collection_name,self.doc_id,values,True); return self

class LocalQuery:
    def __init__(self,store,collection_name,selected_fields=None,order_field=None,descending=False,limit_count=None): self.store=store; self.collection_name=str(collection_name); self.selected_fields=selected_fields; self.order_field=order_field; self.descending=descending; self.limit_count=limit_count
    def select(self,fields): return LocalQuery(self.store,self.collection_name,fields,self.order_field,self.descending,self.limit_count)
    def order_by(self,field,direction="ASCENDING"): return LocalQuery(self.store,self.collection_name,self.selected_fields,field,str(direction).upper()=="DESCENDING",self.limit_count)
    def limit(self,count): return LocalQuery(self.store,self.collection_name,self.selected_fields,self.order_field,self.descending,int(count))
    def stream(self): return iter(self.store._query_docs(self.collection_name,self.selected_fields,self.order_field,self.descending,self.limit_count))

class LocalCollection:
    def __init__(self,store,collection_name): self.store=store; self.collection_name=str(collection_name)
    def document(self,doc_id): return LocalDocumentReference(self.store,self.collection_name,doc_id)
    def select(self,fields): return LocalQuery(self.store,self.collection_name,selected_fields=fields)
    def order_by(self,field,direction="ASCENDING"): return LocalQuery(self.store,self.collection_name,order_field=field,descending=str(direction).upper()=="DESCENDING")

class LocalStore:
    def __init__(self,filename=LOCAL_DB_FILE):
        self.filename=filename; self.lock=threading.RLock(); self.conn=sqlite3.connect(filename,check_same_thread=False,timeout=30); self.conn.row_factory=sqlite3.Row; self._init_schema(); self._migrate_legacy_json()
    def _init_schema(self):
        with self.lock:
            self.conn.executescript("""
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=NORMAL;
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, username TEXT DEFAULT '', profile_name TEXT DEFAULT 'User',
                balance REAL DEFAULT 0, total_otps INTEGER DEFAULT 0, total_refers INTEGER DEFAULT 0,
                total_earnings REAL DEFAULT 0, ref_income REAL DEFAULT 0, ref_otp_commissions INTEGER DEFAULT 0,
                total_withdrawals REAL DEFAULT 0, total_deposits REAL DEFAULT 0, total_numbers INTEGER DEFAULT 0,
                activity_count INTEGER DEFAULT 0, banned INTEGER DEFAULT 0, verified INTEGER DEFAULT 0,
                referred_by INTEGER, ref_paid INTEGER DEFAULT 0, created_at REAL, updated_at REAL,
                last_activity_at REAL, last_activity_type TEXT DEFAULT '', data_json TEXT DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS activity_logs (
                id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, activity_type TEXT NOT NULL,
                payload_json TEXT DEFAULT '{}', created_at REAL, balance_before REAL, balance_after REAL
            );
            CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_logs(user_id,created_at);
            CREATE TABLE IF NOT EXISTS collection_docs (
                collection_name TEXT NOT NULL, doc_id TEXT NOT NULL, data_json TEXT NOT NULL,
                updated_at REAL, PRIMARY KEY(collection_name,doc_id)
            );
            """); self.conn.commit()
    def _resolve_values(self,old,values):
        result=dict(old or {})
        for key,value in (values or {}).items():
            if isinstance(value,Increment):
                try:
                    n=float(result.get(key,0) or 0)+float(value.amount); result[key]=int(n) if n.is_integer() else n
                except: result[key]=value.amount
            elif value is SERVER_TIMESTAMP: result[key]=time.time()
            else: result[key]=value
        return result
    def _normalize_user(self,d,doc_id=None):
        d=dict(d or {})
        if doc_id is not None: d["user_id"]=int(d.get("user_id") or doc_id)
        defaults={"user_id":int(d.get("user_id") or 0),"username":"","profile_name":"User","balance":0.0,"total_otps":0,"total_refers":0,"total_earnings":0.0,"ref_income":0.0,"ref_otp_commissions":0,"total_withdrawals":0.0,"total_deposits":0.0,"total_numbers":0,"activity_count":0,"banned":False,"verified":False,"referred_by":None,"ref_paid":False,"created_at":time.time(),"updated_at":time.time(),"last_activity_at":time.time(),"last_activity_type":""}
        for k,v in defaults.items(): d.setdefault(k,v)
        return d
    def _user_from_row(self,row):
        if not row: return None
        try: d=json.loads(row["data_json"] or "{}")
        except: d={}
        for col in USER_COLUMNS:
            if col in row.keys(): d[col]=row[col]
        for col in ("banned","verified","ref_paid"):
            d[col]=bool(d.get(col))
        d["user_id"]=int(row["user_id"]); return d
    def _get_doc(self,collection,doc_id):
        with self.lock:
            if collection=="users":
                row=self.conn.execute("SELECT * FROM users WHERE user_id=?",(int(doc_id),)).fetchone(); return LocalDocumentSnapshot(doc_id,self._user_from_row(row)) if row else LocalDocumentSnapshot(doc_id,None)
            if collection=="activity_logs":
                row=self.conn.execute("SELECT * FROM activity_logs WHERE id=?",(str(doc_id),)).fetchone()
                if not row: return LocalDocumentSnapshot(doc_id,None)
                d={"user_id":row["user_id"],"activity_type":row["activity_type"],"created_at":row["created_at"]}
                try:d.update(json.loads(row["payload_json"] or "{}"))
                except:pass
                if row["balance_before"] is not None:d["balance_before"]=row["balance_before"]
                if row["balance_after"] is not None:d["balance_after"]=row["balance_after"]
                return LocalDocumentSnapshot(doc_id,d)
            row=self.conn.execute("SELECT data_json FROM collection_docs WHERE collection_name=? AND doc_id=?",(collection,str(doc_id))).fetchone()
            if not row:return LocalDocumentSnapshot(doc_id,None)
            try:d=json.loads(row[0])
            except:d={}
            return LocalDocumentSnapshot(doc_id,d)
    def _set_doc(self,collection,doc_id,values,merge=False):
        with self.lock:
            old=self._get_doc(collection,doc_id); current=old.to_dict() if old.exists else {}; data=self._resolve_values(current if merge else {},values); now=time.time()
            if collection=="users":
                data=self._normalize_user(data,doc_id); known={k:data.get(k) for k in USER_COLUMNS if k!="user_id"}; extra={k:v for k,v in data.items() if k not in USER_COLUMNS}
                self.conn.execute("INSERT OR IGNORE INTO users(user_id,data_json) VALUES(?,?)",(int(data["user_id"]),"{}"))
                cols=list(known); assignments=", ".join(f"{c}=?" for c in cols)+", data_json=?"
                self.conn.execute(f"UPDATE users SET {assignments} WHERE user_id=?",[known[c] for c in cols]+[json.dumps(extra,ensure_ascii=False),int(data["user_id"])])
            elif collection=="activity_logs":
                payload=dict(data); uid=int(payload.pop("user_id",0) or 0); atype=str(payload.pop("activity_type","activity")); created=float(payload.pop("created_at",now) or now); bb=payload.pop("balance_before",None); ba=payload.pop("balance_after",None)
                self.conn.execute("INSERT OR REPLACE INTO activity_logs(id,user_id,activity_type,payload_json,created_at,balance_before,balance_after) VALUES(?,?,?,?,?,?,?)",(str(doc_id),uid,atype,json.dumps(payload,ensure_ascii=False),created,bb,ba))
            else:
                self.conn.execute("INSERT OR REPLACE INTO collection_docs(collection_name,doc_id,data_json,updated_at) VALUES(?,?,?,?)",(collection,str(doc_id),json.dumps(data,ensure_ascii=False),now))
            self.conn.commit()
    def _query_docs(self,collection,selected_fields=None,order_field=None,descending=False,limit_count=None):
        with self.lock:
            if collection=="users":
                rows=self.conn.execute("SELECT * FROM users").fetchall(); items=[(str(r["user_id"]),self._user_from_row(r)) for r in rows]
            elif collection=="activity_logs":
                rows=self.conn.execute("SELECT * FROM activity_logs ORDER BY created_at DESC").fetchall(); items=[]
                for r in rows:
                    d={"user_id":r["user_id"],"activity_type":r["activity_type"],"created_at":r["created_at"]}
                    try:d.update(json.loads(r["payload_json"] or "{}"))
                    except:pass
                    items.append((str(r["id"]),d))
            else:
                rows=self.conn.execute("SELECT doc_id,data_json FROM collection_docs WHERE collection_name=?",(collection,)).fetchall(); items=[]
                for r in rows:
                    try:d=json.loads(r["data_json"] or "{}")
                    except:d={}
                    items.append((str(r["doc_id"]),d))
            if order_field:
                try:items.sort(key=lambda x:(x[1].get(order_field) is None,x[1].get(order_field) if x[1].get(order_field) is not None else ""),reverse=descending)
                except TypeError:items.sort(key=lambda x:str(x[1].get(order_field,"")),reverse=descending)
            if limit_count is not None:items=items[:limit_count]
            return [LocalDocumentSnapshot(i,{k:d[k] for k in selected_fields if k in d} if selected_fields else d) for i,d in items]
    def collection(self,collection_name): return LocalCollection(self,collection_name)
    def close(self): self.conn.commit(); self.conn.close()
    def _migrate_legacy_json(self):
        try:
            if self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]>0 or not os.path.exists(LEGACY_LOCAL_JSON):return
            with open(LEGACY_LOCAL_JSON,"r",encoding="utf-8") as f: legacy=json.load(f)
            for cname,docs in (legacy.get("collections",{}) if isinstance(legacy,dict) else {}).items():
                if isinstance(docs,dict):
                    for did,data in docs.items(): self._set_doc(cname,did,data,False)
            print("✅ Migrated local_db.json → bot_database.db")
        except Exception as exc: print(f"[SQLITE MIGRATION] {exc}")

db=LocalStore()
print("✅ SQLite database enabled: bot_database.db")

bot_settings = {
    "admins": [OWNER_ID],
    "special_users": [],
    "panels": [], 
    "fw_groups": [], 
    "otp_link": "https://t.me/your_otp_group",
    "withdraw_on": True,
    "min_withdraw": 30.0,
    "otp_reward": 0.1,
    "panel_otp_rewards": {},
    "refer_otp_commission": 0.2,
    "refer_otp_commission_on": True,
    "cooldown": 10,
    "num_req": 3,
    "num_share": 1, 
    "support_link": "https://t.me/your_support",
    "support_button_name": "Support",
    "w_methods": ["bKash", "Nagad"],
    "w_group": "",
    "traffic_window_minutes": 30,
    "console_traffic_mode": "on",
    "console_traffic": True, 
    "console_otp": False, 
    
    "fj_on": False,
    "fj_channels": [], 
    "stex_keys": [], 
    "voltx_keys": [],
    "zenex_keys": [],
    "fastx_keys": [],
    "search_countries": [],
    "stex_services": {},
    "voltx_services": {},
    "zenex_services": {},
    "premium_flags": {
        "1": {"char": "🇺🇸", "iso": "US", "name": "United States", "id": "5913463998522592692"},
        "880": {"char": "🇧🇩", "iso": "BD", "name": "Bangladesh", "id": "5911365056594973179"},
        "91": {"char": "🇮🇳", "iso": "IN", "name": "India", "id": "5913754823643107921"},
        "92": {"char": "🇵🇰", "iso": "PK", "name": "Pakistan", "id": "5913705895375672082"},
        "44": {"char": "🇬🇧", "iso": "GB", "name": "United Kingdom", "id": "5913443365499703513"}
    },
    "premium_apps": {
        "FACEBOOK": {"char": "🚫", "id": "5334807341109908955", "name": "Facebook"},
        "WHATSAPP": {"char": "🚫", "id": "5334759662677957452", "name": "WhatsApp"}
    },
    "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy(),
    "reply_keyboard_emojis": {
        "Get Number": "5337132498965010628",
        "Live Traffic": "5203993413346680064",
        "Refer & Earn": "5420396762189831222",
        "Traffic": "5203993413346680064",
        "Refer": "5420396762189831222",
        "My profile": "5352861489541714456",
        "Support": "5420145051336485498",
        "Admin panel": "5420155432272438703"
    }
}

FS_KEYS = [
    "admins", "special_users", "panels", "fw_groups", "otp_link", "withdraw_on", 
    "min_withdraw", "otp_reward", "refer_otp_commission", "refer_otp_commission_on", "cooldown", 
    "num_req", "num_share", "support_link", "support_button_name", "w_methods", "stex_keys", "voltx_keys", "search_countries", "stex_services", "voltx_services",
    "fj_on", "fj_channels", "console_otp", "voltx_auto", "stex_auto", "zenex_auto", "zenex_keys", "zenex_services", "zenex_search_countries", "fastx_keys", "fastx_enabled", "fastx_auto", "fastx_services", "fastx_search_countries"
]

number_batches = {}
used_numbers_list = []
stex_assigned_numbers = {} 
voltx_assigned_numbers = {}
zenex_assigned_numbers = {}
STEX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api"
VOLTX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
ZENEX_BASE_URL = "https://api.zenexnetwork.com"
# Fast X backend extracted from the uploaded working Fast X bot.
# The backend uses the same public endpoints and payloads as that bot.
FASTX_BASE_URL = "https://2eee7.com/@Access/@Bot/2eee7/@public/api"
FASTX_ENABLED_DEFAULT = True
fastx_assigned_numbers = {}
# Persist the exact Fast X range used for each assigned number so auto service/range
# discovery can mirror the StexSMS/Voltx behaviour.
fastx_assigned_ranges = {}
processed_fastx_otps = set()
# Fast X manual deletions are remembered so liveaccess auto-sync does not immediately
# recreate a service/country/range that an admin intentionally removed.
fastx_hidden_services = set()
fastx_hidden_countries = set()
fastx_hidden_ranges = set()
total_uploaded_stats = 0
total_assigned_stats = 0
processed_otps = set() 
# KSI has its own processed ledger so older generic OTP history can never
# suppress a newly delivered KSI message.
processed_ksi_messages = set()
recent_traffic = []
user_banned_cache = {}

# Active HTTP sessions for Auto Captcha Panels
panel_sessions = {}

# 🌟 sAjaxSource (AJAX/DataTable) এবং Fallback HTML Parser Helper Function
def fetch_cpt_panel_cdrs(p, session, check_url):
    res = session.get(check_url, timeout=15)
    html_text = res.text
    
    # সেশন শেষ হয়েছে বা লগইন পেজে রিডাইরেক্ট করেছে কি না তা চেক করা
    if "login" in html_text.lower() or "signin" in html_text.lower() or any(x in html_text for x in ["Sign in to your account", "Please sign in", "Welcome back!"]):
        raise Exception("Session expired")
        
    soup = BeautifulSoup(html_text, 'html.parser')
    s_ajax_source = ""
    for script in soup.find_all("script"):
        script_text = script.string or ""
        match = re.search(r'sAjaxSource":\s*"([^"]+)"', script_text)
        if match:
            s_ajax_source = match.group(1)
            break
            
    results = []
    
    n_col_name = p.get("num_col_name", "number").lower()
    m_col_name = p.get("msg_col_name", "message").lower()
    n_idx = int(p.get("num_col_idx", 1)) - 1 if p.get("num_col_idx") else 1
    m_idx = int(p.get("msg_col_idx", 2)) - 1 if p.get("msg_col_idx") else 2

    # ৫.১ যদি sAjaxSource AJAX লিংক পাওয়া যায়
    if s_ajax_source:
        baseUrl = p.get("login_url", "").split("/client")[0].split("/login")[0].strip()
        if not baseUrl.startswith("http"):
            baseUrl = "http://" + baseUrl
            
        full_ajax_url = ""
        if s_ajax_source.startswith("http"):
            full_ajax_url = s_ajax_source
        elif s_ajax_source.startswith("/"):
            full_ajax_url = f"{baseUrl}{s_ajax_source}"
        else:
            last_slash_idx = check_url.rfind("/")
            current_dir = check_url[:last_slash_idx]
            full_ajax_url = f"{current_dir}/{s_ajax_source}"

        if "iDisplayLength" not in full_ajax_url:
            # 250 এর জায়গায় 10000 করে দেওয়া হলো যাতে সব মেসেজ ফেচ করতে পারে
            query_params = "sEcho=1&iColumns=7&iDisplayStart=0&iDisplayLength=10000&sSearch=&iSortingCols=1&iSortCol_0=0&sSortDir_0=desc"
            divider = "&" if "?" in full_ajax_url else "?"
            full_ajax_url += f"{divider}{query_params}"

        ajax_headers = {
            "Referer": check_url,
            "X-Requested-With": "XMLHttpRequest"
        }
        
        ajax_res = session.get(full_ajax_url, headers=ajax_headers, timeout=15)
        data_dict = ajax_res.json()
        rows = data_dict.get("aaData", [])
        for row_val in rows:
            if not isinstance(row_val, list):
                continue
                
            if len(row_val) < max(n_idx, m_idx) + 1:
                continue
                
            num_val = row_val[n_idx] if (0 <= n_idx < len(row_val)) else row_val[2]
            msg_val = row_val[m_idx] if (0 <= m_idx < len(row_val)) else row_val[4]
            
            clean_num = re.sub(r'\D', '', str(num_val))
            if clean_num and 5 <= len(clean_num) <= 18:
                otp = extract_otp_code(msg_val)
                if otp and len(msg_val) > 4:
                    results.append({"number": clean_num, "message": msg_val, "otp": otp})
                    
    else:
        # ৫.২ ডাইরেক্ট HTML টেবিল থেকে রিড করার ব্যাকআপ লজিক
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if not rows: continue
            
            final_n_idx = n_idx
            final_m_idx = m_idx
            
            header_cells = rows[0].find_all(['th', 'td'])
            for i, cell in enumerate(header_cells):
                c_text = cell.get_text(strip=True).lower()
                if n_col_name in c_text: final_n_idx = i
                if m_col_name in c_text: final_m_idx = i

            for row in rows:
                cols = row.find_all(['td', 'th'])
                if all(c.name == 'th' for c in cols): continue
                
                if len(cols) > max(final_n_idx, final_m_idx):
                    num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                    msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                    
                    clean_num = re.sub(r'\D', '', num_text)
                    if clean_num and 5 <= len(clean_num) <= 18:
                        otp = extract_otp_code(msg_text)
                        if otp and len(msg_text) > 4:
                            results.append({"number": clean_num, "message": msg_text, "otp": otp})
                            
    return results, html_text

# Track active number sessions to expire them automatically
user_active_sessions = {}

# Persistent KSI IPRN number -> Telegram user mapping.  This is the
# authoritative fallback after the stock entry has been removed.
ksi_assigned_numbers = {}

assigned_number_rates = {}

def is_special_user(user_id):
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        uid = user_id
    return uid in set(bot_settings.get("special_users", [])) or str(uid) in {str(x) for x in bot_settings.get("special_users", [])}

def _panel_reward_key(panel_name):
    """Normalize provider names for panel-specific OTP reward settings."""
    name = str(panel_name or "").strip().lower()
    if "stex" in name:
        return "stexsms"
    if "voltx" in name:
        return "voltx"
    if "zenex" in name:
        return "zenex"
    if "fast" in name and "x" in name:
        return "fastx"
    return name.replace(" ", "_") if name else ""

def get_otp_reward_for_user(number, user_id, panel_name=None):
    """Get OTP reward: panel-specific User/Special rate first, then old fallbacks."""
    if panel_name:
        key = _panel_reward_key(panel_name)
        panel_rates = bot_settings.get("panel_otp_rewards", {}).get(key)
        if isinstance(panel_rates, dict):
            rate_key = "special" if is_special_user(user_id) else "user"
            try:
                return float(panel_rates.get(rate_key, bot_settings.get("otp_reward", 0.0)))
            except (TypeError, ValueError):
                pass

    info = assigned_number_rates.get(number)
    if info is None:
        return float(bot_settings.get("otp_reward", 0.0))
    if isinstance(info, dict):
        key = "special" if is_special_user(user_id) else "normal"
        try:
            return float(info.get(key, info.get("normal", bot_settings.get("otp_reward", 0.0))))
        except (TypeError, ValueError):
            return 0.0
    try:
        return float(info)
    except (TypeError, ValueError):
        return 0.0

def special_user_management_text():
    users = bot_settings.get("special_users", [])
    lines = "\n".join(f"• <code>{html.escape(str(uid))}</code>" for uid in users) if users else "<i>No special users set.</i>"
    return render_body_text(
        f"<b>SPECIAL USER MANAGEMENT</b>\n\n"
        f"<b>Special User IDs:</b>\n{lines}\n\n"
        f"Special users will receive the Special User OTP earning rate configured during number upload."
    )

KSI_IPRN_API_KEY = 'sk_live_3Z8HuV0lFxEtIsPDRqc0YtKP3WSn3sCYYQnXDkY8'

def ksi_iprn_messages_url(base_url=None):
    """Return the documented KSI IPRN Message History endpoint.

    KSI's API documentation exposes Message History at /messages, with
    optional type, page and per_page query parameters.
    """
    base = (base_url or "https://www.ksiiprn.com/api/v1/iprn/messages").strip()
    # If an older saved configuration still points to /numbers, migrate it.
    if base.rstrip("/").lower().endswith("/numbers"):
        base = base.rstrip("/")[:-len("/numbers")] + "/messages"
    sep = "&" if "?" in base else "?"
    if "type=" not in base:
        base += f"{sep}type=all"
        sep = "&"
    if "page=" not in base:
        base += f"{sep}page=1"
        sep = "&"
    if "per_page=" not in base:
        base += f"{sep}per_page=200"
    return base


def ensure_ksi_iprn_panel():
    """Ensure the KSI IPRN provider is available in Panel Management."""
    try:
        panels = bot_settings.setdefault("panels", [])
        for p in panels:
            if str(p.get("name", "")).strip().lower() == "ksi iprn":
                p.setdefault("type", "API Panel")
                p.setdefault("status", "ON")
                p.setdefault("api_url", "https://www.ksiiprn.com/api/v1/iprn/messages")
                if str(p.get("api_url", "")).rstrip("/").lower().endswith("/numbers"):
                    p["api_url"] = "https://www.ksiiprn.com/api/v1/iprn/messages"
                if not p.get("token"):
                    p["token"] = KSI_IPRN_API_KEY
                p.setdefault("full_api_url", "")
                p.setdefault("records", 0)
                p["auth_mode"] = "bearer"
                return
        panels.append({
            "name": "KSI IPRN",
            "type": "API Panel",
            "status": "ON",
            "api_url": "https://www.ksiiprn.com/api/v1/iprn/messages",
            "token": KSI_IPRN_API_KEY,
            "full_api_url": "",
            "records": 0,
            "auth_mode": "bearer"
        })
        save_db()
    except Exception:
        pass

def load_db():
    global bot_settings, number_batches, used_numbers_list, total_uploaded_stats, total_assigned_stats, recent_traffic, stex_assigned_numbers, voltx_assigned_numbers, zenex_assigned_numbers, fastx_assigned_numbers, fastx_assigned_ranges, processed_otps, processed_fastx_otps, processed_ksi_messages, assigned_number_rates, ksi_assigned_numbers, fastx_hidden_services, fastx_hidden_countries, fastx_hidden_ranges
    
    loaded_from_local = False
    
    # ১. প্রথমে Local DB লোড করবে (এটি সবচেয়ে আপডেট থাকে, তাই Key হারাবে না)
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                saved_settings = data.get("bot_settings", {})
                for key, val in saved_settings.items():
                    if key == "custom_messages":
                        for m_key, m_val in val.items():
                            bot_settings["custom_messages"][m_key] = m_val
                    else:
                        bot_settings[key] = val
                        
                for m_key, m_val in DEFAULT_CUSTOM_MESSAGES.items():
                    if m_key not in bot_settings["custom_messages"]:
                        bot_settings["custom_messages"][m_key] = m_val
                        
                number_batches = data.get("number_batches", {})
                used_numbers_list = data.get("used_numbers_list", [])
                total_uploaded_stats = data.get("total_uploaded_stats", 0)
                total_assigned_stats = data.get("total_assigned_stats", 0)
                recent_traffic = data.get("recent_traffic", [])
                stex_assigned_numbers = data.get("stex_assigned_numbers", {})
                voltx_assigned_numbers = data.get("voltx_assigned_numbers", {})
                zenex_assigned_numbers = data.get("zenex_assigned_numbers", {})
                fastx_assigned_numbers = data.get("fastx_assigned_numbers", {})
                fastx_assigned_ranges = data.get("fastx_assigned_ranges", {})
                processed_fastx_otps = set(data.get("processed_fastx_otps", []))
                fastx_hidden_services = set(data.get("fastx_hidden_services", []))
                fastx_hidden_countries = set(data.get("fastx_hidden_countries", []))
                fastx_hidden_ranges = set(data.get("fastx_hidden_ranges", []))
                processed_otps = set(data.get("processed_otps", []))
                processed_ksi_messages = set(data.get("processed_ksi_messages", []))
                assigned_number_rates = data.get("assigned_number_rates", {})
                ksi_assigned_numbers = data.get("ksi_assigned_numbers", {})
                loaded_from_local = True
            print("✅ Local Stock/UI DB Loaded Successfully!")
        except Exception as e:
            print(f"❌ Error loading local DB: {e}")

    # All persistent configuration is stored locally; no external database is required.

def save_local_db():
    local_data = {
        "bot_settings": bot_settings,
        "number_batches": number_batches,
        "used_numbers_list": used_numbers_list,
        "total_uploaded_stats": total_uploaded_stats,
        "total_assigned_stats": total_assigned_stats,
        "recent_traffic": recent_traffic,
        "stex_assigned_numbers": stex_assigned_numbers,
        "voltx_assigned_numbers": voltx_assigned_numbers,
        "zenex_assigned_numbers": zenex_assigned_numbers,
        "fastx_assigned_numbers": fastx_assigned_numbers,
        "fastx_assigned_ranges": fastx_assigned_ranges,
        "processed_fastx_otps": list(processed_fastx_otps),
        "fastx_hidden_services": list(fastx_hidden_services),
        "fastx_hidden_countries": list(fastx_hidden_countries),
        "fastx_hidden_ranges": list(fastx_hidden_ranges),
        "processed_otps": list(processed_otps),
        "processed_ksi_messages": list(processed_ksi_messages),
        "assigned_number_rates": assigned_number_rates,
        "ksi_assigned_numbers": ksi_assigned_numbers,
        "pending_withdrawals": globals().get("pending_withdrawals", {})
    }
    try:
        with open(DB_FILE, "w", encoding='utf-8') as f:
            json.dump(local_data, f, indent=4)
    except Exception as e:
        pass

def save_db():
    # bot_data.json stores stock/settings state; user/withdrawal data is
    # persisted by LocalStore in local_db.json.
    save_local_db()


load_db()
ensure_ksi_iprn_panel()

user_states = {}
temp_data = {}
user_cooldowns = {}
pending_withdrawals = {}

def restore_pending_withdrawals():
    global pending_withdrawals
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            saved = data.get("pending_withdrawals", {})
            if isinstance(saved, dict):
                pending_withdrawals.clear()
                pending_withdrawals.update(saved)
    except Exception as e:
        print(f"Pending withdrawal restore warning: {e}")

restore_pending_withdrawals()

def migrate_user_records():
    """Backfill the complete user schema in older local_db.json records."""
    if not db:
        return
    now = time.time()
    defaults = {
        "balance": 0.0, "total_refers": 0, "total_otps": 0, "total_earnings": 0.0,
        "ref_income": 0.0, "ref_otp_commissions": 0, "total_withdrawals": 0.0,
        "total_deposits": 0.0, "total_numbers": 0, "activity_count": 0,
        "banned": False, "verified": False, "profile_name": "User", "username": "",
        "referred_by": None, "ref_paid": False, "created_at": now, "updated_at": now,
        "last_activity_at": now, "last_activity_type": "migration"
    }
    try:
        for doc in db.collection("users").stream():
            current = doc.to_dict() or {}
            missing = {k: v for k, v in defaults.items() if k not in current}
            if missing:
                db.collection("users").document(str(doc.id)).set(missing, merge=True)
    except Exception as exc:
        print(f"[USER MIGRATION] {exc}")

migrate_user_records()

# ==========================================
# Universal Number File Parser
# ==========================================
def _normalize_uploaded_number(value):
    if value is None: return None
    digits = re.sub(r"\D", "", str(value).strip())
    if not (5 <= len(digits) <= 18): return None
    return "+" + digits

def _extract_numbers_from_text(text):
    if not text: return []
    text = str(text).replace("\x00", " ")
    found = []
    pattern = re.compile(r"(?<!\d)(?:\+\d[\d\s().-]{4,24}\d|\d[\d\s().-]{4,24}\d)(?!\d)")
    for m in pattern.finditer(text):
        n = _normalize_uploaded_number(m.group(0))
        if n: found.append(n)
    for m in re.finditer(r"(?<!\d)\d{5,18}(?!\d)", text):
        n = _normalize_uploaded_number(m.group(0))
        if n: found.append(n)
    return found

def _xlsx_text_values(raw):
    import xml.etree.ElementTree as ET
    values=[]
    with zipfile.ZipFile(io.BytesIO(raw),'r') as z:
        names=z.namelist(); shared=[]
        if 'xl/sharedStrings.xml' in names:
            root=ET.fromstring(z.read('xl/sharedStrings.xml')); ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for si in root.findall('.//m:si',ns): shared.append(''.join(x.text or '' for x in si.findall('.//m:t',ns)))
        ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for name in names:
            if not (name.startswith('xl/worksheets/') and name.endswith('.xml')): continue
            root=ET.fromstring(z.read(name))
            for cell in root.findall('.//m:c',ns):
                v=cell.find('m:v',ns)
                if v is None or v.text is None: continue
                val=v.text
                if cell.get('t')=='s':
                    try: val=shared[int(val)]
                    except: pass
                values.append(val)
            for inline in root.findall('.//m:is',ns):
                val=''.join(x.text or '' for x in inline.findall('.//m:t',ns))
                if val: values.append(val)
    return values

def _docx_text_values(raw):
    import xml.etree.ElementTree as ET
    values=[]
    with zipfile.ZipFile(io.BytesIO(raw),'r') as z:
        for name in z.namelist():
            if name.startswith('word/') and name.endswith('.xml'):
                try: root=ET.fromstring(z.read(name))
                except: continue
                vals=[e.text for e in root.iter() if e.tag.endswith('}t') and e.text]
                if vals: values.append(' '.join(vals))
    return values

def extract_numbers_from_uploaded_file(filename, raw):
    """Accept any Telegram document; parse common formats and scan unknown ones."""
    ext=os.path.splitext(str(filename).lower())[1]; texts=[]
    if ext in {'.xlsx','.xlsm','.xltx','.xltm'}:
        try: texts.extend(_xlsx_text_values(raw))
        except Exception as e: print(f'XLSX parser warning: {e}')
    elif ext=='.docx':
        try: texts.extend(_docx_text_values(raw))
        except Exception as e: print(f'DOCX parser warning: {e}')
    elif ext=='.pdf':
        for mod in ('pypdf','PyPDF2'):
            try:
                m=__import__(mod); reader=m.PdfReader(io.BytesIO(raw))
                for page in reader.pages: texts.append(page.extract_text() or '')
                break
            except: pass
    if not texts or ext not in {'.xlsx','.xlsm','.xltx','.xltm','.docx','.pdf'}:
        for enc in ('utf-8-sig','utf-8','utf-16','latin-1'):
            try: texts.append(raw.decode(enc)); break
            except: pass
    if not texts: texts.append(''.join(chr(b) if 32<=b<127 else ' ' for b in raw))
    nums=[]
    for value in texts: nums.extend(_extract_numbers_from_text(value))
    return list(dict.fromkeys(nums))

# ==========================================
# Telegram API & Helpers
# ==========================================
tg_session = requests.Session() # 🌟 Keep-Alive Connection (Makes bot 10x faster)

def api_call(method, payload=None):
    url = f"{BASE_URL}/{method}"
    try:
        # 🌟 Added timeout to prevent hanging!
        res = tg_session.post(url, json=payload, timeout=15)
        return res.json()
    except Exception as e:
        return {}

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendMessage", payload)

def send_photo(chat_id, photo_url_or_file_id, caption="", reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "photo": photo_url_or_file_id, "caption": caption, "parse_mode": parse_mode}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendPhoto", payload)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("editMessageText", payload)

def delete_message(chat_id, message_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

def answer_callback(callback_id, text="", show_alert=False):
    api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text, "show_alert": show_alert})

def send_document(chat_id, filename, text_content):
    url = f"{BASE_URL}/sendDocument"
    files = {'document': (filename, text_content)}
    data = {'chat_id': chat_id}
    try: requests.post(url, data=data, files=files)
    except: pass

# 🌟 Local User List
all_known_users = set()

def sync_users_list():
    global all_known_users
    try:
        if os.path.exists("users_list.json"):
            with open("users_list.json", "r") as f:
                all_known_users = set(json.load(f))
        if not all_known_users and db:
            for doc in db.collection('users').select([]).stream():
                all_known_users.add(doc.id)
            with open("users_list.json", "w") as f:
                json.dump(list(all_known_users), f)
    except: pass

threading.Thread(target=sync_users_list, daemon=True).start()

def _save_users_list():
    try:
        with open("users_list.json", "w") as f:
            json.dump(list(all_known_users), f)
    except: pass

def register_user_local(uid):
    uid_str = str(uid)
    if uid_str not in all_known_users:
        all_known_users.add(uid_str)
        # 🌟 Non-blocking background save (Prevents lag)
        threading.Thread(target=_save_users_list, daemon=True).start()

def broadcast_copymessage(from_chat_id, msg_id, status_msg_id=None):
    success = 0
    failed = 0
    users = list(all_known_users)
    
    # 🌟 Dedicated Connection Pool for Broadcast (Fixes Port Exhaustion & Network Lag)
    b_session = requests.Session()
    url = f"{BASE_URL}/copyMessage"
    
    for user_id in users:
        payload = {"chat_id": user_id, "from_chat_id": from_chat_id, "message_id": msg_id}
        try:
            res = b_session.post(url, json=payload, timeout=5).json()
            if res.get("ok"): success += 1
            else: failed += 1
        except:
            failed += 1
        time.sleep(0.035) # Safe speed (28 msgs/sec) to prevent Telegram Ban

    if status_msg_id:
        try:
            delete_message(from_chat_id, status_msg_id)
        except Exception:
            pass
        

def render_body_text(text):
    if not text: return str(text)
    parts = re.split(r'(<tg-emoji.*?</tg-emoji>)', str(text))
    for i in range(len(parts)):
        if not parts[i].startswith('<tg-emoji'):
            for normal_emj, prem_id in GLOBAL_BODY_EMOJIS.items():
                if normal_emj in parts[i]:
                    parts[i] = parts[i].replace(normal_emj, f'<tg-emoji emoji-id="{prem_id}">{normal_emj}</tg-emoji>')
    return "".join(parts)

def extract_premium_html(msg):
    text = msg.get("text", msg.get("caption", ""))
    entities = msg.get("entities", msg.get("caption_entities", []))
    if not entities: return text
    try:
        b_text = text.encode('utf-16-le')
        c_entities = [e for e in entities if e.get("type") == "custom_emoji"]
        c_entities.sort(key=lambda x: x["offset"], reverse=True)
        for ent in c_entities:
            offset = ent["offset"] * 2
            length = ent["length"] * 2
            eid = ent["custom_emoji_id"]
            emoji_char = b_text[offset:offset+length].decode('utf-16-le')
            html_tag = f'<tg-emoji emoji-id="{eid}">{emoji_char}</tg-emoji>'
            replacement = html_tag.encode('utf-16-le')
            b_text = b_text[:offset] + replacement + b_text[offset+length:]
        return b_text.decode('utf-16-le')
    except Exception as e:
        return text 

def get_flag_info_from_num(num):
    clean = num.replace("+", "").replace(" ", "")
    sorted_codes = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code):
            data = bot_settings["premium_flags"][code]
            return data["char"], data.get("iso", "XX"), data.get("id")
    return "🌍", "XX", None

def get_flag_and_code(num):
    char, iso, _ = get_flag_info_from_num(num)
    return char, iso

def get_flag_info_html(num_or_iso, return_full_name=False):
    if len(num_or_iso) == 2:
        for code, data in bot_settings.get("premium_flags", {}).items():
            if data.get("iso") == num_or_iso:
                eid = data.get("id")
                char = data.get("char")
                name = data.get("name", num_or_iso)
                if return_full_name: return name
                if eid: return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                return char
        if return_full_name: return num_or_iso
        return "🌍"
        
    char, _, eid = get_flag_info_from_num(num_or_iso)
    if return_full_name:
        for code, data in bot_settings.get("premium_flags", {}).items():
            clean = num_or_iso.replace("+", "").replace(" ", "")
            if clean.startswith(code): return data.get("name", num_or_iso)
        return num_or_iso
        
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
    return char

def mask_number(num):
    clean = num.replace("+", "").replace(" ", "")
    mask = bot_settings.get("mask_emoji", {}) if "bot_settings" in globals() else {}
    mask_id = str(mask.get("id", "") or "")
    mask_char = str(mask.get("char", "") or "")
    if mask_id and mask_char:
        mask = f'<tg-emoji emoji-id="{mask_id}">{mask_char}</tg-emoji>'
    else:
        mask = mask_char or "DXA"
    if len(clean) > 7: return f"{clean[:3]}{mask}{clean[-4:]}"
    elif len(clean) > 4: return f"{clean[:1]}{mask}{clean[-4:]}"
    return clean

LANG_MAP = {
    "#EN": "English", "#BN": "Bengali", "#AR": "Arabic", "#HI": "Hindi", 
    "#PA": "Punjabi", "#GU": "Gujarati", "#OR": "Odia", "#TA": "Tamil", 
    "#TE": "Telugu", "#KN": "Kannada", "#ML": "Malayalam", "#SI": "Sinhala", 
    "#TH": "Thai", "#LO": "Lao", "#BO": "Tibetan", "#MY": "Burmese", 
    "#AM": "Amharic", "#KM": "Khmer", "#KA": "Georgian", "#HY": "Armenian", 
    "#HE": "Hebrew", "#EL": "Greek", "#RU": "Russian", "#ZH": "Chinese", 
    "#JA": "Japanese", "#KO": "Korean", "#ID": "Indonesian", "#MS": "Malay", 
    "#VN": "Vietnamese", "#TL": "Filipino", "#ES": "Spanish", "#PT": "Portuguese", 
    "#FR": "French", "#DE": "German", "#IT": "Italian", "#PL": "Polish", 
    "#TR": "Turkish", "#NL": "Dutch", "#SV": "Swedish", "#DA": "Danish", 
    "#NO": "Norwegian", "#FI": "Finnish", "#CS": "Czech", "#SK": "Slovak", 
    "#HU": "Hungarian", "#RO": "Romanian", "#HR": "Croatian", "#BG": "Bulgarian", 
    "#UK": "Ukrainian", "#SW": "Swahili", "#AF": "Afrikaans"
}

# ==========================================
# 🌟 ADVANCED SERVICE & LANGUAGE DETECTION
# ==========================================

SERVICE_SMS_KEYWORDS = {
    # 🟢 Social Media & Chat (Added Arabic Keywords)
    "whatsapp": ["whatsapp", "whatsa", "whatsap", "whats", "whatsapp business", "whatsapp me", "whatsapp code", "whatsap", "واتساب", "واتساپ", "واٹس ایپ", "व्हाट्सएप", "वाट्सएप", "वॉट्सऐप", "व्हाट्सप्प", "হোয়াটসঅ্যাপ", "হোটসঅ্যাপ", "ватсап", "уотсап", "вотсап", "ватс апп", "వాట్సాప్", "വാട്‌സ്ആപ്പ്", "வாட்ஸ்அப்", "ವಾಟ್ಸಾಪ್", "વોટ્સએપ", "ਵਟਸਐਪ", "ହ୍ଵାଟସ୍ ଆପ୍", "වට්ස්ඇප්", "วอตส์แอปป์", "วอทส์แอพ", "ဝက်စ်အက်ပ်", "វ៉តសាប់", "ວອດແອັບ", "ワッツアップ", "왓츠앱", "whatsapp的", "whatsapp验证码", "וואטסאפ", "γουάτσαπ", "ዋትስአፕ", "ვოთსאფი", "վոթսափ"],
    "facebook": ["facebook", "fb", "meta", "fbook", "fb code", "facebook code", "فيسبوك", "فيس بوك"],
    "instagram": ["instagram", "insta", "ig", "ig code", "instagram code", "انستغرام", "انستقرام"],
    "telegram": ["telegram", "tg", "tele", "telegram code", "tg code", "t.me", "تيليجرام", "تليجرام"],
    "tiktok": ["tiktok", "tik tok", "tikvideo", "tiktok code", "tik code", "تيك توك"],
    "snapchat": ["snapchat", "snap", "snap code", "سناب شات"],
    "twitter": ["twitter", "x.com", "x code", "twitter code", "تويتر"],
    "discord": ["discord", "discord code", "ديسكورد"],
    "viber": ["viber", "viber code", "فايبر"],
    "line": ["line", "line code", "line verification", "لاين"],
    "wechat": ["wechat", "we chat", "wechat code", "وي تشات"],
    "signal": ["signal", "signal code", "سيجنال"],
    "linkedin": ["linkedin", "linked in", "لينكد إن"],
    "imo": ["imo", "imo code", "imo verification", "ايمو"],
    "kakaotalk": ["kakao", "kakaotalk", "كاكاو"],
    "qq": ["qq", "tencent qq"],
    "vk": ["vk", "vkontakte"],

    # 🔵 Tech & Mail
    "google": ["google", "gmail", "youtube", "g-", "google voice", "جوجل", "غوغل"],
    "microsoft": ["microsoft", "ms", "outlook", "live.com", "hotmail"],
    "apple": ["apple", "icloud", "itunes", "apple id"],
    "yahoo": ["yahoo", "yahoo code", "ymail"],
    "protonmail": ["proton", "protonmail"],
    
    # 💰 Crypto & Trading
    "binance": ["binance", "bnb", "binances"],
    "coinbase": ["coinbase"],
    "okx": ["okx", "okex"],
    "kucoin": ["kucoin"],
    "bybit": ["bybit"],
    "huobi": ["huobi", "htx"],
    "mexc": ["mexc"],
    "trustwallet": ["trust wallet", "trustwallet"],

    # 💳 Finance & Wallets
    "bkash": ["bkash", "b-kash", "bkash code"],
    "nagad": ["nagad", "nagad code"],
    "rocket": ["rocket", "dutch bangla"],
    "upay": ["upay", "upay code"],
    "paypal": ["paypal", "pay pal"],
    "paytm": ["paytm"],
    "cashapp": ["cash app", "cashapp"],
    "wise": ["wise", "transferwise"],

    # 🛒 E-commerce & Delivery
    "amazon": ["amazon", "amzn", "amazon code"],
    "ebay": ["ebay"],
    "aliexpress": ["aliexpress", "ali express"],
    "alibaba": ["alibaba"],
    "daraz": ["daraz", "daraz code"],
    "foodpanda": ["foodpanda", "food panda"],
    "uber": ["uber", "uber code", "uber verification", "uber eats"],
    "pathao": ["pathao", "pathao ride"],

    # 🎮 Gaming & Entertainment
    "netflix": ["netflix", "netflix code"],
    "spotify": ["spotify", "spotify code"],
    "steam": ["steam", "steam guard"],
    "epicgames": ["epic games", "epicgames"],
    "roblox": ["roblox", "roblox code"],
    "riotgames": ["riot", "riot games", "valorant", "league of legends"],
    "garena": ["garena", "free fire", "freefire"],
    "playstation": ["playstation", "psn"],

    # 🎲 Betting & Casino
    "1xbet": ["1xbet", "1x bet"],
    "melbet": ["melbet", "melbet code"],
    "linebet": ["linebet"],
    "bet365": ["bet365"],
    "megapari": ["megapari"],

    # ❤️ Dating
    "tinder": ["tinder", "tinder code"],
    "bumble": ["bumble"],
    "badoo": ["badoo"]
}

def detect_service(text):
    text_lower = str(text).lower()
    for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return service_key.upper()
    return None

def get_service_info_html(service_text, msg_text=""):
    s = str(service_text).upper().strip()
    m = str(msg_text).lower().strip()
    apps = bot_settings.get("premium_apps", {})
    
    detected_service = s
    if m:
        for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
            for kw in keywords:
                if kw in m:
                    detected_service = service_key.upper()
                    break
            if detected_service != s: break

    clean_s = re.sub(r'[^\w\s]', '', detected_service).strip()
    
    for app_name, data in apps.items():
        if app_name == detected_service or app_name == clean_s or app_name in detected_service or detected_service in app_name:
            full_name = data.get("name", app_name.title())
            char = data.get("char", "📱")
            eid = data.get("id")
            if eid: return full_name, f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
            return full_name, char
            
    if len(detected_service) > 20:
        return "Message", "💬"
        
    return detected_service.title(), "📱"

def detect_language(text):
    if not text: return "#EN"
    text_str = str(text)

    # ১. Unicode Block দিয়ে নিখুঁত বর্ণমালা শনাক্তকরণ (100% Accurate for scripts)
    if any('\u0600' <= c <= '\u06ff' for c in text_str): return "#AR" # Arabic / Persian / Urdu
    if any('\u0980' <= c <= '\u09ff' for c in text_str): return "#BN" # Bengali
    if any('\u0900' <= c <= '\u097f' for c in text_str): return "#HI" # Hindi / Marathi / Nepali
    if any('\u0a00' <= c <= '\u0a7f' for c in text_str): return "#PA" # Punjabi (Gurmukhi)
    if any('\u0a80' <= c <= '\u0aff' for c in text_str): return "#GU" # Gujarati
    if any('\u0b00' <= c <= '\u0b7f' for c in text_str): return "#OR" # Odia
    if any('\u0b80' <= c <= '\u0bff' for c in text_str): return "#TA" # Tamil
    if any('\u0c00' <= c <= '\u0c7f' for c in text_str): return "#TE" # Telugu
    if any('\u0c80' <= c <= '\u0cff' for c in text_str): return "#KN" # Kannada
    if any('\u0d00' <= c <= '\u0d7f' for c in text_str): return "#ML" # Malayalam
    if any('\u0d80' <= c <= '\u0dff' for c in text_str): return "#SI" # Sinhala
    if any('\u0e00' <= c <= '\u0e7f' for c in text_str): return "#TH" # Thai
    if any('\u0e80' <= c <= '\u0eff' for c in text_str): return "#LO" # Lao
    if any('\u0f00' <= c <= '\u0fff' for c in text_str): return "#BO" # Tibetan
    if any('\u1000' <= c <= '\u109f' for c in text_str): return "#MY" # Burmese (Myanmar)
    if any('\u1200' <= c <= '\u137f' for c in text_str): return "#AM" # Amharic (Ethiopic)
    if any('\u1780' <= c <= '\u17ff' for c in text_str): return "#KM" # Khmer
    if any('\u10a0' <= c <= '\u10ff' for c in text_str): return "#KA" # Georgian
    if any('\u0530' <= c <= '\u058f' for c in text_str): return "#HY" # Armenian
    if any('\u0590' <= c <= '\u05ff' for c in text_str): return "#HE" # Hebrew
    if any('\u0370' <= c <= '\u03ff' for c in text_str): return "#EL" # Greek
    if any('\u0400' <= c <= '\u04ff' for c in text_str): return "#RU" # Russian / Ukrainian (Cyrillic)
    if any('\u4e00' <= c <= '\u9fff' for c in text_str): return "#ZH" # Chinese
    if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text_str): return "#JA" # Japanese
    if any('\uac00' <= c <= '\ud7af' for c in text_str): return "#KO" # Korean

    # ২. OTP Keyword দিয়ে ভাষা শনাক্তকরণ (Latin script languages)
    text_lower = text_str.lower()
    
    # Asian / Pacific
    if any(w in text_lower for w in ["kode verifikasi", "jangan bagikan", "rahasia"]): return "#ID" # Indonesian
    if any(w in text_lower for w in ["kod pengesahan", "jangan kongsi"]): return "#MS" # Malay
    if any(w in text_lower for w in ["mã của bạn", "không chia sẻ", "mã xác minh"]): return "#VN" # Vietnamese
    if any(w in text_lower for w in ["ang iyong code", "huwag ibahagi"]): return "#TL" # Tagalog / Filipino
    
    # European / Americas
    if any(w in text_lower for w in ["código", "tu código", "verificación", "no compartas"]): return "#ES" # Spanish
    if any(w in text_lower for w in ["seu código", "código de verificação", "não compartilhe"]): return "#PT" # Portuguese
    if any(w in text_lower for w in ["code secret", "ne partagez pas", "votre code"]): return "#FR" # French
    if any(w in text_lower for w in ["dein code", "bestätigungscode", "nicht teilen"]): return "#DE" # German
    if any(w in text_lower for w in ["il tuo codice", "codice di verifica", "non condividere"]): return "#IT" # Italian
    if any(w in text_lower for w in ["twój kod", "nie udostępniaj", "kod weryfikacyjny"]): return "#PL" # Polish
    if any(w in text_lower for w in ["doğrulama kodu", "paylaşmayın", "onay kodu"]): return "#TR" # Turkish
    if any(w in text_lower for w in ["jouw code", "verificatiecode", "niet delen"]): return "#NL" # Dutch
    if any(w in text_lower for w in ["din kod", "verifieringskod", "dela inte"]): return "#SV" # Swedish
    if any(w in text_lower for w in ["bekræftelseskode", "del ikke"]): return "#DA" # Danish
    if any(w in text_lower for w in ["bekreftelseskode", "ikke del"]): return "#NO" # Norwegian
    if any(w in text_lower for w in ["vahvistuskoodi", "älä jaa"]): return "#FI" # Finnish
    if any(w in text_lower for w in ["váš kód", "ověřovací kód", "nesdílejte"]): return "#CS" # Czech
    if any(w in text_lower for w in ["overovací kód", "nezdieľajte"]): return "#SK" # Slovak
    if any(w in text_lower for w in ["ellenőrző kód", "ne oszd meg"]): return "#HU" # Hungarian
    if any(w in text_lower for w in ["codul tău", "codul de verificare", "nu partaja"]): return "#RO" # Romanian
    if any(w in text_lower for w in ["kontrolni kod", "kod za potvrdu", "ne delite"]): return "#HR" # Croatian/Serbian
    if any(w in text_lower for w in ["код за потвърждение", "не споделяйте"]): return "#BG" # Bulgarian
    if any(w in text_lower for w in ["ваш код", "код підтвердження"]): return "#UK" # Ukrainian
    
    # African
    if any(w in text_lower for w in ["msimbo wako", "usishiriki"]): return "#SW" # Swahili
    if any(w in text_lower for w in ["verifikasiekode", "moenie deel nie"]): return "#AF" # Afrikaans
    
    # ৩. উপরের কোনোটি না মিললে ডিফল্ট
    return "#EN"

def parse_chat_id(text):
    text = text.strip()
    if text.startswith("-100") or (text.startswith("-") and text[1:].isdigit()):
        return text
    if "t.me/" in text:
        parts = text.split("/")
        username = parts[-1]
        if username: return "@" + username if not username.startswith("@") else username
    if text.startswith("@"):
        return text
    return "@" + text

def is_admin(user_id):
    return user_id in bot_settings["admins"] or user_id == OWNER_ID

def check_force_join(user_id):
    if not bot_settings["fj_on"] or not bot_settings["fj_channels"]: return True
    if is_admin(user_id): return True
    for ch in bot_settings["fj_channels"]:
        res = api_call("getChatMember", {"chat_id": ch, "user_id": user_id})
        if res.get("ok") and res["result"]["status"] not in ["left", "kicked"]: continue
        else: return False
    return True

def send_force_join_msg(chat_id):
    kb = []
    for ch in bot_settings["fj_channels"]:
        url = f"https://t.me/{ch.replace('@', '')}" if ch.startswith("@") else ch
        kb.append([{"text": f"Join Channel", "icon_custom_emoji_id": "5789428375261023681", "url": url, "style": "primary"}])
    kb.append([{"text": "Check Joined", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "check_fj", "style": "success"}])
    send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Please join our channels to use the bot!</b>"), reply_markup={"inline_keyboard": kb})

def is_user_banned(user_id):
    if is_admin(user_id): return False
    if user_id in user_banned_cache and time.time() - user_banned_cache[user_id]['time'] < 60:
        return user_banned_cache[user_id]['banned']
    banned = False
    if db:
        try:
            doc = db.collection('users').document(str(user_id)).get()
            banned = doc.exists and doc.to_dict().get("banned", False)
        except: pass
    user_banned_cache[user_id] = {'banned': banned, 'time': time.time()}
    return banned

# ==========================================
# Captcha Auto Login & Parsing Core
# ==========================================
def extract_otp_code(text):
    clean_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', str(text))

    # 1. Multi-part OTPs (e.g. 123-456 or 809-761)
    multi_part = re.search(r'(\d{3}[-\s]+\d{3})|(\d{2}[-\s]+\d{2}[-\s]+\d{2})', clean_text)
    if multi_part:
        # হাইফেন (-) থাকলে সেটা রেখে দিবে, কিন্তু স্পেস থাকলে মুছে একসাথে করে দিবে
        return multi_part.group(0).replace(" ", "")

    # 2. Keyword-based extraction
    otp_keywords = ['code', 'is', 'otp', 'pin', 'verification', 'auth', 'কোড', 'رمز', 'your code']
    keywords_pattern = '|'.join(otp_keywords)
    keyword_match = re.search(rf'(?:{keywords_pattern})\s*(?:is|:|-|=)?\s*([a-z0-9]{{4,10}})', clean_text, re.I)
    if keyword_match and keyword_match.group(1).isdigit():
        return keyword_match.group(1)
        
    keyword_match_rev = re.search(rf'([a-z0-9]{{4,10}})\s*(?:is your|is the|কোড)', clean_text, re.I)
    if keyword_match_rev and keyword_match_rev.group(1).isdigit():
        return keyword_match_rev.group(1)

    # 3. Google OTP
    g_match = re.search(r'G-(\d{6})', clean_text, re.IGNORECASE)
    if g_match: return g_match.group(1)

    # 4. Digit sequences fallback
    digit_matches = re.findall(r'(?<!\d)\d{4,8}(?!\d)', clean_text)
    if digit_matches: return digit_matches[0]

    return None

def parse_panel_response(response_text, p_config=None):
    """Parse API/HTML panel responses.

    KSI IPRN returns JSON shaped roughly like:
    {"success": true, "data": [{"source": "...", "number": "...",
      "message": "...", "rate": ..., "status": "...", "received_at": "..."}]}

    The parser deliberately uses the message body as the OTP source and keeps
    the complete message so it can be delivered to the user.
    """
    results = []
    p_config = p_config or {}
    p_type = p_config.get("type", "API Panel")
    n_col_name = str(p_config.get("num_col_name", "number")).lower()
    m_col_name = str(p_config.get("msg_col_name", "message")).lower()

    try:
        n_idx = int(p_config.get("num_col_idx", 1)) - 1
    except Exception:
        n_idx = 0
    try:
        m_idx = int(p_config.get("msg_col_idx", 2)) - 1
    except Exception:
        m_idx = 1

    def normalize_number(value):
        if value is None:
            return ""
        return re.sub(r"\D", "", str(value))

    def add_result(num, message):
        num = normalize_number(num)
        message = str(message or "").strip()
        if not num or not (5 <= len(num) <= 18) or len(message) <= 4:
            return
        otp = extract_otp_code(message) or "N/A"
        # Keep every valid SMS, not only OTP-bearing SMS.
        results.append({"number": num, "message": message, "otp": str(otp)})

    # HTML/Captcha panels keep the existing table behaviour.
    if p_type == "Auto Captcha Panel":
        try:
            soup = BeautifulSoup(response_text, "html.parser")
            for table in soup.find_all("table"):
                rows = table.find_all("tr")
                if not rows:
                    continue
                final_n_idx, final_m_idx = n_idx, m_idx
                header_cells = rows[0].find_all(["th", "td"])
                for i, cell in enumerate(header_cells):
                    c_text = cell.get_text(" ", strip=True).lower()
                    if n_col_name in c_text:
                        final_n_idx = i
                    if m_col_name in c_text:
                        final_m_idx = i

                for row in rows:
                    cols = row.find_all(["td", "th"])
                    if all(c.name == "th" for c in cols):
                        continue
                    if len(cols) > max(final_n_idx, final_m_idx):
                        add_result(
                            cols[final_n_idx].get_text(" ", strip=True),
                            cols[final_m_idx].get_text(" ", strip=True)
                        )
        except Exception:
            pass
        return _dedupe_parsed_results(results)

    # JSON API parser.
    try:
        data = json.loads(response_text)
    except Exception:
        return results

    # KSI-specific path: only inspect message records under data.
    is_ksi = str(p_config.get("name", "")).strip().lower() == "ksi iprn"
    if is_ksi:
        records = data.get("data", []) if isinstance(data, dict) else []
        if isinstance(records, dict):
            records = records.get("messages", records.get("data", []))
        if isinstance(records, list):
            for item in records:
                if not isinstance(item, dict):
                    continue
                # KSI's canonical fields.
                num = (
                    item.get("number")
                    or item.get("phone")
                    or item.get("msisdn")
                    or item.get("num")
                )
                message = (
                    item.get("message")
                    or item.get("msg")
                    or item.get("sms")
                    or item.get("content")
                    or item.get("text")
                )
                add_result(num, message)

        # Some KSI responses can be nested; inspect nested data only if the
        # canonical list did not produce anything.
        if not results:
            def walk(node):
                if isinstance(node, dict):
                    if any(k in node for k in ("message", "msg", "sms", "content", "text")):
                        add_result(
                            node.get("number") or node.get("phone") or node.get("msisdn") or node.get("num"),
                            node.get("message") or node.get("msg") or node.get("sms") or node.get("content") or node.get("text")
                        )
                    for value in node.values():
                        if isinstance(value, (dict, list)):
                            walk(value)
                elif isinstance(node, list):
                    for value in node:
                        if isinstance(value, (dict, list)):
                            walk(value)
            walk(data)

        return _dedupe_parsed_results(results)

    # Generic JSON parser.
    def process_item(item):
        pot_nums = []
        pot_msg = None
        values = []

        if isinstance(item, dict):
            lower_keys = {str(k).lower(): v for k, v in item.items()}
            for key in ("number", "num", "phone", "msisdn", "sender"):
                if key in lower_keys:
                    n = normalize_number(lower_keys[key])
                    if 5 <= len(n) <= 18 and n not in pot_nums:
                        pot_nums.append(n)

            for key in ("message", "msg", "sms", "content", "text"):
                if key in lower_keys and str(lower_keys[key]).strip():
                    candidate = str(lower_keys[key]).strip()
                    if extract_otp_code(candidate):
                        pot_msg = candidate
                        break
            values = list(item.values())
        elif isinstance(item, list):
            values = item

        for value in values:
            if isinstance(value, (dict, list)) or value is None:
                continue
            value_str = str(value).strip()
            n = normalize_number(value_str)
            if (
                7 <= len(n) <= 18
                and not re.search(r"[A-Za-z]", value_str)
                and not re.search(r"\d{4}[-/]\d{2}[-/]\d{2}", value_str)
                and not re.search(r"\d{2}:\d{2}:\d{2}", value_str)
                and "." not in value_str
                and n not in pot_nums
            ):
                pot_nums.append(n)

            if len(value_str) > 4 and not value_str.isdigit() and extract_otp_code(value_str):
                if pot_msg is None or len(value_str) > len(pot_msg):
                    pot_msg = value_str

        if pot_nums and pot_msg:
            # Prefer an active-session number over unrelated numeric fields.
            chosen = None
            for n in pot_nums:
                for session_data in user_active_sessions.values():
                    if any(_numbers_match(n, x) for x in session_data.get("nums", [])):
                        chosen = n
                        break
                if chosen:
                    break
            chosen = chosen or pot_nums[0]
            add_result(chosen, pot_msg)

    def walk(node):
        if isinstance(node, dict):
            process_item(node)
            for value in node.values():
                if isinstance(value, (dict, list)):
                    walk(value)
        elif isinstance(node, list):
            if node and not isinstance(node[0], (dict, list)):
                process_item(node)
            for value in node:
                if isinstance(value, (dict, list)):
                    walk(value)

    walk(data)
    return _dedupe_parsed_results(results)


def _numbers_match(a, b):
    a = re.sub(r"\D", "", str(a or ""))
    b = re.sub(r"\D", "", str(b or ""))
    if not a or not b:
        return False
    return (
        a == b
        or (len(a) >= 8 and len(b) >= 8 and (a.endswith(b[-8:]) or b.endswith(a[-8:])))
    )


def _dedupe_parsed_results(items):
    seen = set()
    out = []
    for item in items:
        key = f"{item.get('number','')}_{item.get('otp','')}_{item.get('message','')}"
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


# 🌟 Advanced Automated Background Captcha Solver 🌟
def attempt_auto_login(p, idx):
    login_url = p.get("login_url", "").strip()
    if not login_url.startswith("http"):
        login_url = "http://" + login_url
        
    if not login_url.lower().endswith('/login') and not login_url.lower().endswith('.php'):
        login_url = f"{login_url.rstrip('/')}/login"
        
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })
    
    try:
        res = session.get(login_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        all_text = res.text
        
        # 1. SOLVE CAPTCHA (Exact bot 3.py logic)
        captcha_match = re.search(r'(\d+\s*[\+\-\*]\s*\d+)\s*[=\?:]', all_text)
        if not captcha_match:
            captcha_match = re.search(r'what is\s*(\d+\s*[\+\-\*]\s*\d+)', all_text, re.I)
        if not captcha_match:
            elements = soup.find_all(["label", "div", "span", "p", "strong"])
            for el in elements:
                txt = el.get_text(separator=" ", strip=True)
                if any(op in txt for op in ["+", "-", "*"]):
                    m = re.search(r'(\d+\s*[\+\-\*]\s*\d+)', txt)
                    if m:
                        captcha_match = m
                        break
                        
        captcha_text = captcha_match.group(1) if captcha_match else "0 + 0"
        answer = "0"
        m2 = re.search(r'(\d+)\s*([\+\-\*])\s*(\d+)', captcha_text)
        if m2:
            a, op, b = int(m2.group(1)), m2.group(2), int(m2.group(3))
            if op == '+': answer = str(a + b)
            elif op == '-': answer = str(a - b)
            elif op == '*': answer = str(a * b)

        # 2. FIND FORM
        form = soup.find("form")
        if not form:
            p["login_status"] = "❌ No login form found"
            return False
            
        action = form.get("action")
        from urllib.parse import urljoin
        post_url = urljoin(login_url, action) if action else login_url

        form_data = {}
        for hidden in form.find_all("input", type="hidden"):
            name = hidden.get("name")
            if name: form_data[name] = hidden.get("value") or ""
        
        user_input = form.find("input", {"name": re.compile(r"user|email|id", re.I)}) or \
                     form.find("input", {"type": "text", "placeholder": re.compile(r"user|email", re.I)}) or \
                     form.find("input", {"type": "text"})
                     
        pass_input = form.find("input", {"name": re.compile(r"pass", re.I)}) or \
                     form.find("input", {"type": "password"})
                     
        captcha_input = form.find("input", {"placeholder": re.compile(r"answer|ans|code|verification|value|captcha", re.I)}) or \
                        form.find("input", {"name": re.compile(r"ans|captcha|ver|code", re.I)})
        
        user_field = user_input.get("name") if user_input else "username"
        pass_field = pass_input.get("name") if pass_input else "password"
        captcha_field = captcha_input.get("name") if captcha_input else "answer"

        form_data[user_field] = p.get("username", "")
        form_data[pass_field] = p.get("password", "")
        if captcha_field:
            form_data[captcha_field] = answer

        # 3. SUBMIT
        login_req = session.post(post_url, data=form_data, allow_redirects=True, timeout=15)
        
        # 4. VERIFY (Exact bot 3.py check logic)
        msg_link = p.get("msg_link", "").strip()
        if not msg_link.startswith("http") and msg_link != "":
            msg_link = "http://" + msg_link
            
        check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
        
        check_res = session.get(check_url, timeout=10)
        
        if 'logout' in login_req.text.lower() or 'logout' in check_res.text.lower() or 'sms reports' in check_res.text.lower() or 'dashboard' in check_res.text.lower() or 'cdrs' in check_res.text.lower():
            panel_sessions[idx] = session
            p["login_status"] = "✅ Active & Fetching"
            return True
        else:
            # এখানে ফেইল হলে অংক কী পেয়েছিল তা দেখা যাবে
            p["login_status"] = f"❌ Login Failed (Math: {captcha_text} = {answer})"
            return False
            
    except Exception as e:
        p["login_status"] = f"❌ Error: {str(e)[:20]}"
        
    return False

# ==========================================
# Fast X Provider Adapter
# ==========================================
def fastx_fetch_number(range_str, api_key):
    """Fetch one Fast X number using the fixed Fast X API and the admin-supplied key."""
    try:
        headers = {"X-API-Key": str(api_key).strip()}
        res = requests.post(
            f"{FASTX_BASE_URL}/getnum",
            json={"range": str(range_str), "is_national": False},
            headers=headers,
            timeout=15,
        )
        data = res.json()
        payload = data.get("data", {}) if isinstance(data, dict) else {}
        if isinstance(payload, dict) and payload.get("full_number"):
            return {
                "number": str(payload.get("full_number")),
                "otp_now": bool(payload.get("otp_now", False)),
                "otp": payload.get("otp"),
                "sms": payload.get("sms"),
            }
    except Exception as exc:
        print(f"[FAST X] getnum error: {exc}")
    return None


def fastx_country_range(country_name):
    """Resolve a displayed country name/ISO/calling code to the Fast X range."""
    q = str(country_name or "").strip().upper()
    flags = bot_settings.get("premium_flags", {})
    for calling_code, info in flags.items():
        if not isinstance(info, dict):
            continue
        iso = str(info.get("iso", "")).upper()
        name = str(info.get("name", "")).upper()
        if q in {iso, name, str(calling_code).upper()} or q == str(info.get("char", "")).upper():
            return str(calling_code)
        if q and q in name:
            return str(calling_code)
    digits = re.sub(r"\D", "", q)
    return digits or q


def fastx_range_from_number(number):
    """Return the longest configured calling-code prefix for a Fast X number."""
    clean = re.sub(r"\D", "", str(number or ""))
    if not clean:
        return ""
    flags = bot_settings.get("premium_flags", {})
    for code in sorted((str(k) for k in flags.keys()), key=len, reverse=True):
        if clean.startswith(code):
            return code
    return clean[:3] if len(clean) >= 3 else clean


def fastx_build_number_message(chat_id, msg_id, call, country_name, service_name="Fast X", range_override=None):
    """Allocate Fast X number(s) and render them through the main bot UI."""
    global total_assigned_stats, fastx_assigned_ranges
    range_str = str(range_override).strip() if range_override else fastx_country_range(country_name)
    req_count = max(1, int(bot_settings.get("num_req", 1) or 1))
    fastx_keys = [str(k).strip() for k in bot_settings.get("fastx_keys", []) if str(k).strip()]
    if not fastx_keys:
        answer_callback(call["id"], "❌ Fast X API Key is not configured!", show_alert=True)
        return False
    fetched_nums = []
    for _ in range(req_count):
        result = None
        for api_key in fastx_keys:
            result = fastx_fetch_number(range_str, api_key)
            if result and result.get("number"):
                break
        if not result or not result.get("number"):
            break
        num_str = re.sub(r"\D", "", str(result["number"]))
        if not num_str or num_str in fetched_nums:
            continue
        fetched_nums.append(num_str)
        fastx_assigned_numbers[num_str] = chat_id
        fastx_assigned_ranges[num_str] = str(range_str)
        total_assigned_stats += 1

    if not fetched_nums:
        answer_callback(call["id"], "❌ Fast X number out of stock!", show_alert=True)
        return False

    save_db()
    first = fetched_nums[0]
    char_flag, iso = get_flag_and_code(first)
    app_full_name, _ = get_service_info_html(service_name)
    flags_db = bot_settings.get("premium_flags", {})
    country_emoji_html = char_flag
    for _, flag_data in flags_db.items():
        if isinstance(flag_data, dict) and str(flag_data.get("iso", "")).upper() == str(iso).upper():
            if flag_data.get("id"):
                country_emoji_html = f'<tg-emoji emoji-id="{flag_data["id"]}">{flag_data.get("char", char_flag)}</tg-emoji>'
            break

    kb = [[{"text": str(app_full_name), "icon_custom_emoji_id": "5337302974806922068", "callback_data": "ignore", "style": "primary"}]]
    for num in fetched_nums:
        display_num = f"+{num}"
        flag_id = "5780471598922337683"
        for _, fd in flags_db.items():
            if isinstance(fd, dict) and str(fd.get("iso", "")).upper() == str(iso).upper() and fd.get("id"):
                flag_id = fd["id"]
                break
        kb.append([{"text": display_num, "icon_custom_emoji_id": flag_id, "copy_text": {"text": display_num}, "style": "success"}])

    kb.append([{
        "text": "Change Number", "icon_custom_emoji_id": "5465368548702446780",
        "callback_data": f"fastx_change_{country_name}", "style": "danger"
    }, {
        "text": "Change Country", "icon_custom_emoji_id": "5305517382138112561",
        "callback_data": "g_s_Fast X", "style": "danger"
    }])
    c_btns = []
    for b in bot_settings.get("custom_messages", {}).get("get_number", {}).get("buttons", []):
        b2 = b.copy()
        b2.setdefault("style", "primary")
        c_btns.append(b2)
    for i in range(0, len(c_btns), 2):
        kb.append(c_btns[i:i+2])
    kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings.get("otp_link", ""), "style": "primary"}])

    text_numbers, custom_kb = render_new_number_message(country_emoji_html, country_name, app_full_name)
    kb.extend(custom_kb)
    edit_message(chat_id, msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
    user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": fetched_nums, "provider": "Fast X", "service": service_name, "range": str(range_str)}
    answer_callback(call["id"], "✅ Fast X number assigned!")
    return True


def fastx_sync_liveaccess(api_key):
    """Sync Fast X service -> country -> range directly from the Fast X /liveaccess API.

    The original Fast X bot uses GET /api/liveaccess with the admin API key and receives:
        {"status": "ok", "services": [{"sid": "...", "ranges": ["261", ...]}]}
    So Fast X does not need an OTP to discover its available services/ranges.
    """
    global bot_settings
    try:
        res = requests.get(
            f"{FASTX_BASE_URL}/liveaccess",
            headers={"X-API-Key": str(api_key).strip()},
            timeout=15,
        )
        data = res.json()
        if not isinstance(data, dict):
            return False
        # Fast X original bot returns services from /api/liveaccess.
        # Accept both the original root shape and a data-wrapped response.
        payload = data.get("data") if isinstance(data.get("data"), dict) else data
        status = str(data.get("status", payload.get("status", "ok"))).lower()
        services = payload.get("services", []) or []
        if status not in ("ok", "success", "200") or not isinstance(services, list):
            return False

        fx = bot_settings.setdefault("fastx_services", {})
        search = bot_settings.setdefault("fastx_search_countries", [])
        changed = False

        for item in services:
            if not isinstance(item, dict):
                continue
            sid = str(item.get("sid", "")).strip().upper()
            # Ignore internal numeric IDs returned by Fast X (they are not
            # human-readable service names). Also reject generic Number entries.
            if not sid or sid in fastx_hidden_services:
                continue
            if sid.isdigit() or sid in {"NUMBER", "NUMBERS", "PHONE", "PHONE NUMBER"}:
                continue
            if not re.search(r"[A-Z]", sid):
                continue
            ranges = item.get("ranges", []) or []
            if not isinstance(ranges, list):
                continue

            service_map = fx.setdefault(sid, {})
            for raw_range in ranges:
                if isinstance(raw_range, dict):
                    raw_range = raw_range.get("range", raw_range.get("code", raw_range.get("value", "")))
                rng = str(raw_range).strip().replace("+", "").replace("X", "")
                if not rng or f"{sid}|{rng}" in fastx_hidden_ranges:
                    continue
                # Resolve the liveaccess range through the existing country/flag
                # database. V20 called a non-existent get_country_info() helper,
                # so valid ranges were being discarded as Unknown.
                try:
                    country_name = get_flag_info_html(rng, return_full_name=True)
                except Exception:
                    country_name = "Unknown"
                country_name = str(country_name or "Unknown").strip()
                if not country_name or country_name == "Unknown":
                    continue
                hidden_country_key = f"{sid}|{country_name}"
                if hidden_country_key in fastx_hidden_countries:
                    continue
                arr = service_map.setdefault(country_name, [])
                if rng not in arr:
                    arr.append(rng)
                    changed = True
                # Search Number country code follows the same range discovered by liveaccess.
                code = re.sub(r"\D", "", rng)
                if code and code not in search:
                    search.append(code)
                    changed = True

        if changed:
            save_db()
        return True
    except Exception as exc:
        print(f"[FAST X] liveaccess sync error: {exc}")
        return False


def fastx_sms_listener():
    """Poll Fast X OTPs and auto-build service/country/range mappings.

    Fast X automatic menu discovery is driven by the same /liveaccess API used
    by the original Fast X bot: API key + Auto Range ON is enough to populate
    service -> country -> range without waiting for an OTP.
    """
    global processed_fastx_otps, recent_traffic, fastx_assigned_ranges
    last_auto_update = 0.0
    last_liveaccess_sync = 0.0

    while True:
        try:
            if not bot_settings.get("fastx_enabled", FASTX_ENABLED_DEFAULT):
                time.sleep(5)
                continue
            fastx_keys = [str(k).strip() for k in bot_settings.get("fastx_keys", []) if str(k).strip()]
            if not fastx_keys:
                time.sleep(5)
                continue

            # Fast X original bot discovers services/countries/ranges from /liveaccess
            # immediately from the API key. Do the same whenever Auto Range is ON.
            now_liveaccess = time.time()
            if bot_settings.get("fastx_auto", False) and now_liveaccess - last_liveaccess_sync >= 20:
                last_liveaccess_sync = now_liveaccess
                for api_key in fastx_keys:
                    if fastx_sync_liveaccess(api_key):
                        break

            # Keep the same key-driven connection model as the other Bangla panels.
            for api_key in fastx_keys:
                try:
                    res = requests.get(
                        f"{FASTX_BASE_URL}/success-otp-info",
                        headers={"X-API-Key": api_key},
                        timeout=15
                    )
                    data = res.json()
                except Exception:
                    continue

                records = data.get("data", {}).get("otps", []) if isinstance(data, dict) else []
                if not isinstance(records, list):
                    continue

                for item in records:
                    if not isinstance(item, dict):
                        continue
                    num = re.sub(r"\D", "", str(item.get("number", "")))
                    if not num:
                        continue
                    owner_id = fastx_assigned_numbers.get(num)
                    if not owner_id:
                        for assigned, uid in list(fastx_assigned_numbers.items()):
                            if _numbers_match(assigned, num):
                                owner_id = uid
                                num = assigned
                                break
                    if not owner_id:
                        continue

                    msg_text = str(item.get("message", "") or "").strip()
                    if not msg_text:
                        continue
                    otp = extract_otp_code(msg_text) or "N/A"
                    otp_id = str(item.get("otp_id", "") or "")
                    unique = f"FASTX|{num}|{otp_id}|{otp}|{hash(msg_text)}"
                    if unique in processed_fastx_otps:
                        continue
                    processed_fastx_otps.add(unique)
                    if len(processed_fastx_otps) > 10000:
                        processed_fastx_otps = set(list(processed_fastx_otps)[-5000:])

                    display_num = f"+{num}"
                    char, iso = get_flag_and_code(num)
                    service = detect_service(msg_text) or "Fast X"
                    app_full_name, prem_app_html = get_service_info_html(service, msg_text)
                    lang = detect_language(msg_text)
                    reward = get_otp_reward_for_user(num, owner_id, "Fast X")
                    reward_line = f"\n💰 <b>Reward: {reward:g} TK</b>" if reward > 0 else ""
                    inbox_msg = render_body_text(
                        f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {display_num} | 💬 {lang}\n"
                        f"📝 <b>Full Msg:</b> <code>{html.escape(msg_text)}</code>\n"
                        f"🔐 <b>OTP:</b> <code>{html.escape(otp)}</code>{reward_line}"
                    )
                    otp_button = [{"text": str(otp), "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": str(otp)}, "style": "primary"}]
                    result = send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": [otp_button]})
                    if isinstance(result, dict) and result.get("ok"):
                        credit_earning(owner_id, reward, "otp")
                        if db:
                            try:
                                increment_user_otp(owner_id)
                            except Exception:
                                pass

                    group_msg = render_body_text(
                        f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {mask_number(display_num)} | 💬 {str(lang).upper()[:3] if lang else '#EN'}"
                    )
                    for fw in bot_settings.get("fw_groups", []):
                        fw_kb = [list(otp_button)]
                        temp_row = []
                        styles = ["danger", "success", "primary"]
                        for i, btn in enumerate(fw.get("buttons", [])):
                            if not btn.get("url"):
                                continue
                            b_obj = {"text": btn.get("text", ""), "url": btn["url"], "style": styles[i % 3]}
                            if btn.get("icon_custom_emoji_id"):
                                b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                            temp_row.append(b_obj)
                            if len(temp_row) == 2:
                                fw_kb.append(temp_row); temp_row = []
                        if temp_row:
                            fw_kb.append(temp_row)
                        send_message(fw.get("chat_id"), group_msg, reply_markup={"inline_keyboard": fw_kb})

                    current_time = time.time()
                    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                    # Prefer the exact range used to allocate this number. If an old
                    # assignment has no stored range, fall back to its country code.
                    real_range = str(fastx_assigned_ranges.get(num, "") or "")
                    if not real_range:
                        real_range = fastx_range_from_number(num)
                    recent_traffic.append({
                        "service": app_full_name,
                        "iso": iso,
                        "flag": char,
                        "number": num,
                        "time": current_time,
                        "real_range": real_range,
                        "source": "fastx"
                    })

                # One key is enough to populate the shared recent-traffic feed.
                # Do not break here; another key may have unique OTP traffic.

            # Fast X service/country/range discovery is now driven by the original
            # /liveaccess endpoint above. Do not let the old OTP-traffic-only updater
            # delete valid liveaccess ranges when no OTP has arrived yet.
            current_time = time.time()
            if False and bot_settings.get("fastx_auto", False) and current_time - last_auto_update > 120:
                last_auto_update = current_time
                changed = False
                bot_settings.setdefault("fastx_services", {})
                bot_settings.setdefault("fastx_search_countries", [])

                source_hits = [t for t in recent_traffic if t.get("source") == "fastx" and "real_range" in t]
                srv_counts = Counter(str(t.get("service", "Fast X")).upper() for t in source_hits)
                top_srvs = [s for s, c in srv_counts.most_common(6)]

                for srv in top_srvs:
                    if srv not in bot_settings["fastx_services"]:
                        bot_settings["fastx_services"][srv] = {}
                        changed = True

                    iso_counts = Counter(t.get("iso") for t in source_hits if str(t.get("service", "")).upper() == srv)
                    top_isos = [i for i, c in iso_counts.most_common(3) if i]
                    for iso in top_isos:
                        full_country_name = get_flag_info_html(str(iso), return_full_name=True).title()
                        if full_country_name not in bot_settings["fastx_services"][srv]:
                            bot_settings["fastx_services"][srv][full_country_name] = []
                            changed = True

                        rng_counts = Counter(
                            str(t.get("real_range", "")) for t in source_hits
                            if str(t.get("service", "")).upper() == srv
                            and t.get("iso") == iso
                            and t.get("real_range")
                        )
                        for rng, _count in rng_counts.most_common(2):
                            if rng and rng not in bot_settings["fastx_services"][srv][full_country_name]:
                                bot_settings["fastx_services"][srv][full_country_name].append(rng)
                                changed = True
                            if rng:
                                country_code = rng[:3]
                                if country_code and country_code not in bot_settings["fastx_search_countries"]:
                                    bot_settings["fastx_search_countries"].append(country_code)
                                    changed = True

                # Remove stale Fast X services/countries/ranges when no traffic
                # has appeared in the last 120 seconds, exactly like Voltx/Stex.
                services_to_remove = []
                for srv, countries in list(bot_settings["fastx_services"].items()):
                    srv_hit = sum(
                        1 for t in source_hits
                        if str(t.get("service", "")).upper() == str(srv).upper()
                        and current_time - t.get("time", 0) <= 120
                    )
                    if srv_hit < 1:
                        services_to_remove.append(srv)
                        continue

                    countries_to_remove = []
                    for country, ranges in list(countries.items()):
                        c_hit = sum(
                            1 for t in source_hits
                            if str(t.get("service", "")).upper() == str(srv).upper()
                            and get_flag_info_html(str(t.get("iso", "")), return_full_name=True).title() == country
                            and current_time - t.get("time", 0) <= 120
                        )
                        if c_hit < 1:
                            countries_to_remove.append(country)
                            continue

                        for rng in list(ranges):
                            r_hit = sum(
                                1 for t in source_hits
                                if str(t.get("service", "")).upper() == str(srv).upper()
                                and str(t.get("real_range", "")) == str(rng)
                                and current_time - t.get("time", 0) <= 120
                            )
                            if r_hit < 1:
                                ranges.remove(rng)
                                changed = True

                        if not ranges:
                            countries_to_remove.append(country)

                    for country in countries_to_remove:
                        if country in bot_settings["fastx_services"].get(srv, {}):
                            del bot_settings["fastx_services"][srv][country]
                            changed = True

                for srv in services_to_remove:
                    bot_settings["fastx_services"].pop(srv, None)
                    changed = True

                if changed:
                    save_db()

        except Exception as exc:
            print(f"[FAST X] listener error: {exc}")
        time.sleep(5)


def panel_monitor_thread():
    """Background SMS monitor.

    KSI is handled as a real delivery source, not as a Test Connection parser.
    A KSI record is only consumed after at least one assigned Telegram user has
    actually accepted the message from Telegram's sendMessage endpoint.
    """
    global processed_otps, processed_ksi_messages, recent_traffic, panel_sessions

    def clean_num(v):
        return re.sub(r"\D", "", str(v or ""))

    def find_ksi_owners(number):
        target = clean_num(number)
        if not target:
            return []
        owners = set()

        # 1) Live active sessions — authoritative while a user is holding a number.
        for uid, session_data in list(user_active_sessions.items()):
            try:
                for assigned in session_data.get("nums", []):
                    if _numbers_match(assigned, target):
                        owners.add(uid)
                        ksi_assigned_numbers[str(assigned)] = uid
                        break
            except Exception:
                continue

        # 2) Persistent KSI mapping.
        for assigned, uid in list(ksi_assigned_numbers.items()):
            if _numbers_match(assigned, target):
                owners.add(uid)

        # 3) Other API assignment maps used by this bot.
        for amap in (stex_assigned_numbers, voltx_assigned_numbers, zenex_assigned_numbers):
            for assigned, uid in list(amap.items()):
                if _numbers_match(assigned, target):
                    owners.add(uid)

        # 4) Last-resort recovery from stock metadata, including used_by.
        for batch in number_batches.values():
            for nobj in batch.get("numbers", []):
                assigned = nobj.get("num", "")
                if _numbers_match(assigned, target):
                    for uid in nobj.get("used_by", []) or []:
                        owners.add(uid)
                        ksi_assigned_numbers[str(assigned)] = uid

        return list(owners)

    def safe_send(chat_id, text, reply_markup=None):
        """Send the message with the requested inline keyboard; fall back to plain text only if Telegram rejects the markup."""
        try:
            result = send_message(chat_id, text, reply_markup=reply_markup) if reply_markup else send_message(chat_id, text)
            if isinstance(result, dict) and result.get("ok") is True:
                return True
            if reply_markup:
                result = send_message(chat_id, text)
                return isinstance(result, dict) and result.get("ok") is True
            return False
        except Exception as exc:
            print(f"[KSI DELIVERY] Telegram send exception to {chat_id}: {exc}")
            if reply_markup:
                try:
                    result = send_message(chat_id, text)
                    return isinstance(result, dict) and result.get("ok") is True
                except Exception:
                    pass
            return False

    while True:
        try:
            for idx, p in enumerate(bot_settings.get("panels", [])):
                if p.get("status") != "ON":
                    continue

                parsed_data = []
                is_ksi = str(p.get("name", "")).strip().lower() == "ksi iprn"

                if p.get("type") == "Auto Captcha Panel":
                    sess = panel_sessions.get(idx)
                    if not sess:
                        now = time.time()
                        if now - p.get("last_login_attempt", 0) < 30:
                            continue
                        p["last_login_attempt"] = now
                        if not attempt_auto_login(p, idx):
                            continue
                        sess = panel_sessions.get(idx)
                    try:
                        parsed_data, _ = fetch_cpt_panel_cdrs(p, sess, p.get("msg_link", ""))
                        p["login_status"] = "✅ Active & Fetching"
                    except Exception:
                        panel_sessions.pop(idx, None)
                        continue
                elif p.get("api_url") or p.get("full_api_url"):
                    full_url = p.get("full_api_url", "").strip()
                    url = p.get("api_url", "").strip()
                    token = p.get("token", "").strip()
                    if not full_url and not url:
                        continue

                    if is_ksi:
                        urls_to_try = [ksi_iprn_messages_url(url)]
                    elif full_url:
                        urls_to_try = [full_url]
                    else:
                        urls_to_try = []
                        if "{token}" in url or "{key}" in url:
                            urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                        elif "token=" in url or "key=" in url:
                            urls_to_try.append(url)
                        else:
                            sep = "&" if "?" in url else "?"
                            urls_to_try += [f"{url}{sep}token={token}", f"{url}{sep}key={token}&start=0", f"{url}{sep}key={token}"]

                    headers = {"User-Agent": "Mozilla/5.0"}
                    if is_ksi and token:
                        headers["Authorization"] = f"Bearer {token}"

                    for try_url in urls_to_try:
                        try:
                            res = requests.get(try_url, headers=headers, timeout=15)
                            p["last_http_status"] = res.status_code
                            if res.status_code in (401, 403, 429):
                                p["last_error"] = f"HTTP {res.status_code}"
                                break
                            parsed_data = parse_panel_response(res.text, p)
                            if parsed_data:
                                break
                        except Exception as exc:
                            p["last_error"] = str(exc)[:200]
                else:
                    continue

                if not parsed_data:
                    continue

                limit = p.get("records", 0)
                if p.get("type") != "Auto Captcha Panel" and limit and limit > 0:
                    parsed_data = parsed_data[:limit]

                for item in parsed_data:
                    num = clean_num(item.get("number", ""))
                    msg_text = str(item.get("message", "") or "").strip()
                    if not num or len(msg_text) < 5:
                        continue

                    otp = str(item.get("otp", "") or "").strip()
                    if not otp or otp.upper() in {"CODE", "N/A", "NA", "NONE", "NULL"}:
                        otp = extract_otp_code(msg_text) or "N/A"

                    # Include the source record time/id when available, so a new SMS
                    # can never be confused with an older message having the same OTP.
                    source_key = str(item.get("id") or item.get("message_id") or item.get("received_at") or "")
                    ksi_key = f"KSI|{num}|{source_key}|{otp}|{hash(msg_text)}"
                    if is_ksi and ksi_key in processed_ksi_messages:
                        continue

                    # Resolve the actual owner BEFORE sending anything to the group.
                    owners = find_ksi_owners(num) if is_ksi else []
                    if is_ksi and not owners:
                        # Keep it in the API history and retry next cycle; do not lose it.
                        continue

                    display_num = f"+{num}"
                    char, iso = get_flag_and_code(num)
                    app_name = item.get("service") or detect_service(msg_text) or p.get("name", "Panel")
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                    lang = detect_language(msg_text)

                    # Inline button: OTP when present, N/A otherwise. Telegram's
                    # copy_text makes the value directly copyable from the button.
                    otp_button = [{
                        "text": str(otp or "N/A"),
                        # Same premium OTP emoji used by the Bangla/MG OTP panel.
                        "icon_custom_emoji_id": "5296369303661067030",
                        "copy_text": {"text": str(otp or "N/A")},
                        "style": "primary"
                    }]
                    inbox_kb = {"inline_keyboard": [otp_button]}

                    delivered_users = []
                    for owner_id in owners:
                        # Reward is for every delivered SMS/message, including N/A.
                        # The reward is shown at the end of the inbox message, not as an inline button.
                        reward = 0.0
                        try:
                            reward = get_otp_reward_for_user(num, owner_id, p.get("name"))
                        except Exception:
                            reward = float(bot_settings.get("otp_reward", 0.0) or 0.0)

                        reward_line = f"\n💰 <b>Reward: {reward:g} TK</b>" if reward > 0 else ""
                        inbox_msg = render_body_text(
                            f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {display_num} | 💬 {lang}\n"
                            f"📝 <b>Full Msg:</b> <code>{html.escape(msg_text)}</code>\n"
                            f"🔐 <b>OTP:</b> <code>{html.escape(otp)}</code>"
                            f"{reward_line}"
                        )

                        # User gets only the OTP/N/A copy button inline.
                        user_kb = {"inline_keyboard": [list(otp_button)]}

                        if safe_send(owner_id, inbox_msg, reply_markup=user_kb):
                            delivered_users.append(owner_id)
                            try:
                                credit_earning(owner_id, reward, "otp")
                                if db:
                                    increment_user_otp(owner_id)
                            except Exception as exc:
                                print(f"[KSI DELIVERY] reward/db update failed for {owner_id}: {exc}")

                    if not delivered_users:
                        # User delivery failed; do not consume the KSI record.
                        continue

                    # KSI IPRN uses the exact same visual group layout as the
                    # existing Bangla/MG OTP messages.
                    lang_code = str(lang or "#EN").upper()
                    if not lang_code.startswith("#"):
                        lang_code = "#" + lang_code
                    if len(lang_code) > 3:
                        lang_code = lang_code[:3]

                    group_msg = render_body_text(
                        f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {mask_number(display_num)} | 💬 {lang_code}"
                    )
                    group_ok = True
                    if bot_settings.get("fw_groups"):
                        for fw in bot_settings.get("fw_groups", []):
                            # OTP/N/A is always the first row, exactly like the
                            # other OTP providers. Custom group buttons remain below it.
                            fw_kb = [list(otp_button)]
                            temp_row = []
                            styles = ["danger", "success", "primary"]
                            for i, btn in enumerate(fw.get("buttons", [])):
                                if not btn.get("url"):
                                    continue
                                b_obj = {
                                    "text": btn.get("text", ""),
                                    "url": btn["url"],
                                    "style": styles[i % 3]
                                }
                                if btn.get("icon_custom_emoji_id"):
                                    b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                temp_row.append(b_obj)
                                if len(temp_row) == 2:
                                    fw_kb.append(temp_row)
                                    temp_row = []
                            if temp_row:
                                fw_kb.append(temp_row)
                            if not safe_send(fw.get("chat_id"), group_msg, reply_markup={"inline_keyboard": fw_kb}):
                                group_ok = False

                    # Record as consumed after successful user delivery.  Even if a
                    # group is misconfigured, the user's SMS must not be lost/repeated.
                    if is_ksi:
                        processed_ksi_messages.add(ksi_key)
                        if len(processed_ksi_messages) > 10000:
                            processed_ksi_messages = set(list(processed_ksi_messages)[-5000:])
                    else:
                        processed_otps.add(f"{num}_{otp}_{hash(msg_text)}")

                    current_time = time.time()
                    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                    recent_traffic.append({
                        "service": app_full_name, "iso": iso, "flag": char,
                        "number": num, "time": current_time, "source": "bot"
                    })
                    save_local_db()

        except Exception as exc:
            print(f"[KSI MONITOR] {type(exc).__name__}: {exc}")
        time.sleep(5)

# ==========================================
# Persistent User Activity Tracking
# ==========================================
def record_user_activity(user_id, activity_type, details=None, balance_before=None, balance_after=None):
    """Persist a durable per-user activity record and update user activity summary fields."""
    try:
        uid = int(user_id) if str(user_id).isdigit() else user_id
        now = time.time()
        payload = {
            "user_id": uid,
            "activity_type": str(activity_type),
            "details": details if isinstance(details, dict) else {"text": str(details)} if details is not None else {},
            "timestamp": now,
        }
        if balance_before is not None:
            payload["balance_before"] = float(balance_before)
        if balance_after is not None:
            payload["balance_after"] = float(balance_after)
        if db:
            activity_id = f"{int(now * 1000)}_{uuid.uuid4().hex[:8]}"
            db.collection("activity_logs").document(activity_id).set(payload)
            db.collection("users").document(str(user_id)).set({
                "user_id": uid,
                "activity_count": Increment(1),
                "last_activity_type": str(activity_type),
                "last_activity_at": now,
                "updated_at": now,
            }, merge=True)
        if user_id in user_cache:
            user_cache[user_id]["activity_count"] = int(user_cache[user_id].get("activity_count", 0) or 0) + 1
            user_cache[user_id]["last_activity_type"] = str(activity_type)
            user_cache[user_id]["last_activity_at"] = now
            user_cache[user_id]["updated_at"] = now
        return True
    except Exception as exc:
        print(f"[ACTIVITY LOG] {exc}")
        return False

# ==========================================
# Local User Management
# ==========================================
# 🌟 Local User Cache: avoid repeated local-database reads
user_cache = {}

def get_user(user_id):
    if user_id in user_cache: return user_cache[user_id]
    if not db: return {"user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0}
    
    doc_ref = db.collection('users').document(str(user_id))
    doc = doc_ref.get()
    if doc.exists: 
        data = doc.to_dict()
        changed = False
        defaults = {
            "user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0,
            "total_earnings": 0.0, "ref_income": 0.0, "ref_otp_commissions": 0,
            "total_withdrawals": 0.0, "total_deposits": 0.0, "total_numbers": 0,
            "activity_count": 0, "banned": False, "verified": False,
            "profile_name": "User", "username": "", "referred_by": None, "ref_paid": False,
            "created_at": time.time(), "updated_at": time.time(),
            "last_activity_at": time.time(), "last_activity_type": "profile_loaded"
        }
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
                changed = True
        if changed:
            try:
                doc_ref.set({k: data[k] for k in defaults}, merge=True)
            except Exception:
                pass
        user_cache[user_id] = data
        return data
    else:
        now = time.time()
        new_user = {
            "user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0,
            "total_earnings": 0.0, "ref_income": 0.0, "ref_otp_commissions": 0,
            "total_withdrawals": 0.0, "total_deposits": 0.0, "total_numbers": 0,
            "activity_count": 0, "banned": False, "verified": False,
            "profile_name": "User", "username": "", "referred_by": None, "ref_paid": False,
            "created_at": now, "updated_at": now, "last_activity_at": now,
            "last_activity_type": "user_created"
        }
        doc_ref.set(new_user)
        user_cache[user_id] = new_user
        record_user_activity(user_id, "user_created", {"source": "telegram"})
        return user_cache[user_id]

def update_balance(user_id, amount, reason="balance_update", activity_type="balance_change"):
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return False
    before = float(get_user(user_id).get("balance", 0.0) or 0.0)
    after = before + amount
    if user_id in user_cache:
        user_cache[user_id]["balance"] = after
    if db:
        try:
            doc_ref = db.collection('users').document(str(user_id))
            doc_ref.set({"user_id": user_id, "balance": Increment(amount), "updated_at": time.time()}, merge=True)
        except Exception as exc:
            print(f"[BALANCE UPDATE] {exc}")
    record_user_activity(user_id, activity_type, {
        "reason": reason, "amount": amount
    }, balance_before=before, balance_after=after)
    return True

def increment_user_otp(user_id):
    """Increment total OTP in DB and keep the in-memory profile cache synchronized."""
    try:
        if db:
            db.collection("users").document(str(user_id)).set(
                {"user_id": user_id, "total_otps": Increment(1)}, merge=True
            )
        u = user_cache.get(user_id)
        if u is not None:
            u["total_otps"] = int(u.get("total_otps", 0) or 0) + 1
        record_user_activity(user_id, "otp_received", {"count_increment": 1})
        return True
    except Exception as exc:
        print(f"[TOTAL OTP] {exc}")
        return False

def credit_earning(user_id, amount, earning_type="otp", trigger_referral=True):
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return
    if amount == 0:
        if earning_type == "otp" and trigger_referral:
            apply_referral_otp_commission(user_id)
        return
    update_balance(user_id, amount, reason=f"{earning_type}_earning", activity_type="earning")
    if db:
        try:
            db.collection("users").document(str(user_id)).set({"total_earnings": Increment(amount)}, merge=True)
        except Exception:
            pass
    if user_id in user_cache:
        user_cache[user_id]["total_earnings"] = user_cache[user_id].get("total_earnings", 0.0) + amount
    if earning_type == "otp" and trigger_referral:
        apply_referral_otp_commission(user_id)

def apply_referral_otp_commission(referred_user_id):
    try:
        if not bot_settings.get("refer_otp_commission_on", True):
            return 0.0
        commission = float(bot_settings.get("refer_otp_commission", 0.0) or 0.0)
        if commission <= 0:
            return 0.0
        referred = get_user(referred_user_id)
        inviter = referred.get("referred_by")
        if not inviter or str(inviter) == str(referred_user_id):
            return 0.0
        inviter = int(inviter)
        referrer = get_user(inviter)
        credit_earning(inviter, commission, earning_type="referral", trigger_referral=False)
        if db:
            db.collection("users").document(str(inviter)).set(
                {"ref_income": Increment(commission), "ref_otp_commissions": Increment(1)}, merge=True
            )
        if inviter in user_cache:
            user_cache[inviter]["ref_income"] = user_cache[inviter].get("ref_income", 0.0) + commission
            user_cache[inviter]["ref_otp_commissions"] = user_cache[inviter].get("ref_otp_commissions", 0) + 1
        record_user_activity(inviter, "referral_otp_commission", {
            "referred_user_id": referred_user_id, "commission": commission
        })
        return commission
    except Exception as exc:
        print(f"[REFERRAL COMMISSION] {exc}")
        return 0.0

def add_referral(inviter_id, new_user_id):
    try:
        if not db.collection('users').document(str(new_user_id)).get().exists:
            get_user(new_user_id)
        db.collection('users').document(str(new_user_id)).set(
            {"referred_by": inviter_id, "ref_paid": False}, merge=True
        )
    except Exception:
        pass

# ==========================================
# UI Keyboards & Menu Builders
# ==========================================
def get_cancel_kb():
    return {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}

def main_menu(user_id):
    rk = bot_settings.get("reply_keyboard_emojis", {})
    def rb(text, style):
        b = {"text": text, "style": style}
        emoji_id = rk.get(text)
        if emoji_id:
            b["icon_custom_emoji_id"] = str(emoji_id)
        return b
    kb = [
        [rb("Get Number", "primary"), rb("Live Traffic", "success")],
        [rb("Refer & Earn", "success"), rb("My profile", "primary")],
        [rb("Support", "danger")]
    ]
    if is_admin(user_id):
        kb.append([rb("Admin panel", "danger")])
    return {"keyboard": kb, "resize_keyboard": True}

def user_profile_keyboard():
    return {"inline_keyboard": [
        [{"text": "Withdraw", "icon_custom_emoji_id": "5352585194295564660", "callback_data": "profile_withdraw", "style": "success"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}

def get_user_profile_text(user_id):
    u = get_user(user_id)
    name = u.get("profile_name") or "User"
    username = u.get("username") or "Not set"
    balance = float(u.get("balance", 0) or 0)
    total_otp = int(u.get("total_otps", 0) or 0)
    total_ref = int(u.get("total_refers", 0) or 0)
    ref_income = float(u.get("ref_income", 0.0) or 0)
    username_value = f"@{html.escape(str(username).lstrip('@'))}" if username != 'Not set' else 'Not set'
    return render_body_text(
        f"{PEM['user']} <b>MY PROFILE</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"{PEM['user']} <b>Name:</b> {html.escape(str(name))}\n"
        f"{PEM['msg']} <b>Username:</b> {username_value}\n"
        f"{PEM['num']} <b>User ID:</b> <code>{user_id}</code>\n"
        f"{PEM['money']} <b>Balance:</b> {balance:g} ৳\n"
        f"{PEM['phone']} <b>Total OTP:</b> {total_otp}\n"
        f"{PEM['gift']} <b>Total Referred:</b> {total_ref}\n"
        f"{PEM['money']} <b>Total Earnings:</b> {float(u.get("total_earnings", 0) or 0):g} ৳\n"
        f"{PEM['money']} <b>Referral Income:</b> {ref_income:g} ৳\n"
        f"━━━━━━━━━━━━━━"
    )

def get_admin_text():
    users_count = len(all_known_users) # 🌟 Zero Cost User Count!
    total_files = len(number_batches)
    available_nums = sum(len(b["numbers"]) for b in number_batches.values())

    txt = f"""
{PEM['admin']} <b>ADMIN CONTROL PANEL</b> {PEM['admin']}
━━━━━━━━━━━━━━━━━━

{PEM['graph']} <b>DATABASE OVERVIEW</b>
— — — — — — — — — —
{PEM['user']} Users      » {users_count}
{PEM['file']} Files      » {total_files}
{PEM['num']} Numbers    » {total_uploaded_stats}
{PEM['ok']} Assigned   » {total_assigned_stats}
{PEM['rocket']} Available  » {available_nums}

{PEM['graph']} <b>STOCK LEVEL</b>
— — — — — — — — — —
[██████░░░░░░░░░] {available_nums} free
"""
    return render_body_text(txt)

def send_file_document(chat_id, filename, file_bytes):
    url = f"{BASE_URL}/sendDocument"
    try:
        requests.post(url, data={"chat_id": chat_id},
                      files={"document": (filename, file_bytes, "application/zip")},
                      timeout=30)
        return True
    except:
        return False

def create_database_backup():
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as z:
        for filename in ["bot_data.json", "local_db.json", "users_list.json"]:
            if os.path.exists(filename):
                z.write(filename, arcname=filename)
    mem.seek(0)
    return mem.getvalue()

def database_keyboard():
    return {"inline_keyboard": [
        [{"text": "Download Database", "icon_custom_emoji_id": "5352721946054268944", "callback_data": "db_download", "style": "success"}],
        [{"text": "Upload Database", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "db_upload", "style": "primary"}],
        [{"text": "Clear All Data", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "db_clear_confirm", "style": "danger"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}]
    ]}

def reset_all_database_data():
    global db, bot_settings, number_batches, used_numbers_list
    global total_uploaded_stats, total_assigned_stats, recent_traffic
    global stex_assigned_numbers, voltx_assigned_numbers, zenex_assigned_numbers
    global processed_otps, assigned_number_rates, all_known_users
    try:
        for filename in ["bot_data.json", "local_db.json", "users_list.json"]:
            if os.path.exists(filename):
                os.remove(filename)
    except:
        pass
    number_batches = {}
    used_numbers_list = []
    total_uploaded_stats = 0
    total_assigned_stats = 0
    recent_traffic = []
    stex_assigned_numbers = {}
    voltx_assigned_numbers = {}
    zenex_assigned_numbers = {}
    processed_otps = set()
    assigned_number_rates = {}
    all_known_users = set()
    user_cache.clear()
    pending_withdrawals.clear()
    # Recreate the local store and restore default settings.
    db = LocalStore()
    bot_settings.clear()
    bot_settings.update({
        "admins": [OWNER_ID], "special_users": [], "panels": [], "fw_groups": [],
        "otp_link": "https://t.me/your_otp_group", "withdraw_on": True,
        "min_withdraw": 30.0, "otp_reward": 0.1,
        "panel_otp_rewards": {},
            "cooldown": 10, "num_req": 3, "num_share": 1,
        "support_link": "https://t.me/your_support", "support_button_name": "Support", "w_methods": ["bKash", "Nagad"],
        "fj_on": False, "fj_channels": [], "console_otp": False, "stex_keys": [], "voltx_keys": [], "zenex_keys": [],
        "fastx_keys": [], "fastx_enabled": True, "fastx_auto": False, "fastx_services": {}, "fastx_search_countries": [],
        "fastx_hidden_services": [], "fastx_hidden_countries": [], "fastx_hidden_ranges": [],
        "search_countries": [], "stex_services": {}, "voltx_services": {}, "zenex_services": {},
        "premium_flags": DEFAULT_PREMIUM_FLAGS.copy() if "DEFAULT_PREMIUM_FLAGS" in globals() else {},
        "premium_apps": DEFAULT_PREMIUM_APPS.copy() if "DEFAULT_PREMIUM_APPS" in globals() else {},
        "mask_emoji": {"id": "", "char": "DXA"},
        "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy()
    })
    save_db()

def support_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "EDIT SUPPORT LINK", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "support_edit_link", "style": "primary"}],
        [{"text": "EDIT SUPPORT BUTTON NAME", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "support_edit_name", "style": "success"}],
        [{"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def support_management_text():
    link = bot_settings.get("support_link", "") or "Not set"
    name = bot_settings.get("support_button_name", "Support")
    return render_body_text(
        f"{PEM['msg']} <b>SUPPORT MANAGEMENT</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Button Name:</b> {html.escape(str(name))}\n"
        f"<b>Support Link:</b> <code>{html.escape(str(link))}</code>\n\n"
        f"<i>Manage only the Support Center contact button name and its support link.</i>"
    )

def support_user_keyboard():
    kb = []
    link = bot_settings.get("support_link", "") or ""
    if link:
        kb.append([{"text": str(bot_settings.get("support_button_name", "CONTACT SUPPORT"))[:64], "icon_custom_emoji_id": "5337302974806922068", "url": link, "style": "success"}])
    kb.append([{"text": "SEND MESSAGE", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "support_start", "style": "primary"}])
    kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
    return {"inline_keyboard": kb}

def support_ticket_keyboard(user_id):
    return {"inline_keyboard": [
        [{"text": "REPLY", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"support_reply_{user_id}", "style": "success"},
         {"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"support_close_{user_id}", "style": "danger"}]
    ]}

def admin_panel_keyboard():
    return {"inline_keyboard": [
        [{"text": "LEADER BOARD SYSTEM", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "lb_main", "style": "success"}],
        [{"text": "Upload Number", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "upload_num", "style": "primary"},
         {"text": "Delete files", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "delete_files", "style": "danger"}],
        [{"text": "Broadcast", "icon_custom_emoji_id": "5789428375261023681", "callback_data": "broadcast_msg", "style": "success"}],
        [{"text": "System", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "system_settings", "style": "primary"}],
        [{"text": "Database", "icon_custom_emoji_id": "5352721946054268944", "callback_data": "database_menu", "style": "danger"}],
        [{"text": "Used number", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "show_used", "style": "success"},
         {"text": "Unused number", "icon_custom_emoji_id": "5352597830089347330", "callback_data": "show_unused", "style": "success"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}

def system_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Force Join System", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "manage_fj", "style": "primary"},
         {"text": "Admin Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "manage_admins", "style": "danger"}],
        [{"text": "Support Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "support_management", "style": "success"}],
        [{"text": "Special User", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "special_users", "style": "primary"}],
        [{"text": "Console OTP", "icon_custom_emoji_id": "5203993413346680064", "callback_data": "console_otp_toggle", "style": "success" if bot_settings.get("console_otp", False) else "danger"}],
        [{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "callback_data": "manage_otp_groups", "style": "danger"},
         {"text": "User Management", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_management", "style": "primary"}], 
        [{"text": "Panel MANAGEMENT", "icon_custom_emoji_id": "5336879280578138635", "callback_data": "manage_panels", "style": "danger"},
         {"text": "Subscription", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "dummy_alert", "style": "success"}],
        [{"text": "DXA Control", "icon_custom_emoji_id": "5193100774988617665", "callback_data": "dxa_control", "style": "primary"},
         {"text": "Premium Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "manage_emojis", "style": "success"}],
        [{"text": "Menu Design", "icon_custom_emoji_id": "5190751148704833975", "callback_data": "menu_design_list", "style": "primary"},
         {"text": "Test", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "test_message_flow", "style": "primary"}], 
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def refer_otp_reward_text():
    status = "🟢 ON" if bot_settings.get("refer_otp_commission_on", True) else "🔴 OFF"
    amount = float(bot_settings.get("refer_otp_commission", 0.0) or 0.0)
    return render_body_text(
        "━━━━━━━━━━━━━━━━━━\n🎁 <b>REFER OTP REWARD</b>\n━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Commission Per OTP:</b> {amount:g} ৳\n"
        f"📡 <b>Status:</b> {status}\n\n"
        "A referrer earns the configured commission for every OTP received by a referred member.\n"
        "This is the main referral reward system.\n"
        "━━━━━━━━━━━━━━━━━━"
    )

def refer_otp_reward_keyboard():
    status_on = bot_settings.get("refer_otp_commission_on", True)
    return {"inline_keyboard": [
        [{"text": "Set OTP Commission", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "refer_set_commission", "style": "primary"}],
        [{"text": "Commission ON" if not status_on else "Commission OFF",
          "icon_custom_emoji_id": "5420155432272438703", "callback_data": "refer_toggle",
          "style": "success" if not status_on else "danger"}],
        [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def build_all_user_list(page=0):
    try: page = max(0, int(page))
    except Exception: page = 0
    users = []
    if db:
        try:
            for doc in db.collection("users").stream():
                d = doc.to_dict() or {}
                d["_uid"] = doc.id
                users.append(d)
        except Exception as exc:
            print(f"[ALL USERS] database stream error: {exc}")
    # Ensure locally known users are also visible if a database read is delayed.
    seen = {str(d.get("_uid", "")) for d in users}
    for uid in list(all_known_users):
        if str(uid) in seen:
            continue
        try:
            d = get_user(int(uid))
            d = dict(d or {})
            d["_uid"] = str(uid)
            users.append(d)
        except Exception:
            pass
    def uid_num(d):
        v = str(d.get("_uid", d.get("user_id", ""))).strip()
        return int(v) if v.isdigit() else 0
    users.sort(key=uid_num, reverse=True)
    per_page = 5
    total = len(users)
    pages = max(1, (total + per_page - 1) // per_page)
    page = min(page, pages - 1)
    chunk = users[page * per_page:(page + 1) * per_page]
    body = [
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "👥 <b>ALL USER LIST</b>",
        f"📊 <b>Total Users:</b> {total}  •  <b>Page:</b> {page + 1}/{pages}",
        "━━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    if not chunk:
        body.append("📭 <i>No users found.</i>")
    for idx, d in enumerate(chunk, page * per_page + 1):
        uid = d.get("_uid", d.get("user_id", ""))
        name = d.get("profile_name") or "User"
        username = d.get("username") or "Not set"
        uname = f"@{str(username).lstrip('@')}" if username != "Not set" else "Not set"
        bal = float(d.get("balance", 0) or 0)
        otp = int(d.get("total_otps", 0) or 0)
        refs = int(d.get("total_refers", 0) or 0)
        earn = float(d.get("total_earnings", d.get("lifetime_income", 0)) or 0)
        body.append(
            f"\n<b>{idx}. {html.escape(str(name))}</b>\n"
            f"  👤 {html.escape(uname)}\n"
            f"  🆔 <code>{html.escape(str(uid))}</code>\n"
            f"  💰 Balance: <b>{bal:g} ৳</b>\n"
            f"  🔐 Total OTP: <b>{otp}</b>  •  🤝 Refer: <b>{refs}</b>\n"
            f"  💎 Lifetime Income: <b>{earn:g} ৳</b>"
        )
    body.append("\n━━━━━━━━━━━━━━━━━━━━━━━━")
    nav = []
    if page > 0: nav.append({"text": "◀️ Previous", "callback_data": f"all_users_{page-1}", "style": "primary"})
    if page < pages - 1: nav.append({"text": "Next ▶️", "callback_data": f"all_users_{page+1}", "style": "primary"})
    kb = []
    if nav: kb.append(nav)
    kb.append([{"text": "🔄 Refresh", "callback_data": f"all_users_{page}", "style": "success"},
               {"text": "↩️ Back", "callback_data": "user_management", "style": "danger"}])
    return render_body_text("\n".join(body)), {"inline_keyboard": kb}

def get_user_management_text():
    # 🌟 Fast & Free User Management Stats!
    total = len(all_known_users)
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txt = f"""➖➖➖➖➖➖➖➖
《 👋 USER VIEW 》
➖➖➖➖➖➖➖➖
📊 LIVE STATISTICS:
➖➖➖➖➖➖➖➖
🫂 TOTAL USERS: {total}
✅ VERIFIED USERS: (Hidden to save DB Cost)
🚫 BANNED USERS: (Hidden to save DB Cost)
➖➖➖➖➖➖➖➖
⌛ UPDATED: {now_str}"""
    return render_body_text(txt)

def user_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "All User List", "icon_custom_emoji_id": "5352861489541714456", "callback_data": "all_users_0", "style": "success"}],
        [{"text": "Manage Balance", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "um_manage_balance", "style": "primary"},
         {"text": "Ban/Unban User", "icon_custom_emoji_id": "5334807341109908955", "callback_data": "um_ban_unban", "style": "danger"}],
        [{"text": "User Profile", "icon_custom_emoji_id": "5352861489541714456", "callback_data": "um_user_profile", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def reply_keyboard_emoji_settings_keyboard():
    buttons = [
        ("Get Number", "primary"), ("Live Traffic", "success"),
        ("Refer & Earn", "success"), ("My profile", "primary"),
        ("Support", "danger"), ("Admin panel", "danger")
    ]
    rk = bot_settings.get("reply_keyboard_emojis", {})
    rows = []
    for text, style in buttons:
        eid = rk.get(text, "Not set")
        label = f"{text} • {eid}"
        rows.append([{"text": label, "icon_custom_emoji_id": str(eid) if eid != "Not set" else "5420130255174145507", "callback_data": "rkemoji_set:" + text, "style": style}])
    rows.append([{"text": "Back to Menu Design", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "primary"}])
    return {"inline_keyboard": rows}

def menu_design_list_keyboard():
    return {"inline_keyboard": [
        [{"text": "Edit /start Menu", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "md_edit_start", "style": "primary"}],
        [{"text": "Edit GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "md_edit_get_number", "style": "success"},
         {"text": "Edit NEW NUMBER", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "md_edit_new_number", "style": "success"}],
        [{"text": "Edit Select Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "md_edit_select_country", "style": "primary"}],
        [{"text": "Edit TRAFFIC", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "md_edit_traffic", "style": "primary"},
         {"text": "Edit Refer", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "md_edit_refer", "style": "primary"}],
        [{"text": "Reply Keyboard Emoji", "icon_custom_emoji_id": "6298790803414189709", "callback_data": "reply_keyboard_emoji_settings", "style": "success"}],
        [{"text": "Reset Defaults", "icon_custom_emoji_id": "5192812028632274956", "callback_data": "md_reset_defaults", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_edit_options_keyboard(menu_key):
    return {"inline_keyboard": [
        [{"text": "Edit Body (Text)", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"md_text_{menu_key}", "style": "primary"}],
        [{"text": "Edit Inline Buttons", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"md_btns_{menu_key}", "style": "success"}],
        [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
    ]}

def menu_buttons_list_keyboard(menu_key):
    kb = []
    btns = bot_settings["custom_messages"].get(menu_key, {}).get("buttons", [])
    for idx, btn in enumerate(btns):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"md_delbtn_{menu_key}_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"md_addbtn_{menu_key}", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{menu_key}", "style": "primary"}])
    return {"inline_keyboard": kb}

def emoji_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Upload Flags (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_flags_txt", "style": "primary"},
         {"text": "Download Flags", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_flags_txt", "style": "success"}],
        [{"text": "Upload Services (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_apps_txt", "style": "primary"},
         {"text": "Download Services", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_apps_txt", "style": "success"}],
        [{"text": "Delete All Flags", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "del_all_flags", "style": "danger"},
         {"text": "Add Single Emoji", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_single_emoji", "style": "success"}],
        [{"text": "Set Number Mask Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "set_mask_emoji", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def fj_settings_keyboard():
    status_text = 'ON' if bot_settings['fj_on'] else 'OFF'
    status_icon = "5352694861990501856" if bot_settings['fj_on'] else "5318840353510408444"
    kb = [[{"text": f"STATUS: {status_text}", "icon_custom_emoji_id": status_icon, "callback_data": "toggle_fj", "style": "primary"}]]
    for idx, ch in enumerate(bot_settings["fj_channels"]):
        kb.append([{"text": f"Delete: {ch}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fj_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Channel", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fj", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def admin_settings_keyboard():
    kb = []
    for idx, adm in enumerate(bot_settings["admins"]):
        text_btn = f"Owner: {adm}" if adm == OWNER_ID else f"Delete: {adm}"
        icon_id = "5353032893096567467" if adm == OWNER_ID else "5420130255174145507"
        cb_data = "ignore" if adm == OWNER_ID else f"del_adm_{idx}"
        kb.append([{"text": text_btn, "icon_custom_emoji_id": icon_id, "callback_data": cb_data, "style": "danger" if adm != OWNER_ID else "primary"}])
    kb.append([{"text": "Add Admin", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_adm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def otp_groups_list_keyboard():
    kb = [[{"text": "Edit OTP Button Link", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "edit_otp_link", "style": "primary"}]]
    for idx, fg in enumerate(bot_settings["fw_groups"]):
        kb.append([{"text": f"Group: {fg['chat_id']}", "icon_custom_emoji_id": "5193063022226086560", "callback_data": f"manage_fw_{idx}", "style": "primary"}])
    kb.append([{"text": "Add Forward Group", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fw", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}])
    return {"inline_keyboard": kb}

def stex_control_keyboard():
    auto_status = "ON" if bot_settings.get("stex_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add StexSMS Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_stex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_stex_keys", "style": "danger"}],
        [{"text": "Manage StexSMS Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_stex_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_stex_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def zenex_control_keyboard():
    auto_status = "ON" if bot_settings.get("zenex_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add Zenex Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_zenex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_zenex_keys", "style": "danger"}],
        [{"text": "Manage Zenex Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_zenex_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_zenex_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "zenex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def voltx_control_keyboard():
    auto_status = "ON" if bot_settings.get("voltx_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add Voltx Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_voltx_keys", "style": "danger"}],
        [{"text": "Manage Voltx Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_voltx_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_voltx_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def fastx_control_keyboard():
    auto_status = "ON" if bot_settings.get("fastx_auto", False) else "OFF"
    auto_emoji = "5352694861990501856" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add Fast X Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fastx_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_fastx_keys", "style": "danger"}],
        [{"text": "Manage Fast X Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_fastx_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_fastx_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "fastx_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def specific_fw_group_keyboard(idx):
    group = bot_settings["fw_groups"][idx]
    kb = []
    for b_idx, btn in enumerate(group.get("buttons", [])):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fwbtn_{idx}_{b_idx}", "style": "danger"}])
    
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"add_fwbtn_{idx}", "style": "success"}])
    kb.append([{"text": "Delete Entire Group", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_fw_{idx}", "style": "danger"}])
    kb.append([{"text": "Back to Groups", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "primary"}])
    return {"inline_keyboard": kb}

def otp_reward_panel_keyboard():
    """Select one of the built-in Bangla panels for its own OTP reward rates."""
    panel_defs = [("Voltx", "voltx"), ("StexSMS", "stexsms"), ("Zenex", "zenex"), ("Fast X", "fastx")]
    kb = []
    for i in range(0, len(panel_defs), 2):
        row = []
        for name, key in panel_defs[i:i+2]:
            row.append({"text": name, "icon_custom_emoji_id": "5190576863226933563", "callback_data": f"otp_reward_panel:{key}", "style": "primary"})
        kb.append(row)
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "danger"}])
    return {"inline_keyboard": kb}

def otp_reward_panel_manage_keyboard(panel_key):
    rates = bot_settings.setdefault("panel_otp_rewards", {}).setdefault(
        panel_key, {"user": float(bot_settings.get("otp_reward", 0.0)), "special": float(bot_settings.get("otp_reward", 0.0))}
    )
    return {"inline_keyboard": [
        [{"text": f"Set User Reward ({rates.get('user', 0)})", "icon_custom_emoji_id": "5420396762189831222", "callback_data": f"set_panel_reward:{panel_key}:user", "style": "success"}],
        [{"text": f"Set Special User ({rates.get('special', 0)})", "icon_custom_emoji_id": "5420396762189831222", "callback_data": f"set_panel_reward:{panel_key}:special", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_otp_r", "style": "danger"}]
    ]}

def otp_reward_panel_name(panel_key):
    return {"voltx": "Voltx", "stexsms": "StexSMS", "zenex": "Zenex", "fastx": "Fast X"}.get(panel_key, panel_key)

def dxa_control_keyboard():
    w_status = "ON" if bot_settings["withdraw_on"] else "OFF"
    pending_count = len(pending_withdrawals)
    return {"inline_keyboard": [
        [{"text": f"WITHDRAW: {w_status}", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "dxa_toggle_w", "style": "primary"}],
        [{"text": f"MIN WITHDRAW: {bot_settings['min_withdraw']}", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "dxa_min_w", "style": "success"},
         {"text": f"OTP REWARD: {bot_settings['otp_reward']}", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "dxa_otp_r", "style": "primary"}],
        [{"text": "REFER OTP REWARD", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "refer_management", "style": "success"}],
        [{"text": f"COOLDOWN: {bot_settings['cooldown']}s", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "dxa_cool", "style": "primary"}],
        [{"text": f"NUM/REQ: {bot_settings['num_req']}", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "dxa_num_req", "style": "success"},
         {"text": f"NUM/SHARE: {bot_settings['num_share']}", "icon_custom_emoji_id": "5352862640592949843", "callback_data": "dxa_num_share", "style": "primary"}],
        [{"text": "W. METHODS", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "manage_w_methods", "style": "primary"}],
        [{"text": f"W. REQUEST ({pending_count})", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "withdraw_requests", "style": "success"},
         {"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def withdrawal_request_keyboard(req_id):
    # Keep the action keyboard Telegram-Bot-API compatible: callback buttons
    # must not depend on optional button icon/style fields.
    return {"inline_keyboard": [[
        {"text": "APPROVE", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"wapp_{req_id}", "style": "success"},
        {"text": "REJECT", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"wrej_{req_id}", "style": "danger"}
    ]]}

def withdrawal_request_text(req_id, req_data):
    uid = req_data.get("user_id")
    return render_body_text(
        f"{PEM['money']} <b>NEW WITHDRAWAL REQUEST</b>\n\n"
        f"{PEM['user']} <b>USER:</b> <a href='tg://user?id={uid}'>{html.escape(str(req_data.get('full_name', uid)))}</a>\n"
        f"{PEM['money']} <b>AMOUNT:</b> {req_data.get('amount', 0)} TK\n"
        f"{PEM['phone']} <b>NUMBER:</b> <code>{html.escape(str(req_data.get('number', '')))}</code>\n"
        f"{PEM['admin']} <b>METHOD:</b> {html.escape(str(req_data.get('method', '')))}\n"
        f"{PEM['lock']} <b>STATUS:</b> PENDING\n"
        f"<b>REQUEST:</b> <code>{html.escape(str(req_id))}</code>"
    )

def w_methods_keyboard():
    kb = []
    for idx, m in enumerate(bot_settings["w_methods"]):
        kb.append([{"text": f"Delete: {m}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_wm_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Method", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_wm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "primary"}])
    return {"inline_keyboard": kb}

def typed_panels_list_keyboard(p_type):
    kb = []
    for idx, p in enumerate(bot_settings["panels"]):
        if p.get("type", "API Panel") != p_type:
            continue
        action_text = f"Turn OFF {p['name']}" if p['status'] == 'ON' else f"Turn ON {p['name']}"
        action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
        icon_id = "5420155432272438703"
        kb.append([
            {"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"},
            {"text": f"{p['name']}", "icon_custom_emoji_id": icon_id, "callback_data": f"conf_pnl_{idx}", "style": "primary"}
        ])
    add_cb = "add_api_panel" if p_type == "API Panel" else "add_cpt_panel"
    kb.append([{"text": "Add New Provider", "icon_custom_emoji_id": "5420323438508155202", "callback_data": add_cb, "style": "success"}])
    kb.append([{"text": "Delete Provider", "icon_custom_emoji_id": "5336944168944047463", "callback_data": f"list_del_{'api' if p_type=='API Panel' else 'cpt'}", "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
    return {"inline_keyboard": kb}


def _legacy_panel_status(name):
    key = {
        "Voltx": "voltx_auto",
        "StexSMS": "stex_auto",
        "Zenex": "zenex_auto",
    }.get(name)
    return bool(bot_settings.get(key, False)) if key else False


def panel_management_keyboard():
    """Panel Management with every provider arranged strictly two per row."""
    # Keep the original 2-panels-per-row layout.
    panels = [
        ("StexSMS", "legacy_stex", _legacy_panel_status("StexSMS")),
        ("Voltx", "legacy_voltx", _legacy_panel_status("Voltx")),
        ("Zenex", "legacy_zenex", _legacy_panel_status("Zenex")),
        ("Fast X", "fastx_control", bool(bot_settings.get("fastx_enabled", False) and bot_settings.get("fastx_keys"))),
    ]
    ksi_idx = next((i for i, p in enumerate(bot_settings.get("panels", []))
                    if str(p.get("name", "")).strip().lower() == "ksi iprn"), None)
    if ksi_idx is not None:
        panels.append(("KSI IPRN", f"conf_pnl_{ksi_idx}",
                       bot_settings["panels"][ksi_idx].get("status") == "ON"))

    default_names = {"voltx", "stexsms", "stetx", "zenex", "ksi iprn", "fast x"}
    for idx, p in enumerate(bot_settings.get("panels", [])):
        name = str(p.get("name", "")).strip()
        if not name or name.lower() in default_names:
            continue
        panels.append((name, f"conf_pnl_{idx}", p.get("status") == "ON"))

    kb = []
    for i in range(0, len(panels), 2):
        row = []
        for name, callback, active in panels[i:i+2]:
            row.append({
                "text": name,
                "icon_custom_emoji_id": "5352694861990501856" if active else "5420130255174145507",
                "callback_data": callback,
                "style": "success" if active else "danger"
            })
        kb.append(row)
    kb.append([{"text": "Add More Panel", "icon_custom_emoji_id": "5420323438508155202",
                "callback_data": "add_more_panel", "style": "success"}])
    kb.append([{"text": "Delete Panel", "icon_custom_emoji_id": "5422557736330106570",
                "callback_data": "delete_panel_type", "style": "danger"}])
    return {"inline_keyboard": kb}


def panel_type_actions_keyboard():
    return {"inline_keyboard": [
        [{"text": "API Panel", "icon_custom_emoji_id": "5336972142066047577",
          "callback_data": "panel_type_api", "style": "primary"},
         {"text": "Auto Captcha Panel", "icon_custom_emoji_id": "5353022963132174959",
          "callback_data": "panel_type_cpt", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176",
          "callback_data": "manage_panels", "style": "danger"}]
    ]}


def panel_type_manage_keyboard(p_type):
    if p_type == "API Panel":
        add_cb, del_cb = "add_api_panel", "delete_api_panel"
        icon = "5336972142066047577"
    else:
        add_cb, del_cb = "add_cpt_panel", "delete_cpt_panel"
        icon = "5353022963132174959"
    return {"inline_keyboard": [
        [{"text": "Add Panel", "icon_custom_emoji_id": "5420323438508155202",
          "callback_data": add_cb, "style": "success"}],
        [{"text": "Delete Panel", "icon_custom_emoji_id": "5422557736330106570",
          "callback_data": del_cb, "style": "danger"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176",
          "callback_data": "add_more_panel", "style": "primary"}]
    ]}

def panel_config_keyboard(idx):
    p = bot_settings["panels"][idx]
    
    kb = []
    action_text = "Turn OFF" if p['status'] == 'ON' else "Turn ON"
    action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
    kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])
    
    if p["type"] != "Auto Captcha Panel":
        rec_count_text = "All (Unlimited)" if p.get('records', 0) == 0 else str(p.get('records'))
        kb.append([{"text": "Set API URL", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_api_{idx}", "style": "primary"}])
        kb.append([{"text": "Set Token", "icon_custom_emoji_id": "5353022963132174959", "callback_data": f"set_p_tok_{idx}", "style": "primary"}])
        kb.append([{"text": "🌐 Full API (URL+Token)", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_fapi_{idx}", "style": "primary"}])
        kb.append([{"text": f"Set Records Count: {rec_count_text}", "icon_custom_emoji_id": "5192739271886282680", "callback_data": f"set_p_rec_{idx}", "style": "primary"}])
        
    kb.append([{"text": "Test Connection", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
        
    # From provider configuration, always return directly to the main Panel Management page.
    back_data = "manage_panels"
    kb.append([{"text": "Back to Providers", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_data, "style": "danger"}])
    return {"inline_keyboard": kb}

def build_traffic_ui():
    """Show OTP traffic grouped by service/country using the compact premium layout."""
    global recent_traffic
    current_time = time.time()
    try:
        window_minutes = max(1, int(bot_settings.get("traffic_window_minutes", 30)))
    except Exception:
        window_minutes = 30
    window = window_minutes * 60

    recent_traffic = [
        t for t in recent_traffic
        if current_time - t.get("time", 0) <= window
    ]

    # Traffic source modes:
    # off  = only bot-originated OTP traffic
    # on   = only Console/Auto traffic
    # all  = both sources
    mode = str(bot_settings.get("console_traffic_mode", "on")).lower()
    if mode not in ("off", "on", "all"):
        # Backward compatibility with the old boolean setting.
        mode = "on" if bot_settings.get("console_traffic", True) else "off"
    if mode == "off":
        recent_traffic = [t for t in recent_traffic if t.get("source", "bot") != "console"]
    elif mode == "on":
        recent_traffic = [t for t in recent_traffic if t.get("source", "bot") == "console"]
    # mode == all: keep both sources

    stats = {}
    for t in recent_traffic:
        srv = t.get("service", "Unknown") or "Unknown"
        iso = t.get("iso", "XX") or "XX"
        flag = t.get("flag", "🌍")
        stats.setdefault(srv, {})
        stats[srv].setdefault(iso, {"count": 0, "flag": flag})
        stats[srv][iso]["count"] += 1

    traffic_emoji = '<tg-emoji emoji-id="5203993413346680064">📊</tg-emoji>'
    txt = f"{traffic_emoji} <b>TRAFFIC</b>\n\n"

    if not stats:
        txt += f"<i>No OTP received in the last {window_minutes} minutes.</i>\n"
        return render_body_text(txt), None

    srv_totals = []
    for srv, countries in stats.items():
        total = sum(c["count"] for c in countries.values())
        srv_totals.append((srv, total, countries))
    srv_totals.sort(key=lambda x: x[1], reverse=True)

    for index, (srv, total, countries) in enumerate(srv_totals):
        app_full_name, prem_app_html = get_service_info_html(srv)
        txt += f"{prem_app_html} <b>{html.escape(app_full_name.upper())}</b>\n"

        c_list = sorted(countries.items(), key=lambda x: x[1]["count"], reverse=True)
        max_count = c_list[0][1]["count"] if c_list else 0

        for iso, c_data in c_list:
            count = c_data["count"]
            prem_flag_html = get_flag_info_html(iso)
            c_name = iso
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    c_name = fdata.get("name", iso)
                    break

            ratio = (count / max_count) if max_count else 0
            if ratio >= 0.60:
                status_emoji = '<tg-emoji emoji-id="6113685078825505075">🟢</tg-emoji>'
            elif ratio >= 0.30:
                status_emoji = '<tg-emoji emoji-id="5350512473143273043">🟡</tg-emoji>'
            else:
                status_emoji = '<tg-emoji emoji-id="5215313353706057331">🔴</tg-emoji>'

            txt += (
                f"│ {prem_flag_html} <b>{html.escape(str(c_name).upper())}</b>"
                f"    <b>{count}</b> {status_emoji}\n"
            )

        # Premium-looking separator after every service.
        txt += "└────────────────────\n"
        if index < len(srv_totals) - 1:
            txt += "\n"

    now = datetime.now().strftime("%I:%M %p")
    txt += f'\n<tg-emoji emoji-id="5336983442125001376">🕒</tg-emoji> <i>Updated {now} • Last {window_minutes} minutes</i>\n'

    # Traffic is intentionally display-only: no inline buttons.
    return render_body_text(txt), None

# ==========================================
# Referral Join + Notification Helper
# ==========================================
def register_referral_from_start(user_id, start_text):
    """Save the inviter from a referral deep-link even if the user record already exists."""
    try:
        if not start_text or not start_text.startswith("/start") or not db:
            return
        parts = start_text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip().isdigit():
            return
        inviter = int(parts[1].strip())
        if inviter == user_id:
            return
        current = get_user(user_id)
        # Never overwrite an already recorded inviter.
        if current.get("referred_by"):
            return
        if not db.collection("users").document(str(inviter)).get().exists:
            return
        db.collection("users").document(str(user_id)).set(
            {"referred_by": inviter, "ref_paid": False}, merge=True
        )
        current["referred_by"] = inviter
        current["ref_paid"] = False
        user_cache[user_id] = current
    except Exception as exc:
        print(f"[REFERRAL SAVE] {exc}")

def process_referral_join(user_id, msg=None):
    """Count a referral once and notify the referrer with the joined username."""
    try:
        if not db:
            return False
        doc = db.collection("users").document(str(user_id)).get()
        if not doc.exists:
            return False
        u = doc.to_dict() or {}
        inviter = u.get("referred_by")
        if not inviter or u.get("ref_paid"):
            return False
        inviter = int(inviter)
        if inviter == user_id:
            return False

        # Refresh the joined user's Telegram identity before notifying.
        frm = (msg or {}).get("from", {})
        username = (frm.get("username") or u.get("username") or "").strip().lstrip("@")
        full_name = " ".join([x for x in [frm.get("first_name", ""), frm.get("last_name", "")] if x]).strip()
        if username or full_name:
            updates = {}
            if username: updates["username"] = username
            if full_name: updates["profile_name"] = full_name
            if updates:
                db.collection("users").document(str(user_id)).set(updates, merge=True)
                u.update(updates)
                user_cache[user_id] = u

        # Atomic-ish guard: mark first, then notify. This prevents duplicate notifications.
        db.collection("users").document(str(user_id)).set({"ref_paid": True}, merge=True)
        db.collection("users").document(str(inviter)).set({"total_refers": Increment(1), "updated_at": time.time()}, merge=True)
        if inviter in user_cache:
            user_cache[inviter]["total_refers"] = user_cache[inviter].get("total_refers", 0) + 1
        record_user_activity(inviter, "referral_joined", {
            "referred_user_id": user_id, "username": username or "", "name": full_name or ""
        })
        record_user_activity(user_id, "joined_via_referral", {"referrer_id": inviter})

        joined_identity = f"@{html.escape(username)}" if username else html.escape(full_name or "User")
        ref_msg = (
            f"🎉 <b>Congratulations {joined_identity} joined with your refer link.</b>\n\n"
            f"👤 <b>User ID:</b> <code>{user_id}</code>\n"
            f"💰 <i>OTP commission will be paid when this member receives an OTP.</i>"
        )
        result = send_message(inviter, render_body_text(ref_msg))
        if not result or result.get("ok") is not True:
            print(f"[REFERRAL NOTIFY] failed for inviter {inviter}: {result}")
        return True
    except Exception as exc:
        print(f"[REFERRAL JOIN] {exc}")
        return False

# ==========================================
# Message Handler
# ==========================================
def handle_message(msg):
    global total_uploaded_stats
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")
    
    if chat_type != "private":
        return
        
    text = msg.get("text", "")
    register_user_local(chat_id) # 🌟 Save User locally for Free Broadcasts!
    try:
        frm = msg.get("from", {})
        profile_name = " ".join([x for x in [frm.get("first_name", ""), frm.get("last_name", "")] if x]).strip() or "User"
        username = frm.get("username", "")
        u = get_user(chat_id)
        if db and (u.get("profile_name") != profile_name or u.get("username", "") != username):
            db.collection("users").document(str(chat_id)).set({"profile_name": profile_name, "username": username}, merge=True)
            u.update({"profile_name": profile_name, "username": username})
            user_cache[chat_id] = u
    except:
        pass

    if is_user_banned(chat_id):
        send_message(chat_id, render_body_text("🚫 <b>You are banned from using this bot!</b>\nIf you think this is a mistake, please contact support."))
        return
    
    # --- REFERRAL FIX: Save inviter BEFORE Force Join ---
    if text.startswith("/start"):
        register_referral_from_start(chat_id, text)
    if not check_force_join(chat_id):
        send_force_join_msg(chat_id)
        return
        
    MAIN_MENU_CMDS = ["Get Number", "Live Traffic", "Refer & Earn", "My profile", "Support", "Admin panel", "GET NUMBER", "LIVE TRAFFIC", "REFER & EARN", "WITHDRAWAL", "SUPPORT", "Admin Panel", "Search Number", "2FA ONLINE"]
    
    is_main_cmd = False
    if text in MAIN_MENU_CMDS or text.startswith("/start"):
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        is_main_cmd = True
    
    if chat_id in user_states and not is_main_cmd:
        state = user_states[chat_id]

        # ================= SUPPORT USER MESSAGE =================
        if state == "support_wait_message" and (text or msg.get("caption")):
            support_text = text or msg.get("caption", "")
            u = get_user(chat_id)
            uname = u.get("username") or msg.get("from", {}).get("username") or "Not set"
            full_name = u.get("profile_name") or msg.get("from", {}).get("first_name") or "User"
            ticket = render_body_text(
                f"{PEM['msg']} <b>NEW SUPPORT MESSAGE</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"<b>User:</b> <a href='tg://user?id={chat_id}'>{html.escape(str(full_name))}</a>\n"
                f"<b>Username:</b> @{html.escape(str(uname).lstrip('@'))}\n"
                f"<b>User ID:</b> <code>{chat_id}</code>\n\n"
                f"<b>Message:</b>\n{html.escape(str(support_text))}"
            )
            delivered = 0
            for admin_id in bot_settings.get("admins", [OWNER_ID]):
                try:
                    r = send_message(admin_id, ticket, reply_markup=support_ticket_keyboard(chat_id))
                    if r and r.get("ok"): delivered += 1
                except Exception as e:
                    print(f"Support delivery error: {e}")
            if delivered:
                record_user_activity(chat_id, "support_message", {"message_length": len(str(support_text))})
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Message sent to Support.</b>\n\nPlease wait for an admin reply."), reply_markup=main_menu(chat_id))
            else:
                send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Support is temporarily unavailable.</b>\nPlease try again later."), reply_markup=main_menu(chat_id))
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            return

        # ================= SUPPORT ADMIN SETTINGS / REPLY =================
        if state == "support_admin_link" and text:
            link = text.strip()
            if not (link.startswith("https://t.me/") or link.startswith("http://t.me/") or link.startswith("https://telegram.me/") or link.startswith("http://telegram.me/")):
                send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Invalid support link.</b>\nPlease send a valid Telegram link."))
                return
            bot_settings["support_link"] = link
            save_db()
            user_states.pop(chat_id, None); temp_data.pop(chat_id, None)
            send_message(chat_id, support_management_text(), reply_markup=support_management_keyboard())
            return

        if state == "support_admin_name" and text:
            name = text.strip()[:40]
            if not name:
                return
            bot_settings["support_button_name"] = name
            save_db()
            user_states.pop(chat_id, None); temp_data.pop(chat_id, None)
            send_message(chat_id, support_management_text(), reply_markup=support_management_keyboard())
            return

        if state == "support_admin_reply" and (text or msg.get("caption")):
            target = str(temp_data.get(chat_id, {}).get("target_user", ""))
            reply_text = text or msg.get("caption", "")
            if target and str(target).isdigit():
                target_id = int(target)
                r = send_message(target_id, render_body_text(f"{PEM['msg']} <b>SUPPORT REPLY</b>\n━━━━━━━━━━━━━━━━━━\n{html.escape(str(reply_text))}"), reply_markup=main_menu(target_id))
                if r and r.get("ok"):
                    old_msg = temp_data.get(chat_id, {}).get("msg_id")
                    if old_msg:
                        edit_message(chat_id, old_msg, render_body_text(f"{PEM['ok']} <b>SUPPORT REPLIED</b>\n\n<b>User ID:</b> <code>{html.escape(target)}</code>\n<b>Reply:</b> {html.escape(str(reply_text))}"), reply_markup=None)
                else:
                    send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Could not deliver the reply.</b>"))
            user_states.pop(chat_id, None); temp_data.pop(chat_id, None)
            return

        # 🌟 Auto Captcha Panel Setup Flow 
        if state == "wait_for_cpanel_url" and text:
            temp_data[chat_id]["p_data"]["login_url"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_user"
            send_message(chat_id, render_body_text("2️⃣ <b>Username</b>\n➡️ Panel এর Username দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_user" and text:
            temp_data[chat_id]["p_data"]["username"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_pass"
            send_message(chat_id, render_body_text("3️⃣ <b>Password</b>\n➡️ Panel এর Password দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_pass" and text:
            temp_data[chat_id]["p_data"]["password"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_link"
            send_message(chat_id, render_body_text("4️⃣ <b>Message Link</b>\n➡️ যেখান থেকে SMS/OTP ডাটা (JSON) আসবে সেই Link দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_link" and text:
            temp_data[chat_id]["p_data"]["msg_link"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_name"
            send_message(chat_id, render_body_text("5️⃣ <b>Number Column Name</b>\n➡️ Data তে Number column এর নাম কী? (যেমন: number, phone):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_name" and text:
            temp_data[chat_id]["p_data"]["num_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_idx"
            send_message(chat_id, render_body_text("6️⃣ <b>Number Column Serial</b>\n➡️ Number Column এর Serial Number কত? (যেমন: 3, 5):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["num_col_idx"] = int(text)
                user_states[chat_id] = "wait_for_cpanel_msg_col_name"
                send_message(chat_id, render_body_text("7️⃣ <b>Message Column Name</b>\n➡️ Message/OTP column এর নাম কী? (যেমন: message, sms):"), reply_markup=get_cancel_kb())
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_name" and text:
            temp_data[chat_id]["p_data"]["msg_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_col_idx"
            send_message(chat_id, render_body_text("8️⃣ <b>Message Column Serial</b>\n➡️ Message Column এর Serial Number কত? (যেমন: 5, 7):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["msg_col_idx"] = int(text)
                temp_data[chat_id]["p_data"]["login_status"] = "⏳ Pending Auto-Login..."
                
                # Save the panel configuration
                bot_settings["panels"].append(temp_data[chat_id]["p_data"])
                save_db()
                
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Auto Captcha Panel Added Successfully!</b>\nবট এখন থেকে নিজেই ব্যাকগ্রাউন্ডে ক্যাপচা সলভ করে লগিন করে নিবে।"), reply_markup=main_menu(chat_id))
                
                msg_id = temp_data[chat_id]["msg_id"]
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_panels", "id": "internal"})
                
                del user_states[chat_id]
                del temp_data[chat_id]
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return

        # --- Refer OTP Reward ---
        elif state == "wait_for_refer_commission" and text:
            try:
                amount = float(text.strip())
                if amount < 0 or amount > 100000: raise ValueError
                bot_settings["refer_otp_commission"] = amount
                bot_settings["refer_otp_commission_on"] = amount > 0
                save_db()
                msg_id_to_edit = temp_data.get(chat_id, {}).get("msg_id")
                user_states.pop(chat_id, None)
                temp_data.pop(chat_id, None)
                if msg_id_to_edit:
                    edit_message(chat_id, msg_id_to_edit, refer_otp_reward_text(), reply_markup=refer_otp_reward_keyboard())
                else:
                    send_message(chat_id, refer_otp_reward_text(), reply_markup=refer_otp_reward_keyboard())
            except Exception:
                send_message(chat_id, render_body_text("❌ Invalid amount. Send a number like <code>0.50</code>."), reply_markup=get_cancel_kb())
            return

        # --- User Management Flows ---
        elif state == "wait_for_um_bal_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID! Please send a numeric User ID."), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc = db.collection('users').document(str(target_uid)).get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                current_bal = doc.to_dict().get('balance', 0.0)
                temp_data[chat_id]["target_uid"] = target_uid
                user_states[chat_id] = "wait_for_um_bal_amt"
                send_message(chat_id, render_body_text(f"✅ User found!\n💰 Current Balance: {current_bal} ৳\n\n📝 Send the amount to ADD (e.g. 50) or REMOVE (e.g. -50):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_bal_amt" and text:
            try:
                amt = float(text.strip())
                target_uid = temp_data[chat_id]["target_uid"]
                update_balance(target_uid, amt)
                send_message(chat_id, render_body_text(f"{PEM['ok']} Balance updated successfully for {target_uid}!"), reply_markup=main_menu(chat_id))
                send_message(target_uid, render_body_text(f"🔔 Your balance has been adjusted by <b>{amt} ৳</b> by an Admin."))
                del user_states[chat_id]
                del temp_data[chat_id]
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid amount! Please send a number."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_ban_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc_ref = db.collection('users').document(str(target_uid))
                doc = doc_ref.get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                current_status = doc.to_dict().get("banned", False)
                new_status = not current_status
                doc_ref.update({"banned": new_status})
                
                user_banned_cache[target_uid] = {'banned': new_status, 'time': time.time()}
                
                status_text = "BANNED 🚫" if new_status else "UNBANNED ✅"
                send_message(chat_id, render_body_text(f"✅ User {target_uid} has been {status_text}!"), reply_markup=main_menu(chat_id))
                del user_states[chat_id]
                del temp_data[chat_id]
            return

        elif state == "wait_for_um_prof_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc = db.collection('users').document(str(target_uid)).get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                data = doc.to_dict()
                is_verified = True if data.get('total_otps', 0) > 0 else data.get('verified', False)
                prof_text = f"""➖➖➖➖➖➖➖➖
👤 <b>USER PROFILE</b>
➖➖➖➖➖➖➖➖
🆔 ID: <code>{target_uid}</code>
💰 Balance: {data.get('balance', 0.0)} ৳
🤝 Total Refers: {data.get('total_refers', 0)}
🔐 Total OTPs: {data.get('total_otps', 0)}
✅ Verified: {is_verified}
🚫 Banned: {data.get('banned', False)}
➖➖➖➖➖➖➖➖"""
                kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "user_management", "style": "primary"}]]}
                send_message(chat_id, render_body_text(prof_text), reply_markup=kb)
                del user_states[chat_id]
                del temp_data[chat_id]
            return

        elif state == "wait_for_traffic_time" and text:
            try:
                minutes = int(text.strip())
                if minutes < 1 or minutes > 1440:
                    raise ValueError
                bot_settings["traffic_window_minutes"] = minutes
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"📊 <b>Traffic time updated</b>\n\nLast <b>{minutes} minutes</b> of OTP traffic will now be counted."), reply_markup={"inline_keyboard": [[{"text": "Back to Traffic Settings", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "md_edit_traffic", "style": "primary"}], [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]]})
            except Exception:
                send_message(chat_id, render_body_text("❌ Invalid time. Send a whole number from 1 to 1440."))
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        # --- Reply Keyboard Emoji Settings ---
        elif state == "wait_for_reply_keyboard_emoji" and text:
            try:
                button_name = temp_data[chat_id]["reply_button"]
                emoji_id = None
                for ent in msg.get("entities", []):
                    if ent.get("type") == "custom_emoji" and ent.get("custom_emoji_id"):
                        emoji_id = str(ent.get("custom_emoji_id"))
                        break
                raw = text.strip()
                if emoji_id is None and raw.isdigit():
                    emoji_id = raw
                if not emoji_id:
                    send_message(chat_id, render_body_text("<b>Invalid Premium Emoji</b>\n\nSend a Premium Custom Emoji, or send its Custom Emoji ID."), reply_markup=get_cancel_kb())
                    return
                bot_settings.setdefault("reply_keyboard_emojis", {})[button_name] = emoji_id
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['ok']} <b>Reply Keyboard Emoji Updated</b>\n\n<b>Button:</b> {html.escape(button_name)}\n<b>Emoji ID:</b> <code>{emoji_id}</code>"), reply_markup=reply_keyboard_emoji_settings_keyboard())
            except Exception as e:
                send_message(chat_id, render_body_text(f"{PEM['no']} Error: {html.escape(str(e))}"), reply_markup=get_cancel_kb())
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        # --- Menu Design Flow ---
        elif state == "wait_for_menu_text" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                formatted_html_text = extract_premium_html(msg)
                
                bot_settings["custom_messages"][menu_key]["text"] = formatted_html_text
                save_db()
                
                delete_message(chat_id, msg["message_id"])
                
                preview_text = render_body_text(formatted_html_text)
                success_text = f"{PEM['ok']} <b>Message Body Updated successfully!</b>\n\n🎨 <b>Editing: {menu_key.upper()}</b>\n\nPreview of current Text:\n{preview_text}"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(success_text), reply_markup=menu_edit_options_keyboard(menu_key))
            except Exception as e:
                send_message(chat_id, f"❌ Error saving text: {e}")
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return
            
        elif state == "wait_for_menu_btn" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                if "-" in text:
                    parts = text.split("-", 1)
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    
                    emoji_id = None
                    emoji_char = ""
                    for ent in msg.get("entities", []):
                        if ent.get("type") == "custom_emoji":
                            emoji_id = ent.get("custom_emoji_id")
                            offset = ent.get("offset", 0)
                            length = ent.get("length", 0)
                            b_text = text.encode('utf-16-le')
                            emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                            break
                            
                    if emoji_char:
                        btn_text = btn_text.replace(emoji_char, "").strip()
                        
                    btn_data = {"text": btn_text, "url": btn_url, "style": "primary"}
                    if emoji_id:
                        btn_data["icon_custom_emoji_id"] = emoji_id
                        
                    bot_settings["custom_messages"][menu_key]["buttons"].append(btn_data)
                    save_db()
                    delete_message(chat_id, msg["message_id"])
                    edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['gear']} <b>Edit Inline Buttons: {menu_key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(menu_key))
                else:
                    send_message(chat_id, render_body_text(f"{PEM['no']} Invalid format. Use <code>Button Text - https://link.com</code>"))
            except Exception as e:
                 pass
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        elif state == "wait_for_test_service" and text:
            temp_data[chat_id]["service"] = text.strip()
            user_states[chat_id] = "wait_for_test_number"
            send_message(chat_id, render_body_text("📝 Send the Number (e.g. +8801712345678):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_number" and text:
            temp_data[chat_id]["number"] = text.strip()
            user_states[chat_id] = "wait_for_test_otp"
            send_message(chat_id, render_body_text("📝 Send the OTP (e.g. 556677):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_otp" and text:
            temp_data[chat_id]["otp"] = text.strip()
            user_states[chat_id] = "wait_for_test_lang"
            send_message(chat_id, render_body_text("📝 Send the Language (e.g. EN, AR):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_lang" and text:
            lang = text.strip().upper()
            if not lang.startswith("#"):
                lang = "#" + lang
                
            srv = temp_data[chat_id]["service"]
            num = temp_data[chat_id]["number"]
            otp = temp_data[chat_id]["otp"]
            
            masked = mask_number(num)
            prem_flag_html = get_flag_info_html(num)
            char, iso = get_flag_and_code(num)
            app_full_name, prem_app_html = get_service_info_html(srv)
            
            lang_name = lang
            msg_text = render_body_text(f"{prem_flag_html} {iso} | {prem_app_html} {masked} | 💬 {lang}")
            
            for fw in bot_settings.get("fw_groups", []):
                kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
                temp_row = []
                styles = ["danger", "success", "primary"]
                for i, btn in enumerate(fw.get("buttons", [])):
                    b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                    if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                    temp_row.append(b_obj)
                    if len(temp_row) == 2:
                        kb.append(temp_row)
                        temp_row = []
                if temp_row: kb.append(temp_row)
                send_message(fw["chat_id"], msg_text, reply_markup={"inline_keyboard": kb})
                
            send_message(chat_id, render_body_text(f"{PEM['ok']} Test message formatted and sent to all Forward Groups!"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_mask_emoji":
            entities = msg.get("entities", [])
            custom_emoji_id = None
            emoji_text = ""
            for ent in entities:
                if ent.get("type") == "custom_emoji":
                    custom_emoji_id = ent.get("custom_emoji_id")
                    offset = ent.get("offset", 0)
                    length = ent.get("length", 0)
                    b_text = msg.get("text", "").encode("utf-16-le")
                    emoji_text = b_text[offset*2:(offset+length)*2].decode("utf-16-le")
                    break
            if custom_emoji_id:
                bot_settings["mask_emoji"] = {"id": custom_emoji_id, "char": emoji_text}
                save_db()
                edit_id = temp_data.get(chat_id, {}).get("msg_id")
                if edit_id:
                    edit_message(chat_id, edit_id, render_body_text(f"{PEM['ok']} Number mask emoji updated successfully."), reply_markup=emoji_settings_keyboard())
                else:
                    send_message(chat_id, render_body_text(f"{PEM['ok']} Number mask emoji updated successfully."), reply_markup=emoji_settings_keyboard())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} Please send a Premium Custom Emoji."), reply_markup=emoji_settings_keyboard())
            delete_message(chat_id, msg.get("message_id"))
            user_states.pop(chat_id, None)
            temp_data.pop(chat_id, None)
            return

        elif state == "wait_for_emoji_extract":
            entities = msg.get("entities", [])
            custom_emoji_id = None
            emoji_text = ""
            for ent in entities:
                if ent.get("type") == "custom_emoji":
                    custom_emoji_id = ent.get("custom_emoji_id")
                    offset = ent.get("offset", 0)
                    length = ent.get("length", 0)
                    b_text = msg.get("text", "").encode('utf-16-le')
                    emoji_text = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                    break
            
            if custom_emoji_id:
                temp_data[chat_id] = {"id": custom_emoji_id, "char": emoji_text}
                user_states[chat_id] = "wait_for_emoji_details"
                send_message(chat_id, render_body_text(f"{PEM['ok']} Emoji ID পাওয়া গেছে: <code>{custom_emoji_id}</code>\n\n📌 এখন এটি সেভ করার জন্য টাইপ এবং নাম লিখুন।\n\n<b>ফরমেট:</b>\n`FLAG | 880 | BD | Bangladesh`\nঅথবা\n`APP | WhatsApp`"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} কোনো Premium Emoji পাওয়া যায়নি! দয়া করে Custom Emoji সেন্ড করুন।"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_emoji_details" and text:
            parts = [p.strip() for p in text.split("|")]
            mode = parts[0].upper()
            eid = temp_data[chat_id]["id"]
            char = temp_data[chat_id]["char"]
            
            if mode == "FLAG" and len(parts) == 4:
                code, iso, name = parts[1], parts[2], parts[3]
                bot_settings["premium_flags"][code] = {"char": char, "iso": iso.upper(), "name": name, "id": eid}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} Flag Emoji সেভ হয়েছে!\nCode: {code} | Name: {name}"), reply_markup=emoji_settings_keyboard())
            elif mode == "APP" and len(parts) == 2:
                name = parts[1]
                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name.title()}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} App Emoji সেভ হয়েছে!\nName: {name}"), reply_markup=emoji_settings_keyboard())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} ফরম্যাট ভুল!\n\nসঠিক ফরম্যাট:\n`FLAG | 880 | BD | Bangladesh`\n`APP | WhatsApp`"))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state in ["wait_for_flag_txt", "wait_for_app_txt"] and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            content = requests.get(f"{FILE_URL}{file_path}").text
            
            mode = "flags" if state == "wait_for_flag_txt" else "apps"
            count = 0
            
            if mode == "flags":
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            prefix_str = line[:json_match.start()].strip()
                            code_match = re.search(r'\((\d+)\)', prefix_str)
                            iso_match = re.search(r'\(([A-Za-z]+)\)', prefix_str)
                            
                            if code_match and iso_match and char and eid:
                                code = code_match.group(1)
                                iso = iso_match.group(1).upper()
                                name = prefix_str.replace(f"({code})", "").replace(f"({iso_match.group(1)})", "").replace(char, "").strip()
                                bot_settings["premium_flags"][code] = {"char": char, "iso": iso, "name": name, "id": eid}
                                count += 1
                        except: pass
            else:
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            name_part = line[:json_match.start()].strip()
                            name = name_part.replace(char, '').strip() if char else name_part
                            
                            if char and eid and name:
                                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name}
                                count += 1
                        except: pass
            
            save_db()
            send_message(chat_id, render_body_text(f"{PEM['ok']} Successfully loaded {count} Emojis!"), reply_markup=emoji_settings_keyboard())
            del user_states[chat_id]
            return

        elif state == "wait_for_broadcast":
            msg_id = msg["message_id"]
            status_res = send_message(chat_id, render_body_text(f"{PEM['ok']} Broadcast started..."))
            status_msg_id = None
            try:
                if status_res and status_res.get("ok") and status_res.get("result"):
                    status_msg_id = status_res["result"].get("message_id")
            except Exception:
                pass
            threading.Thread(target=broadcast_copymessage, args=(chat_id, msg_id, status_msg_id), daemon=True).start()
            del user_states[chat_id]
            return

        elif state == "wait_for_database_upload" and "document" in msg:
            doc = msg["document"]
            filename = doc.get("file_name", "")
            if not filename.lower().endswith(".zip"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a <b>.zip</b> database backup."))
                return
            try:
                file_id = doc["file_id"]
                file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}", timeout=15).json()
                file_path = file_info["result"]["file_path"]
                raw = requests.get(f"{FILE_URL}{file_path}", timeout=30).content
                with zipfile.ZipFile(io.BytesIO(raw), "r") as z:
                    names = set(z.namelist())
                    if not ({"bot_data.json", "local_db.json"} & names):
                        raise ValueError("Invalid database backup")
                    for name in ["bot_data.json", "local_db.json", "users_list.json"]:
                        if name in names:
                            with z.open(name) as src, open(name, "wb") as dst:
                                dst.write(src.read())
                load_db()
                sync_users_list()
                user_cache.clear()
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Database uploaded and restored successfully.</b>"), reply_markup=main_menu(chat_id))
            except Exception as e:
                send_message(chat_id, render_body_text(f"{PEM['no']} <b>Database restore failed.</b>\nInvalid or corrupted backup."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_special_users" and text:
            if not is_admin(chat_id):
                user_states.pop(chat_id, None)
                return
            ids = []
            for token in re.split(r"[,\s]+", text.strip()):
                if token.isdigit():
                    try:
                        uid = int(token)
                        if uid > 0 and uid not in ids:
                            ids.append(uid)
                    except ValueError:
                        pass
            if not ids:
                send_message(chat_id, render_body_text("<b>Invalid User ID.</b>\nPlease send one or more numeric Telegram user IDs."), reply_markup=get_cancel_kb())
                return
            bot_settings["special_users"] = ids
            save_db()
            user_states.pop(chat_id, None)
            send_message(chat_id, special_user_management_text(), reply_markup={"inline_keyboard": [
                [{"text": "Set Special User", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "special_users", "style": "success"}],
                [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}]
            ]})
            return

        elif state == "wait_for_txt" and "document" in msg:
            doc=msg["document"]; filename=doc.get("file_name","numbers_file"); file_id=doc["file_id"]
            try:
                file_info=requests.get(f"{BASE_URL}/getFile",params={"file_id":file_id},timeout=15).json()
                if not file_info.get("ok"): raise ValueError("Telegram could not prepare the file")
                file_path=file_info["result"]["file_path"]
                raw_file=requests.get(f"{FILE_URL}{file_path}",timeout=60).content
                extracted_numbers=extract_numbers_from_uploaded_file(filename,raw_file)
                if not extracted_numbers:
                    send_message(chat_id,render_body_text(f"{PEM['no']} <b>No valid numbers found in this file.</b>\nPlease upload a file containing phone numbers."),reply_markup=get_cancel_kb()); return
                temp_data[chat_id]={"numbers":extracted_numbers,"filename":filename}
                user_states[chat_id]="wait_for_service"
                send_message(chat_id,render_body_text(f"{PEM['ok']} <b>File received successfully.</b>\n\n📁 File: <code>{html.escape(filename)}</code>\n🔢 Numbers found: <b>{len(extracted_numbers)}</b>\n\n📌 Enter the service name (e.g., WHATSAPP):"),reply_markup=get_cancel_kb())
            except Exception as e:
                print(f"Number file parse error ({filename}): {e}")
                send_message(chat_id,render_body_text(f"{PEM['no']} <b>Could not read this file.</b>\nThe file may be empty, corrupted, or contain no readable numbers."),reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_service" and text:
            temp_data[chat_id]["service"] = text.upper()
            # Country is detected automatically from the uploaded number prefix.
            numbers = temp_data[chat_id].get("numbers", [])
            country = get_flag_info_html(numbers[0], return_full_name=True) if numbers else "UNKNOWN"
            temp_data[chat_id]["country"] = str(country).upper()
            user_states[chat_id] = "wait_for_file_rate"
            send_message(chat_id, render_body_text(
                f"{PEM['ok']} Service set.\n"
                f"🌍 Country detected automatically: <b>{html.escape(str(country).upper())}</b>\n\n"
                f"💰 Enter the OTP earning rate for <b>normal users</b> for this file.\n\n"
                f"You can use <code>0</code> to disable the reward line."
            ), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_file_rate" and text:
            try:
                rate = float(text.strip())
                if rate < 0: raise ValueError
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid rate! Please enter a number 0 or greater."), reply_markup=get_cancel_kb())
                return
            temp_data[chat_id]["normal_rate"] = rate
            user_states[chat_id] = "wait_for_special_file_rate"
            send_message(chat_id, render_body_text("💰 Now enter the OTP earning rate for <b>Special Users</b> for this file.\n\nYou can use <code>0</code> to disable the reward line."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_special_file_rate" and text:
            try:
                special_rate = float(text.strip())
                if special_rate < 0: raise ValueError
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid rate! Please enter a number 0 or greater."), reply_markup=get_cancel_kb())
                return
                
            rate = float(temp_data[chat_id].get("normal_rate", 0.0))
            country = temp_data[chat_id]["country"]
            service = temp_data[chat_id]["service"]
            raw_numbers = temp_data[chat_id]["numbers"]
            
            clean_nums = []
            for num in raw_numbers:
                num = num.strip()
                if num:
                    if not num.startswith('+'): num = '+' + num
                    clean_nums.append(num)
            
            batch_id = str(uuid.uuid4())[:8]
            number_batches[batch_id] = {
                "filename": temp_data[chat_id]["filename"], 
                "service": service, 
                "country": country, 
                "rate": rate,
                "normal_rate": rate,
                "special_rate": special_rate,
                "numbers": [{"num": n, "shares": 0, "used_by": []} for n in clean_nums]
            }
            total_uploaded_stats += len(clean_nums)
            save_db()
            
            app_full_name, prem_app_html = get_service_info_html(service)
            prem_flag_html = get_flag_info_html(clean_nums[0]) if clean_nums else f"{PEM['world']} "
            
            def build_new_numbers_notice(reward):
                reward_line = f"\n💰 Reward: <b>{reward:g} TK</b>" if float(reward) > 0 else ""
                return render_body_text(
                    f"➖➖➖➖➖➖➖➖\n《 NEW NUMBERS 》\n➖➖➖➖➖➖➖➖\n"
                    f"{prem_flag_html} {country} {prem_app_html} {service}\n➖➖➖➖➖➖➖➖\n"
                    f"📤 Total Added: <b>{len(clean_nums)}</b>{reward_line}\n"
                    f"➖➖➖➖➖➖➖➖\nUse /start to get your numbers!"
                )

            status_res = send_message(chat_id, render_body_text(
                f"{PEM['ok']} Numbers added to local stock.\n"
                f"Normal User Rate: <b>{rate:g} TK</b>\n"
                f"Special User Rate: <b>{special_rate:g} TK</b>\n\nStarting broadcast..."
            ))
            status_msg_id = None
            try:
                if status_res and status_res.get("ok") and status_res.get("result"):
                    status_msg_id = status_res["result"].get("message_id")
            except Exception:
                status_msg_id = None

            def simple_broadcast():
                b_session = requests.Session()
                url = f"{BASE_URL}/sendMessage"
                recipients = set(all_known_users) | {str(x) for x in bot_settings.get("special_users", [])}
                for u_id in list(recipients):
                    try:
                        reward_for_user = special_rate if is_special_user(u_id) else rate
                        txt = build_new_numbers_notice(reward_for_user)
                        b_session.post(url, json={"chat_id": u_id, "text": txt, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=5)
                    except Exception as e:
                        print(f"New number broadcast failed for {u_id}: {e}")
                    time.sleep(0.035)
                # Remove the admin-side broadcast status after sending is finished.
                if status_msg_id:
                    try:
                        delete_message(chat_id, status_msg_id)
                    except Exception:
                        pass
            threading.Thread(target=simple_broadcast, daemon=True).start()
            
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_stex_key" and text:
            bot_settings["stex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ StexSMS API Key Added! Total Keys: {len(bot_settings.get('stex_keys', []))}"), reply_markup=stex_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fastx_key" and text:
            key = text.strip()
            if not key:
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("❌ Invalid Fast X API Key."), reply_markup=fastx_control_keyboard())
                return
            bot_settings.setdefault("fastx_keys", [])
            if key not in bot_settings["fastx_keys"]:
                bot_settings["fastx_keys"].append(key)
            bot_settings["fastx_enabled"] = True
            bot_settings.setdefault("fastx_auto", False)
            # Validate/sync immediately when Auto Range is already ON.
            # This matches the original Fast X bot: API key -> /api/liveaccess -> services/ranges.
            if bot_settings.get("fastx_auto", False):
                try:
                    fastx_sync_liveaccess(key)
                except Exception as exc:
                    print(f"[FAST X] immediate liveaccess sync failed: {exc}")
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ <b>Fast X API Key Connected!</b>\n\nTotal API Keys: {len(bot_settings.get('fastx_keys', []))}\nStatus: 🟢 Connected"), reply_markup=fastx_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_voltx_key" and text:
            bot_settings["voltx_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Voltx API Key Added! Total Keys: {len(bot_settings.get('voltx_keys', []))}"), reply_markup=voltx_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_sc" and text:
            code = text.strip().replace("+", "")
            if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
            bot_settings["search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            kb = []
            for idx, c in enumerate(bot_settings.get("search_countries", [])):
                kb.append([{"text": f"❌ Delete {c}", "callback_data": f"del_sc_{idx}", "style": "danger"}])
            kb.append([{"text": "➕ Add Country Code", "callback_data": "add_search_country", "style": "success"}])
            kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_vsc" and text:
            code = text.strip().replace("+", "")
            if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
            bot_settings["voltx_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "voltx_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_nx_srv_name" and text:
            srv = text.strip().upper()
            if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
            if srv not in bot_settings["stex_services"]: bot_settings["stex_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_stex_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_nx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["stex_services"][srv]: bot_settings["stex_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_nx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["stex_services"][srv][cnt]:
                bot_settings["stex_services"][srv][cnt].append(new_range)
                
                if "search_countries" not in bot_settings:
                    bot_settings["search_countries"] = []
                if new_range not in bot_settings["search_countries"]:
                    bot_settings["search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_fx_srv_name" and text:
            srv = text.strip().upper()
            fastx_hidden_services.discard(srv)
            bot_settings.setdefault("fastx_services", {}).setdefault(srv, {})
            save_db(); delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_fastx_srv", "id": "internal"})
            del user_states[chat_id]; del temp_data[chat_id]; return

        elif state == "wait_fx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            fastx_hidden_countries.discard(f"{srv}|{cnt}")
            bot_settings.setdefault("fastx_services", {}).setdefault(srv, {}).setdefault(cnt, [])
            save_db(); delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"fx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]; del temp_data[chat_id]; return

        elif state == "wait_fx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            fastx_hidden_ranges.discard(f"{srv}|{new_range}")
            fastx_hidden_countries.discard(f"{srv}|{cnt}")
            fastx_hidden_services.discard(srv)
            bot_settings.setdefault("fastx_services", {}).setdefault(srv, {}).setdefault(cnt, [])
            if new_range not in bot_settings["fastx_services"][srv][cnt]: bot_settings["fastx_services"][srv][cnt].append(new_range)
            if new_range[:3] not in bot_settings.setdefault("fastx_search_countries", []): bot_settings["fastx_search_countries"].append(new_range[:3])
            save_db(); delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"fx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]; del temp_data[chat_id]; return

        elif state == "wait_for_add_fxc" and text:
            code = re.sub(r"\D", "", text.strip())
            if code:
                arr = bot_settings.setdefault("fastx_search_countries", [])
                if code not in arr: arr.append(code); save_db()
            delete_message(chat_id, msg["message_id"]); handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "fastx_search_country", "id": "internal"})
            del user_states[chat_id]; del temp_data[chat_id]; return

        elif state == "wait_vx_srv_name" and text:
            srv = text.strip().upper()
            if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
            if srv not in bot_settings["voltx_services"]: bot_settings["voltx_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_voltx_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["voltx_services"][srv]: bot_settings["voltx_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["voltx_services"][srv][cnt]:
                bot_settings["voltx_services"][srv][cnt].append(new_range)
                
                if "voltx_search_countries" not in bot_settings:
                    bot_settings["voltx_search_countries"] = []
                if new_range not in bot_settings["voltx_search_countries"]:
                    bot_settings["voltx_search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_zenex_key" and text:
            bot_settings["zenex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Zenex API Key Added! Total Keys: {len(bot_settings.get('zenex_keys', []))}"), reply_markup=zenex_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_zsc" and text:
            code = text.strip().replace("+", "")
            if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
            bot_settings["zenex_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "zenex_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_zx_srv_name" and text:
            srv = text.strip().upper()
            if "zenex_services" not in bot_settings: bot_settings["zenex_services"] = {}
            if srv not in bot_settings["zenex_services"]: bot_settings["zenex_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_zenex_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_zx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["zenex_services"][srv]: bot_settings["zenex_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"zx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_zx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            if new_range not in bot_settings["zenex_services"][srv][cnt]:
                bot_settings["zenex_services"][srv][cnt].append(new_range)
                if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
                if new_range not in bot_settings["zenex_search_countries"]: bot_settings["zenex_search_countries"].append(new_range)
                save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"zx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_wm" and text:
            bot_settings["w_methods"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fj" and text:
            bot_settings["fj_channels"].append(parse_chat_id(text))
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🔗 <b>FORCE JOIN SYSTEM</b>\nManage channels below:\n<i>(Note: For private links, use numeric IDs like -100...)</i>"), reply_markup=fj_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_adm" and text:
            if text.isdigit():
                bot_settings["admins"].append(int(text))
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("👥 <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fw_id" and text:
            bot_settings["fw_groups"].append({"chat_id": text.strip(), "buttons": []})
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_fw_btn" and text:
            fw_idx = temp_data[chat_id]["fw_idx"]
            if "-" in text:
                parts = text.split("-", 1)
                btn_text = parts[0].strip()
                btn_url = parts[1].strip()
                
                emoji_id = None
                emoji_char = ""
                for ent in msg.get("entities", []):
                    if ent.get("type") == "custom_emoji":
                        emoji_id = ent.get("custom_emoji_id")
                        offset = ent.get("offset", 0)
                        length = ent.get("length", 0)
                        b_text = text.encode('utf-16-le')
                        emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                        break
                
                if emoji_char:
                    btn_text = btn_text.replace(emoji_char, "").strip()
                    
                btn_data = {"text": btn_text, "url": btn_url}
                if emoji_id:
                    btn_data["icon_custom_emoji_id"] = emoji_id
                    
                bot_settings["fw_groups"][fw_idx]["buttons"].append(btn_data)
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][fw_idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(fw_idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_otp_link" and text:
            bot_settings["otp_link"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_panel_name" and text:
            p_name = text.strip()
            t_key = temp_data[chat_id].get("add_type", "api")
            msg_id = temp_data[chat_id]["msg_id"]
            delete_message(chat_id, msg["message_id"])
            
            if t_key == "logc":
                user_states[chat_id] = "wait_for_cpanel_url"
                temp_data[chat_id] = {"msg_id": msg_id, "p_data": {
                    "name": p_name, "type": "Auto Captcha Panel", "status": "ON", "records": 0, "login_status": "⏳ Pending First Login"
                }}
                edit_message(chat_id, msg_id, render_body_text("1️⃣ <b>Login URL</b>\n➡️ Panel এর Login Link দিন:"), reply_markup=get_cancel_kb())
                return
            else:
                bot_settings["panels"].append({
                    "name": p_name, "type": "API Panel", "status": "OFF", "api_url": "", "token": "", "records": 0
                })
                save_db()
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_panels", "id": "internal"})
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return

        elif state == "wait_for_p_api" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_tok" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["token"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_fapi" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["full_api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_rec" and text:
            if text.isdigit():
                idx = temp_data[chat_id]["p_idx"]
                bot_settings["panels"][idx]["records"] = int(text)
                save_db()
                delete_message(chat_id, msg["message_id"])
                p = bot_settings["panels"][idx]
                
                ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid number! Try again."), reply_markup=get_cancel_kb())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "set_panel_otp_reward":
            msg_id = temp_data[chat_id]["msg_id"]
            panel_key = temp_data[chat_id]["panel_key"]
            rate_type = temp_data[chat_id]["rate_type"]
            try:
                value = float(text.strip())
                if value < 0 or value > 100000:
                    raise ValueError
                panel_rates = bot_settings.setdefault("panel_otp_rewards", {}).setdefault(
                    panel_key, {"user": float(bot_settings.get("otp_reward", 0.0)), "special": float(bot_settings.get("otp_reward", 0.0))}
                )
                panel_rates[rate_type] = value
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text(
                    f"💰 <b>{otp_reward_panel_name(panel_key)} OTP REWARD</b>\n\n"
                    f"👤 User Reward: <b>{panel_rates.get('user', 0)}</b> TK\n"
                    f"⭐ Special User Reward: <b>{panel_rates.get('special', 0)}</b> TK\n\n"
                    "Choose which rate you want to change:"
                ), reply_markup=otp_reward_panel_manage_keyboard(panel_key))
            except Exception:
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text(
                    f"💰 <b>{otp_reward_panel_name(panel_key)} OTP REWARD</b>\n\n❌ Invalid reward amount. Send a number like <code>0.50</code>."
                ), reply_markup=otp_reward_panel_manage_keyboard(panel_key))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "set_dxa":
            msg_id = temp_data[chat_id]["msg_id"]
            key = temp_data[chat_id]["key"]
            try:
                if key in ["min_withdraw", "otp_reward"]: bot_settings[key] = float(text)
                elif key in ["cooldown", "num_req", "num_share"]: bot_settings[key] = int(text)
                else: bot_settings[key] = text
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
            except:
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>\n\n❌ Invalid value!"), reply_markup=dxa_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_search" and text:
            query = text.strip().replace("+", "")
            if not query.isdigit() or len(query) < 3 or len(query) > 9:
                send_message(chat_id, render_body_text("❌ Please enter a valid 3 to 9 digit number!"))
                return
                
            wait_msg = send_message(chat_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = wait_msg.get("result", {}).get("message_id")
            
            # 🌟 ১. প্রথমে Local থেকে নাম্বার খুঁজবে (যে কোনো দেশের জন্য)
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                # 🌟 ২. যদি Local এ না পায়, তখন চেক করবে Voltx বা StexSMS থেকে আনা যাবে কি না
                stex_allowed = bot_settings.get("search_countries", [])
                voltx_allowed = bot_settings.get("voltx_search_countries", [])
                
                # ফিক্স: অ্যাডমিন প্যানেলে দেশ এড না থাকলে অটোমেটিক Block করে দেবে
                is_stex_allowed = any(query.startswith(c) for c in stex_allowed) if stex_allowed else False
                is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
                
                if not is_stex_allowed and not is_voltx_allowed:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ This country code is not allowed!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                    
                if wait_msg_id: edit_message(chat_id, wait_msg_id, render_body_text("⌛ <i>Processing... Finding Number via API...</i>"))
                
                is_voltx_used = False
                req_count = bot_settings.get("num_req", 1)
                
                # 🌟 প্রথমে Voltx চেক করবে
                if is_voltx_allowed:
                    voltx_keys = bot_settings.get("voltx_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in voltx_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    ksi_assigned_numbers[num_str] = chat_id
                                    voltx_assigned_numbers[num_str] = chat_id 
                                    is_voltx_used = True
                                    global total_assigned_stats
                                    total_assigned_stats += 1
                                    break # শুধু api_key লুপ ব্রেক করবে, যাতে পরের নাম্বার আনতে পারে
                            except: continue

                # 🌟 Voltx এ না পেলে বা আরও নাম্বার লাগলে StexSMS তে চেক করবে
                if len(fetched_nums) < req_count and is_stex_allowed:
                    stex_keys = bot_settings.get("stex_keys", [])
                    
                    for _ in range(req_count - len(fetched_nums)): 
                        for api_key in stex_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                data = res.json()
                                if data.get("meta", {}).get("code") == 200 and data.get("data"):
                                    num_str = str(data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    ksi_assigned_numbers[num_str] = chat_id
                                    stex_assigned_numbers[num_str] = chat_id 
                                    total_assigned_stats += 1
                                    break 
                            except: continue
                        
                if not fetched_nums:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Number out of stock!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    
                    fetched_nums.append(num_str)
                    # Persist the exact getter -> number ownership for KSI delivery.
                    # This is required for numbers coming from LOCAL STOCK too.
                    ksi_assigned_numbers[num_str] = chat_id
                    
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
                
            kb = []
            flags_db = bot_settings.get("premium_flags", {})
            country_emoji_html = ""
            for num in fetched_nums:
                char_flag, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                flag_emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: 
                            flag_emoji_id = flag_data["id"]
                            country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                        break
                if not country_emoji_html: country_emoji_html = char_flag
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": "success"}])
            
            vtx_ext = "_vtx" if 'is_voltx_used' in locals() and is_voltx_used else ""
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{vtx_ext}", "style": "danger"}])
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns: 
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
                
            kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            
            text_numbers, new_number_custom_kb = render_new_number_message(country_emoji_html)
            kb.extend(new_number_custom_kb)
            
            if wait_msg_id:
                edit_message(chat_id, wait_msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
                user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
                for _assigned_num in fetched_nums:
                    ksi_assigned_numbers[str(_assigned_num)] = chat_id
                if db:
                    try:
                        db.collection("users").document(str(chat_id)).set({
                            "total_numbers": Increment(len(fetched_nums)), "updated_at": time.time()
                        }, merge=True)
                    except Exception: pass
                if chat_id in user_cache:
                    user_cache[chat_id]["total_numbers"] = user_cache[chat_id].get("total_numbers", 0) + len(fetched_nums)
                record_user_activity(chat_id, "number_assigned", {"numbers": fetched_nums, "count": len(fetched_nums)})
                save_db()
            else:
                msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
                if msg_res and "result" in msg_res:
                    user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums}
                    for _assigned_num in fetched_nums:
                        ksi_assigned_numbers[str(_assigned_num)] = chat_id
                    save_db()
            return
            
        elif state == "wait_for_withdraw_amount" and text:
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            try:
                amount = float(text.strip())
                bal = temp_data[chat_id]["balance"]
                min_w = bot_settings['min_withdraw']
                
                if amount < min_w:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ Minimum withdrawal is {min_w} ৳!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                if amount > bal:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ You don't have enough balance!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                    
                temp_data[chat_id]["amount"] = amount
                user_states[chat_id] = "wait_for_withdraw_number"
                if msg_id_to_edit:
                    edit_message(chat_id, msg_id_to_edit, render_body_text(f"✅ Amount: {amount} ৳\n\n📱 Now send your <b>{temp_data[chat_id]['method']}</b> account number:"), reply_markup=get_cancel_kb())
            except ValueError:
                if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text("❌ Invalid amount!\n\n📝 Please send a valid number:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_2fa_key" and text:
            msg_id_to_edit = temp_data.get(chat_id, {}).get("msg_id")
            delete_message(chat_id, msg.get("message_id")) # ইউজারের মেসেজ ডিলিট

            if not msg_id_to_edit:
                send_message(chat_id, render_body_text("❌ Error: Message not found. Try again."))
                del user_states[chat_id]
                return

            try:
                secret = text.strip().replace(" ", "")
                totp = pyotp.TOTP(secret)
                code = totp.now()
                remaining_time = 30 - (int(time.time()) % 30)
                
                success_txt = (
                    f"━━━━━━━━━━━━━━━\n"
                    f"《 🔐 <b>2FA CODE</b> 》\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                    f"━━━━━━━━━━━━━━━"
                )
                kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                      [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                       {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                      [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
                
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
                del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            except Exception:
                error_txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━\n❌ <b>Invalid Secret Key! Try again.</b>\n━━━━━━━━━━━━━━━"
                cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
                edit_message(chat_id, msg_id_to_edit, render_body_text(error_txt), reply_markup=cancel_kb)
            return

        elif state == "wait_for_withdraw_number":
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            
            method = temp_data[chat_id]["method"]
            amount = temp_data[chat_id]["amount"]
            number = text
            req_id = f"W_{str(uuid.uuid4())[:6].upper()}"
            
            first_name = msg.get("from", {}).get("first_name", "User")
            last_name = msg.get("from", {}).get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            
            update_balance(chat_id, -amount, reason="withdrawal_request", activity_type="withdrawal_requested")
            if db:
                try:
                    db.collection("users").document(str(chat_id)).set({
                        "total_withdrawals": Increment(amount), "updated_at": time.time()
                    }, merge=True)
                except Exception as exc:
                    print(f"[WITHDRAWAL TOTAL] {exc}")
            if chat_id in user_cache:
                user_cache[chat_id]["total_withdrawals"] = user_cache[chat_id].get("total_withdrawals", 0.0) + amount
            record_user_activity(chat_id, "withdrawal_created", {
                "request_id": req_id, "amount": amount, "method": method, "account": number, "status": "pending"
            })
            pending_withdrawals[req_id] = {"user_id": chat_id, "amount": amount, "method": method, "number": number, "full_name": full_name}
            save_db()
            
            # Save to local database for history
            if db:
                try:
                    db.collection('withdrawals').document(req_id).set({
                        "user_id": str(chat_id),
                        "amount": amount,
                        "method": method,
                        "number": number,
                        "full_name": full_name,
                        "status": "pending",
                        "timestamp": SERVER_TIMESTAMP
                    })
                except: pass

            # Notify every configured admin as soon as a withdrawal is submitted.
            admin_req_data = {
                "user_id": chat_id,
                "amount": amount,
                "method": method,
                "number": number,
                "full_name": full_name
            }
            try:
                notified_admins = set()
                for admin_id in bot_settings.get("admins", [OWNER_ID]):
                    try:
                        admin_id = int(admin_id)
                    except Exception:
                        continue
                    if admin_id in notified_admins:
                        continue
                    notified_admins.add(admin_id)
                    send_message(
                        admin_id,
                        withdrawal_request_text(req_id, admin_req_data),
                        reply_markup=withdrawal_request_keyboard(req_id)
                    )
            except Exception as exc:
                print(f"[WITHDRAWAL ADMIN NOTIFY] {exc}")
            
            kb = {"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
            success_text = f"{PEM['ok']} Your withdrawal request has been submitted!\n\n🧾 <b>Req ID:</b> {req_id}\n💰 <b>Amount:</b> {amount} ৳\n🏦 <b>Method:</b> {method}\n📱 <b>Number:</b> <code>{number}</code>"
            
            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_text), reply_markup=kb)
            else:
                send_message(chat_id, render_body_text(success_text), reply_markup=kb)
                
            del user_states[chat_id]
            del temp_data[chat_id]
            return

    # --- Regular Commands ---
    if text.startswith("/start"):
        get_user(chat_id)
        
        # --- PROCESS PENDING REFERRAL ---
        process_referral_join(chat_id, msg)
                    
        c_msg = bot_settings["custom_messages"].get("start", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['hi']} Welcome!"))
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        
        if kb:
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
            send_message(chat_id, render_body_text(f"{PEM['gear']} Navigation Menu:"), reply_markup=main_menu(chat_id))
        else:
            send_message(chat_id, txt, reply_markup=main_menu(chat_id))
            
    elif text in ["Live Traffic", "LIVE TRAFFIC"]:
        txt, markup = build_traffic_ui()
        send_message(chat_id, txt, reply_markup=markup)
        
    elif text == "Refer & Earn":
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        commission = float(bot_settings.get("refer_otp_commission", 0.0) or 0.0)
        commission_status = "ON" if bot_settings.get("refer_otp_commission_on", True) else "OFF"
        total_ref = int(u_data.get("total_refers", 0) or 0)
        ref_otp_count = int(u_data.get("ref_otp_commissions", 0) or 0)
        ref_income = float(u_data.get("ref_income", 0.0) or 0.0)

        txt = render_body_text(
            f"━━━━━━━━━━━━\n"
            f"🎁  <b>REFER &amp; EARN</b>\n"
            f"━━━━━━━━━━━━\n"
            f"<i>Invite friends and earn automatically.</i>\n\n"
            f"🔗 <b>Your Link</b>\n"
            f"<code>{html.escape(ref_link)}</code>\n\n"
            f"👥 <b>Referred</b>           : <b>{total_ref}</b>\n"
            f"📈 <b>OTP Received</b>    : <b>{ref_otp_count}</b>\n"
            f"💰 <b>Earned</b>             : <b>{ref_income:g} ৳</b>\n\n"
            f"💎 <b>৳{commission:g} / OTP</b>\n"
            f"──────────────────────\n"
            f"<i>When a referred member receives an OTP, you earn {commission:g} ৳ per OTP.</i>"
        )
        kb = [
            [{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}],
            [{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
        ]
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "My profile":
        # Keep profile identity current from Telegram's message metadata.
        frm = msg.get("from", {})
        profile_name = " ".join([x for x in [frm.get("first_name", ""), frm.get("last_name", "")] if x]).strip() or "User"
        username = frm.get("username", "")
        u_data = get_user(chat_id)
        updates = {}
        if u_data.get("profile_name") != profile_name:
            updates["profile_name"] = profile_name
        if u_data.get("username", "") != username:
            updates["username"] = username
        if updates and db:
            try:
                db.collection("users").document(str(chat_id)).set(updates, merge=True)
                u_data.update(updates)
                user_cache[chat_id] = u_data
            except:
                pass
        send_message(chat_id, get_user_profile_text(chat_id), reply_markup=user_profile_keyboard())

    elif text == "WITHDRAWAL":
        if not bot_settings["withdraw_on"]:
            send_message(chat_id, render_body_text(f"{PEM['no']} Withdrawals are currently disabled."))
            return
        
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        
        c_msg = bot_settings["custom_messages"].get("withdrawal", {})
        raw_txt = c_msg.get("text", "Withdrawal").replace("{bal}", str(bal)).replace("{total_otp}", str(u_data.get('total_otps', 0))).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{min_w}", str(bot_settings['min_withdraw']))
        txt = render_body_text(raw_txt)
        
        kb = []
        for m in bot_settings["w_methods"]:
            kb.append([{"text": m.strip(), "icon_custom_emoji_id": "5190899075968441286", "callback_data": f"sel_wm_{m.strip()}", "style": "primary"}])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text in ["Admin panel", "Admin Panel"] and is_admin(chat_id):
        send_message(chat_id, get_admin_text(), reply_markup=admin_panel_keyboard())

    elif text in ["Get Number", "GET NUMBER"]:
        all_services = set(build_active_service_keyboard())
        
        if not all_services:
            send_message(chat_id, render_body_text(f"{PEM['no']} No numbers or services available!"))
        else:
            c_msg = bot_settings["custom_messages"].get("get_number", {})
            txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
            
            apps_db = bot_settings.get("premium_apps", {})
            kb = []
            service_buttons = []
            for s in sorted(all_services, key=lambda x: str(x).lower()):
                emoji_id = "5352694861990501856" # Default icon
                for app_key, app_data in apps_db.items():
                    if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                        if "id" in app_data:
                            emoji_id = app_data["id"]
                            break
                service_buttons.append({"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"})
            for i in range(0, len(service_buttons), 2):
                kb.append(service_buttons[i:i + 2])
            
            custom_buttons = []
            for b in c_msg.get("buttons", []): 
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                custom_buttons.append(b_copy)
            for i in range(0, len(custom_buttons), 2):
                kb.append(custom_buttons[i:i + 2])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Search Number":
        user_states[chat_id] = "wait_for_search"
        c_msg = bot_settings["custom_messages"].get("search_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['num']} Search Number"))
        kb = [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "2FA ONLINE" or text == "🔐 2FA ONLINE":
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        send_message(chat_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif text in ["Support", "SUPPORT"]:
        txt = render_body_text(
            f"{PEM['msg']} <b>SUPPORT CENTER</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Need help? Send your message to our support team.\n\n"
            f"<i>Write your issue and our admin will reply here.</i>"
        )
        send_message(chat_id, txt, reply_markup=support_user_keyboard())

def render_new_number_message(country_emoji_html, country="", service=""):
    """Render the user-facing NEW NUMBER message from Admin > Menu Design."""
    c_msg = bot_settings.get("custom_messages", {}).get("new_number", {})
    raw_txt = c_msg.get("text", "{flag} NEW NUMBER")
    raw_txt = str(raw_txt).replace("{flag}", str(country_emoji_html))
    raw_txt = raw_txt.replace("{country}", str(country)).replace("{service}", str(service))
    txt = render_body_text(raw_txt)
    # Optional custom buttons for the NEW NUMBER message.
    kb = []
    btns = []
    for b in c_msg.get("buttons", []):
        b_copy = b.copy()
        if "style" not in b_copy:
            b_copy["style"] = "primary"
        btns.append(b_copy)
    for i in range(0, len(btns), 2):
        kb.append(btns[i:i + 2])
    return txt, kb

def expire_previous_number(chat_id):
    if chat_id in user_active_sessions:
        prev_data = user_active_sessions[chat_id]
        prev_msg_id = prev_data["msg_id"]
        nums = prev_data["nums"]
        
        # API সিস্টেম থেকে রিমুভ করা যাতে ইনবক্সে আর মেসেজ না যায়
        for num in nums:
            if num in stex_assigned_numbers: del stex_assigned_numbers[num]
            if num in voltx_assigned_numbers: del voltx_assigned_numbers[num]
            if num in zenex_assigned_numbers: del zenex_assigned_numbers[num]
            if num in ksi_assigned_numbers: del ksi_assigned_numbers[num]
            if num in fastx_assigned_numbers: del fastx_assigned_numbers[num]
            if num in fastx_assigned_ranges: del fastx_assigned_ranges[num]
        save_db()
        
        # আগের মেসেজ ইডিট করে Expired বাটন বসানো
        kb = [[{"text": "Number Expired", "icon_custom_emoji_id": "5336997731481193790", "callback_data": "ignore", "style": "danger"}]]
        try:
            edit_message(chat_id, prev_msg_id, "NEW NUMBER\n", reply_markup={"inline_keyboard": kb})
        except:
            pass
        del user_active_sessions[chat_id]

# ==========================================
# Active Bangla Panel / Range Helpers
# ==========================================
def get_active_bangla_providers():
    providers = []
    if bot_settings.get("stex_auto", False) and bot_settings.get("stex_keys"): providers.append(("stexsms", "StexSMS"))
    if bot_settings.get("voltx_auto", False) and bot_settings.get("voltx_keys"): providers.append(("voltx", "Voltx"))
    if bot_settings.get("zenex_auto", False) and bot_settings.get("zenex_keys"): providers.append(("zenex", "Zenex"))
    if bot_settings.get("fastx_enabled", FASTX_ENABLED_DEFAULT) and bot_settings.get("fastx_auto", False) and bot_settings.get("fastx_keys"): providers.append(("fastx", "Fast X"))
    return providers

def _provider_services(provider_key):
    mapping={"stexsms":"stex_services","voltx":"voltx_services","zenex":"zenex_services","fastx":"fastx_services"}
    return bot_settings.get(mapping.get(provider_key,""),{}) or {}

def _country_match_key(country):
    q=str(country or "").strip()
    for _,fd in bot_settings.get("premium_flags",{}).items():
        if isinstance(fd,dict):
            name=str(fd.get("name","")).strip(); iso=str(fd.get("iso","")).strip().upper()
            if name and iso and q.casefold()==name.casefold(): return iso
            if iso and q.upper()==iso: return iso
    return q.casefold()

def _encode_cb_part(value):
    return base64.urlsafe_b64encode(str(value).encode()).decode().rstrip("=")

def _decode_cb_part(value):
    value=str(value); value += "=" * (-len(value)%4)
    return base64.urlsafe_b64decode(value.encode()).decode()

def build_active_service_keyboard():
    services=set()
    for b in number_batches.values():
        if b.get("numbers"): services.add(str(b.get("service","")))
    for pk,_ in get_active_bangla_providers(): services.update(_provider_services(pk).keys())
    services.discard("")
    return sorted(services,key=lambda x:str(x).lower())

def build_provider_country_buttons(service):
    entries=[]
    for pk,_ in get_active_bangla_providers():
        cdict=_provider_services(pk).get(service,{}) or {}
        for country,ranges in cdict.items():
            if ranges: entries.append((pk,str(country)))
    for country in sorted({str(b.get("country")) for b in number_batches.values() if b.get("service")==service and b.get("numbers")},key=str.lower): entries.append(("local",country))
    counts={}; buttons=[]; flags_db=bot_settings.get("premium_flags",{})
    for pk,country in entries:
        key=_country_match_key(country); counts[key]=counts.get(key,0)+1
        label=country if counts[key]==1 else f"{country} {counts[key]}"
        eid="5780471598922337683"
        for _,fd in flags_db.items():
            if isinstance(fd,dict) and (str(fd.get("name","")).strip().casefold()==country.casefold() or str(fd.get("iso","")).strip().upper()==country.upper()): eid=fd.get("id",eid); break
        buttons.append({"text":label,"icon_custom_emoji_id":eid,"callback_data":f"g_p:{pk}:{_encode_cb_part(service)}:{_encode_cb_part(country)}","style":"success"})
    return buttons


# ==========================================
# Callback Query Handler
# ==========================================
def handle_callback(call):
    global total_assigned_stats
    chat_id = call["message"]["chat"]["id"]
    chat_type = call["message"]["chat"].get("type", "private")
    data = call.get("data", "")

    # 🌟 Button Loading Fix: বাটন চাপার সাথে সাথেই টেলিগ্রামকে Response দিয়ে দেওয়া, যাতে বাটন আটকে না থাকে!
    if not data.startswith("test_p_conn_") and not data.startswith("c_n_") and not data.startswith("g_c_") and not data.startswith("fastx_"):
        try: threading.Thread(target=answer_callback, args=(call["id"],)).start()
        except: pass

    if chat_type != "private" and not (data.startswith("wapp_") or data.startswith("wrej_")):
        return

    msg_id = call["message"]["message_id"]

    if chat_type == "private":
        if is_user_banned(chat_id):
            answer_callback(call["id"], "🚫 You are banned from using this bot!", show_alert=True)
            return

        if not check_force_join(chat_id) and data != "check_fj":
            send_force_join_msg(chat_id)
            return

    if data == "check_fj":
        if check_force_join(chat_id):
            delete_message(chat_id, msg_id)
            send_message(chat_id, render_body_text(f"{PEM['ok']} Thanks for joining! You can now use the bot."), reply_markup=main_menu(chat_id))
            
            # --- PROCESS PENDING REFERRAL ---
            process_referral_join(chat_id, {})
        else:
            answer_callback(call["id"], "❌ You haven't joined all channels yet!", show_alert=True)
        return

    if data == "close_msg":
        delete_message(chat_id, msg_id)
        
    elif data == "cancel_state":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        delete_message(chat_id, msg_id)

    elif data == "cancel_2fa":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "gen_2fa":
        user_states[chat_id] = "wait_for_2fa_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━"
        kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)
        answer_callback(call["id"])

    elif data.startswith("ref_2fa_"):
        secret = data.replace("ref_2fa_", "")
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()
            remaining_time = 30 - (int(time.time()) % 30)
            
            success_txt = (
                f"━━━━━━━━━━━━━━━\n"
                f"《 🔐 <b>2FA CODE</b> 》\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                f"━━━━━━━━━━━━━━━"
            )
            kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                  [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                   {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                  [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
            
            edit_message(chat_id, msg_id, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
        except:
            answer_callback(call["id"], "❌ Error refreshing code!", show_alert=True)

    elif data == "cancel_dxa_edit":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
        
    elif data == "dummy_alert":
        answer_callback(call["id"], "This feature will be added later!", show_alert=True)
        
    elif data == "refresh_traffic":
        txt, markup = build_traffic_ui()
        edit_message(chat_id, msg_id, txt, reply_markup=markup)
        answer_callback(call["id"], "✅ Traffic Refreshed!", show_alert=False)

    elif data.startswith("exp_rng_"):
        srv_query = data.replace("exp_rng_", "")
        
        country_stats = {}
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query):
                    iso = t.get("iso", "XX")
                    flag = t.get("flag", "🌍")
                    if iso not in country_stats:
                        country_stats[iso] = {"count": 0, "flag": flag}
                    country_stats[iso]["count"] += 1
        
        if not country_stats:
            answer_callback(call["id"], "❌ No recent traffic found for this service!", show_alert=True)
            return
            
        kb = []
        for iso, c_data in sorted(country_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            count = c_data["count"]
            c_name = iso
            emoji_id = "5780471598922337683"
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    c_name = fdata.get("name", iso)
                    if "id" in fdata: emoji_id = fdata["id"]
                    break
            
            btn_text = f"{c_name} ({iso}) - {count} OTP"
            kb.append([{"text": btn_text, "icon_custom_emoji_id": emoji_id, "callback_data": f"exp_c_{srv_query}_{iso}", "style": "primary"}])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "refresh_traffic", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Explore Service: {prem_app_html} {app_full_name}</b>\n\nSelect a country to view available ranges:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("exp_c_"):
        parts = data.split("_")
        srv_query = parts[2]
        iso_query = parts[3]
        
        nums = []
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query) and t.get("iso") == iso_query:
                    # 🌟 X রিমুভ করে ক্লিন রেঞ্জ নেওয়া হলো
                    num = t.get("real_range", t.get("number", "").replace("X", "").replace("x", "")).replace("+", "").strip()
                    if num: nums.append(num)
        
        if not nums:
            answer_callback(call["id"], "❌ No recent numbers found for this country!", show_alert=True)
            return
            
        # শুধুমাত্র StexSMS Services থেকে রেঞ্জ নিবো (Search Countries নিবো না, কারণ ওগুলোতে শুধু দেশের কোড থাকে)
        known_ranges = set()
        for s_name, c_dict in bot_settings.get("stex_services", {}).items():
            for c_name, r_list in c_dict.items():
                for r in r_list:
                    # 🌟 এখানেও সেভ করা রেঞ্জ থেকে X সরিয়ে নিচ্ছি
                    known_ranges.add(r.replace("X", "").replace("x", ""))
                    
        sorted_known = sorted(list(known_ranges), key=len, reverse=True)
        
        r_counts = Counter()
        for num in nums:
            matched = False
            for r in sorted_known:
                if num.startswith(r):
                    r_counts[r] += 1
                    matched = True
                    break
            if not matched:
                if len(num) >= 7:
                    r_counts[num[:7]] += 1
                else:
                    r_counts[num] += 1
                    
        r_list = r_counts.most_common(12)
        
        kb = []
        temp_row = []
        for r, count in r_list:
            # 🌟 বাটনে এবং কলব্যাকে যাতে কোনো X না থাকে তা নিশ্চিত করা হলো
            clean_r = str(r).replace("X", "").replace("x", "")
            temp_row.append({"text": f"{clean_r} ({count})", "icon_custom_emoji_id": "5352862640592949843", "callback_data": f"c_n_s_{clean_r}_{srv_query}", "style": "primary"})
            if len(temp_row) == 2:
                kb.append(temp_row)
                temp_row = []
        if temp_row:
            kb.append(temp_row)
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"exp_rng_{srv_query}", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        prem_flag_html = get_flag_info_html(iso_query)
        
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Ranges for {prem_app_html} {app_full_name} - {prem_flag_html} {iso_query}</b>\n\nClick on any range to copy it."), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    # --- Refer OTP Reward ---
    elif data == "refer_management":
        edit_message(chat_id, msg_id, refer_otp_reward_text(), reply_markup=refer_otp_reward_keyboard())

    elif data == "refer_toggle":
        bot_settings["refer_otp_commission_on"] = not bot_settings.get("refer_otp_commission_on", True)
        save_db()
        edit_message(chat_id, msg_id, refer_otp_reward_text(), reply_markup=refer_otp_reward_keyboard())

    elif data == "refer_set_commission":
        user_states[chat_id] = "wait_for_refer_commission"
        temp_data[chat_id] = {"msg_id": msg_id}
        current = float(bot_settings.get("refer_otp_commission", 0.0) or 0.0)
        edit_message(chat_id, msg_id, render_body_text(
            f"💰 <b>Set Referral OTP Commission</b>\n\nCurrent: <b>{current:g} ৳ / OTP</b>\n\n"
            "Send the commission amount per OTP. Example: <code>0.50</code>"
        ), reply_markup=get_cancel_kb())

    # --- User Management Flows Integration ---
    elif data == "user_management":
        edit_message(chat_id, msg_id, get_user_management_text(), reply_markup=user_management_keyboard())

    elif data.startswith("all_users_"):
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can view the user list.", show_alert=True)
            return
        try: page = int(data.split("_")[-1])
        except Exception: page = 0
        txt, kb = build_all_user_list(page)
        edit_message(chat_id, msg_id, txt, reply_markup=kb)
        answer_callback(call["id"])

    elif data == "um_manage_balance":
        user_states[chat_id] = "wait_for_um_bal_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Manage Balance:"), reply_markup=get_cancel_kb())
        
    elif data == "um_ban_unban":
        user_states[chat_id] = "wait_for_um_ban_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Ban or Unban:"), reply_markup=get_cancel_kb())

    elif data == "um_user_profile":
        user_states[chat_id] = "wait_for_um_prof_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to View Profile:"), reply_markup=get_cancel_kb())

    # --- Menu Design Integration ---
    elif data == "menu_design_list":
        edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Menu Design Editor</b>\n\nSelect a menu block to edit its Body Text and Inline Buttons. You can use Premium Emojis too!"), reply_markup=menu_design_list_keyboard())

    elif data == "md_reset_defaults":
        bot_settings["custom_messages"] = DEFAULT_CUSTOM_MESSAGES.copy()
        save_db()
        answer_callback(call["id"], "✅ Resetted to Premium Defaults!", show_alert=True)

    elif data == "reply_keyboard_emoji_settings":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Not authorized", show_alert=True)
            return
        edit_message(chat_id, msg_id, render_body_text("🎨 <b>Reply Keyboard Emoji</b>\n\nSelect a button to change its Premium Custom Emoji.\nSend the Premium Emoji itself, or send its Custom Emoji ID."), reply_markup=reply_keyboard_emoji_settings_keyboard())
        answer_callback(call["id"])

    elif data.startswith("rkemoji_set:"):
        if not is_admin(chat_id):
            answer_callback(call["id"], "Not authorized", show_alert=True)
            return
        button_name = data.split(":", 1)[1]
        user_states[chat_id] = "wait_for_reply_keyboard_emoji"
        temp_data[chat_id] = {"msg_id": msg_id, "reply_button": button_name}
        edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Set Emoji: {html.escape(button_name)}</b>\n\nSend the Premium Custom Emoji now, or send its Custom Emoji ID."), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "md_edit_traffic":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        try:
            current_window = max(1, int(bot_settings.get("traffic_window_minutes", 30)))
        except Exception:
            current_window = 30
        mode = str(bot_settings.get("console_traffic_mode", "on")).lower()
        if mode not in ("off", "on", "all"):
            mode = "on" if bot_settings.get("console_traffic", True) else "off"
        mode_style = {"on": "success", "off": "primary", "all": "danger"}.get(mode, "success")
        traffic_kb = {"inline_keyboard": [
            [{"text": "Consol Traffic", "icon_custom_emoji_id": "5203993413346680064", "callback_data": "console_traffic_cycle", "style": mode_style}],
            [{"text": "Set Traffic Time", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "traffic_time_custom", "style": "primary"}],
            [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Edit TRAFFIC</b>\n\nCurrent traffic window: <b>{current_window} minutes</b>\n\nConsol Traffic mode is selected by the button color."), reply_markup=traffic_kb)
        answer_callback(call["id"])

    elif data == "traffic_time_custom":
        user_states[chat_id] = "wait_for_traffic_time"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📊 <b>Set Custom Traffic Time</b>\n\nSend the number of minutes. Example: <code>15</code> or <code>45</code>\n\nMinimum: 1 minute."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "md_edit_traffic", "style": "danger"}]]})
        answer_callback(call["id"])

    elif data.startswith("md_edit_"):
        answer_callback(call["id"])
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_edit_", "")
        cm_text = render_body_text(bot_settings["custom_messages"].get(key, {}).get("text", "..."))
        try:
            edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Editing: {key.upper()}</b>\n\nPreview of current Text:\n{cm_text}"), reply_markup=menu_edit_options_keyboard(key))
        except: pass

    elif data.startswith("md_text_"):
        key = data.replace("md_text_", "")
        user_states[chat_id] = "wait_for_menu_text"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"📝 <b>Edit Body: {key.upper()}</b>\n\nSend the new text. You can use Premium Emojis directly here.\n(Use standard HTML like <b>bold</b>, <i>italic</i> for formatting)"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{key}", "style": "danger"}]]})

    elif data.startswith("md_btns_"):
        answer_callback(call["id"]) 
        if chat_id in user_states: del user_states[chat_id] 
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_btns_", "")
        try:
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))
        except: pass

    elif data.startswith("md_addbtn_"):
        key = data.replace("md_addbtn_", "")
        user_states[chat_id] = "wait_for_menu_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"➕ <b>Add Button: {key.upper()}</b>\n\nSend custom button in this format:\n<code>Button Text - https://link.com</code>\n\n<i>(Only normal Emojis supported here!)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_btns_{key}", "style": "danger"}]]})

    elif data.startswith("md_delbtn_"):
        parts = data.split("_")
        key = parts[2]
        b_idx = int(parts[3])
        if b_idx < len(bot_settings["custom_messages"][key]["buttons"]):
            del bot_settings["custom_messages"][key]["buttons"][b_idx]
            save_db()
            answer_callback(call["id"], "✅ Button Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))

    elif data == "profile_withdraw":
        if not bot_settings.get("withdraw_on", True):
            answer_callback(call["id"], "Withdrawals are currently disabled.", show_alert=True)
            return
        # Reuse the existing withdrawal workflow from the profile button.
        u_data = get_user(chat_id)
        bal = u_data.get("balance", 0.0)
        min_w = bot_settings.get("min_withdraw", 0)
        if bal < min_w:
            answer_callback(call["id"], f"Minimum withdrawal is {min_w} ৳.", show_alert=True)
            return
        c_msg = bot_settings["custom_messages"].get("withdrawal", {})
        raw_txt = c_msg.get("text", "Withdrawal").replace("{bal}", str(bal)).replace("{total_otp}", str(u_data.get("total_otps", 0))).replace("{total_ref}", str(u_data.get("total_refers", 0))).replace("{min_w}", str(min_w))
        kb = []
        for m in bot_settings.get("w_methods", []):
            kb.append([{"text": m.strip(), "icon_custom_emoji_id": "5190899075968441286", "callback_data": f"sel_wm_{m.strip()}", "style": "primary"}])
        kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text(raw_txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("sel_wm_"):
        method = data.replace("sel_wm_", "")
        bal = get_user(chat_id).get('balance', 0.0)
        min_w = bot_settings['min_withdraw']
        
        if bal < min_w:
            answer_callback(call["id"], f"❌ আপনার ব্যালেন্স অপর্যাপ্ত! মিনিমাম {min_w} ৳ প্রয়োজন।", show_alert=True)
            return
            
        temp_data[chat_id] = {"method": method, "balance": bal, "msg_id": msg_id}
        user_states[chat_id] = "wait_for_withdraw_amount"
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} Method: {method}\n💰 Available Balance: {bal} ৳\n\n📝 Enter the amount you want to withdraw (Min: {min_w} ৳):"), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "test_message_flow":
        user_states[chat_id] = "wait_for_test_service"
        temp_data[chat_id] = {}
        edit_message(chat_id, msg_id, render_body_text("🧪 <b>Test Mode</b>\n\n📝 Send the Service Name (e.g., IG):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]]})

    elif data == "manage_emojis":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['star']} <b>Premium Emoji Management</b>\n\nUpload your TXT files or manually add them below:"), reply_markup=emoji_settings_keyboard())

    elif data == "up_flags_txt":
        user_states[chat_id] = "wait_for_flag_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Flag Emojis</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "up_apps_txt":
        user_states[chat_id] = "wait_for_app_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Service Apps</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "add_single_emoji":
        user_states[chat_id] = "wait_for_emoji_extract"
        edit_message(chat_id, msg_id, render_body_text("📝 যেকোনো একটি Premium Emoji সেন্ড করুন (যেমন: 🇧🇩 বা 🚫):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "set_mask_emoji":
        user_states[chat_id] = "wait_for_mask_emoji"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Premium Emoji you want to use between the first and last digits of masked numbers."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})
        answer_callback(call["id"])

    elif data == "dl_flags_txt":
        content = generate_emoji_txt("flags")
        if content:
            send_document(chat_id, "Flag_Emojis.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No Flag Emojis found!", show_alert=True)

    elif data == "dl_apps_txt":
        content = generate_emoji_txt("apps")
        if content:
            send_document(chat_id, "Service_Apps.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No App Emojis found!", show_alert=True)

    elif data == "del_all_flags":
        bot_settings["premium_flags"] = {}
        save_db()
        answer_callback(call["id"], "✅ All Premium Flags Deleted Successfully!", show_alert=True)

    elif data == "database_menu":
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['file']} <b>DATABASE</b>\n\nManage the bot database backup and restore operations."
        ), reply_markup=database_keyboard())

    elif data == "db_download":
        backup = create_database_backup()
        if send_file_document(chat_id, "database_backup.zip", backup):
            answer_callback(call["id"], "Database backup sent.", show_alert=False)
        else:
            answer_callback(call["id"], "Database download failed.", show_alert=True)

    elif data == "db_upload":
        user_states[chat_id] = "wait_for_database_upload"
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['upload']} <b>UPLOAD DATABASE</b>\n\nSend the database backup <code>.zip</code> file."
        ), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "database_menu", "style": "danger"}]]})

    elif data == "db_clear_confirm":
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['warn']} <b>CLEAR ALL DATABASE DATA?</b>\n\nThis will permanently remove users, balances, referrals, withdrawals, number stock, traffic and saved settings.\n\nContinue only if you have a backup."
        ), reply_markup={"inline_keyboard": [
            [{"text": "Yes, Clear All Data", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "db_clear_all", "style": "danger"}],
            [{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "database_menu", "style": "primary"}]
        ]})

    elif data == "db_clear_all":
        if not is_admin(chat_id):
            return
        reset_all_database_data()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>All database data has been cleared.</b>"), reply_markup=admin_panel_keyboard())

    elif data == "broadcast_msg":
        user_states[chat_id] = "wait_for_broadcast"
        edit_message(chat_id, msg_id, render_body_text("📢 <b>Broadcast Mode</b>\n\nSend the message you want to broadcast (Text, Photo, Video, File etc)."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "upload_num":
        user_states[chat_id] = "wait_for_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the number file. TXT, CSV, XLSX, DOCX, PDF and other supported document files are accepted. Country will be detected automatically from the numbers."), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "special_users":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can manage Special Users.", show_alert=True)
            return
        edit_message(chat_id, msg_id, special_user_management_text(), reply_markup={"inline_keyboard": [
            [{"text": "Set Special User", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "special_users_set", "style": "success"}],
            [{"text": "Clear Special Users", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "special_users_clear", "style": "danger"}],
            [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
        ]})

    elif data == "special_users_set":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can manage Special Users.", show_alert=True)
            return
        user_states[chat_id] = "wait_for_special_users"
        edit_message(chat_id, msg_id, render_body_text(
            "<b>SET SPECIAL USER</b>\n\nSend Telegram user ID(s). You can send multiple IDs separated by comma, space, or new line.\n\n"
            "These users will receive the Special User OTP earning rate."
        ), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "special_users", "style": "danger"}]]})

    elif data == "special_users_clear":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can manage Special Users.", show_alert=True)
            return
        bot_settings["special_users"] = []
        save_db()
        edit_message(chat_id, msg_id, special_user_management_text(), reply_markup={"inline_keyboard": [
            [{"text": "Set Special User", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "special_users_set", "style": "success"}],
            [{"text": "Clear Special Users", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "special_users_clear", "style": "danger"}],
            [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
        ]})

    elif data == "delete_files":
        kb = []
        for b_id, b_data in number_batches.items():
            # Do not expose the uploaded filename here. Show detected country + service instead.
            country_name = str(b_data.get("country") or "UNKNOWN").upper()
            service_name = str(b_data.get("service") or "UNKNOWN").upper()
            label = f"{country_name} • {service_name} ({len(b_data.get('numbers', []))})"
            kb.append([{"text": label, "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_b_{b_id}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}])
        txt = "🗑 Select a file to delete:" if len(kb) > 1 else f"{PEM['no']} No files found."
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_b_"):
        b_id = data.split("del_b_")[1]
        if b_id in number_batches:
            del number_batches[b_id]
            save_db()
            answer_callback(call["id"], "✅ File deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "delete_files", "id": call["id"]})

    elif data == "show_used":
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_used", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>Total Used Numbers:</b> {len(used_numbers_list)}"), reply_markup=kb)

    elif data == "show_unused":
        unused_count = sum(len(b["numbers"]) for b in number_batches.values())
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_unused", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['rocket']} <b>Total Unused Numbers:</b> {unused_count}"), reply_markup=kb)

    elif data == "dl_used":
        if not used_numbers_list:
            answer_callback(call["id"], "❌ No used numbers found!", show_alert=True)
            return
        content = "\n".join(used_numbers_list).encode('utf-8')
        send_document(chat_id, "used_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "dl_unused":
        unused_list = [n["num"] for b in number_batches.values() for n in b["numbers"]]
        if not unused_list:
            answer_callback(call["id"], "❌ No unused numbers found!", show_alert=True)
            return
        content = "\n".join(unused_list).encode('utf-8')
        send_document(chat_id, "unused_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for w in ws:
                    d = w.to_dict()
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get('amount',0)}৳</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for w in ws:
                    d = w.to_dict()
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get('amount',0)}৳</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "back_to_admin":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
        
    elif data == "system_settings":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['gear']} <b>System Settings</b>\nManage advanced bot configurations below:"), reply_markup=system_settings_keyboard())

    elif data == "stex_control":
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('stex_keys', []))}\nManage your StexSMS API Keys below:"), reply_markup=stex_control_keyboard())

    elif data == "toggle_stex_auto":
        bot_settings["stex_auto"] = not bot_settings.get("stex_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('stex_keys', []))}\nManage your StexSMS API Keys below:"), reply_markup=stex_control_keyboard())
        answer_callback(call["id"], f"✅ Stex Auto Range is now {'ON' if bot_settings['stex_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_stex_key":
        user_states[chat_id] = "wait_for_add_stex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new StexSMS API Key (e.g. nxa_...):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}]]})

    elif data == "view_stex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("stex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_nxa_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select StexSMS Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_nxa_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("stex_keys", [])):
            del bot_settings["stex_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ StexSMS Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_stex_keys", "id": call["id"]})

    elif data == "stex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_sc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_search_country":
        user_states[chat_id] = "wait_for_add_sc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Country Code (e.g. 880 or 92):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_search_country", "style": "danger"}]]})

    elif data.startswith("del_sc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("search_countries", [])):
            del bot_settings["search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Country Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "stex_search_country", "id": call["id"]})

    elif data == "manage_stex_srv":
        kb = []
        srvs = bot_settings.get("stex_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "nx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("📦 <b>StexSMS Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "nx_add_srv":
        user_states[chat_id] = "wait_nx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_srv_"):
        srv = data.replace("nx_srv_", "")
        kb = []
        countries = bot_settings["stex_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_stex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_add_cnt_"):
        srv = data.replace("nx_add_cnt_", "")
        user_states[chat_id] = "wait_nx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["stex_services"][srv].get(cnt, [])
        
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"nx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"nx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_nx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 88017):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("nx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["stex_services"].get(srv, {}).get(cnt, []):
            bot_settings["stex_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("nx_del_srv_"):
        srv = data.replace("nx_del_srv_", "")
        if srv in bot_settings["stex_services"]: del bot_settings["stex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_stex_srv", "id": call["id"]})

    elif data.startswith("nx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["stex_services"].get(srv, {}): del bot_settings["stex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_srv_{srv}", "id": call["id"]})

    elif data == "fastx_control":
        keys = bot_settings.get("fastx_keys", [])
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Fast X Control Panel</b>\n\nTotal API Keys: {len(keys)}\n\nFast X uses a fixed API endpoint. Add only your API key."), reply_markup=fastx_control_keyboard())

    elif data == "toggle_fastx":
        bot_settings["fastx_enabled"] = not bot_settings.get("fastx_enabled", True)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Fast X Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('fastx_keys', []))}"), reply_markup=fastx_control_keyboard())
        answer_callback(call["id"], f"✅ Fast X is now {'ON' if bot_settings['fastx_enabled'] else 'OFF'}!", show_alert=False)

    elif data == "add_fastx_key":
        user_states[chat_id] = "wait_for_add_fastx_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Send the Fast X API Key:</b>\n\nOnly the API key is required. The API URL is built into the bot."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "fastx_control", "style": "danger"}]]})

    elif data == "view_fastx_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("fastx_keys", [])):
            safe_name = key[:10] + "..." if len(key) > 10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fastx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "fastx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Fast X Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_fastx_"):
        idx = int(data.split("_")[-1])
        if 0 <= idx < len(bot_settings.get("fastx_keys", [])):
            del bot_settings["fastx_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Fast X Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_fastx_keys", "id": call["id"]})

    elif data == "toggle_fastx_auto":
        bot_settings["fastx_auto"] = not bot_settings.get("fastx_auto", False)
        if bot_settings["fastx_auto"] and bot_settings.get("fastx_keys"):
            for _fx_key in bot_settings.get("fastx_keys", []):
                try:
                    fastx_sync_liveaccess(_fx_key)
                except Exception as exc:
                    print(f"[FAST X] auto-range toggle sync failed: {exc}")
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Fast X Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('fastx_keys', []))}"), reply_markup=fastx_control_keyboard())
        answer_callback(call["id"], f"✅ Fast X Auto Range is now {'ON' if bot_settings['fastx_auto'] else 'OFF'}!", show_alert=False)

    elif data == "manage_fastx_srv":
        kb = []
        srvs = bot_settings.get("fastx_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"fx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "fx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "fastx_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("⚡ <b>Fast X Services Manager</b>\nManage Fast X services and their country/range mappings below:"), reply_markup={"inline_keyboard": kb})

    elif data == "fx_add_srv":
        user_states[chat_id] = "wait_fx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("fx_srv_"):
        srv = data.replace("fx_srv_", "")
        kb = []
        countries = bot_settings.get("fastx_services", {}).get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = str(flag_data.get("iso", "")).upper(); name = str(flag_data.get("name", "")).upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"fx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"fx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"fx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fastx_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("fx_add_cnt_"):
        srv = data.replace("fx_add_cnt_", "")
        user_states[chat_id] = "wait_fx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("fx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings.get("fastx_services", {}).get(srv, {}).get(cnt, [])
        kb = []; row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"fx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"fx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"fx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"fx_srv_{srv}", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("fx_addr_"):
        parts = data.split("_"); srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_fx_addr"; temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 88017):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"fx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("fx_dr_"):
        parts = data.split("_"); srv, cnt, rng = parts[2], parts[3], parts[4]
        fastx_hidden_ranges.add(f"{srv}|{rng}")
        if rng in bot_settings.get("fastx_services", {}).get(srv, {}).get(cnt, []):
            bot_settings["fastx_services"][srv][cnt].remove(rng); save_db()
        else:
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"fx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("fx_del_srv_"):
        srv = data.replace("fx_del_srv_", "")
        fastx_hidden_services.add(srv)
        bot_settings.get("fastx_services", {}).pop(srv, None); save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_fastx_srv", "id": call["id"]})

    elif data.startswith("fx_del_cnt_"):
        parts = data.split("_"); srv, cnt = parts[3], parts[4]
        fastx_hidden_countries.add(f"{srv}|{cnt}")
        bot_settings.get("fastx_services", {}).get(srv, {}).pop(cnt, None); save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"fx_srv_{srv}", "id": call["id"]})

    elif data == "fastx_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("fastx_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fxc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fastx_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "fastx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Fast X Allowed Search Countries:</b>\nOnly these country codes will be allowed in Fast X Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_fastx_search_country":
        user_states[chat_id] = "wait_for_add_fxc"; temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Fast X country code (e.g. 880):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "fastx_search_country", "style": "danger"}]]})

    elif data.startswith("del_fxc_"):
        idx = int(data.split("_")[-1]); arr = bot_settings.setdefault("fastx_search_countries", [])
        if 0 <= idx < len(arr): arr.pop(idx); save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "fastx_search_country", "id": call["id"]})

    elif data == "voltx_control":
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())

    elif data == "toggle_voltx_auto":
        bot_settings["voltx_auto"] = not bot_settings.get("voltx_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())
        answer_callback(call["id"], f"✅ Voltx Auto Range is now {'ON' if bot_settings['voltx_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_voltx_key":
        user_states[chat_id] = "wait_for_add_voltx_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Voltx API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}]]})

    elif data == "view_voltx_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("voltx_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vtx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Voltx Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_vtx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_keys", [])):
            del bot_settings["voltx_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_voltx_keys", "id": call["id"]})

    elif data == "voltx_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("voltx_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Voltx Allowed Ranges:</b>\nOnly these ranges/codes will be allowed in Voltx Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_voltx_search_country":
        user_states[chat_id] = "wait_for_add_vsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Voltx Range Code (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_search_country", "style": "danger"}]]})

    elif data.startswith("del_vsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_search_countries", [])):
            del bot_settings["voltx_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "voltx_search_country", "id": call["id"]})

    elif data == "manage_voltx_srv":
        kb = []
        srvs = bot_settings.get("voltx_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "vx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("⚡ <b>Voltx Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "vx_add_srv":
        user_states[chat_id] = "wait_vx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_srv_"):
        srv = data.replace("vx_srv_", "")
        kb = []
        countries = bot_settings["voltx_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_voltx_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_add_cnt_"):
        srv = data.replace("vx_add_cnt_", "")
        user_states[chat_id] = "wait_vx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["voltx_services"][srv].get(cnt, [])
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"vx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_vx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("vx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["voltx_services"].get(srv, {}).get(cnt, []):
            bot_settings["voltx_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("vx_del_srv_"):
        srv = data.replace("vx_del_srv_", "")
        if srv in bot_settings["voltx_services"]: del bot_settings["voltx_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_voltx_srv", "id": call["id"]})

    elif data.startswith("vx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["voltx_services"].get(srv, {}): del bot_settings["voltx_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_srv_{srv}", "id": call["id"]})

    # --- ZENEX CONTROL CALLBACKS ---
    elif data == "zenex_control":
        edit_message(chat_id, msg_id, render_body_text(f"💠 <b>Zenex Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('zenex_keys', []))}\nManage your Zenex API Keys below:"), reply_markup=zenex_control_keyboard())

    elif data == "toggle_zenex_auto":
        bot_settings["zenex_auto"] = not bot_settings.get("zenex_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"💠 <b>Zenex Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('zenex_keys', []))}\nManage your Zenex API Keys below:"), reply_markup=zenex_control_keyboard())
        answer_callback(call["id"], f"✅ Zenex Auto Range is now {'ON' if bot_settings['zenex_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_zenex_key":
        user_states[chat_id] = "wait_for_add_zenex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Zenex API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "danger"}]]})

    elif data == "view_zenex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("zenex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_znx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Zenex Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_znx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("zenex_keys", [])):
            del bot_settings["zenex_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Zenex Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_zenex_keys", "id": call["id"]})

    elif data == "zenex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("zenex_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_zsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_zenex_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Zenex Allowed Ranges:</b>\nOnly these codes will be allowed in Zenex Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_zenex_search_country":
        user_states[chat_id] = "wait_for_add_zsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Zenex Range Code (e.g. 447):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_search_country", "style": "danger"}]]})

    elif data.startswith("del_zsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("zenex_search_countries", [])):
            del bot_settings["zenex_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Zenex Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "zenex_search_country", "id": call["id"]})

    elif data == "manage_zenex_srv":
        kb = []
        for srv in bot_settings.get("zenex_services", {}):
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": "5257969839313526622", "callback_data": f"zx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "zx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("💠 <b>Zenex Services Manager</b>\nManage your API-based manual services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "zx_add_srv":
        user_states[chat_id] = "wait_zx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("zx_srv_"):
        srv = data.replace("zx_srv_", "")
        kb = []
        for c in bot_settings.get("zenex_services", {}).get(srv, {}):
            kb.append([{"text": f"{c} ({len(bot_settings['zenex_services'][srv][c])} Ranges)", "icon_custom_emoji_id": "5780471598922337683", "callback_data": f"zx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"zx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"zx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_zenex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("zx_add_cnt_"):
        srv = data.replace("zx_add_cnt_", "")
        user_states[chat_id] = "wait_zx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. UK, USA):"), reply_markup=get_cancel_kb())

    elif data.startswith("zx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["zenex_services"][srv].get(cnt, [])
        kb, row = [], []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"zx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"zx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"zx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"zx_srv_{srv}", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("zx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_zx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 4473845XXX):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"zx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("zx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["zenex_services"].get(srv, {}).get(cnt, []):
            bot_settings["zenex_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"zx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("zx_del_srv_"):
        srv = data.replace("zx_del_srv_", "")
        if srv in bot_settings["zenex_services"]: del bot_settings["zenex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_zenex_srv", "id": call["id"]})

    elif data.startswith("zx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["zenex_services"].get(srv, {}): del bot_settings["zenex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"zx_srv_{srv}", "id": call["id"]})

    elif data == "manage_fj":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "toggle_fj":
        bot_settings["fj_on"] = not bot_settings["fj_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "add_fj":
        user_states[chat_id] = "wait_for_add_fj"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Channel Username or Invite Link:\n<i>(Note: For private channels, use the numeric ID like -100...)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})

    elif data.startswith("del_fj_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fj_channels"]):
            del bot_settings["fj_channels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Channel deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "manage_admins":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "add_adm":
        user_states[chat_id] = "wait_for_add_adm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID of the new Admin:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_admins", "style": "danger"}]]})

    elif data.startswith("del_adm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["admins"]):
            del bot_settings["admins"][idx]
            save_db()
            answer_callback(call["id"], "✅ Admin deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "manage_otp_groups":
        edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "add_fw":
        user_states[chat_id] = "wait_for_add_fw_id"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Group ID/Username to forward messages to:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data.startswith("manage_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            grp_id = bot_settings["fw_groups"][idx]["chat_id"]
            edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {grp_id}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("add_fwbtn_"):
        idx = int(data.split("_")[2])
        user_states[chat_id] = "wait_for_add_fw_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "fw_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Custom Inline Button format:\n<code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_fw_{idx}", "style": "danger"}]]})

    elif data.startswith("del_fwbtn_"):
        parts = data.split("_")
        idx, b_idx = int(parts[2]), int(parts[3])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            if 0 <= b_idx < len(bot_settings["fw_groups"][idx]["buttons"]):
                del bot_settings["fw_groups"][idx]["buttons"][b_idx]
                save_db()
                answer_callback(call["id"], "✅ Button deleted!", show_alert=True)
                edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("del_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            del bot_settings["fw_groups"][idx]
            save_db()
            answer_callback(call["id"], "✅ Group deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "edit_otp_link":
        user_states[chat_id] = "wait_for_otp_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new OTP Group Link:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "manage_panels":
        text = (f"{PEM['gear']} <b>Panel Management</b>\n\n"
                f"{PEM['ok']} <b>Green:</b> Active\n"
                f"{PEM['no']} <b>Red:</b> Stopped\n\n"
                f"Select a provider to manage it in one click:")
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_management_keyboard())

    elif data == "add_more_panel":
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['gear']} <b>Add More Panel</b>\n\nSelect panel type:"),
            reply_markup=panel_type_actions_keyboard())

    elif data == "panel_type_api":
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['world']} <b>API Panel</b>\n\nChoose an action:"),
            reply_markup=panel_type_manage_keyboard("API Panel"))

    elif data == "panel_type_cpt":
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['lock']} <b>Auto Captcha Panel</b>\n\nChoose an action:"),
            reply_markup=panel_type_manage_keyboard("Auto Captcha Panel"))

    elif data == "delete_panel_type":
        # Show every removable custom panel together, without asking for a panel type first.
        kb = []
        for idx, p in enumerate(bot_settings.get("panels", [])):
            name = str(p.get("name", "")).strip()
            if not name:
                continue
            # KSI IPRN is a built-in/default provider; keep it protected.
            if name.lower() == "ksi iprn":
                continue
            p_type = str(p.get("type", "API Panel"))
            if p_type not in ("API Panel", "Auto Captcha Panel"):
                continue
            kb.append([{
                "text": name,
                "icon_custom_emoji_id": "5422557736330106570",
                "callback_data": f"confirm_del_pnl_{idx}",
                "style": "danger"
            }])
        if not kb:
            kb.append([{"text": "No removable panels", "icon_custom_emoji_id": "5420130255174145507",
                        "callback_data": "manage_panels", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176",
                    "callback_data": "manage_panels", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['trash']} <b>Delete Panel</b>\n\nSelect a panel to delete:"),
            reply_markup={"inline_keyboard": kb})

    elif data.startswith("confirm_del_pnl_"):
        idx = int(data.split("_")[-1])
        if 0 <= idx < len(bot_settings.get("panels", [])):
            p = bot_settings["panels"][idx]
            name = str(p.get("name", "")).strip()
            if name.lower() == "ksi iprn":
                answer_callback(call["id"], "This provider cannot be deleted.", show_alert=True)
            else:
                edit_message(chat_id, msg_id, render_body_text(
                    f"{PEM['trash']} <b>Delete Panel?</b>\n\n<b>{html.escape(name)}</b>\n\nConfirm deletion:"),
                    reply_markup={"inline_keyboard": [
                        [{"text": "Confirm Delete", "icon_custom_emoji_id": "5422557736330106570",
                          "callback_data": f"do_del_pnl_{idx}", "style": "danger"}],
                        [{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176",
                          "callback_data": "delete_panel_type", "style": "primary"}]
                    ]})

    elif data in ["legacy_voltx", "legacy_stex", "legacy_zenex"]:
        target = {
            "legacy_voltx": "voltx_control",
            "legacy_stex": "stex_control",
            "legacy_zenex": "zenex_control",
        }[data]
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id},
                         "data": target, "id": "internal"})

    elif data == "bangla_panel":
        # Keep Bangla providers two-per-row, matching the older layout.
        kb = {"inline_keyboard": [
            [{"text": "StexSMS Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_control", "style": "success"},
             {"text": "Voltx Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_control", "style": "primary"}],
            [{"text": "Zenex Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "zenex_control", "style": "success"},
             {"text": "Fast X Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "fastx_control", "style": "success"}],
            [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text("<b>Bangla Panel</b>\n\nManage Bangla Panel providers below:"), reply_markup=kb)

    elif data in ["manage_api_panels", "manage_cpt_panels"]:
        p_type = "API Panel" if data == "manage_api_panels" else "Auto Captcha Panel"
        p_list = [p for p in bot_settings["panels"] if p.get("type", "API Panel") == p_type]
        icon = f"{PEM['world']} API" if p_type == 'API Panel' else f"{PEM['lock']} Auto Captcha"
        
        text = f"{icon} <b>{p_type}s Management</b>\n\n👀 <b>Active Monitors:</b> {len(p_list)}\n\n🟢 <b>Available Providers:</b>\n"
        for p in p_list:
            status = "Monitoring" if p['status'] == 'ON' else "Stopped"
            login_state = p.get('login_status', '')
            if p['type'] == 'Auto Captcha Panel':
                conf = f" {login_state}" if login_state else f"{PEM['ok']} Configured"
            else:
                conf = f"{PEM['ok']} Configured" if p.get('api_url') else f"{PEM['no']} Not Configured"
            text += f"• {p['name']}: {PEM['ok'] if p['status']=='ON' else PEM['no']} {status} | {conf}\n"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=typed_panels_list_keyboard(p_type))

    elif data == "add_ksi_iprn":
        existing = next((i for i, p in enumerate(bot_settings.get("panels", [])) if str(p.get("name", "")).strip().lower() == "ksi iprn"), None)
        if existing is None:
            bot_settings.setdefault("panels", []).append({
                "name": "KSI IPRN", "type": "API Panel", "status": "OFF",
                "api_url": "https://www.ksiiprn.com/api/v1/iprn/messages",
                "token": KSI_IPRN_API_KEY, "full_api_url": "", "records": 0, "auth_mode": "bearer"
            })
            save_db()
            existing = len(bot_settings["panels"]) - 1
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"conf_pnl_{existing}", "id": "internal"})

    elif data in ["add_api_panel", "add_cpt_panel"]:
        user_states[chat_id] = "wait_for_panel_name"
        p_type = "api" if data == "add_api_panel" else "logc"
        temp_data[chat_id] = {"msg_id": msg_id, "add_type": p_type}
        edit_message(chat_id, msg_id, render_body_text("📝 Please send the name of the New Provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='api' else 'cpt'}_panels", "style": "danger"}]]})

    elif data.startswith("add_ptype_"):
        pass

    elif data in ["list_del_api", "list_del_cpt"]:
        p_type = "API Panel" if data == "list_del_api" else "Auto Captcha Panel"
        kb = []
        for idx, p in enumerate(bot_settings["panels"]):
            if p.get("type", "API Panel") == p_type:
                kb.append([{"text": f"Delete {p['name']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"do_del_pnl_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['trash']} <b>Select a Provider to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("do_del_pnl_"):
        idx = int(data.split("_")[3])
        if 0 <= idx < len(bot_settings["panels"]):
            p_type = bot_settings["panels"][idx].get("type", "API Panel")
            del bot_settings["panels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Provider Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_panels", "id": "internal"})

    elif data.startswith("tog_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            
            p["status"] = "ON" if p["status"] == "OFF" else "OFF"
            save_db()
            
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("conf_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>\n<b>Num Col:</b> {p.get('num_col_name')} (Idx: {p.get('num_col_idx')})\n<b>Msg Col:</b> {p.get('msg_col_name')} (Idx: {p.get('msg_col_idx')})"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("set_p_api_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_api"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the API URL for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_tok_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_tok"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the API Key for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_fapi_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_fapi"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the FULL API URL (Example: http://api.com/get?key=YOUR_TOKEN&start=0):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_rec_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_rec"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the number of records to fetch (e.g. 10).\nType <code>0</code> for Unlimited:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("test_p_conn_"):
        idx = int(data.split("_")[3])
        p = bot_settings["panels"][idx]
        wait_msg = send_message(chat_id, render_body_text("⏳ Testing connection. Please wait..."))
        wait_msg_id = wait_msg.get("result", {}).get("message_id") if wait_msg else None
        answer_callback(call["id"])
        
        try:
            parsed = []
            raw_text = ""
            
            if p["type"] == "Auto Captcha Panel":
                sess = panel_sessions.get(idx)
                if not sess:
                    success = attempt_auto_login(p, idx)
                    if not success:
                        if wait_msg_id: delete_message(chat_id, wait_msg_id)
                        send_message(chat_id, render_body_text(f"❌ <b>Auto Login Failed!</b>\nReason: {html.escape(str(p.get('login_status', 'Unknown')))}"))
                        return
                    sess = panel_sessions.get(idx)
                    
                login_url = p.get("login_url", "").strip()
                if not login_url.startswith("http"): login_url = "http://" + login_url
                msg_link = p.get("msg_link", "").strip()
                if not msg_link.startswith("http") and msg_link != "": msg_link = "http://" + msg_link
                check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
                
                # 🌟 test connection supports sAjaxSource & HTML table parser
                parsed, raw_text = fetch_cpt_panel_cdrs(p, sess, check_url)
                
            else:
                full_url = p.get("full_api_url", "").strip()
                url = p.get("api_url", "").strip()
                token = p.get("token", "").strip()
                if not full_url and not url:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Please Set API URL or Full API URL first!"))
                    return

                is_ksi = str(p.get("name", "")).strip().lower() == "ksi iprn"
                if is_ksi:
                    urls_to_try = [ksi_iprn_messages_url(url)]
                elif full_url:
                    urls_to_try = [full_url]
                else:
                    urls_to_try = []
                    if "{token}" in url or "{key}" in url:
                        urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                    elif "token=" in url or "key=" in url:
                        urls_to_try.append(url)
                    else:
                        sep = '&' if '?' in url else '?'
                        urls_to_try.extend([f"{url}{sep}token={token}", f"{url}{sep}key={token}&start=0", f"{url}{sep}key={token}"])

                parsed = []
                raw_text = ""
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                if is_ksi:
                    if not token:
                        if wait_msg_id: delete_message(chat_id, wait_msg_id)
                        send_message(chat_id, render_body_text("❌ KSI IPRN API key is missing."))
                        return
                    headers['Authorization'] = f'Bearer {token}'

                for try_url in urls_to_try:
                    try:
                        res = requests.get(try_url, headers=headers, timeout=10)
                        raw_text = res.text
                        if res.status_code in (401, 403, 429):
                            break
                        parsed = parse_panel_response(raw_text, p)
                        if parsed:
                            break
                    except Exception:
                        pass

            if wait_msg_id: delete_message(chat_id, wait_msg_id)
                 
            if parsed:
                txt = f"✅ <b>Connection Successful!</b>\n\n🎯 <b>Parsed Data Sample (Max 3):</b>\n\n"
                
                for i, sample in enumerate(parsed[:3]):
                    num = sample['number']
                    msg = sample['message']
                    otp = sample['otp']
                    
                    detected_app = detect_service(msg)
                    app_name = detected_app if detected_app else p.get("name", "Unknown")
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg)
                    
                    txt += f"<b>{i+1}.</b> {prem_app_html} <b>{app_full_name}</b>\n"
                    txt += f"📱 Number: <code>{num}</code>\n"
                    txt += f"📝 Full Msg: <code>{html.escape(msg)}</code>\n"
                    txt += f"🔐 OTP: <code>{otp}</code>\n"
                    txt += "➖" * 12 + "\n"
                    
                send_message(chat_id, render_body_text(txt))
            else:
                if p["type"] == "Auto Captcha Panel":
                    try:
                        soup = BeautifulSoup(raw_text, 'html.parser')
                        tables = soup.find_all('table')
                        if tables:
                            full_table_data = "🔍 FULL TABLE DATA (A-Z)\n" + "="*50 + "\n\n"
                            for t_idx, table in enumerate(tables):
                                full_table_data += f"--- Table {t_idx+1} ---\n"
                                rows = table.find_all('tr')
                                for r_idx, row in enumerate(rows):
                                    cols = row.find_all(['th', 'td'])
                                    col_texts = [f"[{c_idx+1}] {c.get_text(separator=' ', strip=True)}" for c_idx, c in enumerate(cols)]
                                    full_table_data += f"Row {r_idx+1}: {' | '.join(col_texts)}\n"
                                full_table_data += "\n" + "="*50 + "\n"
                            
                            send_document(chat_id, f"Full_Panel_Data_{idx}.txt", full_table_data.encode('utf-8'))
                            fail_txt = f"⚠️ <b>Connected, but couldn't parse OTP data!</b>\n\n<i>আমি ওই লিংকের সম্পূর্ণ (A-Z) ডাটা একটি Text File এ পাঠিয়েছি। ফাইলটি ওপেন করে সঠিক Column Number (যেমন: [1], [3]) চেক করে প্যানেলে আপডেট করে নাও।</i>"
                            send_message(chat_id, render_body_text(fail_txt))
                        else:
                            send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but no HTML Table found!</b>\nMake sure the message link is correct."))
                    except Exception as e:
                        send_message(chat_id, render_body_text(f"❌ <b>Error parsing HTML:</b> {html.escape(str(e))}"))
                else:
                    safe_html = html.escape(str(raw_text)[:300])
                    send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but couldn't find/parse OTP data.</b>\n\n<i>Make sure your API config is correct.</i>\n\nRaw HTML/Data (excerpt):\n<code>{safe_html}...</code>"))
        except Exception as e:
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
            send_message(chat_id, render_body_text(f"❌ <b>Connection Failed!</b>\nError: {html.escape(str(e))}"))

    elif data == "support_management":
        if not is_admin(chat_id): return
        edit_message(chat_id, msg_id, support_management_text(), reply_markup=support_management_keyboard())
        answer_callback(call["id"])

    elif data == "support_edit_link":
        if not is_admin(chat_id): return
        user_states[chat_id] = "support_admin_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['msg']} <b>EDIT SUPPORT LINK</b>\n\nSend the new Telegram support link.\nExample: <code>https://t.me/your_support</code>"), reply_markup={"inline_keyboard":[[{"text":"CANCEL","icon_custom_emoji_id":"5267490665117275176","callback_data":"support_management","style":"danger"}]]})
        answer_callback(call["id"])

    elif data == "support_edit_name":
        if not is_admin(chat_id): return
        user_states[chat_id] = "support_admin_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['msg']} <b>EDIT SUPPORT BUTTON NAME</b>\n\nSend the new name for the Support button."), reply_markup={"inline_keyboard":[[{"text":"CANCEL","icon_custom_emoji_id":"5267490665117275176","callback_data":"support_management","style":"danger"}]]})
        answer_callback(call["id"])

    elif data == "support_start":
        user_states[chat_id] = "support_wait_message"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['msg']} <b>SUPPORT MESSAGE</b>\n\nSend your problem/message now. It will be delivered to the admin.\n\n<i>After sending, wait for the admin reply.</i>"), reply_markup={"inline_keyboard":[[{"text":"CANCEL","icon_custom_emoji_id":"5267490665117275176","callback_data":"close_msg","style":"danger"}]]})
        answer_callback(call["id"])

    elif data.startswith("support_reply_"):
        if not is_admin(chat_id): return
        target = data.replace("support_reply_", "", 1)
        user_states[chat_id] = "support_admin_reply"
        temp_data[chat_id] = {"msg_id": msg_id, "target_user": target}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['msg']} <b>REPLY TO USER</b>\n\nSend your reply message now."), reply_markup={"inline_keyboard":[[{"text":"CANCEL","icon_custom_emoji_id":"5267490665117275176","callback_data":"close_msg","style":"danger"}]]})
        answer_callback(call["id"])

    elif data.startswith("support_close_"):
        if not is_admin(chat_id): return
        target = data.replace("support_close_", "", 1)
        send_message(target, render_body_text(f"{PEM['msg']} <b>Support ticket closed.</b>\n\nIf you need more help, open Support again."), reply_markup=main_menu(target))
        delete_message(chat_id, msg_id)
        answer_callback(call["id"], "Support ticket closed.")

    elif data == "dxa_sup_link":
        if not is_admin(chat_id): return
        edit_message(chat_id, msg_id, support_management_text(), reply_markup=support_management_keyboard())
        answer_callback(call["id"])

    elif data == "console_otp_toggle":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can change Console OTP.", show_alert=True)
            return
        bot_settings["console_otp"] = not bool(bot_settings.get("console_otp", False))
        save_db()
        style = "success" if bot_settings["console_otp"] else "danger"
        kb = admin_panel_keyboard()
        # admin_panel_keyboard reads the saved state and sets the correct color.
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['ok'] if bot_settings['console_otp'] else PEM['no']} "
            f"<b>Console OTP {'Enabled' if bot_settings['console_otp'] else 'Disabled'}</b>"
        ), reply_markup=kb)
        answer_callback(call["id"])
        return

    elif data == "console_traffic_cycle":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can change Consol Traffic.", show_alert=True)
            return
        mode = str(bot_settings.get("console_traffic_mode", "on")).lower()
        if mode not in ("off", "on", "all"):
            mode = "on" if bot_settings.get("console_traffic", True) else "off"
        # Cycle: ON (green) -> OFF (blue) -> ALL ON (red) -> ON
        next_mode = {"on": "off", "off": "all", "all": "on"}[mode]
        bot_settings["console_traffic_mode"] = next_mode
        # Keep legacy boolean in sync for compatibility.
        bot_settings["console_traffic"] = next_mode != "off"
        save_db()
        style = {"on": "success", "off": "primary", "all": "danger"}[next_mode]
        traffic_kb = {"inline_keyboard": [
            [{"text": "Consol Traffic", "icon_custom_emoji_id": "5203993413346680064", "callback_data": "console_traffic_cycle", "style": style}],
            [{"text": "Set Traffic Time", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "traffic_time_custom", "style": "primary"}],
            [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
        ]}
        answer_callback(call["id"])
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Edit TRAFFIC</b>\n\nCurrent traffic window: <b>{max(1, int(bot_settings.get('traffic_window_minutes', 30)))} minutes</b>\n\nConsol Traffic mode updated."), reply_markup=traffic_kb)

    elif data == "dxa_control":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can access DXA Control.", show_alert=True)
            return
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
        answer_callback(call["id"])

    elif data == "dxa_toggle_w":
        bot_settings["withdraw_on"] = not bot_settings["withdraw_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())

    elif data == "manage_w_methods":
        edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data == "add_wm":
        user_states[chat_id] = "wait_for_add_wm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the name of the new Withdrawal Method:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_w_methods", "style": "danger"}]]})

    elif data.startswith("del_wm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["w_methods"]):
            del bot_settings["w_methods"][idx]
            save_db()
            answer_callback(call["id"], "✅ Method deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data == "withdraw_requests":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can view withdrawal requests.", show_alert=True)
            return
        count = len(pending_withdrawals)
        if count == 0:
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['money']} <b>WITHDRAWAL REQUESTS</b>\n\n{PEM['ok']} No pending withdrawal requests."),
                         reply_markup={"inline_keyboard":[
                             [{"text":"REFRESH","icon_custom_emoji_id":"5352694861990501856","callback_data":"withdraw_requests","style":"primary"}],
                             [{"text":"BACK","icon_custom_emoji_id":"5267490665117275176","callback_data":"dxa_control","style":"danger"}]
                         ]})
            return
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['money']} <b>WITHDRAWAL REQUESTS</b>\n\n{PEM['lock']} <b>PENDING:</b> {count}"),
                     reply_markup={"inline_keyboard":[
                         [{"text":"REFRESH","icon_custom_emoji_id":"5352694861990501856","callback_data":"withdraw_requests","style":"primary"}],
                         [{"text":"BACK","icon_custom_emoji_id":"5267490665117275176","callback_data":"dxa_control","style":"danger"}]
                     ]})
        for req_id, req_data in list(pending_withdrawals.items()):
            result = send_message(chat_id, withdrawal_request_text(req_id, req_data), reply_markup=withdrawal_request_keyboard(req_id))
            if not result or result.get("ok") is not True:
                print(f"Withdrawal request message failed for {req_id}: {result}")

    elif data == "dxa_otp_r":
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can change OTP rewards.", show_alert=True)
            return
        edit_message(chat_id, msg_id, render_body_text(
            "💰 <b>OTP REWARD</b>\n\nSelect a Bangla panel to set its own User/Special User OTP reward rate:"
        ), reply_markup=otp_reward_panel_keyboard())
        answer_callback(call["id"])

    elif data.startswith("otp_reward_panel:"):
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can change OTP rewards.", show_alert=True)
            return
        panel_key = data.split(":", 1)[1]
        if panel_key not in {"voltx", "stexsms", "zenex", "fastx"}:
            answer_callback(call["id"], "Invalid panel.", show_alert=True)
            return
        bot_settings.setdefault("panel_otp_rewards", {}).setdefault(
            panel_key, {"user": float(bot_settings.get("otp_reward", 0.0)), "special": float(bot_settings.get("otp_reward", 0.0))}
        )
        rates = bot_settings["panel_otp_rewards"][panel_key]
        edit_message(chat_id, msg_id, render_body_text(
            f"💰 <b>{otp_reward_panel_name(panel_key)} OTP REWARD</b>\n\n"
            f"👤 User Reward: <b>{rates.get('user', 0)}</b> TK\n"
            f"⭐ Special User Reward: <b>{rates.get('special', 0)}</b> TK\n\n"
            "Choose which rate you want to change:"
        ), reply_markup=otp_reward_panel_manage_keyboard(panel_key))
        answer_callback(call["id"])

    elif data.startswith("set_panel_reward:"):
        if not is_admin(chat_id):
            answer_callback(call["id"], "Only Bot Admins can change OTP rewards.", show_alert=True)
            return
        parts = data.split(":")
        if len(parts) != 3 or parts[1] not in {"voltx", "stexsms", "zenex", "fastx"} or parts[2] not in {"user", "special"}:
            answer_callback(call["id"], "Invalid reward setting.", show_alert=True)
            return
        panel_key, rate_type = parts[1], parts[2]
        user_states[chat_id] = "set_panel_otp_reward"
        temp_data[chat_id] = {"msg_id": msg_id, "panel_key": panel_key, "rate_type": rate_type}
        label = "User Reward" if rate_type == "user" else "Special User Reward"
        edit_message(chat_id, msg_id, render_body_text(
            f"💰 <b>{otp_reward_panel_name(panel_key)} - {label}</b>\n\n"
            "Send the reward amount in TK. Example: <code>0.50</code>"
        ), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"otp_reward_panel:{panel_key}", "style": "danger"}]]})
        answer_callback(call["id"])

    elif data.startswith("dxa_"):
        key = data.replace("dxa_", "")
        key_map = {"min_w": "min_withdraw", "otp_r": "otp_reward", "cool": "cooldown", "num_req": "num_req", "num_share": "num_share", "sup_link": "support_link"}
        if key in key_map:
            temp_data[chat_id] = {"msg_id": msg_id, "key": key_map[key]}
            user_states[chat_id] = "set_dxa"
            cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_dxa_edit", "style": "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(f"📝 Please send the new value for <code>{key_map[key]}</code>:"), reply_markup=cancel_kb)
            answer_callback(call["id"])

    elif data == "back_to_services":
        all_services = set(build_active_service_keyboard())
        
        if not all_services:
            answer_callback(call["id"], "❌ No numbers or services available!", show_alert=True)
            return
            
        c_msg = bot_settings["custom_messages"].get("get_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
        
        apps_db = bot_settings.get("premium_apps", {})
        kb = []
        service_buttons = []
        for s in sorted(all_services, key=lambda x: str(x).lower()):
            emoji_id = "5352694861990501856"
            for app_key, app_data in apps_db.items():
                if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            service_buttons.append({"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"})
        for i in range(0, len(service_buttons), 2):
            kb.append(service_buttons[i:i + 2])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_s_"):
        service=data.split("g_s_",1)[1]
        c_msg=bot_settings.get("custom_messages",{}).get("select_country",{})
        txt=render_body_text(c_msg.get("text","📌 Select a country for {service}:").replace("{service}",service))
        kb=[]; buttons=build_provider_country_buttons(service)
        for i in range(0,len(buttons),2): kb.append(buttons[i:i+2])
        custom=[]
        for b in c_msg.get("buttons",[]):
            b2=b.copy(); b2.setdefault("style","primary"); custom.append(b2)
        for i in range(0,len(custom),2): kb.append(custom[i:i+2])
        kb.append([{"text":"Back","icon_custom_emoji_id":"5267490665117275176","callback_data":"back_to_services","style":"danger"}])
        edit_message(chat_id,msg_id,txt,reply_markup={"inline_keyboard":kb})

    elif data.startswith("g_p:"):
        try:
            _,pk,es,ec=data.split(":",3); service=_decode_cb_part(es); country=_decode_cb_part(ec)
        except Exception:
            answer_callback(call["id"],"❌ Invalid country selection.",show_alert=True); return
        if pk not in {k for k,_ in get_active_bangla_providers()} and pk!="local":
            answer_callback(call["id"],"❌ This panel is currently OFF or not connected.",show_alert=True); return
        handle_callback({"message":call["message"],"data":f"g_c_{service}_{country}__p={pk}","id":call["id"]}); return

    elif data.startswith("fastx_get_") or data.startswith("fastx_change_"):
        if not any(k == "fastx" for k, _ in get_active_bangla_providers()):
            answer_callback(call["id"], "❌ Fast X is currently OFF or Auto Range is OFF.", show_alert=True)
            return
        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Please wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s.", show_alert=True)
            return

        # IMPORTANT: For Change Number, keep the exact Fast X range used by the
        # currently assigned number.  Previously we called expire_previous_number()
        # first and then rebuilt the request only from the country name.  That
        # converted a live Fast X range (for example a provider-specific range)
        # back to the generic calling code, which could make /getnum return no
        # stock even though the original range still had numbers.
        is_fastx_change = data.startswith("fastx_change_")
        previous_range = ""
        previous_service = "Fast X"
        if is_fastx_change:
            prev_session = user_active_sessions.get(chat_id, {})
            prev_nums = prev_session.get("nums", []) if isinstance(prev_session, dict) else []
            if prev_nums:
                previous_range = str(fastx_assigned_ranges.get(str(prev_nums[0]), "") or "").strip()
                if not previous_range:
                    previous_range = str(fastx_assigned_ranges.get(str(prev_nums[0]).lstrip("+"), "") or "").strip()
            previous_service = str(prev_session.get("service", "Fast X") or "Fast X") if isinstance(prev_session, dict) else "Fast X"

        user_cooldowns[chat_id] = now
        expire_previous_number(chat_id)
        prefix = "fastx_get_" if data.startswith("fastx_get_") else "fastx_change_"
        country_name = data.split(prefix, 1)[1]
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing... Finding Fast X Number...</i>"))
        fastx_build_number_message(
            chat_id, msg_id, call, country_name,
            service_name=previous_service if is_fastx_change else "Fast X",
            range_override=previous_range or None
        )
        return

    elif data.startswith("g_c_") or data.startswith("c_n_"):
        provider_hint=None
        if "__p=" in data: data,provider_hint=data.split("__p=",1)
        # ১. গ্লোবাল কুলডাউন চেক (সকল নাম্বার মেথডের জন্য)
        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Please wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s.", show_alert=True)
            return
        
        # কুলডাউন আপডেট
        user_cooldowns[chat_id] = now
        
        # আগের নাম্বার এক্সপায়ার করা
        expire_previous_number(chat_id)

        # যদি সার্চ নাম্বার থেকে আসে
        if data.startswith("c_n_s_"):
            is_voltx_req = data.endswith("_vtx")
            is_fastx_req = data.endswith("_fx")
            if is_fastx_req:
                clean_data = data[:-3]
            else:
                clean_data = data[:-4] if is_voltx_req else data
            parts_s = clean_data.split("_", 4)
            
            query = parts_s[3] if len(parts_s) > 3 else ""
            service_from_cb = parts_s[4] if len(parts_s) > 4 else None
            
            allowed_countries = bot_settings.get("search_countries", [])
            voltx_allowed = bot_settings.get("voltx_search_countries", [])
            
            zenex_allowed = bot_settings.get("zenex_search_countries", [])
            fastx_allowed = bot_settings.get("fastx_search_countries", [])
            
            is_stex_allowed = any(query.startswith(c) for c in allowed_countries) if allowed_countries else False
            is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
            is_zenex_allowed = any(query.startswith(c) for c in zenex_allowed) if zenex_allowed else False
            is_fastx_allowed = any(query.startswith(c) for c in fastx_allowed) if fastx_allowed else False
            is_zenex_req = data.endswith("_znx")
            
            if not is_voltx_req and not is_zenex_req and not is_fastx_req and not is_stex_allowed and not is_voltx_allowed and not is_zenex_allowed and not is_fastx_allowed:
                answer_callback(call["id"], "❌ This country code is not allowed for search!", show_alert=True)
                return
                
            edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = msg_id
            
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                api_found = False
                req_count = bot_settings.get("num_req", 1)
                
                # Fast X search uses the same API key + range workflow as normal Fast X.
                if (provider_hint == "fastx") or (not provider_hint and (is_fastx_allowed or is_fastx_req)):
                    fastx_keys = bot_settings.get("fastx_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in fastx_keys:
                            result = fastx_fetch_number(query, api_key)
                            if result and result.get("number"):
                                num_str = str(result["number"]).replace("+", "")
                                if num_str and num_str not in fetched_nums:
                                    fetched_nums.append(num_str)
                                    ksi_assigned_numbers[num_str] = chat_id
                                    fastx_assigned_numbers[num_str] = chat_id
                                    api_found = True
                                    total_assigned_stats += 1
                                break

                # প্রথমে Zenex চেক করবে
                if len(fetched_nums) < req_count and (provider_hint == "zenex" or (not provider_hint and (is_zenex_allowed or is_zenex_req))) and not is_fastx_req and provider_hint != "fastx":
                    zenex_keys = bot_settings.get("zenex_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in zenex_keys:
                            try:
                                headers = {"mapikey": api_key}
                                payload = {"range": query, "is_national": False, "remove_plus": False}
                                res = requests.post(f"{ZENEX_BASE_URL}/v1/getnum", json=payload, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("full_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("number", "")).replace("+", "")
                                    fetched_nums.append(num_str)
                                    ksi_assigned_numbers[num_str] = chat_id
                                    zenex_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    is_zenex_req = True 
                                    break
                            except: continue

                # তারপর Voltx চেক করবে
                if len(fetched_nums) < req_count and (provider_hint == "voltx" or (not provider_hint and (is_voltx_allowed or is_voltx_req))) and not is_zenex_req and not is_fastx_req and provider_hint not in {"fastx", "zenex"}:
                    voltx_keys = bot_settings.get("voltx_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in voltx_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                payload = {"rid": query}
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json=payload, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    ksi_assigned_numbers[num_str] = chat_id
                                    voltx_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    is_voltx_req = True # মার্ক করে দিলাম যাতে পরবর্তীতে Voltx রিকোয়েস্ট হিসেবে কাজ করে
                                    break
                            except: continue

                # Voltx এ না পেলে বা আরও নাম্বার লাগলে StexSMS তে চেক করবে
                if len(fetched_nums) < req_count and (provider_hint == "stexsms" or (not provider_hint and is_stex_allowed)) and not is_voltx_req and not is_zenex_req and not is_fastx_req and provider_hint not in {"fastx", "zenex", "voltx"}:
                    stex_keys = bot_settings.get("stex_keys", [])
                    for _ in range(req_count - len(fetched_nums)):
                        for api_key in stex_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    ksi_assigned_numbers[num_str] = chat_id
                                    stex_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    break
                            except: continue
                        
                if not api_found:
                    answer_callback(call["id"], "❌ Number out of stock!", show_alert=True)
                    delete_message(chat_id, wait_msg_id)
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    fetched_nums.append(num_str)
                    ksi_assigned_numbers[num_str] = chat_id
                    
                    # 🌟 Save File Specific Rate
                    assigned_number_rates[num_str] = {"normal": float(number_batches[b_id].get("normal_rate", number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0)))), "special": float(number_batches[b_id].get("special_rate", number_batches[b_id].get("normal_rate", number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0)))))}
                    
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
                
            kb = []
            if service_from_cb:
                app_full_name, _ = get_service_info_html(service_from_cb)
                emoji_id_srv = "5337302974806922068"
                for app_key, app_data in bot_settings.get("premium_apps", {}).items():
                    if service_from_cb.upper() == app_key or service_from_cb.upper() in app_key or app_key in service_from_cb.upper():
                        if "id" in app_data: emoji_id_srv = app_data["id"]; break
                kb.append([{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id_srv, "callback_data": "ignore", "style": "primary"}])

            flags_db = bot_settings.get("premium_flags", {})
            country_emoji_html = ""
            for num in fetched_nums:
                char_flag, iso = get_flag_and_code(num)
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                flag_emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: 
                            flag_emoji_id = flag_data["id"]
                            country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                        break
                if not country_emoji_html: country_emoji_html = char_flag
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": "success"}])
            
            vtx_ext = "_vtx" if is_voltx_req else "_znx" if is_zenex_req else "_fx" if is_fastx_req else ""
            srv_ext = f"_{service_from_cb}" if service_from_cb else ""
            change_buttons = [{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{srv_ext}{vtx_ext}", "style": "danger"}]
            if service_from_cb:
                change_buttons.append({"text": "Change Country", "icon_custom_emoji_id": "5305517382138112561", "callback_data": f"g_s_{service_from_cb}", "style": "danger"})
            kb.append(change_buttons)

            # Custom inline buttons: 2 per row.
            c_btns = []
            for c_b in bot_settings["custom_messages"].get("search_number", {}).get("buttons", []):
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                c_btns.append(b_copy)
            for i in range(0, len(c_btns), 2):
                kb.append(c_btns[i:i + 2])

            # OTP Group stays on its own row.
            kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            
            # Build the NEW NUMBER message context from the search callback.
            # `country` and `service` are not defined in this c_n_s_ branch.
            # Derive them from the fetched number and callback service so a
            # custom NEW NUMBER template cannot break the number-delivery flow.
            display_country = get_flag_info_html(fetched_nums[0], return_full_name=True).title() if fetched_nums else query
            display_service = service_from_cb or ""
            if display_service:
                display_service, _ = get_service_info_html(display_service)

            text_numbers, new_number_custom_kb = render_new_number_message(
                country_emoji_html, display_country, display_service
            )
            kb.extend(new_number_custom_kb)
            edit_message(chat_id, wait_msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
            return

        # যদি আপলোড করা বা সার্ভিস থেকে আসে
        parts = data.split("_")
        service = parts[2]
        country = parts[3]

        available_indices = []
        # Check Local Stock First
        for b_id, b_data in number_batches.items():
            if b_data["service"] == service and b_data["country"] == country:
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if chat_id not in n_obj.get("used_by", []):
                        available_indices.append((b_id, idx))

        # IF NO LOCAL STOCK, use only the selected active Bangla panel.
        if not available_indices:
            stex_srv_data=bot_settings.get("stex_services",{}).get(service,{}).get(country)
            voltx_srv_data=bot_settings.get("voltx_services",{}).get(service,{}).get(country)
            zenex_srv_data=bot_settings.get("zenex_services",{}).get(service,{}).get(country)
            fastx_srv_data=bot_settings.get("fastx_services",{}).get(service,{}).get(country)
            target_range=None; is_voltx=False; is_zenex=False; is_fastx=False
            if provider_hint=="stexsms" and stex_srv_data: target_range=random.choice(stex_srv_data)
            elif provider_hint=="voltx" and voltx_srv_data: target_range=random.choice(voltx_srv_data); is_voltx=True
            elif provider_hint=="zenex" and zenex_srv_data: target_range=random.choice(zenex_srv_data); is_zenex=True
            elif provider_hint=="fastx" and fastx_srv_data and bot_settings.get("fastx_keys"):
                fastx_build_number_message(chat_id,msg_id,call,country,service_name=service,range_override=random.choice(fastx_srv_data)); return
            elif provider_hint is None:
                if stex_srv_data and bot_settings.get("stex_auto") and bot_settings.get("stex_keys"): target_range=random.choice(stex_srv_data)
                elif voltx_srv_data and bot_settings.get("voltx_auto") and bot_settings.get("voltx_keys"): target_range=random.choice(voltx_srv_data); is_voltx=True
                elif zenex_srv_data and bot_settings.get("zenex_auto") and bot_settings.get("zenex_keys"): target_range=random.choice(zenex_srv_data); is_zenex=True
                elif fastx_srv_data and bot_settings.get("fastx_enabled",FASTX_ENABLED_DEFAULT) and bot_settings.get("fastx_auto") and bot_settings.get("fastx_keys"):
                    fastx_build_number_message(chat_id,msg_id,call,country,service_name=service,range_override=random.choice(fastx_srv_data)); return

            if target_range:
                user_cooldowns[chat_id] = 0
                vtx_flag = "_vtx" if is_voltx else "_znx" if is_zenex else ""
                handle_callback({"message": call["message"], "data": f"c_n_s_{target_range}_{service}{vtx_flag}", "id": call["id"]})
                return
            else:
                answer_callback(call["id"], "❌ Number out of stock or range missing!", show_alert=True)
                if data.startswith("c_n_"): delete_message(chat_id, msg_id)
                return

        random.shuffle(available_indices)
        
        fetched_nums = []
        for b_id, idx in available_indices:
            if len(fetched_nums) >= bot_settings["num_req"]: break
            n_obj = number_batches[b_id]["numbers"][idx]
            
            fetched_nums.append(n_obj["num"])
            ksi_assigned_numbers[n_obj["num"]] = chat_id
            
            # 🌟 Save File Specific Rate
            assigned_number_rates[n_obj["num"]] = {"normal": float(number_batches[b_id].get("normal_rate", number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0)))), "special": float(number_batches[b_id].get("special_rate", number_batches[b_id].get("normal_rate", number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0)))))}
            
            n_obj["shares"] += 1
            n_obj["used_by"].append(chat_id)
            total_assigned_stats += 1
            
            if n_obj["shares"] >= bot_settings.get("num_share", 1):
                n_obj["to_remove"] = True
                used_numbers_list.append(n_obj["num"])

        for b_id in number_batches:
            number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
        save_db()

        if not fetched_nums:
            answer_callback(call["id"], "❌ You have already taken all numbers or stock is empty!", show_alert=True)
            if data.startswith("c_n_"): delete_message(chat_id, msg_id)
            return

        app_full_name, _ = get_service_info_html(service)
        emoji_id = "5337302974806922068"
        apps_db = bot_settings.get("premium_apps", {})
        for app_key, app_data in apps_db.items():
            if service.upper() == app_key or service.upper() in app_key or app_key in service.upper():
                if "id" in app_data:
                    emoji_id = app_data["id"]
                    break
        kb = [[{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id, "callback_data": "ignore", "style": "primary"}]]
        
        flags_db = bot_settings.get("premium_flags", {})
        country_emoji_html = ""
        for num in fetched_nums:
            char_flag, iso = get_flag_and_code(num)
            display_num = f"+{num}" if not num.startswith("+") else num
            
            flag_emoji_id = "5780471598922337683" # Default Flag
            for flag_code, flag_data in flags_db.items():
                if iso == flag_data.get("iso"):
                    if "id" in flag_data: 
                        flag_emoji_id = flag_data["id"]
                        country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                    break
            
            if not country_emoji_html: country_emoji_html = char_flag
            kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": "success"}])
            
        # Change Number + Change Country on the same row.
        kb.append([
            {"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_{service}_{country}", "style": "danger"},
            {"text": "Change Country", "icon_custom_emoji_id": "5305517382138112561", "callback_data": f"g_s_{service}", "style": "danger"}
        ])

        # Custom inline buttons: 2 per row.
        c_btns = []
        for c_b in bot_settings["custom_messages"].get("get_number", {}).get("buttons", []):
            b_copy = c_b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            c_btns.append(b_copy)
        for i in range(0, len(c_btns), 2):
            kb.append(c_btns[i:i + 2])

        # OTP Group stays on its own row.
        kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
        
        text_numbers, new_number_custom_kb = render_new_number_message(country_emoji_html, country, service)
        kb.extend(new_number_custom_kb)
        # সবসময় মেসেজ ইডিট করবে (Change Number করলেও নতুন মেসেজ আসবে না)
        try:
            edit_message(chat_id, msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": fetched_nums}
        except:
            # যদি মেসেজ ইডিট করা সম্ভব না হয় (যেমন অনেক আগের মেসেজ), তবে নতুন মেসেজ দিবে
            msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
            if msg_res and "result" in msg_res:
                user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums}

    elif data.startswith("wapp_") or data.startswith("wrej_"):
        # অ্যাডমিন চেক (User ID চেক করতে হবে)
        user_id_clicked = call["from"]["id"]
        if not is_admin(user_id_clicked):
            answer_callback(call["id"], "🚫 Only Bot Admins can process withdrawals!", show_alert=True)
            return
            
        action = "APPROVE" if data.startswith("wapp_") else "REJECT"
        req_id = data.replace("wapp_", "").replace("wrej_", "")
        
        if req_id in pending_withdrawals:
            req_data = pending_withdrawals[req_id]
            u_id, amt = req_data["user_id"], req_data["amount"]
            num = req_data["number"]
            full_name = req_data.get("full_name", u_id)
            
            if action == "APPROVE" and len(num) >= 7:
                masked_num = f"{num[:4]}❖DXA❖{num[-3:]}"
            else:
                masked_num = num
            
            if action == "REJECT":
                update_balance(u_id, amt, reason="withdrawal_rejected_refund", activity_type="withdrawal_rejected")
                record_user_activity(u_id, "withdrawal_rejected", {"request_id": req_id, "amount": amt, "status": "rejected"})
                send_message(u_id, render_body_text(f"❌ Your {amt} TK withdrawal request was rejected. Balance refunded."))
            else:
                record_user_activity(u_id, "withdrawal_approved", {"request_id": req_id, "amount": amt, "status": "approved"})
                send_message(u_id, render_body_text(f"{PEM['ok']} Your {amt} TK withdrawal request has been paid successfully!"))
            
            if db:
                try: db.collection('withdrawals').document(req_id).update({"status": "approved" if action == "APPROVE" else "rejected"})
                except: pass
                
            del pending_withdrawals[req_id]
            save_db()
            delete_message(chat_id, msg_id)
        else:
            answer_callback(call["id"], "❌ Request already processed!", show_alert=True)

# ==========================================
# Console OTP Forwarding
# ==========================================
def forward_console_otp_to_groups(number, service, message, iso=None):
    """Forward an OTP detected from Bangla/console panels to configured OTP groups."""
    try:
        if not bot_settings.get("console_otp", False):
            return
        message = str(message or "").strip()
        if not message:
            return
        otp = extract_otp_code(message)
        if not otp:
            return

        raw_num = str(number or "").strip()
        if not raw_num:
            return
        display_num = raw_num if raw_num.startswith("+") else "+" + raw_num

        # Console numbers can be incomplete, so the country calling code
        # must come from the detected country/ISO, not from the partial number.
        clean_console = ''.join(ch for ch in raw_num if ch.isdigit())
        _, detected_iso = get_flag_and_code(raw_num)
        detected_iso = str(iso or detected_iso or "XX").upper()

        # premium_flags is keyed by international calling code (e.g. 880 -> BD,
        # 382 -> ME). Reverse-lookup the calling code from the detected ISO.
        country_calling_code = None
        for calling_code, flag_data in bot_settings.get("premium_flags", {}).items():
            if str(flag_data.get("iso", "")).upper() == detected_iso:
                country_calling_code = str(calling_code)
                break

        # Fallback: if ISO lookup is unavailable, use the calling code detected
        # from the number itself.
        if not country_calling_code:
            clean_for_lookup = clean_console
            for calling_code in sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True):
                if clean_for_lookup.startswith(str(calling_code)):
                    country_calling_code = str(calling_code)
                    break
        country_calling_code = country_calling_code or "000"

        mask_cfg = bot_settings.get("mask_emoji", {}) if "bot_settings" in globals() else {}
        mask_id = str(mask_cfg.get("id", "") or "")
        mask_char = str(mask_cfg.get("char", "") or "")
        if mask_id and mask_char:
            console_mask = f'<tg-emoji emoji-id="{mask_id}">{mask_char}</tg-emoji>'
        else:
            console_mask = mask_char or "DXA"

        # The prefix is the country's real international calling code.
        # It is NOT generated and is NOT taken from the partial console number.
        # Example: ME -> 382, BD -> 880.
        # Console numbers may be incomplete/reused, so the 4 digits after
        # the hide marker are intentionally randomized for each displayed OTP.
        suffix = f"{random.randint(0, 9999):04d}"
        masked = f"{country_calling_code}{console_mask}{suffix}"

        app_full_name, prem_app_html = get_service_info_html(
            str(service or "Unknown"), message
        )
        flag_html = get_flag_info_html(display_num)
        lang = detect_language(message)
        # Display the detected language as its short code: #EN, #BN, #AR, etc.
        lang_code = str(lang or "#EN").upper()
        if not lang_code.startswith("#"):
            lang_code = "#" + lang_code
        if len(lang_code) > 3:
            lang_code = lang_code[:3]

        # Same interface as the real OTP group message:
        # FLAG ISO | APP NUMBER | #LANG
        display_msg = render_body_text(
            f"{flag_html} {detected_iso} | {prem_app_html} {masked} | 💬 {lang_code}"
        )

        for fw in bot_settings.get("fw_groups", []):
            try:
                kb = [[{
                    "text": str(otp),
                    "icon_custom_emoji_id": "5296369303661067030",
                    "copy_text": {"text": str(otp)},
                    "style": "primary"
                }]]
                temp_row = []
                styles = ["danger", "success", "primary"]
                for i, btn in enumerate(fw.get("buttons", [])):
                    if not btn.get("url"):
                        continue
                    b_obj = {
                        "text": btn.get("text", ""),
                        "url": btn["url"],
                        "style": styles[i % 3]
                    }
                    if btn.get("icon_custom_emoji_id"):
                        b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                    temp_row.append(b_obj)
                    if len(temp_row) == 2:
                        kb.append(temp_row)
                        temp_row = []
                if temp_row:
                    kb.append(temp_row)
                send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
            except Exception:
                pass
    except Exception:
        pass

# ==========================================
# Polling Loop
# ==========================================
def poll_otp_with_status(number_id, num_str, owner_id, api_key):
    headers = {"X-API-Key": api_key}
    for _ in range(150): # 150 * 4 seconds = 10 Minutes Polling
        try:
            res = requests.get(f"{STEX_BASE_URL}/api/v1/numbers/{number_id}/sms", headers=headers, timeout=10)
            data = res.json()
            if data.get("success") and data.get("otp"):
                otp = str(data["otp"])
                msg_text = data.get("message", f"Your code is {otp}")
                
                # 🌟 সম্পূর্ণ মেসেজ থেকে ড্যাশসহ বা বড় OTP খোঁজার ফিক্স
                extracted_otp = extract_otp_code(msg_text)
                if extracted_otp and len(extracted_otp) > len(otp):
                    otp = extracted_otp
                    
                # 🌟 সম্পূর্ণ মেসেজ থেকে সার্ভিস/অ্যাপ চেনার ফিক্স
                app_name = data.get("service", "StexSMS Service")
                detected_app = detect_service(msg_text)
                if detected_app:
                    app_name = detected_app
                
                unique_id = f"POLL_{number_id}_{otp}"
                if unique_id not in processed_otps:
                    processed_otps.add(unique_id)
                    
                    char, iso = get_flag_and_code(num_str)
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                    
                    global recent_traffic
                    current_time = time.time()
                    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                    recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num_str, "time": current_time, "source": "bot"})
                    save_local_db()
                    
                    display_num = f"+{num_str}" if not str(num_str).startswith("+") else str(num_str)
                    masked = mask_number(display_num)
                    lang = detect_language(msg_text)
                    
                    display_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} {masked} {lang}\n╚═══════════════╝")
                    
                    for fw in bot_settings.get("fw_groups", []):
                        kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
                        temp_row = []
                        styles = ["danger", "success", "primary"]
                        for i, btn in enumerate(fw.get("buttons", [])):
                            b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                            if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                            temp_row.append(b_obj)
                            if len(temp_row) == 2:
                                kb.append(temp_row)
                                temp_row = []
                        if temp_row: kb.append(temp_row)
                        send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                    
                    reward = get_otp_reward_for_user(num_str, owner_id, "StexSMS")
                    reward_line = f"\n💰 <b>Reward: {reward:g} TK</b>" if reward > 0 else ""
                    inbox_msg = render_body_text(
                        f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {display_num} | 💬 {lang}\n"
                        f"📝 <b>Full Msg:</b> <code>{html.escape(str(msg_text))}</code>\n"
                        f"🔐 <b>OTP:</b> <code>{html.escape(str(otp))}</code>"
                        f"{reward_line}"
                    )
                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
                    credit_earning(owner_id, reward, "otp")
                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                    
                    if db:
                        try: increment_user_otp(owner_id)
                        except: pass
                break
        except: pass
        time.sleep(4)

def stex_console_listener():
    global recent_traffic, bot_settings
    seen_console_hits = set()
    last_auto_update = time.time()
    
    while True:
        try:
            stex_keys = bot_settings.get("stex_keys", [])
            if stex_keys:
                api_key = stex_keys[0]
                headers = {"mauthapi": api_key}
                res = requests.get(f"{STEX_BASE_URL}/console", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("meta", {}).get("code") == 200 and data.get("data", {}).get("hits"):
                    current_time = time.time()
                    new_hits = False
                    
                    for hit in data["data"]["hits"]:
                        range_str = str(hit.get("range", "")).replace("X", "")
                        if len(range_str) > 9:
                            range_str = range_str[:9]
                        sid = str(hit.get("sid", "Unknown"))
                        msg = str(hit.get("message", ""))
                        hit_time = hit.get("time", current_time * 1000) / 1000.0
                        
                        unique_hit = f"STEX_{range_str}_{sid}_{hit.get('time', 0)}"
                        if unique_hit not in seen_console_hits and range_str:
                            seen_console_hits.add(unique_hit)
                            if len(seen_console_hits) > 2000: seen_console_hits.clear()
                            
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, msg)
                            forward_console_otp_to_groups(range_str, app_full_name, msg, iso)
                            
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": f"{range_str}XXX", 
                                "time": hit_time,
                                "real_range": range_str,
                                "source": "console"
                            })
                            new_hits = True
                            
                    if new_hits:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    # 🌟 Auto ADD and DELETE logic for Stex every 2 minutes
                    if bot_settings.get("stex_auto", False) and current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        changed = False
                        
                        if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
                        if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
                        
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)]
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["stex_services"]:
                                bot_settings["stex_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)]
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["stex_services"][srv]:
                                    bot_settings["stex_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)]
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["stex_services"][srv][full_country_name]:
                                        bot_settings["stex_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["search_countries"]:
                                        bot_settings["search_countries"].append(country_code)
                                        changed = True

                        services_to_remove = []
                        for srv, countries in list(bot_settings["stex_services"].items()):
                            srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and "real_range" in t and current_time - t.get("time", 0) <= 120)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and current_time - t.get("time", 0) <= 120)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["stex_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["stex_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)

def voltx_console_listener():
    global recent_traffic, bot_settings
    seen_console_hits = set()
    last_auto_update = time.time()
    
    while True:
        try:
            if not bot_settings.get("voltx_on", True):
                time.sleep(5)
                continue
            voltx_keys = bot_settings.get("voltx_keys", [])
            if voltx_keys:
                api_key = voltx_keys[0]
                headers = {"mauthapi": api_key}
                res = requests.get(f"{VOLTX_BASE_URL}/console", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("meta", {}).get("code") == 200 and data.get("data", {}).get("hits"):
                    current_time = time.time()
                    new_hits = False
                    
                    for hit in data["data"]["hits"]:
                        range_str = str(hit.get("range", "")).replace("X", "")
                        if len(range_str) > 9:
                            range_str = range_str[:9] # 9 ডিজিটের বেশি হলে প্রথম 9 ডিজিট নেবে
                        sid = str(hit.get("sid", "Unknown"))
                        msg = str(hit.get("message", ""))
                        hit_time = hit.get("time", current_time * 1000) / 1000.0
                        
                        unique_hit = f"{range_str}_{sid}_{hit.get('time', 0)}"
                        if unique_hit not in seen_console_hits and range_str:
                            seen_console_hits.add(unique_hit)
                            if len(seen_console_hits) > 2000: seen_console_hits.clear()
                            
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, msg)
                            forward_console_otp_to_groups(range_str, app_full_name, msg, iso)
                            
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": f"{range_str}XXX", 
                                "time": hit_time,
                                "real_range": range_str,
                                "source": "console"
                            })
                            new_hits = True
                            
                    if new_hits:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    # 🌟 Auto ADD and DELETE logic every 2 minutes (120 seconds)
                    if bot_settings.get("voltx_auto", False) and current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        changed = False
                        
                        if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
                        if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
                        
                        # --- ১. Auto ADD Logic ---
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)] # Top 6 Services
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["voltx_services"]:
                                bot_settings["voltx_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)] # Top 3 Countries
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["voltx_services"][srv]:
                                    bot_settings["voltx_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)] # Top 2 Ranges
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["voltx_services"][srv][full_country_name]:
                                        bot_settings["voltx_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    # 🌟 শুধুমাত্র ৩ ডিজিট কান্ট্রি কোড অ্যাড করবে
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["voltx_search_countries"]:
                                        bot_settings["voltx_search_countries"].append(country_code)
                                        changed = True

                        # --- ২. Auto DELETE Logic (Only if NO traffic in the LAST 120 SECONDS) ---
                        services_to_remove = []
                        for srv, countries in list(bot_settings["voltx_services"].items()):
                            # চেক করবে গত ১২০ সেকেন্ডে কোনো ট্রাফিক আছে কি না
                            srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and "real_range" in t and current_time - t.get("time", 0) <= 120)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and current_time - t.get("time", 0) <= 120)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["voltx_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["voltx_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)

def voltx_sms_listener():
    global processed_otps, recent_traffic, voltx_assigned_numbers
    while True:
        try:
            voltx_keys = bot_settings.get("voltx_keys", [])
            for api_key in voltx_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{VOLTX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = "Voltx Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"VOLTX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time, "source": "bot"})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = lang
                                display_msg = render_body_text(f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {masked} | 💬 {lang}")
                                
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
                                    temp_row = []
                                    styles = ["danger", "success", "primary"]
                                    for i, btn in enumerate(fw.get("buttons", [])):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        temp_row.append(b_obj)
                                        if len(temp_row) == 2:
                                            kb.append(temp_row)
                                            temp_row = []
                                    if temp_row: kb.append(temp_row)
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for vtx_n, n_owner in voltx_assigned_numbers.items():
                                        clean_vtx = str(vtx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_vtx == clean_api_num or (len(clean_vtx) >= 8 and clean_vtx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_vtx[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    lang_name = lang
                                    reward = get_otp_reward_for_user(num, owner_id, "Voltx")

                                    reward_line = f"\n💰 <b>Reward: {reward:g} TK</b>" if reward > 0 else ""

                                    inbox_msg = render_body_text(

                                        f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {display_num} | 💬 {lang}\n"

                                        f"📝 <b>Full Msg:</b> <code>{html.escape(str(msg_text))}</code>\n"

                                        f"🔐 <b>OTP:</b> <code>{html.escape(str(otp))}</code>"

                                        f"{reward_line}"

                                    )

                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]

                                    credit_earning(owner_id, reward, "otp")

                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    if db:
                                        try: 
                                            increment_user_otp(owner_id)
                                        except: pass
                except: pass
        except: pass
        time.sleep(5)

def zenex_sms_listener():
    global processed_otps, recent_traffic, zenex_assigned_numbers
    while True:
        try:
            zenex_keys = bot_settings.get("zenex_keys", [])
            for api_key in zenex_keys:
                try:
                    headers = {"mapikey": api_key}
                    res = requests.get(f"{ZENEX_BASE_URL}/v1/numsuccess/info", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("otp", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("nid", otp))
                            
                            app_name = "Zenex Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"ZENEX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time, "source": "bot"})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = lang
                                display_msg = render_body_text(f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {masked} | 💬 {lang}")
                                
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
                                    temp_row = []
                                    styles = ["danger", "success", "primary"]
                                    for i, btn in enumerate(fw.get("buttons", [])):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        temp_row.append(b_obj)
                                        if len(temp_row) == 2:
                                            kb.append(temp_row)
                                            temp_row = []
                                    if temp_row: kb.append(temp_row)
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for znx_n, n_owner in zenex_assigned_numbers.items():
                                        clean_znx = str(znx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_znx == clean_api_num or (len(clean_znx) >= 8 and clean_znx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_znx[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    reward = get_otp_reward_for_user(num, owner_id, "Zenex")

                                    reward_line = f"\n💰 <b>Reward: {reward:g} TK</b>" if reward > 0 else ""

                                    inbox_msg = render_body_text(

                                        f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {display_num} | 💬 {lang}\n"

                                        f"📝 <b>Full Msg:</b> <code>{html.escape(str(msg_text))}</code>\n"

                                        f"🔐 <b>OTP:</b> <code>{html.escape(str(otp))}</code>"

                                        f"{reward_line}"

                                    )

                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]

                                    credit_earning(owner_id, reward, "otp")

                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    if db:
                                        try: 
                                            increment_user_otp(owner_id)
                                        except: pass
                except: pass
        except: pass
        time.sleep(5)

def global_sms_listener():
    global processed_otps, recent_traffic, stex_assigned_numbers
    while True:
        try:
            stex_keys = bot_settings.get("stex_keys", [])
            for api_key in stex_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{STEX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = "Stex Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"STEX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time, "source": "bot"})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = lang
                                display_msg = render_body_text(f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {masked} | 💬 {lang}")
                                
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
                                    temp_row = []
                                    styles = ["danger", "success", "primary"]
                                    for i, btn in enumerate(fw.get("buttons", [])):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[i % 3]}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        temp_row.append(b_obj)
                                        if len(temp_row) == 2:
                                            kb.append(temp_row)
                                            temp_row = []
                                    if temp_row: kb.append(temp_row)
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for stex_n, n_owner in stex_assigned_numbers.items():
                                        clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    lang_name = lang
                                    reward = get_otp_reward_for_user(num, owner_id, "StexSMS")
                                    reward_line = f"\n💰 <b>Reward: {reward:g} TK</b>" if reward > 0 else ""
                                    inbox_msg = render_body_text(
                                        f"{get_flag_info_html(display_num)} {iso} | {prem_app_html} {display_num} | 💬 {lang}\n"
                                        f"📝 <b>Full Msg:</b> <code>{html.escape(str(msg_text))}</code>\n"
                                        f"🔐 <b>OTP:</b> <code>{html.escape(str(otp))}</code>"
                                        f"{reward_line}"
                                    )
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5296369303661067030", "copy_text": {"text": otp}, "style": "primary"}]]
                                    credit_earning(owner_id, reward, "otp")
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    if db:
                                        try: 
                                            increment_user_otp(owner_id)
                                        except: pass
                except: pass
        except: pass
        time.sleep(5)

def zenex_console_listener():
    global recent_traffic, bot_settings
    last_auto_update = time.time()
    zenex_last_hits = {} 
    
    while True:
        try:
            zenex_keys = bot_settings.get("zenex_keys", [])
            if zenex_keys:
                api_key = zenex_keys[0]
                headers = {"mapikey": api_key}
                res = requests.get(f"{ZENEX_BASE_URL}/v1/active-ranges", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("success") and "data" in data and "active_ranges" in data["data"]:
                    current_time = time.time()
                    new_hits_added = False
                    
                    for hit in data["data"]["active_ranges"]:
                        range_str = str(hit.get("range", "")).replace("X", "").replace("x", "")
                        sid = str(hit.get("service", "Unknown")).upper()
                        hits_count = int(hit.get("hits", 1))
                        
                        if range_str:
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, "")
                            
                            range_key = f"{range_str}_{app_full_name}"
                            prev_hits = zenex_last_hits.get(range_key, 0)
                            
                            if hits_count > prev_hits:
                                new_hits = hits_count - prev_hits
                            else:
                                new_hits = hits_count
                                
                            zenex_last_hits[range_key] = hits_count
                            if new_hits > 150: new_hits = 150
                            
                            for _ in range(new_hits):
                                recent_traffic.append({
                                    "service": app_full_name,
                                    "iso": iso,
                                    "flag": char,
                                    "number": f"{range_str}XXX", 
                                    "time": current_time,
                                    "real_range": range_str,
                                    "source": "zenex"
                                })
                                new_hits_added = True
                            
                    if new_hits_added:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    if bot_settings.get("zenex_auto", False) and current_time - last_auto_update > 120:
                        last_auto_update = current_time
                        changed = False
                        
                        if "zenex_services" not in bot_settings: bot_settings["zenex_services"] = {}
                        if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
                        
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if t.get("source") == "zenex" and "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)]
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["zenex_services"]:
                                bot_settings["zenex_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("source") == "zenex" and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)]
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["zenex_services"][srv]:
                                    bot_settings["zenex_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and t.get("source") == "zenex" and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)]
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["zenex_services"][srv][full_country_name]:
                                        bot_settings["zenex_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["zenex_search_countries"]:
                                        bot_settings["zenex_search_countries"].append(country_code)
                                        changed = True

                        services_to_remove = []
                        for srv, countries in list(bot_settings["zenex_services"].items()):
                            srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("source") == "zenex" and "real_range" in t and current_time - t.get("time", 0) <= 120)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and t.get("source") == "zenex" and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and t.get("source") == "zenex" and current_time - t.get("time", 0) <= 120)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["zenex_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["zenex_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)

def main():
    global BOT_USERNAME
    res = api_call("getMe")
    if res.get("ok"): BOT_USERNAME = res["result"]["username"]
    print(f"🤖 Bot is starting... @{BOT_USERNAME}")
    
    threading.Thread(target=panel_monitor_thread, daemon=True).start()
    threading.Thread(target=global_sms_listener, daemon=True).start()
    threading.Thread(target=stex_console_listener, daemon=True).start()
    threading.Thread(target=voltx_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_console_listener, daemon=True).start()
    threading.Thread(target=zenex_sms_listener, daemon=True).start()
    threading.Thread(target=zenex_console_listener, daemon=True).start()
    threading.Thread(target=fastx_sms_listener, daemon=True).start()
    print("📡 Background APIs & Global SMS Listener Started!")
    
    # 🌟 PRO-LEVEL FAST SYSTEM: 500 Workers Pool
    executor = ThreadPoolExecutor(max_workers=500)
    
    offset = None
    while True:
        try:
            updates = api_call(f"getUpdates?timeout=50&offset={offset}")
            if updates and "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update: 
                        executor.submit(handle_message, update["message"])
                    elif "callback_query" in update: 
                        executor.submit(handle_callback, update["callback_query"])
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()    
