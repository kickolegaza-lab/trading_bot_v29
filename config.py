import os
import sys
import json

# --- CONFIGURACION DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# El archivo de llaves se busca en la carpeta superior por seguridad
DB_FILE = os.path.join(os.path.dirname(BASE_DIR), "secret_keys.json")
HISTORICAL_DATA_FILE = os.path.join(BASE_DIR, "historical_data.json")
BOT_MEMORY_FILE = os.path.join(BASE_DIR, "bot_memory.json")
LOCK_FILE = os.path.join(BASE_DIR, "bot.lock")

# --- CARGA SEGURA DE CREDENCIALES ---
def load_credentials():
      if not os.path.exists(DB_FILE):
                return {
                              "TELEGRAM_TOKEN": "TU_TOKEN",
                              "CHAT_ID": "TU_CHAT_ID",
                              "MT5_LOGIN": 0,
                              "MT5_PASSWORD": "TU_PASSWORD",
                              "MT5_SERVER": "TU_SERVER",
                              "GEMINI_API_KEY": "TU_GEMINI_KEY"
                }
            with open(DB_FILE, "r") as f:
                      return json.load(f)

KEYS = load_credentials()
TELEGRAM_TOKEN = KEYS.get("TELEGRAM_TOKEN")
CHAT_ID = KEYS.get("CHAT_ID")
GEMINI_API_KEY = KEYS.get("GEMINI_API_KEY")

# --- PARAMETROS ESTRATEGIA (V29.5) ---
ALLOWED_SYMBOLS = ["GOLD#"]
MAX_GOLD_POSITIONS = 1
MAX_FOREX_POSITIONS = 2
MAX_RISK_EUR_GOLD = 1.5
MAX_RISK_EUR_FOREX = 3.0
MAX_TOTAL_DAILY_LOSS = 10.0
MAX_SPREAD_PIPS_GOLD = 35.0
MAX_SPREAD_PIPS = 14.0
HURST_THRESHOLD = 0.58
HURST_REVERSION_THRESHOLD = 0.32
CALENDAR_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

# --- RIESGO Y LOTES ---
LOT_SIZE = 0.01
ATR_MULTIPLIER_SL = 2.0
MAGIC_TREND = 2881
MAGIC_RANGE = 2882
ALLOWED_MAGICS = [MAGIC_TREND, MAGIC_RANGE]

# --- DASHBOARD ---
DASHBOARD_PASSWORD = "TU_PASSWORD_AQUI"
