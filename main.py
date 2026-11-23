"""Trend-following cbBTC bot for make.fun btc-race-24h-20261123-0511.

Strategy: long-only EMA trend follower on 1-minute closes.
  - Enter (full cash) when the fast EMA (20 bars) crosses above the slow
    EMA (45 bars) while the slow EMA is itself rising over the last 30 bars.
  - Exit (sell everything) when the fast EMA falls 40 bps below the slow
    EMA, or price drops 300 bps from its peak since entry.
  - One round trip costs ~26 bps in fees, slippage and impact, so the
    wide exit and the rising-slow-EMA filter keep it out of chop: it only
    rides established trends and cuts them when they reverse.

Dev window (frozen 24h before the opening): net PnL +$30.87, 1 round trip,
max drawdown 1.97%. House ema-cross baseline on the same window: -$114.83.

Deterministic: pure functions of the bars seen so far, no clock, no network,
no files, no randomness. Standard library only.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"
FAST_N = 20
SLOW_N = 45
SLOPE_BARS = 30
EXIT_SPREAD_BPS = -40
TRAIL_STOP_BPS = 300
MAX_SLIPPAGE_BPS = 500


class TrendBot:
    def __init__(self):
        self.fast_alpha = 2.0 / (FAST_N + 1)
        self.slow_alpha = 2.0 / (SLOW_N + 1)
        self.fast_ema = None
        self.slow_ema = None
        self.slow_history = []
        self.in_position = False
        self.entry_close = 0
        self.peak_close = 0

    def on_batch(self, state, batch):
        if state.warming_up:
            return []
        close = state.close(SYMBOL)
        if close is None:
            return []
        if self.fast_ema is None:
            self.fast_ema = float(close)
            self.slow_ema = float(close)
        else:
            self.fast_ema += self.fast_alpha * (close - self.fast_ema)
            self.slow_ema += self.slow_alpha * (close - self.slow_ema)
        self.slow_history.append(self.slow_ema)
        if state.seq < SLOW_N:
            return []

        spread_bps = (self.fast_ema - self.slow_ema) / self.slow_ema * 10000.0
        holding = state.positions.get(SYMBOL)
        qty = holding.qty if holding is not None else 0

        if not self.in_position:
            if qty:
                # Position held without our flag (should not happen); track it.
                self.in_position = True
                self.entry_close = close
                self.peak_close = close
                return []
            return self._maybe_enter(state, spread_bps)

        # In position: update peak, check exits. A buy that the market
        # rejected leaves us flat: clear the flag and re-enter on signal.
        if qty <= 0:
            self.in_position = False
            return self._maybe_enter(state, spread_bps)
        if close > self.peak_close:
            self.peak_close = close
        trail_down_bps = (close - self.peak_close) / self.peak_close * 10000.0
        if spread_bps < EXIT_SPREAD_BPS or trail_down_bps < -TRAIL_STOP_BPS:
            self.in_position = False
            return [{
                "side": "sell",
                "symbol": SYMBOL,
                "qty": qty,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            }]
        return []

    def _maybe_enter(self, state, spread_bps):
        if spread_bps <= 0:
            return []
        if len(self.slow_history) > SLOPE_BARS:
            if self.slow_ema <= self.slow_history[-SLOPE_BARS - 1]:
                return []
        if state.cash < 1_000_000:
            return []
        close = state.close(SYMBOL)
        self.in_position = True
        self.entry_close = close
        self.peak_close = close
        return [{
            "side": "buy",
            "symbol": SYMBOL,
            "notional_quote_units": state.cash,
            "max_slippage_bps": MAX_SLIPPAGE_BPS,
        }]


_BOT = TrendBot()


def on_batch(state, batch):
    return _BOT.on_batch(state, batch)


makefun_bars.run(on_batch)
