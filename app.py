from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import yfinance as yf
import time
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

trading_client = TradingClient(os.getenv('ALPACA_PUBLIC'), os.getenv('ALPACA_SECRET'))
moving_averages = [30,70] # customizable moving averages
tickers = ['SPY', 'VNQ', 'GSG', 'TLH'] # customizable tickers to trade


# calculates moving averages to know when they intersect
def create_signals(tickers, moving_averages):
    # add moving average columns to dataframe
    signals = {}
    for ticker in tickers:
        df = yf.Ticker(ticker).history(period="1y")
        df[f'{moving_averages[0]}_SMA'] = df['Close'].rolling(window=moving_averages[0]).mean()
        df[f'{moving_averages[1]}_SMA'] = df['Close'].rolling(window=moving_averages[1]).mean()
        signals[ticker] = df[f'{moving_averages[0]}_SMA'].iloc[-1] > df[f'{moving_averages[1]}_SMA'].iloc[-1]
    
    return signals


signals = create_signals(tickers,moving_averages)
num_buy_signals = sum(signals.values())
portfolio = trading_client.get_all_positions()
updated_portfolio = []

def calculate_etf_price():
    account = trading_client.get_account() # update account to reflect changes
    total_balance = float(account.cash) # total cash + equity balance
    if num_buy_signals != 0: # avoid div by 0 err in case of 0 favorable security purchases
        weighted_etf_cost = int(total_balance / num_buy_signals)
    else:
        weighted_etf_cost = 0
    return weighted_etf_cost

def sell_holdings(positions):
    sell_order_data = []
    for position in positions:
        sell_order_data.append(MarketOrderRequest(
                    symbol=position.symbol,
                    qty=position.qty, # sell entire holdings
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                    ))
    for order in sell_order_data:
        trading_client.submit_order(order_data=order)

def buy_securities(signals,cost):
    buy_order_data = []
    for signal in signals:
        buy_order_data.append(MarketOrderRequest(
                    symbol=signal,
                    notional=cost,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                    ))
    for order in buy_order_data:
        trading_client.submit_order(order_data=order)


# check if the portfolio is weighted differently than buy signals
if num_buy_signals != len(portfolio):
    try:
        sell_holdings(portfolio) # sell entire portfolio to rebalance
    except Exception as e:
        print("Error selling:", e)
        time.sleep(10)
        sell_holdings(portfolio) # wait and retry once more

    time.sleep(5) # 5 seconds for portfolio balance to update
    weighted_etf_cost = calculate_etf_price()
    buy_signals = [ticker for ticker,signal in signals.items() if signal]

    try:
        buy_securities(buy_signals,weighted_etf_cost) # redistribute holdings with new securities
    except Exception as e:
        print("Error buying:", e)
        time.sleep(10)
        buy_securities(buy_signals,weighted_etf_cost)
else: 
    # sell positions that are no longer favorable
    for position in portfolio: 
        if not signals[position.symbol]:
            sell_holdings([position]) # sell entire holdings of particular security
        else:
            updated_portfolio.append(position.symbol)
    time.sleep(5) # 5 seconds for portfolio balance to update
    weighted_etf_cost = calculate_etf_price() # recalculate etf price with updated account
    # buy shares of favorable securities
    for ticker, value in signals.items():
        if value and ticker not in updated_portfolio:
            try:
                buy_securities([ticker],weighted_etf_cost)
            except Exception as e:
                print("Error buying:", e)
                time.sleep(10)
                buy_securities([ticker],weighted_etf_cost)