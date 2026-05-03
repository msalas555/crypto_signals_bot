import requests
import json
from typing import List

def calculate_ema(prices: List[float], period: int) -> List[float]:
    if len(prices) < period:
        return []
    ema = [sum(prices[:period]) / period]
    multiplier = 2 / (period + 1)
    for price in prices[period:]:
        ema_value = (price - ema[-1]) * multiplier + ema[-1]
        ema.append(ema_value)
    return ema

def get_macd_line(closes: List[float]) -> List[float]:
    ema12 = calculate_ema(closes, 12)
    ema26 = calculate_ema(closes, 26)
    
    if len(ema12) < len(ema26):
        ema12 = ema12[-len(ema26):]
    
    macd = [e12 - e26 for e12, e26 in zip(ema12, ema26)]
    return macd

def get_signal_line(macd: List[float]) -> List[float]:
    return calculate_ema(macd, 9)

def get_trading_signal():
    try:
        response = requests.get('https://api.kraken.com/0/public/OHLC', params={'pair': 'XXBTZUSD', 'interval': 240})
        data = response.json()
        closes = [float(entry[4]) for entry in data['result']['XXBTZUSD']][-60:]
        
        if len(closes) < 34:
            return "Hold: Insufficient data"
        
        macd_line = get_macd_line(closes)
        signal_line = get_signal_line(macd_line)
        
        if len(signal_line) < 2:
            return "Hold: Calculating indicators"
        
        prev_macd = macd_line[-2]
        curr_macd = macd_line[-1]
        prev_signal = signal_line[-2]
        curr_signal = signal_line[-1]
        
        if curr_macd > curr_signal and prev_macd <= prev_signal:
            print("Buy: Bullish crossover detected")
            return "BUY"
        elif curr_macd < curr_signal and prev_macd >= prev_signal:
            print("Take Profit: Bearish crossover detected")
            return "TAKE PROFIT"
        print("Hold: No clear signal")
        return "HOLD"
    
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print(get_trading_signal())
