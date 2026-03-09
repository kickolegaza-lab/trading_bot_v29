import threading
import socket
import time
from datetime import datetime
import MetaTrader5 as mt5
from flask import Flask, jsonify, request, session, redirect, url_for
from google import genai
from .config import *
from .indicators import get_markov_state
from .trading_engine import *
from .signals import *
from .ai_auditor import *

# --- GLOBALES ---
MARKOV_MODELS = {}
BOT_STOPPED = False
SESSION_START = datetime.now().timestamp()
MEMORY = {"last_trade_time": {}}

# --- TRADINGVIEW MAPPING ---
TRADINGVIEW_MAPPING = {
      "GOLD#": {"sym": "XAUUSD", "ex": "OANDA", "scr": "forex"}
}

app = Flask(__name__)
app.secret_key = "modular_fractal_secret"

# --- WORKER MARKOV ---
def markov_worker():
      while True:
                for sym in ALLOWED_SYMBOLS:
                              rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M1, 0, 300)
                              if rates is not None:
                                                returns = pd.DataFrame(rates)['close'].pct_change().dropna()
                                                matrix, last_s = get_markov_state(returns)
                                                MARKOV_MODELS[sym] = {"probs": matrix[last_s].tolist(), "state": last_s}
                                        time.sleep(900)

        # --- DASHBOARD FLASK ---
        @app.route('/')
def index():
      return "<h1>Fractal Guardian V29.5 - Modular</h1><p>Dashboard ready.</p>"

# --- BUCLE PRINCIPAL ---
def run_bot():
      check_instance_lock()
    if not mt5.initialize(login=KEYS["MT5_LOGIN"], password=KEYS["MT5_PASSWORD"], server=KEYS["MT5_SERVER"]):
              print("Error MT5")
              return

    threading.Thread(target=markov_worker, daemon=True).start()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000), daemon=True).start()

    # Cliente GenAI
    client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_ENABLED else None

    while True:
              if BOT_STOPPED: 
                  time.sleep(60)
                            continue

        # Gestion de riesgo diaria
              if get_real_daily_profit_loss(SESSION_START) <= -MAX_TOTAL_DAILY_LOSS:
                            print("Freno diario alcanzado")
                            break

              manage_trades(ALLOWED_MAGICS)

        for sym in ALLOWED_SYMBOLS:
                      # 1. Obtener Datos
                      df_m5 = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M5, 0, 80)
                      df_m15 = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, 0, 200)
                      df_h1 = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_H1, 0, 100)

            if df_m5 is None: continue
                          df_m5 = pd.DataFrame(df_m5)
            df_m15 = pd.DataFrame(df_m15)
            df_h1 = pd.DataFrame(df_h1)

            # 2. Senal Tecnica
            last_trade = MEMORY["last_trade_time"].get(sym, 0)
            range_high, range_low = df_m5["high"].max(), df_m5["low"].min()

            sig, reason = get_gold_signal(sym, df_m5, df_h1, range_high, range_low, last_trade)
            if sig == "WAIT":
                              sig, reason = get_scalper_signal(sym, df_m5)

            # 3. Auditoria
            if sig != "WAIT":
                              valid, tv_res = ask_tradingview(sym, sig)
                              if valid:
                                                    decision, ai_res = ask_gemini(client, "models/gemini-2.5-flash", sym, sig, reason, df_m5)
                                                    if decision != "WAIT":
                                                                              # 4. Ejecutar
                                                                              if place_trade(sym, decision, 150, 400, LOT_SIZE, reason):
                                                                                                            MEMORY["last_trade_time"][sym] = datetime.now().timestamp()
                                                                                                            print(f"Trade {decision} ejecutado en {sym}")

                                                              time.sleep(60)

              if __name__ == "__main__":
                    run_bot()
                
