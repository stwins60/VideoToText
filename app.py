from flask import Flask, render_template, request, session, redirect, url_for, flash, Blueprint
import sqlite3 as db
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# bp = Blueprint('app', __name__, url_prefix='/app')

conn = db.connect('schema.db')
cur = db.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', title='About us')
    # return render_template('index.html')
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', title='Login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method  == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        cur.execute("SELECT * FROM users WHERE username = % ", (username,))
        
        if username == 'admin' and password == 'admin':
            return redirect(url_for('index'))
        else:
            msg = 'Invalid username or password'
    return render_template('signup.html', title='Signup')

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    return render_template('forgotpassword.html', title='Forgot Password')


if __name__ == '__main__':
    app.run(debug=True)