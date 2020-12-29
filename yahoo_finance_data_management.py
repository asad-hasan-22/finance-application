# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 02:35:49 2020

@author: Asad PC
"""
##through vscode 2

from pandas_datareader import data
#from pandas_datareader.utils import RemoteDataError
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime

START_DATE = '2015-01-01'
END_DATE = str(datetime.now().strftime('%Y-%m-%d'))

STOCK = 'GOOG'

def stock_stats(stock_data):
    return{
        'short_rolling': stock_data.rolling(window=10).mean(),
        'long_rolling': stock_data.rolling(window=100).mean()}

def plot(stock_data, ticker):
    stats = stock_stats(stock_data)
    plt.subplots(figsize=(20,10))
    plt.plot(stock_data, label=ticker)
    plt.show()
    
    
def get_data(ticker):
    stock_data = data.DataReader(ticker, 'yahoo', START_DATE, END_DATE)
    print(stock_data)
    adj_close = stock_data['Adj Close']
    plot(adj_close, ticker)
    return stock_data


stock_data = get_data(STOCK)