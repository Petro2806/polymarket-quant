# Polymarket Quantitative Research Assignment

This repository contains my solution and experiments for a **Polymarket quantitative research**.

The project is split into three main parts:

1. **Core data analysis** on the given dataset.
2. **Design of a simple market-making model** suitable for Polymarket.
3. **A minimal simulation setup**, plus a sketch of how I would connect it to live Polymarket data to get closer to “real” market making.

The overall task description is in [`task.txt`](task.txt).

---

## 1. Core data analysis on the provided dataset

For the assignment I use a dataset [`polymarket-data-basic-all-markets.csv`](data/given/polymarket-data-basic-all-markets.csv).  
I checked that each row is a unique *market* (identified by columns like `question` / `market_slug` / `condition_id`).

### 1.1 Spread & liquidity

For each market I:

- use the `best_bid` and `best_ask` columns to compute:
  - **absolute spread** = `best_ask - best_bid`
- rank markets by spread:
  - top-3 markets with the **tightest** spreads,
  - top-3 markets with the **widest** spreads.
- give a short interpretation of what the spread says about:
  - **liquidity**,
  - **competition between MMs**,
  - **expected edge**.

### 1.2 Volatility

In the provided sheet there is no time-series data for each market (only aggregate columns such as `volatility_sum`, `1_hour`, `3_hour`, `24_hour`, etc.). Because of that:

- I **cannot** recompute a true 3-hour rolling volatility from raw mid-price history for a given market.
- Instead, I:
  - rely on the pre-computed volatility-related columns in the dataset,
  - treat them as **aggregated volatility proxies**,
  - rank markets by these measures and discuss how volatility affects:
    - inventory risk,
    - spread selection,
    - when it makes sense to widen or tighten quotes.

### 1.3 Flow & drift

The provided dataset does **not** contain time-series events over time for each market. So:

- I can define and discuss:
  - what **net taker flow** means conceptually,
  - why persistent flow imbalance is important for a MM,
- but I **cannot** run a proper empirical test on this exact file.

---

## 2. Strategy design

In a separate notebook [`strategy-design.ipynb`](scripts/strategy-design.ipynb) I sketch a simple, realistic Polymarket market-making model.  
The main components:

### 2.1 Quoting logic

(High-level quoting rules and spread adjustments are explained in the notebook.)

### 2.2 Inventory control

(Maximum inventory, rebalancing rules and pause conditions are described in the notebook.)

### 2.3 Refresh rules

(Definition of “material” price moves and refresh vs keep logic is also described in the notebook.)

---

## 3. Minimal simulation

The last part of the task is a **lightweight simulation**.

Conceptually, I do the following:

0. **Get a time-series per market** from Polymarket:
   - I use the Polymarket API to get trades.
   - I created a Docker container to update the list of trades in almost real time.
   - In that container I can adjust how frequently to poll data and for which markets.

1. **Build a time-series per market**:
   - I work with Polymarket trades (one JSON line per trade) with fields like:
     - `timestamp`, `price`, `side`, `size`, `conditionId`, etc.
   - For each chosen `conditionId` I build a DataFrame with:
     - `timestamp_datetime`,
     - `mid_price` (here: trade price, as a proxy),
     - `rolling volatility`.

2. **Simulate a simple MM** over this time-series:
   - For each trade I:
     - compute my current bid/ask using the quoting + volatility + inventory logic,
     - apply a *crossing rule*:
       - if taker is `BUY`, I **sell** to them at my `ask` (if inventory allows),
       - if taker is `SELL`, I **buy** from them at my `bid`.
   - Track:
     - inventory,
     - cash,
     - mark-to-market PnL (`cash + inventory * mid_price`),
     - spread quoted,
     - which trades I actually got filled on.

3. At the end I compute:
   - **Net PnL**
   - **Maximum |inventory|**
   - **Average spread quoted**
   - **Average volatility in rolling window**

---

## 4. Sketch for live Polymarket data & “real” MM

To get closer to the **bonus** part (“running real market making on Polymarket”), I outline how I would connect this project to live data.

### 4.1 Recording trades

The idea is:

- Use Polymarket’s public APIs to download recent trades for a set of chosen `conditionId`s.
- Save them as JSON/JSONL files locally, e.g. in `data/raw/`:
  - `trades_<conditionId>.jsonl`
- Periodically append new trades as they appear.

Currently this trade collection is implemented via a Docker container.

### 4.2 Using simulation logic on live data

To plug the simulation into “online” data, I would:

1. Take the logic from [`basic-simulation.ipynb`](polymarket-mm/src/simulation/basic-simulation.ipynb) and refactor it so that:
   - there is a **pure function** that processes **one event / trade**  
     (update inventory, cash, quotes, internal state).
2. Store the MM state between calls in a state file in the `data/processed` folder.
3. When a new trade arrives from the data-collection process (Docker container):
   - parse the trade into a standard record,
   - pass it to the “one-event” function,
   - immediately get updated MM state and decide what actions to take next.

This design would allow the same code to be used both:

- in **offline mode** (run over a historical JSONL file for simulation), and  
- in a **near-real-time mode** (process one trade at a time as a stream).

---

## 5. How to run the code

**Data analysis** can be run using the notebook [`data-analysis.ipynb`](scripts/data-analysis.ipynb).

For **MM simulation** you need to start the data-mining container:

1. Choose markets to monitor:
   - Put conditionIds into [`docker-compose.yml`](polymarket-mm/docker-compose.yml).
   - Put the same conditionIds into [`basic-simulation.ipynb`](polymarket-mm/src/simulation/basic-simulation.ipynb) (in corresponding config section).

2. In folder [`polymarket-mm`](polymarket-mm) run in bash terminal:
   - ```docker-compose up --build -d```
   - You will get trades, and the container will try to keep your dataset updated.
   - If you do not need to update the dataset anymore, you can stop the container with
     - ```docker-compose down```

3. Run [`basic-simulation.ipynb`](polymarket-mm/src/simulation/basic-simulation.ipynb) to see MM statistics for the chosen markets.
