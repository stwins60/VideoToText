from flask import Flask, render_template, request, session, redirect, url_for, flash, Blueprint
import sqlite3 as db
from werkzeug.security import check_password_hash, generate_password_hash
import re, os


os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'development'

current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# bp = Blueprint('app', __name__, url_prefix='/app')

# @app.route('/')
# def index():
#     return render_template('login.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', title='About us')
    # return render_template('index.html')
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    alert = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        conn = db.connect(current_dir +'\database.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username=?', (username,))
        user = cur.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            alert = 'You are logged in'
            flash(alert)
            return redirect(url_for('index'))
        else:
            alert = 'Wrong password'
    return render_template('login.html', title='Login', alert=alert)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method  == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        print(username, password, email)
        conn = db.connect(current_dir +'\database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = % s", (username,))
        user = cur.fetchone()   
        
        if user:
            msg = 'Username already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill all the fields !'
        else:
            cur.execute("INSERT INTO database.users (username, password, email) VALUES (% s, % s, % s)", (username, generate_password_hash(password), email))
            conn.commit()
            msg = 'Signed up successfully !'
    return render_template('signup.html', title='Signup', msg=msg)

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    return render_template('forgotpassword.html', title='Forgot Password')


if __name__ == '__main__':
    app.run(debug=True)