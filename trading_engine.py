import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from .config import *

# --- GESTION DE RIESGO Y POSICIONES ---
def get_open_positions_count(symbol=None):
      positions = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
      return len(positions) if positions else 0

def check_currency_exposure(new_symbol):
      positions = mt5.positions_get()
      if not positions: return True
            base = new_symbol[:3]
    if base in ["GOL", "SIL", "OIL"]: return True
          count = sum(1 for p in positions if base in p.symbol)
    return count < 2

def get_real_daily_profit_loss(session_start_time):
      from_date = datetime.fromtimestamp(session_start_time)
    deals = mt5.history_deals_get(from_date, datetime.now() + timedelta(days=1))
    if not deals: return 0.0
          return sum(d.profit + d.commission + d.swap for d in deals if d.entry in [mt5.DEAL_ENTRY_OUT, mt5.DEAL_ENTRY_OUT_BY] and d.magic in ALLOWED_MAGICS)

# --- EJECUCION DE ORDENES ---
def place_trade(symbol, trade_type, sl_pips, tp_pips, lot, reason):
      tick = mt5.symbol_info_tick(symbol)
    sym_info = mt5.symbol_info(symbol)
    if not tick or not sym_info: return False

    price = tick.ask if trade_type == "BUY" else tick.bid
    sl = price - (sl_pips * sym_info.point) if trade_type == "BUY" else price + (sl_pips * sym_info.point)
    tp = price + (tp_pips * sym_info.point) if trade_type == "BUY" else price - (tp_pips * sym_info.point)

    request = {
              "action": mt5.TRADE_ACTION_DEAL,
              "symbol": symbol,
              "volume": float(lot),
              "type": mt5.ORDER_TYPE_BUY if trade_type == "BUY" else mt5.ORDER_TYPE_SELL,
              "price": price, "sl": float(sl), "tp": float(tp),
              "magic": MAGIC_TREND if "Trend" in reason else MAGIC_RANGE,
              "comment": f"FG:{reason}",
              "type_time": mt5.ORDER_TIME_GTC,
              "type_filling": mt5.ORDER_FILLING_IOC,
    }
    return mt5.order_send(request)

# --- GESTION DE POSICIONES ABIERTAS ---
def manage_trades(magic_list):
      positions = mt5.positions_get()
    if not positions: return
          for pos in positions:
                    if pos.magic not in magic_list: continue
                              sym_info = mt5.symbol_info(pos.symbol)
        tick = mt5.symbol_info_tick(pos.symbol)
        if not tick: continue

        curr_price = tick.bid if pos.type == mt5.ORDER_TYPE_BUY else tick.ask
        profit_pips = abs(curr_price - pos.price_open) / sym_info.point

        # Breakeven y Trailing
        if profit_pips >= 150.0 and pos.sl != pos.price_open:
                      mt5.order_send({"action": mt5.TRADE_ACTION_SLTP, "position": pos.ticket, "sl": pos.price_open, "tp": pos.tp})

        ts_activation, ts_dist = 120.0, 60.0
        if profit_pips >= ts_activation:
                      new_sl = curr_price - (ts_dist * sym_info.point) if pos.type == mt5.ORDER_TYPE_BUY else curr_price + (ts_dist * sym_info.point)
                      if (pos.type == mt5.ORDER_TYPE_BUY and new_sl > pos.sl) or (pos.type == mt5.ORDER_TYPE_SELL and (pos.sl == 0 or new_sl < pos.sl)):
                                        mt5.order_send({"action": mt5.TRADE_ACTION_SLTP, "position": pos.ticket, "sl": new_sl, "tp": pos.tp})

          def close_all():
                positions = mt5.positions_get()
    if not positions: return True
          for p in positions:
                    tick = mt5.symbol_info_tick(p.symbol)
        mt5.order_send({
                      "action": mt5.TRADE_ACTION_DEAL, "position": p.ticket, "symbol": p.symbol, "volume": p.volume,
                      "type": mt5.ORDER_TYPE_SELL if p.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                      "price": tick.bid if p.type == mt5.ORDER_TYPE_BUY else tick.ask,
                      "type_filling": mt5.ORDER_FILLING_IOC, "magic": p.magic
        })
    return True
