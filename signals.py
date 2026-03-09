import pandas as pd
from datetime import datetime
from .config import *
from .indicators import calculate_hurst, calculate_rsi

# --- SENAL FRACTAL GUARD ---
def get_signal(symbol, df_m15, df_h1, markov_state=1, markov_probs=None):
      hurst = calculate_hurst(df_m15["close"].values)
      ema200_m15 = df_m15["close"].ewm(span=200, adjust=False).mean().iloc[-1]
      ema200_h1 = df_h1["close"].ewm(span=200, adjust=False).mean().iloc[-1]
      last = df_m15["close"].iloc[-1]
      rsi = calculate_rsi(df_m15["close"])

    up, down = (last > ema200_m15 and last > ema200_h1), (last < ema200_m15 and last < ema200_h1)
    if hurst > HURST_THRESHOLD:
              if up and 30 < rsi < 70: return "BUY", "Trend M15"
                        if down and 30 < rsi < 70: return "SELL", "Trend M15"
                              return "WAIT", ""

# --- SCALPER ELITE ---
def get_scalper_signal(symbol, df_m5):
      ema8 = df_m5["close"].ewm(span=SCALPER_FAST_EMA, adjust=False).mean()
    ema21 = df_m5["close"].ewm(span=SCALPER_SLOW_EMA, adjust=False).mean()
    ema50 = df_m5["close"].ewm(span=SCALPER_TREND_EMA, adjust=False).mean()
    rsi = calculate_rsi(df_m5["close"])

    buy = (ema8.iloc[-2] < ema21.iloc[-2] and ema8.iloc[-1] > ema21.iloc[-1])
    sell = (ema8.iloc[-2] > ema21.iloc[-2] and ema8.iloc[-1] < ema21.iloc[-1])

    if buy and df_m5["close"].iloc[-1] < ema50.iloc[-1] and rsi < SCALPER_RSI_UPPER: return "BUY", "Scalper Cross"
          if sell and df_m5["close"].iloc[-1] > ema50.iloc[-1] and rsi > SCALPER_RSI_LOWER: return "SELL", "Scalper Cross"
                return "WAIT", ""

# --- SNIPER ORO (V29.5) ---
def get_gold_signal(symbol, df_m5, df_h1, range_high, range_low, last_trade_ts):
      now = datetime.now()
    if (now.timestamp() - last_trade_ts) < 15 * 60: return "WAIT", "Time-Lock"

    hurst = calculate_hurst(df_m5["close"].values)
    rsi = calculate_rsi(df_m5["close"])
    ema200_h1 = df_h1["close"].ewm(span=200, adjust=False).mean().iloc[-1]
    last_h1 = df_h1["close"].iloc[-1]
    last_close = df_m5["close"].iloc[-1]

    if hurst > HURST_THRESHOLD:
              if df_m5["high"].iloc[-2] > range_high and last_close < range_high and rsi > 75 and last_h1 < ema200_h1:
                            return "SELL", "Sniper Trend"
                        if df_m5["low"].iloc[-2] < range_low and last_close > range_low and rsi < 30 and last_h1 > ema200_h1:
                                      return "BUY", "Sniper Trend"
elif hurst < HURST_REVERSION_THRESHOLD:
        if last_close < range_low and rsi < 20: return "BUY", "Sniper Range"
                  if last_close > range_high and rsi > 80: return "SELL", "Sniper Range"
                        return "WAIT", ""
