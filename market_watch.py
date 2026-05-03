from signal import KrakenMeanReversion
from signal_macd import get_trading_signal
import time
import os
import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)

def logthis(text):
    logging.info(text)

def previous(text):
    with open('previous_action.txt', 'w') as f:
        f.write(text)

def main():
    kmr = KrakenMeanReversion()
    try:
        mr_signal, price = kmr.get_signal()
    except ValueError:
        timestamp = datetime.datetime.now()
        logging.error(f'{timestamp} - insufficient data - skipping')
        time.sleep(600)
        return
    
    previous_action = ''
    timestamp = datetime.datetime.now()

    try:
        with open('previous_action.txt','r') as f:
            previous_action = f.read().strip()
    except FileNotFoundError as error:
        logging.error(f'{error}')

    logging.info(f'previous action: {previous_action}')

    if mr_signal == 'BUY':
        logging.info('mean reversion BUY')
        macd = get_trading_signal()
        if macd == 'BUY':
            logging.info(f'{timestamp} signal confirmed time to buy!')
            if previous_action != 'BUY':
                action = 'BUY'
                previous(f'{action} at {price}')

    elif mr_signal == 'TAKE PROFIT':
        logging.info('mean reversion TAKE PROFIT')
        macd = get_trading_signal()
        if macd == 'TAKE PROFIT':
            logging.info(f'{timestamp} signal confirmed time to take profit?')
            if previous_action != 'TAKE PROFIT':
                action = 'TAKE PROFIT'
                previous(f'{action} at {price}')
    else:
        logging.info(f'{timestamp} hold?')

if __name__ == "__main__":
    while True:
        main()
        time.sleep(600)
