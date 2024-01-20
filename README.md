# Momentum Trading Bot

## Overview
The script is a momentum-based trading bot implemented in Python. The bot's strategy involves creating an equally weighted portfolio of selected ETFs (SPY, VNQ, GSG, TLH) that show a higher 30-day moving average compared to their 100-day moving average. This project also includes a backtesting script using historical data to validate the trading strategy.

## Strategy Description  
The bot evaluates the 30-day and 100-day moving averages of each ETF (SPY, VNQ, GSG, TLH). If the 30-day average is higher, the ETF is included in the portfolio. The portfolio is rebalanced to ensure equal weighting across the selected ETFs.

## Backtesting  
The backtest script compares the performance of the momentum strategy against a buy-and-hold strategy over a 5-year period. Results are visualized using matplotlib.  


  <img width="609" alt="image" src="https://github.com/Landonbads/tradingbot/assets/52727727/389c3587-2c07-4e43-8871-719a33db8974">


**Note:** The script is currently deployed on a Google Cloud server, operating on a simulated trading account.
