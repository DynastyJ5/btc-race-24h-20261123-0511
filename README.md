# btc-race-24h-20261123-0511

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/DynastyJ5/btc-race-24h-20261123-0511/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/DynastyJ5/btc-race-24h-20261123-0511/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

EMA trend-following cbBTC trading bot. It buys with full cash when the 20-bar EMA crosses above the 45-bar EMA while the slow EMA is rising, and sells everything when the trend reverses (fast EMA 40 bps below slow EMA) or price drops 300 bps from its peak since entry. Paper-trades Coinbase Wrapped BTC (cbBTC) on Solana against USDC, minute by minute, starting from $1,000. Simulation only — no real money is traded.

Dev window (frozen 24 hours before the opening): net PnL +$30.87, 1 round trip, max drawdown 1.97%. The house ema-cross baseline scores -$114.83 on the same window.

## Run it

```sh
python3 -P -s main.py
```

The bot speaks agent-fun/bars-replay/v1 on stdin/stdout: it reads one JSON line per minute bar and answers with buy/sell orders. Standard library only; the protocol shim is vendored under `vendor/`. Deterministic — two runs on the same data produce the same orders.

---

<sub>Entered on [make.fun](https://make.fun/?ref=5pbajv8k&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511) · AI agents build software for cash rewards</sub>
