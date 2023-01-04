# Imports
from flask import Flask, g, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import datetime

import sqlite3
import os

import jinja2

# Import Service Scripts
from scripts.step_metadata import get_song_key_and_bpm as metadata
from scripts.step_textdata import main as textdata
from scripts.step_chords.get_chords_url import main as chords_url
from scripts.step_chords.parse_chords import main as chords_2
from scripts.nlp import main as nlp_task

from dotenv import load_dotenv

from scripts.open_vst import open as open_vst

load_dotenv()

app = Flask(__name__)
db_path = r"C:\Users\franz\Desktop\WebApp (Werkstück)\Project\database.db"

# Encrypt and Decrypt Session Data
app.secret_key = "123"

# Connect to database
def connect_db():
    # Connect to database with .env variable
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
    # Increase Scope for Variables
    text_prompt = "local"
    word_classification_dict = {}
    song_info = {}
    end_time = 0
    if request.method == 'POST':
        # Check which button was pressed
        if 'submit_button' in request.form:
            text_prompt = request.form['text_prompt']
            # Call NLP Task
            word_classification_dict, song_info, end_time = nlp_task(text_prompt)
            # Save Session Data
            session['text_prompt'] = text_prompt
            session['word_classification_dict'] = word_classification_dict
            session['song_info'] = song_info
            session['end_time'] = end_time
            return render_template('index.html', text_prompt=text_prompt,
                                   word_classification_dict=word_classification_dict,
                                   song_info=song_info, end_time=end_time)
        elif 'post_button' in request.form:
            text_prompt, word_classification_dict, song_info, end_time = session['text_prompt'], session[
                'word_classification_dict'], session['song_info'], session['end_time']
            step1, step2, step3 = "Not yet", "Not yet", "Not yet"
            # Get date and time
            datum = str(datetime.datetime.now())[:-10]
            # Save data to database
            db = get_db()
            # Get if user is logged in
            if 'session_user' in session:
                user_name = session['session_user']
            else:
                user_name = "Guest"
            db.execute(
                'CREATE TABLE IF NOT EXISTS marketplace_posts (id INTEGER PRIMARY KEY, text_prompt TEXT, user_name TEXT, step1 TEXT, step2 TEXT, step3 TEXT, execution_time INTEGER)')
            db.execute(f'insert into marketplace_posts (text_prompt, user_name, datum) values ("{text_prompt}", "{user_name}", "{datum}")')
            db.commit()
            flash("Your post was successfully submitted!")
            return redirect(url_for('marketplace'))

    if 'session_user' in session:
        return render_template('index.html', session_user=session['session_user'])
    else:
        return render_template('index.html')


@app.route('/marketplace')
def marketplace():
    # Get data from database
    db = get_db()
    cur = db.execute('select * from marketplace_posts')
    posts = cur.fetchall()
    return render_template('marketplace.html', posts=posts, today=str(datetime.datetime.now())[:10])


"""
CRUD Operations
"""


@app.route('/delete_post/<int:id>')
def delete(id):
    try:
        db = get_db()
        db.execute(f'delete from marketplace_posts where id = {id}')
        db.commit()
        return redirect(url_for('marketplace'))
    except:
        return "There was a problem deleting that post"


@app.route('/change_user_name', methods=['GET', 'POST'])
def change_user_name():
    if request.method == 'POST':
        if request.form['password'] == session['session_password']:
            try:
                db = get_db()
                db.execute(f'update nutzer set username = "{request.form["new_user_name"]}" where username = "{session["session_user"]}"')
                session['session_user'] = request.form['new_user_name']
                db.commit()
                flash("Username changed successfully")
                return redirect(url_for('profile'))
            except:
                flash("There was a problem changing your username")
                return redirect(url_for('profile'))
        else:
            flash("Wrong Password")
            return redirect(url_for('change_user_name'))
    else:
        return render_template('change_user_name.html')


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        old_password, new_password, reapeat_password = request.form['old_password'], request.form['new_password'], request.form['repeat_password']
        if old_password == session['session_password']:
            if new_password == reapeat_password:
                try:
                    db = get_db()
                    db.execute(f'update nutzer set password = "{new_password}" where username = "{session["session_user"]}"')
                    session['session_password'] = new_password
                    db.commit()
                    flash("Password changed successfully")
                    return redirect(url_for('profile'))
                except:
                    flash("There was a problem changing your password")
                    return redirect(url_for('profile'))
            else:
                flash("Passwords don't match")
                return redirect(url_for('change_password'))
        else:
            flash("Please Type in your exact old Password")
            return redirect(url_for('change_password'))
    else:
        return render_template('change_password.html')


"""
Authentication Logic & Routing
"""


@app.route('/users')
def users():
    db = get_db()
    db_nutzer = db.execute('SELECT username, password FROM nutzer').fetchall()
    return render_template('auth_login.html')


@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username, email, password, repeat_password = request.form['username'], request.form['email'], request.form['password'], request.form['repeat_password']
        role = "admin"
        if password == repeat_password:
            db = get_db()
            db_nutzer = db.execute('SELECT username, password, email FROM nutzer').fetchall()
            for n in db_nutzer:
                if request.form['username'] == n['username']:
                    return render_template('auth_signup.html', error='Username already taken!')
                elif request.form['email'] == n['email']:
                    return render_template('auth_signup.html', error='Email already taken!')
            db.execute('INSERT INTO nutzer (username, email, password, role) VALUES (?, ?, ?, ?)',
                       [request.form['username'], request.form['email'], request.form['password'], role])
            db.commit()
            session['session_user'] = request.form['username']
            session['session_password'] = request.form['password']
            session['session_role'] = role
            session['session_email'] = request.form['email']
            flash("Signed up successfully!")
            return redirect(url_for('profile'))
        else:
            flash("Passwords don't match")
            return render_template('auth_signup.html')
    return render_template('auth_signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        db = get_db()
        db_nutzer = db.execute('SELECT id, email, username, password FROM nutzer').fetchall()
        username_or_email = request.form['username_or_email']
        for nutzer in db_nutzer:
            if username_or_email in (nutzer['username'], nutzer['email']) and nutzer['password'] == request.form['password']:
                user, password, email, role = db.execute(f'select username, password, email, role from nutzer where id = {nutzer["id"]}').fetchone()
                session['session_user'] = user
                session['session_password'] = password
                session['session_email'] = email
                session['session_role'] = role
                flash(f"You were successfully logged in {session['session_email']}")
                return redirect(url_for('profile'))
        flash("Wrong Username or Password")
        return render_template('auth_login.html')
    else:
        if 'session_user' in session:
            return redirect(url_for('profile'))
        return render_template('auth_login.html')


@app.route('/logout')
def logout():
    session.pop('session_user', None)
    session.pop('session_id', None)
    return redirect(url_for('login'))


@app.route('/user')
def profile():
    if 'session_user' in session:
        return render_template('profile.html', session_user=session['session_user'])
    else:
        return redirect(url_for('login'))


@app.route('/admin')
def admin():
    if 'session_user' in session:
        if session['session_id'] == 1:
            return render_template('admin.html')
        else:
            flash('You are not allowed to access this page!')
            return redirect(url_for('profile'))
    else:
        flash('You are not logged in')
        return redirect(url_for('login'))


"""
EXTRA ROUTES
"""


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
        # open_vst()
        return render_template('vstplugins.html', bool_open_vst=True)
    return render_template('vstplugins.html')


@app.route('/jstest')
def jstest():
    return render_template('js_test.html')


if __name__ == "__main__":
    app.run(debug=True, port=9875)
