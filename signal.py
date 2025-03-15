import time
import requests

class KrakenMeanReversion:
    def __init__(self):
        self.api_url = "https://api.kraken.com/0/public"
        self.rsi_period = 10
        self.sma_period = 200
        
    def _get_ohlc_data(self, pair='XXBTZUSD', interval=5):
        endpoint = '/OHLC'
        params = {
            'pair': pair,
            'interval': interval
        }
        
        response = requests.get(self.api_url + endpoint, params=params)
        data = response.json()
        return data['result'][pair]

    def _calculate_rsi(self, closes):
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [x if x > 0 else 0 for x in deltas]
        losses = [-x if x < 0 else 0 for x in deltas]
        
        avg_gain = sum(gains[:self.rsi_period])/self.rsi_period
        avg_loss = sum(losses[:self.rsi_period])/self.rsi_period
        
        for i in range(self.rsi_period, len(gains)):
            avg_gain = (avg_gain*(self.rsi_period-1) + gains[i])/self.rsi_period
            avg_loss = (avg_loss*(self.rsi_period-1) + losses[i])/self.rsi_period

        rs = avg_gain / avg_loss if avg_loss != 0 else float('inf')
        return 100 - (100 / (1 + rs))

    def _calculate_sma(self, closes):
        return sum(closes[-self.sma_period:]) / self.sma_period

    def get_signal(self):
        ohlc_data = self._get_ohlc_data()
        closes = [float(entry[4]) for entry in ohlc_data]
        
        if len(closes) < self.sma_period + self.rsi_period:
            return "Insufficient data"
            
        current_price = closes[-1]
        sma = self._calculate_sma(closes[:-1])
        rsi = self._calculate_rsi(closes[-(self.rsi_period+1):])

        print(current_price)

        if current_price > sma:  # Uptrend condition
            if rsi < 30:
                return "BUY",current_price
            elif rsi > 40:
                return "TAKE PROFIT",current_price
                
        return "HOLD",current_price

# Usage example:
if __name__ == "__main__":
    # Change timeframe (minutes: 1, 5, 15, 30, 60, 240, 1440, 10080, 21600)
    trader = KrakenMeanReversion()
    print(f"Current signal: {trader.get_signal()}")

