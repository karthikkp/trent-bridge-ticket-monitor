# Trent Bridge Ticket Monitor 🏏

Monitors the [Trent Bridge Ticket Exchange](https://ticketexchange.trentbridge.co.uk/list/resaleProducts/) for available resale tickets (Eng vs Ind IT20, Tue 7 July 2026) and sends push notifications via [ntfy.sh](https://ntfy.sh).

## How it works

- Runs every **10 minutes** via GitHub Actions
- Checks the official Trent Bridge ticket exchange page
- When tickets become available, sends an **urgent push notification** via ntfy.sh
- Only alerts once per availability window (resets when tickets sell out again)
- Persists state in `state.json` (committed back to the repo after each run)

## Set up notifications on your phone

1. Install the **ntfy** app ([iOS](https://apps.apple.com/app/ntfy/id1625396343) / [Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy))
2. Open the app and tap **+** to subscribe to a topic
3. Subscribe to: **`trent-bridge-tickets-karthikkp`**
4. That's it — you'll get a push notification the moment tickets appear

You can also test it right now by visiting: [https://ntfy.sh/trent-bridge-tickets-karthikkp](https://ntfy.sh/trent-bridge-tickets-karthikkp)

## Manual trigger

Go to **Actions** → "Trent Bridge Ticket Monitor" → "Run workflow"