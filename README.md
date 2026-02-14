# Momentum-Trading-Strategy---QQQ
This momentum trading strategy captures profits of the price movement of QQQ relative to the VWAP. This strategy has been backtested over 5 years - 01/02/2021 to 01/01/2026. Alpaca APIs were used to access data and backtest the strategy with a starting capital of $100,000. This strategy was compared to a simple Buy & Hold strategy for QQQ, naturally making it a benchmark. This strategy was able to generate higher returns, with lower risk, lower drawdowns and lower volatility. This is numerically portrayed through a range of metrics below. 

My objective in building it was not only to generate returns, but to explore how design choices, assumptions and risk considerations influence portfolio returns over time. The strategy is rule-based and evaluated on historical data of QQQ, emphasising consistency, transparency and structured decision making rather than discretionary and emotional judgement. This project reflects that learning process as much as the final output.

## Numerical Summary - Strategy
Final Capital: $270,316.52
CAGR: 22.08%
Sharpe: 1.28
Sortino: 1.77
Volatility: 16.50%
Max Drawdown: -12.33%
Win Rate: 16.13%
Trades: 19416

## Reflection - Buy & Hold
Final Capital: $196,316.73
CAGR: 14.49%
Sharpe: 0.72
Sortino: 0.97
Volatility: 22.46%
Max Drawdown: -37.07%

## Reflection
I am proud of this strategy not simply because of the performance metrics, but because of the process behind building it. Developing it required questioning assumptions, debugging ideas that did not work and refining the logic repeatedly.

Recognising that there is still room for improvement in this strategy, I view this project as a living project rather than a finished result. Sharing it is part documentation, accountability and curiousity about where it can go next. 

The next steps for me include rigorous backtesting with Monte Carlo simulations, as the strategy partly leverages the volatile behaviour of technology stocks in the past few years, leaving a risk of overfitting. This will allow me to recognise gaps in the strategy, test for Type I and II errors through statistical significance tests and bootstrapping, and incorporate relevant indicators like RSI, options order flows and moving averages.   

Anyone reviewing the project is welcome to explore or critique it. Continuous iteration and learning are central to why I built this in the first place.
