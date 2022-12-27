# Imports
from flask import Flask, g, render_template, request, redirect, url_for, session
import sqlite3

# Import Service Scripts
from scripts.step_metadata import get_song_key_and_bpm as metadata
from scripts.step_textdata import main as textdata
from scripts.step_chords.get_chords_url import main as chords_url
from scripts.step_chords.parse_chords import main as chords_2
from scripts.nlp import main as nlp_task

from scripts.open_vst import open as open_vst

app = Flask(__name__)
db_path = r"C:\Users\franz\Desktop\WebApp (Werkstück)\Project\database.db"

# Encrypt and Decrypt Session Data
app.secret_key = "123"


# Connect to database
def connect_db():
    sql = sqlite3.connect(db_path)
    sql.row_factory = sqlite3.Row
    return sql


# Check if variable g has attribute db
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


# Close connection to database
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text_prompt = request.form['text_prompt']
        # Call NLP Task
        word_classification_dict, song_info, end_time = nlp_task(text_prompt)
        return render_template('index.html', text_prompt=text_prompt, word_classification_dict=word_classification_dict,
                               song_info=song_info, end_time=end_time)
    if 'session_user' in session:
        return render_template('index.html', session_user=session['session_user'])
    else:
        return render_template('index.html')


@app.route('/users')
def users():
    db = get_db()
    db_nutzer = db.execute('SELECT username, password FROM nutzer').fetchall()
    return render_template('login.html')


@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        db = get_db()
        db_nutzer = db.execute('SELECT username, password FROM nutzer').fetchall()
        for n in db_nutzer:
            if request.form['username'] == n['username']:
                return render_template('sign_up.html', error='Username already taken!')
        db.execute('INSERT INTO nutzer (username, password) VALUES (?, ?)',
                   [request.form['username'], request.form['password']])
        db.commit()
        session['session_user'] = request.form['username']
        return redirect(url_for('profile'))
    return render_template('sign_up.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        db = get_db()
        db_nutzer = db.execute('SELECT username, password FROM nutzer').fetchall()
        for nutzer in db_nutzer:
            if nutzer['username'] == request.form['username'] and nutzer['password'] == request.form['password']:
                session['session_user'] = request.form['username']
                return redirect(url_for('profile'))
        return "user or password incorrect <br> <a href='/login'>Try again</a>"
    else:
        if 'session_user' in session:
            return redirect(url_for('profile'))
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('session_user', None)
    return redirect(url_for('login'))


@app.route('/user')
def profile():
    if 'session_user' in session:
        return render_template('profile.html', session_user=session['session_user'])
    else:
        return redirect(url_for('login'))


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/services', methods=['POST'])
def service_download():
    # Check which Service was demanded
    if request.form['btn'] == 'Download':
        from scripts.yt_downloader import download_video
        download_url = request.form['url'].replace('"', '')
        download_path = request.form['path'].replace('"', '')
        download_video(download_url, download_path)
        downloaded = True
        return redirect(url_for('services'))
    if request.form['btn'] == 'Scrape':
        song_name = request.form['song']
        artist_name = request.form['artist']
        base_path = request.form['path'].replace('"', '')
        bpm_and_key = metadata(song_name, artist_name, base_path)
        song_json = {"song": song_name,
                     "artist": artist_name,
                     "bpm": bpm_and_key[0],
                     "key": bpm_and_key[1]}
        textdata_json = textdata(song_name, artist_name, base_path)
        # url = chords_url(song_name, artist_name, base_path)
        # chords = chords_2(url, song_name, artist_name, base_path)
        song_json = song_json | textdata_json
        # return render_template("songprofiler.html", song_json=song_json, chord_progression=chords)
        return render_template("services.html", song_json=song_json)


@app.route('/research')
def research():
    return render_template('research.html')


@app.route('/vstplugins', methods=['POST', 'GET'])
def vstplugins():
    if request.method == 'POST':
        #open_vst()
        return render_template('vstplugins.html', bool_open_vst=True)
    return render_template('vstplugins.html')

@app.route('/jstest')
def jstest():
    return render_template('js_test.html')


if __name__ == "__main__":
    app.run(debug=True, port=9875)
