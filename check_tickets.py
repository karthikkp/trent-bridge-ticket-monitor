#!/usr/bin/env python3
"""
Trent Bridge Ticket Exchange Monitor
Checks for available resale tickets and sends a Telegram notification.
Runs as a GitHub Actions cron job. Persists state in the repo itself.
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

# --- Config ---
CHECK_URL = "https://ticketexchange.trentbridge.co.uk/list/resaleProducts/"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "7985595751")
STATE_FILE = "state.json"


def fetch_page(url):
    """Fetch the ticket exchange page."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        print(f"Error fetching page: {e}", file=sys.stderr)
        return None


def check_availability(html):
    """Check if there are tickets available (not just the 'no tickets' message)."""
    if not html:
        return False, "Failed to fetch page"

    no_tickets_pattern = r"there are currently no tickets being resold"
    if re.search(no_tickets_pattern, html, re.IGNORECASE):
        return False, "No tickets currently available"

    product_pattern = r'(resaleProduct|ticket.*available|Add to cart|Select|seat|stand)'
    if re.search(product_pattern, html, re.IGNORECASE):
        return True, "Tickets may be available!"

    return False, "Page loaded but status unclear - manual check recommended"


def load_state():
    """Load previous state from file in repo."""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"last_available": None, "last_check": None, "already_alerted": False}


def save_state(state):
    """Save state to file in repo (for commit-based persistence in Actions)."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def send_telegram(message):
    """Send notification via Telegram."""
    if not TELEGRAM_BOT_TOKEN:
        print(f"Telegram not configured. Message: {message}", file=sys.stderr)
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }).encode()

    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result.get("ok", False)
    except Exception as e:
        print(f"Telegram send error: {e}", file=sys.stderr)
        return False


def main():
    now = datetime.now(timezone.utc).isoformat()
    state = load_state()

    print(f"[{now}] Checking Trent Bridge Ticket Exchange...")

    html = fetch_page(CHECK_URL)
    available, message = check_availability(html)

    state["last_check"] = now

    if available:
        if not state.get("already_alerted", False):
            alert_msg = (
                f"🏏 *TRENT BRIDGE TICKETS AVAILABLE!*\n\n"
                f"Tickets detected on the exchange!\n\n"
                f"👉 Check now: {CHECK_URL}\n\n"
                f"Eng vs Ind IT20 — Tue 7 July 2026, 5:30pm\n"
                f"Move fast — face value tickets get snapped up quickly!"
            )
            print(f"🚨 {message}")
            send_telegram(alert_msg)
            state["already_alerted"] = True
        else:
            print(f"✅ {message} (already alerted)")
        state["last_available"] = now
    else:
        state["already_alerted"] = False
        print(f"  {message}")

    save_state(state)
    print(f"  Check complete.")


if __name__ == "__main__":
    main()