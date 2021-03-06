from sqlite3.dbapi2 import Connection
from flask import Flask, render_template, request, session, redirect, url_for, flash, send_from_directory, send_file
import sqlite3 as db
from werkzeug.utils import secure_filename
import re, os
import speech_recognition as sr
import moviepy.editor as mp
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.playback import play
from passlib.hash import sha256_crypt
from datetime import datetime
import shutil
import subprocess
import io
from flask_cors import CORS
import pyttsx3

import boto3
import boto.s3.connection
import boto.s3.key
# import auth


date = str(datetime.date(datetime.now()))

output_audio = date + "_output.wav"
output_text = date + "_output.txt"

os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'development'

current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

CORS(app)

app.secret_key = 'your secret key'
app.config['UPLOAD_EXTENSIONS'] = ['.mp3', '.mp4', '.wav']
app.config['UPLOAD_PATH'] = os.path.join(current_dir, 'static\\uploads')

# app.config['S3_ACCESS_KEY'] = auth.S3_ACCESS_KEY
# app.config['S3_SECRET_KEY'] = auth.S3_SECRET_KEY
# app.config['S3_BUCKET'] = auth.S3_BUCKET


# creating an upload folder
upload_folder = os.path.join(current_dir, 'static\\uploads')

if os.path.exists(upload_folder):
    shutil.rmtree(upload_folder)
if not os.path.isdir(upload_folder):
    os.mkdir(upload_folder)


# create a function to upload a file to s3
# def upload_file_to_s3(file_name):
#     conn = boto.connect_s3(app.config['S3_ACCESS_KEY'], app.config['S3_SECRET_KEY'])
#     bucket = conn.get_bucket(app.config['S3_BUCKET'])
#     k = boto.s3.key.Key(bucket)
#     k.key = file_name
#     k.set_contents_from_filename(os.path.join(app.config['UPLOAD_PATH'], file_name))
#     k.make_public()
#     return k.generate_url(expires_in=0, query_auth=False)

# create a function to download a file from s3
# def download_file_from_s3(file_name):
#     conn = boto.connect_s3(app.config['S3_ACCESS_KEY'], app.config['S3_SECRET_KEY'])
#     bucket = conn.get_bucket(app.config['S3_BUCKET'])
#     k = boto.s3.key.Key(bucket)
#     k.key = file_name
#     k.get_contents_to_filename(os.path.join(app.config['UPLOAD_PATH'], file_name))
#     return os.path.join(app.config['UPLOAD_PATH'], file_name)


@app.route('/convert', methods=['GET', 'POST'])
def convert():
    msg = ''
    converted_text = ''
    if request.method == 'POST':
        file_upload = request.files['upload']
        file_name = file_upload.filename
        if file_name != '':
            file_extension = os.path.splitext(file_name)[1]
            if file_extension not in app.config['UPLOAD_EXTENSIONS']:
                msg = 'File extension not allowed'
            else:
                file_upload.save(
                    os.path.join(app.config['UPLOAD_PATH'], file_name))
                msg = 'File uploaded successfully'
                conv_file = date + file_name
                VIDEO_FILE = os.path.join(app.config['UPLOAD_PATH'], file_name)
                OUTPUT_AUDIO_FILE = os.path.join(app.config['UPLOAD_PATH'],
                                                 output_audio)
                CONVERTED_TEXT_FILE = os.path.join(app.config['UPLOAD_PATH'],
                                                   output_text)
                print(CONVERTED_TEXT_FILE)
                # call the upload_file_to_s3 function
                # upload_file_to_s3(VIDEO_FILE)
                # upload_file_to_s3(output_audio)
                # upload_file_to_s3(CONVERTED_TEXT_FILE)

                # for file in os.listdir(app.config['UPLOAD_PATH']):
                #     if file.endswith(".wav") and file.endswith(".txt"):
                #         upload_file_to_s3(file)

                # call the download_file_from_s3 function
                # download_file = download_file_from_s3(CONVERTED_TEXT_FILE)
                # print(download_file)

                try:
                    # video_file = download_file_from_s3(app.config['S3_BUCKET'], VIDEO_FILE)
                    # print(video_file)
    
                    clip = mp.VideoFileClip(r"{}".format(VIDEO_FILE))
                    clip.audio.write_audiofile(r"{}".format(OUTPUT_AUDIO_FILE))
                    r = sr.Recognizer()
                    audio_clip = sr.AudioFile(r"{}".format(OUTPUT_AUDIO_FILE))
                    # print(get_duration(output_audio))
                    with audio_clip as source:
                        audio = r.record(source)
                    converted_text = r.recognize_google(audio)
                    with open(CONVERTED_TEXT_FILE, "w") as f:
                        f.write(converted_text)
                    # print(converted_text)
                    # get_large_audio_transcription(
                    #     r"{}".format(OUTPUT_AUDIO_FILE))

                    if request.form['playText']:
                        print("Playing text")
                        engine = pyttsx3.init()
                        engine.say(converted_text)
                        engine.runAndWait()

                    conn = db.connect('schema.db')
                    title = file_name.split('.')[0]
                    audio_title = title + '.wav'
                    text_title = title + '.txt'
                    video_file_size = os.path.getsize(r"{}".format(VIDEO_FILE))
                    converted_text = open(CONVERTED_TEXT_FILE, 'r').read()
                    upload_type = file_name.split('.')[1]
                    
                    with conn:
                        cur = conn.cursor()
                        cur.execute(
                            "INSERT INTO video(title, user_id) VALUES(?,?)",
                            (title, session['id']))
                        cur.execute(
                            "INSERT INTO audio(title, user_id) VALUES(?,?)",
                            (audio_title, session['id']))
                        cur.execute(
                            "INSERT INTO texts(title, user_id) VALUES(?,?)",
                            (text_title, session['id']))
                        cur.execute(
                            "INSERT INTO details(details, size, upload_type, user_id) VALUES(?,?,?,?)",
                            (output_text, video_file_size, upload_type,
                             session['id']))
                        conn.commit()
                        logged_in_user = cur.execute('SELECT * FROM users WHERE id = ?', (session['id'],)).fetchone()
                        
                        print(logged_in_user)
                        
                    msg = 'Speech to text conversion is done.'

                except Exception as e:
                    msg = 'Error in converting speech to text. {}'.format(e)
        if 'playTEXT' in request.form:
            print("Playing text")
            engine = pyttsx3.init()
            engine.say(converted_text)
            engine.runAndWait()
    # return render_template('convert.html', msg=msg, user = session['username'], converted_text=converted_text)
    return render_template('convert.html', converted_text=converted_text)
            


def get_large_audio_transcription(path):
    CONVERTED_TEXT_FILE = os.path.join(app.config['UPLOAD_FOLDER'], output_text)
    r = sr.Recognizer()
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)
    CONV_TEXT = open(CONVERTED_TEXT_FILE, 'w+')
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(
        sound,
        # experiment with this value for your target audio file
        min_silence_len=500,
        # adjust this per requirement
        silence_thresh=sound.dBFS - 14,
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


@app.route('/download', methods=['GET', 'POST'])
def download():
    alert = ""
    for file in os.listdir(app.config['UPLOAD_PATH']):
        if file.endswith(".txt"):
            # download_file = download_file_from_s3(output_text)
            alert = "File downloaded successfully."
        else:
            alert = 'No file found.'
            print("No file found")
        
        # return send_file(download_file, mimetype= 'text/plain', as_attachment=True)
        return send_file('static\\uploads\\' + output_text,
                         attachment_filename='ouptut.txt',
                         mimetype='text/plain',
                         as_attachment=True)
    return render_template('convert.html', alert=alert)

    # return send_file('static\\uploads\\' + output_text,
    #                      attachment_filename='ouptut.txt',
    #                      mimetype='text/plain',
    #                      as_attachment=True)

@app.route('/playText', methods=['GET'])
def playText():
    alert = ""
    for file in os.listdir(app.config['UPLOAD_PATH']):
        try:
            if file.endswith(".wav"):
               text = AudioSegment.from_wav(r"{}".format(file))
               play(text)

        except Exception as e:
            alert = 'Unable to read text. {}'.format(e)
        return render_template('convert.html', alert=alert)

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Home')


@app.route('/auth/admin', methods=['GET', 'POST'])
def admin():
    conn = db.connect('schema.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    return render_template('/auth/admin.html', user = session['username'], users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    alert = ''
    NoneType = type(None)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        conn = db.connect('schema.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cur.fetchone()
        name = user[1]
        id = user[0]

        if user is None:
            alert = 'Invalid username'
        
        elif username == name and sha256_crypt.verify(password, user[4]):
            session['logged_in'] = True
            session['username'] = name
            session['id'] = id
            return redirect(url_for('convert'))

        elif name == 'admin' and password == 'admin':
            session['username'] = name
            session['id'] = id
            session['logged_in'] = True

            return redirect(url_for('admin'))
        else:
            alert = 'Invalid Credentials. Please try again.'

    return render_template('login.html', alert=alert)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        firstname = request.form['fname']
        lastname = request.form['lname']
        email = request.form['email']
        password = request.form['password']
        country = request.form['country']
        

        conn = db.connect('schema.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username, ))
        user = cur.fetchone()

        if user:
            msg = 'Username already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not firstname or not lastname or not email or not password or not country:
            msg = 'Please fill all the fields !'
        else:
            cur.execute(
                "INSERT INTO users (username, firstname, lastname, password, email, country) VALUES (?,?,?,?,?,?)",
                (username, firstname, lastname, sha256_crypt.encrypt(password), email, country))
            conn.commit()
            msg = 'Signed up successfully !'
    return render_template('signup.html', title='Signup', msg=msg)



@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    return render_template('contactus.html', title='Contact Us')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # # cleaning upload folder
    # upload_path = os.path.join(current_dir, 'static\\uploads')
    # for files in os.listdir(upload_path):
    #     path = os.path.join(upload_path, files)
    #     try:
    #         shutil.rmtree(path)
    #     except OSError:
    #         os.remove(path)

    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)

    flash('You are logged out')
    return redirect(url_for('index'))


# @app.route('/uploads/<file_name>')
# def uploaded_file(file_name):
#     return send_from_directory(app.config['UPLOAD_PATH'], file_name)


@app.route('/sendMessage', methods=['GET','POST'])
def sendMessage():
    if request.method == 'POST':
        msg = ''
        firstname = request.form['fname']
        lastname = request.form['lname']
        email = request.form['email']
        message = request.form['message']

        if not firstname or not lastname or not email or not message:
            msg = 'Please fill all the fields !'
        else:
            conn = db.connect('schema.db')
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO enquiry (firstname, lastname, email, message) VALUES (?,?,?,?)',
                (firstname, lastname, email, message))
            conn.commit()
            msg = 'Message sent successfully !'
            redirect(url_for('contactus'))

        return render_template('contactus.html', title='Contact Us', msg=msg)

# #getting file duration
# def get_duration(filename):
#     result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     return float(result.stdout)

# cleaning upload folder
upload_path = os.path.join(current_dir, 'static\\uploads')
for files in os.listdir(upload_path):
    path = os.path.join(upload_path, files)
    try:
        shutil.rmtree(path)
    except OSError:
        os.remove(path)

# create a function to upload the file to s3
# def upload_file_to_s3(file_name):
#     conn = boto.connect_s3(app.config['S3_KEY'], app.config['S3_SECRET'])
#     bucket = conn.get_bucket(app.config['S3_BUCKET'])
#     k = boto.s3.key.Key(bucket)
#     k.key = file_name
#     k.set_contents_from_filename(os.path.join(app.config['UPLOAD_PATH'], file_name))
#     k.make_public()

# # create function that downloads the file from s3
# def download_file_from_s3(bucket_name, file_name):
#     conn = boto.connect_s3(app.config['S3_KEY'], app.config['S3_SECRET'])
#     bucket = conn.get_bucket(bucket_name)
#     k = boto.s3.key.Key(bucket)
#     k.key = file_name
#     k.get_contents_to_filename(file_name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)