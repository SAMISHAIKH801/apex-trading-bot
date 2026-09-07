










import streamlit as st
import ccxt
import pandas as pd
import numpy as np
import time
import os
import json
import hashlib
import hmac
import secrets
import threading
import socket
import ssl
import http.client
import urllib.request
import urllib.error
from datetime import datetime, date

# Optional strong encryption for API keys (pip install cryptography)
try:
    from cryptography.fernet import Fernet
    _CRYPTO_OK = True
except Exception:
    _CRYPTO_OK = False

# ==========================================
# PAGE SETUP & STYLING
# ==========================================
favicon_path = "apex-favicon.png" if os.path.exists("apex-favicon.png") else "⚡"
logo_path = "apex-logo.png" if os.path.exists("apex-logo.png") else None

st.set_page_config(
    page_title="Apex Trading - Pro Terminal",
    page_icon=favicon_path if os.path.exists("apex-favicon.png") else "⚡",
    layout="wide"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 0%, rgba(252,213,53,0.06), transparent 32%),
            radial-gradient(circle at 88% 100%, rgba(14,203,129,0.05), transparent 38%),
            #0b0e11;
        color: #eaecef;
    }

    .block-container { padding-top: 1.6rem; padding-bottom: 3rem; }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes softPulse {
        0% { box-shadow: 0 0 0 0 rgba(14,203,129,0.35); }
        70% { box-shadow: 0 0 0 8px rgba(14,203,129,0); }
        100% { box-shadow: 0 0 0 0 rgba(14,203,129,0); }
    }

    .crypto-card {
        background: linear-gradient(150deg, #181a20 0%, #121418 100%);
        border: 1px solid #2b313a;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 10px 26px rgba(0,0,0,0.28);
        animation: fadeInUp 0.35s ease both;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .crypto-card:hover { border-color: #3a4552; }

    .badge-live {
        background-color: rgba(14, 203, 129, 0.15);
        color: #0ecb81;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        border: 1px solid #0ecb81;
        animation: softPulse 2.4s ease-in-out infinite;
    }
    .badge-signal {
        background-color: rgba(240, 185, 11, 0.15);
        color: #fcd535;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        border: 1px solid #fcd535;
    }
    .rule-tag {
        display:inline-block;
        background:#0ecb8122;
        border:1px solid #0ecb81;
        color:#0ecb81;
        padding:4px 12px;
        border-radius:20px;
        font-size:12px;
        margin-right:6px;
        margin-bottom:6px;
        transition: background 0.15s ease;
    }
    .rule-tag:hover { background:#0ecb8140; }

    .sig-card {
        background: linear-gradient(180deg,#181a20 0%, #131519 100%);
        border: 1px solid #2b313a;
        border-left: 4px solid #fcd535;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 12px;
        animation: fadeInUp 0.3s ease both;
        transition: transform 0.15s ease, border-color 0.2s ease;
    }
    .sig-card:hover { transform: translateY(-2px); border-color: #3a4552; }

    .trade-card {
        background: linear-gradient(180deg,#181a20 0%, #131519 100%);
        border: 1px solid #2b313a;
        border-left: 4px solid #0ecb81;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 12px;
        animation: fadeInUp 0.3s ease both;
        transition: transform 0.15s ease, border-color 0.2s ease;
    }
    .trade-card:hover { transform: translateY(-2px); border-color: #3a4552; }

    .kv-row { display:flex; flex-wrap:wrap; row-gap:10px; column-gap:22px; }
    .kv { display:inline-block; margin-right:20px; }
    .kv .k { color:#848e9c; font-size:11px; letter-spacing:.4px; display:block; margin-bottom:2px; }
    .kv .v { font-size:15px; font-weight:700; }
    .sym-title { color:#fcd535; font-size:19px; font-weight:800; margin:0; }

    .stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 700;
        border: 1px solid #303943;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        border-color: #52606e;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.25);
    }
    .stButton > button:active { transform: translateY(0) scale(0.98); }

    div[data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid #252c34; }
    button[data-baseweb="tab"] {
        background: #11161b;
        border-radius: 9px 9px 0 0;
        transition: background 0.15s ease;
    }
    button[data-baseweb="tab"][aria-selected="true"] { background: #1a2027; }

    [data-testid="stDataFrame"] { border: 1px solid #2b313a; border-radius: 12px; overflow: hidden; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c1015 0%, #090c10 100%);
        border-right: 1px solid #20262e;
    }

    /* ==========================================
       MOBILE / SMALL-SCREEN RESPONSIVE TUNING
       (sirf spacing/sizing — koi functionality nahi badli)
       ========================================== */
    @media (max-width: 900px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1.1rem; padding-bottom: 2rem; }
        .crypto-card, .sig-card, .trade-card { padding: 15px 16px; border-radius: 12px; margin-bottom: 12px; }
        .sym-title { font-size: 16px; }
        .kv { margin-right: 0; }
        .kv .k { font-size: 10px; }
        .kv .v { font-size: 13px; }
        h1 { font-size: 21px !important; }
        h2 { font-size: 18px !important; }
        h3, .stMarkdown h3 { font-size: 16px !important; }
        div[data-baseweb="tab-list"] { overflow-x: auto; flex-wrap: nowrap !important; -webkit-overflow-scrolling: touch; }
        button[data-baseweb="tab"] { font-size: 12px; padding: 8px 10px !important; white-space: nowrap; }
        div[role="radiogroup"] { flex-wrap: wrap !important; row-gap: 8px !important; column-gap: 8px !important; }
        div[role="radiogroup"] label { font-size: 12.5px !important; padding: 3px 4px !important; }
        .stButton > button { min-height: 44px; font-size: 13.5px; width: 100%; }
        [data-testid="column"] { padding-left: 4px !important; padding-right: 4px !important; }
        [data-testid="stMetricValue"] { font-size: 18px !important; }
        [data-testid="stMetricLabel"] { font-size: 11px !important; }
    }
    @media (max-width: 480px) {
        .crypto-card, .sig-card, .trade-card { padding: 13px 14px; }
        .sym-title { font-size: 14.5px; }
        .kv .v { font-size: 12.5px; }
        .badge-live, .badge-signal { font-size: 10.5px; padding: 3px 9px; }
    }

    /* ==========================================
       GLOBAL RADIO -> PILL / NAV STYLE
       (Streamlit ke default radio circles hata kar clean
       clickable nav-items / pills banate hain — sidebar
       menu, dashboard tabs, exec-mode, market-type sab par)
       ========================================== */
    div[role="radiogroup"] { row-gap: 8px; }
    div[role="radiogroup"] > label {
        cursor: pointer;
        transition: background 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
    }
    div[role="radiogroup"] > label > div:first-child { display: none !important; }

    /* Horizontal pill-style groups (dashboard tabs, exec mode, market type, login sub-tabs) */
    div[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] > label {
        background: #12161b;
        border: 1px solid #232a33;
        border-radius: 20px;
        padding: 7px 16px !important;
        margin: 0 6px 6px 0 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] > label:hover {
        border-color: #52606e;
    }
    div[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] > label:has(input:checked) {
        background: linear-gradient(90deg, rgba(14,203,129,0.18), rgba(14,203,129,0.05));
        border-color: #0ecb81;
    }
    div[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] > label:has(input:checked) p {
        color: #0ecb81 !important;
        font-weight: 700 !important;
    }

    /* Sidebar main navigation — vertical list, distinct highlighted "active page" look */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: #12161b;
        border: 1px solid #222831;
        border-radius: 10px;
        padding: 11px 14px !important;
        margin: 0 !important;
        width: 100%;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: #171d25;
        border-color: #3a4552;
        transform: translateX(2px);
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(90deg, rgba(252,213,53,0.16), rgba(252,213,53,0.03));
        border-color: #fcd535;
        border-left: 3px solid #fcd535;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) p {
        color: #fcd535 !important;
        font-weight: 700 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 14px;
        margin: 0 !important;
    }

    /* Sidebar section captions (NAVIGATION / etc.) */
    .apex-side-caption {
        color: #5b6672; font-size: 10.5px; font-weight: 700; letter-spacing: 1px;
        margin: 2px 0 8px 2px; text-transform: uppercase;
    }

    /* Consistent vertical rhythm across cards/sections everywhere */
    .crypto-card, .sig-card, .trade-card { line-height: 1.5; }
    .stApp [data-testid="stVerticalBlock"] > div:has(> .crypto-card) { margin-bottom: 2px; }

    /* Dashboard header — icon + text alignment, clean stacking on small screens */
    .apex-header-icon {
        font-size: 26px; line-height: 1; margin-right: 8px; vertical-align: -3px;
    }
    @media (max-width: 900px) {
        .apex-header-icon { font-size: 21px; margin-right: 6px; }
        [data-testid="stMetric"] { text-align: center; }
        h1 .apex-header-icon, h2 .apex-header-icon, h3 .apex-header-icon { display: inline-block; }
        /* Sidebar top logo + user card: mobile me chhota aur clean */
        section[data-testid="stSidebar"] .stImage, section[data-testid="stSidebar"] img { max-width: 110px !important; margin: 0 auto; display: block; }
        /* Selectbox (Candle Timeframe, Exchange select etc.) mobile me full-width + clean */
        div[data-baseweb="select"] > div { min-height: 44px !important; }
        /* Dashboard analytics card: mobile me 2x2 grid ke bajaye 1x4 stack better */
        [data-testid="stHorizontalBlock"]:has(> [data-testid="column"]:nth-child(4)) {
            /* Let streamlit handle, but tune spacing */
            row-gap: 10px;
        }
        [data-testid="stMetric"] {
            padding: 10px 8px; border-radius: 10px;
            background: linear-gradient(180deg, #13171c 0%, #0f1318 100%);
            border: 1px solid #242b34;
        }
    }
    @media (max-width: 600px) {
        /* small phones: metric font sizes */
        [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 17px !important; }
        [data-testid="stMetric"] [data-testid="stMetricDelta"] { font-size: 11px !important; }
        h1 { font-size: 20px !important; line-height: 1.3 !important; }
        h2 { font-size: 17px !important; line-height: 1.3 !important; }
        .block-container { padding-top: 0.9rem; }
        /* start/stop buttons me text thoda chhota lekin full tap area */
        .stButton > button { padding: 0 12px !important; font-size: 13px !important; letter-spacing: .2px; }
        /* Login/signup cards: side padding kam */
        .stApp > header { display: none !important; } /* hide streamlit default header for cleaner app */
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CONFIG / PATHS (env se override ho sakte hain — VPS par persistent disk ke liye useful)
# ==========================================
DB_FILE = os.environ.get("APEX_DB_FILE", "database.json")
LOCK_FILE = os.environ.get("APEX_LOCK_FILE", "apex.lock")
KEY_FILE = os.environ.get("APEX_KEY_FILE", "apex_secret.key")
SECRET_ENV = "APEX_SECRET_KEY"       # live par ye env var set karo (sabse safe)
MIN_ACTION_GAP_SEC = 10              # do actions ke beech gap (rapid-fire / multi-tab race rokne ke liye)
STALE_LOCK_SEC = 25
UNIVERSE_CACHE_TTL = 180             # seconds — market/tickers data itni der cache rehta hai (chhote VPS ka RAM/CPU bachane ke liye)

# ==========================================
# ENCRYPTION (API keys / secrets at rest)
# ==========================================
def _load_or_create_fernet():
    if not _CRYPTO_OK:
        return None
    key = os.environ.get(SECRET_ENV)
    if key:
        try:
            return Fernet(key.encode() if isinstance(key, str) else key)
        except Exception:
            pass
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "rb") as f:
                return Fernet(f.read().strip())
        except Exception:
            pass
    k = Fernet.generate_key()
    try:
        with open(KEY_FILE, "wb") as f:
            f.write(k)
    except Exception:
        pass
    return Fernet(k)

FERNET = _load_or_create_fernet()
ENC_PREFIX = "enc::"

def enc_secret(plain):
    """Plain text ko encrypt karke store karo. Pehle se encrypted ho to waise hi rehne do."""
    if not plain:
        return ""
    if not isinstance(plain, str):
        plain = str(plain)
    if plain.startswith(ENC_PREFIX):
        return plain
    if FERNET is None:
        return plain  # cryptography install nahi — plain (UI me warning dikhega)
    try:
        return ENC_PREFIX + FERNET.encrypt(plain.encode()).decode()
    except Exception:
        return plain

def dec_secret(stored):
    """Encrypted value ko wapas plain me karo. Legacy plain value ho to waise hi de do."""
    if not stored or not isinstance(stored, str):
        return stored or ""
    if not stored.startswith(ENC_PREFIX):
        return stored  # legacy plain
    if FERNET is None:
        return ""
    try:
        return FERNET.decrypt(stored[len(ENC_PREFIX):].encode()).decode()
    except Exception:
        return ""

# ==========================================
# PASSWORD HASHING (login/signup)
# ==========================================
def hash_password(pw):
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200000).hex()
    return f"pbkdf2${salt}${h}"

def verify_password(pw, stored):
    if not stored:
        return False
    if isinstance(stored, str) and stored.startswith("pbkdf2$"):
        try:
            _, salt, h = stored.split("$", 2)
            calc = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200000).hex()
            return hmac.compare_digest(calc, h)
        except Exception:
            return False
    # legacy plain password (purane accounts) — match ho to login ke baad hash me upgrade kar denge
    return hmac.compare_digest(str(pw), str(stored))

# ==========================================
# DATABASE
# ==========================================
DEFAULT_MANUAL_STRATEGY = {
    "timeframe": "1h", "timeframes": ["1h"], "multi_tf_enabled": False,
    "ma_enabled": False, "ma_periods": [], "ma_logic": "AND",
    "rsi_enabled": False, "rsi_min": 30, "rsi_max": 45,
    "sr_enabled": False, "sr_lookback": 50, "sr_tolerance_pct": 1.0,
    "ob_enabled": False, "ob_lookback": 50,
    "vol_enabled": False, "vol_min_usdt": 500000,
    "trend_enabled": False, "trend_lookback": 100, "trend_touches": 3,
}

DEFAULT_RUNTIME = {
    "trade_date": "", "trades_today": 0, "signals_today": 0,
    "traded_coins_today": [], "last_action_epoch": 0
}

DEFAULT_FILTERS = {
    "universe_min_volume": 1000000,   # scan sirf itne 24h USDT volume+ wale coins par
    "exclude": []                     # user-defined coins jo kabhi trade na hon (jaise QKC)
}

# Har user ka apna data yahan — live par ek user ka doosre se alag aur persistent
USER_BUCKETS = ["active_trades", "trade_history", "signals_feed", "signal_history", "logs"]

def _blank_user_settings():
    return {
        "exchange": {"name": "Binance", "market": "Spot", "key": "", "secret": "", "demo": True, "connected": False},
        "strategy": {
            "mode": "manual",
            "exec_mode": "Automated Trading (Bot takes trades & sets TP/SL automatically)",
            "ai_prompt": "",
            "manual": dict(DEFAULT_MANUAL_STRATEGY),
            "sl_pct": 2.0, "tp_pct": 4.5
        },
        "limits": {"campaign_days": 1, "daily_limit": 1, "trade_amount": 100.0},
        "filters": dict(DEFAULT_FILTERS),
        "runtime": dict(DEFAULT_RUNTIME),
        "email": {"enabled": True, "sender": "", "receiver": "", "brevo_api_key": ""},
        "bot_active": False,   # DB me persistent flag — asli "bot on/off" state (session/tab se independent)
        "active_trades": [], "trade_history": [], "signals_feed": [], "signal_history": [], "logs": []
    }

def _backfill_user(cfg):
    strat = cfg.setdefault("strategy", {})
    strat.setdefault("mode", "manual")
    strat.setdefault("exec_mode", "Automated Trading (Bot takes trades & sets TP/SL automatically)")
    strat.setdefault("manual", dict(DEFAULT_MANUAL_STRATEGY))
    for k, v in DEFAULT_MANUAL_STRATEGY.items():
        strat["manual"].setdefault(k, v)
    # purana "timeframe" (single) tha -> naya "timeframes" (list, multi-select) me migrate karo
    if not strat["manual"].get("timeframes"):
        old_tf = strat["manual"].get("timeframe", "1h")
        strat["manual"]["timeframes"] = [old_tf] if old_tf else ["1h"]
    strat["manual"].setdefault("ma_logic", "AND")
    strat.setdefault("ai_prompt", "")
    strat.setdefault("sl_pct", 2.0)
    strat.setdefault("tp_pct", 4.5)
    cfg.setdefault("bot_active", False)
    cfg.setdefault("exchange", {"name": "Binance", "market": "Spot", "key": "", "secret": "", "demo": True, "connected": False})
    cfg.setdefault("limits", {"campaign_days": 1, "daily_limit": 1, "trade_amount": 100.0})
    flt = cfg.setdefault("filters", dict(DEFAULT_FILTERS))
    for k, v in DEFAULT_FILTERS.items():
        flt.setdefault(k, v)
    rt = cfg.setdefault("runtime", dict(DEFAULT_RUNTIME))
    for k, v in DEFAULT_RUNTIME.items():
        rt.setdefault(k, v)
    email_cfg = cfg.setdefault("email", {"enabled": True, "sender": "", "receiver": "", "brevo_api_key": ""})
    email_cfg.setdefault("brevo_api_key", "")
    email_cfg.setdefault("sender", "")
    email_cfg.setdefault("receiver", "")
    email_cfg.setdefault("enabled", True)
    for b in USER_BUCKETS:
        cfg.setdefault(b, [])

def load_db():
    if not os.path.exists(DB_FILE):
        default_data = {"users": {}, "settings": {"admin": _blank_user_settings()}, "logs": []}
        with open(DB_FILE, "w") as f:
            json.dump(default_data, f, indent=4)

    with open(DB_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {"users": {}, "settings": {}, "logs": []}

    data.setdefault("users", {})
    data.setdefault("settings", {})
    data.setdefault("logs", [])
    if "admin" not in data["settings"]:
        data["settings"]["admin"] = _blank_user_settings()
    for uname, cfg in data["settings"].items():
        _backfill_user(cfg)
    return data

def save_db(db):
    """Atomic write — crash ya restart par file corrupt/khali na ho, data safe rahe."""
    tmp = DB_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(db, f, indent=4)
    os.replace(tmp, DB_FILE)

def get_runtime(user_settings):
    rt = user_settings.setdefault("runtime", dict(DEFAULT_RUNTIME))
    for k, v in DEFAULT_RUNTIME.items():
        rt.setdefault(k, v)
    today_str = str(date.today())
    if rt.get("trade_date") != today_str:
        rt["trade_date"] = today_str
        rt["trades_today"] = 0
        rt["signals_today"] = 0
        rt["traded_coins_today"] = []
        rt["last_action_epoch"] = 0
    return rt

# ------------------------------------------------------------------
# CROSS-TAB / CROSS-PROCESS FILE LOCK
# ------------------------------------------------------------------
def acquire_lock(timeout=8.0):
    start = time.time()
    while True:
        try:
            fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            try:
                os.write(fd, str(os.getpid()).encode())
            except Exception:
                pass
            return fd
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(LOCK_FILE) > STALE_LOCK_SEC:
                    os.remove(LOCK_FILE)
                    continue
            except FileNotFoundError:
                continue
            except Exception:
                pass
            if time.time() - start > timeout:
                return None
            time.sleep(0.2)

def release_lock(fd):
    if fd is None:
        return
    try:
        os.close(fd)
    except Exception:
        pass
    try:
        os.remove(LOCK_FILE)
    except Exception:
        pass

def try_reserve_slot(curr_user, chosen_coin, daily_lim, is_signal_only, min_gap=MIN_ACTION_GAP_SEC):
    """Order se PEHLE slot reserve (lock ke andar): limit + duplicate-coin + cooldown check. Returns (ok, reason, fresh_db)."""
    lock = acquire_lock()
    if lock is None:
        return False, "busy (dusra tab active)", load_db()
    try:
        fresh = load_db()
        us = fresh["settings"].get(curr_user)
        if us is None:
            return False, "user missing", fresh
        rtf = get_runtime(us)
        now = time.time()
        if now - float(rtf.get("last_action_epoch", 0)) < min_gap:
            return False, "cooldown", fresh
        active_syms = {t.get("Symbol", "") for t in (us.get("active_trades") or []) if t.get("Symbol")}
        if (not is_signal_only) and chosen_coin in active_syms:
            return False, "coin already has an open trade", fresh
        if not is_signal_only:
            if rtf["trades_today"] >= daily_lim:
                return False, "limit reached", fresh
            rtf["trades_today"] += 1
        else:
            rtf["signals_today"] += 1
        rtf["last_action_epoch"] = now
        save_db(fresh)
        return True, "reserved", fresh
    finally:
        release_lock(lock)


def rollback_reserved_slot(username, chosen_coin, is_signal_only):
    """Buy fail / exchange not connected — daily slot wapas, ghost trade na bane."""
    lock = acquire_lock()
    if lock is None:
        return
    try:
        fresh = load_db()
        us = fresh["settings"].get(username)
        if us is None:
            return
        rtf = get_runtime(us)
        if is_signal_only:
            if int(rtf.get("signals_today", 0) or 0) > 0:
                rtf["signals_today"] = int(rtf["signals_today"]) - 1
        else:
            if int(rtf.get("trades_today", 0) or 0) > 0:
                rtf["trades_today"] = int(rtf["trades_today"]) - 1
        coins = rtf.get("traded_coins_today") or []
        if chosen_coin in coins:
            coins.remove(chosen_coin)
            rtf["traded_coins_today"] = coins
        save_db(fresh)
    finally:
        release_lock(lock)


def _is_futures_market(market):
    return "Futures" in str(market or "")


def _base_from_symbol(sym):
    s = str(sym or "")
    if "/" in s:
        return s.split("/")[0].split(":")[0]
    return s.split(":")[0]


@st.cache_resource
def get_bot_registry():
    """Process-wide singleton (Streamlit reruns poori script har interaction par dobara
    chalata hai, isliye normal global variable har baar reset ho jata — is decorator ki
    wajah se ye dict/lock HAMESHA wahi ek object rahega, chahe kitni bhi reruns hon)."""
    return {"threads": {}, "lock": threading.Lock()}


def _run_one_bot_cycle(username):
    """Ek user ke liye bot ka EK scan+trade cycle. Koi Streamlit UI call (st.rerun,
    st.warning, st.session_state) use NAHI karta — isliye background thread me bhi
    (bina kisi browser tab ke) chal sakta hai. Returns False = thread ko rukna chahiye."""
    dbx = load_db()
    us = dbx["settings"].get(username)
    if us is None or not us.get("bot_active"):
        return False

    _backfill_user(us)
    rt = get_runtime(us)
    save_db(dbx)

    daily_lim = int(us["limits"].get("daily_limit", 1))
    exec_mode_setting = us["strategy"].get("exec_mode", "")
    is_signal_only = "Signal-Only" in exec_mode_setting or "Signal" in exec_mode_setting

    # ---------- PEHLE: Active trades ka TP/SL filled check, PnL settle + history shift ----------
    monitor_close_active_trades(username)
    fresh_act = load_db()
    us2 = fresh_act["settings"].get(username) or us
    active_syms_now = {t.get("Symbol", "") for t in (us2.get("active_trades", []) or []) if t.get("Symbol")}
    rt2 = get_runtime(us2)

    if (not is_signal_only) and rt2["trades_today"] >= daily_lim:
        add_log(f"⏳ Daily auto-trade limit reached ({rt2['trades_today']}/{daily_lim}). Aaj ke liye paused (kal reset).", username)
        return True

    try:
        ex_cfg = us2["exchange"]
        market_m = ex_cfg.get("market", "Spot")
        # Dynamic exchange factory: Binance/Bybit/OKX/KuCoin koi bhi select ho sahi ccxt object
        ex = create_exchange(ex_cfg)

        ex.load_markets()
        flt = us2.get("filters", DEFAULT_FILTERS)

        # Cached tickers use karo — baar-baar API hit nahi, CPU/RAM bachao
        all_tickers = get_cached_tickers(ex)
        if all_tickers is None:
            try:
                all_tickers = ex.fetch_tickers()
            except Exception:
                all_tickers = None

        # ---- FULL UNIVERSE SCAN — koi 25/40 wali cap nahi, jitne bhi coin criteria
        # (volume/stablecoin/leveraged/delisted filters) pass karein sab scan honge.
        universe = build_symbol_universe(ex, all_tickers,
                                         min_volume=int(flt.get("universe_min_volume", 1000000)),
                                         exclude_bases=flt.get("exclude", []),
                                         market=market_m)
        if not universe:
            excl = {e.upper() for e in flt.get("exclude", [])}
            if _is_futures_market(market_m):
                universe = [s for s in (ex.symbols or [])
                            if (":USDT" in s or s.endswith("/USDT"))
                            and _base_from_symbol(s).upper() not in STABLE_OR_FIAT
                            and _base_from_symbol(s).upper() not in excl]
            else:
                universe = [s for s in (ex.symbols or [])
                            if s.endswith('/USDT') and s.split('/')[0].upper() not in STABLE_OR_FIAT
                            and s.split('/')[0].upper() not in excl]
        if not universe:
            universe = ["BTC/USDT:USDT", "ETH/USDT:USDT"] if _is_futures_market(market_m) else ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

        # Open position wale coin skip — close hone ke baad (daily limit bachi ho to) dubara allowed
        excluded_now = set(active_syms_now) if not is_signal_only else set()
        available = [c for c in universe if c not in excluded_now]
        if not available:
            if active_syms_now and not is_signal_only:
                add_log(f"🔎 Active positions me {len(active_syms_now)} coin hain — unke close hone tak in par dobara trade nahi. Idling.", username)
            else:
                add_log("🔎 Scan universe empty after filters. Idling.", username)
            return True

        chosen_coin = None; c_price = 0.0; matched_rules_str = ""
        strategy_mode = "manual"
        manual_cfg = us2["strategy"]["manual"]
        candidates = []
        for coin in available:
            try:
                passed, rules = evaluate_manual_strategy(ex, coin, manual_cfg)
                if passed:
                    candidates.append((coin, rules))
            except Exception:
                continue
        if candidates:
            best = None; best_vol = -1
            for coin, rules in candidates:
                vol = 0.0
                if all_tickers and coin in all_tickers:
                    try: vol = float(all_tickers[coin].get('quoteVolume') or 0)
                    except Exception: vol = 0.0
                else:
                    try: vol = float(ex.fetch_ticker(coin).get('quoteVolume') or 0)
                    except Exception: vol = 0.0
                if vol > best_vol:
                    best_vol = vol; best = (coin, rules)
            chosen_coin, matched_rules_list = best
            matched_rules_str = ", ".join(matched_rules_list)
            try:
                c_price = float(ex.fetch_ticker(chosen_coin).get('last') or 0.0)
            except Exception:
                c_price = 0.0
        else:
            add_log("🔎 Manual scan complete — koi coin saari ticked conditions match nahi kar raha. Idling.", username)

        if chosen_coin is None:
            return True

        ok, reason, dbx3 = try_reserve_slot(username, chosen_coin, daily_lim, is_signal_only)
        us3 = dbx3["settings"][username]
        rt3 = get_runtime(us3)

        if ok and not is_signal_only and rt3["trades_today"] > daily_lim:
            rt3["trades_today"] = daily_lim
            if chosen_coin in rt3["traded_coins_today"]:
                rt3["traded_coins_today"].remove(chosen_coin)
            save_db(dbx3)
            add_log(f"🛡️ Safety rollback: {chosen_coin} reservation undo ki gayi (limit {daily_lim} already reached tha).", username)
            ok = False
            reason = "limit reached"

        if not ok:
            if reason == "limit reached":
                add_log(f"⏳ Limit reached ({rt3['trades_today']}/{daily_lim}) — {chosen_coin} skip. Paused for today.", username)
            else:
                add_log(f"↩️ {chosen_coin} skip ({reason}). Agla coin dekhenge.", username)
            return True

        if c_price <= 0:
            try:
                ohlcv = ex.fetch_ohlcv(chosen_coin, timeframe='1m', limit=1)
                if ohlcv: c_price = float(ohlcv[0][4])
            except Exception:
                c_price = 1.0

        amt_usdt = float(us3["limits"]["trade_amount"])
        try:
            coin_qty = float(ex.amount_to_precision(chosen_coin, amt_usdt / c_price))
        except Exception:
            coin_qty = amt_usdt / c_price

        tp_p = us3["strategy"]["tp_pct"]; sl_p = us3["strategy"]["sl_pct"]
        tp_val = c_price * (1 + tp_p / 100); sl_val = c_price * (1 - sl_p / 100)

        current_time_str = datetime.now().strftime("%I:%M:%S %p")
        full_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp_epoch = datetime.now().timestamp()

        new_signal = {
            "id": f"{chosen_coin}_{int(timestamp_epoch)}",
            "time": current_time_str, "full_timestamp": full_ts, "timestamp_epoch": timestamp_epoch,
            "symbol": chosen_coin,
            "strategy": "Manual Rule Engine" if strategy_mode == "manual" else "AI Prompt Engine",
            "rules": matched_rules_str, "entry": c_price, "tp": tp_val, "sl": sl_val,
            "type": "Signal Only" if is_signal_only else "Executed Trade"
        }

        # ---- signal record save (apna alag lock — try_reserve_slot ka lock already release ho chuka hai) ----
        lock2 = acquire_lock()
        try:
            dbx4 = load_db()
            us4 = dbx4["settings"].get(username)
            if us4 is not None:
                us_feed = us4.setdefault("signals_feed", [])
                us_hist = us4.setdefault("signal_history", [])
                active_signals = []
                for sig in us_feed:
                    if (timestamp_epoch - sig.get("timestamp_epoch", timestamp_epoch)) >= 86400:
                        if sig not in us_hist:
                            us_hist.insert(0, sig)
                    else:
                        active_signals.append(sig)
                active_signals.insert(0, new_signal)
                us4["signals_feed"] = active_signals
                save_db(dbx4)
        finally:
            if lock2 is not None:
                release_lock(lock2)

        email_cfg = us3.get("email", {})
        if email_cfg.get("enabled"):
            email_sub = f"🚨 [Apex Trading] {'Signal Generated' if is_signal_only else 'Trade Executed'}: {chosen_coin}"
            email_body_html = f"""
            <html><body style="font-family: Arial, sans-serif; background-color: #0b0e11; color: #eaecef; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background: #181a20; border: 1px solid #2b313a; border-radius: 12px; padding: 25px;">
                    <h2 style="color: #fcd535; margin-top: 0; text-align: center;">⚡ Apex Automated Alert</h2>
                    <p style="color: #0ecb81; text-align: center; font-weight: bold;">Status: Strategy conditions successfully met!</p>
                    <p style="color: #848e9c; text-align:center; font-size:12px;">Matched rules: {matched_rules_str or "N/A"}</p>
                    <hr style="border: 0; border-top: 1px solid #2b313a; margin: 20px 0;">
                    <table style="width: 100%; font-size: 14px; color: #eaecef; border-collapse: collapse;">
                        <tr><td style="padding: 8px 0; color: #848e9c;">Trading Pair:</td><td style="padding: 8px 0; font-weight: bold; color: #fcd535; text-align: right;">{chosen_coin}</td></tr>
                        <tr><td style="padding: 8px 0; color: #848e9c;">Market Type:</td><td style="padding: 8px 0; font-weight: bold; text-align: right;">{market_m}</td></tr>
                        <tr><td style="padding: 8px 0; color: #848e9c;">Entry Price:</td><td style="padding: 8px 0; font-weight: bold; color: #3b82f6; text-align: right;">${c_price:,.6f}</td></tr>
                        <tr><td style="padding: 8px 0; color: #848e9c;">Take Profit (TP):</td><td style="padding: 8px 0; font-weight: bold; color: #0ecb81; text-align: right;">${tp_val:,.6f} (+{tp_p}%)</td></tr>
                        <tr><td style="padding: 8px 0; color: #848e9c;">Stop Loss (SL):</td><td style="padding: 8px 0; font-weight: bold; color: #f6465d; text-align: right;">${sl_val:,.6f} (-{sl_p}%)</td></tr>
                        <tr><td style="padding: 8px 0; color: #848e9c;">Allocated Amount:</td><td style="padding: 8px 0; font-weight: bold; text-align: right;">${amt_usdt} USDT</td></tr>
                    </table>
                </div></body></html>"""
            send_email_alert(email_sub, email_body_html, email_cfg)

        if is_signal_only:
            add_log(f"📡 Signal #{rt3['signals_today']} generated for {chosen_coin} (rules: {matched_rules_str}).", username)
            return True

        # -------- AUTO TRADE (Spot path aur Futures path alag — mix nahi) --------
        placed_ok = False
        if "Automated Trading" in exec_mode_setting:
            if not (ex_cfg.get("connected") and ex_cfg.get("key")):
                add_log(f"⚠️ {chosen_coin}: exchange not connected — signal recorded, koi live order nahi. Slot rollback.", username)
                rollback_reserved_slot(username, chosen_coin, is_signal_only)
            elif market_m == "Spot" and _is_futures_market(market_m):
                add_log("⚠️ Market setting inconsistent — order skip.", username)
                rollback_reserved_slot(username, chosen_coin, is_signal_only)
            else:
                if _is_futures_market(market_m):
                    try:
                        ex.set_leverage(FUTURES_SAFE_LEVERAGE, chosen_coin)
                        add_log(f"🛡️ Futures leverage set — {chosen_coin} @ {FUTURES_SAFE_LEVERAGE}x", username)
                    except Exception as _lv_err:
                        add_log(f"⚠️ Futures leverage set note ({chosen_coin}): {str(_lv_err)[:80]}", username)
                    try:
                        set_margin_fn = getattr(ex, "set_margin_mode", None)
                        if callable(set_margin_fn):
                            set_margin_fn(FUTURES_MARGIN_MODE, chosen_coin)
                    except Exception as _mg_err:
                        add_log(f"⚠️ Futures margin note ({chosen_coin}): {str(_mg_err)[:80]}", username)

                try:
                    formatted_tp_price = float(ex.price_to_precision(chosen_coin, tp_val))
                    formatted_sl_price = float(ex.price_to_precision(chosen_coin, sl_val))
                except Exception:
                    formatted_tp_price = tp_val; formatted_sl_price = sl_val

                if market_m == "Spot" and not _is_futures_market(market_m):
                    try:
                        buy_res = ex.create_market_buy_order(chosen_coin, coin_qty)
                        placed_ok = True
                        add_log(f"✅ Spot Market Buy Executed for {chosen_coin} (rules: {matched_rules_str})", username)
                    except Exception as buy_err:
                        add_log(f"❌ Buy Order Error: {str(buy_err)[:180]}", username); buy_res = None
                    if buy_res:
                        time.sleep(1.5)
                        base_ccy = _base_from_symbol(chosen_coin); sell_qty = coin_qty
                        try:
                            bal = ex.fetch_balance()
                            free_amt = float(bal['free'].get(base_ccy, 0) or 0)
                            if free_amt > 0: sell_qty = free_amt
                        except Exception: pass
                        try: sell_qty = float(ex.amount_to_precision(chosen_coin, sell_qty))
                        except Exception: pass
                        try: sl_limit_price = float(ex.price_to_precision(chosen_coin, sl_val * 0.997))
                        except Exception: sl_limit_price = formatted_sl_price
                        oco_done = False
                        oco_fn = getattr(ex, 'private_post_order_oco', None)
                        if oco_fn is not None:
                            try:
                                oco_sym = chosen_coin.replace('/', '').replace(':USDT', '')
                                oco_fn({'symbol': oco_sym, 'side': 'SELL',
                                        'quantity': ex.amount_to_precision(chosen_coin, sell_qty),
                                        'price': ex.price_to_precision(chosen_coin, formatted_tp_price),
                                        'stopPrice': ex.price_to_precision(chosen_coin, formatted_sl_price),
                                        'stopLimitPrice': ex.price_to_precision(chosen_coin, sl_limit_price),
                                        'stopLimitTimeInForce': 'GTC'})
                                add_log(f"🛡️ OCO placed — TP ${formatted_tp_price} / SL ${formatted_sl_price}", username)
                                oco_done = True
                            except Exception as oco_err:
                                add_log(f"⚠️ OCO not available ({str(oco_err)[:70]}), trying separate SL/TP...", username)
                        if not oco_done:
                            try:
                                ex.create_order(chosen_coin, 'STOP_LOSS_LIMIT', 'sell', sell_qty, sl_limit_price, {'stopPrice': formatted_sl_price})
                                add_log(f"🛡️ Stop Loss placed at trigger ${formatted_sl_price}", username)
                            except Exception:
                                try:
                                    ex.create_order(chosen_coin, 'STOP_LOSS', 'sell', sell_qty, None, {'stopPrice': formatted_sl_price})
                                    add_log(f"🛡️ Stop Loss (Market) placed at trigger ${formatted_sl_price}", username)
                                except Exception as sl_fallback_err:
                                    add_log(f"⚠️ Stop Loss Order Warning: {str(sl_fallback_err)[:120]}", username)
                            try:
                                bal2 = ex.fetch_balance()
                                free2 = float(bal2['free'].get(base_ccy, 0) or 0)
                                tp_qty = float(ex.amount_to_precision(chosen_coin, free2)) if free2 > 0 else 0
                                if tp_qty > 0:
                                    ex.create_limit_sell_order(chosen_coin, tp_qty, formatted_tp_price)
                                    add_log(f"🎯 Take Profit placed at ${formatted_tp_price}", username)
                            except Exception as tp_err:
                                add_log(f"⚠️ TP Order Warning: {str(tp_err)[:120]}", username)
                elif _is_futures_market(market_m):
                    try:
                        ex.create_market_buy_order(chosen_coin, coin_qty)
                        placed_ok = True
                        add_log(f"✅ Futures Market Buy executed for {chosen_coin} (rules: {matched_rules_str})", username)
                    except Exception as fut_buy_err:
                        add_log(f"❌ Futures Buy Error: {str(fut_buy_err)[:180]}", username)
                    if placed_ok:
                        try:
                            time.sleep(1)
                            ex.create_order(chosen_coin, 'TAKE_PROFIT_MARKET', 'sell', coin_qty, None, {'stopPrice': formatted_tp_price, 'reduceOnly': True})
                            add_log(f"🎯 Futures Take Profit set at ${formatted_tp_price}", username)
                            ex.create_order(chosen_coin, 'STOP_MARKET', 'sell', coin_qty, None, {'stopPrice': formatted_sl_price, 'reduceOnly': True})
                            add_log(f"🛡️ Futures Stop Loss set at ${formatted_sl_price}", username)
                        except Exception as fut_err:
                            add_log(f"⚠️ Futures TP/SL note: {str(fut_err)[:120]}", username)
                else:
                    add_log(f"⚠️ Unknown market '{market_m}' — order skip, slot rollback.", username)
                    rollback_reserved_slot(username, chosen_coin, is_signal_only)

                if not placed_ok and (ex_cfg.get("connected") and ex_cfg.get("key")):
                    rollback_reserved_slot(username, chosen_coin, is_signal_only)

        if placed_ok:
            lock3 = acquire_lock()
            try:
                dbx5 = load_db()
                us5 = dbx5["settings"].get(username)
                if us5 is not None:
                    us5.setdefault("active_trades", []).append({
                        "Symbol": chosen_coin, "Market": market_m,
                        "Entry": f"{c_price:,.6f}", "Amount": f"${amt_usdt}",
                        "TP": f"{tp_val:,.6f}", "SL": f"{sl_val:,.6f}", "Rules": matched_rules_str
                    })
                    save_db(dbx5)
            finally:
                if lock3 is not None:
                    release_lock(lock3)
            rt_after = get_runtime(load_db()["settings"].get(username) or us3)
            add_log(f"📊 Auto trade {rt_after.get('trades_today', rt3['trades_today'])}/{daily_lim} done for {chosen_coin}.", username)
            if int(rt_after.get("trades_today", 0) or 0) >= daily_lim:
                add_log(f"✅ Aaj ki limit ({daily_lim}) complete. Bot ab naye auto-trade nahi lega — open trades monitor honge.", username)

    except Exception as e:
        add_log(f"⚠️ Loop Error: {str(e)}", username)

    return True


def _bot_thread_main(username):
    """Ye function EK background thread me chalta hai, jab tak us user ka bot_active
    True rahe. Kisi bhi browser tab/session se bilkul independent — tab band karo,
    phone lock karo, PC minimize karo, ye chalta rehta hai jab tak khud STOP na dabao."""
    add_log("🟢 Background bot thread shuru — ab browser/phone band karne se bhi ye RUKEGA NAHI.", username)
    while True:
        try:
            keep_going = _run_one_bot_cycle(username)
        except Exception as e:
            add_log(f"⚠️ Bot thread fatal error: {str(e)}", username)
            keep_going = True
        if keep_going is False:
            break
        time.sleep(15)
    add_log("🛑 Background bot thread ruk gaya (Stop Bot dabaya gaya tha).", username)


def ensure_all_bot_threads():
    """Har us user ke liye jiska bot_active=True hai, ek background thread chalao (agar
    pehle se chal raha ho to dobara nahi). Ye function HAR page-load/interaction par
    call hota hai (kisi ke bhi) — isliye agar server restart bhi ho jaye, jaise hi
    koi bhi pehla visitor site kholega, saare active bots khud-ba-khud resume ho jayenge."""
    registry = get_bot_registry()
    with registry["lock"]:
        try:
            dbx = load_db()
        except Exception:
            return
        for uname, cfg in dbx.get("settings", {}).items():
            if cfg.get("bot_active"):
                th = registry["threads"].get(uname)
                if th is None or not th.is_alive():
                    t = threading.Thread(target=_bot_thread_main, args=(uname,), daemon=True)
                    registry["threads"][uname] = t
                    t.start()
        for uname in list(registry["threads"].keys()):
            th = registry["threads"][uname]
            if not th.is_alive():
                del registry["threads"][uname]


db = load_db()
ensure_all_bot_threads()
ACTIVE_USER = None  # login ke baad set hota hai; add_log isi user ke logs me likhta hai

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = ""
# NOTE: bot on/off ab st.session_state me store NAHI hota (wo browser tab ke sath khatam
# ho jata) — ab DB me `user_settings["bot_active"]` persist hota hai aur ek background
# thread (ensure_all_bot_threads) isko chalata hai, tab/session se bilkul independent.

def add_log(msg, username=None):
    """Thread-safe log append. Hamesha DISK se fresh load karke likhta hai (file-lock ke
    sath) taake background bot-threads aur UI ke beech log lines ek dusre ko overwrite
    na karen — pehle sirf in-memory `db` par likhta tha, jo multi-thread me unsafe tha."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    target_user = username or ACTIVE_USER
    lock = acquire_lock(timeout=5.0)
    try:
        fresh = load_db()
        try:
            if target_user and target_user in fresh.get("settings", {}):
                fresh["settings"][target_user].setdefault("logs", []).append(line)
            else:
                fresh.setdefault("logs", []).append(line)
        except Exception:
            fresh.setdefault("logs", []).append(line)
        save_db(fresh)
    finally:
        if lock is not None:
            release_lock(lock)

# ------------------------------------------------------------------
# EMAIL — Brevo HTTPS API (SMTP ports 25/465/587 DigitalOcean par HAMESHA
# block rehte hain — ye unki apni official policy hai, spam rokne ke liye,
# aur kisi bhi SMTP provider ke liye lagu hoti hai, chahe wo Gmail ho ya
# koi aur). Isliye email ab HTTPS (port 443) ke zariye Brevo ki API se
# bheji jati hai — ye port kabhi block nahi hota (isi se bot Binance se
# baat karta hai). Poore app me email sirf isi function se jaati hai, is
# liye trade/signal ke waqt jahan pehle call hoti thi, wahi ab bhi hoti
# hai — koi aur jagah kuch badalna nahi pada.
# ------------------------------------------------------------------
_orig_getaddrinfo = socket.getaddrinfo

def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

def send_email_alert(subject, body_html, email_cfg):
    if not email_cfg.get("enabled") or not email_cfg.get("sender") or not email_cfg.get("receiver"):
        return False
    api_key = dec_secret(email_cfg.get("brevo_api_key", ""))
    api_key = api_key.strip() if api_key else ""
    if not api_key:
        add_log("Email Error: Brevo API key set nahi hai — Limitation & Campaign me daalo.")
        return False
    payload = json.dumps({
        "sender": {"name": "Apex Trading Bot", "email": email_cfg["sender"]},
        "to": [{"email": email_cfg["receiver"]}],
        "subject": subject,
        "htmlContent": body_html
    }).encode("utf-8")
    req = urllib.request.Request(
        BREVO_API_URL, data=payload, method="POST",
        headers={"api-key": api_key, "Content-Type": "application/json", "Accept": "application/json"}
    )
    # -------- Thread-safe socket IPv4 swap (EMAIL_LOCK) --------
    EMAIL_LOCK.acquire()
    swapped_back = False
    try:
        socket.getaddrinfo = _ipv4_only_getaddrinfo
        swapped_back = False
    except Exception:
        pass
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            # WAPAS RESTORE jaldi se — baaki socket ka code (ccxt Binance API) lock chhode hi normal ho jaye
            try:
                socket.getaddrinfo = _orig_getaddrinfo
                swapped_back = True
            except Exception:
                pass
            try:
                EMAIL_LOCK.release()
            except Exception:
                pass
            if 200 <= resp.status < 300:
                return True
            add_log(f"Email Error: Brevo HTTP {resp.status}")
            return False
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", errors="ignore")
        except Exception:
            err_body = ""
        add_log(f"Email Error: Brevo HTTP {e.code} - {err_body[:300]}")
        return False
    except Exception as e:
        add_log(f"Email Error: {str(e)}")
        return False
    finally:
        if not swapped_back:
            try:
                socket.getaddrinfo = _orig_getaddrinfo
            except Exception:
                pass
        try:
            if EMAIL_LOCK.locked():
                EMAIL_LOCK.release()
        except Exception:
            pass


# ------------------------------------------------------------------
# COIN UNIVERSE FILTER
# Sirf real, liquid, tradeable USDT spot coins. Stablecoins/fiat, leveraged tokens,
# inactive/delisted pairs, aur user ke exclude-list wale coins (jaise Monitoring-Tag) hata dete hain.
# ------------------------------------------------------------------
STABLE_OR_FIAT = {
    "USDT", "USDC", "BUSD", "FDUSD", "TUSD", "DAI", "USDP", "PAX", "PYUSD", "USDD",
    "AEUR", "EUR", "EURI", "EURT", "GBP", "AUD", "BRL", "TRY", "RUB", "UAH", "NGN",
    "IDRT", "ZAR", "ARS", "BIDR", "VAI", "UST", "USTC", "GUSD", "SUSD", "XUSD", "BVND"
}

def _is_leveraged_token(base):
    b = (base or "").upper()
    if "BULL" in b or "BEAR" in b:
        return True
    if len(b) >= 5 and (b.endswith("UP") or b.endswith("DOWN")):
        return True
    return False

def build_symbol_universe(ex, tickers=None, min_volume=1_000_000, top_n=None, exclude_bases=None, market="Spot"):
    """
    top_n=None -> koi cap nahi, jitne bhi coin criteria pe fit hon SAB scan honge.
    Spot select ho to sirf spot USDT pairs; Futures select ho to sirf USDT-M swap.
    """
    exclude_bases = {e.strip().upper() for e in (exclude_bases or []) if e.strip()}
    markets = getattr(ex, "markets", {}) or {}
    want_futures = _is_futures_market(market)
    universe = []
    for sym, m in markets.items():
        try:
            if m.get("active", True) is False:
                continue
            base = (m.get("base") or _base_from_symbol(sym)).upper()
            if base in STABLE_OR_FIAT or base in exclude_bases:
                continue
            if _is_leveraged_token(base):
                continue
            quote = (m.get("quote") or "").upper()
            settle = (m.get("settle") or "").upper()
            if want_futures:
                if m.get("spot") is True and not m.get("swap"):
                    continue
                if m.get("inverse"):
                    continue
                is_usdt_m = bool(m.get("swap")) or bool(m.get("linear"))
                if not is_usdt_m:
                    continue
                if quote != "USDT" and settle != "USDT" and ":USDT" not in str(sym):
                    continue
            else:
                if m.get("spot") is False:
                    continue
                if m.get("swap") or m.get("future"):
                    continue
                if not str(sym).endswith("/USDT"):
                    continue
            universe.append(sym)
        except Exception:
            continue

    if tickers:
        scored = []
        for sym in universe:
            t = tickers.get(sym) or {}
            try:
                qv = float(t.get("quoteVolume") or 0)
            except Exception:
                qv = 0.0
            if qv >= min_volume:
                scored.append((sym, qv))
        scored.sort(key=lambda x: x[1], reverse=True)
        if scored:
            ordered = [s for s, _ in scored]
            return ordered[:top_n] if top_n else ordered
    return universe[:top_n] if top_n else universe

# ==========================================
# EXCHANGE FACTORY  (Spot/Futures sahi, har exchange ke sandbox URLs, leverage set)
# ==========================================
EXCHANGE_LIST = ["Binance", "Bybit", "OKX", "KuCoin"]
# Per-exchange sandbox — sirf Binance URLs hardcode (ccxt demo-api). Baaki exchanges
# ccxt.set_sandbox_mode() par depend karte hain (galat public/private overwrite nahi).
_EXCHANGE_SANDBOX = {
    "Binance": {
        "spot":     {"public": "https://demo-api.binance.com/api/v3", "private": "https://demo-api.binance.com/api/v3"},
        "futures":  {"fapiPublic": "https://testnet.binancefuture.com/fapi/v1", "fapiPrivate": "https://testnet.binancefuture.com/fapi/v1"},
    },
}
FUTURES_SAFE_LEVERAGE = 3    # default safe leverage — liquidation risk kam
FUTURES_MARGIN_MODE = "isolated"  # cross nahi — sirf itna hi margin use, poora account safe

def create_exchange(ex_cfg):
    """
    ex_cfg = {"name": "Binance", "market": "Spot"|"Futures (Derivatives)",
              "key": "...", "secret": "...", "demo": True/False}
    Returns: ccxt exchange object — Spot = spot, Futures = USDT-M swap (coin-m nahi).
    """
    name = (ex_cfg.get("name") or "Binance").strip()
    market = (ex_cfg.get("market") or "Spot").strip()
    is_futures = _is_futures_market(market)
    api_key = dec_secret(ex_cfg.get("key", ""))
    secret = dec_secret(ex_cfg.get("secret", ""))
    demo = bool(ex_cfg.get("demo", True))

    ccxt_class_name = name.lower()
    if not hasattr(ccxt, ccxt_class_name):
        ccxt_class_name = "binance"  # fallback
    cls = getattr(ccxt, ccxt_class_name)

    default_type = "swap" if is_futures else "spot"
    ex_obj = cls({
        "apiKey": api_key or "",
        "secret": secret or "",
        "enableRateLimit": True,
        "options": {"defaultType": default_type, "adjustForTimeDifference": True, "defaultSubType": "linear"},
    })

    if demo:
        try:
            ex_obj.set_sandbox_mode(True)
        except Exception:
            pass
        sb = _EXCHANGE_SANDBOX.get(name, {})
        endpoints = sb.get("futures" if is_futures else "spot", {})
        try:
            for k, v in endpoints.items():
                if k in ex_obj.urls.get("api", {}):
                    ex_obj.urls["api"][k] = v
        except Exception:
            pass

    if is_futures and api_key:
        for _sym in ["BTC/USDT:USDT", "ETH/USDT:USDT", "BTC/USDT", "ETH/USDT"]:
            try:
                ex_obj.set_leverage(FUTURES_SAFE_LEVERAGE, _sym)
            except Exception:
                pass
            try:
                set_margin_fn = getattr(ex_obj, "set_margin_mode", None)
                if callable(set_margin_fn):
                    set_margin_fn(FUTURES_MARGIN_MODE, _sym)
            except Exception:
                pass

    return ex_obj


# ==========================================
# UNIVERSE / TICKERS CACHE  (har UNIVERSE_CACHE_TTL seconds me refresh, CPU bachao)
# ==========================================
_UNIVERSE_CACHE = {"data": None, "tickers": None, "ts": 0}

def get_cached_tickers(ex):
    """Cached tickers fetch — baar-baar Binance API hit nahi hoga."""
    global _UNIVERSE_CACHE
    now = time.time()
    if _UNIVERSE_CACHE["tickers"] is not None and (now - _UNIVERSE_CACHE["ts"]) < UNIVERSE_CACHE_TTL:
        return _UNIVERSE_CACHE["tickers"]
    try:
        _UNIVERSE_CACHE["tickers"] = ex.fetch_tickers()
        _UNIVERSE_CACHE["ts"] = now
    except Exception:
        _UNIVERSE_CACHE["tickers"] = None
    return _UNIVERSE_CACHE["tickers"]


# ==========================================
# EMAIL THREAD LOCK  (socket monkeypatch thread-safe banao)
# ==========================================
EMAIL_LOCK = threading.Lock()


# ==========================================
# ACTIVE TRADE CLOSED MONITOR + PnL CALCULATOR
# ==========================================
def _is_order_filled(ex_obj, sym, order_id_hint=None):
    """Try best-effort: check recent trades/orders to decide if TP/SL already filled."""
    try:
        trades = ex_obj.fetch_my_trades(sym, None, 20)
        if trades and len(trades) >= 2:
            return True
    except Exception:
        pass
    return False

def _get_live_price(ex_obj, sym, fallback=0.0):
    try:
        return float(ex_obj.fetch_ticker(sym).get("last") or fallback)
    except Exception:
        return fallback

def monitor_close_active_trades(username):
    """
    Bot cycle ke start me call hota hai:
    (A) Exchange se check karega ki kisi active trade ka TP/SL hit ho gaya (order filled)
    (B) Agar user manually exchange se close karde to usko bhi pata chalega
    (C) Close hone par PnL calculate karke trade_history me shift karega
    """
    lock_a = acquire_lock(timeout=7.0)
    if lock_a is None:
        return
    try:
        fresh = load_db()
        us = fresh["settings"].get(username)
        if us is None:
            return
        active_list = us.get("active_trades", []) or []
        if not active_list:
            return
        ex_cfg = us.get("exchange") or {}
        if not (ex_cfg.get("connected") and ex_cfg.get("key")):
            # Exchange connect nahi — bas price check karke unrealized show; history shift nahi hoga safe
            return
        try:
            ex_obj = create_exchange(ex_cfg)
        except Exception:
            return
        changed = False
        closed_any = False
        still_active = []
        for trade in list(active_list):
            sym = trade.get("Symbol", "")
            entry_str = str(trade.get("Entry", "0")).replace(",", "")
            try:
                entry_price = float(entry_str)
            except Exception:
                entry_price = 0.0
            amt_str = str(trade.get("Amount", "$0")).replace("$", "").replace(",", "").strip()
            try:
                amt_usdt = float(amt_str)
            except Exception:
                amt_usdt = 0.0
            tp_str = str(trade.get("TP", "0")).replace(",", "")
            sl_str = str(trade.get("SL", "0")).replace(",", "")
            try:
                tp_price = float(tp_str)
                sl_price = float(sl_str)
            except Exception:
                tp_price = 0.0
                sl_price = 0.0
            live_price = _get_live_price(ex_obj, sym, fallback=0.0)

            tp_hit = (tp_price > 0) and (live_price >= tp_price)
            sl_hit = (sl_price > 0) and (live_price <= sl_price)
            order_filled = _is_order_filled(ex_obj, sym)
            is_closed = tp_hit or sl_hit or order_filled

            close_price_used = live_price if live_price > 0 else entry_price
            if tp_hit:
                close_price_used = tp_price
            elif sl_hit:
                close_price_used = sl_price

            pnl_val = 0.0
            pnl_pct = 0.0
            if entry_price > 0 and close_price_used > 0 and amt_usdt > 0:
                pnl_pct = ((close_price_used - entry_price) / entry_price) * 100
                pnl_val = (pnl_pct / 100.0) * amt_usdt

            if is_closed:
                status_txt = "PROFIT" if pnl_val >= 0 else "LOSS"
                history_entry = {
                    "date": str(date.today()),
                    "time": datetime.now().strftime("%I:%M:%S %p"),
                    "Symbol": sym,
                    "Market": trade.get("Market", "Spot"),
                    "Entry": f"{entry_price:,.6f}",
                    "Close": f"{close_price_used:,.6f}",
                    "Amount": f"${amt_usdt:,.2f}",
                    "PnL%": f"{pnl_pct:+.2f}%",
                    "pnl_val": pnl_val,
                    "status": status_txt,
                    "Reason": ("TP Hit" if tp_hit else ("SL Hit" if sl_hit else "Order Filled/Manually Closed")),
                    "Rules": trade.get("Rules", ""),
                }
                us.setdefault("trade_history", []).insert(0, history_entry)
                changed = True
                closed_any = True
                add_log(f"✅ {sym} closed — {history_entry['Reason']}, PnL ${pnl_val:+,.2f} ({pnl_pct:+.2f}%). Moved to History.", username)
            else:
                # Live PnL + current_price update kar do (UI me dikhne ke liye)
                trade["LivePrice"] = f"{live_price:,.6f}" if live_price > 0 else trade.get("Entry", "0")
                if entry_price > 0 and live_price > 0 and amt_usdt > 0:
                    up_pct = ((live_price - entry_price) / entry_price) * 100
                    up_val = (up_pct / 100.0) * amt_usdt
                    trade["Unrealized"] = f"{up_val:+,.2f} USD ({up_pct:+.2f}%)"
                else:
                    trade["Unrealized"] = trade.get("Unrealized", "—")
                still_active.append(trade)
        if changed:
            us["active_trades"] = still_active
            save_db(fresh)
    except Exception as ex_err:
        try:
            add_log(f"⚠️ monitor_close_active_trades issue: {str(ex_err)[:180]}", username)
        except Exception:
            pass
    finally:
        if lock_a is not None:
            release_lock(lock_a)


def manual_close_trade_db(username, trade_index, close_price_override=None):
    """User 'Close Manually' button dabaye to ye call hota hai — PnL calculate + history shift."""
    lock_m = acquire_lock(timeout=7.0)
    if lock_m is None:
        return False, "Lock busy"
    try:
        fresh = load_db()
        us = fresh["settings"].get(username)
        if us is None:
            return False, "User missing"
        actives = us.get("active_trades", []) or []
        if trade_index < 0 or trade_index >= len(actives):
            return False, "Invalid index"
        trade = actives.pop(trade_index)
        sym = trade.get("Symbol", "")
        entry_str = str(trade.get("Entry", "0")).replace(",", "")
        try:
            entry_price = float(entry_str)
        except Exception:
            entry_price = 0.0
        amt_str = str(trade.get("Amount", "$0")).replace("$", "").replace(",", "").strip()
        try:
            amt_usdt = float(amt_str)
        except Exception:
            amt_usdt = 0.0
        if close_price_override is None or close_price_override <= 0:
            live_p = 0.0
            ex_cfg = us.get("exchange") or {}
            if ex_cfg.get("connected") and ex_cfg.get("key"):
                try:
                    ex_obj = create_exchange(ex_cfg)
                    live_p = _get_live_price(ex_obj, sym, 0.0)
                except Exception:
                    live_p = 0.0
            close_price_override = live_p if live_p > 0 else entry_price
        pnl_pct = ((close_price_override - entry_price) / entry_price) * 100 if entry_price > 0 else 0.0
        pnl_val = (pnl_pct / 100.0) * amt_usdt if amt_usdt > 0 else 0.0
        status_txt = "PROFIT" if pnl_val >= 0 else "LOSS"
        history_entry = {
            "date": str(date.today()),
            "time": datetime.now().strftime("%I:%M:%S %p"),
            "Symbol": sym,
            "Market": trade.get("Market", "Spot"),
            "Entry": f"{entry_price:,.6f}",
            "Close": f"{close_price_override:,.6f}",
            "Amount": f"${amt_usdt:,.2f}",
            "PnL%": f"{pnl_pct:+.2f}%",
            "pnl_val": pnl_val,
            "status": status_txt,
            "Reason": "Manually Closed",
            "Rules": trade.get("Rules", ""),
        }
        us.setdefault("trade_history", []).insert(0, history_entry)
        us["active_trades"] = actives
        save_db(fresh)
        add_log(f"✅ {sym} MANUALLY closed — PnL ${pnl_val:+,.2f} ({pnl_pct:+.2f}%). Moved to History.", username)
        return True, f"{status_txt} ${pnl_val:+,.2f}"
    except Exception as e:
        return False, str(e)
    finally:
        if lock_m is not None:
            release_lock(lock_m)


# ==========================================
# STRATEGY / INDICATOR ENGINE  (signal + confirmation candle)
# ==========================================
def get_ohlcv_df(ex, symbol, timeframe, limit=250):
    try:
        ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if not ohlcv or len(ohlcv) < 30:
            return None
        return pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
    except Exception:
        return None

def is_green(row):
    return float(row['close']) > float(row['open'])

def calc_rsi(close_series, period=14):
    delta = close_series.diff()
    gain = delta.clip(lower=0); loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean(); avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def parse_ma_periods(raw):
    """
    User jo bhi likhe uska separator dekh kar AND/OR decide karta hai:
      - Comma (,)  -> AND  -> "200,44,25" = teeno MA par condition honi chahiye
      - Slash (/)  -> OR   -> "200/44/25" = in me se KISI EK MA par bhi mil jaye to trade
    """
    raw = (raw or "").strip()
    if not raw:
        return [], "AND"
    if "/" in raw:
        parts = raw.split("/")
        logic = "OR"
    else:
        parts = raw.split(",")
        logic = "AND"
    periods = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        try:
            periods.append(int(p))
        except Exception:
            pass
    return periods, logic

def check_ma_condition(df, periods, logic="AND"):
    """
    2 REAL HUMAN MA patterns (per-period check, then AND/OR across multiple MAs):
      Pattern A (BOUNCE / SUPPORT on MA):
         Price thoda niche ho MA se → signal candle ki WICK/BODY MA ko TOUCH kare ya
         thoda niche chali gayi ho (wick) par CLOSE wapas MA ke qareeb/upar aa jaye
         (rejection/reclaim) → Confirmation candle GREEN ho + signal candle se Upar close.
      Pattern B (BREAKOUT / Resistance Break above MA):
         Pichhli 3-5 candles ke CLOSE MA se NICHE the → Signal candle ko CLOSE ho MA
         ke Upar (properly closes above MA = resistance break) → Confirmation GREEN ho
         + Signal candle ke close se bhi upar close kare (follow-through).
    Multiple MAs diye ho to:
      logic="AND" → HAR MA par in dono me se koi ek pattern milna chahiye
      logic="OR"  → KISI BHI EK MA par koi ek pattern match kaafi hai
    """
    if not periods:
        return False
    if len(df) < max(periods) + 10:
        return False
    sig = df.iloc[-2]; conf = df.iloc[-1]
    sig_open, sig_high, sig_low, sig_close = [float(sig[x]) for x in ['open','high','low','close']]
    conf_open, conf_high, conf_low, conf_close = [float(conf[x]) for x in ['open','high','low','close']]

    if conf_close <= conf_open:
        return False
    if conf_close <= sig_close:
        return False

    per_ma_match = []
    for p in periods:
        ma_series = df['close'].rolling(int(p)).mean()
        ma_sig = float(ma_series.iloc[-2]) if not pd.isna(ma_series.iloc[-2]) else None
        ma_conf = float(ma_series.iloc[-1]) if not pd.isna(ma_series.iloc[-1]) else None
        if ma_sig is None or ma_conf is None:
            per_ma_match.append(False)
            continue

        pat_ok = False
        touched_by_range = sig_low <= ma_sig <= sig_high
        reclaim_close = (sig_low < ma_sig) and (sig_close >= ma_sig * 0.9985)
        pattern_a = (touched_by_range or reclaim_close) and (sig_close >= ma_sig * 0.999)
        pattern_a = pattern_a and (conf_close > ma_conf * 0.999)

        was_below_ma = True
        check_n = min(5, len(df) - 2)
        for i in range(1, check_n + 1):
            idx = -(i + 2)
            c_val = float(df['close'].iloc[idx])
            m_val = float(ma_series.iloc[idx]) if not pd.isna(ma_series.iloc[idx]) else None
            if m_val is None or c_val >= m_val:
                was_below_ma = False
                break
        breakout_signal = (sig_close > ma_sig) and (sig_open < ma_sig or sig_low < ma_sig)
        pattern_b = was_below_ma and breakout_signal and (conf_close > max(sig_close, ma_conf))

        pat_ok = pattern_a or pattern_b
        per_ma_match.append(pat_ok)

    if logic == "OR":
        return any(per_ma_match)
    return all(per_ma_match)

def check_rsi_condition(df, rsi_min, rsi_max, period=14):
    if len(df) < period + 3: return False
    rsi = calc_rsi(df['close'], period)
    rsi_sig = rsi.iloc[-2]; rsi_conf = rsi.iloc[-1]
    if pd.isna(rsi_sig) or pd.isna(rsi_conf): return False
    conf = df.iloc[-1]
    in_range = rsi_min <= float(rsi_sig) <= rsi_max
    momentum_up = float(rsi_conf) >= float(rsi_sig)
    return in_range and momentum_up and is_green(conf)

def check_support_condition(df, lookback, tolerance_pct):
    """
    2 REAL HUMAN patterns for zones:
      PATTERN 1 (SUPPORT ZONE BOUNCE):
         Lookback me last 'n' SWING LOWs (local minima) ka zone — jahan 2+ baar price
         bounce kiya ho. Signal candle us zone me aaye (touch/qareeb), phir confirmation
         candle green bounce de + close upar jaye.
      PATTERN 2 (RESISTANCE ZONE BREAKOUT):
         Lookback me last 'n' SWING HIGHs (local maxima) = resistance zone.
         Pichhli 3+ candles zone se niche thi → signal candle CLOSES ABOVE zone →
         confirmation candle green + bhi upar follow kare (proper breakout).
    Dono me se koi bhi match kare to return True.
    """
    recent = df.tail(int(lookback)).reset_index(drop=True)
    if len(recent) < 10: return False

    # --- SUPPORT ZONE: swing lows (local minima) ---
    swing_lows = []
    lows = recent['low'].astype(float).values
    for i in range(2, len(lows) - 2):
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            swing_lows.append(lows[i])
    if len(swing_lows) < 2:
        swing_lows = list(recent['low'].astype(float).nsmallest(3).values)
    sup_zone_low  = min(swing_lows) * (1 - tolerance_pct/100 * 0.2)
    sup_zone_high = max(swing_lows) * (1 + tolerance_pct/100)

    # --- RESISTANCE ZONE: swing highs (local maxima) ---
    swing_highs = []
    highs = recent['high'].astype(float).values
    for i in range(2, len(highs) - 2):
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            swing_highs.append(highs[i])
    if len(swing_highs) < 2:
        swing_highs = list(recent['high'].astype(float).nlargest(3).values)
    res_zone_low  = min(swing_highs) * (1 - tolerance_pct/100)
    res_zone_high = max(swing_highs) * (1 + tolerance_pct/100 * 0.2)

    sig = df.iloc[-2]; conf = df.iloc[-1]
    sig_low_f   = float(sig['low']);   sig_close_f = float(sig['close'])
    conf_close_f = float(conf['close']); conf_green = is_green(conf)

    # Pattern 1: Support zone touch → green bounce
    pattern_1 = False
    touch_sup = (sup_zone_low <= sig_low_f <= sup_zone_high) or (sup_zone_low <= sig_close_f <= sup_zone_high)
    if touch_sup and conf_green and conf_close_f > sig_close_f:
        pattern_1 = True

    # Pattern 2: Resistance zone breakout
    pattern_2 = False
    n_check = min(5, len(df) - 2)
    was_below_res = True
    for i in range(1, n_check + 1):
        c_v = float(df['close'].iloc[-(i + 2)])
        if c_v >= res_zone_low:
            was_below_res = False
            break
    broke_above = sig_close_f > res_zone_high
    if was_below_res and broke_above and conf_green and conf_close_f > max(sig_close_f, res_zone_high):
        pattern_2 = True

    return pattern_1 or pattern_2

def check_order_block_condition(df, lookback, tolerance_pct=1.0):
    """
    Bullish Order Block: ek strong impulse (bade body + averagese zyada volume wali)
    green candle dhoondo. Uske pichle 1-2 candles ka combined high/low hi asli "zone"
    hai (real trader bhi sirf ek candle nahi, base banane wali 1-2 candles dekhta hai).
    Price wapas us zone me aaye (tap) aur confirmation candle green reaction de.
    """
    recent = df.tail(int(lookback)).reset_index(drop=True)
    if len(recent) < 25: return False
    body = (recent['close'] - recent['open']).abs()
    avg_body = body.rolling(20).mean()
    avg_vol = recent['volume'].rolling(20).mean()
    ob_zone = None
    for i in range(20, len(recent)):
        is_bullish = recent['close'].iloc[i] > recent['open'].iloc[i]
        is_impulse = (not pd.isna(avg_body.iloc[i])) and body.iloc[i] > 1.8 * avg_body.iloc[i]
        vol_ok = True
        if not pd.isna(avg_vol.iloc[i]):
            vol_ok = float(recent['volume'].iloc[i]) >= float(avg_vol.iloc[i])
        if is_bullish and is_impulse and vol_ok and i > 0:
            prev1 = recent.iloc[i - 1]
            prev2 = recent.iloc[i - 2] if i >= 2 else prev1
            base_is_down = (prev1['close'] < prev1['open']) or (prev2['close'] < prev2['open'])
            if base_is_down:
                zone_low = min(float(prev1['low']), float(prev2['low']))
                zone_high = max(float(prev1['high']), float(prev2['high']))
                ob_zone = (zone_low, zone_high)
    if ob_zone is None: return False
    zone_low, zone_high = ob_zone
    zone_high_padded = zone_high * (1 + tolerance_pct / 100)
    sig = df.iloc[-2]; conf = df.iloc[-1]
    tapped = (zone_low <= float(sig['low']) <= zone_high_padded) or (zone_low <= float(sig['close']) <= zone_high_padded)
    reaction = is_green(conf) and float(conf['close']) > float(sig['close'])
    return tapped and reaction

def check_volume_condition(ex, symbol, min_usdt):
    try:
        ticker = ex.fetch_ticker(symbol)
        return float(ticker.get('quoteVolume') or 0) >= float(min_usdt)
    except Exception:
        return False

def check_trendline_condition(df, lookback, touches_required, tolerance_pct=1.5):
    recent = df.tail(int(lookback)).reset_index(drop=True)
    if len(recent) < 20: return False
    lows_idx = []
    for i in range(2, len(recent) - 2):
        low = recent['low'].iloc[i]
        if (low < recent['low'].iloc[i - 1] and low < recent['low'].iloc[i - 2] and
                low < recent['low'].iloc[i + 1] and low < recent['low'].iloc[i + 2]):
            lows_idx.append(i)
    if len(lows_idx) < touches_required: return False
    xs = np.array(lows_idx[-int(touches_required):])
    ys = recent['low'].iloc[xs].values
    slope, intercept = np.polyfit(xs, ys, 1)
    if slope <= 0: return False
    sig_pos = len(recent) - 2
    trend_val = slope * sig_pos + intercept
    if trend_val <= 0: return False
    sig = df.iloc[-2]; conf = df.iloc[-1]
    near_line = abs(float(sig['low']) - trend_val) / trend_val * 100 <= tolerance_pct
    bounce = is_green(conf) and float(conf['close']) > float(sig['close'])
    return near_line and bounce

def evaluate_manual_strategy(ex, symbol, cfg):
    """
    Ek ya zyada timeframes diye ja sakte hain (OR logic: kisi bhi EK timeframe par
    saari enabled conditions match ho jayein to trade/signal ban jata hai — doosre
    timeframes check karne ki zaroorat nahi). Ek hi timeframe diya ho to wahi jaisa
    pehle hota tha waisa hi kaam karta hai.
    """
    timeframes = cfg.get("timeframes") or [cfg.get("timeframe", "1h")]
    ma_periods = cfg.get("ma_periods", []) or [0]
    ma_logic = cfg.get("ma_logic", "AND")
    needed_limit = max(cfg.get("sr_lookback", 50), cfg.get("ob_lookback", 50),
                       cfg.get("trend_lookback", 100), max(ma_periods), 210) + 30

    for tf in timeframes:
        df = get_ohlcv_df(ex, symbol, tf, limit=int(needed_limit))
        if df is None:
            continue
        matched_rules = []; results = []
        if cfg.get("ma_enabled"):
            periods = cfg.get("ma_periods", [])
            if not periods:
                results.append(False)
            else:
                r = check_ma_condition(df, periods, ma_logic); results.append(r)
                if r:
                    sep = "/" if ma_logic == "OR" else ","
                    matched_rules.append(f"MA({sep.join(str(p) for p in periods)} {ma_logic})")
        if cfg.get("rsi_enabled"):
            r = check_rsi_condition(df, cfg.get("rsi_min", 30), cfg.get("rsi_max", 45)); results.append(r)
            if r: matched_rules.append(f"RSI({cfg.get('rsi_min')}-{cfg.get('rsi_max')})")
        if cfg.get("sr_enabled"):
            r = check_support_condition(df, cfg.get("sr_lookback", 50), cfg.get("sr_tolerance_pct", 1.0)); results.append(r)
            if r: matched_rules.append("Support Bounce")
        if cfg.get("ob_enabled"):
            r = check_order_block_condition(df, cfg.get("ob_lookback", 50)); results.append(r)
            if r: matched_rules.append("Order Block")
        if cfg.get("vol_enabled"):
            r = check_volume_condition(ex, symbol, cfg.get("vol_min_usdt", 500000)); results.append(r)
            if r: matched_rules.append("Volume Filter")
        if cfg.get("trend_enabled"):
            r = check_trendline_condition(df, cfg.get("trend_lookback", 100), cfg.get("trend_touches", 3)); results.append(r)
            if r: matched_rules.append("Trendline Bounce")
        if results and all(results):
            matched_rules.append(f"TF:{tf}")
            return True, matched_rules
    return False, []

# ==========================================
# AUTHENTICATION
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.4, 1])
    with col_b:
        st.markdown("<div class='crypto-card' style='text-align: center;'>", unsafe_allow_html=True)
        if logo_path and os.path.exists(logo_path): st.image(logo_path, width=150)
        st.markdown("<h1>⚡ Apex Trading</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #848e9c;'>Secure Multi-Exchange Algorithmic Platform</p><br>", unsafe_allow_html=True)
        if not _CRYPTO_OK:
            st.warning("⚠️ 'cryptography' install nahi hai — API keys encrypt nahi hongi. Terminal me: pip install cryptography")
        tab_l, tab_s = st.tabs(["🔐 Login", "📝 Sign Up"])
        with tab_l:
            l_user = st.text_input("Username", key="l_user")
            l_pass = st.text_input("Password", type="password", key="l_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Access Terminal", use_container_width=True, type="primary"):
                users = db["users"]
                if l_user in users and verify_password(l_pass, users[l_user].get("password", "")):
                    # legacy plain password -> hash me upgrade
                    if not str(users[l_user].get("password", "")).startswith("pbkdf2$"):
                        users[l_user]["password"] = hash_password(l_pass)
                    st.session_state.logged_in = True
                    st.session_state.username = l_user
                    if l_user not in db["settings"]:
                        db["settings"][l_user] = _blank_user_settings()
                    save_db(db)
                    st.success("✅ Login successful!"); st.rerun()
                else:
                    st.error("❌ Invalid username or password.")
        with tab_s:
            s_user = st.text_input("Choose Username", key="s_user")
            s_pass = st.text_input("Choose Password", type="password", key="s_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account & Login", use_container_width=True):
                users = db["users"]
                if s_user in users:
                    st.warning("⚠️ Username already exists.")
                elif not s_user or not s_pass:
                    st.warning("⚠️ Fields cannot be blank.")
                else:
                    users[s_user] = {"password": hash_password(s_pass), "created": str(date.today())}
                    db["settings"][s_user] = _blank_user_settings()
                    save_db(db)
                    st.session_state.logged_in = True
                    st.session_state.username = s_user
                    st.success("✅ Account created!"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

curr_user = st.session_state.username
ACTIVE_USER = curr_user
user_settings = db["settings"].setdefault(curr_user, _blank_user_settings())
_backfill_user(user_settings)
get_runtime(user_settings)
save_db(db)

# ==========================================
# SIDEBAR
# ==========================================
if logo_path and os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=140)
st.sidebar.markdown(f"""
    <div style='padding: 12px; background: #181a20; border-radius: 10px; border: 1px solid #2b313a; margin-top: 10px; margin-bottom: 15px;'>
        <div style='color: #848e9c; font-size: 11px;'>APEX TRADER</div>
        <div style='color: #fcd535; font-size: 16px; font-weight: bold;'>👤 {curr_user}</div>
    </div>
""", unsafe_allow_html=True)
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    # bot_active DB me hai, session se independent — logout karne se bot NAHI rukta
    st.rerun()
st.sidebar.markdown("---")
st.sidebar.markdown("<div class='apex-side-caption'>Navigation</div>", unsafe_allow_html=True)
config_menu = st.sidebar.radio(
    "Configs",
    ["📊 Dashboard", "🔌 Exchange Integration", "⚙️ Strategy Studio", "📦 Limitation & Campaign"],
    label_visibility="collapsed"
)

# ==========================================
# 1. EXCHANGE INTEGRATION
# ==========================================
if config_menu == "🔌 Exchange Integration":
    st.title("🔌 Exchange API Integration")
    st.markdown("---")
    if _CRYPTO_OK:
        st.markdown("<div class='crypto-card' style='border-left:4px solid #0ecb81;'>🔐 API key aur secret database me <b>encrypted</b> save hote hain (plain nahi).</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='crypto-card' style='border-left:4px solid #f6465d;'>⚠️ <b>cryptography</b> install nahi — keys abhi plain save hongi. <code>pip install cryptography</code> chala kar dobara connect karo.</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.3, 1], gap="large")
    with col1:
        st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
        ex_list = EXCHANGE_LIST  # Binance, Bybit, OKX, KuCoin
        cur_ex = user_settings["exchange"].get("name", "Binance")
        ex_choice = st.selectbox("Select Crypto Exchange", ex_list, index=ex_list.index(cur_ex) if cur_ex in ex_list else 0)
        market_type = st.radio("Market Architecture", ["Spot", "Futures (Derivatives)"], index=0 if user_settings["exchange"].get("market") == "Spot" else 1, horizontal=True)
        if "Futures" in market_type:
            st.caption(f"🛡️ **Auto Safety:** Futures select karte hi bot <b>leverage={FUTURES_SAFE_LEVERAGE}x aur margin={FUTURES_MARGIN_MODE}</b> set kar dega — liquidation risk kam.", unsafe_allow_html=True)
        api_k = st.text_input("API Key", type="password", value=dec_secret(user_settings["exchange"].get("key", "")))
        secret_k = st.text_input("Secret Key", type="password", value=dec_secret(user_settings["exchange"].get("secret", "")))
        demo_chk = st.checkbox("Enable Sandbox / Testnet Mode", value=user_settings["exchange"].get("demo", True))
        st.caption("Tip: exchange par key banate waqt sirf **Spot trading** on karo, **Withdrawal OFF** rakho, aur ho sake to server IP whitelist karo.")
        if st.button("🔌 Connect & Verify API", type="primary", use_container_width=True):
            try:
                # Dynamic factory — Binance/Bybit/OKX/KuCoin sab me same code se connect ho jayega
                test_cfg = {"name": ex_choice, "market": market_type,
                            "key": enc_secret(api_k) if api_k else "",
                            "secret": enc_secret(secret_k) if secret_k else "",
                            "demo": demo_chk}
                # connect-time check ke liye actual decrypted values hi pass karte hain (dec_secret already works)
                test_cfg_plain = {"name": ex_choice, "market": market_type,
                                  "key": api_k, "secret": secret_k, "demo": demo_chk}
                ex = create_exchange(test_cfg_plain)
                # Pehle load_markets phir balance (ccxt me kai exchanges ko is order me zaroori hota hai)
                ex.load_markets()
                ex.fetch_balance()
                user_settings["exchange"] = {"name": ex_choice, "market": market_type,
                                             "key": enc_secret(api_k), "secret": enc_secret(secret_k),
                                             "demo": demo_chk, "connected": True}
                save_db(db)
                st.success(f"✨ Successfully connected to {ex_choice} ({market_type})! Keys {'encrypted' if _CRYPTO_OK else 'saved'}.")
            except Exception as e:
                user_settings["exchange"]["connected"] = False
                save_db(db)
                st.error(f"❌ Connection failed: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 2. STRATEGY STUDIO
# ==========================================
elif config_menu == "⚙️ Strategy Studio":
    st.title("⚙️ Algorithmic Strategy Studio")
    st.markdown("---")
    st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
    exec_modes = ["Automated Trading (Bot takes trades & sets TP/SL automatically)",
                  "Signal-Only Mode (Bot sends signals & email alerts only)"]
    cur_exec = user_settings["strategy"].get("exec_mode", exec_modes[0])
    exec_choice = st.radio("Choose how the bot should operate:", exec_modes, index=exec_modes.index(cur_exec) if cur_exec in exec_modes else 0)
    user_settings["strategy"]["exec_mode"] = exec_choice
    st.markdown("</div>", unsafe_allow_html=True)

    mode_tab1, mode_tab2 = st.tabs(["🛠️ Manual Rule Builder", "🤖 AI Prompt (Auto)"])
    with mode_tab1:
        st.caption("Sirf jo checkbox tick karoge, bot SIRF wahi condition check karega (AND logic). "
                   "Har indicator signal + confirmation candle dekh kar trade karta hai. Timeframe global hai.")
        manual_cfg = user_settings["strategy"]["manual"]
        st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
        st.subheader("⏱️ Timeframe (Global)")
        tf_options = ["15m", "1h", "4h", "1d", "1w"]

        # Current defaults: purana multi-TF wala setting ho to usi hisab se checkbox state set karo
        stored_tfs = manual_cfg.get("timeframes") or ([manual_cfg["timeframe"]] if manual_cfg.get("timeframe") else ["1h"])
        stored_tfs = [t for t in stored_tfs if t in tf_options] or ["1h"]
        stored_single = manual_cfg.get("timeframe") if manual_cfg.get("timeframe") in tf_options else (stored_tfs[0] if stored_tfs else "1h")
        multi_tf_default = (len(stored_tfs) > 1) or bool(manual_cfg.get("multi_tf_enabled", False))

        multi_on = st.checkbox("Enable Multi-Timeframe Scan (OR logic: kisi bhi TF par match ho jaye to trade/signal)", value=multi_tf_default)
        manual_cfg["multi_tf_enabled"] = bool(multi_on)

        if not multi_on:
            # ============ DEFAULT: SINGLE SELECT DROPDOWN (jaise user ki reference image me) ============
            cur_single = stored_single if stored_single in tf_options else "1h"
            selected_single = st.selectbox("Candle Timeframe", tf_options, index=tf_options.index(cur_single))
            manual_cfg["timeframe"] = selected_single
            manual_cfg["timeframes"] = [selected_single]
            st.caption("Rule: Saari indicators ishi timeframe ke candles par check honge. Multi TF chahiye to upar ka checkbox tick karo.")
        else:
            # ============ OPTIONAL: MULTI-SELECT (OR logic) ============
            default_multi = stored_tfs if all(t in tf_options for t in stored_tfs) else ["1h"]
            picked_multi = st.multiselect("Candle Timeframes (ek ya zyada select karo)", tf_options, default=default_multi)
            if not picked_multi:
                picked_multi = [stored_single] if stored_single in tf_options else ["1h"]
            manual_cfg["timeframe"] = picked_multi[0]  # backward compat
            manual_cfg["timeframes"] = picked_multi
            st.caption("1 TF select karo to single jaisa hi kaam. 2+ select karo to OR logic — jis bhi TF par saari conditions match ho, wahi se trade.")
        st.markdown("</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
            manual_cfg["ma_enabled"] = st.checkbox("📈 Enable Moving Average (MA) Filter", value=manual_cfg.get("ma_enabled", False))
            _cur_ma_periods = manual_cfg.get("ma_periods", [])
            _cur_ma_logic = manual_cfg.get("ma_logic", "AND")
            _cur_ma_sep = "/" if _cur_ma_logic == "OR" else ","
            ma_str = st.text_input(
                "MA Periods —  ,  se AND  |  /  se OR",
                value=_cur_ma_sep.join(str(p) for p in _cur_ma_periods),
                placeholder="AND (sabhi MA par): 200,44,25   |   OR (kisi bhi ek MA par): 200/44/25",
                disabled=not manual_cfg["ma_enabled"])
            manual_cfg["ma_periods"], manual_cfg["ma_logic"] = parse_ma_periods(ma_str)
            if manual_cfg.get("ma_enabled") and manual_cfg["ma_periods"]:
                if manual_cfg["ma_logic"] == "OR":
                    st.caption(f"Mode: **OR** — in me se KISI BHI EK MA ({', '.join(map(str, manual_cfg['ma_periods']))}) par pattern mile to trade.")
                else:
                    st.caption(f"Mode: **AND** — SABHI MA ({', '.join(map(str, manual_cfg['ma_periods']))}) par pattern hona chahiye.")
            st.caption("Rule: signal candle MA ko touch/react kare (bounce/reclaim), phir confirmation candle green + upar close kare.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
            manual_cfg["rsi_enabled"] = st.checkbox("📊 Enable RSI Range Filter", value=manual_cfg.get("rsi_enabled", False))
            rc1, rc2 = st.columns(2)
            manual_cfg["rsi_min"] = rc1.number_input("RSI Min", 0, 100, value=int(manual_cfg.get("rsi_min", 30)), disabled=not manual_cfg["rsi_enabled"])
            manual_cfg["rsi_max"] = rc2.number_input("RSI Max", 0, 100, value=int(manual_cfg.get("rsi_max", 45)), disabled=not manual_cfg["rsi_enabled"])
            st.caption("Rule: RSI range me + confirmation candle green (momentum up).")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
            manual_cfg["sr_enabled"] = st.checkbox("🧱 Enable Support Bounce Filter", value=manual_cfg.get("sr_enabled", False))
            manual_cfg["sr_lookback"] = st.number_input("Support Lookback Candles", 10, 500, value=int(manual_cfg.get("sr_lookback", 50)), disabled=not manual_cfg["sr_enabled"])
            manual_cfg["sr_tolerance_pct"] = st.number_input("Max Distance From Support (%)", 0.1, 10.0, value=float(manual_cfg.get("sr_tolerance_pct", 1.0)), disabled=not manual_cfg["sr_enabled"])
            st.caption("Rule: price support ZONE (3 lowest lows ka average) ke paas aaye + green bounce candle confirm kare.")
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
            manual_cfg["ob_enabled"] = st.checkbox("🟩 Enable Order Block (Bullish) Filter", value=manual_cfg.get("ob_enabled", False))
            manual_cfg["ob_lookback"] = st.number_input("Order Block Lookback Candles", 20, 500, value=int(manual_cfg.get("ob_lookback", 50)), disabled=not manual_cfg["ob_enabled"])
            st.caption("Rule: volume-confirmed impulse + pichli 1-2 candles ka zone touch + green reaction candle confirm kare.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
            manual_cfg["vol_enabled"] = st.checkbox("💧 Enable Volume Filter", value=manual_cfg.get("vol_enabled", False))
            manual_cfg["vol_min_usdt"] = st.number_input("Minimum 24h Volume (USDT)", 0, 1000000000, value=int(manual_cfg.get("vol_min_usdt", 500000)), disabled=not manual_cfg["vol_enabled"])
            st.caption("Rule: 24h volume kam se kam itna ho (confirmation candle nahi lagti).")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
            manual_cfg["trend_enabled"] = st.checkbox("📐 Enable Trendline Bounce Filter", value=manual_cfg.get("trend_enabled", False))
            manual_cfg["trend_lookback"] = st.number_input("Trendline Lookback Candles", 20, 500, value=int(manual_cfg.get("trend_lookback", 100)), disabled=not manual_cfg["trend_enabled"])
            manual_cfg["trend_touches"] = st.number_input("Minimum Touches", 2, 10, value=int(manual_cfg.get("trend_touches", 3)), disabled=not manual_cfg["trend_enabled"])
            st.caption("Rule: rising trendline touch + green bounce candle confirm kare.")
            st.markdown("</div>", unsafe_allow_html=True)

        active_rules = []
        if manual_cfg.get("ma_enabled"): active_rules.append("MA")
        if manual_cfg.get("rsi_enabled"): active_rules.append("RSI")
        if manual_cfg.get("sr_enabled"): active_rules.append("Support")
        if manual_cfg.get("ob_enabled"): active_rules.append("Order Block")
        if manual_cfg.get("vol_enabled"): active_rules.append("Volume")
        if manual_cfg.get("trend_enabled"): active_rules.append("Trendline")

        st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
        st.write("**Active Rules (AND logic):**")
        if active_rules:
            st.markdown("".join([f"<span class='rule-tag'>{r}</span>" for r in active_rules]), unsafe_allow_html=True)
            if manual_cfg.get("ma_enabled") and not manual_cfg.get("ma_periods"):
                st.warning("⚠️ MA on hai lekin koi number nahi diya — MA field me kam se kam ek number likho (jaise 200).")
        else:
            st.warning("⚠️ Koi rule enable nahi hai — is state mein bot koi trade nahi lega.")
        st.markdown("</div>", unsafe_allow_html=True)

        # ---- Coin Universe / Monitoring-Tag filter ----
        st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
        st.subheader("🌐 Coin Filters (scan universe)")
        flt = user_settings.setdefault("filters", dict(DEFAULT_FILTERS))
        flt["universe_min_volume"] = st.number_input(
            "Scan sirf itne 24h Volume (USDT) se upar wale coins par",
            0, 1000000000, value=int(flt.get("universe_min_volume", 1000000)))
        exclude_str = st.text_input(
            "Exclude coins (comma separated) — Monitoring-Tag / risky coins yahan likho",
            value=",".join(flt.get("exclude", [])),
            placeholder="e.g. QKC, XYZ")
        flt["exclude"] = [x.strip().upper() for x in exclude_str.split(",") if x.strip()]
        st.caption("Note: Binance ka 'Monitoring Tag' API se seedha nahi milta, is liye aise coins yahan likh kar block karo. "
                   "Stablecoins/leveraged/delisted pehle se auto-filtered hain.")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("💾 Save Manual Strategy", type="primary", use_container_width=True, key="save_manual"):
            user_settings["strategy"]["manual"] = manual_cfg
            user_settings["strategy"]["mode"] = "manual"
            save_db(db)
            st.success("✅ Manual strategy + filters saved. Bot ab isi ke hisab se scan karega.")

    with mode_tab2:
        st.caption("Free-text prompt (Note: abhi AI evaluation connect nahi — trades manual rule builder se lagti hain).")
        st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
        ai_p = st.text_area("Write your custom prompt:", value=user_settings["strategy"].get("ai_prompt", ""), height=160)
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("💾 Save & Use AI Prompt Mode", type="primary", use_container_width=True, key="save_ai"):
            user_settings["strategy"]["ai_prompt"] = ai_p
            user_settings["strategy"]["mode"] = "ai_prompt"
            save_db(db)
            st.success("✅ AI Prompt mode active.")

    st.markdown("---")
    st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
    st.subheader("🛡️ Risk Management (applies to both modes)")
    sl = st.number_input("Stop Loss Percentage (%)", 0.1, 20.0, value=user_settings["strategy"].get("sl_pct", 2.0))
    tp = st.number_input("Take Profit Percentage (%)", 0.1, 50.0, value=user_settings["strategy"].get("tp_pct", 4.5))
    user_settings["strategy"]["sl_pct"] = sl
    user_settings["strategy"]["tp_pct"] = tp
    if st.button("💾 Save Risk Settings", use_container_width=True):
        save_db(db); st.success("✅ Risk settings saved.")
    st.markdown("</div>", unsafe_allow_html=True)

    active_mode = user_settings["strategy"].get("mode", "manual")
    st.info(f"🔵 Currently active mode: **{'Manual Rule Builder' if active_mode == 'manual' else 'AI Prompt (Auto)'}**")

# ==========================================
# 3. LIMITATION & CAMPAIGN
# ==========================================
elif config_menu == "📦 Limitation & Campaign":
    st.markdown("<h2>📦 Limitation & Campaign</h2>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        c_days = st.number_input("Campaign Duration", 1, 365, value=user_settings["limits"].get("campaign_days", 1))
        d_limit = st.number_input("Daily Maximum Auto Trades", 1, 100, value=user_settings["limits"].get("daily_limit", 1))
        t_amt = st.number_input("Per Trade USDT", 5.0, value=user_settings["limits"].get("trade_amount", 100.0))
        user_settings["limits"]["campaign_days"] = c_days
        user_settings["limits"]["daily_limit"] = d_limit
        user_settings["limits"]["trade_amount"] = t_amt
        st.caption("Auto mode: bot exactly itni hi trades lega (2→2, 20→20), har coin sirf 1 baar, phir aaj ke liye ruk jayega. "
                   "Signal-Only mode: is limit se azaad — signal deta rahega.")
    with col2:
        email_cfg = user_settings.setdefault("email", {"enabled": True, "sender": "", "receiver": "", "brevo_api_key": ""})
        e_en = st.checkbox("Enable Email Notifications", value=email_cfg.get("enabled", True))
        e_sender = st.text_input("Sender Email (Brevo par verified hona chahiye)", value=email_cfg.get("sender", "")).strip()
        e_key_raw = st.text_input("Brevo API Key", type="password", value=dec_secret(email_cfg.get("brevo_api_key", "")))
        e_key = e_key_raw.strip()
        e_recv = st.text_input("Send Alerts To", value=email_cfg.get("receiver", "")).strip()
        email_cfg.update({"enabled": e_en, "sender": e_sender,
                          "brevo_api_key": enc_secret(e_key), "receiver": e_recv})

        st.caption("Tip: DigitalOcean jaise VPS par SMTP (Gmail) ports hamesha block hote hain, isliye email ab "
                   "**Brevo** (free, 300/din) ke zariye HTTPS se jati hai. brevo.com par free sign-up karo, apna "
                   "sender email verify karo, phir SMTP & API → API Keys se key banao. **Zaroori:** Brevo ke Security "
                   "settings me apne server ka IP (jo aapke droplet ka public IP hai) authorize/whitelist karna hoga, "
                   "warna API key kaam nahi karegi.")


        if st.button("📧 Send Test Email", use_container_width=True):
            with st.spinner("Test email bheja ja raha hai..."):
                test_ok = send_email_alert(
                    "✅ Apex Trading — Test Email",
                    "<html><body style='font-family:Arial;background:#0b0e11;color:#eaecef;padding:20px;'>"
                    "<h2 style='color:#fcd535;'>Test email successful!</h2>"
                    "<p>Agar aapko ye email mila hai, matlab SMTP settings bilkul sahi hain.</p>"
                    "</body></html>",
                    email_cfg
                )
            if test_ok:
                st.success("✅ Test email bhej diya gaya! Apna inbox (aur Spam folder) check karo.")
            else:
                st.error("❌ Test email fail hua. Exact error dekhne ke liye Dashboard → 📜 Bot Logs kholo — "
                         "wahan Gmail ka asli error message milega (jaise galat App Password, ya 2-Step Verification off).")

    if st.button("💾 Save Limits & Notifications", type="primary", use_container_width=True):
        save_db(db); st.success("✅ Saved successfully!")

# ==========================================
# 4. DASHBOARD
# ==========================================
else:
    rt = get_runtime(user_settings)
    save_db(db)
    st.markdown(f"""
        <div style='display: flex; flex-wrap: wrap; gap: 10px; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
            <div>
                <h1 style='margin: 0; font-size: 26px;'>⚡ Apex Trading Dashboard</h1>
                <p style='margin: 4px 0 0 0; color: #848e9c; font-size: 13px;'>Rule-Based Strategy Engine + optional AI Prompt mode.</p>
            </div>
            <div style='background: #181a20; border: 1px solid #2b313a; padding: 8px 16px; border-radius: 8px; text-align: right;'>
                <div style='color: #fcd535; font-weight: bold;'>👤 {curr_user}</div>
                <div style='color: #0ecb81; font-size: 12px;'>● Active Session</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    dash_tab = st.radio("Tabs", ["📊 Analytics", "🎯 Active Trades", "🔍 Signal Feed", "💰 History", "📜 Bot Logs"],
                        horizontal=True, label_visibility="collapsed")
    st.markdown("---")

    if dash_tab == "📊 Analytics":
        ex_status_cfg = user_settings.get("exchange", {})
        is_connected = bool(ex_status_cfg.get("connected")) and bool(ex_status_cfg.get("key"))
        if is_connected:
            st.markdown("<div class='crypto-card'>🟢 <b>Exchange Status:</b> Connected — Automated mode CAN place real orders.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='crypto-card'>🔴 <b>Exchange Status:</b> NOT connected (or API key missing). "
                        "Bot signals to banata rahega par tab tak real order NAHI karega jab tak <b>Exchange Integration</b> me connect na karo.</div>", unsafe_allow_html=True)

        st.markdown("<div class='crypto-card' style='border-left:4px solid #0ecb81;'>✅ <b>Bot ab background me chalta hai:</b> "
                    "Start karne ke baad browser tab band karo, phone lock karo, PC bhi band kar do — bot chalta rahega jab tak "
                    "aap khud <b>STOP BOT</b> na dabao. Kitne bhi tabs khule hon, sirf EK hi bot-thread chalta hai (double-trade ka purana masla khatam).</div>", unsafe_allow_html=True)

        history = user_settings["trade_history"]
        total_trades = len(history)
        successful_wins = len([h for h in history if "PROFIT" in h.get("status", "")])
        today_pnl = sum([float(h.get("pnl_val", 0)) for h in history if h.get("date") == str(date.today())])

        bot_is_active = bool(user_settings.get("bot_active", False))

        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        c_m1.metric("Total Trades Executed", total_trades)
        c_m2.metric("Successful Wins", successful_wins)
        c_m3.metric("Today's Net PnL", f"${today_pnl:+,.2f}")
        c_m4.metric("Bot Status", "🟢 Running (background)" if bot_is_active else "🔴 Stopped")

        _lim = int(user_settings["limits"].get("daily_limit", 1))
        # Display ko hamesha clamp karo — chahe kisi bhi wajah se number thoda idhar-udhar ho,
        # user ko kabhi limit se zyada "X/Y" ka number NAHI dikhna chahiye.
        _shown_trades = min(int(rt.get('trades_today', 0)), _lim)
        st.markdown(
            f"<div class='crypto-card'><b>Today's Auto Trades:</b> "
            f"<span style='color:#fcd535;'>{_shown_trades} / {_lim}</span> &nbsp; "
            f"({max(_lim - _shown_trades, 0)} remaining today) &nbsp;|&nbsp; "
            f"<b>Signals Today:</b> <span style='color:#0ecb81;'>{rt['signals_today']}</span></div>",
            unsafe_allow_html=True)

        active_mode = user_settings["strategy"].get("mode", "manual")
        st.markdown(f"<div class='crypto-card'><b>Strategy Mode:</b> "
                    f"<span style='color:#fcd535;'>{'🛠️ Manual Rule Builder' if active_mode=='manual' else '🤖 AI Prompt (Auto)'}</span></div>",
                    unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        b_c1, b_c2 = st.columns(2)
        with b_c1:
            if st.button("🚀 START BOT ENGINE", use_container_width=True, type="primary", disabled=bot_is_active):
                user_settings["bot_active"] = True
                save_db(db)
                ensure_all_bot_threads()
                add_log("Apex bot engine started — background thread me chalega, tab/phone band karne se nahi rukega.")
                st.rerun()
        with b_c2:
            if st.button("🛑 STOP BOT", use_container_width=True, disabled=not bot_is_active):
                user_settings["bot_active"] = False
                save_db(db)
                add_log("Apex bot stop request diya gaya — chalu cycle khatam hote hi (~15 sec) ruk jayega.")
                st.rerun()

    elif dash_tab == "🎯 Active Trades":
        top1, top2, top3 = st.columns([0.45, 0.3, 0.25])
        with top1:
            st.subheader("🎯 Active Positions")
        with top2:
            st.caption("TP/SL auto-check har bot cycle me hota hai. Ya neeche Refresh dabao.")
        with top3:
            need_ui_rerun_after = False
            if st.button("🔄 Refresh PnL", use_container_width=True, key="refresh_active_pnl"):
                monitor_close_active_trades(curr_user)
                need_ui_rerun_after = True
        if user_settings["active_trades"]:
            st.button("🗑️ Clear (UI Only — history me NAHI jayega)", key="clr_active",
                      on_click=lambda: (user_settings.__setitem__("active_trades", []), save_db(db)))
        active_list = user_settings["active_trades"]
        if active_list:
            cols_header = st.columns([0.18, 0.14, 0.12, 0.15, 0.15, 0.1, 0.16])
            h = cols_header[0].write("🪙 Symbol"); cols_header[1].write("Entry / Live")
            cols_header[2].write("Unrealized PnL"); cols_header[3].write("TP / SL"); cols_header[4].write("Allocated")
            cols_header[5].write("Rules"); cols_header[6].write("Action")
            st.markdown("---")
            for idx, trade in enumerate(list(active_list)):
                sym = trade.get("Symbol", "")
                entry_str = str(trade.get("Entry", "0")).replace(",", "")
                entry_f = 0.0
                try: entry_f = float(entry_str)
                except Exception: entry_f = 0.0
                live_str = str(trade.get("LivePrice", trade.get("Entry", "0"))).replace(",", "")
                live_f = 0.0
                try: live_f = float(live_str)
                except Exception: live_f = entry_f
                unreal_str = trade.get("Unrealized", "—")
                amt_str = str(trade.get("Amount", "$0")).replace("$", "").replace(",", "").strip()
                amt_f = 0.0
                try: amt_f = float(amt_str)
                except Exception: amt_f = 0.0
                if unreal_str == "—" and amt_f > 0 and entry_f > 0 and live_f > 0:
                    up = ((live_f - entry_f) / entry_f) * 100
                    uv = (up / 100.0) * amt_f
                    unreal_str = f"{uv:+,.2f} USD ({up:+.2f}%)"
                try:
                    up_col = unreal_str.split("USD")[0].strip()
                    if up_col.startswith("+"): up_color = "#0ecb81"
                    elif up_col.startswith("-"): up_color = "#f6465d"
                    else: up_color = "#eaecef"
                except Exception:
                    up_color = "#eaecef"
                r1, r2, r3, r4, r5, r6, r7 = st.columns([0.18, 0.14, 0.12, 0.15, 0.15, 0.1, 0.16])
                r1.markdown(f"<b style='color:#fcd535;'>{sym}</b><br><span style='color:#848e9c;font-size:11px;'>{trade.get('Market','Spot')}</span>", unsafe_allow_html=True)
                r2.markdown(f"E: <b style='color:#3b82f6;'>${entry_f:,.6f}</b><br>L: <b>${live_f:,.6f}</b>", unsafe_allow_html=True)
                r3.markdown(f"<b style='color:{up_color};'>{unreal_str}</b>", unsafe_allow_html=True)
                r4.markdown(f"TP: <b style='color:#0ecb81;'>${trade.get('TP','0')}</b><br>SL: <b style='color:#f6465d;'>${trade.get('SL','0')}</b>", unsafe_allow_html=True)
                r5.write(trade.get("Amount", "$0"))
                r6.write(str(trade.get("Rules", "—"))[:18])
                close_clicked = r7.button("✅ Close", key=f"close_manual_{idx}", use_container_width=True,
                                          help="Live price se close karke PnL ke saath History me shift karega")
                if close_clicked:
                    with st.spinner(f"Closing {sym}..."):
                        ok, msg = manual_close_trade_db(curr_user, idx)
                        if ok:
                            st.success(f"Closed — {msg}")
                        else:
                            st.error(f"Error: {msg}")
                    need_ui_rerun_after = True
                st.markdown("---")
            if need_ui_rerun_after:
                st.rerun()
        else:
            st.info("No active trades running right now.")

    elif dash_tab == "🔍 Signal Feed":
        top1, top2 = st.columns([0.7, 0.3])
        with top1:
            st.subheader("📡 Live Signals Feed")
        with top2:
            if user_settings["signals_feed"] and st.button("🗑️ Clear All", use_container_width=True, key="clr_signals"):
                user_settings["signals_feed"] = []
                save_db(db); st.rerun()

        if user_settings["signals_feed"]:
            for i, sig in enumerate(list(user_settings["signals_feed"])):
                epoch_time = sig.get("timestamp_epoch", time.time())
                diff_seconds = int(time.time() - epoch_time)
                if diff_seconds < 60: time_ago_str = "Just now"
                elif diff_seconds < 3600: time_ago_str = f"{diff_seconds // 60} mins ago"
                elif diff_seconds < 86400: time_ago_str = f"{diff_seconds // 3600} hrs ago"
                else: time_ago_str = "1 day ago"

                stype = sig.get("type", "Signal")
                badge = "badge-live" if stype == "Executed Trade" else "badge-signal"
                badge_txt = "✅ EXECUTED" if stype == "Executed Trade" else "📡 SIGNAL"
                rules_html = f"<br><span style='color:#848e9c;font-size:12px;'>Rules:</span> <b style='font-size:12px;'>{sig.get('rules')}</b>" if sig.get('rules') else ""

                cc1, cc2 = st.columns([0.9, 0.1])
                with cc1:
                    st.markdown(f"""
                    <div class='sig-card'>
                        <div style='display:flex; flex-wrap:wrap; gap:8px; justify-content:space-between; align-items:center;'>
                            <span class='sym-title'>{sig['symbol']}</span>
                            <span class='{badge}'>{badge_txt}</span>
                        </div>
                        <div class='kv-row' style='margin-top:10px;'>
                            <span class='kv'><span class='k'>Entry</span><span class='v' style='color:#3b82f6;'>{sig.get('entry',0):,.6f}</span></span>
                            <span class='kv'><span class='k'>Take Profit</span><span class='v' style='color:#0ecb81;'>{sig.get('tp',0):,.6f}</span></span>
                            <span class='kv'><span class='k'>Stop Loss</span><span class='v' style='color:#f6465d;'>{sig.get('sl',0):,.6f}</span></span>
                        </div>
                        {rules_html}
                        <div style='color:#848e9c; font-size:11px; margin-top:8px;'>🕒 {time_ago_str} ({sig.get('time','N/A')})</div>
                    </div>
                    """, unsafe_allow_html=True)
                with cc2:
                    if st.button("❌", key=f"del_sig_{sig.get('id', i)}", help="Is signal ko hatao"):
                        user_settings["signals_feed"].pop(i)
                        save_db(db); st.rerun()
        else:
            st.info("No active signals right now.")

    elif dash_tab == "💰 History":
        top1, top2 = st.columns([0.7, 0.3])
        with top1:
            st.subheader("💰 Trade History")
        with top2:
            if user_settings["trade_history"] and st.button("🗑️ Clear History", use_container_width=True, key="clr_hist"):
                user_settings["trade_history"] = []
                save_db(db); st.rerun()
        if user_settings["trade_history"]:
            st.dataframe(pd.DataFrame(user_settings["trade_history"]), use_container_width=True)
        else:
            st.info("No trade history available yet.")

    elif dash_tab == "📜 Bot Logs":
        st.subheader("📜 Bot Logs (most recent first)")
        st.caption("Yahan exact reason milega ke koi trade kyun skip hui, ya order kyun fail hua.")
        logs = user_settings.get("logs", [])
        if logs:
            if st.button("🗑️ Clear Logs"):
                user_settings["logs"] = []; save_db(db); st.rerun()
            for line in reversed(logs[-200:]):
                st.text(line)
        else:
            st.info("Koi log abhi tak nahi bana.")

