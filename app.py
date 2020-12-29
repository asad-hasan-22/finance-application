from flask import Flask, render_template, request, redirect, g, url_for, session
from flask_mysqldb import MySQL
import os
import yaml

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)


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
        return render_template('profile.html', user=session['user'])
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
