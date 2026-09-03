"""
worker.py
Run this as a SEPARATE, always-on process on your VPS:

    python3 worker.py
    # ya better, so it survives SSH disconnect / reboot:
    tmux new -s apexworker
    python3 worker.py
    # (Ctrl+B then D to detach — it keeps running)

    # ya production ke liye systemd service bana lo:
    # /etc/systemd/system/apex-worker.service
    #   [Unit]
    #   Description=Apex Trading Worker
    #   After=network.target
    #   [Service]
    #   WorkingDirectory=/path/to/your/app
    #   ExecStart=/usr/bin/python3 worker.py
    #   Restart=always
    #   [Install]
    #   WantedBy=multi-user.target
    # then: sudo systemctl enable --now apex-worker

This process does NOT depend on any browser tab, login session, or
Streamlit at all. It just watches the shared database.json file and
trades for every user whose "bot_running" flag (set from the app's
START/STOP buttons) is True — until you press STOP or close nothing
at all, because closing your phone/laptop no longer matters.
"""
import time
import traceback
import apex_core as core

TICK_SECONDS = 15   # how often the whole user-list is scanned

def main():
    print("Apex worker started. Watching", core.DB_FILE)
    ex_cache = {}
    universe_cache = {}
    while True:
        try:
            db = core.load_db()
            any_running = False
            for username, cfg in list(db.get("settings", {}).items()):
                core._backfill_user(cfg)
                rt = core.get_runtime(cfg)
                if rt.get("bot_running"):
                    any_running = True
                    try:
                        core.run_bot_cycle(db, username, ex_cache, universe_cache)
                    except Exception as e:
                        core.add_log(db, username, f"Worker error: {e}")
                        core.save_db(db)
                else:
                    # keep heartbeat honest even when idle, so UI doesn't show stale "alive"
                    rt["last_heartbeat"] = time.time()
            core.save_db(db)
            if not any_running:
                # nobody has the bot on right now — sleep a bit longer to save CPU
                time.sleep(min(TICK_SECONDS * 2, 30))
            else:
                time.sleep(TICK_SECONDS)
        except Exception:
            print("Worker top-level error:\n", traceback.format_exc())
            time.sleep(TICK_SECONDS)

if __name__ == "__main__":
    main()