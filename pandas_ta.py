#imports
#!pip install pandas_ta
import numpy as np
import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import pandas_ta as ta
import matplotlib.pyplot as plt
from datetime import date
from numpy import array

#Setup
plt.style.use('fivethirtyeight')
yf.pdr_override()

#Getting the portfolios
#Enter stock symbols in your portfolio here:
stocksymbols = ['NVDA']

#enter the start date and end date
startdate = date(2020,8,4)
end_date = date.today()
initial_cash = 100000
num_stocks = len(stocksymbols)  # Number of stocks in the portfolio
cash_balance = initial_cash
cash_list = [cash_balance]

def getMyPortfolio(stocks = stocksymbols ,start = startdate , end = end_date):
    data = web.get_data_yahoo(stocks , start = start ,end= end )
    return data

#test the portfolio function
data = getMyPortfolio(stocksymbols)

#Trading Strategy:
def bb_strategy(data):
    bbBuy = []
    bbSell = []
    position = False
    cash_balance = 100000
    #get b bands for closing prices
    bb = ta.bbands(data['Adj Close'], length=20,std=2)
    #Add to the original data:
    data = pd.concat([data, bb], axis=1).reindex(data.index)
    #Strategy:
    #Buy when the Close Price touches upon the lower band (BBL lengthstandard-deviation) indicating an oversold scenario S
    #sell when the Close Price touches upon the upper band (BBU length_standard-deviation) indicating an overbought scenario.
    for i in range(len(data)):
        if data['Adj Close'][i] < data['BBL_20_2.0'][i]:
            if position == False and (cash_balance - data['Adj Close'][i]) > 0:
                bbBuy.append(data['Adj Close'][i])
                bbSell.append(np.nan)
                position = True
                cash_balance -= data['Adj Close'][i]
                cash_list.append(cash_balance)
            else:
                bbBuy.append(np.nan)
                bbSell.append(np.nan)
        elif data['Adj Close'][i] > data['BBU_20_2.0'][i]:
            if position == True:
                bbBuy.append(np.nan)
                bbSell.append(data['Adj Close'][i])
                cash_balance += data['Adj Close'][i]
                position = False 
                cash_list.append(cash_balance)
            else:
                bbBuy.append(np.nan)
                bbSell.append(np.nan)
        else :
            bbBuy.append(np.nan)
            bbSell.append(np.nan)

    data['bb_Buy_Signal_price'] = bbBuy
    data['bb_Sell_Signal_price'] = bbSell

    return data

#storing the function
data = bb_strategy(data)

#plot the data
fig, ax1 = plt.subplots(figsize=(14,8))
fig.suptitle(stocksymbols[0], fontsize=10, backgroundcolor='blue', color='white')
ax1 = plt.subplot2grid((14, 8), (0, 0), rowspan=8, colspan=14)
ax2 = plt.subplot2grid((14, 12), (10, 0), rowspan=6, colspan=14)
ax1.set_ylabel('Price in ₨')
ax1.plot(data['Adj Close'],label='Close Price', linewidth=0.5, color='blue')
ax1.scatter(data.index, data['bb_Buy_Signal_price'], color='green', marker='^', alpha=1)
ax1.scatter(data.index, data['bb_Sell_Signal_price'], color='red', marker='v', alpha=1)
ax1.legend()
ax1.grid()
ax1.set_xlabel('Date', fontsize=8)
ax2.plot(data['BBM_20_2.0'], label='Middle Band', color='blue', alpha=0.35) #middle band
ax2.plot(data['BBU_20_2.0'], label='Upper Band', color='green', alpha=0.35) #Upper band
ax2.plot(data['BBL_20_2.0'], label='Lower Band', color='red', alpha=0.35) #lower band
ax2.fill_between(data.index, data['BBL_20_2.0'], data['BBU_20_2.0'], alpha=0.1)
ax2.legend(loc='upper left')
ax2.grid()
plt.show()
ax3 = plt.subplot2grid((14, 8), (0, 0), rowspan=8, colspan=14)
ax3.plot(cash_list)
ax3.set_ylabel("Cash")
ax3.set_xticklabels(ax1.get_xticklabels())
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.show()
