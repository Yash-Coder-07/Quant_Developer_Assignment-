# 📊 Real-Time Quantitative Analytics Dashboard

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Binance](https://img.shields.io/badge/Data-Binance_WebSocket-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## 📖 Project Overview

This project is a complete **end-to-end quantitative trading analytics dashboard** developed for the **Quant Developer Evaluation Assignment**.

It implements a **Statistical Arbitrage (Pairs Trading)** strategy on the **BTCUSDT / ETHUSDT** pair. The system ingests real-time tick data from Binance, stores it in a thread-safe local database, calculates cointegration metrics (Hedge Ratio, Z-Score, ADF Test) on-the-fly, and visualizes trading signals in a reactive **Streamlit dashboard**.

---

## 🏗️ Architecture & Design

<img width="1899" height="314" alt="image" src="https://github.com/user-attachments/assets/c19efc8b-af4b-4d61-b1cf-00d805095e26" />


### 🔑 Key Design Decisions

* **Asynchronous Ingestion**
  Uses `asyncio` and `aiohttp` to handle high-throughput WebSocket streams without blocking.

* **Thread-Safe Storage**
  SQLite is configured in **WAL (Write-Ahead Logging)** mode to allow concurrent writes (ingestion) and reads (dashboard).

* **Modular Analytics**
  Mathematical logic is isolated in `analytics/calculations.py`, making it testable and reusable independent of the UI.

* **Cold Start Handling**
  The dashboard displays a *System Warming Up* state until sufficient historical bars (≈20–30 minutes) are collected.

---

## ⚙️ Setup & Installation

### 1️⃣ Prerequisites

* Python **3.8+**
* Git

### 2️⃣ Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/Yash-Coder-07/Quant_Developer_Assignment-.git
cd Quant_Developer_Assignment-

# Create virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 How to Run

### ✅ Method 1: Unified Launcher (Recommended)

Automatically runs both the ingestion service and the Streamlit dashboard.

```bash
python run.py
```

---

### 🧪 Method 2: Manual Execution (Debug Mode)

Run backend and frontend in separate terminals.

**Terminal 1 — Data Ingestion**

```bash
python websocket_ingestion.py
```

**Terminal 2 — Dashboard**

```bash
streamlit run dashboard.py
```

> ⚠️ **First Run Note**
> On initial startup, the database is empty. The dashboard will display **“System Warming Up”** for the first 2–3 minutes while sufficient 1-minute candles are accumulated.

---

## 🧮 Quantitative Methodology

The strategy is based on **mean reversion** between two cointegrated assets.

---

### 1️⃣ Hedge Ratio (β)

Calculated dynamically using **Rolling OLS (Ordinary Least Squares)** regression:

$$
P_A = \alpha + \beta P_B + \epsilon
$$

---

### 2️⃣ Spread

Represents deviation from the equilibrium relationship between the two assets:

$$
\text{Spread}_t = P_{A,t} - \beta P_{B,t}
$$


---

### 3️⃣ Z-Score (Trading Signal)

Normalizes the spread across different volatility regimes:

$$
Z_t = \frac{\text{Spread}_t - \mu_{\text{spread}}}{\sigma_{\text{spread}}}
$$

**Signal Logic**

- 📈 **Buy:** \( Z < -2.0 \) → Spread undervalued  
- 📉 **Sell:** \( Z > 2.0 \) → Spread overvalued

---

### 4️⃣ Stationarity Test (ADF)

An **Augmented Dickey-Fuller (ADF)** test is applied to the spread series.

* **p-value < 0.05** ⇒ Stationary & tradable pair

---

## 📂 Project Structure

```text
QUANTATIVE_DEVELOPER/
├── analytics/                  # Core Math & Data Logic
│   ├── calculations.py         # OLS, Z-Score, ADF implementation
│   ├── core.py                 # Analytics orchestrator
│   └── data_processing.py      # Tick → OHLC resampling
├── charts/                     # Plotly visualization modules
│   ├── analysis.py             # Z-Score & Spread charts
│   └── trading.py              # Price overlays & volume
├── components/                 # UI widgets
│   ├── metrics.py              # KPI cards
│   └── sidebar.py              # User controls
├── dashboard.py                # Streamlit entry point
├── database.py                 # SQLite wrapper (thread-safe)
├── run.py                      # Unified application launcher
├── websocket_ingestion.py      # Async Binance WebSocket client
├── requirements.txt            # Project dependencies
└── README.md                   # Documentation
```

## Results
-  📈 **Buy Signal Triggred (For demonstration z-score threshold value adjusted):**
<img width="1919" height="811" alt="Screenshot 2025-12-17 011143" src="https://github.com/user-attachments/assets/4da5ea86-f9ba-41af-a7a7-5e984ac7ca91" />


- 📉 **Sell Signal Triggred (For demonstration z-score threshold value adjusted):**
<img width="1872" height="848" alt="Screenshot 2025-12-17 004314" src="https://github.com/user-attachments/assets/4b49512a-5e52-48f6-9e23-1eb72d4488c5" />


##  AI Usage Transparency

In compliance with the assignment guidelines, generative AI tools (ChatGPT, Cursor) were used **only** for:

1. **Project scaffolding** (initial directory structure).
2. **Async WebSocket logic assistance** (reconnection handling).
3. **Plotly visualization configuration** (dual Y-axis charts).

---

### 📈 Designed for Quantitative Developer Evaluation



















