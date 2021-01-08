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
