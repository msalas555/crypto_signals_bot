import time
import requests
from datetime import datetime

class KrakenBacktest:
    def __init__(self, initial_capital=10000):
        self.api_url = "https://api.kraken.com/0/public"
        self.rsi_period = 10
        self.sma_period = 200
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []
        self.trade_history = []
        
    def _get_ohlc_data(self, pair='XXBTZUSD', interval=1440):
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

    def get_signal(self, closes, current_index):
        if current_index < self.sma_period + self.rsi_period:
            return "HOLD"
            
        current_price = closes[current_index]
        sma = self._calculate_sma(closes[current_index-self.sma_period:current_index])
        rsi = self._calculate_rsi(closes[current_index-self.rsi_period-1:current_index+1])
        
        if current_price > sma:  # Uptrend condition
            if rsi < 30:
                return "BUY"
            elif rsi > 40:
                return "TAKE PROFIT"
                
        return "HOLD"

    def run_backtest(self, pair='XXBTZUSD', interval=1440):
        # Get historical data
        ohlc_data = self._get_ohlc_data(pair, interval)
        
        # Extract close prices and timestamps
        closes = [float(entry[4]) for entry in ohlc_data]
        timestamps = [int(entry[0]) for entry in ohlc_data]
        
        # Initialize metrics
        max_drawdown = 0
        peak_capital = self.initial_capital
        
        # Run through each day
        for i in range(self.sma_period, len(closes)):
            current_price = closes[i]
            signal = self.get_signal(closes, i)
            
            # Execute trades based on signals
            if signal == "BUY" and self.position == 0:
                # Calculate position size (invest 100% of capital)
                self.position = self.capital / current_price
                self.trades.append({
                    'type': 'BUY',
                    'price': current_price,
                    'timestamp': timestamps[i],
                    'position': self.position,
                    'capital': self.capital
                })
                
            elif signal == "TAKE PROFIT" and self.position > 0:
                # Close position
                self.capital = self.position * current_price
                self.trades.append({
                    'type': 'SELL',
                    'price': current_price,
                    'timestamp': timestamps[i],
                    'position': self.position,
                    'capital': self.capital
                })
                self.position = 0
                
            # Update metrics
            current_value = self.capital
            if self.position > 0:
                current_value = self.position * current_price
                
            if current_value > peak_capital:
                peak_capital = current_value
            
            drawdown = (peak_capital - current_value) / peak_capital
            max_drawdown = max(max_drawdown, drawdown)
            
        # Calculate final metrics
        total_trades = len(self.trades)
        profitable_trades = sum(1 for i in range(0, len(self.trades), 2) 
                              if i + 1 < len(self.trades) and 
                              self.trades[i+1]['price'] > self.trades[i]['price'])
        
        final_value = self.capital if self.position == 0 else self.position * closes[-1]
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        return {
            'Initial Capital': self.initial_capital,
            'Final Capital': round(final_value, 2),
            'Total Return %': round(total_return, 2),
            'Max Drawdown %': round(max_drawdown * 100, 2),
            'Total Trades': total_trades,
            'Profitable Trades': profitable_trades,
            'Win Rate %': round((profitable_trades / (total_trades/2)) * 100, 2) if total_trades > 0 else 0
        }

    def print_trades(self):
        for trade in self.trades:
            date = datetime.fromtimestamp(trade['timestamp']).strftime('%Y-%m-%d')
            print(f"Date: {date}, Type: {trade['type']}, Price: ${trade['price']:.2f}, Capital: ${trade['capital']:.2f}")

# Run backtest
if __name__ == "__main__":
    backtest = KrakenBacktest(initial_capital=10000)
    results = backtest.run_backtest(pair='XXBTZUSD', interval=1440)
    
    print("\n=== Backtest Results ===")
    for metric, value in results.items():
        print(f"{metric}: {value}")
        
    print("\n=== Trade History ===")
    backtest.print_trades()

