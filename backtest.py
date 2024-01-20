# A simple python script that simulates an equally weighted portfolio of all ETF's (out of 4) that have a higher 30 day moving average than 100 day moving average.
# This is a common and very basic trading strategy that indicates momentum.
# The four ETF's will be: SPY (Stocks ETF), VNQ (Real estate ETF), GSG (Commodities ETF), TLH (Bonds ETF).
# I then compared this strategy to simply buying and holding an equally weighted portfolio of the four ETF's.

import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

plt.style.use('dark_background')
moving_averages = [30,100]
tickers = yf.Tickers('SPY VNQ GSG TLH')

def create_signals(df, moving_averages):
    buy_signals = []
    # add moving average columns to dataframe
    for ma in moving_averages:
        df[f'{ma}_SMA'] = df['Close'].rolling(window=ma).mean()

    # remove first ma_1 days b/c there isn't a moving average yet
    df = df.iloc[moving_averages[1]:]
    # loop through rows and determine if it's necessary to buy/keep holding or sell/keep not buying
    for x in range(len(df)):
        if df[f'{moving_averages[0]}_SMA'].iloc[x] > df[f'{moving_averages[1]}_SMA'].iloc[x]:
            buy_signals.append('Buy/Hold')
        else:
            buy_signals.append(float('nan'))
        
    df['Buy Signals'] = buy_signals
    return df

SPY_data = create_signals(tickers.tickers['SPY'].history(period='5y'), moving_averages)
VNQ_data = create_signals(tickers.tickers['VNQ'].history(period='5y'), moving_averages)
GSG_data = create_signals(tickers.tickers['GSG'].history(period='5y'), moving_averages)
TLH_data = create_signals(tickers.tickers['TLH'].history(period='5y'), moving_averages)

# create equity array containing return % overtime
equity = [1]
buy_and_hold = [1]

# loop through rows in ETF data to calculate holdings overtime
for x in range(1, len(SPY_data)):

    # create weights array to hold holding % of each ETF
    weights = np.array([0.0,0.0,0.0,0.0])

    if SPY_data['Buy Signals'].iloc[x] == 'Buy/Hold':
        weights[0] = 1.0
    if VNQ_data['Buy Signals'].iloc[x] == 'Buy/Hold':
        weights[1] = 1.0
    if GSG_data['Buy Signals'].iloc[x] == 'Buy/Hold':
        weights[2] = 1.0
    if TLH_data['Buy Signals'].iloc[x] == 'Buy/Hold':
        weights[3] = 1.0
    
    if sum(weights) != 0: # prevent div by 0 err
        weights /= sum(weights) # normalize weights

    # calculate return of each ETF over one day
    SPY_ret = (SPY_data['Close'].iloc[x] - SPY_data['Close'].iloc[x-1]) / SPY_data['Close'].iloc[x]
    VNQ_ret = (VNQ_data['Close'].iloc[x] - VNQ_data['Close'].iloc[x-1]) / VNQ_data['Close'].iloc[x]
    GSG_ret = (GSG_data['Close'].iloc[x] - GSG_data['Close'].iloc[x-1]) / GSG_data['Close'].iloc[x]
    TLH_ret = (TLH_data['Close'].iloc[x] - TLH_data['Close'].iloc[x-1]) / TLH_data['Close'].iloc[x]

    # combine ETF returns
    equity.append(equity[x-1] * (1 + weights[0]*SPY_ret + weights[1]*VNQ_ret + weights[2]*GSG_ret + weights[3]*TLH_ret))
    # compare to a buy and hold strategy of 25% of each ETF
    buy_and_hold.append(buy_and_hold[x-1] * (1 + 0.25*SPY_ret + 0.25*VNQ_ret + 0.25*GSG_ret + 0.25*TLH_ret))


# plot the two different strategies
plt.plot(SPY_data.index,buy_and_hold,label="Buy and Hold", color="purple")
plt.plot(SPY_data.index,equity,label="Strategy", color="orange")
plt.title('Five-year backtest')
plt.legend(loc="upper left")
plt.show()
