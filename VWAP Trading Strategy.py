# ================================
# VWAP TREND TRADING — FINAL VERSION
# ================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# ----------------
# USER SETTINGS
# ----------------
API_KEY = "PKOOK5K4PNPGFGES4PPWPTOQAB"
API_SECRET = "37RfLQQ2xtvXFztAsYtgzAvQYvfjQhLQrpmkZjNdHuBu"

SYMBOL = "QQQ"
START_DATE = "2021-02-01"
END_DATE = "2026-02-01"

INITIAL_CAPITAL = 100000
COMMISSION_PER_SHARE = 0.0005

# ================================
# DOWNLOAD DATA
# ================================

print("Downloading data...")

client = StockHistoricalDataClient(API_KEY, API_SECRET)

request = StockBarsRequest(
    symbol_or_symbols=SYMBOL,
    timeframe=TimeFrame.Minute,
    start=pd.Timestamp(START_DATE, tz="UTC"),
    end=pd.Timestamp(END_DATE, tz="UTC"),
)

bars = client.get_stock_bars(request).df.reset_index()

# ================================
# PREP DATA
# ================================

df = bars.copy()

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

df["timestamp"] = df["timestamp"].dt.tz_convert("America/New_York")
df = df.set_index("timestamp")

df = df.between_time("09:30", "16:00")
df["date"] = df.index.date

# ================================
# VWAP
# ================================

df["hlc"] = (df["high"] + df["low"] + df["close"]) / 3
df["hlc_vol"] = df["hlc"] * df["volume"]

df["cum_hlc_vol"] = df.groupby("date")["hlc_vol"].cumsum()
df["cum_vol"] = df.groupby("date")["volume"].cumsum()
df["vwap"] = df["cum_hlc_vol"] / df["cum_vol"]

# ================================
# BACKTEST
# ================================

capital = INITIAL_CAPITAL
equity_curve = []
trades = []

position = 0
shares = 0
entry_price = 0

for day, day_df in df.groupby("date"):

    day_df = day_df.reset_index(drop=True)

    for i in range(1, len(day_df)):

        price = day_df.loc[i, "close"]
        prev_price = day_df.loc[i-1, "close"]
        vwap = day_df.loc[i, "vwap"]
        prev_vwap = day_df.loc[i-1, "vwap"]

        cross_up = (prev_price <= prev_vwap) and (price > vwap)
        cross_down = (prev_price >= prev_vwap) and (price < vwap)

        if position == 0:

            if cross_up or cross_down:
                shares = int(capital // price)
                if shares == 0:
                    continue
                entry_price = price
                position = 1 if cross_up else -1

        elif position == 1 and cross_down:

            pnl = shares * (price - entry_price)
            commission = shares * COMMISSION_PER_SHARE * 2
            capital += pnl - commission
            trades.append(pnl - commission)

            shares = int(capital // price)
            entry_price = price
            position = -1

        elif position == -1 and cross_up:

            pnl = shares * (entry_price - price)
            commission = shares * COMMISSION_PER_SHARE * 2
            capital += pnl - commission
            trades.append(pnl - commission)

            shares = int(capital // price)
            entry_price = price
            position = 1

    if position != 0:
        price = day_df.iloc[-1]["close"]
        pnl = shares * (price - entry_price) if position == 1 else shares * (entry_price - price)
        commission = shares * COMMISSION_PER_SHARE * 2
        capital += pnl - commission
        trades.append(pnl - commission)

        position = 0
        shares = 0

    equity_curve.append(capital)

# ================================
# PERFORMANCE
# ================================

equity_series = pd.Series(equity_curve)
returns = equity_series.pct_change().dropna()

sharpe = np.sqrt(252) * returns.mean() / returns.std()
volatility = returns.std() * np.sqrt(252)
sortino = np.sqrt(252) * returns.mean() / returns[returns < 0].std()

rolling_max = equity_series.cummax()
drawdown = equity_series / rolling_max - 1
max_dd = drawdown.min()

years = len(equity_series) / 252
cagr = (equity_series.iloc[-1] / INITIAL_CAPITAL) ** (1/years) - 1

win_rate = (np.array(trades) > 0).mean() if trades else 0

# ================================
# BUY & HOLD
# ================================

daily_close = df.groupby("date")["close"].first()
bh_shares = INITIAL_CAPITAL // daily_close.iloc[0]
bh_equity_series = (bh_shares * daily_close).reset_index(drop=True)

bh_returns = bh_equity_series.pct_change().dropna()
bh_sharpe = np.sqrt(252) * bh_returns.mean() / bh_returns.std()
bh_volatility = bh_returns.std() * np.sqrt(252)
bh_sortino = np.sqrt(252) * bh_returns.mean() / bh_returns[bh_returns < 0].std()

bh_roll = bh_equity_series.cummax()
bh_drawdown = bh_equity_series / bh_roll - 1

bh_years = len(bh_equity_series) / 252
bh_cagr = (bh_equity_series.iloc[-1] / INITIAL_CAPITAL) ** (1/bh_years) - 1

# ================================
# PRINT RESULTS
# ================================

print("\n===== STRATEGY =====")
print(f"Final Capital: ${capital:,.2f}")
print(f"CAGR: {cagr:.2%}")
print(f"Sharpe: {sharpe:.2f}")
print(f"Sortino: {sortino:.2f}")
print(f"Volatility: {volatility:.2%}")
print(f"Max Drawdown: {max_dd:.2%}")
print(f"Win Rate: {win_rate:.2%}")
print(f"Trades: {len(trades)}")

print("\n===== BUY & HOLD =====")
print(f"Final Capital: ${bh_equity_series.iloc[-1]:,.2f}")
print(f"CAGR: {bh_cagr:.2%}")
print(f"Sharpe: {bh_sharpe:.2f}")
print(f"Sortino: {bh_sortino:.2f}")
print(f"Volatility: {bh_volatility:.2%}")
print(f"Max Drawdown: {bh_drawdown.min():.2%}")

# ================================
# PLOTS
# ================================

plt.figure(figsize=(12,5))
plt.plot(equity_series, label="VWAP Strategy")
plt.plot(bh_equity_series, linestyle="--", label="Buy & Hold")
plt.legend()
plt.title("Equity Curve Comparison")
plt.show()

plt.figure(figsize=(12,4))
plt.plot(drawdown, label="VWAP Strategy")
plt.plot(bh_drawdown, linestyle="--", label="Buy & Hold")
plt.legend()
plt.title("Drawdown Comparison")
plt.show()

plt.figure(figsize=(10,4))
plt.hist(trades, bins=40)
plt.title("Trade PnL Distribution")
plt.show()
