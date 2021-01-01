from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import pandas as pd
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def sentiment_analysis(ticker):
    tickerless_url = 'https://finviz.com/quote.ashx?t='

    tickers = [ticker]
    
    for ticker in tickers:
        url = tickerless_url + ticker
        req = Request(url=url,headers={'user-agent': 'my-app/0.0.1'}) 
        response = urlopen(req)
        html = BeautifulSoup(response)
        news_table = html.find(id='news-table')

    news_list = []
    
    for x in news_table.findAll('tr'):
        text = x.a.get_text() 
        date_scrape = x.td.text.split()
    
        if len(date_scrape) == 1:
            time = date_scrape[0]
                
        else:
            date = date_scrape[0]
            time = date_scrape[1]
        
        news_list.append([ticker, date, time, text])
        


    vader = SentimentIntensityAnalyzer()
    
    cols = ['ticker', 'date', 'time', 'headline']
    
    news_df = pd.DataFrame(news_list, columns=cols)
    
    polarity = news_df['headline'].apply(vader.polarity_scores).tolist()
    
    polarity_df = pd.DataFrame(polarity)
    
    news_df = news_df.join(polarity_df, rsuffix='_ri''ght')
    
    news_df['date'] = pd.to_datetime(news_df.date).dt.date

    
    news_df.sort_values(by=['compound'], inplace=True)    
    
    a = news_df['headline'].head()
    
    total = news_df['compound'].sum()
    
    #good_bad = 0
    if total >= 0:
        print('Good sentiment')
        news_df.sort_values(by=['compound'], inplace=True, ascending=False)
        print('Here are 5 news pieces backing this claim:')
        print(news_df['headline'].head())
    elif total <0:
        print('Bad sentiment')
        news_df.sort_values(by=['compound'], inplace=True)
        print('Here are 5 news pieces backing this claim:')
        print(news_df['headline'].head())        
    
    return total

sentiment_analysis('GOOG')