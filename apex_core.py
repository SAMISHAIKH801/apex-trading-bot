"""
apex_core.py
Shared logic for Apex Trading — used by BOTH app.py (Streamlit UI) and
worker.py (the always-on background trading loop). Nothing here depends
on Streamlit, so it keeps running fine even if every browser tab is closed.
"""
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
import urllib.request
import urllib.error
from datetime import datetime, date

try:
    from cryptography.fernet import Fernet
    _CRYPTO_OK = True
except Exception:
    _CRYPTO_OK = False

# ==========================================
# CONFIG / PATHS
# ==========================================
DB_FILE = os.environ.get("APEX_DB_FILE", "database.json")
LOCK_FILE = os.environ.get("APEX_LOCK_FILE", "apex.lock")
KEY_FILE = os.environ.get("APEX_KEY_FILE", "apex_secret.key")
SECRET_ENV = "APEX_SECRET_KEY"
MIN_ACTION_GAP_SEC = 10
STALE_LOCK_SEC = 25
UNIVERSE_CACHE_TTL = 180
HEARTBEAT_STALE_SEC = 45          # UI warns if worker hasn't checked in for this long
SIGNAL_SCAN_WINDOW = 8            # how many recent candle-pairs to scan for a setup (was: only the very last pair)

# ==========================================
# ENCRYPTION
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
    if not plain:
        return ""
    if not isinstance(plain, str):
        plain = str(plain)
    if plain.startswith(ENC_PREFIX):
        return plain
    if FERNET is None:
        return plain
    try:
        return ENC_PREFIX + FERNET.encrypt(plain.encode()).decode()
    except Exception:
        return plain

def dec_secret(stored):
    if not stored or not isinstance(stored, str):
        return stored or ""
    if not stored.startswith(ENC_PREFIX):
        return stored
    if FERNET is None:
        return ""
    try:
        return FERNET.decrypt(stored[len(ENC_PREFIX):].encode()).decode()
    except Exception:
        return ""

# ==========================================
# PASSWORD HASHING
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
    "traded_coins_today": [], "last_action_epoch": 0,
    # NEW: bot on/off now lives in the DB (persisted), not in a browser session,
    # so it survives tab closes / phone lock / logout. worker.py reads this.
    "bot_running": False,
    "last_heartbeat": 0,          # updated by worker.py every cycle it looks at this user
}

DEFAULT_FILTERS = {
    "universe_min_volume": 1000000,
    "exclude": []
}

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

def add_log(db, username, msg):
    """Append a log line for a specific user. Does NOT save_db — caller decides when to flush."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    try:
        if username and username in db.get("settings", {}):
            db["settings"][username].setdefault("logs", []).append(line)
        else:
            db.setdefault("logs", []).append(line)
    except Exception:
        db.setdefault("logs", []).append(line)

# ------------------------------------------------------------------
# CROSS-PROCESS FILE LOCK (protects UI + worker touching the DB at once)
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
    lock = acquire_lock()
    if lock is None:
        return False, "busy (lock could not be acquired)", load_db()
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

# ------------------------------------------------------------------
# EMAIL — Brevo HTTPS API
# ------------------------------------------------------------------
_orig_getaddrinfo = socket.getaddrinfo

def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

def send_email_alert(subject, body_html, email_cfg, log_fn=None):
    """log_fn(msg) is optional — pass a small callback if you want errors logged."""
    if not email_cfg.get("enabled") or not email_cfg.get("sender") or not email_cfg.get("receiver"):
        return False
    api_key = dec_secret(email_cfg.get("brevo_api_key", ""))
    api_key = api_key.strip() if api_key else ""
    if not api_key:
        if log_fn: log_fn("Email Error: Brevo API key set nahi hai — Limitation & Campaign me daalo.")
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
    socket.getaddrinfo = _ipv4_only_getaddrinfo
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if 200 <= resp.status < 300:
                return True
            if log_fn: log_fn(f"Email Error: Brevo HTTP {resp.status}")
            return False
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", errors="ignore")
        except Exception:
            err_body = ""
        if log_fn: log_fn(f"Email Error: Brevo HTTP {e.code} - {err_body[:300]}")
        return False
    except Exception as e:
        if log_fn: log_fn(f"Email Error: {str(e)}")
        return False
    finally:
        socket.getaddrinfo = _orig_getaddrinfo

# ------------------------------------------------------------------
# COIN UNIVERSE FILTER
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
# STRATEGY / INDICATOR ENGINE
#
# IMPORTANT FIX: the old version only ever looked at the very last
# completed candle-pair (signal candle -2, confirm candle -1). That
# means a valid MA-touch / support-bounce / OB-tap / trendline-bounce
# had to have happened in EXACTLY the last hour (or whatever timeframe)
# to be seen at all — extremely rare, which is why MA/Support/OB/Trend
# almost never fired while RSI (a loose range check) fired often.
#
# Fix: each condition now scans the last SIGNAL_SCAN_WINDOW candle-pairs
# and returns True if ANY of them forms a valid setup. Same rules, same
# strictness per-candle — just not limited to "this exact instant".
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

def _recent_pairs(n_rows, window=SIGNAL_SCAN_WINDOW, min_sig_idx=1):
    """Yield (sig_idx, conf_idx) absolute row indices, most recent pair first."""
    for offset in range(1, window + 1):
        conf_idx = n_rows - offset
        sig_idx = conf_idx - 1
        if sig_idx < min_sig_idx or conf_idx < 0:
            continue
        yield sig_idx, conf_idx

def check_ma_condition(df, periods, window=SIGNAL_SCAN_WINDOW):
    """
    Real trader jaisa MA bounce, scanned across the last `window` candles:
    signal candle MA ko touch/react kare (bounce) ya thoda break karke wapas
    MA ke qareeb/upar close kare (reclaim) -> confirmation candle GREEN ho
    aur signal candle se upar close kare. Multiple MA ho to sab par AND.
    """
    if not periods:
        return False
    n = len(df)
    if n < max(periods) + window + 2:
        return False
    mas = {}
    for p in periods:
        mas[p] = df['close'].rolling(int(p)).mean()

    for sig_idx, conf_idx in _recent_pairs(n, window):
        conf = df.iloc[conf_idx]; sig = df.iloc[sig_idx]
        if not is_green(conf):
            continue
        if float(conf['close']) <= float(sig['close']):
            continue
        all_ok = True
        for p in periods:
            ma_sig = mas[p].iloc[sig_idx]
            if pd.isna(ma_sig):
                all_ok = False
                break
            sig_low = float(sig['low']); sig_high = float(sig['high']); sig_close = float(sig['close'])
            touched = sig_low <= ma_sig <= sig_high
            reclaimed = (sig_low < ma_sig) and (sig_close >= ma_sig * 0.998)
            if not (touched or reclaimed):
                all_ok = False
                break
        if all_ok:
            return True
    return False

def check_rsi_condition(df, rsi_min, rsi_max, period=14, window=SIGNAL_SCAN_WINDOW):
    n = len(df)
    if n < period + window + 2:
        return False
    rsi = calc_rsi(df['close'], period)
    for sig_idx, conf_idx in _recent_pairs(n, window):
        rsi_sig = rsi.iloc[sig_idx]; rsi_conf = rsi.iloc[conf_idx]
        if pd.isna(rsi_sig) or pd.isna(rsi_conf):
            continue
        conf = df.iloc[conf_idx]
        in_range = rsi_min <= float(rsi_sig) <= rsi_max
        momentum_up = float(rsi_conf) >= float(rsi_sig)
        if in_range and momentum_up and is_green(conf):
            return True
    return False

def check_support_condition(df, lookback, tolerance_pct, window=SIGNAL_SCAN_WINDOW):
    """
    Support zone = lookback ke 3 sabse neeche wale lows ka average.
    Scanned across last `window` candle-pairs instead of only the very last one.
    """
    recent = df.tail(int(lookback))
    if len(recent) < 6:
        return False
    n_sample = min(3, len(recent))
    support = float(recent['low'].nsmallest(n_sample).mean())
    if support <= 0:
        return False
    n = len(df)
    for sig_idx, conf_idx in _recent_pairs(n, window):
        sig = df.iloc[sig_idx]; conf = df.iloc[conf_idx]
        near_support = abs(float(sig['low']) - support) / support * 100 <= tolerance_pct
        bounce = is_green(conf) and float(conf['close']) > float(sig['close'])
        if near_support and bounce:
            return True
    return False

def check_order_block_condition(df, lookback, tolerance_pct=1.0, window=SIGNAL_SCAN_WINDOW):
    """
    Bullish Order Block: impulse candle (big body + above-average volume) whose
    base (previous 1-2 down candles) forms the zone. We look for the impulse
    candle BEFORE the recent scanning window (so it's a real historical zone,
    not the signal/confirm candle itself), then check if price tapped back
    into that zone within the last `window` candle-pairs.
    """
    recent = df.tail(int(lookback)).reset_index(drop=True)
    if len(recent) < 25:
        return False
    body = (recent['close'] - recent['open']).abs()
    avg_body = body.rolling(20).mean()
    avg_vol = recent['volume'].rolling(20).mean()
    ob_zone = None
    search_end = max(21, len(recent) - window - 1)   # exclude the scanning window itself
    for i in range(20, search_end):
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
    if ob_zone is None:
        return False
    zone_low, zone_high = ob_zone
    zone_high_padded = zone_high * (1 + tolerance_pct / 100)
    n = len(df)
    for sig_idx, conf_idx in _recent_pairs(n, window):
        sig = df.iloc[sig_idx]; conf = df.iloc[conf_idx]
        tapped = (zone_low <= float(sig['low']) <= zone_high_padded) or (zone_low <= float(sig['close']) <= zone_high_padded)
        reaction = is_green(conf) and float(conf['close']) > float(sig['close'])
        if tapped and reaction:
            return True
    return False

def check_volume_condition(ex, symbol, min_usdt, tickers=None):
    """Prefer the already-fetched tickers cache (fast, no extra API call / rate-limit risk)."""
    try:
        if tickers and symbol in tickers:
            qv = float((tickers[symbol] or {}).get('quoteVolume') or 0)
        else:
            ticker = ex.fetch_ticker(symbol)
            qv = float(ticker.get('quoteVolume') or 0)
        return qv >= float(min_usdt)
    except Exception:
        return False

def check_trendline_condition(df, lookback, touches_required, tolerance_pct=1.5, window=SIGNAL_SCAN_WINDOW):
    recent = df.tail(int(lookback)).reset_index(drop=True)
    if len(recent) < 20:
        return False
    lows_idx = []
    for i in range(2, len(recent) - 2):
        low = recent['low'].iloc[i]
        if (low < recent['low'].iloc[i - 1] and low < recent['low'].iloc[i - 2] and
                low < recent['low'].iloc[i + 1] and low < recent['low'].iloc[i + 2]):
            lows_idx.append(i)
    if len(lows_idx) < touches_required:
        return False
    xs = np.array(lows_idx[-int(touches_required):])
    ys = recent['low'].iloc[xs].values
    slope, intercept = np.polyfit(xs, ys, 1)
    if slope <= 0:
        return False

    n_df = len(df)
    n_recent = len(recent)
    offset_recent_to_df = n_df - n_recent   # df.iloc[offset_recent_to_df + j] == recent.iloc[j]
    for sig_idx, conf_idx in _recent_pairs(n_df, window):
        recent_pos = sig_idx - offset_recent_to_df
        if recent_pos < 0:
            continue
        trend_val = slope * recent_pos + intercept
        if trend_val <= 0:
            continue
        sig = df.iloc[sig_idx]; conf = df.iloc[conf_idx]
        near_line = abs(float(sig['low']) - trend_val) / trend_val * 100 <= tolerance_pct
        bounce = is_green(conf) and float(conf['close']) > float(sig['close'])
        if near_line and bounce:
            return True
    return False

def evaluate_manual_strategy(ex, symbol, cfg, tickers=None):
    tf = cfg.get("timeframe", "1h")
    ma_periods = cfg.get("ma_periods", []) or [0]
    needed_limit = max(cfg.get("sr_lookback", 50), cfg.get("ob_lookback", 50),
                       cfg.get("trend_lookback", 100), max(ma_periods), 210) + SIGNAL_SCAN_WINDOW + 30
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
        r = check_volume_condition(ex, symbol, cfg.get("vol_min_usdt", 500000), tickers=tickers); results.append(r)
        if r: matched_rules.append("Volume Filter")
    if cfg.get("trend_enabled"):
        r = check_trendline_condition(df, cfg.get("trend_lookback", 100), cfg.get("trend_touches", 3)); results.append(r)
        if r: matched_rules.append("Trendline Bounce")
    if not results:
        return False, []
    return all(results), matched_rules

# ==========================================
# EXCHANGE HELPERS
# ==========================================
def build_exchange(ex_cfg):
    market_m = ex_cfg.get("market", "Spot")
    ex_config = {
        'apiKey': dec_secret(ex_cfg.get("key")),
        'secret': dec_secret(ex_cfg.get("secret")),
        'enableRateLimit': True,
        'options': {'defaultType': 'future' if market_m == "Futures (Derivatives)" else 'spot'}
    }
    ex = ccxt.binance(ex_config)
    if ex_cfg.get("demo"):
        ex.set_sandbox_mode(True)
        if market_m == "Futures (Derivatives)":
            ex.urls['api']['fapiPublic'] = 'https://testnet.binancefuture.com/fapi/v1'
            ex.urls['api']['fapiPrivate'] = 'https://testnet.binancefuture.com/fapi/v1'
        else:
            ex.urls['api']['public'] = 'https://demo-api.binance.com/api/v3'
            ex.urls['api']['private'] = 'https://demo-api.binance.com/api/v3'
    return ex, market_m

# ==========================================
# ONE TRADING CYCLE FOR ONE USER
# (this is the exact same logic that used to live inside the Streamlit
#  "while bot_running: ... time.sleep(15); st.rerun()" loop — now it's a
#  plain function so worker.py can call it forever, independent of any
#  browser session)
# ==========================================
def run_bot_cycle(db, curr_user, ex_cache, universe_cache):
    """
    ex_cache / universe_cache: plain dicts the caller keeps across calls,
    e.g. {} passed in from worker.py, so exchange objects / ticker universes
    are reused instead of rebuilt every single cycle (keeps VPS load low).
    Mutates `db` in place and calls save_db where needed. Returns True if
    it did something "actionable" (found + processed a candidate) just for
    logging/telemetry purposes in the caller.
    """
    user_settings = db["settings"].get(curr_user)
    if user_settings is None:
        return False
    _backfill_user(user_settings)
    rt = get_runtime(user_settings)
    rt["last_heartbeat"] = time.time()

    if not rt.get("bot_running"):
        save_db(db)
        return False

    daily_lim = int(user_settings["limits"].get("daily_limit", 1))
    exec_mode_setting = user_settings["strategy"].get("exec_mode", "")
    is_signal_only = "Signal-Only" in exec_mode_setting or "Signal" in exec_mode_setting

    def log(msg):
        add_log(db, curr_user, msg)

    if (not is_signal_only) and rt["trades_today"] >= daily_lim:
        save_db(db)
        return False

    try:
        ex_cfg = user_settings["exchange"]
        cache_entry = ex_cache.get(curr_user)
        need_new_ex = (
            cache_entry is None
            or cache_entry.get("key") != json.dumps(ex_cfg, sort_keys=True)
            or (time.time() - cache_entry.get("loaded_at", 0)) > 900  # refresh markets every 15 min
        )
        if need_new_ex:
            ex, market_m = build_exchange(ex_cfg)
            ex.load_markets()
            ex_cache[curr_user] = {"ex": ex, "market_m": market_m, "loaded_at": time.time(),
                                    "key": json.dumps(ex_cfg, sort_keys=True)}
        else:
            ex = cache_entry["ex"]; market_m = cache_entry["market_m"]

        flt = user_settings.get("filters", DEFAULT_FILTERS)
        _now_ts = time.time()
        _cache_key = (curr_user, int(flt.get("universe_min_volume", 1000000)),
                      tuple(sorted(e.upper() for e in flt.get("exclude", []))))
        u_entry = universe_cache.get(curr_user)
        _cache_fresh = (
            u_entry is not None
            and u_entry.get("key") == _cache_key
            and (_now_ts - u_entry.get("ts", 0)) < UNIVERSE_CACHE_TTL
            and u_entry.get("universe")
        )
        if _cache_fresh:
            universe = u_entry["universe"]
            all_tickers = u_entry.get("tickers")
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
            universe_cache[curr_user] = {"universe": universe, "tickers": all_tickers,
                                          "key": _cache_key, "ts": _now_ts}

        available = [c for c in universe if c not in rt["traded_coins_today"]]
        if not available:
            if is_signal_only:
                rt["traded_coins_today"] = []
                save_db(db)
                available = universe
            else:
                log("Aaj ke available coins khatam. Idling.")
                save_db(db)
                return False

        strategy_mode = user_settings["strategy"].get("mode", "manual")
        chosen_coin = None; c_price = 0.0; matched_rules_str = ""

        if strategy_mode == "manual":
            manual_cfg = user_settings["strategy"]["manual"]
            sample_pool = available[:25] if len(available) >= 25 else available
            candidates = []
            for coin in sample_pool:
                try:
                    passed, rules = evaluate_manual_strategy(ex, coin, manual_cfg, tickers=all_tickers)
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
                log("Manual scan complete — koi coin saari ticked conditions match nahi kar raha. Idling.")
        else:
            log("AI Prompt mode selected hai par koi AI evaluation connect nahi — is mode me trade nahi banegi.")

        if chosen_coin is None:
            save_db(db)
            return False

        ok, reason, db2 = try_reserve_slot(curr_user, chosen_coin, daily_lim, is_signal_only)
        db["settings"][curr_user] = db2["settings"][curr_user]
        user_settings = db["settings"][curr_user]
        rt = get_runtime(user_settings)
        rt["last_heartbeat"] = time.time()

        if ok and not is_signal_only and rt["trades_today"] > daily_lim:
            rt["trades_today"] = daily_lim
            if chosen_coin in rt["traded_coins_today"]:
                rt["traded_coins_today"].remove(chosen_coin)
            save_db(db)
            log(f"Safety rollback: {chosen_coin} reservation undo ki gayi (limit {daily_lim} already reached tha).")
            ok = False
            reason = "limit reached"

        if not ok:
            if reason == "limit reached":
                log(f"Limit reached ({rt['trades_today']}/{daily_lim}) — {chosen_coin} skip. Paused for today.")
            else:
                log(f"{chosen_coin} skip ({reason}). Agla coin dekhenge.")
            save_db(db)
            return False

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
            email_sub = f"Apex Trading — {'Signal Generated' if is_signal_only else 'Trade Executed'}: {chosen_coin}"
            email_body_html = f"""
            <html><body style="font-family: Arial, sans-serif; background-color: #0b0e11; color: #eaecef; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background: #181a20; border: 1px solid #2b313a; border-radius: 12px; padding: 25px;">
                    <h2 style="color: #fcd535; margin-top: 0; text-align: center;">Apex Automated Alert</h2>
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
            send_email_alert(email_sub, email_body_html, email_cfg, log_fn=log)
            save_db(db)

        if is_signal_only:
            log(f"Signal #{rt['signals_today']} generated for {chosen_coin} (rules: {matched_rules_str}).")
            save_db(db)
            return True

        placed_ok = False
        if "Automated Trading" in exec_mode_setting:
            if not (ex_cfg.get("connected") and ex_cfg.get("key")):
                log(f"{chosen_coin}: exchange not connected — real order skip, signal recorded. (Slot consumed to keep limit safe.)")
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
                        log(f"Spot Market Buy Executed for {chosen_coin} (rules: {matched_rules_str})")
                    except Exception as buy_err:
                        log(f"Buy Order Error: {str(buy_err)}"); buy_res = None
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
                                log(f"OCO placed — TP ${formatted_tp_price} / SL ${formatted_sl_price}")
                                oco_done = True
                            except Exception as oco_err:
                                log(f"OCO not available ({str(oco_err)[:70]}), trying separate SL/TP...")
                        if not oco_done:
                            try:
                                ex.create_order(chosen_coin, 'STOP_LOSS_LIMIT', 'sell', sell_qty, sl_limit_price, {'stopPrice': formatted_sl_price})
                                log(f"Stop Loss placed at trigger ${formatted_sl_price}")
                            except Exception:
                                try:
                                    ex.create_order(chosen_coin, 'STOP_LOSS', 'sell', sell_qty, None, {'stopPrice': formatted_sl_price})
                                    log(f"Stop Loss (Market) placed at trigger ${formatted_sl_price}")
                                except Exception as sl_fallback_err:
                                    log(f"Stop Loss Order Warning: {str(sl_fallback_err)}")
                            try:
                                bal2 = ex.fetch_balance()
                                free2 = float(bal2['free'].get(base_ccy, 0) or 0)
                                tp_qty = float(ex.amount_to_precision(chosen_coin, free2)) if free2 > 0 else 0
                                if tp_qty > 0:
                                    ex.create_limit_sell_order(chosen_coin, tp_qty, formatted_tp_price)
                                    log(f"Take Profit placed at ${formatted_tp_price}")
                            except Exception as tp_err:
                                log(f"TP Order Warning: {str(tp_err)}")
                else:
                    try:
                        ex.create_market_buy_order(chosen_coin, coin_qty); placed_ok = True
                        log(f"Futures Market Buy executed for {chosen_coin} (rules: {matched_rules_str})")
                        time.sleep(1)
                        ex.create_order(chosen_coin, 'TAKE_PROFIT_MARKET', 'sell', coin_qty, None, {'stopPrice': formatted_tp_price, 'reduceOnly': True})
                        log(f"Futures Take Profit set at ${formatted_tp_price}")
                        ex.create_order(chosen_coin, 'STOP_MARKET', 'sell', coin_qty, None, {'stopPrice': formatted_sl_price, 'reduceOnly': True})
                        log(f"Futures Stop Loss set at ${formatted_sl_price}")
                    except Exception as fut_err:
                        log(f"Futures TP/SL note: {str(fut_err)}")

        user_settings.setdefault("active_trades", []).append({
            "Symbol": chosen_coin, "Market": market_m,
            "Entry": f"{c_price:,.6f}", "Amount": f"${amt_usdt}",
            "TP": f"{tp_val:,.6f}", "SL": f"{sl_val:,.6f}", "Rules": matched_rules_str
        })
        log(f"Auto trade {rt['trades_today']}/{daily_lim} done for {chosen_coin}"
            f"{'' if placed_ok else ' (signal only — no live order)'}.")
        if rt["trades_today"] >= daily_lim:
            log(f"Aaj ki limit ({daily_lim}) complete. Bot ab kal tak naye auto-trade nahi lega.")
        save_db(db)
        return True

    except Exception as e:
        log(f"Loop Error: {str(e)}")
        save_db(db)
        return False