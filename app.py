










# import streamlit as st
# import ccxt
# import pandas as pd
# import numpy as np
# import time
# import os
# import json
# import hashlib
# import hmac
# import secrets
# import socket
# import smtplib
# import urllib.request
# import urllib.error
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from datetime import datetime, date

# # Optional strong encryption for API keys (pip install cryptography)
# try:
#     from cryptography.fernet import Fernet
#     _CRYPTO_OK = True
# except Exception:
#     _CRYPTO_OK = False

# # ==========================================
# # PAGE SETUP & STYLING
# # ==========================================
# favicon_path = "apex-favicon.png" if os.path.exists("apex-favicon.png") else "⚡"
# logo_path = "apex-logo.png" if os.path.exists("apex-logo.png") else None

# st.set_page_config(
#     page_title="Apex Trading - Pro Terminal",
#     page_icon=favicon_path if os.path.exists("apex-favicon.png") else "⚡",
#     layout="wide"
# )

# st.markdown("""
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

#     html, body, [class*="css"] {
#         font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
#     }

#     .stApp {
#         background:
#             radial-gradient(circle at 12% 0%, rgba(252,213,53,0.06), transparent 32%),
#             radial-gradient(circle at 88% 100%, rgba(14,203,129,0.05), transparent 38%),
#             #0b0e11;
#         color: #eaecef;
#     }

#     .block-container { padding-top: 1.6rem; padding-bottom: 3rem; }

#     @keyframes fadeInUp {
#         from { opacity: 0; transform: translateY(10px); }
#         to { opacity: 1; transform: translateY(0); }
#     }
#     @keyframes softPulse {
#         0% { box-shadow: 0 0 0 0 rgba(14,203,129,0.35); }
#         70% { box-shadow: 0 0 0 8px rgba(14,203,129,0); }
#         100% { box-shadow: 0 0 0 0 rgba(14,203,129,0); }
#     }

#     .crypto-card {
#         background: linear-gradient(150deg, #181a20 0%, #121418 100%);
#         border: 1px solid #2b313a;
#         border-radius: 14px;
#         padding: 20px;
#         margin-bottom: 15px;
#         box-shadow: 0 10px 26px rgba(0,0,0,0.28);
#         animation: fadeInUp 0.35s ease both;
#         transition: border-color 0.2s ease, transform 0.2s ease;
#     }
#     .crypto-card:hover { border-color: #3a4552; }

#     .badge-live {
#         background-color: rgba(14, 203, 129, 0.15);
#         color: #0ecb81;
#         padding: 4px 12px;
#         border-radius: 20px;
#         font-size: 12px;
#         font-weight: 700;
#         border: 1px solid #0ecb81;
#         animation: softPulse 2.4s ease-in-out infinite;
#     }
#     .badge-signal {
#         background-color: rgba(240, 185, 11, 0.15);
#         color: #fcd535;
#         padding: 4px 12px;
#         border-radius: 20px;
#         font-size: 12px;
#         font-weight: 700;
#         border: 1px solid #fcd535;
#     }
#     .rule-tag {
#         display:inline-block;
#         background:#0ecb8122;
#         border:1px solid #0ecb81;
#         color:#0ecb81;
#         padding:4px 12px;
#         border-radius:20px;
#         font-size:12px;
#         margin-right:6px;
#         margin-bottom:6px;
#         transition: background 0.15s ease;
#     }
#     .rule-tag:hover { background:#0ecb8140; }

#     .sig-card {
#         background: linear-gradient(180deg,#181a20 0%, #131519 100%);
#         border: 1px solid #2b313a;
#         border-left: 4px solid #fcd535;
#         border-radius: 14px;
#         padding: 16px 20px;
#         margin-bottom: 12px;
#         animation: fadeInUp 0.3s ease both;
#         transition: transform 0.15s ease, border-color 0.2s ease;
#     }
#     .sig-card:hover { transform: translateY(-2px); border-color: #3a4552; }

#     .trade-card {
#         background: linear-gradient(180deg,#181a20 0%, #131519 100%);
#         border: 1px solid #2b313a;
#         border-left: 4px solid #0ecb81;
#         border-radius: 14px;
#         padding: 16px 20px;
#         margin-bottom: 12px;
#         animation: fadeInUp 0.3s ease both;
#         transition: transform 0.15s ease, border-color 0.2s ease;
#     }
#     .trade-card:hover { transform: translateY(-2px); border-color: #3a4552; }

#     .kv { display:inline-block; margin-right:20px; }
#     .kv .k { color:#848e9c; font-size:11px; letter-spacing:.4px; display:block; margin-bottom:2px; }
#     .kv .v { font-size:15px; font-weight:700; }
#     .sym-title { color:#fcd535; font-size:19px; font-weight:800; margin:0; }

#     .stButton > button {
#         border-radius: 10px;
#         min-height: 42px;
#         font-weight: 700;
#         border: 1px solid #303943;
#         transition: all 0.15s ease;
#     }
#     .stButton > button:hover {
#         border-color: #52606e;
#         transform: translateY(-1px);
#         box-shadow: 0 6px 16px rgba(0,0,0,0.25);
#     }
#     .stButton > button:active { transform: translateY(0) scale(0.98); }

#     div[data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid #252c34; }
#     button[data-baseweb="tab"] {
#         background: #11161b;
#         border-radius: 9px 9px 0 0;
#         transition: background 0.15s ease;
#     }
#     button[data-baseweb="tab"][aria-selected="true"] { background: #1a2027; }

#     [data-testid="stDataFrame"] { border: 1px solid #2b313a; border-radius: 12px; overflow: hidden; }

#     section[data-testid="stSidebar"] {
#         background: linear-gradient(180deg, #0c1015 0%, #090c10 100%);
#         border-right: 1px solid #20262e;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # ==========================================
# # CONFIG / PATHS (env se override ho sakte hain — VPS par persistent disk ke liye useful)
# # ==========================================
# DB_FILE = os.environ.get("APEX_DB_FILE", "database.json")
# LOCK_FILE = os.environ.get("APEX_LOCK_FILE", "apex.lock")
# KEY_FILE = os.environ.get("APEX_KEY_FILE", "apex_secret.key")
# SECRET_ENV = "APEX_SECRET_KEY"       # live par ye env var set karo (sabse safe)
# MIN_ACTION_GAP_SEC = 10              # do actions ke beech gap (rapid-fire / multi-tab race rokne ke liye)
# STALE_LOCK_SEC = 25
# UNIVERSE_CACHE_TTL = 180             # seconds — market/tickers data itni der cache rehta hai (chhote VPS ka RAM/CPU bachane ke liye)

# # ==========================================
# # ENCRYPTION (API keys / secrets at rest)
# # ==========================================
# def _load_or_create_fernet():
#     if not _CRYPTO_OK:
#         return None
#     key = os.environ.get(SECRET_ENV)
#     if key:
#         try:
#             return Fernet(key.encode() if isinstance(key, str) else key)
#         except Exception:
#             pass
#     if os.path.exists(KEY_FILE):
#         try:
#             with open(KEY_FILE, "rb") as f:
#                 return Fernet(f.read().strip())
#         except Exception:
#             pass
#     k = Fernet.generate_key()
#     try:
#         with open(KEY_FILE, "wb") as f:
#             f.write(k)
#     except Exception:
#         pass
#     return Fernet(k)

# FERNET = _load_or_create_fernet()
# ENC_PREFIX = "enc::"

# def enc_secret(plain):
#     """Plain text ko encrypt karke store karo. Pehle se encrypted ho to waise hi rehne do."""
#     if not plain:
#         return ""
#     if not isinstance(plain, str):
#         plain = str(plain)
#     if plain.startswith(ENC_PREFIX):
#         return plain
#     if FERNET is None:
#         return plain  # cryptography install nahi — plain (UI me warning dikhega)
#     try:
#         return ENC_PREFIX + FERNET.encrypt(plain.encode()).decode()
#     except Exception:
#         return plain

# def dec_secret(stored):
#     """Encrypted value ko wapas plain me karo. Legacy plain value ho to waise hi de do."""
#     if not stored or not isinstance(stored, str):
#         return stored or ""
#     if not stored.startswith(ENC_PREFIX):
#         return stored  # legacy plain
#     if FERNET is None:
#         return ""
#     try:
#         return FERNET.decrypt(stored[len(ENC_PREFIX):].encode()).decode()
#     except Exception:
#         return ""

# # ==========================================
# # PASSWORD HASHING (login/signup)
# # ==========================================
# def hash_password(pw):
#     salt = secrets.token_hex(16)
#     h = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200000).hex()
#     return f"pbkdf2${salt}${h}"

# def verify_password(pw, stored):
#     if not stored:
#         return False
#     if isinstance(stored, str) and stored.startswith("pbkdf2$"):
#         try:
#             _, salt, h = stored.split("$", 2)
#             calc = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200000).hex()
#             return hmac.compare_digest(calc, h)
#         except Exception:
#             return False
#     # legacy plain password (purane accounts) — match ho to login ke baad hash me upgrade kar denge
#     return hmac.compare_digest(str(pw), str(stored))

# # ==========================================
# # DATABASE
# # ==========================================
# DEFAULT_MANUAL_STRATEGY = {
#     "timeframe": "1h",
#     "ma_enabled": False, "ma_periods": [],
#     "rsi_enabled": False, "rsi_min": 30, "rsi_max": 45,
#     "sr_enabled": False, "sr_lookback": 50, "sr_tolerance_pct": 1.0,
#     "ob_enabled": False, "ob_lookback": 50,
#     "vol_enabled": False, "vol_min_usdt": 500000,
#     "trend_enabled": False, "trend_lookback": 100, "trend_touches": 3,
# }

# DEFAULT_RUNTIME = {
#     "trade_date": "", "trades_today": 0, "signals_today": 0,
#     "traded_coins_today": [], "last_action_epoch": 0
# }

# DEFAULT_FILTERS = {
#     "universe_min_volume": 1000000,   # scan sirf itne 24h USDT volume+ wale coins par
#     "exclude": []                     # user-defined coins jo kabhi trade na hon (jaise QKC)
# }

# # Har user ka apna data yahan — live par ek user ka doosre se alag aur persistent
# USER_BUCKETS = ["active_trades", "trade_history", "signals_feed", "signal_history", "logs"]

# def _blank_user_settings():
#     return {
#         "exchange": {"name": "Binance", "market": "Spot", "key": "", "secret": "", "demo": True, "connected": False},
#         "strategy": {
#             "mode": "manual",
#             "exec_mode": "Automated Trading (Bot takes trades & sets TP/SL automatically)",
#             "ai_prompt": "",
#             "manual": dict(DEFAULT_MANUAL_STRATEGY),
#             "sl_pct": 2.0, "tp_pct": 4.5
#         },
#         "limits": {"campaign_days": 1, "daily_limit": 1, "trade_amount": 100.0},
#         "filters": dict(DEFAULT_FILTERS),
#         "runtime": dict(DEFAULT_RUNTIME),
#         "email": {"enabled": True, "sender": "", "receiver": "", "brevo_api_key": ""},
#         "active_trades": [], "trade_history": [], "signals_feed": [], "signal_history": [], "logs": []
#     }

# def _backfill_user(cfg):
#     strat = cfg.setdefault("strategy", {})
#     strat.setdefault("mode", "manual")
#     strat.setdefault("exec_mode", "Automated Trading (Bot takes trades & sets TP/SL automatically)")
#     strat.setdefault("manual", dict(DEFAULT_MANUAL_STRATEGY))
#     for k, v in DEFAULT_MANUAL_STRATEGY.items():
#         strat["manual"].setdefault(k, v)
#     strat.setdefault("ai_prompt", "")
#     strat.setdefault("sl_pct", 2.0)
#     strat.setdefault("tp_pct", 4.5)
#     cfg.setdefault("exchange", {"name": "Binance", "market": "Spot", "key": "", "secret": "", "demo": True, "connected": False})
#     cfg.setdefault("limits", {"campaign_days": 1, "daily_limit": 1, "trade_amount": 100.0})
#     flt = cfg.setdefault("filters", dict(DEFAULT_FILTERS))
#     for k, v in DEFAULT_FILTERS.items():
#         flt.setdefault(k, v)
#     rt = cfg.setdefault("runtime", dict(DEFAULT_RUNTIME))
#     for k, v in DEFAULT_RUNTIME.items():
#         rt.setdefault(k, v)
#     email_cfg = cfg.setdefault("email", {"enabled": True, "sender": "", "receiver": "", "brevo_api_key": ""})
#     email_cfg.setdefault("brevo_api_key", "")
#     email_cfg.setdefault("sender", "")
#     email_cfg.setdefault("receiver", "")
#     email_cfg.setdefault("enabled", True)
#     for b in USER_BUCKETS:
#         cfg.setdefault(b, [])

# def load_db():
#     if not os.path.exists(DB_FILE):
#         default_data = {"users": {}, "settings": {"admin": _blank_user_settings()}, "logs": []}
#         with open(DB_FILE, "w") as f:
#             json.dump(default_data, f, indent=4)

#     with open(DB_FILE, "r") as f:
#         try:
#             data = json.load(f)
#         except json.JSONDecodeError:
#             data = {"users": {}, "settings": {}, "logs": []}

#     data.setdefault("users", {})
#     data.setdefault("settings", {})
#     data.setdefault("logs", [])
#     if "admin" not in data["settings"]:
#         data["settings"]["admin"] = _blank_user_settings()
#     for uname, cfg in data["settings"].items():
#         _backfill_user(cfg)
#     return data

# def save_db(db):
#     """Atomic write — crash ya restart par file corrupt/khali na ho, data safe rahe."""
#     tmp = DB_FILE + ".tmp"
#     with open(tmp, "w") as f:
#         json.dump(db, f, indent=4)
#     os.replace(tmp, DB_FILE)

# def get_runtime(user_settings):
#     rt = user_settings.setdefault("runtime", dict(DEFAULT_RUNTIME))
#     for k, v in DEFAULT_RUNTIME.items():
#         rt.setdefault(k, v)
#     today_str = str(date.today())
#     if rt.get("trade_date") != today_str:
#         rt["trade_date"] = today_str
#         rt["trades_today"] = 0
#         rt["signals_today"] = 0
#         rt["traded_coins_today"] = []
#         rt["last_action_epoch"] = 0
#     return rt

# # ------------------------------------------------------------------
# # CROSS-TAB / CROSS-PROCESS FILE LOCK
# # ------------------------------------------------------------------
# def acquire_lock(timeout=8.0):
#     start = time.time()
#     while True:
#         try:
#             fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_RDWR)
#             try:
#                 os.write(fd, str(os.getpid()).encode())
#             except Exception:
#                 pass
#             return fd
#         except FileExistsError:
#             try:
#                 if time.time() - os.path.getmtime(LOCK_FILE) > STALE_LOCK_SEC:
#                     os.remove(LOCK_FILE)
#                     continue
#             except FileNotFoundError:
#                 continue
#             except Exception:
#                 pass
#             if time.time() - start > timeout:
#                 return None
#             time.sleep(0.2)

# def release_lock(fd):
#     if fd is None:
#         return
#     try:
#         os.close(fd)
#     except Exception:
#         pass
#     try:
#         os.remove(LOCK_FILE)
#     except Exception:
#         pass

# def try_reserve_slot(curr_user, chosen_coin, daily_lim, is_signal_only, min_gap=MIN_ACTION_GAP_SEC):
#     """Order se PEHLE slot reserve (lock ke andar): limit + duplicate-coin + cooldown check. Returns (ok, reason, fresh_db)."""
#     lock = acquire_lock()
#     if lock is None:
#         return False, "busy (dusra tab active)", load_db()
#     try:
#         fresh = load_db()
#         us = fresh["settings"].get(curr_user)
#         if us is None:
#             return False, "user missing", fresh
#         rtf = get_runtime(us)
#         now = time.time()
#         if now - float(rtf.get("last_action_epoch", 0)) < min_gap:
#             return False, "cooldown", fresh
#         if chosen_coin in rtf["traded_coins_today"]:
#             return False, "coin already used today", fresh
#         if not is_signal_only:
#             if rtf["trades_today"] >= daily_lim:
#                 return False, "limit reached", fresh
#             rtf["trades_today"] += 1
#         else:
#             rtf["signals_today"] += 1
#         rtf["traded_coins_today"].append(chosen_coin)
#         rtf["last_action_epoch"] = now
#         save_db(fresh)
#         return True, "reserved", fresh
#     finally:
#         release_lock(lock)

# db = load_db()
# ACTIVE_USER = None  # login ke baad set hota hai; add_log isi user ke logs me likhta hai

# if "logged_in" not in st.session_state: st.session_state.logged_in = False
# if "username" not in st.session_state: st.session_state.username = ""
# if "bot_running" not in st.session_state: st.session_state.bot_running = False

# def add_log(msg):
#     ts = datetime.now().strftime("%H:%M:%S")
#     line = f"[{ts}] {msg}"
#     try:
#         if ACTIVE_USER and ACTIVE_USER in db.get("settings", {}):
#             db["settings"][ACTIVE_USER].setdefault("logs", []).append(line)
#         else:
#             db.setdefault("logs", []).append(line)
#     except Exception:
#         db.setdefault("logs", []).append(line)
#     save_db(db)

# # ------------------------------------------------------------------
# # EMAIL — Brevo HTTPS API (SMTP ports 25/465/587 DigitalOcean par HAMESHA
# # block rehte hain — ye unki apni official policy hai, spam rokne ke liye,
# # aur kisi bhi SMTP provider ke liye lagu hoti hai, chahe wo Gmail ho ya
# # koi aur). Isliye email ab HTTPS (port 443) ke zariye Brevo ki API se
# # bheji jati hai — ye port kabhi block nahi hota (isi se bot Binance se
# # baat karta hai). Poore app me email sirf isi function se jaati hai, is
# # liye trade/signal ke waqt jahan pehle call hoti thi, wahi ab bhi hoti
# # hai — koi aur jagah kuch badalna nahi pada.
# # ------------------------------------------------------------------
# _orig_getaddrinfo = socket.getaddrinfo

# def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
#     return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

# BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

# def send_email_alert(subject, body_html, email_cfg):
#     if not email_cfg.get("enabled") or not email_cfg.get("sender") or not email_cfg.get("receiver"):
#         return False
#     api_key = dec_secret(email_cfg.get("brevo_api_key", ""))
#     api_key = api_key.strip() if api_key else ""
#     if not api_key:
#         add_log("Email Error: Brevo API key set nahi hai — Limitation & Campaign me daalo.")
#         return False
#     payload = json.dumps({
#         "sender": {"name": "Apex Trading Bot", "email": email_cfg["sender"]},
#         "to": [{"email": email_cfg["receiver"]}],
#         "subject": subject,
#         "htmlContent": body_html
#     }).encode("utf-8")
#     req = urllib.request.Request(
#         BREVO_API_URL, data=payload, method="POST",
#         headers={"api-key": api_key, "Content-Type": "application/json", "Accept": "application/json"}
#     )
#     socket.getaddrinfo = _ipv4_only_getaddrinfo  # is call ke liye IPv4 force (safety, HTTPS ke liye bhi)
#     try:
#         with urllib.request.urlopen(req, timeout=20) as resp:
#             if 200 <= resp.status < 300:
#                 return True
#             add_log(f"Email Error: Brevo HTTP {resp.status}")
#             return False
#     except urllib.error.HTTPError as e:
#         try:
#             err_body = e.read().decode("utf-8", errors="ignore")
#         except Exception:
#             err_body = ""
#         # Brevo error body me exact wajah hoti hai — jaise IP authorize nahi,
#         # ya sender email verify nahi, ya key galat. Bot Logs me poora dikhega.
#         add_log(f"Email Error: Brevo HTTP {e.code} - {err_body[:300]}")
#         return False
#     except Exception as e:
#         add_log(f"Email Error: {str(e)}")
#         return False
#     finally:
#         socket.getaddrinfo = _orig_getaddrinfo  # turant wapas normal


# # ------------------------------------------------------------------
# # COIN UNIVERSE FILTER
# # Sirf real, liquid, tradeable USDT spot coins. Stablecoins/fiat, leveraged tokens,
# # inactive/delisted pairs, aur user ke exclude-list wale coins (jaise Monitoring-Tag) hata dete hain.
# # ------------------------------------------------------------------
# STABLE_OR_FIAT = {
#     "USDT", "USDC", "BUSD", "FDUSD", "TUSD", "DAI", "USDP", "PAX", "PYUSD", "USDD",
#     "AEUR", "EUR", "EURI", "EURT", "GBP", "AUD", "BRL", "TRY", "RUB", "UAH", "NGN",
#     "IDRT", "ZAR", "ARS", "BIDR", "VAI", "UST", "USTC", "GUSD", "SUSD", "XUSD", "BVND"
# }

# def _is_leveraged_token(base):
#     b = (base or "").upper()
#     if "BULL" in b or "BEAR" in b:
#         return True
#     if len(b) >= 5 and (b.endswith("UP") or b.endswith("DOWN")):
#         return True
#     return False

# def build_symbol_universe(ex, tickers=None, min_volume=1_000_000, top_n=40, exclude_bases=None):
#     exclude_bases = {e.strip().upper() for e in (exclude_bases or []) if e.strip()}
#     markets = getattr(ex, "markets", {}) or {}
#     universe = []
#     for sym, m in markets.items():
#         try:
#             if not sym.endswith("/USDT"):
#                 continue
#             if m.get("active", True) is False:
#                 continue
#             if m.get("spot", True) is False:
#                 continue
#             base = (m.get("base") or sym.split("/")[0]).upper()
#             if base in STABLE_OR_FIAT or base in exclude_bases:
#                 continue
#             if _is_leveraged_token(base):
#                 continue
#             universe.append(sym)
#         except Exception:
#             continue

#     if tickers:
#         scored = []
#         for sym in universe:
#             t = tickers.get(sym) or {}
#             try:
#                 qv = float(t.get("quoteVolume") or 0)
#             except Exception:
#                 qv = 0.0
#             if qv >= min_volume:
#                 scored.append((sym, qv))
#         scored.sort(key=lambda x: x[1], reverse=True)
#         if scored:
#             return [s for s, _ in scored[:top_n]]
#     return universe[:top_n]

# # ==========================================
# # STRATEGY / INDICATOR ENGINE  (signal + confirmation candle)
# # ==========================================
# def get_ohlcv_df(ex, symbol, timeframe, limit=250):
#     try:
#         ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
#         if not ohlcv or len(ohlcv) < 30:
#             return None
#         return pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
#     except Exception:
#         return None

# def is_green(row):
#     return float(row['close']) > float(row['open'])

# def calc_rsi(close_series, period=14):
#     delta = close_series.diff()
#     gain = delta.clip(lower=0); loss = -delta.clip(upper=0)
#     avg_gain = gain.rolling(period).mean(); avg_loss = loss.rolling(period).mean()
#     rs = avg_gain / avg_loss.replace(0, np.nan)
#     return 100 - (100 / (1 + rs))

# def check_ma_condition(df, periods):
#     if not periods: return False
#     if len(df) < max(periods) + 3: return False
#     sig = df.iloc[-2]; conf = df.iloc[-1]
#     for p in periods:
#         ma = df['close'].rolling(int(p)).mean()
#         ma_sig = ma.iloc[-2]; ma_conf = ma.iloc[-1]
#         if pd.isna(ma_sig) or pd.isna(ma_conf): return False
#         if float(sig['close']) < float(ma_sig): return False
#         if float(conf['close']) < float(ma_conf): return False
#     return is_green(sig) and is_green(conf)

# def check_rsi_condition(df, rsi_min, rsi_max, period=14):
#     if len(df) < period + 3: return False
#     rsi = calc_rsi(df['close'], period)
#     rsi_sig = rsi.iloc[-2]; rsi_conf = rsi.iloc[-1]
#     if pd.isna(rsi_sig) or pd.isna(rsi_conf): return False
#     conf = df.iloc[-1]
#     in_range = rsi_min <= float(rsi_sig) <= rsi_max
#     momentum_up = float(rsi_conf) >= float(rsi_sig)
#     return in_range and momentum_up and is_green(conf)

# def check_support_condition(df, lookback, tolerance_pct):
#     recent = df.tail(int(lookback))
#     if len(recent) < 6: return False
#     support = float(recent['low'].min())
#     if support <= 0: return False
#     sig = df.iloc[-2]; conf = df.iloc[-1]
#     near_support = abs(float(sig['low']) - support) / support * 100 <= tolerance_pct
#     bounce = is_green(conf) and float(conf['close']) > float(sig['close'])
#     return near_support and bounce

# def check_order_block_condition(df, lookback, tolerance_pct=1.0):
#     recent = df.tail(int(lookback)).reset_index(drop=True)
#     if len(recent) < 25: return False
#     body = (recent['close'] - recent['open']).abs()
#     avg_body = body.rolling(20).mean()
#     ob_zone = None
#     for i in range(20, len(recent)):
#         is_bullish = recent['close'].iloc[i] > recent['open'].iloc[i]
#         is_impulse = (not pd.isna(avg_body.iloc[i])) and body.iloc[i] > 1.8 * avg_body.iloc[i]
#         if is_bullish and is_impulse and i > 0:
#             prev = recent.iloc[i - 1]
#             if prev['close'] < prev['open']:
#                 ob_zone = (float(prev['low']), float(prev['high']))
#     if ob_zone is None: return False
#     zone_low, zone_high = ob_zone
#     zone_high_padded = zone_high * (1 + tolerance_pct / 100)
#     sig = df.iloc[-2]; conf = df.iloc[-1]
#     tapped = (zone_low <= float(sig['low']) <= zone_high_padded) or (zone_low <= float(sig['close']) <= zone_high_padded)
#     reaction = is_green(conf) and float(conf['close']) > float(sig['close'])
#     return tapped and reaction

# def check_volume_condition(ex, symbol, min_usdt):
#     try:
#         ticker = ex.fetch_ticker(symbol)
#         return float(ticker.get('quoteVolume') or 0) >= float(min_usdt)
#     except Exception:
#         return False

# def check_trendline_condition(df, lookback, touches_required, tolerance_pct=1.5):
#     recent = df.tail(int(lookback)).reset_index(drop=True)
#     if len(recent) < 20: return False
#     lows_idx = []
#     for i in range(2, len(recent) - 2):
#         low = recent['low'].iloc[i]
#         if (low < recent['low'].iloc[i - 1] and low < recent['low'].iloc[i - 2] and
#                 low < recent['low'].iloc[i + 1] and low < recent['low'].iloc[i + 2]):
#             lows_idx.append(i)
#     if len(lows_idx) < touches_required: return False
#     xs = np.array(lows_idx[-int(touches_required):])
#     ys = recent['low'].iloc[xs].values
#     slope, intercept = np.polyfit(xs, ys, 1)
#     if slope <= 0: return False
#     sig_pos = len(recent) - 2
#     trend_val = slope * sig_pos + intercept
#     if trend_val <= 0: return False
#     sig = df.iloc[-2]; conf = df.iloc[-1]
#     near_line = abs(float(sig['low']) - trend_val) / trend_val * 100 <= tolerance_pct
#     bounce = is_green(conf) and float(conf['close']) > float(sig['close'])
#     return near_line and bounce

# def evaluate_manual_strategy(ex, symbol, cfg):
#     tf = cfg.get("timeframe", "1h")
#     ma_periods = cfg.get("ma_periods", []) or [0]
#     needed_limit = max(cfg.get("sr_lookback", 50), cfg.get("ob_lookback", 50),
#                        cfg.get("trend_lookback", 100), max(ma_periods), 210) + 30
#     df = get_ohlcv_df(ex, symbol, tf, limit=int(needed_limit))
#     if df is None:
#         return False, []
#     matched_rules = []; results = []
#     if cfg.get("ma_enabled"):
#         periods = cfg.get("ma_periods", [])
#         if not periods:
#             results.append(False)
#         else:
#             r = check_ma_condition(df, periods); results.append(r)
#             if r: matched_rules.append(f"MA({','.join(str(p) for p in periods)})")
#     if cfg.get("rsi_enabled"):
#         r = check_rsi_condition(df, cfg.get("rsi_min", 30), cfg.get("rsi_max", 45)); results.append(r)
#         if r: matched_rules.append(f"RSI({cfg.get('rsi_min')}-{cfg.get('rsi_max')})")
#     if cfg.get("sr_enabled"):
#         r = check_support_condition(df, cfg.get("sr_lookback", 50), cfg.get("sr_tolerance_pct", 1.0)); results.append(r)
#         if r: matched_rules.append("Support Bounce")
#     if cfg.get("ob_enabled"):
#         r = check_order_block_condition(df, cfg.get("ob_lookback", 50)); results.append(r)
#         if r: matched_rules.append("Order Block")
#     if cfg.get("vol_enabled"):
#         r = check_volume_condition(ex, symbol, cfg.get("vol_min_usdt", 500000)); results.append(r)
#         if r: matched_rules.append("Volume Filter")
#     if cfg.get("trend_enabled"):
#         r = check_trendline_condition(df, cfg.get("trend_lookback", 100), cfg.get("trend_touches", 3)); results.append(r)
#         if r: matched_rules.append("Trendline Bounce")
#     if not results:
#         return False, []
#     return all(results), matched_rules

# # ==========================================
# # AUTHENTICATION
# # ==========================================
# if not st.session_state.logged_in:
#     st.markdown("<br><br>", unsafe_allow_html=True)
#     col_a, col_b, col_c = st.columns([1, 1.4, 1])
#     with col_b:
#         st.markdown("<div class='crypto-card' style='text-align: center;'>", unsafe_allow_html=True)
#         if logo_path and os.path.exists(logo_path): st.image(logo_path, width=150)
#         st.markdown("<h1>⚡ Apex Trading</h1>", unsafe_allow_html=True)
#         st.markdown("<p style='color: #848e9c;'>Secure Multi-Exchange Algorithmic Platform</p><br>", unsafe_allow_html=True)
#         if not _CRYPTO_OK:
#             st.warning("⚠️ 'cryptography' install nahi hai — API keys encrypt nahi hongi. Terminal me: pip install cryptography")
#         tab_l, tab_s = st.tabs(["🔐 Login", "📝 Sign Up"])
#         with tab_l:
#             l_user = st.text_input("Username", key="l_user")
#             l_pass = st.text_input("Password", type="password", key="l_pass")
#             st.markdown("<br>", unsafe_allow_html=True)
#             if st.button("Access Terminal", use_container_width=True, type="primary"):
#                 users = db["users"]
#                 if l_user in users and verify_password(l_pass, users[l_user].get("password", "")):
#                     # legacy plain password -> hash me upgrade
#                     if not str(users[l_user].get("password", "")).startswith("pbkdf2$"):
#                         users[l_user]["password"] = hash_password(l_pass)
#                     st.session_state.logged_in = True
#                     st.session_state.username = l_user
#                     if l_user not in db["settings"]:
#                         db["settings"][l_user] = _blank_user_settings()
#                     save_db(db)
#                     st.success("✅ Login successful!"); st.rerun()
#                 else:
#                     st.error("❌ Invalid username or password.")
#         with tab_s:
#             s_user = st.text_input("Choose Username", key="s_user")
#             s_pass = st.text_input("Choose Password", type="password", key="s_pass")
#             st.markdown("<br>", unsafe_allow_html=True)
#             if st.button("Create Account & Login", use_container_width=True):
#                 users = db["users"]
#                 if s_user in users:
#                     st.warning("⚠️ Username already exists.")
#                 elif not s_user or not s_pass:
#                     st.warning("⚠️ Fields cannot be blank.")
#                 else:
#                     users[s_user] = {"password": hash_password(s_pass), "created": str(date.today())}
#                     db["settings"][s_user] = _blank_user_settings()
#                     save_db(db)
#                     st.session_state.logged_in = True
#                     st.session_state.username = s_user
#                     st.success("✅ Account created!"); st.rerun()
#         st.markdown("</div>", unsafe_allow_html=True)
#     st.stop()

# curr_user = st.session_state.username
# ACTIVE_USER = curr_user
# user_settings = db["settings"].setdefault(curr_user, _blank_user_settings())
# _backfill_user(user_settings)
# get_runtime(user_settings)
# save_db(db)

# # ==========================================
# # SIDEBAR
# # ==========================================
# if logo_path and os.path.exists(logo_path):
#     st.sidebar.image(logo_path, width=140)
# st.sidebar.markdown(f"""
#     <div style='padding: 12px; background: #181a20; border-radius: 10px; border: 1px solid #2b313a; margin-top: 10px; margin-bottom: 15px;'>
#         <div style='color: #848e9c; font-size: 11px;'>APEX TRADER</div>
#         <div style='color: #fcd535; font-size: 16px; font-weight: bold;'>👤 {curr_user}</div>
#     </div>
# """, unsafe_allow_html=True)
# if st.sidebar.button("🚪 Logout", use_container_width=True):
#     st.session_state.logged_in = False
#     st.session_state.bot_running = False
#     st.rerun()
# st.sidebar.markdown("---")
# config_menu = st.sidebar.radio(
#     "Configs",
#     ["📊 Dashboard", "🔌 Exchange Integration", "⚙️ Strategy Studio", "📦 Limitation & Campaign"],
#     label_visibility="collapsed"
# )

# # ==========================================
# # 1. EXCHANGE INTEGRATION
# # ==========================================
# if config_menu == "🔌 Exchange Integration":
#     st.title("🔌 Exchange API Integration")
#     st.markdown("---")
#     if _CRYPTO_OK:
#         st.markdown("<div class='crypto-card' style='border-left:4px solid #0ecb81;'>🔐 API key aur secret database me <b>encrypted</b> save hote hain (plain nahi).</div>", unsafe_allow_html=True)
#     else:
#         st.markdown("<div class='crypto-card' style='border-left:4px solid #f6465d;'>⚠️ <b>cryptography</b> install nahi — keys abhi plain save hongi. <code>pip install cryptography</code> chala kar dobara connect karo.</div>", unsafe_allow_html=True)
#     col1, col2 = st.columns([1.3, 1], gap="large")
#     with col1:
#         st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#         ex_list = ["Binance", "Bybit", "OKX", "KuCoin"]
#         cur_ex = user_settings["exchange"].get("name", "Binance")
#         ex_choice = st.selectbox("Select Crypto Exchange", ex_list, index=ex_list.index(cur_ex) if cur_ex in ex_list else 0)
#         market_type = st.radio("Market Architecture", ["Spot", "Futures (Derivatives)"], index=0 if user_settings["exchange"].get("market") == "Spot" else 1, horizontal=True)
#         api_k = st.text_input("API Key", type="password", value=dec_secret(user_settings["exchange"].get("key", "")))
#         secret_k = st.text_input("Secret Key", type="password", value=dec_secret(user_settings["exchange"].get("secret", "")))
#         demo_chk = st.checkbox("Enable Sandbox / Testnet Mode", value=user_settings["exchange"].get("demo", True))
#         st.caption("Tip: exchange par key banate waqt sirf **Spot trading** on karo, **Withdrawal OFF** rakho, aur ho sake to server IP whitelist karo.")
#         if st.button("🔌 Connect & Verify API", type="primary", use_container_width=True):
#             try:
#                 ex_config = {'apiKey': api_k, 'secret': secret_k, 'enableRateLimit': True,
#                              'options': {'defaultType': 'future' if market_type == "Futures (Derivatives)" else 'spot'}}
#                 ex = ccxt.binance(ex_config)
#                 if demo_chk:
#                     ex.set_sandbox_mode(True)
#                     if market_type == "Futures (Derivatives)":
#                         ex.urls['api']['fapiPublic'] = 'https://testnet.binancefuture.com/fapi/v1'
#                         ex.urls['api']['fapiPrivate'] = 'https://testnet.binancefuture.com/fapi/v1'
#                     else:
#                         ex.urls['api']['public'] = 'https://demo-api.binance.com/api/v3'
#                         ex.urls['api']['private'] = 'https://demo-api.binance.com/api/v3'
#                 ex.fetch_balance()
#                 user_settings["exchange"] = {"name": ex_choice, "market": market_type,
#                                              "key": enc_secret(api_k), "secret": enc_secret(secret_k),
#                                              "demo": demo_chk, "connected": True}
#                 save_db(db)
#                 st.success(f"✨ Successfully connected to {ex_choice} ({market_type})! Keys {'encrypted' if _CRYPTO_OK else 'saved'}.")
#             except Exception as e:
#                 user_settings["exchange"]["connected"] = False
#                 save_db(db)
#                 st.error(f"❌ Connection failed: {str(e)}")
#         st.markdown("</div>", unsafe_allow_html=True)

# # ==========================================
# # 2. STRATEGY STUDIO
# # ==========================================
# elif config_menu == "⚙️ Strategy Studio":
#     st.title("⚙️ Algorithmic Strategy Studio")
#     st.markdown("---")
#     st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#     exec_modes = ["Automated Trading (Bot takes trades & sets TP/SL automatically)",
#                   "Signal-Only Mode (Bot sends signals & email alerts only)"]
#     cur_exec = user_settings["strategy"].get("exec_mode", exec_modes[0])
#     exec_choice = st.radio("Choose how the bot should operate:", exec_modes, index=exec_modes.index(cur_exec) if cur_exec in exec_modes else 0)
#     user_settings["strategy"]["exec_mode"] = exec_choice
#     st.markdown("</div>", unsafe_allow_html=True)

#     mode_tab1, mode_tab2 = st.tabs(["🛠️ Manual Rule Builder", "🤖 AI Prompt (Auto)"])
#     with mode_tab1:
#         st.caption("Sirf jo checkbox tick karoge, bot SIRF wahi condition check karega (AND logic). "
#                    "Har indicator signal + confirmation candle dekh kar trade karta hai. Timeframe global hai.")
#         manual_cfg = user_settings["strategy"]["manual"]
#         st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#         st.subheader("⏱️ Timeframe (Global)")
#         tf_options = ["15m", "1h", "4h", "1d"]
#         cur_tf = manual_cfg.get("timeframe", "1h")
#         manual_cfg["timeframe"] = st.selectbox("Candle Timeframe", tf_options, index=tf_options.index(cur_tf) if cur_tf in tf_options else 1)
#         st.markdown("</div>", unsafe_allow_html=True)

#         c1, c2 = st.columns(2, gap="large")
#         with c1:
#             st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#             manual_cfg["ma_enabled"] = st.checkbox("📈 Enable Moving Average (MA) Filter", value=manual_cfg.get("ma_enabled", False))
#             ma_str = st.text_input("MA Periods (comma separated)",
#                                    value=",".join(str(p) for p in manual_cfg.get("ma_periods", [])),
#                                    placeholder="e.g. 200  ya  44,100,200  (khaali = MA check nahi hoga)",
#                                    disabled=not manual_cfg["ma_enabled"])
#             try:
#                 manual_cfg["ma_periods"] = [int(x.strip()) for x in ma_str.split(",") if x.strip()]
#             except Exception:
#                 manual_cfg["ma_periods"] = []
#             st.caption("Rule: signal candle green + har MA ke upar, phir confirmation candle bhi green + upar.")
#             st.markdown("</div>", unsafe_allow_html=True)

#             st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#             manual_cfg["rsi_enabled"] = st.checkbox("📊 Enable RSI Range Filter", value=manual_cfg.get("rsi_enabled", False))
#             rc1, rc2 = st.columns(2)
#             manual_cfg["rsi_min"] = rc1.number_input("RSI Min", 0, 100, value=int(manual_cfg.get("rsi_min", 30)), disabled=not manual_cfg["rsi_enabled"])
#             manual_cfg["rsi_max"] = rc2.number_input("RSI Max", 0, 100, value=int(manual_cfg.get("rsi_max", 45)), disabled=not manual_cfg["rsi_enabled"])
#             st.caption("Rule: RSI range me + confirmation candle green (momentum up).")
#             st.markdown("</div>", unsafe_allow_html=True)

#             st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#             manual_cfg["sr_enabled"] = st.checkbox("🧱 Enable Support Bounce Filter", value=manual_cfg.get("sr_enabled", False))
#             manual_cfg["sr_lookback"] = st.number_input("Support Lookback Candles", 10, 500, value=int(manual_cfg.get("sr_lookback", 50)), disabled=not manual_cfg["sr_enabled"])
#             manual_cfg["sr_tolerance_pct"] = st.number_input("Max Distance From Support (%)", 0.1, 10.0, value=float(manual_cfg.get("sr_tolerance_pct", 1.0)), disabled=not manual_cfg["sr_enabled"])
#             st.caption("Rule: price support ke paas aaye + green bounce candle confirm kare.")
#             st.markdown("</div>", unsafe_allow_html=True)

#         with c2:
#             st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#             manual_cfg["ob_enabled"] = st.checkbox("🟩 Enable Order Block (Bullish) Filter", value=manual_cfg.get("ob_enabled", False))
#             manual_cfg["ob_lookback"] = st.number_input("Order Block Lookback Candles", 20, 500, value=int(manual_cfg.get("ob_lookback", 50)), disabled=not manual_cfg["ob_enabled"])
#             st.caption("Rule: OB zone touch + green reaction candle confirm kare.")
#             st.markdown("</div>", unsafe_allow_html=True)

#             st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#             manual_cfg["vol_enabled"] = st.checkbox("💧 Enable Volume Filter", value=manual_cfg.get("vol_enabled", False))
#             manual_cfg["vol_min_usdt"] = st.number_input("Minimum 24h Volume (USDT)", 0, 1000000000, value=int(manual_cfg.get("vol_min_usdt", 500000)), disabled=not manual_cfg["vol_enabled"])
#             st.caption("Rule: 24h volume kam se kam itna ho (confirmation candle nahi lagti).")
#             st.markdown("</div>", unsafe_allow_html=True)

#             st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#             manual_cfg["trend_enabled"] = st.checkbox("📐 Enable Trendline Bounce Filter", value=manual_cfg.get("trend_enabled", False))
#             manual_cfg["trend_lookback"] = st.number_input("Trendline Lookback Candles", 20, 500, value=int(manual_cfg.get("trend_lookback", 100)), disabled=not manual_cfg["trend_enabled"])
#             manual_cfg["trend_touches"] = st.number_input("Minimum Touches", 2, 10, value=int(manual_cfg.get("trend_touches", 3)), disabled=not manual_cfg["trend_enabled"])
#             st.caption("Rule: rising trendline touch + green bounce candle confirm kare.")
#             st.markdown("</div>", unsafe_allow_html=True)

#         active_rules = []
#         if manual_cfg.get("ma_enabled"): active_rules.append("MA")
#         if manual_cfg.get("rsi_enabled"): active_rules.append("RSI")
#         if manual_cfg.get("sr_enabled"): active_rules.append("Support")
#         if manual_cfg.get("ob_enabled"): active_rules.append("Order Block")
#         if manual_cfg.get("vol_enabled"): active_rules.append("Volume")
#         if manual_cfg.get("trend_enabled"): active_rules.append("Trendline")

#         st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#         st.write("**Active Rules (AND logic):**")
#         if active_rules:
#             st.markdown("".join([f"<span class='rule-tag'>{r}</span>" for r in active_rules]), unsafe_allow_html=True)
#             if manual_cfg.get("ma_enabled") and not manual_cfg.get("ma_periods"):
#                 st.warning("⚠️ MA on hai lekin koi number nahi diya — MA field me kam se kam ek number likho (jaise 200).")
#         else:
#             st.warning("⚠️ Koi rule enable nahi hai — is state mein bot koi trade nahi lega.")
#         st.markdown("</div>", unsafe_allow_html=True)

#         # ---- Coin Universe / Monitoring-Tag filter ----
#         st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#         st.subheader("🌐 Coin Filters (scan universe)")
#         flt = user_settings.setdefault("filters", dict(DEFAULT_FILTERS))
#         flt["universe_min_volume"] = st.number_input(
#             "Scan sirf itne 24h Volume (USDT) se upar wale coins par",
#             0, 1000000000, value=int(flt.get("universe_min_volume", 1000000)))
#         exclude_str = st.text_input(
#             "Exclude coins (comma separated) — Monitoring-Tag / risky coins yahan likho",
#             value=",".join(flt.get("exclude", [])),
#             placeholder="e.g. QKC, XYZ")
#         flt["exclude"] = [x.strip().upper() for x in exclude_str.split(",") if x.strip()]
#         st.caption("Note: Binance ka 'Monitoring Tag' API se seedha nahi milta, is liye aise coins yahan likh kar block karo. "
#                    "Stablecoins/leveraged/delisted pehle se auto-filtered hain.")
#         st.markdown("</div>", unsafe_allow_html=True)

#         if st.button("💾 Save Manual Strategy", type="primary", use_container_width=True, key="save_manual"):
#             user_settings["strategy"]["manual"] = manual_cfg
#             user_settings["strategy"]["mode"] = "manual"
#             save_db(db)
#             st.success("✅ Manual strategy + filters saved. Bot ab isi ke hisab se scan karega.")

#     with mode_tab2:
#         st.caption("Free-text prompt (Note: abhi AI evaluation connect nahi — trades manual rule builder se lagti hain).")
#         st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#         ai_p = st.text_area("Write your custom prompt:", value=user_settings["strategy"].get("ai_prompt", ""), height=160)
#         st.markdown("</div>", unsafe_allow_html=True)
#         if st.button("💾 Save & Use AI Prompt Mode", type="primary", use_container_width=True, key="save_ai"):
#             user_settings["strategy"]["ai_prompt"] = ai_p
#             user_settings["strategy"]["mode"] = "ai_prompt"
#             save_db(db)
#             st.success("✅ AI Prompt mode active.")

#     st.markdown("---")
#     st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#     st.subheader("🛡️ Risk Management (applies to both modes)")
#     sl = st.number_input("Stop Loss Percentage (%)", 0.1, 20.0, value=user_settings["strategy"].get("sl_pct", 2.0))
#     tp = st.number_input("Take Profit Percentage (%)", 0.1, 50.0, value=user_settings["strategy"].get("tp_pct", 4.5))
#     user_settings["strategy"]["sl_pct"] = sl
#     user_settings["strategy"]["tp_pct"] = tp
#     if st.button("💾 Save Risk Settings", use_container_width=True):
#         save_db(db); st.success("✅ Risk settings saved.")
#     st.markdown("</div>", unsafe_allow_html=True)

#     active_mode = user_settings["strategy"].get("mode", "manual")
#     st.info(f"🔵 Currently active mode: **{'Manual Rule Builder' if active_mode == 'manual' else 'AI Prompt (Auto)'}**")

# # ==========================================
# # 3. LIMITATION & CAMPAIGN
# # ==========================================
# elif config_menu == "📦 Limitation & Campaign":
#     st.markdown("<h2>📦 Limitation & Campaign</h2>", unsafe_allow_html=True)
#     st.markdown("---")
#     col1, col2 = st.columns(2, gap="large")
#     with col1:
#         c_days = st.number_input("Campaign Duration", 1, 365, value=user_settings["limits"].get("campaign_days", 1))
#         d_limit = st.number_input("Daily Maximum Auto Trades", 1, 100, value=user_settings["limits"].get("daily_limit", 1))
#         t_amt = st.number_input("Per Trade USDT", 5.0, value=user_settings["limits"].get("trade_amount", 100.0))
#         user_settings["limits"]["campaign_days"] = c_days
#         user_settings["limits"]["daily_limit"] = d_limit
#         user_settings["limits"]["trade_amount"] = t_amt
#         st.caption("Auto mode: bot exactly itni hi trades lega (2→2, 20→20), har coin sirf 1 baar, phir aaj ke liye ruk jayega. "
#                    "Signal-Only mode: is limit se azaad — signal deta rahega.")
#     with col2:
#         email_cfg = user_settings.setdefault("email", {"enabled": True, "sender": "", "receiver": "", "brevo_api_key": ""})
#         e_en = st.checkbox("Enable Email Notifications", value=email_cfg.get("enabled", True))
#         e_sender = st.text_input("Sender Email (Brevo par verified hona chahiye)", value=email_cfg.get("sender", "")).strip()
#         e_key_raw = st.text_input("Brevo API Key", type="password", value=dec_secret(email_cfg.get("brevo_api_key", "")))
#         e_key = e_key_raw.strip()
#         e_recv = st.text_input("Send Alerts To", value=email_cfg.get("receiver", "")).strip()
#         email_cfg.update({"enabled": e_en, "sender": e_sender,
#                           "brevo_api_key": enc_secret(e_key), "receiver": e_recv})

#         st.caption("Tip: DigitalOcean jaise VPS par SMTP (Gmail) ports hamesha block hote hain, isliye email ab "
#                    "**Brevo** (free, 300/din) ke zariye HTTPS se jati hai. brevo.com par free sign-up karo, apna "
#                    "sender email verify karo, phir SMTP & API → API Keys se key banao. **Zaroori:** Brevo ke Security "
#                    "settings me apne server ka IP (jo aapke droplet ka public IP hai) authorize/whitelist karna hoga, "
#                    "warna API key kaam nahi karegi.")


#         if st.button("📧 Send Test Email", use_container_width=True):
#             with st.spinner("Test email bheja ja raha hai..."):
#                 test_ok = send_email_alert(
#                     "✅ Apex Trading — Test Email",
#                     "<html><body style='font-family:Arial;background:#0b0e11;color:#eaecef;padding:20px;'>"
#                     "<h2 style='color:#fcd535;'>Test email successful!</h2>"
#                     "<p>Agar aapko ye email mila hai, matlab SMTP settings bilkul sahi hain.</p>"
#                     "</body></html>",
#                     email_cfg
#                 )
#             if test_ok:
#                 st.success("✅ Test email bhej diya gaya! Apna inbox (aur Spam folder) check karo.")
#             else:
#                 st.error("❌ Test email fail hua. Exact error dekhne ke liye Dashboard → 📜 Bot Logs kholo — "
#                          "wahan Gmail ka asli error message milega (jaise galat App Password, ya 2-Step Verification off).")

#     if st.button("💾 Save Limits & Notifications", type="primary", use_container_width=True):
#         save_db(db); st.success("✅ Saved successfully!")

# # ==========================================
# # 4. DASHBOARD
# # ==========================================
# else:
#     rt = get_runtime(user_settings)
#     save_db(db)
#     st.markdown(f"""
#         <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
#             <div>
#                 <h1 style='margin: 0; font-size: 26px;'>⚡ Apex Trading Dashboard</h1>
#                 <p style='margin: 4px 0 0 0; color: #848e9c; font-size: 13px;'>Rule-Based Strategy Engine + optional AI Prompt mode.</p>
#             </div>
#             <div style='background: #181a20; border: 1px solid #2b313a; padding: 8px 16px; border-radius: 8px; text-align: right;'>
#                 <div style='color: #fcd535; font-weight: bold;'>👤 {curr_user}</div>
#                 <div style='color: #0ecb81; font-size: 12px;'>● Active Session</div>
#             </div>
#         </div>
#     """, unsafe_allow_html=True)

#     dash_tab = st.radio("Tabs", ["📊 Analytics", "🎯 Active Trades", "🔍 Signal Feed", "💰 History", "📜 Bot Logs"],
#                         horizontal=True, label_visibility="collapsed")
#     st.markdown("---")

#     if dash_tab == "📊 Analytics":
#         ex_status_cfg = user_settings.get("exchange", {})
#         is_connected = bool(ex_status_cfg.get("connected")) and bool(ex_status_cfg.get("key"))
#         if is_connected:
#             st.markdown("<div class='crypto-card'>🟢 <b>Exchange Status:</b> Connected — Automated mode CAN place real orders.</div>", unsafe_allow_html=True)
#         else:
#             st.markdown("<div class='crypto-card'>🔴 <b>Exchange Status:</b> NOT connected (or API key missing). "
#                         "Bot signals to banata rahega par tab tak real order NAHI karega jab tak <b>Exchange Integration</b> me connect na karo.</div>", unsafe_allow_html=True)

#         st.markdown("<div class='crypto-card' style='border-left:4px solid #f6465d;'>⚠️ <b>Zaroori:</b> App ko sirf <b>ek hi browser tab</b> me chalao. "
#                     "Ek se zyada tab khule honge to har tab apna bot loop chalata hai — is se limit galat lag sakti hai.</div>", unsafe_allow_html=True)

#         history = user_settings["trade_history"]
#         total_trades = len(history)
#         successful_wins = len([h for h in history if "PROFIT" in h.get("status", "")])
#         today_pnl = sum([float(h.get("pnl_val", 0)) for h in history if h.get("date") == str(date.today())])

#         c_m1, c_m2, c_m3, c_m4 = st.columns(4)
#         c_m1.metric("Total Trades Executed", total_trades)
#         c_m2.metric("Successful Wins", successful_wins)
#         c_m3.metric("Today's Net PnL", f"${today_pnl:+,.2f}")
#         c_m4.metric("Bot Status", "Running" if st.session_state.bot_running else "Stopped")

#         _lim = int(user_settings["limits"].get("daily_limit", 1))
#         # Display ko hamesha clamp karo — chahe kisi bhi wajah se number thoda idhar-udhar ho,
#         # user ko kabhi limit se zyada "X/Y" ka number NAHI dikhna chahiye.
#         _shown_trades = min(int(rt.get('trades_today', 0)), _lim)
#         st.markdown(
#             f"<div class='crypto-card'><b>Today's Auto Trades:</b> "
#             f"<span style='color:#fcd535;'>{_shown_trades} / {_lim}</span> &nbsp; "
#             f"({max(_lim - _shown_trades, 0)} remaining today) &nbsp;|&nbsp; "
#             f"<b>Signals Today:</b> <span style='color:#0ecb81;'>{rt['signals_today']}</span></div>",
#             unsafe_allow_html=True)

#         active_mode = user_settings["strategy"].get("mode", "manual")
#         st.markdown(f"<div class='crypto-card'><b>Strategy Mode:</b> "
#                     f"<span style='color:#fcd535;'>{'🛠️ Manual Rule Builder' if active_mode=='manual' else '🤖 AI Prompt (Auto)'}</span></div>",
#                     unsafe_allow_html=True)

#         st.markdown("<br>", unsafe_allow_html=True)
#         b_c1, b_c2 = st.columns(2)
#         with b_c1:
#             if st.button("🚀 START BOT ENGINE", use_container_width=True, type="primary"):
#                 st.session_state.bot_running = True
#                 add_log("Apex bot engine started.")
#                 st.rerun()
#         with b_c2:
#             if st.button("🛑 STOP BOT", use_container_width=True):
#                 st.session_state.bot_running = False
#                 add_log("Apex bot stopped.")
#                 st.rerun()

#     elif dash_tab == "🎯 Active Trades":
#         top1, top2 = st.columns([0.7, 0.3])
#         with top1:
#             st.subheader("🎯 Active Positions")
#         with top2:
#             if user_settings["active_trades"] and st.button("🗑️ Clear All", use_container_width=True, key="clr_active"):
#                 user_settings["active_trades"] = []
#                 save_db(db); st.rerun()

#         active_list = user_settings["active_trades"]
#         if active_list:
#             for idx, trade in enumerate(list(active_list)):
#                 cc1, cc2 = st.columns([0.9, 0.1])
#                 with cc1:
#                     rules_html = f"<br><span style='color:#848e9c;font-size:12px;'>Rules:</span> <b style='font-size:12px;'>{trade.get('Rules','—')}</b>" if trade.get("Rules") else ""
#                     st.markdown(f"""
#                     <div class='trade-card'>
#                         <div style='display:flex; justify-content:space-between; align-items:center;'>
#                             <span class='sym-title'>{trade['Symbol']} <span style='color:#848e9c;font-size:12px;'>({trade['Market']})</span></span>
#                             <span class='badge-live'>🟢 LIVE</span>
#                         </div>
#                         <div style='margin-top:10px;'>
#                             <span class='kv'><span class='k'>Entry</span><span class='v' style='color:#3b82f6;'>${trade['Entry']}</span></span>
#                             <span class='kv'><span class='k'>Allocated</span><span class='v'>{trade['Amount']}</span></span>
#                             <span class='kv'><span class='k'>Take Profit</span><span class='v' style='color:#0ecb81;'>${trade['TP']}</span></span>
#                             <span class='kv'><span class='k'>Stop Loss</span><span class='v' style='color:#f6465d;'>${trade['SL']}</span></span>
#                         </div>
#                         {rules_html}
#                     </div>
#                     """, unsafe_allow_html=True)
#                 with cc2:
#                     if st.button("❌", key=f"del_trade_{idx}", help="Is card ko hatao"):
#                         user_settings["active_trades"].pop(idx)
#                         save_db(db); st.rerun()
#         else:
#             st.info("No active trades running right now.")

#     elif dash_tab == "🔍 Signal Feed":
#         top1, top2 = st.columns([0.7, 0.3])
#         with top1:
#             st.subheader("📡 Live Signals Feed")
#         with top2:
#             if user_settings["signals_feed"] and st.button("🗑️ Clear All", use_container_width=True, key="clr_signals"):
#                 user_settings["signals_feed"] = []
#                 save_db(db); st.rerun()

#         if user_settings["signals_feed"]:
#             for i, sig in enumerate(list(user_settings["signals_feed"])):
#                 epoch_time = sig.get("timestamp_epoch", time.time())
#                 diff_seconds = int(time.time() - epoch_time)
#                 if diff_seconds < 60: time_ago_str = "Just now"
#                 elif diff_seconds < 3600: time_ago_str = f"{diff_seconds // 60} mins ago"
#                 elif diff_seconds < 86400: time_ago_str = f"{diff_seconds // 3600} hrs ago"
#                 else: time_ago_str = "1 day ago"

#                 stype = sig.get("type", "Signal")
#                 badge = "badge-live" if stype == "Executed Trade" else "badge-signal"
#                 badge_txt = "✅ EXECUTED" if stype == "Executed Trade" else "📡 SIGNAL"
#                 rules_html = f"<br><span style='color:#848e9c;font-size:12px;'>Rules:</span> <b style='font-size:12px;'>{sig.get('rules')}</b>" if sig.get('rules') else ""

#                 cc1, cc2 = st.columns([0.9, 0.1])
#                 with cc1:
#                     st.markdown(f"""
#                     <div class='sig-card'>
#                         <div style='display:flex; justify-content:space-between; align-items:center;'>
#                             <span class='sym-title'>{sig['symbol']}</span>
#                             <span class='{badge}'>{badge_txt}</span>
#                         </div>
#                         <div style='margin-top:10px;'>
#                             <span class='kv'><span class='k'>Entry</span><span class='v' style='color:#3b82f6;'>{sig.get('entry',0):,.6f}</span></span>
#                             <span class='kv'><span class='k'>Take Profit</span><span class='v' style='color:#0ecb81;'>{sig.get('tp',0):,.6f}</span></span>
#                             <span class='kv'><span class='k'>Stop Loss</span><span class='v' style='color:#f6465d;'>{sig.get('sl',0):,.6f}</span></span>
#                         </div>
#                         {rules_html}
#                         <div style='color:#848e9c; font-size:11px; margin-top:8px;'>🕒 {time_ago_str} ({sig.get('time','N/A')})</div>
#                     </div>
#                     """, unsafe_allow_html=True)
#                 with cc2:
#                     if st.button("❌", key=f"del_sig_{sig.get('id', i)}", help="Is signal ko hatao"):
#                         user_settings["signals_feed"].pop(i)
#                         save_db(db); st.rerun()
#         else:
#             st.info("No active signals right now.")

#     elif dash_tab == "💰 History":
#         top1, top2 = st.columns([0.7, 0.3])
#         with top1:
#             st.subheader("💰 Trade History")
#         with top2:
#             if user_settings["trade_history"] and st.button("🗑️ Clear History", use_container_width=True, key="clr_hist"):
#                 user_settings["trade_history"] = []
#                 save_db(db); st.rerun()
#         if user_settings["trade_history"]:
#             st.dataframe(pd.DataFrame(user_settings["trade_history"]), use_container_width=True)
#         else:
#             st.info("No trade history available yet.")

#     elif dash_tab == "📜 Bot Logs":
#         st.subheader("📜 Bot Logs (most recent first)")
#         st.caption("Yahan exact reason milega ke koi trade kyun skip hui, ya order kyun fail hua.")
#         logs = user_settings.get("logs", [])
#         if logs:
#             if st.button("🗑️ Clear Logs"):
#                 user_settings["logs"] = []; save_db(db); st.rerun()
#             for line in reversed(logs[-200:]):
#                 st.text(line)
#         else:
#             st.info("Koi log abhi tak nahi bana.")

# # ==========================================
# # BACKGROUND AUTOMATED & EMAIL LOOP
# # ==========================================
# if st.session_state.bot_running:
#     rt = get_runtime(user_settings)
#     save_db(db)
#     daily_lim = int(user_settings["limits"].get("daily_limit", 1))
#     exec_mode_setting = user_settings["strategy"].get("exec_mode", "")
#     is_signal_only = "Signal-Only" in exec_mode_setting or "Signal" in exec_mode_setting

#     if (not is_signal_only) and rt["trades_today"] >= daily_lim:
#         add_log(f"⏳ Daily auto-trade limit reached ({rt['trades_today']}/{daily_lim}). Aaj ke liye paused (kal reset).")
#         st.warning(f"⚠️ Daily trade limit {daily_lim} poori ho gayi — aaj {rt['trades_today']} trade ho chuke. Ab kal tak paused.")
#         time.sleep(15); st.rerun()

#     try:
#         ex_cfg = user_settings["exchange"]
#         market_m = ex_cfg.get("market", "Spot")
#         ex_config = {'apiKey': dec_secret(ex_cfg.get("key")), 'secret': dec_secret(ex_cfg.get("secret")),
#                      'enableRateLimit': True,
#                      'options': {'defaultType': 'future' if market_m == "Futures (Derivatives)" else 'spot'}}
#         ex = ccxt.binance(ex_config)
#         if ex_cfg.get("demo"):
#             ex.set_sandbox_mode(True)
#             if market_m == "Futures (Derivatives)":
#                 ex.urls['api']['fapiPublic'] = 'https://testnet.binancefuture.com/fapi/v1'
#                 ex.urls['api']['fapiPrivate'] = 'https://testnet.binancefuture.com/fapi/v1'
#             else:
#                 ex.urls['api']['public'] = 'https://demo-api.binance.com/api/v3'
#                 ex.urls['api']['private'] = 'https://demo-api.binance.com/api/v3'

#         ex.load_markets()
#         flt = user_settings.get("filters", DEFAULT_FILTERS)

#         # ---- PERF/STABILITY FIX ----
#         # Pehle har 15 second me Binance ke SAARE (2000+) coins ka poora ticker data
#         # (fetch_tickers) dobara mangwaya jata tha — chhote VPS (1GB RAM) ke liye ye
#         # bahut bhaari kaam hai aur crash/restart ki sabse badi wajah tha (jisse
#         # session/login "khud logout" jaisa lagta tha). Ab ye data sirf har
#         # UNIVERSE_CACHE_TTL second (3 minute) me ek baar refresh hota hai — baaki
#         # waqt session me cache se use hota hai. Strategy/behaviour bilkul wahi
#         # rehta hai, sirf resource-use kam ho jata hai.
#         _now_ts = time.time()
#         _cache_key = (curr_user, int(flt.get("universe_min_volume", 1000000)),
#                       tuple(sorted(e.upper() for e in flt.get("exclude", []))))
#         _cache_fresh = (
#             st.session_state.get("_universe_cache_key") == _cache_key
#             and (_now_ts - st.session_state.get("_universe_cache_ts", 0)) < UNIVERSE_CACHE_TTL
#             and st.session_state.get("_universe_cache")
#         )
#         if _cache_fresh:
#             universe = st.session_state["_universe_cache"]
#             all_tickers = st.session_state.get("_tickers_cache")
#         else:
#             try:
#                 all_tickers = ex.fetch_tickers()
#             except Exception:
#                 all_tickers = None
#             universe = build_symbol_universe(ex, all_tickers,
#                                              min_volume=int(flt.get("universe_min_volume", 1000000)),
#                                              exclude_bases=flt.get("exclude", []))
#             if not universe:
#                 excl = {e.upper() for e in flt.get("exclude", [])}
#                 universe = [s for s in ex.symbols
#                             if s.endswith('/USDT') and s.split('/')[0].upper() not in STABLE_OR_FIAT
#                             and s.split('/')[0].upper() not in excl][:40]
#             if not universe:
#                 universe = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
#             st.session_state["_universe_cache"] = universe
#             st.session_state["_tickers_cache"] = all_tickers
#             st.session_state["_universe_cache_key"] = _cache_key
#             st.session_state["_universe_cache_ts"] = _now_ts

#         available = [c for c in universe if c not in rt["traded_coins_today"]]
#         if not available:
#             if is_signal_only:
#                 rt["traded_coins_today"] = []
#                 save_db(db)
#                 available = universe
#             else:
#                 add_log("🔎 Aaj ke available coins khatam. Idling.")
#                 time.sleep(15); st.rerun()

#         strategy_mode = user_settings["strategy"].get("mode", "manual")
#         chosen_coin = None; c_price = 0.0; matched_rules_str = ""

#         if strategy_mode == "manual":
#             manual_cfg = user_settings["strategy"]["manual"]
#             sample_pool = available[:25] if len(available) >= 25 else available
#             candidates = []
#             for coin in sample_pool:
#                 try:
#                     passed, rules = evaluate_manual_strategy(ex, coin, manual_cfg)
#                     if passed:
#                         candidates.append((coin, rules))
#                 except Exception:
#                     continue
#             if candidates:
#                 best = None; best_vol = -1
#                 for coin, rules in candidates:
#                     vol = 0.0
#                     if all_tickers and coin in all_tickers:
#                         try: vol = float(all_tickers[coin].get('quoteVolume') or 0)
#                         except Exception: vol = 0.0
#                     else:
#                         try: vol = float(ex.fetch_ticker(coin).get('quoteVolume') or 0)
#                         except Exception: vol = 0.0
#                     if vol > best_vol:
#                         best_vol = vol; best = (coin, rules)
#                 chosen_coin, matched_rules_list = best
#                 matched_rules_str = ", ".join(matched_rules_list)
#                 try:
#                     c_price = float(ex.fetch_ticker(chosen_coin).get('last') or 0.0)
#                 except Exception:
#                     c_price = 0.0
#             else:
#                 add_log("🔎 Manual scan complete — koi coin saari ticked conditions match nahi kar raha. Idling.")
#         else:
#             add_log("⚠️ AI Prompt mode selected hai par koi AI evaluation connect nahi — is mode me trade nahi banegi.")

#         if chosen_coin is None:
#             time.sleep(15); st.rerun()

#         # ---- SLOT RESERVE (order se PEHLE) ----
#         ok, reason, db = try_reserve_slot(curr_user, chosen_coin, daily_lim, is_signal_only)
#         user_settings = db["settings"][curr_user]
#         rt = get_runtime(user_settings)

#         # ---- EXTRA SAFETY NET ----
#         # Chahe kitni bhi tabs/process ya restart ho jaye, trades_today kabhi bhi
#         # daily_lim se zyada NAHI hona chahiye. Agar phir bhi (kisi wajah se) ho
#         # jaye, is reservation ko turant undo karo — order place hi NAHI hoga, aur
#         # limit hamesha exactly wahi rahegi jo user ne set ki hai (2 -> 2, 50 -> 50).
#         if ok and not is_signal_only and rt["trades_today"] > daily_lim:
#             rt["trades_today"] = daily_lim
#             if chosen_coin in rt["traded_coins_today"]:
#                 rt["traded_coins_today"].remove(chosen_coin)
#             save_db(db)
#             add_log(f"🛡️ Safety rollback: {chosen_coin} reservation undo ki gayi (limit {daily_lim} already reached tha).")
#             ok = False
#             reason = "limit reached"

#         if not ok:
#             if reason == "limit reached":
#                 add_log(f"⏳ Limit reached ({rt['trades_today']}/{daily_lim}) — {chosen_coin} skip. Paused for today.")
#                 st.warning(f"⚠️ Daily limit {daily_lim} poori. Ab kal tak paused.")
#             else:
#                 add_log(f"↩️ {chosen_coin} skip ({reason}). Agla coin dekhenge.")
#             time.sleep(15); st.rerun()

#         if c_price <= 0:
#             try:
#                 ohlcv = ex.fetch_ohlcv(chosen_coin, timeframe='1m', limit=1)
#                 if ohlcv: c_price = float(ohlcv[0][4])
#             except Exception:
#                 c_price = 1.0

#         amt_usdt = float(user_settings["limits"]["trade_amount"])
#         try:
#             coin_qty = float(ex.amount_to_precision(chosen_coin, amt_usdt / c_price))
#         except Exception:
#             coin_qty = amt_usdt / c_price

#         tp_p = user_settings["strategy"]["tp_pct"]; sl_p = user_settings["strategy"]["sl_pct"]
#         tp_val = c_price * (1 + tp_p / 100); sl_val = c_price * (1 - sl_p / 100)

#         current_time_str = datetime.now().strftime("%I:%M:%S %p")
#         full_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         timestamp_epoch = datetime.now().timestamp()

#         # per-user signals feed (24h se purane -> signal_history)
#         us_feed = user_settings.setdefault("signals_feed", [])
#         us_hist = user_settings.setdefault("signal_history", [])
#         active_signals = []
#         for sig in us_feed:
#             if (timestamp_epoch - sig.get("timestamp_epoch", timestamp_epoch)) >= 86400:
#                 if sig not in us_hist:
#                     us_hist.insert(0, sig)
#             else:
#                 active_signals.append(sig)
#         user_settings["signals_feed"] = active_signals

#         new_signal = {
#             "id": f"{chosen_coin}_{int(timestamp_epoch)}",
#             "time": current_time_str, "full_timestamp": full_ts, "timestamp_epoch": timestamp_epoch,
#             "symbol": chosen_coin,
#             "strategy": "Manual Rule Engine" if strategy_mode == "manual" else "AI Prompt Engine",
#             "rules": matched_rules_str, "entry": c_price, "tp": tp_val, "sl": sl_val,
#             "type": "Signal Only" if is_signal_only else "Executed Trade"
#         }
#         user_settings["signals_feed"].insert(0, new_signal)
#         save_db(db)

#         email_cfg = user_settings.get("email", {})
#         if email_cfg.get("enabled"):
#             email_sub = f"🚨 [Apex Trading] {'Signal Generated' if is_signal_only else 'Trade Executed'}: {chosen_coin}"
#             email_body_html = f"""
#             <html><body style="font-family: Arial, sans-serif; background-color: #0b0e11; color: #eaecef; padding: 20px;">
#                 <div style="max-width: 600px; margin: auto; background: #181a20; border: 1px solid #2b313a; border-radius: 12px; padding: 25px;">
#                     <h2 style="color: #fcd535; margin-top: 0; text-align: center;">⚡ Apex Automated Alert</h2>
#                     <p style="color: #0ecb81; text-align: center; font-weight: bold;">Status: Strategy conditions successfully met!</p>
#                     <p style="color: #848e9c; text-align:center; font-size:12px;">Matched rules: {matched_rules_str or "N/A"}</p>
#                     <hr style="border: 0; border-top: 1px solid #2b313a; margin: 20px 0;">
#                     <table style="width: 100%; font-size: 14px; color: #eaecef; border-collapse: collapse;">
#                         <tr><td style="padding: 8px 0; color: #848e9c;">Trading Pair:</td><td style="padding: 8px 0; font-weight: bold; color: #fcd535; text-align: right;">{chosen_coin}</td></tr>
#                         <tr><td style="padding: 8px 0; color: #848e9c;">Market Type:</td><td style="padding: 8px 0; font-weight: bold; text-align: right;">{market_m}</td></tr>
#                         <tr><td style="padding: 8px 0; color: #848e9c;">Entry Price:</td><td style="padding: 8px 0; font-weight: bold; color: #3b82f6; text-align: right;">${c_price:,.6f}</td></tr>
#                         <tr><td style="padding: 8px 0; color: #848e9c;">Take Profit (TP):</td><td style="padding: 8px 0; font-weight: bold; color: #0ecb81; text-align: right;">${tp_val:,.6f} (+{tp_p}%)</td></tr>
#                         <tr><td style="padding: 8px 0; color: #848e9c;">Stop Loss (SL):</td><td style="padding: 8px 0; font-weight: bold; color: #f6465d; text-align: right;">${sl_val:,.6f} (-{sl_p}%)</td></tr>
#                         <tr><td style="padding: 8px 0; color: #848e9c;">Allocated Amount:</td><td style="padding: 8px 0; font-weight: bold; text-align: right;">${amt_usdt} USDT</td></tr>
#                     </table>
#                 </div></body></html>"""
#             send_email_alert(email_sub, email_body_html, email_cfg)

#         # -------- SIGNAL-ONLY --------
#         if is_signal_only:
#             add_log(f"📡 Signal #{rt['signals_today']} generated for {chosen_coin} (rules: {matched_rules_str}).")
#             time.sleep(15); st.rerun()

#         # -------- AUTO TRADE --------
#         placed_ok = False
#         if "Automated Trading" in exec_mode_setting:
#             if not (ex_cfg.get("connected") and ex_cfg.get("key")):
#                 add_log(f"⚠️ {chosen_coin}: exchange not connected — real order skip, signal recorded. "
#                         f"(Slot consume ho gaya taake limit safe rahe.)")
#             else:
#                 try:
#                     formatted_tp_price = float(ex.price_to_precision(chosen_coin, tp_val))
#                     formatted_sl_price = float(ex.price_to_precision(chosen_coin, sl_val))
#                 except Exception:
#                     formatted_tp_price = tp_val; formatted_sl_price = sl_val

#                 if market_m == "Spot":
#                     try:
#                         buy_res = ex.create_market_buy_order(chosen_coin, coin_qty)
#                         placed_ok = True
#                         add_log(f"✅ Spot Market Buy Executed for {chosen_coin} (rules: {matched_rules_str})")
#                     except Exception as buy_err:
#                         add_log(f"❌ Buy Order Error: {str(buy_err)}"); buy_res = None
#                     if buy_res:
#                         time.sleep(1.5)
#                         base_ccy = chosen_coin.split('/')[0]; sell_qty = coin_qty
#                         try:
#                             bal = ex.fetch_balance()
#                             free_amt = float(bal['free'].get(base_ccy, 0) or 0)
#                             if free_amt > 0: sell_qty = free_amt
#                         except Exception: pass
#                         try: sell_qty = float(ex.amount_to_precision(chosen_coin, sell_qty))
#                         except Exception: pass
#                         try: sl_limit_price = float(ex.price_to_precision(chosen_coin, sl_val * 0.997))
#                         except Exception: sl_limit_price = formatted_sl_price
#                         oco_done = False
#                         oco_fn = getattr(ex, 'private_post_order_oco', None)
#                         if oco_fn is not None:
#                             try:
#                                 oco_fn({'symbol': chosen_coin.replace('/', ''), 'side': 'SELL',
#                                         'quantity': ex.amount_to_precision(chosen_coin, sell_qty),
#                                         'price': ex.price_to_precision(chosen_coin, formatted_tp_price),
#                                         'stopPrice': ex.price_to_precision(chosen_coin, formatted_sl_price),
#                                         'stopLimitPrice': ex.price_to_precision(chosen_coin, sl_limit_price),
#                                         'stopLimitTimeInForce': 'GTC'})
#                                 add_log(f"🛡️ OCO placed — TP ${formatted_tp_price} / SL ${formatted_sl_price}")
#                                 oco_done = True
#                             except Exception as oco_err:
#                                 add_log(f"⚠️ OCO not available ({str(oco_err)[:70]}), trying separate SL/TP...")
#                         if not oco_done:
#                             try:
#                                 ex.create_order(chosen_coin, 'STOP_LOSS_LIMIT', 'sell', sell_qty, sl_limit_price, {'stopPrice': formatted_sl_price})
#                                 add_log(f"🛡️ Stop Loss placed at trigger ${formatted_sl_price}")
#                             except Exception:
#                                 try:
#                                     ex.create_order(chosen_coin, 'STOP_LOSS', 'sell', sell_qty, None, {'stopPrice': formatted_sl_price})
#                                     add_log(f"🛡️ Stop Loss (Market) placed at trigger ${formatted_sl_price}")
#                                 except Exception as sl_fallback_err:
#                                     add_log(f"⚠️ Stop Loss Order Warning: {str(sl_fallback_err)}")
#                             try:
#                                 bal2 = ex.fetch_balance()
#                                 free2 = float(bal2['free'].get(base_ccy, 0) or 0)
#                                 tp_qty = float(ex.amount_to_precision(chosen_coin, free2)) if free2 > 0 else 0
#                                 if tp_qty > 0:
#                                     ex.create_limit_sell_order(chosen_coin, tp_qty, formatted_tp_price)
#                                     add_log(f"🎯 Take Profit placed at ${formatted_tp_price}")
#                             except Exception as tp_err:
#                                 add_log(f"⚠️ TP Order Warning: {str(tp_err)}")
#                 else:
#                     try:
#                         ex.create_market_buy_order(chosen_coin, coin_qty); placed_ok = True
#                         add_log(f"✅ Futures Market Buy executed for {chosen_coin} (rules: {matched_rules_str})")
#                         time.sleep(1)
#                         ex.create_order(chosen_coin, 'TAKE_PROFIT_MARKET', 'sell', coin_qty, None, {'stopPrice': formatted_tp_price, 'reduceOnly': True})
#                         add_log(f"🎯 Futures Take Profit set at ${formatted_tp_price}")
#                         ex.create_order(chosen_coin, 'STOP_MARKET', 'sell', coin_qty, None, {'stopPrice': formatted_sl_price, 'reduceOnly': True})
#                         add_log(f"🛡️ Futures Stop Loss set at ${formatted_sl_price}")
#                     except Exception as fut_err:
#                         add_log(f"⚠️ Futures TP/SL note: {str(fut_err)}")

#         user_settings.setdefault("active_trades", []).append({
#             "Symbol": chosen_coin, "Market": market_m,
#             "Entry": f"{c_price:,.6f}", "Amount": f"${amt_usdt}",
#             "TP": f"{tp_val:,.6f}", "SL": f"{sl_val:,.6f}", "Rules": matched_rules_str
#         })
#         save_db(db)
#         add_log(f"📊 Auto trade {rt['trades_today']}/{daily_lim} done for {chosen_coin}"
#                 f"{'' if placed_ok else ' (signal only — no live order)'}.")
#         if rt["trades_today"] >= daily_lim:
#             add_log(f"✅ Aaj ki limit ({daily_lim}) complete. Bot ab kal tak naye auto-trade nahi lega.")

#     except Exception as e:
#         add_log(f"⚠️ Loop Error: {str(e)}")

#     time.sleep(15)
#     st.rerun()

    





















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
import socket
import smtplib
import urllib.request
import urllib.error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
    "timeframe": "1h",
    "ma_enabled": False, "ma_periods": [],
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
        "active_trades": [], "trade_history": [], "signals_feed": [], "signal_history": [], "logs": []
    }

def _backfill_user(cfg):
    strat = cfg.setdefault("strategy", {})
    strat.setdefault("mode", "manual")
    strat.setdefault("exec_mode", "Automated Trading (Bot takes trades & sets TP/SL automatically)")
    strat.setdefault("manual", dict(DEFAULT_MANUAL_STRATEGY))
    for k, v in DEFAULT_MANUAL_STRATEGY.items():
        strat["manual"].setdefault(k, v)
    strat.setdefault("ai_prompt", "")
    strat.setdefault("sl_pct", 2.0)
    strat.setdefault("tp_pct", 4.5)
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
        if chosen_coin in rtf["traded_coins_today"]:
            return False, "coin already used today", fresh
        if not is_signal_only:
            if rtf["trades_today"] >= daily_lim:
                return False, "limit reached", fresh
            rtf["trades_today"] += 1
        else:
            rtf["signals_today"] += 1
        rtf["traded_coins_today"].append(chosen_coin)
        rtf["last_action_epoch"] = now
        save_db(fresh)
        return True, "reserved", fresh
    finally:
        release_lock(lock)

db = load_db()
ACTIVE_USER = None  # login ke baad set hota hai; add_log isi user ke logs me likhta hai

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = ""
if "bot_running" not in st.session_state: st.session_state.bot_running = False

def add_log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    try:
        if ACTIVE_USER and ACTIVE_USER in db.get("settings", {}):
            db["settings"][ACTIVE_USER].setdefault("logs", []).append(line)
        else:
            db.setdefault("logs", []).append(line)
    except Exception:
        db.setdefault("logs", []).append(line)
    save_db(db)

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
    socket.getaddrinfo = _ipv4_only_getaddrinfo  # is call ke liye IPv4 force (safety, HTTPS ke liye bhi)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if 200 <= resp.status < 300:
                return True
            add_log(f"Email Error: Brevo HTTP {resp.status}")
            return False
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", errors="ignore")
        except Exception:
            err_body = ""
        # Brevo error body me exact wajah hoti hai — jaise IP authorize nahi,
        # ya sender email verify nahi, ya key galat. Bot Logs me poora dikhega.
        add_log(f"Email Error: Brevo HTTP {e.code} - {err_body[:300]}")
        return False
    except Exception as e:
        add_log(f"Email Error: {str(e)}")
        return False
    finally:
        socket.getaddrinfo = _orig_getaddrinfo  # turant wapas normal


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

def build_symbol_universe(ex, tickers=None, min_volume=1_000_000, top_n=40, exclude_bases=None):
    exclude_bases = {e.strip().upper() for e in (exclude_bases or []) if e.strip()}
    markets = getattr(ex, "markets", {}) or {}
    universe = []
    for sym, m in markets.items():
        try:
            if not sym.endswith("/USDT"):
                continue
            if m.get("active", True) is False:
                continue
            if m.get("spot", True) is False:
                continue
            base = (m.get("base") or sym.split("/")[0]).upper()
            if base in STABLE_OR_FIAT or base in exclude_bases:
                continue
            if _is_leveraged_token(base):
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
            return [s for s, _ in scored[:top_n]]
    return universe[:top_n]

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

def check_ma_condition(df, periods):
    """
    Real trader jaisa MA bounce:
    Signal candle MA ko TOUCH kare ya thoda break karke wapas MA ke qareeb/upar close kare
    (rejection dikhna chahiye) -> phir Confirmation candle GREEN ho aur signal candle se
    upar close kare (bounce confirm). Multiple MA diye ho to har MA par ye pattern hona
    chahiye (AND logic) — sirf "close upar tha" ki jagah ab "MA pe react karke upar gaya".
    """
    if not periods:
        return False
    if len(df) < max(periods) + 5:
        return False
    sig = df.iloc[-2]; conf = df.iloc[-1]

    # confirmation candle hamesha green ho aur signal se upar close kare
    if not is_green(conf):
        return False
    if float(conf['close']) <= float(sig['close']):
        return False

    for p in periods:
        ma = df['close'].rolling(int(p)).mean()
        ma_sig = ma.iloc[-2]
        if pd.isna(ma_sig):
            return False
        sig_low = float(sig['low']); sig_high = float(sig['high']); sig_close = float(sig['close'])
        # (a) MA signal candle ki wick range ke andar hai -> seedha touch
        touched = sig_low <= ma_sig <= sig_high
        # (b) ya candle MA se thoda neeche gayi thi (wick break) par close wapas MA ke
        #     bahut qareeb / upar aa gaya -> rejection/reclaim
        reclaimed = (sig_low < ma_sig) and (sig_close >= ma_sig * 0.998)
        if not (touched or reclaimed):
            return False
    return True

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
    Support zone = lookback ke 3 sabse neeche wale lows ka average (sirf ek akeli wick
    par depend nahi — real support ek "zone" hota hai jahan price baar baar tiki ho).
    Signal candle us zone ke qareeb aaye, phir confirmation candle green bounce de.
    """
    recent = df.tail(int(lookback))
    if len(recent) < 6: return False
    n = min(3, len(recent))
    support = float(recent['low'].nsmallest(n).mean())
    if support <= 0: return False
    sig = df.iloc[-2]; conf = df.iloc[-1]
    near_support = abs(float(sig['low']) - support) / support * 100 <= tolerance_pct
    bounce = is_green(conf) and float(conf['close']) > float(sig['close'])
    return near_support and bounce

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
    tf = cfg.get("timeframe", "1h")
    ma_periods = cfg.get("ma_periods", []) or [0]
    needed_limit = max(cfg.get("sr_lookback", 50), cfg.get("ob_lookback", 50),
                       cfg.get("trend_lookback", 100), max(ma_periods), 210) + 30
    df = get_ohlcv_df(ex, symbol, tf, limit=int(needed_limit))
    if df is None:
        return False, []
    matched_rules = []; results = []
    if cfg.get("ma_enabled"):
        periods = cfg.get("ma_periods", [])
        if not periods:
            results.append(False)
        else:
            r = check_ma_condition(df, periods); results.append(r)
            if r: matched_rules.append(f"MA({','.join(str(p) for p in periods)})")
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
    if not results:
        return False, []
    return all(results), matched_rules

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
    st.session_state.bot_running = False
    st.rerun()
st.sidebar.markdown("---")
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
        ex_list = ["Binance", "Bybit", "OKX", "KuCoin"]
        cur_ex = user_settings["exchange"].get("name", "Binance")
        ex_choice = st.selectbox("Select Crypto Exchange", ex_list, index=ex_list.index(cur_ex) if cur_ex in ex_list else 0)
        market_type = st.radio("Market Architecture", ["Spot", "Futures (Derivatives)"], index=0 if user_settings["exchange"].get("market") == "Spot" else 1, horizontal=True)
        api_k = st.text_input("API Key", type="password", value=dec_secret(user_settings["exchange"].get("key", "")))
        secret_k = st.text_input("Secret Key", type="password", value=dec_secret(user_settings["exchange"].get("secret", "")))
        demo_chk = st.checkbox("Enable Sandbox / Testnet Mode", value=user_settings["exchange"].get("demo", True))
        st.caption("Tip: exchange par key banate waqt sirf **Spot trading** on karo, **Withdrawal OFF** rakho, aur ho sake to server IP whitelist karo.")
        if st.button("🔌 Connect & Verify API", type="primary", use_container_width=True):
            try:
                ex_config = {'apiKey': api_k, 'secret': secret_k, 'enableRateLimit': True,
                             'options': {'defaultType': 'future' if market_type == "Futures (Derivatives)" else 'spot'}}
                ex = ccxt.binance(ex_config)
                if demo_chk:
                    ex.set_sandbox_mode(True)
                    if market_type == "Futures (Derivatives)":
                        ex.urls['api']['fapiPublic'] = 'https://testnet.binancefuture.com/fapi/v1'
                        ex.urls['api']['fapiPrivate'] = 'https://testnet.binancefuture.com/fapi/v1'
                    else:
                        ex.urls['api']['public'] = 'https://demo-api.binance.com/api/v3'
                        ex.urls['api']['private'] = 'https://demo-api.binance.com/api/v3'
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
        tf_options = ["15m", "1h", "4h", "1d"]
        cur_tf = manual_cfg.get("timeframe", "1h")
        manual_cfg["timeframe"] = st.selectbox("Candle Timeframe", tf_options, index=tf_options.index(cur_tf) if cur_tf in tf_options else 1)
        st.markdown("</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
            manual_cfg["ma_enabled"] = st.checkbox("📈 Enable Moving Average (MA) Filter", value=manual_cfg.get("ma_enabled", False))
            ma_str = st.text_input("MA Periods (comma separated)",
                                   value=",".join(str(p) for p in manual_cfg.get("ma_periods", [])),
                                   placeholder="e.g. 200  ya  44,100,200  (khaali = MA check nahi hoga)",
                                   disabled=not manual_cfg["ma_enabled"])
            try:
                manual_cfg["ma_periods"] = [int(x.strip()) for x in ma_str.split(",") if x.strip()]
            except Exception:
                manual_cfg["ma_periods"] = []
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

        st.markdown("<div class='crypto-card' style='border-left:4px solid #f6465d;'>⚠️ <b>Zaroori:</b> App ko sirf <b>ek hi browser tab</b> me chalao. "
                    "Ek se zyada tab khule honge to har tab apna bot loop chalata hai — is se limit galat lag sakti hai.</div>", unsafe_allow_html=True)

        history = user_settings["trade_history"]
        total_trades = len(history)
        successful_wins = len([h for h in history if "PROFIT" in h.get("status", "")])
        today_pnl = sum([float(h.get("pnl_val", 0)) for h in history if h.get("date") == str(date.today())])

        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        c_m1.metric("Total Trades Executed", total_trades)
        c_m2.metric("Successful Wins", successful_wins)
        c_m3.metric("Today's Net PnL", f"${today_pnl:+,.2f}")
        c_m4.metric("Bot Status", "Running" if st.session_state.bot_running else "Stopped")

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
            if st.button("🚀 START BOT ENGINE", use_container_width=True, type="primary"):
                st.session_state.bot_running = True
                add_log("Apex bot engine started.")
                st.rerun()
        with b_c2:
            if st.button("🛑 STOP BOT", use_container_width=True):
                st.session_state.bot_running = False
                add_log("Apex bot stopped.")
                st.rerun()

    elif dash_tab == "🎯 Active Trades":
        top1, top2 = st.columns([0.7, 0.3])
        with top1:
            st.subheader("🎯 Active Positions")
        with top2:
            if user_settings["active_trades"] and st.button("🗑️ Clear All", use_container_width=True, key="clr_active"):
                user_settings["active_trades"] = []
                save_db(db); st.rerun()

        active_list = user_settings["active_trades"]
        if active_list:
            for idx, trade in enumerate(list(active_list)):
                cc1, cc2 = st.columns([0.9, 0.1])
                with cc1:
                    rules_html = f"<br><span style='color:#848e9c;font-size:12px;'>Rules:</span> <b style='font-size:12px;'>{trade.get('Rules','—')}</b>" if trade.get("Rules") else ""
                    st.markdown(f"""
                    <div class='trade-card'>
                        <div style='display:flex; flex-wrap:wrap; gap:8px; justify-content:space-between; align-items:center;'>
                            <span class='sym-title'>{trade['Symbol']} <span style='color:#848e9c;font-size:12px;'>({trade['Market']})</span></span>
                            <span class='badge-live'>🟢 LIVE</span>
                        </div>
                        <div class='kv-row' style='margin-top:10px;'>
                            <span class='kv'><span class='k'>Entry</span><span class='v' style='color:#3b82f6;'>${trade['Entry']}</span></span>
                            <span class='kv'><span class='k'>Allocated</span><span class='v'>{trade['Amount']}</span></span>
                            <span class='kv'><span class='k'>Take Profit</span><span class='v' style='color:#0ecb81;'>${trade['TP']}</span></span>
                            <span class='kv'><span class='k'>Stop Loss</span><span class='v' style='color:#f6465d;'>${trade['SL']}</span></span>
                        </div>
                        {rules_html}
                    </div>
                    """, unsafe_allow_html=True)
                with cc2:
                    if st.button("❌", key=f"del_trade_{idx}", help="Is card ko hatao"):
                        user_settings["active_trades"].pop(idx)
                        save_db(db); st.rerun()
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

# ==========================================
# BACKGROUND AUTOMATED & EMAIL LOOP
# ==========================================
if st.session_state.bot_running:
    rt = get_runtime(user_settings)
    save_db(db)
    daily_lim = int(user_settings["limits"].get("daily_limit", 1))
    exec_mode_setting = user_settings["strategy"].get("exec_mode", "")
    is_signal_only = "Signal-Only" in exec_mode_setting or "Signal" in exec_mode_setting

    if (not is_signal_only) and rt["trades_today"] >= daily_lim:
        add_log(f"⏳ Daily auto-trade limit reached ({rt['trades_today']}/{daily_lim}). Aaj ke liye paused (kal reset).")
        st.warning(f"⚠️ Daily trade limit {daily_lim} poori ho gayi — aaj {rt['trades_today']} trade ho chuke. Ab kal tak paused.")
        time.sleep(15); st.rerun()

    try:
        ex_cfg = user_settings["exchange"]
        market_m = ex_cfg.get("market", "Spot")
        ex_config = {'apiKey': dec_secret(ex_cfg.get("key")), 'secret': dec_secret(ex_cfg.get("secret")),
                     'enableRateLimit': True,
                     'options': {'defaultType': 'future' if market_m == "Futures (Derivatives)" else 'spot'}}
        ex = ccxt.binance(ex_config)
        if ex_cfg.get("demo"):
            ex.set_sandbox_mode(True)
            if market_m == "Futures (Derivatives)":
                ex.urls['api']['fapiPublic'] = 'https://testnet.binancefuture.com/fapi/v1'
                ex.urls['api']['fapiPrivate'] = 'https://testnet.binancefuture.com/fapi/v1'
            else:
                ex.urls['api']['public'] = 'https://demo-api.binance.com/api/v3'
                ex.urls['api']['private'] = 'https://demo-api.binance.com/api/v3'

        ex.load_markets()
        flt = user_settings.get("filters", DEFAULT_FILTERS)

        # ---- PERF/STABILITY FIX ----
        # Pehle har 15 second me Binance ke SAARE (2000+) coins ka poora ticker data
        # (fetch_tickers) dobara mangwaya jata tha — chhote VPS (1GB RAM) ke liye ye
        # bahut bhaari kaam hai aur crash/restart ki sabse badi wajah tha (jisse
        # session/login "khud logout" jaisa lagta tha). Ab ye data sirf har
        # UNIVERSE_CACHE_TTL second (3 minute) me ek baar refresh hota hai — baaki
        # waqt session me cache se use hota hai. Strategy/behaviour bilkul wahi
        # rehta hai, sirf resource-use kam ho jata hai.
        _now_ts = time.time()
        _cache_key = (curr_user, int(flt.get("universe_min_volume", 1000000)),
                      tuple(sorted(e.upper() for e in flt.get("exclude", []))))
        _cache_fresh = (
            st.session_state.get("_universe_cache_key") == _cache_key
            and (_now_ts - st.session_state.get("_universe_cache_ts", 0)) < UNIVERSE_CACHE_TTL
            and st.session_state.get("_universe_cache")
        )
        if _cache_fresh:
            universe = st.session_state["_universe_cache"]
            all_tickers = st.session_state.get("_tickers_cache")
        else:
            try:
                all_tickers = ex.fetch_tickers()
            except Exception:
                all_tickers = None
            universe = build_symbol_universe(ex, all_tickers,
                                             min_volume=int(flt.get("universe_min_volume", 1000000)),
                                             exclude_bases=flt.get("exclude", []))
            if not universe:
                excl = {e.upper() for e in flt.get("exclude", [])}
                universe = [s for s in ex.symbols
                            if s.endswith('/USDT') and s.split('/')[0].upper() not in STABLE_OR_FIAT
                            and s.split('/')[0].upper() not in excl][:40]
            if not universe:
                universe = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
            st.session_state["_universe_cache"] = universe
            st.session_state["_tickers_cache"] = all_tickers
            st.session_state["_universe_cache_key"] = _cache_key
            st.session_state["_universe_cache_ts"] = _now_ts

        available = [c for c in universe if c not in rt["traded_coins_today"]]
        if not available:
            if is_signal_only:
                rt["traded_coins_today"] = []
                save_db(db)
                available = universe
            else:
                add_log("🔎 Aaj ke available coins khatam. Idling.")
                time.sleep(15); st.rerun()

        strategy_mode = user_settings["strategy"].get("mode", "manual")
        chosen_coin = None; c_price = 0.0; matched_rules_str = ""

        if strategy_mode == "manual":
            manual_cfg = user_settings["strategy"]["manual"]
            sample_pool = available[:25] if len(available) >= 25 else available
            candidates = []
            for coin in sample_pool:
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
                add_log("🔎 Manual scan complete — koi coin saari ticked conditions match nahi kar raha. Idling.")
        else:
            add_log("⚠️ AI Prompt mode selected hai par koi AI evaluation connect nahi — is mode me trade nahi banegi.")

        if chosen_coin is None:
            time.sleep(15); st.rerun()

        # ---- SLOT RESERVE (order se PEHLE) ----
        ok, reason, db = try_reserve_slot(curr_user, chosen_coin, daily_lim, is_signal_only)
        user_settings = db["settings"][curr_user]
        rt = get_runtime(user_settings)

        # ---- EXTRA SAFETY NET ----
        # Chahe kitni bhi tabs/process ya restart ho jaye, trades_today kabhi bhi
        # daily_lim se zyada NAHI hona chahiye. Agar phir bhi (kisi wajah se) ho
        # jaye, is reservation ko turant undo karo — order place hi NAHI hoga, aur
        # limit hamesha exactly wahi rahegi jo user ne set ki hai (2 -> 2, 50 -> 50).
        if ok and not is_signal_only and rt["trades_today"] > daily_lim:
            rt["trades_today"] = daily_lim
            if chosen_coin in rt["traded_coins_today"]:
                rt["traded_coins_today"].remove(chosen_coin)
            save_db(db)
            add_log(f"🛡️ Safety rollback: {chosen_coin} reservation undo ki gayi (limit {daily_lim} already reached tha).")
            ok = False
            reason = "limit reached"

        if not ok:
            if reason == "limit reached":
                add_log(f"⏳ Limit reached ({rt['trades_today']}/{daily_lim}) — {chosen_coin} skip. Paused for today.")
                st.warning(f"⚠️ Daily limit {daily_lim} poori. Ab kal tak paused.")
            else:
                add_log(f"↩️ {chosen_coin} skip ({reason}). Agla coin dekhenge.")
            time.sleep(15); st.rerun()

        if c_price <= 0:
            try:
                ohlcv = ex.fetch_ohlcv(chosen_coin, timeframe='1m', limit=1)
                if ohlcv: c_price = float(ohlcv[0][4])
            except Exception:
                c_price = 1.0

        amt_usdt = float(user_settings["limits"]["trade_amount"])
        try:
            coin_qty = float(ex.amount_to_precision(chosen_coin, amt_usdt / c_price))
        except Exception:
            coin_qty = amt_usdt / c_price

        tp_p = user_settings["strategy"]["tp_pct"]; sl_p = user_settings["strategy"]["sl_pct"]
        tp_val = c_price * (1 + tp_p / 100); sl_val = c_price * (1 - sl_p / 100)

        current_time_str = datetime.now().strftime("%I:%M:%S %p")
        full_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp_epoch = datetime.now().timestamp()

        # per-user signals feed (24h se purane -> signal_history)
        us_feed = user_settings.setdefault("signals_feed", [])
        us_hist = user_settings.setdefault("signal_history", [])
        active_signals = []
        for sig in us_feed:
            if (timestamp_epoch - sig.get("timestamp_epoch", timestamp_epoch)) >= 86400:
                if sig not in us_hist:
                    us_hist.insert(0, sig)
            else:
                active_signals.append(sig)
        user_settings["signals_feed"] = active_signals

        new_signal = {
            "id": f"{chosen_coin}_{int(timestamp_epoch)}",
            "time": current_time_str, "full_timestamp": full_ts, "timestamp_epoch": timestamp_epoch,
            "symbol": chosen_coin,
            "strategy": "Manual Rule Engine" if strategy_mode == "manual" else "AI Prompt Engine",
            "rules": matched_rules_str, "entry": c_price, "tp": tp_val, "sl": sl_val,
            "type": "Signal Only" if is_signal_only else "Executed Trade"
        }
        user_settings["signals_feed"].insert(0, new_signal)
        save_db(db)

        email_cfg = user_settings.get("email", {})
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

        # -------- SIGNAL-ONLY --------
        if is_signal_only:
            add_log(f"📡 Signal #{rt['signals_today']} generated for {chosen_coin} (rules: {matched_rules_str}).")
            time.sleep(15); st.rerun()

        # -------- AUTO TRADE --------
        placed_ok = False
        if "Automated Trading" in exec_mode_setting:
            if not (ex_cfg.get("connected") and ex_cfg.get("key")):
                add_log(f"⚠️ {chosen_coin}: exchange not connected — real order skip, signal recorded. "
                        f"(Slot consume ho gaya taake limit safe rahe.)")
            else:
                try:
                    formatted_tp_price = float(ex.price_to_precision(chosen_coin, tp_val))
                    formatted_sl_price = float(ex.price_to_precision(chosen_coin, sl_val))
                except Exception:
                    formatted_tp_price = tp_val; formatted_sl_price = sl_val

                if market_m == "Spot":
                    try:
                        buy_res = ex.create_market_buy_order(chosen_coin, coin_qty)
                        placed_ok = True
                        add_log(f"✅ Spot Market Buy Executed for {chosen_coin} (rules: {matched_rules_str})")
                    except Exception as buy_err:
                        add_log(f"❌ Buy Order Error: {str(buy_err)}"); buy_res = None
                    if buy_res:
                        time.sleep(1.5)
                        base_ccy = chosen_coin.split('/')[0]; sell_qty = coin_qty
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
                                oco_fn({'symbol': chosen_coin.replace('/', ''), 'side': 'SELL',
                                        'quantity': ex.amount_to_precision(chosen_coin, sell_qty),
                                        'price': ex.price_to_precision(chosen_coin, formatted_tp_price),
                                        'stopPrice': ex.price_to_precision(chosen_coin, formatted_sl_price),
                                        'stopLimitPrice': ex.price_to_precision(chosen_coin, sl_limit_price),
                                        'stopLimitTimeInForce': 'GTC'})
                                add_log(f"🛡️ OCO placed — TP ${formatted_tp_price} / SL ${formatted_sl_price}")
                                oco_done = True
                            except Exception as oco_err:
                                add_log(f"⚠️ OCO not available ({str(oco_err)[:70]}), trying separate SL/TP...")
                        if not oco_done:
                            try:
                                ex.create_order(chosen_coin, 'STOP_LOSS_LIMIT', 'sell', sell_qty, sl_limit_price, {'stopPrice': formatted_sl_price})
                                add_log(f"🛡️ Stop Loss placed at trigger ${formatted_sl_price}")
                            except Exception:
                                try:
                                    ex.create_order(chosen_coin, 'STOP_LOSS', 'sell', sell_qty, None, {'stopPrice': formatted_sl_price})
                                    add_log(f"🛡️ Stop Loss (Market) placed at trigger ${formatted_sl_price}")
                                except Exception as sl_fallback_err:
                                    add_log(f"⚠️ Stop Loss Order Warning: {str(sl_fallback_err)}")
                            try:
                                bal2 = ex.fetch_balance()
                                free2 = float(bal2['free'].get(base_ccy, 0) or 0)
                                tp_qty = float(ex.amount_to_precision(chosen_coin, free2)) if free2 > 0 else 0
                                if tp_qty > 0:
                                    ex.create_limit_sell_order(chosen_coin, tp_qty, formatted_tp_price)
                                    add_log(f"🎯 Take Profit placed at ${formatted_tp_price}")
                            except Exception as tp_err:
                                add_log(f"⚠️ TP Order Warning: {str(tp_err)}")
                else:
                    try:
                        ex.create_market_buy_order(chosen_coin, coin_qty); placed_ok = True
                        add_log(f"✅ Futures Market Buy executed for {chosen_coin} (rules: {matched_rules_str})")
                        time.sleep(1)
                        ex.create_order(chosen_coin, 'TAKE_PROFIT_MARKET', 'sell', coin_qty, None, {'stopPrice': formatted_tp_price, 'reduceOnly': True})
                        add_log(f"🎯 Futures Take Profit set at ${formatted_tp_price}")
                        ex.create_order(chosen_coin, 'STOP_MARKET', 'sell', coin_qty, None, {'stopPrice': formatted_sl_price, 'reduceOnly': True})
                        add_log(f"🛡️ Futures Stop Loss set at ${formatted_sl_price}")
                    except Exception as fut_err:
                        add_log(f"⚠️ Futures TP/SL note: {str(fut_err)}")

        user_settings.setdefault("active_trades", []).append({
            "Symbol": chosen_coin, "Market": market_m,
            "Entry": f"{c_price:,.6f}", "Amount": f"${amt_usdt}",
            "TP": f"{tp_val:,.6f}", "SL": f"{sl_val:,.6f}", "Rules": matched_rules_str
        })
        save_db(db)
        add_log(f"📊 Auto trade {rt['trades_today']}/{daily_lim} done for {chosen_coin}"
                f"{'' if placed_ok else ' (signal only — no live order)'}.")
        if rt["trades_today"] >= daily_lim:
            add_log(f"✅ Aaj ki limit ({daily_lim}) complete. Bot ab kal tak naye auto-trade nahi lega.")

    except Exception as e:
        add_log(f"⚠️ Loop Error: {str(e)}")

    time.sleep(15)
    st.rerun()

















    

# import streamlit as st
# import ccxt
# import pandas as pd
# import numpy as np
# import time
# import os
# import json
# import hashlib
# import hmac
# import secrets
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from datetime import datetime, date

# # Optional strong encryption for API keys (pip install cryptography)
# try:
#     from cryptography.fernet import Fernet
#     _CRYPTO_OK = True
# except Exception:
#     _CRYPTO_OK = False

# # ==========================================
# # PAGE SETUP & STYLING
# # ==========================================
# favicon_path = "apex-favicon.png" if os.path.exists("apex-favicon.png") else "⚡"
# logo_path = "apex-logo.png" if os.path.exists("apex-logo.png") else None

# st.set_page_config(
#     page_title="Apex Trading - Pro Terminal",
#     page_icon=favicon_path if os.path.exists("apex-favicon.png") else "⚡",
#     layout="wide"
# )

# st.markdown("""
#     <style>
#     .stApp { background-color: #0b0e11; color: #eaecef; }
#     .crypto-card {
#         background: #181a20; border: 1px solid #2b313a; border-radius: 12px;
#         padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
#     }
#     .badge-live {
#         background-color: rgba(14, 203, 129, 0.15); color: #0ecb81;
#         padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold;
#         border: 1px solid #0ecb81;
#     }
#     .badge-signal {
#         background-color: rgba(240, 185, 11, 0.15); color: #fcd535;
#         padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold;
#         border: 1px solid #fcd535;
#     }
#     .rule-tag {
#         display:inline-block; background:#0ecb8122; border:1px solid #0ecb81; color:#0ecb81;
#         padding:3px 10px; border-radius:6px; font-size:12px; margin-right:6px; margin-bottom:6px;
#     }
#     .sig-card {
#         background: linear-gradient(180deg,#181a20 0%, #14161c 100%);
#         border: 1px solid #2b313a; border-left: 4px solid #fcd535;
#         border-radius: 12px; padding: 14px 18px; margin-bottom: 10px;
#     }
#     .trade-card {
#         background: linear-gradient(180deg,#181a20 0%, #14161c 100%);
#         border: 1px solid #2b313a; border-left: 4px solid #0ecb81;
#         border-radius: 12px; padding: 14px 18px; margin-bottom: 10px;
#     }
#     .kv { display:inline-block; margin-right:18px; }
#     .kv .k { color:#848e9c; font-size:11px; display:block; }
#     .kv .v { font-size:15px; font-weight:bold; }
#     .sym-title { color:#fcd535; font-size:18px; font-weight:bold; margin:0; }
#     </style>
# """, unsafe_allow_html=True)

# # ==========================================
# # CONFIG / PATHS (env se override ho sakte hain — VPS par persistent disk ke liye useful)
# # ==========================================
# DB_FILE = os.environ.get("APEX_DB_FILE", "database.json")
# LOCK_FILE = os.environ.get("APEX_LOCK_FILE", "apex.lock")
# KEY_FILE = os.environ.get("APEX_KEY_FILE", "apex_secret.key")
# SECRET_ENV = "APEX_SECRET_KEY"       # live par ye env var set karo (sabse safe)
# MIN_ACTION_GAP_SEC = 10              # do actions ke beech gap (rapid-fire / multi-tab race rokne ke liye)
# STALE_LOCK_SEC = 25
# UNIVERSE_CACHE_TTL = 180             # seconds — market/tickers data itni der cache rehta hai (chhote VPS ka RAM/CPU bachane ke liye)

# # ==========================================
# # ENCRYPTION (API keys / secrets at rest)
# # ==========================================
# def _load_or_create_fernet():
#     if not _CRYPTO_OK:
#         return None
#     key = os.environ.get(SECRET_ENV)
#     if key:
#         try:
#             return Fernet(key.encode() if isinstance(key, str) else key)
#         except Exception:
#             pass
#     if os.path.exists(KEY_FILE):
#         try:
#             with open(KEY_FILE, "rb") as f:
#                 return Fernet(f.read().strip())
#         except Exception:
#             pass
#     k = Fernet.generate_key()
#     try:
#         with open(KEY_FILE, "wb") as f:
#             f.write(k)
#     except Exception:
#         pass
#     return Fernet(k)

# FERNET = _load_or_create_fernet()
# ENC_PREFIX = "enc::"

# def enc_secret(plain):
#     """Plain text ko encrypt karke store karo. Pehle se encrypted ho to waise hi rehne do."""
#     if not plain:
#         return ""
#     if not isinstance(plain, str):
#         plain = str(plain)
#     if plain.startswith(ENC_PREFIX):
#         return plain
#     if FERNET is None:
#         return plain  # cryptography install nahi — plain (UI me warning dikhega)
#     try:
#         return ENC_PREFIX + FERNET.encrypt(plain.encode()).decode()
#     except Exception:
#         return plain

# def dec_secret(stored):
#     """Encrypted value ko wapas plain me karo. Legacy plain value ho to waise hi de do."""
#     if not stored or not isinstance(stored, str):
#         return stored or ""
#     if not stored.startswith(ENC_PREFIX):
#         return stored  # legacy plain
#     if FERNET is None:
#         return ""
#     try:
#         return FERNET.decrypt(stored[len(ENC_PREFIX):].encode()).decode()
#     except Exception:
#         return ""

# # ==========================================
# # PASSWORD HASHING (login/signup)
# # ==========================================
# def hash_password(pw):
#     salt = secrets.token_hex(16)
#     h = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200000).hex()
#     return f"pbkdf2${salt}${h}"

# def verify_password(pw, stored):
#     if not stored:
#         return False
#     if isinstance(stored, str) and stored.startswith("pbkdf2$"):
#         try:
#             _, salt, h = stored.split("$", 2)
#             calc = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200000).hex()
#             return hmac.compare_digest(calc, h)
#         except Exception:
#             return False
#     # legacy plain password (purane accounts) — match ho to login ke baad hash me upgrade kar denge
#     return hmac.compare_digest(str(pw), str(stored))

# # ==========================================
# # DATABASE
# # ==========================================
# DEFAULT_MANUAL_STRATEGY = {
#     "timeframe": "1h",
#     "ma_enabled": False, "ma_periods": [],
#     "rsi_enabled": False, "rsi_min": 30, "rsi_max": 45,
#     "sr_enabled": False, "sr_lookback": 50, "sr_tolerance_pct": 1.0,
#     "ob_enabled": False, "ob_lookback": 50,
#     "vol_enabled": False, "vol_min_usdt": 500000,
#     "trend_enabled": False, "trend_lookback": 100, "trend_touches": 3,
# }

# DEFAULT_RUNTIME = {
#     "trade_date": "", "trades_today": 0, "signals_today": 0,
#     "traded_coins_today": [], "last_action_epoch": 0
# }

# DEFAULT_FILTERS = {
#     "universe_min_volume": 1000000,   # scan sirf itne 24h USDT volume+ wale coins par
#     "exclude": []                     # user-defined coins jo kabhi trade na hon (jaise QKC)
# }

# # Har user ka apna data yahan — live par ek user ka doosre se alag aur persistent
# USER_BUCKETS = ["active_trades", "trade_history", "signals_feed", "signal_history", "logs"]

# def _blank_user_settings():
#     return {
#         "exchange": {"name": "Binance", "market": "Spot", "key": "", "secret": "", "demo": True, "connected": False},
#         "strategy": {
#             "mode": "manual",
#             "exec_mode": "Automated Trading (Bot takes trades & sets TP/SL automatically)",
#             "ai_prompt": "",
#             "manual": dict(DEFAULT_MANUAL_STRATEGY),
#             "sl_pct": 2.0, "tp_pct": 4.5
#         },
#         "limits": {"campaign_days": 1, "daily_limit": 1, "trade_amount": 100.0},
#         "filters": dict(DEFAULT_FILTERS),
#         "runtime": dict(DEFAULT_RUNTIME),
#         "email": {"enabled": True, "host": "smtp.gmail.com", "port": 587, "sender": "", "password": "", "receiver": ""},
#         "active_trades": [], "trade_history": [], "signals_feed": [], "signal_history": [], "logs": []
#     }

# def _backfill_user(cfg):
#     strat = cfg.setdefault("strategy", {})
#     strat.setdefault("mode", "manual")
#     strat.setdefault("exec_mode", "Automated Trading (Bot takes trades & sets TP/SL automatically)")
#     strat.setdefault("manual", dict(DEFAULT_MANUAL_STRATEGY))
#     for k, v in DEFAULT_MANUAL_STRATEGY.items():
#         strat["manual"].setdefault(k, v)
#     strat.setdefault("ai_prompt", "")
#     strat.setdefault("sl_pct", 2.0)
#     strat.setdefault("tp_pct", 4.5)
#     cfg.setdefault("exchange", {"name": "Binance", "market": "Spot", "key": "", "secret": "", "demo": True, "connected": False})
#     cfg.setdefault("limits", {"campaign_days": 1, "daily_limit": 1, "trade_amount": 100.0})
#     flt = cfg.setdefault("filters", dict(DEFAULT_FILTERS))
#     for k, v in DEFAULT_FILTERS.items():
#         flt.setdefault(k, v)
#     rt = cfg.setdefault("runtime", dict(DEFAULT_RUNTIME))
#     for k, v in DEFAULT_RUNTIME.items():
#         rt.setdefault(k, v)
#     cfg.setdefault("email", {"enabled": True, "host": "smtp.gmail.com", "port": 587, "sender": "", "password": "", "receiver": ""})
#     for b in USER_BUCKETS:
#         cfg.setdefault(b, [])

# def load_db():
#     if not os.path.exists(DB_FILE):
#         default_data = {"users": {}, "settings": {"admin": _blank_user_settings()}, "logs": []}
#         with open(DB_FILE, "w") as f:
#             json.dump(default_data, f, indent=4)

#     with open(DB_FILE, "r") as f:
#         try:
#             data = json.load(f)
#         except json.JSONDecodeError:
#             data = {"users": {}, "settings": {}, "logs": []}

#     data.setdefault("users", {})
#     data.setdefault("settings", {})
#     data.setdefault("logs", [])
#     if "admin" not in data["settings"]:
#         data["settings"]["admin"] = _blank_user_settings()
#     for uname, cfg in data["settings"].items():
#         _backfill_user(cfg)
#     return data

# def save_db(db):
#     """Atomic write — crash ya restart par file corrupt/khali na ho, data safe rahe."""
#     tmp = DB_FILE + ".tmp"
#     with open(tmp, "w") as f:
#         json.dump(db, f, indent=4)
#     os.replace(tmp, DB_FILE)

# def get_runtime(user_settings):
#     rt = user_settings.setdefault("runtime", dict(DEFAULT_RUNTIME))
#     for k, v in DEFAULT_RUNTIME.items():
#         rt.setdefault(k, v)
#     today_str = str(date.today())
#     if rt.get("trade_date") != today_str:
#         rt["trade_date"] = today_str
#         rt["trades_today"] = 0
#         rt["signals_today"] = 0
#         rt["traded_coins_today"] = []
#         rt["last_action_epoch"] = 0
#     return rt

# # ------------------------------------------------------------------
# # CROSS-TAB / CROSS-PROCESS FILE LOCK
# # ------------------------------------------------------------------
# def acquire_lock(timeout=8.0):
#     start = time.time()
#     while True:
#         try:
#             fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_RDWR)
#             try:
#                 os.write(fd, str(os.getpid()).encode())
#             except Exception:
#                 pass
#             return fd
#         except FileExistsError:
#             try:
#                 if time.time() - os.path.getmtime(LOCK_FILE) > STALE_LOCK_SEC:
#                     os.remove(LOCK_FILE)
#                     continue
#             except FileNotFoundError:
#                 continue
#             except Exception:
#                 pass
#             if time.time() - start > timeout:
#                 return None
#             time.sleep(0.2)

# def release_lock(fd):
#     if fd is None:
#         return
#     try:
#         os.close(fd)
#     except Exception:
#         pass
#     try:
#         os.remove(LOCK_FILE)
#     except Exception:
#         pass

# def try_reserve_slot(curr_user, chosen_coin, daily_lim, is_signal_only, min_gap=MIN_ACTION_GAP_SEC):
#     """Order se PEHLE slot reserve (lock ke andar): limit + duplicate-coin + cooldown check. Returns (ok, reason, fresh_db)."""
#     lock = acquire_lock()
#     if lock is None:
#         return False, "busy (dusra tab active)", load_db()
#     try:
#         fresh = load_db()
#         us = fresh["settings"].get(curr_user)
#         if us is None:
#             return False, "user missing", fresh
#         rtf = get_runtime(us)
#         now = time.time()
#         if now - float(rtf.get("last_action_epoch", 0)) < min_gap:
#             return False, "cooldown", fresh
#         if chosen_coin in rtf["traded_coins_today"]:
#             return False, "coin already used today", fresh
#         if not is_signal_only:
#             if rtf["trades_today"] >= daily_lim:
#                 return False, "limit reached", fresh
#             rtf["trades_today"] += 1
#         else:
#             rtf["signals_today"] += 1
#         rtf["traded_coins_today"].append(chosen_coin)
#         rtf["last_action_epoch"] = now
#         save_db(fresh)
#         return True, "reserved", fresh
#     finally:
#         release_lock(lock)

# db = load_db()
# ACTIVE_USER = None  # login ke baad set hota hai; add_log isi user ke logs me likhta hai

# if "logged_in" not in st.session_state: st.session_state.logged_in = False
# if "username" not in st.session_state: st.session_state.username = ""
# if "bot_running" not in st.session_state: st.session_state.bot_running = False

# def add_log(msg):
#     ts = datetime.now().strftime("%H:%M:%S")
#     line = f"[{ts}] {msg}"
#     try:
#         if ACTIVE_USER and ACTIVE_USER in db.get("settings", {}):
#             db["settings"][ACTIVE_USER].setdefault("logs", []).append(line)
#         else:
#             db.setdefault("logs", []).append(line)
#     except Exception:
#         db.setdefault("logs", []).append(line)
#     save_db(db)

# def send_email_alert(subject, body_html, email_cfg):
#     if not email_cfg.get("enabled") or not email_cfg.get("sender") or not email_cfg.get("receiver"):
#         return False
#     try:
#         msg = MIMEMultipart('alternative')
#         msg['From'] = email_cfg["sender"]; msg['To'] = email_cfg["receiver"]; msg['Subject'] = subject
#         msg.attach(MIMEText(body_html, 'html'))
#         server = smtplib.SMTP(email_cfg["host"], int(email_cfg["port"]))
#         server.starttls()
#         server.login(email_cfg["sender"], dec_secret(email_cfg.get("password")))
#         server.sendmail(email_cfg["sender"], email_cfg["receiver"], msg.as_string())
#         server.quit()
#         return True
#     except Exception as e:
#         add_log(f"Email Error: {str(e)}")
#         return False

# # ------------------------------------------------------------------
# # COIN UNIVERSE FILTER
# # Sirf real, liquid, tradeable USDT spot coins. Stablecoins/fiat, leveraged tokens,
# # inactive/delisted pairs, aur user ke exclude-list wale coins (jaise Monitoring-Tag) hata dete hain.
# # ------------------------------------------------------------------
# STABLE_OR_FIAT = {
#     "USDT", "USDC", "BUSD", "FDUSD", "TUSD", "DAI", "USDP", "PAX", "PYUSD", "USDD",
#     "AEUR", "EUR", "EURI", "EURT", "GBP", "AUD", "BRL", "TRY", "RUB", "UAH", "NGN",
#     "IDRT", "ZAR", "ARS", "BIDR", "VAI", "UST", "USTC", "GUSD", "SUSD", "XUSD", "BVND"
# }

# def _is_leveraged_token(base):
#     b = (base or "").upper()
#     if "BULL" in b or "BEAR" in b:
#         return True
#     if len(b) >= 5 and (b.endswith("UP") or b.endswith("DOWN")):
#         return True
#     return False

# def build_symbol_universe(ex, tickers=None, min_volume=1_000_000, top_n=40, exclude_bases=None):
#     exclude_bases = {e.strip().upper() for e in (exclude_bases or []) if e.strip()}
#     markets = getattr(ex, "markets", {}) or {}
#     universe = []
#     for sym, m in markets.items():
#         try:
#             if not sym.endswith("/USDT"):
#                 continue
#             if m.get("active", True) is False:
#                 continue
#             if m.get("spot", True) is False:
#                 continue
#             base = (m.get("base") or sym.split("/")[0]).upper()
#             if base in STABLE_OR_FIAT or base in exclude_bases:
#                 continue
#             if _is_leveraged_token(base):
#                 continue
#             universe.append(sym)
#         except Exception:
#             continue

#     if tickers:
#         scored = []
#         for sym in universe:
#             t = tickers.get(sym) or {}
#             try:
#                 qv = float(t.get("quoteVolume") or 0)
#             except Exception:
#                 qv = 0.0
#             if qv >= min_volume:
#                 scored.append((sym, qv))
#         scored.sort(key=lambda x: x[1], reverse=True)
#         if scored:
#             return [s for s, _ in scored[:top_n]]
#     return universe[:top_n]

# # ==========================================
# # STRATEGY / INDICATOR ENGINE  (signal + confirmation candle)
# # ==========================================
# def get_ohlcv_df(ex, symbol, timeframe, limit=250):
#     try:
#         ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
#         if not ohlcv or len(ohlcv) < 30:
#             return None
#         return pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
#     except Exception:
#         return None

# def is_green(row):
#     return float(row['close']) > float(row['open'])

# def calc_rsi(close_series, period=14):
#     delta = close_series.diff()
#     gain = delta.clip(lower=0); loss = -delta.clip(upper=0)
#     avg_gain = gain.rolling(period).mean(); avg_loss = loss.rolling(period).mean()
#     rs = avg_gain / avg_loss.replace(0, np.nan)
#     return 100 - (100 / (1 + rs))

# def check_ma_condition(df, periods):
#     if not periods: return False
#     if len(df) < max(periods) + 3: return False
#     sig = df.iloc[-2]; conf = df.iloc[-1]
#     for p in periods:
#         ma = df['close'].rolling(int(p)).mean()
#         ma_sig = ma.iloc[-2]; ma_conf = ma.iloc[-1]
#         if pd.isna(ma_sig) or pd.isna(ma_conf): return False
#         if float(sig['close']) < float(ma_sig): return False
#         if float(conf['close']) < float(ma_conf): return False
#     return is_green(sig) and is_green(conf)

# def check_rsi_condition(df, rsi_min, rsi_max, period=14):
#     if len(df) < period + 3: return False
#     rsi = calc_rsi(df['close'], period)
#     rsi_sig = rsi.iloc[-2]; rsi_conf = rsi.iloc[-1]
#     if pd.isna(rsi_sig) or pd.isna(rsi_conf): return False
#     conf = df.iloc[-1]
#     in_range = rsi_min <= float(rsi_sig) <= rsi_max
#     momentum_up = float(rsi_conf) >= float(rsi_sig)
#     return in_range and momentum_up and is_green(conf)

# def check_support_condition(df, lookback, tolerance_pct):
#     recent = df.tail(int(lookback))
#     if len(recent) < 6: return False
#     support = float(recent['low'].min())
#     if support <= 0: return False
#     sig = df.iloc[-2]; conf = df.iloc[-1]
#     near_support = abs(float(sig['low']) - support) / support * 100 <= tolerance_pct
#     bounce = is_green(conf) and float(conf['close']) > float(sig['close'])
#     return near_support and bounce

# def check_order_block_condition(df, lookback, tolerance_pct=1.0):
#     recent = df.tail(int(lookback)).reset_index(drop=True)
#     if len(recent) < 25: return False
#     body = (recent['close'] - recent['open']).abs()
#     avg_body = body.rolling(20).mean()
#     ob_zone = None
#     for i in range(20, len(recent)):
#         is_bullish = recent['close'].iloc[i] > recent['open'].iloc[i]
#         is_impulse = (not pd.isna(avg_body.iloc[i])) and body.iloc[i] > 1.8 * avg_body.iloc[i]
#         if is_bullish and is_impulse and i > 0:
#             prev = recent.iloc[i - 1]
#             if prev['close'] < prev['open']:
#                 ob_zone = (float(prev['low']), float(prev['high']))
#     if ob_zone is None: return False
#     zone_low, zone_high = ob_zone
#     zone_high_padded = zone_high * (1 + tolerance_pct / 100)
#     sig = df.iloc[-2]; conf = df.iloc[-1]
#     tapped = (zone_low <= float(sig['low']) <= zone_high_padded) or (zone_low <= float(sig['close']) <= zone_high_padded)
#     reaction = is_green(conf) and float(conf['close']) > float(sig['close'])
#     return tapped and reaction

# def check_volume_condition(ex, symbol, min_usdt):
#     try:
#         ticker = ex.fetch_ticker(symbol)
#         return float(ticker.get('quoteVolume') or 0) >= float(min_usdt)
#     except Exception:
#         return False

# def check_trendline_condition(df, lookback, touches_required, tolerance_pct=1.5):
#     recent = df.tail(int(lookback)).reset_index(drop=True)
#     if len(recent) < 20: return False
#     lows_idx = []
#     for i in range(2, len(recent) - 2):
#         low = recent['low'].iloc[i]
#         if (low < recent['low'].iloc[i - 1] and low < recent['low'].iloc[i - 2] and
#                 low < recent['low'].iloc[i + 1] and low < recent['low'].iloc[i + 2]):
#             lows_idx.append(i)
#     if len(lows_idx) < touches_required: return False
#     xs = np.array(lows_idx[-int(touches_required):])
#     ys = recent['low'].iloc[xs].values
#     slope, intercept = np.polyfit(xs, ys, 1)
#     if slope <= 0: return False
#     sig_pos = len(recent) - 2
#     trend_val = slope * sig_pos + intercept
#     if trend_val <= 0: return False
#     sig = df.iloc[-2]; conf = df.iloc[-1]
#     near_line = abs(float(sig['low']) - trend_val) / trend_val * 100 <= tolerance_pct
#     bounce = is_green(conf) and float(conf['close']) > float(sig['close'])
#     return near_line and bounce

# def evaluate_manual_strategy(ex, symbol, cfg):
#     tf = cfg.get("timeframe", "1h")
#     ma_periods = cfg.get("ma_periods", []) or [0]
#     needed_limit = max(cfg.get("sr_lookback", 50), cfg.get("ob_lookback", 50),
#                        cfg.get("trend_lookback", 100), max(ma_periods), 210) + 30
#     df = get_ohlcv_df(ex, symbol, tf, limit=int(needed_limit))
#     if df is None:
#         return False, []
#     matched_rules = []; results = []
#     if cfg.get("ma_enabled"):
#         periods = cfg.get("ma_periods", [])
#         if not periods:
#             results.append(False)
#         else:
#             r = check_ma_condition(df, periods); results.append(r)
#             if r: matched_rules.append(f"MA({','.join(str(p) for p in periods)})")
#     if cfg.get("rsi_enabled"):
#         r = check_rsi_condition(df, cfg.get("rsi_min", 30), cfg.get("rsi_max", 45)); results.append(r)
#         if r: matched_rules.append(f"RSI({cfg.get('rsi_min')}-{cfg.get('rsi_max')})")
#     if cfg.get("sr_enabled"):
#         r = check_support_condition(df, cfg.get("sr_lookback", 50), cfg.get("sr_tolerance_pct", 1.0)); results.append(r)
#         if r: matched_rules.append("Support Bounce")
#     if cfg.get("ob_enabled"):
#         r = check_order_block_condition(df, cfg.get("ob_lookback", 50)); results.append(r)
#         if r: matched_rules.append("Order Block")
#     if cfg.get("vol_enabled"):
#         r = check_volume_condition(ex, symbol, cfg.get("vol_min_usdt", 500000)); results.append(r)
#         if r: matched_rules.append("Volume Filter")
#     if cfg.get("trend_enabled"):
#         r = check_trendline_condition(df, cfg.get("trend_lookback", 100), cfg.get("trend_touches", 3)); results.append(r)
#         if r: matched_rules.append("Trendline Bounce")
#     if not results:
#         return False, []
#     return all(results), matched_rules

# # ==========================================
# # AUTHENTICATION
# # ==========================================
# if not st.session_state.logged_in:
#     st.markdown("<br><br>", unsafe_allow_html=True)
#     col_a, col_b, col_c = st.columns([1, 1.4, 1])
#     with col_b:
#         st.markdown("<div class='crypto-card' style='text-align: center;'>", unsafe_allow_html=True)
#         if logo_path and os.path.exists(logo_path): st.image(logo_path, width=150)
#         st.markdown("<h1>⚡ Apex Trading</h1>", unsafe_allow_html=True)
#         st.markdown("<p style='color: #848e9c;'>Secure Multi-Exchange Algorithmic Platform</p><br>", unsafe_allow_html=True)
#         if not _CRYPTO_OK:
#             st.warning("⚠️ 'cryptography' install nahi hai — API keys encrypt nahi hongi. Terminal me: pip install cryptography")
#         tab_l, tab_s = st.tabs(["🔐 Login", "📝 Sign Up"])
#         with tab_l:
#             l_user = st.text_input("Username", key="l_user")
#             l_pass = st.text_input("Password", type="password", key="l_pass")
#             st.markdown("<br>", unsafe_allow_html=True)
#             if st.button("Access Terminal", use_container_width=True, type="primary"):
#                 users = db["users"]
#                 if l_user in users and verify_password(l_pass, users[l_user].get("password", "")):
#                     # legacy plain password -> hash me upgrade
#                     if not str(users[l_user].get("password", "")).startswith("pbkdf2$"):
#                         users[l_user]["password"] = hash_password(l_pass)
#                     st.session_state.logged_in = True
#                     st.session_state.username = l_user
#                     if l_user not in db["settings"]:
#                         db["settings"][l_user] = _blank_user_settings()
#                     save_db(db)
#                     st.success("✅ Login successful!"); st.rerun()
#                 else:
#                     st.error("❌ Invalid username or password.")
#         with tab_s:
#             s_user = st.text_input("Choose Username", key="s_user")
#             s_pass = st.text_input("Choose Password", type="password", key="s_pass")
#             st.markdown("<br>", unsafe_allow_html=True)
#             if st.button("Create Account & Login", use_container_width=True):
#                 users = db["users"]
#                 if s_user in users:
#                     st.warning("⚠️ Username already exists.")
#                 elif not s_user or not s_pass:
#                     st.warning("⚠️ Fields cannot be blank.")
#                 else:
#                     users[s_user] = {"password": hash_password(s_pass), "created": str(date.today())}
#                     db["settings"][s_user] = _blank_user_settings()
#                     save_db(db)
#                     st.session_state.logged_in = True
#                     st.session_state.username = s_user
#                     st.success("✅ Account created!"); st.rerun()
#         st.markdown("</div>", unsafe_allow_html=True)
#     st.stop()

# curr_user = st.session_state.username
# ACTIVE_USER = curr_user
# user_settings = db["settings"].setdefault(curr_user, _blank_user_settings())
# _backfill_user(user_settings)
# get_runtime(user_settings)
# save_db(db)

# # ==========================================
# # SIDEBAR
# # ==========================================
# if logo_path and os.path.exists(logo_path):
#     st.sidebar.image(logo_path, width=140)
# st.sidebar.markdown(f"""
#     <div style='padding: 12px; background: #181a20; border-radius: 10px; border: 1px solid #2b313a; margin-top: 10px; margin-bottom: 15px;'>
#         <div style='color: #848e9c; font-size: 11px;'>APEX TRADER</div>
#         <div style='color: #fcd535; font-size: 16px; font-weight: bold;'>👤 {curr_user}</div>
#     </div>
# """, unsafe_allow_html=True)
# if st.sidebar.button("🚪 Logout", use_container_width=True):
#     st.session_state.logged_in = False
#     st.session_state.bot_running = False
#     st.rerun()
# st.sidebar.markdown("---")
# config_menu = st.sidebar.radio(
#     "Configs",
#     ["📊 Dashboard", "🔌 Exchange Integration", "⚙️ Strategy Studio", "📦 Limitation & Campaign"],
#     label_visibility="collapsed"
# )

# # ==========================================
# # 1. EXCHANGE INTEGRATION
# # ==========================================
# if config_menu == "🔌 Exchange Integration":
#     st.title("🔌 Exchange API Integration")
#     st.markdown("---")
#     if _CRYPTO_OK:
#         st.markdown("<div class='crypto-card' style='border-left:4px solid #0ecb81;'>🔐 API key aur secret database me <b>encrypted</b> save hote hain (plain nahi).</div>", unsafe_allow_html=True)
#     else:
#         st.markdown("<div class='crypto-card' style='border-left:4px solid #f6465d;'>⚠️ <b>cryptography</b> install nahi — keys abhi plain save hongi. <code>pip install cryptography</code> chala kar dobara connect karo.</div>", unsafe_allow_html=True)
#     col1, col2 = st.columns([1.3, 1], gap="large")
#     with col1:
#         st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#         ex_list = ["Binance", "Bybit", "OKX", "KuCoin"]
#         cur_ex = user_settings["exchange"].get("name", "Binance")
#         ex_choice = st.selectbox("Select Crypto Exchange", ex_list, index=ex_list.index(cur_ex) if cur_ex in ex_list else 0)
#         market_type = st.radio("Market Architecture", ["Spot", "Futures (Derivatives)"], index=0 if user_settings["exchange"].get("market") == "Spot" else 1, horizontal=True)
#         api_k = st.text_input("API Key", type="password", value=dec_secret(user_settings["exchange"].get("key", "")))
#         secret_k = st.text_input("Secret Key", type="password", value=dec_secret(user_settings["exchange"].get("secret", "")))
#         demo_chk = st.checkbox("Enable Sandbox / Testnet Mode", value=user_settings["exchange"].get("demo", True))
#         st.caption("Tip: exchange par key banate waqt sirf **Spot trading** on karo, **Withdrawal OFF** rakho, aur ho sake to server IP whitelist karo.")
#         if st.button("🔌 Connect & Verify API", type="primary", use_container_width=True):
#             try:
#                 ex_config = {'apiKey': api_k, 'secret': secret_k, 'enableRateLimit': True,
#                              'options': {'defaultType': 'future' if market_type == "Futures (Derivatives)" else 'spot'}}
#                 ex = ccxt.binance(ex_config)
#                 if demo_chk:
#                     ex.set_sandbox_mode(True)
#                     if market_type == "Futures (Derivatives)":
#                         ex.urls['api']['fapiPublic'] = 'https://testnet.binancefuture.com/fapi/v1'
#                         ex.urls['api']['fapiPrivate'] = 'https://testnet.binancefuture.com/fapi/v1'
#                     else:
#                         ex.urls['api']['public'] = 'https://demo-api.binance.com/api/v3'
#                         ex.urls['api']['private'] = 'https://demo-api.binance.com/api/v3'
#                 ex.fetch_balance()
#                 user_settings["exchange"] = {"name": ex_choice, "market": market_type,
#                                              "key": enc_secret(api_k), "secret": enc_secret(secret_k),
#                                              "demo": demo_chk, "connected": True}
#                 save_db(db)
#                 st.success(f"✨ Successfully connected to {ex_choice} ({market_type})! Keys {'encrypted' if _CRYPTO_OK else 'saved'}.")
#             except Exception as e:
#                 user_settings["exchange"]["connected"] = False
#                 save_db(db)
#                 st.error(f"❌ Connection failed: {str(e)}")
#         st.markdown("</div>", unsafe_allow_html=True)

# # ==========================================
# # 2. STRATEGY STUDIO
# # ==========================================
# elif config_menu == "⚙️ Strategy Studio":
#     st.title("⚙️ Algorithmic Strategy Studio")
#     st.markdown("---")
#     st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#     exec_modes = ["Automated Trading (Bot takes trades & sets TP/SL automatically)",
#                   "Signal-Only Mode (Bot sends signals & email alerts only)"]
#     cur_exec = user_settings["strategy"].get("exec_mode", exec_modes[0])
#     exec_choice = st.radio("Choose how the bot should operate:", exec_modes, index=exec_modes.index(cur_exec) if cur_exec in exec_modes else 0)
#     user_settings["strategy"]["exec_mode"] = exec_choice
#     st.markdown("</div>", unsafe_allow_html=True)

#     mode_tab1, mode_tab2 = st.tabs(["🛠️ Manual Rule Builder", "🤖 AI Prompt (Auto)"])
#     with mode_tab1:
#         st.caption("Sirf jo checkbox tick karoge, bot SIRF wahi condition check karega (AND logic). "
#                    "Har indicator signal + confirmation candle dekh kar trade karta hai. Timeframe global hai.")
#         manual_cfg = user_settings["strategy"]["manual"]
#         st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#         st.subheader("⏱️ Timeframe (Global)")
#         tf_options = ["15m", "1h", "4h", "1d"]
#         cur_tf = manual_cfg.get("timeframe", "1h")
#         manual_cfg["timeframe"] = st.selectbox("Candle Timeframe", tf_options, index=tf_options.index(cur_tf) if cur_tf in tf_options else 1)
#         st.markdown("</div>", unsafe_allow_html=True)

#         c1, c2 = st.columns(2, gap="large")
#         with c1:
#             st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#             manual_cfg["ma_enabled"] = st.checkbox("📈 Enable Moving Average (MA) Filter", value=manual_cfg.get("ma_enabled", False))
#             ma_str = st.text_input("MA Periods (comma separated)",
#                                    value=",".join(str(p) for p in manual_cfg.get("ma_periods", [])),
#                                    placeholder="e.g. 200  ya  44,100,200  (khaali = MA check nahi hoga)",
#                                    disabled=not manual_cfg["ma_enabled"])
#             try:
#                 manual_cfg["ma_periods"] = [int(x.strip()) for x in ma_str.split(",") if x.strip()]
#             except Exception:
#                 manual_cfg["ma_periods"] = []
#             st.caption("Rule: signal candle green + har MA ke upar, phir confirmation candle bhi green + upar.")
#             st.markdown("</div>", unsafe_allow_html=True)

#             st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#             manual_cfg["rsi_enabled"] = st.checkbox("📊 Enable RSI Range Filter", value=manual_cfg.get("rsi_enabled", False))
#             rc1, rc2 = st.columns(2)
#             manual_cfg["rsi_min"] = rc1.number_input("RSI Min", 0, 100, value=int(manual_cfg.get("rsi_min", 30)), disabled=not manual_cfg["rsi_enabled"])
#             manual_cfg["rsi_max"] = rc2.number_input("RSI Max", 0, 100, value=int(manual_cfg.get("rsi_max", 45)), disabled=not manual_cfg["rsi_enabled"])
#             st.caption("Rule: RSI range me + confirmation candle green (momentum up).")
#             st.markdown("</div>", unsafe_allow_html=True)

#             st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#             manual_cfg["sr_enabled"] = st.checkbox("🧱 Enable Support Bounce Filter", value=manual_cfg.get("sr_enabled", False))
#             manual_cfg["sr_lookback"] = st.number_input("Support Lookback Candles", 10, 500, value=int(manual_cfg.get("sr_lookback", 50)), disabled=not manual_cfg["sr_enabled"])
#             manual_cfg["sr_tolerance_pct"] = st.number_input("Max Distance From Support (%)", 0.1, 10.0, value=float(manual_cfg.get("sr_tolerance_pct", 1.0)), disabled=not manual_cfg["sr_enabled"])
#             st.caption("Rule: price support ke paas aaye + green bounce candle confirm kare.")
#             st.markdown("</div>", unsafe_allow_html=True)

#         with c2:
#             st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#             manual_cfg["ob_enabled"] = st.checkbox("🟩 Enable Order Block (Bullish) Filter", value=manual_cfg.get("ob_enabled", False))
#             manual_cfg["ob_lookback"] = st.number_input("Order Block Lookback Candles", 20, 500, value=int(manual_cfg.get("ob_lookback", 50)), disabled=not manual_cfg["ob_enabled"])
#             st.caption("Rule: OB zone touch + green reaction candle confirm kare.")
#             st.markdown("</div>", unsafe_allow_html=True)

#             st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#             manual_cfg["vol_enabled"] = st.checkbox("💧 Enable Volume Filter", value=manual_cfg.get("vol_enabled", False))
#             manual_cfg["vol_min_usdt"] = st.number_input("Minimum 24h Volume (USDT)", 0, 1000000000, value=int(manual_cfg.get("vol_min_usdt", 500000)), disabled=not manual_cfg["vol_enabled"])
#             st.caption("Rule: 24h volume kam se kam itna ho (confirmation candle nahi lagti).")
#             st.markdown("</div>", unsafe_allow_html=True)

#             st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#             manual_cfg["trend_enabled"] = st.checkbox("📐 Enable Trendline Bounce Filter", value=manual_cfg.get("trend_enabled", False))
#             manual_cfg["trend_lookback"] = st.number_input("Trendline Lookback Candles", 20, 500, value=int(manual_cfg.get("trend_lookback", 100)), disabled=not manual_cfg["trend_enabled"])
#             manual_cfg["trend_touches"] = st.number_input("Minimum Touches", 2, 10, value=int(manual_cfg.get("trend_touches", 3)), disabled=not manual_cfg["trend_enabled"])
#             st.caption("Rule: rising trendline touch + green bounce candle confirm kare.")
#             st.markdown("</div>", unsafe_allow_html=True)

#         active_rules = []
#         if manual_cfg.get("ma_enabled"): active_rules.append("MA")
#         if manual_cfg.get("rsi_enabled"): active_rules.append("RSI")
#         if manual_cfg.get("sr_enabled"): active_rules.append("Support")
#         if manual_cfg.get("ob_enabled"): active_rules.append("Order Block")
#         if manual_cfg.get("vol_enabled"): active_rules.append("Volume")
#         if manual_cfg.get("trend_enabled"): active_rules.append("Trendline")

#         st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#         st.write("**Active Rules (AND logic):**")
#         if active_rules:
#             st.markdown("".join([f"<span class='rule-tag'>{r}</span>" for r in active_rules]), unsafe_allow_html=True)
#             if manual_cfg.get("ma_enabled") and not manual_cfg.get("ma_periods"):
#                 st.warning("⚠️ MA on hai lekin koi number nahi diya — MA field me kam se kam ek number likho (jaise 200).")
#         else:
#             st.warning("⚠️ Koi rule enable nahi hai — is state mein bot koi trade nahi lega.")
#         st.markdown("</div>", unsafe_allow_html=True)

#         # ---- Coin Universe / Monitoring-Tag filter ----
#         st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#         st.subheader("🌐 Coin Filters (scan universe)")
#         flt = user_settings.setdefault("filters", dict(DEFAULT_FILTERS))
#         flt["universe_min_volume"] = st.number_input(
#             "Scan sirf itne 24h Volume (USDT) se upar wale coins par",
#             0, 1000000000, value=int(flt.get("universe_min_volume", 1000000)))
#         exclude_str = st.text_input(
#             "Exclude coins (comma separated) — Monitoring-Tag / risky coins yahan likho",
#             value=",".join(flt.get("exclude", [])),
#             placeholder="e.g. QKC, XYZ")
#         flt["exclude"] = [x.strip().upper() for x in exclude_str.split(",") if x.strip()]
#         st.caption("Note: Binance ka 'Monitoring Tag' API se seedha nahi milta, is liye aise coins yahan likh kar block karo. "
#                    "Stablecoins/leveraged/delisted pehle se auto-filtered hain.")
#         st.markdown("</div>", unsafe_allow_html=True)

#         if st.button("💾 Save Manual Strategy", type="primary", use_container_width=True, key="save_manual"):
#             user_settings["strategy"]["manual"] = manual_cfg
#             user_settings["strategy"]["mode"] = "manual"
#             save_db(db)
#             st.success("✅ Manual strategy + filters saved. Bot ab isi ke hisab se scan karega.")

#     with mode_tab2:
#         st.caption("Free-text prompt (Note: abhi AI evaluation connect nahi — trades manual rule builder se lagti hain).")
#         st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#         ai_p = st.text_area("Write your custom prompt:", value=user_settings["strategy"].get("ai_prompt", ""), height=160)
#         st.markdown("</div>", unsafe_allow_html=True)
#         if st.button("💾 Save & Use AI Prompt Mode", type="primary", use_container_width=True, key="save_ai"):
#             user_settings["strategy"]["ai_prompt"] = ai_p
#             user_settings["strategy"]["mode"] = "ai_prompt"
#             save_db(db)
#             st.success("✅ AI Prompt mode active.")

#     st.markdown("---")
#     st.markdown("<div class='crypto-card'>", unsafe_allow_html=True)
#     st.subheader("🛡️ Risk Management (applies to both modes)")
#     sl = st.number_input("Stop Loss Percentage (%)", 0.1, 20.0, value=user_settings["strategy"].get("sl_pct", 2.0))
#     tp = st.number_input("Take Profit Percentage (%)", 0.1, 50.0, value=user_settings["strategy"].get("tp_pct", 4.5))
#     user_settings["strategy"]["sl_pct"] = sl
#     user_settings["strategy"]["tp_pct"] = tp
#     if st.button("💾 Save Risk Settings", use_container_width=True):
#         save_db(db); st.success("✅ Risk settings saved.")
#     st.markdown("</div>", unsafe_allow_html=True)

#     active_mode = user_settings["strategy"].get("mode", "manual")
#     st.info(f"🔵 Currently active mode: **{'Manual Rule Builder' if active_mode == 'manual' else 'AI Prompt (Auto)'}**")

# # ==========================================
# # 3. LIMITATION & CAMPAIGN
# # ==========================================
# elif config_menu == "📦 Limitation & Campaign":
#     st.markdown("<h2>📦 Limitation & Campaign</h2>", unsafe_allow_html=True)
#     st.markdown("---")
#     col1, col2 = st.columns(2, gap="large")
#     with col1:
#         c_days = st.number_input("Campaign Duration", 1, 365, value=user_settings["limits"].get("campaign_days", 1))
#         d_limit = st.number_input("Daily Maximum Auto Trades", 1, 100, value=user_settings["limits"].get("daily_limit", 1))
#         t_amt = st.number_input("Per Trade USDT", 5.0, value=user_settings["limits"].get("trade_amount", 100.0))
#         user_settings["limits"]["campaign_days"] = c_days
#         user_settings["limits"]["daily_limit"] = d_limit
#         user_settings["limits"]["trade_amount"] = t_amt
#         st.caption("Auto mode: bot exactly itni hi trades lega (2→2, 20→20), har coin sirf 1 baar, phir aaj ke liye ruk jayega. "
#                    "Signal-Only mode: is limit se azaad — signal deta rahega.")
#     with col2:
#         email_cfg = user_settings.setdefault("email", {"enabled": True, "host": "smtp.gmail.com", "port": 587, "sender": "", "password": "", "receiver": ""})
#         e_en = st.checkbox("Enable Email Notifications", value=email_cfg.get("enabled", True))
#         e_host = st.text_input("SMTP Host", value=email_cfg.get("host", "smtp.gmail.com"))
#         e_port = st.number_input("SMTP Port", value=email_cfg.get("port", 587))
#         e_sender = st.text_input("Sender Gmail", value=email_cfg.get("sender", ""))
#         e_pass = st.text_input("Gmail App Password", type="password", value=dec_secret(email_cfg.get("password", "")))
#         e_recv = st.text_input("Send Alerts To", value=email_cfg.get("receiver", ""))
#         email_cfg.update({"enabled": e_en, "host": e_host, "port": e_port,
#                           "sender": e_sender, "password": enc_secret(e_pass), "receiver": e_recv})

#         st.caption("Tip: Gmail ke liye normal account password kaam nahi karega — Google Account → Security → "
#                    "2-Step Verification (on karo) → App Passwords se ek 16-digit App Password banao, wahi yahan daalo.")

#         if st.button("📧 Send Test Email", use_container_width=True):
#             with st.spinner("Test email bheja ja raha hai..."):
#                 test_ok = send_email_alert(
#                     "✅ Apex Trading — Test Email",
#                     "<html><body style='font-family:Arial;background:#0b0e11;color:#eaecef;padding:20px;'>"
#                     "<h2 style='color:#fcd535;'>Test email successful!</h2>"
#                     "<p>Agar aapko ye email mila hai, matlab SMTP settings bilkul sahi hain.</p>"
#                     "</body></html>",
#                     email_cfg
#                 )
#             if test_ok:
#                 st.success("✅ Test email bhej diya gaya! Apna inbox (aur Spam folder) check karo.")
#             else:
#                 st.error("❌ Test email fail hua. Exact error dekhne ke liye Dashboard → 📜 Bot Logs kholo — "
#                          "wahan Gmail ka asli error message milega (jaise galat App Password, ya 2-Step Verification off).")

#     if st.button("💾 Save Limits & Notifications", type="primary", use_container_width=True):
#         save_db(db); st.success("✅ Saved successfully!")

# # ==========================================
# # 4. DASHBOARD
# # ==========================================
# else:
#     rt = get_runtime(user_settings)
#     save_db(db)
#     st.markdown(f"""
#         <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
#             <div>
#                 <h1 style='margin: 0; font-size: 26px;'>⚡ Apex Trading Dashboard</h1>
#                 <p style='margin: 4px 0 0 0; color: #848e9c; font-size: 13px;'>Rule-Based Strategy Engine + optional AI Prompt mode.</p>
#             </div>
#             <div style='background: #181a20; border: 1px solid #2b313a; padding: 8px 16px; border-radius: 8px; text-align: right;'>
#                 <div style='color: #fcd535; font-weight: bold;'>👤 {curr_user}</div>
#                 <div style='color: #0ecb81; font-size: 12px;'>● Active Session</div>
#             </div>
#         </div>
#     """, unsafe_allow_html=True)

#     dash_tab = st.radio("Tabs", ["📊 Analytics", "🎯 Active Trades", "🔍 Signal Feed", "💰 History", "📜 Bot Logs"],
#                         horizontal=True, label_visibility="collapsed")
#     st.markdown("---")

#     if dash_tab == "📊 Analytics":
#         ex_status_cfg = user_settings.get("exchange", {})
#         is_connected = bool(ex_status_cfg.get("connected")) and bool(ex_status_cfg.get("key"))
#         if is_connected:
#             st.markdown("<div class='crypto-card'>🟢 <b>Exchange Status:</b> Connected — Automated mode CAN place real orders.</div>", unsafe_allow_html=True)
#         else:
#             st.markdown("<div class='crypto-card'>🔴 <b>Exchange Status:</b> NOT connected (or API key missing). "
#                         "Bot signals to banata rahega par tab tak real order NAHI karega jab tak <b>Exchange Integration</b> me connect na karo.</div>", unsafe_allow_html=True)

#         st.markdown("<div class='crypto-card' style='border-left:4px solid #f6465d;'>⚠️ <b>Zaroori:</b> App ko sirf <b>ek hi browser tab</b> me chalao. "
#                     "Ek se zyada tab khule honge to har tab apna bot loop chalata hai — is se limit galat lag sakti hai.</div>", unsafe_allow_html=True)

#         history = user_settings["trade_history"]
#         total_trades = len(history)
#         successful_wins = len([h for h in history if "PROFIT" in h.get("status", "")])
#         today_pnl = sum([float(h.get("pnl_val", 0)) for h in history if h.get("date") == str(date.today())])

#         c_m1, c_m2, c_m3, c_m4 = st.columns(4)
#         c_m1.metric("Total Trades Executed", total_trades)
#         c_m2.metric("Successful Wins", successful_wins)
#         c_m3.metric("Today's Net PnL", f"${today_pnl:+,.2f}")
#         c_m4.metric("Bot Status", "Running" if st.session_state.bot_running else "Stopped")

#         _lim = int(user_settings["limits"].get("daily_limit", 1))
#         # Display ko hamesha clamp karo — chahe kisi bhi wajah se number thoda idhar-udhar ho,
#         # user ko kabhi limit se zyada "X/Y" ka number NAHI dikhna chahiye.
#         _shown_trades = min(int(rt.get('trades_today', 0)), _lim)
#         st.markdown(
#             f"<div class='crypto-card'><b>Today's Auto Trades:</b> "
#             f"<span style='color:#fcd535;'>{_shown_trades} / {_lim}</span> &nbsp; "
#             f"({max(_lim - _shown_trades, 0)} remaining today) &nbsp;|&nbsp; "
#             f"<b>Signals Today:</b> <span style='color:#0ecb81;'>{rt['signals_today']}</span></div>",
#             unsafe_allow_html=True)

#         active_mode = user_settings["strategy"].get("mode", "manual")
#         st.markdown(f"<div class='crypto-card'><b>Strategy Mode:</b> "
#                     f"<span style='color:#fcd535;'>{'🛠️ Manual Rule Builder' if active_mode=='manual' else '🤖 AI Prompt (Auto)'}</span></div>",
#                     unsafe_allow_html=True)

#         st.markdown("<br>", unsafe_allow_html=True)
#         b_c1, b_c2 = st.columns(2)
#         with b_c1:
#             if st.button("🚀 START BOT ENGINE", use_container_width=True, type="primary"):
#                 st.session_state.bot_running = True
#                 add_log("Apex bot engine started.")
#                 st.rerun()
#         with b_c2:
#             if st.button("🛑 STOP BOT", use_container_width=True):
#                 st.session_state.bot_running = False
#                 add_log("Apex bot stopped.")
#                 st.rerun()

#     elif dash_tab == "🎯 Active Trades":
#         top1, top2 = st.columns([0.7, 0.3])
#         with top1:
#             st.subheader("🎯 Active Positions")
#         with top2:
#             if user_settings["active_trades"] and st.button("🗑️ Clear All", use_container_width=True, key="clr_active"):
#                 user_settings["active_trades"] = []
#                 save_db(db); st.rerun()

#         active_list = user_settings["active_trades"]
#         if active_list:
#             for idx, trade in enumerate(list(active_list)):
#                 cc1, cc2 = st.columns([0.9, 0.1])
#                 with cc1:
#                     rules_html = f"<br><span style='color:#848e9c;font-size:12px;'>Rules:</span> <b style='font-size:12px;'>{trade.get('Rules','—')}</b>" if trade.get("Rules") else ""
#                     st.markdown(f"""
#                     <div class='trade-card'>
#                         <div style='display:flex; justify-content:space-between; align-items:center;'>
#                             <span class='sym-title'>{trade['Symbol']} <span style='color:#848e9c;font-size:12px;'>({trade['Market']})</span></span>
#                             <span class='badge-live'>🟢 LIVE</span>
#                         </div>
#                         <div style='margin-top:10px;'>
#                             <span class='kv'><span class='k'>Entry</span><span class='v' style='color:#3b82f6;'>${trade['Entry']}</span></span>
#                             <span class='kv'><span class='k'>Allocated</span><span class='v'>{trade['Amount']}</span></span>
#                             <span class='kv'><span class='k'>Take Profit</span><span class='v' style='color:#0ecb81;'>${trade['TP']}</span></span>
#                             <span class='kv'><span class='k'>Stop Loss</span><span class='v' style='color:#f6465d;'>${trade['SL']}</span></span>
#                         </div>
#                         {rules_html}
#                     </div>
#                     """, unsafe_allow_html=True)
#                 with cc2:
#                     if st.button("❌", key=f"del_trade_{idx}", help="Is card ko hatao"):
#                         user_settings["active_trades"].pop(idx)
#                         save_db(db); st.rerun()
#         else:
#             st.info("No active trades running right now.")

#     elif dash_tab == "🔍 Signal Feed":
#         top1, top2 = st.columns([0.7, 0.3])
#         with top1:
#             st.subheader("📡 Live Signals Feed")
#         with top2:
#             if user_settings["signals_feed"] and st.button("🗑️ Clear All", use_container_width=True, key="clr_signals"):
#                 user_settings["signals_feed"] = []
#                 save_db(db); st.rerun()

#         if user_settings["signals_feed"]:
#             for i, sig in enumerate(list(user_settings["signals_feed"])):
#                 epoch_time = sig.get("timestamp_epoch", time.time())
#                 diff_seconds = int(time.time() - epoch_time)
#                 if diff_seconds < 60: time_ago_str = "Just now"
#                 elif diff_seconds < 3600: time_ago_str = f"{diff_seconds // 60} mins ago"
#                 elif diff_seconds < 86400: time_ago_str = f"{diff_seconds // 3600} hrs ago"
#                 else: time_ago_str = "1 day ago"

#                 stype = sig.get("type", "Signal")
#                 badge = "badge-live" if stype == "Executed Trade" else "badge-signal"
#                 badge_txt = "✅ EXECUTED" if stype == "Executed Trade" else "📡 SIGNAL"
#                 rules_html = f"<br><span style='color:#848e9c;font-size:12px;'>Rules:</span> <b style='font-size:12px;'>{sig.get('rules')}</b>" if sig.get('rules') else ""

#                 cc1, cc2 = st.columns([0.9, 0.1])
#                 with cc1:
#                     st.markdown(f"""
#                     <div class='sig-card'>
#                         <div style='display:flex; justify-content:space-between; align-items:center;'>
#                             <span class='sym-title'>{sig['symbol']}</span>
#                             <span class='{badge}'>{badge_txt}</span>
#                         </div>
#                         <div style='margin-top:10px;'>
#                             <span class='kv'><span class='k'>Entry</span><span class='v' style='color:#3b82f6;'>{sig.get('entry',0):,.6f}</span></span>
#                             <span class='kv'><span class='k'>Take Profit</span><span class='v' style='color:#0ecb81;'>{sig.get('tp',0):,.6f}</span></span>
#                             <span class='kv'><span class='k'>Stop Loss</span><span class='v' style='color:#f6465d;'>{sig.get('sl',0):,.6f}</span></span>
#                         </div>
#                         {rules_html}
#                         <div style='color:#848e9c; font-size:11px; margin-top:8px;'>🕒 {time_ago_str} ({sig.get('time','N/A')})</div>
#                     </div>
#                     """, unsafe_allow_html=True)
#                 with cc2:
#                     if st.button("❌", key=f"del_sig_{sig.get('id', i)}", help="Is signal ko hatao"):
#                         user_settings["signals_feed"].pop(i)
#                         save_db(db); st.rerun()
#         else:
#             st.info("No active signals right now.")

#     elif dash_tab == "💰 History":
#         top1, top2 = st.columns([0.7, 0.3])
#         with top1:
#             st.subheader("💰 Trade History")
#         with top2:
#             if user_settings["trade_history"] and st.button("🗑️ Clear History", use_container_width=True, key="clr_hist"):
#                 user_settings["trade_history"] = []
#                 save_db(db); st.rerun()
#         if user_settings["trade_history"]:
#             st.dataframe(pd.DataFrame(user_settings["trade_history"]), use_container_width=True)
#         else:
#             st.info("No trade history available yet.")

#     elif dash_tab == "📜 Bot Logs":
#         st.subheader("📜 Bot Logs (most recent first)")
#         st.caption("Yahan exact reason milega ke koi trade kyun skip hui, ya order kyun fail hua.")
#         logs = user_settings.get("logs", [])
#         if logs:
#             if st.button("🗑️ Clear Logs"):
#                 user_settings["logs"] = []; save_db(db); st.rerun()
#             for line in reversed(logs[-200:]):
#                 st.text(line)
#         else:
#             st.info("Koi log abhi tak nahi bana.")

# # ==========================================
# # BACKGROUND AUTOMATED & EMAIL LOOP
# # ==========================================
# if st.session_state.bot_running:
#     rt = get_runtime(user_settings)
#     save_db(db)
#     daily_lim = int(user_settings["limits"].get("daily_limit", 1))
#     exec_mode_setting = user_settings["strategy"].get("exec_mode", "")
#     is_signal_only = "Signal-Only" in exec_mode_setting or "Signal" in exec_mode_setting

#     if (not is_signal_only) and rt["trades_today"] >= daily_lim:
#         add_log(f"⏳ Daily auto-trade limit reached ({rt['trades_today']}/{daily_lim}). Aaj ke liye paused (kal reset).")
#         st.warning(f"⚠️ Daily trade limit {daily_lim} poori ho gayi — aaj {rt['trades_today']} trade ho chuke. Ab kal tak paused.")
#         time.sleep(15); st.rerun()

#     try:
#         ex_cfg = user_settings["exchange"]
#         market_m = ex_cfg.get("market", "Spot")
#         ex_config = {'apiKey': dec_secret(ex_cfg.get("key")), 'secret': dec_secret(ex_cfg.get("secret")),
#                      'enableRateLimit': True,
#                      'options': {'defaultType': 'future' if market_m == "Futures (Derivatives)" else 'spot'}}
#         ex = ccxt.binance(ex_config)
#         if ex_cfg.get("demo"):
#             ex.set_sandbox_mode(True)
#             if market_m == "Futures (Derivatives)":
#                 ex.urls['api']['fapiPublic'] = 'https://testnet.binancefuture.com/fapi/v1'
#                 ex.urls['api']['fapiPrivate'] = 'https://testnet.binancefuture.com/fapi/v1'
#             else:
#                 ex.urls['api']['public'] = 'https://demo-api.binance.com/api/v3'
#                 ex.urls['api']['private'] = 'https://demo-api.binance.com/api/v3'

#         ex.load_markets()
#         flt = user_settings.get("filters", DEFAULT_FILTERS)

#         # ---- PERF/STABILITY FIX ----
#         # Pehle har 15 second me Binance ke SAARE (2000+) coins ka poora ticker data
#         # (fetch_tickers) dobara mangwaya jata tha — chhote VPS (1GB RAM) ke liye ye
#         # bahut bhaari kaam hai aur crash/restart ki sabse badi wajah tha (jisse
#         # session/login "khud logout" jaisa lagta tha). Ab ye data sirf har
#         # UNIVERSE_CACHE_TTL second (3 minute) me ek baar refresh hota hai — baaki
#         # waqt session me cache se use hota hai. Strategy/behaviour bilkul wahi
#         # rehta hai, sirf resource-use kam ho jata hai.
#         _now_ts = time.time()
#         _cache_key = (curr_user, int(flt.get("universe_min_volume", 1000000)),
#                       tuple(sorted(e.upper() for e in flt.get("exclude", []))))
#         _cache_fresh = (
#             st.session_state.get("_universe_cache_key") == _cache_key
#             and (_now_ts - st.session_state.get("_universe_cache_ts", 0)) < UNIVERSE_CACHE_TTL
#             and st.session_state.get("_universe_cache")
#         )
#         if _cache_fresh:
#             universe = st.session_state["_universe_cache"]
#             all_tickers = st.session_state.get("_tickers_cache")
#         else:
#             try:
#                 all_tickers = ex.fetch_tickers()
#             except Exception:
#                 all_tickers = None
#             universe = build_symbol_universe(ex, all_tickers,
#                                              min_volume=int(flt.get("universe_min_volume", 1000000)),
#                                              exclude_bases=flt.get("exclude", []))
#             if not universe:
#                 excl = {e.upper() for e in flt.get("exclude", [])}
#                 universe = [s for s in ex.symbols
#                             if s.endswith('/USDT') and s.split('/')[0].upper() not in STABLE_OR_FIAT
#                             and s.split('/')[0].upper() not in excl][:40]
#             if not universe:
#                 universe = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
#             st.session_state["_universe_cache"] = universe
#             st.session_state["_tickers_cache"] = all_tickers
#             st.session_state["_universe_cache_key"] = _cache_key
#             st.session_state["_universe_cache_ts"] = _now_ts

#         available = [c for c in universe if c not in rt["traded_coins_today"]]
#         if not available:
#             if is_signal_only:
#                 rt["traded_coins_today"] = []
#                 save_db(db)
#                 available = universe
#             else:
#                 add_log("🔎 Aaj ke available coins khatam. Idling.")
#                 time.sleep(15); st.rerun()

#         strategy_mode = user_settings["strategy"].get("mode", "manual")
#         chosen_coin = None; c_price = 0.0; matched_rules_str = ""

#         if strategy_mode == "manual":
#             manual_cfg = user_settings["strategy"]["manual"]
#             sample_pool = available[:25] if len(available) >= 25 else available
#             candidates = []
#             for coin in sample_pool:
#                 try:
#                     passed, rules = evaluate_manual_strategy(ex, coin, manual_cfg)
#                     if passed:
#                         candidates.append((coin, rules))
#                 except Exception:
#                     continue
#             if candidates:
#                 best = None; best_vol = -1
#                 for coin, rules in candidates:
#                     vol = 0.0
#                     if all_tickers and coin in all_tickers:
#                         try: vol = float(all_tickers[coin].get('quoteVolume') or 0)
#                         except Exception: vol = 0.0
#                     else:
#                         try: vol = float(ex.fetch_ticker(coin).get('quoteVolume') or 0)
#                         except Exception: vol = 0.0
#                     if vol > best_vol:
#                         best_vol = vol; best = (coin, rules)
#                 chosen_coin, matched_rules_list = best
#                 matched_rules_str = ", ".join(matched_rules_list)
#                 try:
#                     c_price = float(ex.fetch_ticker(chosen_coin).get('last') or 0.0)
#                 except Exception:
#                     c_price = 0.0
#             else:
#                 add_log("🔎 Manual scan complete — koi coin saari ticked conditions match nahi kar raha. Idling.")
#         else:
#             add_log("⚠️ AI Prompt mode selected hai par koi AI evaluation connect nahi — is mode me trade nahi banegi.")

#         if chosen_coin is None:
#             time.sleep(15); st.rerun()

#         # ---- SLOT RESERVE (order se PEHLE) ----
#         ok, reason, db = try_reserve_slot(curr_user, chosen_coin, daily_lim, is_signal_only)
#         user_settings = db["settings"][curr_user]
#         rt = get_runtime(user_settings)

#         # ---- EXTRA SAFETY NET ----
#         # Chahe kitni bhi tabs/process ya restart ho jaye, trades_today kabhi bhi
#         # daily_lim se zyada NAHI hona chahiye. Agar phir bhi (kisi wajah se) ho
#         # jaye, is reservation ko turant undo karo — order place hi NAHI hoga, aur
#         # limit hamesha exactly wahi rahegi jo user ne set ki hai (2 -> 2, 50 -> 50).
#         if ok and not is_signal_only and rt["trades_today"] > daily_lim:
#             rt["trades_today"] = daily_lim
#             if chosen_coin in rt["traded_coins_today"]:
#                 rt["traded_coins_today"].remove(chosen_coin)
#             save_db(db)
#             add_log(f"🛡️ Safety rollback: {chosen_coin} reservation undo ki gayi (limit {daily_lim} already reached tha).")
#             ok = False
#             reason = "limit reached"

#         if not ok:
#             if reason == "limit reached":
#                 add_log(f"⏳ Limit reached ({rt['trades_today']}/{daily_lim}) — {chosen_coin} skip. Paused for today.")
#                 st.warning(f"⚠️ Daily limit {daily_lim} poori. Ab kal tak paused.")
#             else:
#                 add_log(f"↩️ {chosen_coin} skip ({reason}). Agla coin dekhenge.")
#             time.sleep(15); st.rerun()

#         if c_price <= 0:
#             try:
#                 ohlcv = ex.fetch_ohlcv(chosen_coin, timeframe='1m', limit=1)
#                 if ohlcv: c_price = float(ohlcv[0][4])
#             except Exception:
#                 c_price = 1.0

#         amt_usdt = float(user_settings["limits"]["trade_amount"])
#         try:
#             coin_qty = float(ex.amount_to_precision(chosen_coin, amt_usdt / c_price))
#         except Exception:
#             coin_qty = amt_usdt / c_price

#         tp_p = user_settings["strategy"]["tp_pct"]; sl_p = user_settings["strategy"]["sl_pct"]
#         tp_val = c_price * (1 + tp_p / 100); sl_val = c_price * (1 - sl_p / 100)

#         current_time_str = datetime.now().strftime("%I:%M:%S %p")
#         full_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         timestamp_epoch = datetime.now().timestamp()

#         # per-user signals feed (24h se purane -> signal_history)
#         us_feed = user_settings.setdefault("signals_feed", [])
#         us_hist = user_settings.setdefault("signal_history", [])
#         active_signals = []
#         for sig in us_feed:
#             if (timestamp_epoch - sig.get("timestamp_epoch", timestamp_epoch)) >= 86400:
#                 if sig not in us_hist:
#                     us_hist.insert(0, sig)
#             else:
#                 active_signals.append(sig)
#         user_settings["signals_feed"] = active_signals

#         new_signal = {
#             "id": f"{chosen_coin}_{int(timestamp_epoch)}",
#             "time": current_time_str, "full_timestamp": full_ts, "timestamp_epoch": timestamp_epoch,
#             "symbol": chosen_coin,
#             "strategy": "Manual Rule Engine" if strategy_mode == "manual" else "AI Prompt Engine",
#             "rules": matched_rules_str, "entry": c_price, "tp": tp_val, "sl": sl_val,
#             "type": "Signal Only" if is_signal_only else "Executed Trade"
#         }
#         user_settings["signals_feed"].insert(0, new_signal)
#         save_db(db)

#         email_cfg = user_settings.get("email", {})
#         if email_cfg.get("enabled"):
#             email_sub = f"🚨 [Apex Trading] {'Signal Generated' if is_signal_only else 'Trade Executed'}: {chosen_coin}"
#             email_body_html = f"""
#             <html><body style="font-family: Arial, sans-serif; background-color: #0b0e11; color: #eaecef; padding: 20px;">
#                 <div style="max-width: 600px; margin: auto; background: #181a20; border: 1px solid #2b313a; border-radius: 12px; padding: 25px;">
#                     <h2 style="color: #fcd535; margin-top: 0; text-align: center;">⚡ Apex Automated Alert</h2>
#                     <p style="color: #0ecb81; text-align: center; font-weight: bold;">Status: Strategy conditions successfully met!</p>
#                     <p style="color: #848e9c; text-align:center; font-size:12px;">Matched rules: {matched_rules_str or "N/A"}</p>
#                     <hr style="border: 0; border-top: 1px solid #2b313a; margin: 20px 0;">
#                     <table style="width: 100%; font-size: 14px; color: #eaecef; border-collapse: collapse;">
#                         <tr><td style="padding: 8px 0; color: #848e9c;">Trading Pair:</td><td style="padding: 8px 0; font-weight: bold; color: #fcd535; text-align: right;">{chosen_coin}</td></tr>
#                         <tr><td style="padding: 8px 0; color: #848e9c;">Market Type:</td><td style="padding: 8px 0; font-weight: bold; text-align: right;">{market_m}</td></tr>
#                         <tr><td style="padding: 8px 0; color: #848e9c;">Entry Price:</td><td style="padding: 8px 0; font-weight: bold; color: #3b82f6; text-align: right;">${c_price:,.6f}</td></tr>
#                         <tr><td style="padding: 8px 0; color: #848e9c;">Take Profit (TP):</td><td style="padding: 8px 0; font-weight: bold; color: #0ecb81; text-align: right;">${tp_val:,.6f} (+{tp_p}%)</td></tr>
#                         <tr><td style="padding: 8px 0; color: #848e9c;">Stop Loss (SL):</td><td style="padding: 8px 0; font-weight: bold; color: #f6465d; text-align: right;">${sl_val:,.6f} (-{sl_p}%)</td></tr>
#                         <tr><td style="padding: 8px 0; color: #848e9c;">Allocated Amount:</td><td style="padding: 8px 0; font-weight: bold; text-align: right;">${amt_usdt} USDT</td></tr>
#                     </table>
#                 </div></body></html>"""
#             send_email_alert(email_sub, email_body_html, email_cfg)

#         # -------- SIGNAL-ONLY --------
#         if is_signal_only:
#             add_log(f"📡 Signal #{rt['signals_today']} generated for {chosen_coin} (rules: {matched_rules_str}).")
#             time.sleep(15); st.rerun()

#         # -------- AUTO TRADE --------
#         placed_ok = False
#         if "Automated Trading" in exec_mode_setting:
#             if not (ex_cfg.get("connected") and ex_cfg.get("key")):
#                 add_log(f"⚠️ {chosen_coin}: exchange not connected — real order skip, signal recorded. "
#                         f"(Slot consume ho gaya taake limit safe rahe.)")
#             else:
#                 try:
#                     formatted_tp_price = float(ex.price_to_precision(chosen_coin, tp_val))
#                     formatted_sl_price = float(ex.price_to_precision(chosen_coin, sl_val))
#                 except Exception:
#                     formatted_tp_price = tp_val; formatted_sl_price = sl_val

#                 if market_m == "Spot":
#                     try:
#                         buy_res = ex.create_market_buy_order(chosen_coin, coin_qty)
#                         placed_ok = True
#                         add_log(f"✅ Spot Market Buy Executed for {chosen_coin} (rules: {matched_rules_str})")
#                     except Exception as buy_err:
#                         add_log(f"❌ Buy Order Error: {str(buy_err)}"); buy_res = None
#                     if buy_res:
#                         time.sleep(1.5)
#                         base_ccy = chosen_coin.split('/')[0]; sell_qty = coin_qty
#                         try:
#                             bal = ex.fetch_balance()
#                             free_amt = float(bal['free'].get(base_ccy, 0) or 0)
#                             if free_amt > 0: sell_qty = free_amt
#                         except Exception: pass
#                         try: sell_qty = float(ex.amount_to_precision(chosen_coin, sell_qty))
#                         except Exception: pass
#                         try: sl_limit_price = float(ex.price_to_precision(chosen_coin, sl_val * 0.997))
#                         except Exception: sl_limit_price = formatted_sl_price
#                         oco_done = False
#                         oco_fn = getattr(ex, 'private_post_order_oco', None)
#                         if oco_fn is not None:
#                             try:
#                                 oco_fn({'symbol': chosen_coin.replace('/', ''), 'side': 'SELL',
#                                         'quantity': ex.amount_to_precision(chosen_coin, sell_qty),
#                                         'price': ex.price_to_precision(chosen_coin, formatted_tp_price),
#                                         'stopPrice': ex.price_to_precision(chosen_coin, formatted_sl_price),
#                                         'stopLimitPrice': ex.price_to_precision(chosen_coin, sl_limit_price),
#                                         'stopLimitTimeInForce': 'GTC'})
#                                 add_log(f"🛡️ OCO placed — TP ${formatted_tp_price} / SL ${formatted_sl_price}")
#                                 oco_done = True
#                             except Exception as oco_err:
#                                 add_log(f"⚠️ OCO not available ({str(oco_err)[:70]}), trying separate SL/TP...")
#                         if not oco_done:
#                             try:
#                                 ex.create_order(chosen_coin, 'STOP_LOSS_LIMIT', 'sell', sell_qty, sl_limit_price, {'stopPrice': formatted_sl_price})
#                                 add_log(f"🛡️ Stop Loss placed at trigger ${formatted_sl_price}")
#                             except Exception:
#                                 try:
#                                     ex.create_order(chosen_coin, 'STOP_LOSS', 'sell', sell_qty, None, {'stopPrice': formatted_sl_price})
#                                     add_log(f"🛡️ Stop Loss (Market) placed at trigger ${formatted_sl_price}")
#                                 except Exception as sl_fallback_err:
#                                     add_log(f"⚠️ Stop Loss Order Warning: {str(sl_fallback_err)}")
#                             try:
#                                 bal2 = ex.fetch_balance()
#                                 free2 = float(bal2['free'].get(base_ccy, 0) or 0)
#                                 tp_qty = float(ex.amount_to_precision(chosen_coin, free2)) if free2 > 0 else 0
#                                 if tp_qty > 0:
#                                     ex.create_limit_sell_order(chosen_coin, tp_qty, formatted_tp_price)
#                                     add_log(f"🎯 Take Profit placed at ${formatted_tp_price}")
#                             except Exception as tp_err:
#                                 add_log(f"⚠️ TP Order Warning: {str(tp_err)}")
#                 else:
#                     try:
#                         ex.create_market_buy_order(chosen_coin, coin_qty); placed_ok = True
#                         add_log(f"✅ Futures Market Buy executed for {chosen_coin} (rules: {matched_rules_str})")
#                         time.sleep(1)
#                         ex.create_order(chosen_coin, 'TAKE_PROFIT_MARKET', 'sell', coin_qty, None, {'stopPrice': formatted_tp_price, 'reduceOnly': True})
#                         add_log(f"🎯 Futures Take Profit set at ${formatted_tp_price}")
#                         ex.create_order(chosen_coin, 'STOP_MARKET', 'sell', coin_qty, None, {'stopPrice': formatted_sl_price, 'reduceOnly': True})
#                         add_log(f"🛡️ Futures Stop Loss set at ${formatted_sl_price}")
#                     except Exception as fut_err:
#                         add_log(f"⚠️ Futures TP/SL note: {str(fut_err)}")

#         user_settings.setdefault("active_trades", []).append({
#             "Symbol": chosen_coin, "Market": market_m,
#             "Entry": f"{c_price:,.6f}", "Amount": f"${amt_usdt}",
#             "TP": f"{tp_val:,.6f}", "SL": f"{sl_val:,.6f}", "Rules": matched_rules_str
#         })
#         save_db(db)
#         add_log(f"📊 Auto trade {rt['trades_today']}/{daily_lim} done for {chosen_coin}"
#                 f"{'' if placed_ok else ' (signal only — no live order)'}.")
#         if rt["trades_today"] >= daily_lim:
#             add_log(f"✅ Aaj ki limit ({daily_lim}) complete. Bot ab kal tak naye auto-trade nahi lega.")

#     except Exception as e:
#         add_log(f"⚠️ Loop Error: {str(e)}")

#     time.sleep(15)
#     st.rerun()