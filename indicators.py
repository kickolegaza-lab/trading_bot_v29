import numpy as np
import pandas as pd
import MetaTrader5 as mt5

# --- ANALISIS FRACTAL (EXPONENTE DE HURST) ---
def calculate_hurst(series, min_lags=4, max_lags=20):
      prices = np.array(series, dtype=float)
      if len(prices) < max_lags * 4: return 0.5
            returns = np.diff(np.log(prices + 1e-10))
    lags = range(min_lags, max_lags)
    RS = []
    for lag in lags:
              chunks = [returns[i:i+lag] for i in range(0, len(returns)-lag, lag)]
              rs_vals = []
              for chunk in chunks:
                            mean = np.mean(chunk)
                            deviations = np.cumsum(chunk - mean)
                            R = np.max(deviations) - np.min(deviations)
                            S = np.std(chunk, ddof=1)
                            if S > 0: rs_vals.append(R / S)
                                      if rs_vals: RS.append(np.mean(rs_vals))
                                            if len(RS) < 3: return 0.5
                                                  log_lags = np.log(list(lags[:len(RS)]))
                    log_RS = np.log(np.array(RS) + 1e-10)
    poly = np.polyfit(log_lags, log_RS, 1)
    return float(np.clip(poly[0], 0.0, 1.0))

# --- RSI ---
def calculate_rsi(series, period=14):
      delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(span=period, adjust=False).mean()
    avg_loss = loss.ewm(span=period, adjust=False).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    return (100 - (100 / (1 + rs))).iloc[-1]

# --- ATR ---
def calculate_atr(df, period=14):
      tr = pd.concat([df['high'] - df['low'], 
                                         abs(df['high'] - df['close'].shift(1)), 
                                         abs(df['low'] - df['close'].shift(1))], axis=1).max(axis=1)
    return tr.rolling(window=period).mean().iloc[-1]

# --- MOTOR ESTADISTICO MARKOV ---
def get_markov_state(returns):
      def state(r):
                if r < -0.0002: return 0
                          if r > 0.0002: return 2
                                    return 1
    state_seq = [state(r) for r in returns]
    matrix = np.zeros((3, 3))
    for i in range(len(state_seq) - 1):
              matrix[state_seq[i]][state_seq[i+1]] += 1
    row_sums = matrix.sum(axis=1)
    norm_matrix = np.divide(matrix, row_sums[:, None], 
                                                       out=np.zeros_like(matrix), 
                                                       where=row_sums[:, None]!=0)
    return norm_matrix, int(state_seq[-1])
