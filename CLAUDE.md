# CLAUDE.md — Project 316

## Overview

This project provides Python scripts to interact with the **Facebook Ads API** (Meta Business SDK). It fetches ad account data, campaign metrics, and insights, and outputs formatted reports to the terminal.

## Project Structure

```
316/
├── ads_api.py           # Low-level API wrapper: accounts, campaigns, insights
├── analyze_campaigns.py # High-level 30-day campaign analysis with rankings
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (not committed)
```

## Setup

### Requirements

- Python 3.8+
- A valid Facebook Access Token with `ads_read` permission

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```
FB_ACCESS_TOKEN=your_facebook_access_token_here
```

## Running the Scripts

### Basic API Test & Account Listing

```bash
python ads_api.py
```

Connects to the API, lists all ad accounts with status, currency, and total spend, then shows campaigns and 7-day insights for the first account.

### 30-Day Campaign Analysis

```bash
python analyze_campaigns.py
```

Prompts you to select an ad account (or analyze all), then prints:
- Overall summary: total spend, reach, impressions, clicks, avg CTR, CPM, leads/CPL, purchases/CPP
- Per-campaign breakdown: spend, reach, impressions, frequency, clicks, CTR, CPC, CPM, leads, purchases
- Rankings: best/worst CTR, highest spend, best/worst CPL

## Key Functions

| File | Function | Description |
|------|----------|-------------|
| `ads_api.py` | `init_api()` | Initializes the Facebook SDK with the access token |
| `ads_api.py` | `get_ad_accounts()` | Returns all ad accounts for the authenticated user |
| `ads_api.py` | `get_campaigns(account_id)` | Returns campaigns for a given account |
| `ads_api.py` | `get_insights(account_id, date_preset)` | Returns account-level insights |
| `analyze_campaigns.py` | `get_campaign_insights_30d(account_id)` | Fetches campaign-level insights for last 30 days |
| `analyze_campaigns.py` | `analyze(account_id, currency)` | Runs and prints the full analysis report |

## Dependencies

| Package | Purpose |
|---------|---------|
| `facebook-business` | Meta Business SDK for Ads API |
| `python-dotenv` | Load environment variables from `.env` |

## Notes

- The scripts print output in Portuguese (Brazil).
- Currency formatting defaults to BRL (`R$`); other currencies use `$`.
- The `date_preset` values follow the Facebook Ads API specification (e.g., `last_7d`, `last_30d`).
- No test suite is currently configured.
