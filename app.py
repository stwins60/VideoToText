from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint

app = Flask(__name__)

# bp = Blueprint('app', __name__, url_prefix='/app')

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
    return render_template('signup.html', title='Signup')

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    return render_template('forgotpassword.html', title='Forgot Password')


if __name__ == '__main__':
    app.run(debug=True)