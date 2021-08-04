from flask import Flask, render_template, request, session, redirect, url_for, flash, send_from_directory
import sqlite3 as db
# from werkzeug.security import check_password_hash, generate_password_hash
import re, os
import speech_recognition as sr
import moviepy.editor as mp
from pydub import AudioSegment
from pydub.silence import split_on_silence
from datetime import datetime
import shutil

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

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])

# bp = Blueprint('app', __name__, url_prefix='/app')

@app.route('/convert', methods=['GET', 'POST'])
def convert():
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
                # conv_file = date + file_name
                VIDEO_FILE = os.path.join(app.config['UPLOAD_PATH'], file_name)
                OUTPUT_AUDIO_FILE = os.path.join(app.config['UPLOAD_PATH'], output_audio)
                CONVERTED_TEXT_FILE = os.path.join(app.config['UPLOAD_PATH'], output_text)
                try:
                    clip = mp.VideoFileClip(r"{}".format(VIDEO_FILE))
                    clip.audio.write_audiofile(r"{}".format(OUTPUT_AUDIO_FILE))
                    r = sr.Recognizer()
                    # audio_clip = sr.AudioFile(r"{}".format(OUTPUT_AUDIO_FILE))
                    get_large_audio_transcription(r"{}".format(OUTPUT_AUDIO_FILE))
                    msg = 'Speech to text conversion is done.'
                except Exception as e:
                    msg = 'Error in converting speech to text. {}'.format(e)
            return render_template('convert.html', filename=file_upload.filename, msg=msg)
        # print(file_upload)
    return render_template('convert.html')

def get_large_audio_transcription(path):
    CONVERTED_TEXT_FILE = os.path.join(app.config['UPLOAD_PATH'], output_text)
    r = sr.Recognizer()
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)
    CONV_TEXT = open(CONVERTED_TEXT_FILE, 'w+')  
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    for file in os.listdir(current_dir):
        if 'audio-chunks' in file:
            shutil.rmtree(os.path.join(current_dir, file))
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    full_text = ""
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened)
                # write the text to a file
                CONV_TEXT.write(text + "\n")
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                # print(chunk_filename, ":", text)
                full_text += text
    # return the text for all chunks detected
    return full_text

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

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Home')
    # return render_template('index.html')


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
            return redirect(url_for('convert'))
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

@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    return render_template('contactus.html', title='Contact Us')


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