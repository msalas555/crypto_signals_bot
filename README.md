# Kraken Trading System

A cryptocurrency trading system that implements mean reversion and MACD strategies for BTC/USD on the Kraken exchange.

## To-Do

- [ ] Implement signals to external alerts (email or text,etc.)
- [ ] Add more trading strategies 
- [ ] Add options for live trading

## Overview

This system consists of several Python scripts that work together to analyze market data, generate trading signals, and execute trades based on technical indicators. It combines two trading strategies (mean reversion and MACD) to confirm signals before taking action.

## Components

### signal.py

Implements a mean reversion trading strategy using RSI and SMA indicators:

- Uses a 10-period RSI and 200-period SMA
- Generates BUY signals when price is above SMA and RSI is below 30
- Generates TAKE PROFIT signals when price is above SMA and RSI is above 40
- Fetches 5-minute OHLC data from Kraken API

```python
trader = KrakenMeanReversion()
signal, price = trader.get_signal()
```

### signal_macd.py

Implements a MACD-based trading strategy:

- Calculates EMA (Exponential Moving Average) for different periods
- Generates trading signals based on MACD and signal line crossovers
- Fetches 4-hour (240-minute) OHLC data from Kraken API
- Returns BUY, TAKE PROFIT, or HOLD signals

```python
signal = get_trading_signal()
```

### market_watch.py

Combines both strategies to confirm trading signals:

- Runs in a continuous loop, checking for signals every 10 minutes
- Only executes trades when both strategies agree on the signal
- Prevents duplicate trades by tracking previous actions
- Logs trading actions with timestamps and prices

```python
python market_watch.py
```

### backtest.py

Provides backtesting capabilities to evaluate strategy performance:

- Tests the mean reversion strategy on historical data
- Calculates performance metrics including:
  - Total return
  - Maximum drawdown
  - Win rate
  - Trade history
- Simulates trading with a configurable initial capital

```python
backtest = KrakenBacktest(initial_capital=10000)
results = backtest.run_backtest(pair='XXBTZUSD', interval=1440)
```

## Requirements

- Python 3.6+
- Required packages:
  - requests
  - urllib
  - json
  - datetime

## Usage

1. Run the backtesting script to evaluate strategy performance:
   ```
   python backtest.py
   ```

2. Start the trading system:
   ```
   python market_watch.py
   ```

3. Test individual strategies:
   ```
   python signal.py
   python signal_macd.py
   ```

## Trading Logic

The system uses a dual-confirmation approach:
1. Mean reversion strategy identifies potential entry/exit points based on RSI and SMA
2. MACD strategy confirms signals by detecting crossovers
3. Trades are only executed when both strategies agree

## Disclaimer

This trading system is for educational purposes only. Always perform your own research before trading cryptocurrencies, as they are highly volatile assets.
