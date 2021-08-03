from flask import Flask, render_template, request, session, redirect, url_for, flash, send_from_directory
import sqlite3 as db
# from werkzeug.security import check_password_hash, generate_password_hash
import re, os
import speech_recognition as sr
import moviepy.editor as mp
from datetime import datetime

date = str(datetime.date(datetime.now()))

output_audio = date + "_output.wav"
output_text = date + "_output.txt"


os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'development'

current_dir = os.path.dirname(os.path.abspath(__file__))



app = Flask(__name__)

app.secret_key = 'your secret key'
app.config['UPLOAD_EXTENSIONS'] = ['.mp3', '.mp4', '.wav']
app.config['UPLOAD_PATH'] = os.path.join(current_dir, 'static\\uploads')

@app.route('/')

# bp = Blueprint('app', __name__, url_prefix='/app')

@app.route('/index', methods=['GET', 'POST'])
def index():
    msg = ''
    if request.method == 'POST':
        file_upload = request.files['upload']
        file_name = file_upload.filename
        if file_name != '':
            file_extension = os.path.splitext(file_name)[1]
            if file_extension not in app.config['UPLOAD_EXTENSIONS']:
                msg = 'File extension not allowed'
            else:
                file_upload.save(os.path.join(app.config['UPLOAD_PATH'], file_name))
                msg = 'File uploaded successfully'
                conv_file = date + file_name
                VIDEO_FILE = os.path.join(app.config['UPLOAD_PATH'], conv_file)
                OUTPUT_AUDIO_FILE = os.path.join(app.config['UPLOAD_PATH'], output_audio)
                CONVERTED_TEXT_FILE = os.path.join(app.config['UPLOAD_PATH'], output_text)
                try:
                    clip = mp.VideoFileClip(r"{}".format(VIDEO_FILE))
                    clip.audio.write_audiofile(r"{}".format(OUTPUT_AUDIO_FILE))
                    r = sr.Recognizer()
                    audio_clip = sr.AudioFile(r"{}".format(OUTPUT_AUDIO_FILE))
                    with audio_clip as source:
                        audio = r.record(source)
                    text = r.recognize_google(audio)
                    with open(CONVERTED_TEXT_FILE, 'w') as f:
                        f.write(text)
                    msg = 'Speech to text conversion is done.'
                except Exception as e:
                    msg = 'Error in converting speech to text. {}'.format(e)
            return render_template('index.html', filename=file_upload.filename, msg=msg)
        # print(file_upload)
    return render_template('index.html')

@classmethod
def find_by_username(cls, username):
    conn = db.connect(current_dir +'\database.db')
    cur = conn.cursor()
        
    try:
        data = cur.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if data:
            return (data[1], data[2])
    finally:
        conn.close()

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

        # user = find_by_username(username)

        conn = db.connect(current_dir +'\database.db')
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM users WHERE username= ? AND password= ?', (username, password,))
        user = cur.fetchone()
        name = user[1]
        id = user[0]
        if user:
            session['loggedin'] = True
            session['id'] = id
            session['username'] = name
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

        conn = db.connect(current_dir +'\database.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
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
            cur.execute("INSERT INTO users (username, password, email) VALUES (?,?,?)", (username, password, email))
            conn.commit()
            msg = 'Signed up successfully !'
    return render_template('signup.html', title='Signup', msg=msg)

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    return render_template('forgotpassword.html', title='Forgot Password')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('You are logged out')
    return redirect(url_for('login'))

@app.route('/uploads/<file_name>')
def uploaded_file(file_name):
    return send_from_directory(app.config['UPLOAD_PATH'], file_name)

if __name__ == '__main__':
    app.run(debug=True)