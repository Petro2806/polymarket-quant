import os
import time
import json
from pathlib import Path
import requests



BASE_URL = "https://data-api.polymarket.com/trades"



DATA_DIR = Path(os.getenv("POLYMARKET_DATA_DIR", "/data"))
RAW_DIR = DATA_DIR / "raw"
STATE_FILE = DATA_DIR / "state.json"
RAW_DIR.mkdir(parents=True, exist_ok=True)



MARKETS_ENV = os.getenv("POLYMARKET_MARKETS", "")
if not MARKETS_ENV:
    raise SystemExit("POLYMARKET_MARKETS env var is empty. Set comma-separated conditionIds.")
MARKETS = [m.strip() for m in MARKETS_ENV.split(",") if m.strip()]

POLL_SECONDS = int(os.getenv("POLYMARKET_POLL_SECONDS", "60"))




def load_state() -> dict:
    """
    State format:
    {
        "markets": {
            "<conditionId>": {
                "last_ts": 1234567890
            },
            ...
        }
    }
    """
    if not STATE_FILE.exists():
        return {"markets": {}}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {"markets": {}}


def save_overall_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state))


def fetch_trades_for_market(condition_id: str, last_ts: int) -> list:
    params = {
        "market": condition_id,
        "limit": 1000,      # max history per request
    }

    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    trades = resp.json()


    new_trades = [
        tr for tr in trades
        if tr.get("timestamp", 0) > last_ts
    ]

    return new_trades


def append_trades(condition_id: str, trades: list) -> None:
    if not trades:
        return
    out_path = RAW_DIR / f"trades_{condition_id}.jsonl"
    with out_path.open("a") as f:
        for tr in trades:
            f.write(json.dumps(tr) + "\n")


def main_loop():
    print(f"Starting collector for markets: {MARKETS}")
    print(f"Polling every {POLL_SECONDS} seconds")
    state = load_state()
    markets_state = state.setdefault("markets", {})

    while True:
        try:
            for condition_id in MARKETS:
                current_state = markets_state.get(condition_id, {})
                last_ts = int(current_state.get("last_ts", 0))

                trades = fetch_trades_for_market(condition_id, last_ts)
                if trades:
                    new_last_ts = max(tr["timestamp"] for tr in trades)
                    markets_state[condition_id] = {"last_ts": new_last_ts}

                    append_trades(condition_id, trades)
                    print(f"[{condition_id}] fetched {len(trades)} new trades, last_ts={new_last_ts}")
                else:
                    print(f"[{condition_id}] no new trades")

            save_overall_state(state)

        except requests.RequestException as e:
            print(f"Request error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main_loop()
