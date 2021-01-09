from flask import Flask, render_template, request, redirect, g, url_for, session
from flask_mysqldb import MySQL
import os
import yaml

from pandas_datareader import data
#from pandas_datareader.utils import RemoteDataError
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import pandas as pd
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer


app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)

# Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)




labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

values = [
    967.67, 1190.89, 1079.75, 1349.19,
    2328.91, 2504.28, 2873.83, 4764.87,
    4349.29, 6458.30, 9907, 16297
]

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
       # Form data
        userDetails = request.form
        name = userDetails['name']
        username = userDetails['username']
        email = userDetails['email']
        password = userDetails['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, username, email, password) VALUES(%s, %s, %s, %s)",
                    (name, username, email, password))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    return render_template('signup.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM users WHERE username = %s AND password = %s',
            (username, password))
        account = cur.fetchone()
        session.pop('user', None)

        if account:
            session['user'] = request.form['username']
            return redirect(url_for('profile'))

    return render_template('index.html')


@app.route('/profile')
def profile():
    if g.user:
        START_DATE = '2020-01-01'
        END_DATE = str(datetime.now().strftime('%Y-%m-%d'))

        ticker = 'GOOG'
        STOCK = 'GOOG'
        # Get data
        stock_data = data.DataReader(ticker, 'yahoo', START_DATE, END_DATE)
        print(stock_data)
        adj_close = stock_data['Adj Close']
        #return stock_data

        # Make into list
        close_price_list = stock_data['Close'].tolist()
        #return close_price_list
        

        date_list = pd.date_range(start=START_DATE,end=END_DATE).strftime('%Y-%m-%d').tolist()
        #print(date_list)
        return render_template('profile.html', user=session['user'], date_list = date_list, close_price_list = close_price_list)
    return redirect(url_for('index'))

@app.route('/analysis')
def analysis():
    if g.user:
        ticker = 'GOOG'
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

        
        #news_df.sort_values(by=['compound'], inplace=True)    
        
        a = news_df['headline'].head()
        
        total = news_df['compound'].sum()
        
        news_df1 = news_df.sort_values(by=['compound'], ascending=False)
        pos_sentiment_1 = news_df1['headline'][0]
        pos_sentiment_2 = news_df1['headline'][1]
        pos_sentiment_3 = news_df1['headline'][2]
        pos_sentiment_4 = news_df1['headline'][3]
        pos_sentiment_5 = news_df1['headline'][4] 
        pos_date_1 = news_df1['date'][0]
        pos_date_2 = news_df1['date'][1]
        pos_date_3 = news_df1['date'][2]
        pos_date_4 = news_df1['date'][3]
        pos_date_5 = news_df1['date'][4]
        print(news_df.head())

        news_df2 = news_df.sort_values(by=['compound'], ascending=True)   
        neg_sentiment_1 = news_df2['headline'][0]
        neg_sentiment_2 = news_df2['headline'][1]
        neg_sentiment_3 = news_df2['headline'][2]
        neg_sentiment_4 = news_df2['headline'][3]
        neg_sentiment_5 = news_df2['headline'][4]
        neg_date_1 = news_df2['date'][0]
        neg_date_2 = news_df2['date'][1]
        neg_date_3 = news_df2['date'][2]
        neg_date_4 = news_df2['date'][3]
        neg_date_5 = news_df2['date'][4]
        print(news_df.head())

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
        return render_template('analysis.html', user=session['user'], total = total,
            pos_sentiment_1 = pos_sentiment_1, pos_sentiment_2 = pos_sentiment_2, pos_sentiment_3 = pos_sentiment_3, pos_sentiment_4 = pos_sentiment_4, pos_sentiment_5 = pos_sentiment_5,
            pos_date_1 = pos_date_1, pos_date_2 = pos_date_2, pos_date_3 = pos_date_3, pos_date_4 = pos_date_4, pos_date_5 = pos_date_5,
            neg_sentiment_1 = neg_sentiment_1, neg_sentiment_2 = neg_sentiment_2, neg_sentiment_3 = neg_sentiment_3, neg_sentiment_4 = neg_sentiment_4, neg_sentiment_5 = neg_sentiment_5,
            neg_date_1 = neg_date_1, neg_date_2 = neg_date_2, neg_date_3 = neg_date_3, neg_date_4 = neg_date_4, neg_date_5 = neg_date_5)
            
    return redirect(url_for('index'))


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
