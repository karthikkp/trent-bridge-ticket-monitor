# Trent Bridge Ticket Monitor

Checks the [Trent Bridge Ticket Exchange](https://ticketexchange.trentbridge.co.uk/list/resaleProducts/) for available resale tickets and sends a Telegram alert when tickets appear.

## What it does

- Runs every 10 minutes via GitHub Actions
- Scrapes the Trent Bridge official ticket exchange page
- When tickets become available, sends a Telegram message
- Only alerts once per availability window (resets when tickets sell out again)
- Persists state via GitHub Gist so it remembers across runs

## Setup

1. Create a GitHub Gist with an empty JSON file called `trent_bridge_state.json` containing `{}`. Copy the Gist ID (from the URL).

2. Add these secrets to the GitHub repo (Settings → Secrets and variables → Actions):
   - `TELEGRAM_BOT_TOKEN` — Your Telegram bot token
   - `TELEGRAM_CHAT_ID` — Your Telegram chat ID (default: 7985595751)
   - `GIST_ID` — The Gist ID from step 1
   - `GH_PAT` — A GitHub personal access token with `gist` scope

3. Enable GitHub Actions in the repo settings.

## Manual trigger

Go to Actions tab → "Trent Bridge Ticket Monitor" → "Run workflow"