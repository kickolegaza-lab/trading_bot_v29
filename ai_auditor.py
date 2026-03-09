import re
import json
import requests
from datetime import datetime
from google import genai
from tradingview_ta import TA_Handler, Interval
from .config import *

# --- TRADINGVIEW CONSENSUS ---
def ask_tradingview(symbol, signal):
      if symbol not in TRADINGVIEW_MAPPING: return True, "Not Mapped"
            try:
                      cfg = TRADINGVIEW_MAPPING[symbol]
                      handler = TA_Handler(symbol=cfg["sym"], exchange=cfg["ex"], screener=cfg["scr"], interval=Interval.INTERVAL_15_MINUTES)
                      rec = handler.get_analysis().summary['RECOMMENDATION']
                      if (signal == "BUY" and "BUY" in rec) or (signal == "SELL" and "SELL" in rec):
                                    return True, f"TV OK: {rec}"
                                return False, f"TV Veto: {rec}"
    except: return True, "TV Error (Skip)"

# --- NEWS FILTER ---
def is_high_impact_news(symbol):
      try:
                curr = "USD" if "GOL" in symbol else symbol[:3]
                resp = requests.get(CALENDAR_URL, timeout=10)
                if resp.status_code != 200: return False
                          now = datetime.utcnow()
                for ev in resp.json():
                              if ev["impact"] == "High" and ev["currency"] == curr:
                                                ev_time = datetime.strptime(f"{ev['date']} {ev['time']}", "%Y-%m-%d %H:%M")
                                                if abs((ev_time - now).total_seconds()) / 60 < 30: return True
                                                          return False
                                    except: return False

  # --- GEMINI AI SNIPER ---
  def ask_gemini(client, model_name, symbol, signal, reason, df_m5):
        if not client: return signal, reason
              if is_high_impact_news(symbol): return "WAIT", "High Impact News"

    m5_ctx = df_m5[["close", "tick_volume"]].tail(10).to_string(index=False)
    # Sanitized prompt to avoid non-ASCII characters
    prompt = f"ACTUA COMO SNIPER MOMENTUM. Simbolo: {symbol} | Senal: {signal} ({reason})\nDATOS: {m5_ctx}\nResponde JSON: {{\"valid\": true/false, \"reason\": \"...\"}}"

    try:
              resp = client.models.generate_content(model=model_name, contents=prompt, config=genai.types.GenerateContentConfig(temperature=0.1, max_output_tokens=150))
        data = json.loads(re.search(r'\{.*\}', resp.text.strip(), re.DOTALL).group())
        if data.get("valid"): return signal, f"IA OK: {data.get('reason')}"
                  return "WAIT", f"IA Veto: {data.get('reason')}"
    except: return signal, f"{reason} (IA Error: Fallback)"
