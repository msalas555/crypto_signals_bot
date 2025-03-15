import urllib.request
import json
from typing import List

def calculate_ema(prices: List[float], period: int) -> List[float]:
    if len(prices) < period:
        return []
    ema = [sum(prices[:period]) / period]  # Initialize with SMA
    multiplier = 2 / (period + 1)
    for price in prices[period:]:
        ema_value = (price - ema[-1]) * multiplier + ema[-1]
        ema.append(ema_value)
    return ema

def get_macd_signal(closes: List[float]):
    ema12 = calculate_ema(closes, 12)
    ema26 = calculate_ema(closes, 26)
    
    # Align EMA data
    offset = len(ema12) - len(ema26)
    aligned_ema12 = ema12[offset:]
    macd = [e12 - e26 for e12, e26 in zip(aligned_ema12, ema26)]
    
    # Calculate signal line
    return calculate_ema(macd, 9) if len(macd) >= 9 else []

def get_trading_signal():
    try:
        # Fetch BTC/USD daily data
        response = urllib.request.urlopen('https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=240')
        data = json.loads(response.read())['result']['XXBTZUSD']
        closes = [float(entry[4]) for entry in data][-60:]  # Last 60 days
        
        if len(closes) < 34:  # Minimum required data points
            return "Hold: Insufficient data"
            
        signal_line = get_macd_signal(closes)
        if len(signal_line) < 2:
            return "Hold: Calculating indicators"
        
        macd = get_macd_signal(closes[:-(len(closes)-len(signal_line)-8)])  # Align MACD
        
        # Crossover detection
        prev_macd, curr_macd = macd[-2], macd[-1]
        prev_signal, curr_signal = signal_line[-2], signal_line[-1]
        
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
    # Execute and print signal
    print(get_trading_signal())

