#!/usr/bin/env python3
"""
Trent Bridge Ticket Exchange Monitor
Checks for available resale tickets and sends a ntfy.sh notification.
Runs as a GitHub Actions cron job every 10 minutes.
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
NTFY_TOPIC = "trent-bridge-tickets-karthikkp"  # Subscribe at ntfy.sh/trent-bridge-tickets-karthikkp
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"
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
    """Save state to file in repo."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def send_ntfy(title, message, priority="high", tags="cricket,ticket"):
    """Send notification via ntfy.sh."""
    data = message.encode("utf-8")
    req = urllib.request.Request(NTFY_URL, data=data, headers={
        "Title": title.encode("utf-8").decode("latin-1", errors="replace"),
        "Priority": priority,
        "Tags": tags,
        "Click": CHECK_URL,
        "Content-Type": "text/plain; charset=utf-8",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"  ntfy notification sent (status: {resp.status})")
            return True
    except Exception as e:
        print(f"  ntfy send error: {e}", file=sys.stderr)
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
            print(f"🚨 {message}")
            send_ntfy(
                title="TRENT BRIDGE TICKETS AVAILABLE!",
                message=f"Tickets detected on the exchange!\n\nEng vs Ind IT20 - Tue 7 July 2026, 5:30pm\n\nMove fast: {CHECK_URL}",
                priority="urgent",
                tags="cricket,ticket,urgent"
            )
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
    if "--test" in sys.argv:
        # Test mode: send a notification without checking the site
        print("🧪 TEST MODE: Sending test notification via ntfy.sh...")
        send_ntfy(
            title="TEST - Trent Bridge Monitor Working!",
            message="This is a test from GitHub Actions. You'll get a real alert when tickets appear.\n\nEng vs Ind IT20 - Tue 7 July 2026",
            priority="default",
            tags="cricket,test"
        )
        print("✅ Test notification sent. Check your phone!")
    else:
        main()