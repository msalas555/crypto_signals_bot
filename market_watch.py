from signal import KrakenMeanReversion
from signal_macd import get_trading_signal
import time
import os
import datetime

def logthis(text):
    pass

def previous(text):
    with open('previous_action.txt','w') as f:
        f.write(text)

def main():
    kmr = KrakenMeanReversion()
    mr_signal,price = kmr.get_signal()
    previous_action = ''
    timestamp = datetime.datetime.now()

    try:
        with open('previous_action.txt','r') as f:
            previous_action = f.read().strip()
    except FileNotFoundError as error:
        print(f'{error}')

    print(f'previous action: {previous_action}')

    if mr_signal == 'BUY':
        print('mean reversion BUY')
        macd = get_trading_signal()
        if macd == 'BUY':
            print(f'{timestamp}  signal confirmed time to buy!')
            #stop from taking more than one position
            if previous_action != 'BUY':
                action = 'BUY'
                previous(f'{action} at {price}')

    elif mr_signal == 'TAKE PROFIT':
        print('mean reversion TAKE PROFIT')
        macd = get_trading_signal()
        if macd == 'TAKE PROFIT':
            ##need to also check for target percent
            print(f'{timestamp}  signal confirmed time to take profit?')
            if previous_action != 'TAKE PROFIT':
                action = 'TAKE PROFIT'
                previous(f'{action} at {price}')
    else:
        print(f'{timestamp}  hold?')

if __name__ == "__main__":
    while True:
        main()
        time.sleep(600)
