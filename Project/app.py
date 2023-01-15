# Imports
from flask import Flask, g, render_template, request, redirect, url_for, session, flash
import datetime  # Saving time on clock to db with every Post
import sqlite3  # Connect to database
import time  # Measuring of Execution Times
from flask_sqlalchemy import SQLAlchemy

# Import Service Scripts
from scripts.step_metadata import get_song_key_and_bpm as metadata
from scripts.step_textdata import main as textdata
from scripts.step_chords.get_chords_url import main as chords_url
from scripts.step_chords.parse_chords import main as chords_2
from scripts.nlp import main as nlp_task
import scripts.artist_information.artistSearch_ChordProgressions as artist_chords
import scripts.artist_information.artistSearch_WikipediaInformation as artist_wiki

from dotenv import load_dotenv

load_dotenv()

# Create Flask App
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db_path = r"C:\Users\franz\Desktop\WebApp (Werkstück)\Project\database.db"
sample_db_path = r"C:\Users\franz\Desktop\WebApp (Werkstück)\Music Gallery (Database)\music_gallery.db"

# Encrypt and Decrypt Session Data
app.secret_key = "123"


# Connect to database
def connect_db(db_path_new):
    # Connect to database with .env variable
    sql = sqlite3.connect(db_path_new)
    sql.row_factory = sqlite3.Row
    return sql


# Check if variable g has attribute db
def get_db(db_path):
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db(db_path)
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
            start_time = time.time()
            text_prompt = request.form['text_prompt']
            # Call NLP Task
            found_artists, found_instruments, found_genres, found_time, key_and_bpm = nlp_task(text_prompt)
            artist_objects = []
            instrument_objects = []
            if len(found_artists) >= 1:
                for artist in found_artists:
                    print(artist)
                    artist_objects.append(artist_wiki.wikipedia_search(artist))
                # Clear out empty artist objects
            artist_objects = [x for x in artist_objects if x != None]
            # Save Session Data so it can be accessed when posting to marketplace/databse
            session['text_prompt'] = text_prompt
            session['artists'] = artist_objects
            session['instruments'] = found_instruments
            session['genres'] = found_genres
            session['key_and_bpm'] = key_and_bpm
            execution_time = round(time.time() - start_time, 2)
            return render_template('index.html', text_prompt=text_prompt, artist_objects=artist_objects,
                                   instruments=found_instruments, key_and_bpm=key_and_bpm, genres=found_genres,
                                   end_time=execution_time)
        elif 'post_button' in request.form:
            text_prompt, artists, instruments, genres, key_and_bpm = session['text_prompt'], \
                                                                     session['artists'], session['instruments'], \
                                                                     session['genres'], session['key_and_bpm']
            # Get names out of the dictionary
            artist_names = [artist["name"] for artist in artists]
            # Get date and time
            datum = str(datetime.datetime.now())[:-10]
            # Save data to database
            db = get_db(db_path)
            # Get if user is logged in
            if 'session_user' in session:
                user_name = session['session_user']
            else:
                user_name = "Guest"
            db.execute(
                'CREATE TABLE IF NOT EXISTS marketplace_posts (id INTEGER PRIMARY KEY, text_prompt TEXT, user_name TEXT, datum TEXT, instruments TEXT, genres TEXT, key_and_bpm TEXT, popularity INTEGER)')
            db.execute(
                f'insert into marketplace_posts (text_prompt, user_name, datum, artists, instruments, genres, key_and_bpm, popularity) values ("{text_prompt}", "{user_name}", "{datum}", "{artist_names}", "{instruments}", "{genres}", "{key_and_bpm}", 0)')
            # Create table for each artist
            # db.execute('CREATE TABLE IF NOT EXISTS artists (id INTEGER PRIMARY KEY, name TEXT, genres TEXT, instruments TEXT, occupation TEXT, year TEXT)')
            for artist in artists:
                print(artist)
                name, genres, instruments, occupation, year = artist["name"], artist["genres"], artist["instruments"], \
                                                              artist["occupation"], artist["year"]
                db.execute(
                    f'insert into artists (name, genres, instruments, occupations, year) values ("{name}", "{genres}", "{instruments}", "{occupation}", "{year}")')
            # db.execute('insert into artists (name) values ("test")')
            db.commit()
            flash("Your post was successfully submitted!")
            return redirect(url_for('marketplace'))

    if 'session_user' in session:
        return render_template('index.html', session_user=session['session_user'])
    else:
        return render_template('index.html')


@app.route('/documentation')
def documentation():
    return render_template('documentation.html')


@app.route('/marketplace', methods=['GET', 'POST'])
def marketplace():
    # Get data from database
    db = get_db(db_path)
    cur = db.execute('select * from marketplace_posts')
    cur2 = db.execute('select * from artists')
    posts = cur.fetchall()
    artists = cur2.fetchall()
    if request.method == 'GET':
        return render_template('marketplace.html', posts=posts, artists_db=artists, today=str(datetime.datetime.now())[:10], sort_alg='Popular Posts')
    elif request.method == 'POST':
        sort_alg = request.form.get('form-select')
        if sort_alg == 'Recently Posted':
            posts = sorted(posts, key=lambda x: x[3], reverse=True)
        elif sort_alg == 'Most Popular':
            posts = sorted(posts, key=lambda x: x[8], reverse=True)
        return render_template('marketplace.html', posts=posts, artists_db=artists, today=str(datetime.datetime.now())[:10], sort_alg=sort_alg)


"""
CRUD Operations
"""


@app.route('/delete_post/<int:id>')
def delete(id):
    try:
        db = get_db(db_path)
        db.execute(f'delete from marketplace_posts where id = {id}')
        db.commit()
        return redirect(url_for('marketplace'))
    except:
        return "There was a problem deleting that post"


@app.route('/upvote_post/<int:id>')
def upvote(id):
    # try:
    db = get_db(db_path)
    # Look if user has already upvoted
    if 'session_user' not in session:
        flash("You need to be logged in to upvote!")
        return redirect(url_for('login'))
    else:
        cur = db.execute(f'select liked_post_ids from nutzer where id = "{session["session_id"]}"')
        if str(id) in str(cur).split(","):
            flash("You have already upvoted this post!")
            return redirect(url_for('marketplace'))
        else:
            db.execute(f'update marketplace_posts set popularity = popularity + 1 where id = {id}')
            db.execute(
                f'update nutzer set liked_post_ids = "{str(cur) + str(id) + ","}" where id = "{session["session_id"]}"')
            db.commit()
        return redirect(url_for('marketplace'))
    # except:
    #     return "There was a problem upvoting that post"


@app.route('/change_theme/<int:theme_id>')
def change_theme(theme_id):
    theme = theme_id
    return redirect(url_for('profile', theme=theme, username=session['session_user']))
    # session['theme'] = request.args.get('theme')
    # db = get_db(db_path)
    # db.execute(f'update nutzer set theme = "{session["theme"]}" where id = "{session["session_id"]}"')
    # db.commit()
    #
    # return redirect(url_for('index'
    # session['theme'] = ))


@app.route('/change_user_name', methods=['GET', 'POST'])
def change_user_name():
    if request.method == 'POST':
        if request.form['password'] == session['session_password']:
            try:
                db = get_db(db_path)
                db.execute(
                    f'update nutzer set username = "{request.form["new_user_name"]}" where username = "{session["session_user"]}"')
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
        old_password, new_password, reapeat_password = request.form['old_password'], request.form['new_password'], \
                                                       request.form['repeat_password']
        if old_password == session['session_password']:
            if new_password == reapeat_password:
                try:
                    db = get_db(db_path)
                    db.execute(
                        f'update nutzer set password = "{new_password}" where username = "{session["session_user"]}"')
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
    db = get_db(db_path)
    db_nutzer = db.execute('SELECT username, password, theme FROM nutzer').fetchall()
    return render_template('auth_login.html', theme=session['theme'])


@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username, email, password, repeat_password = request.form['username'], request.form['email'], request.form[
            'password'], request.form['repeat_password']
        role = "admin"
        if password == repeat_password:
            db = get_db(db_path)
            db_nutzer = db.execute('SELECT username, password, email FROM nutzer').fetchall()
            for n in db_nutzer:
                if request.form['username'] == n['username']:
                    return render_template('auth_signup.html', error='Username already taken!')
                elif request.form['email'] == n['email'] and request.form['email'] != "":
                    return render_template('auth_signup.html', error='Email already taken!')
            db.execute(
                'INSERT INTO nutzer (username, email, password, role, posted_prompt_ids, liked_post_ids, theme, appearance_mode) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                [request.form['username'], request.form['email'], request.form['password'], role, None, None, "default", 0])
            db.commit()
            session['session_id'] = \
                db.execute('SELECT id FROM nutzer WHERE username = ?', [request.form['username']]).fetchone()[0]
            session['session_user'] = request.form['username']
            session['session_password'] = request.form['password']
            session['session_role'] = role
            session['session_email'] = request.form['email']
            session['session_theme'] = "default"
            flash("Signed up successfully!")
            return redirect(url_for('profile', username=session['session_user']))
        else:
            flash("Passwords don't match")
            return render_template('auth_signup.html')
    return render_template('auth_signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        db = get_db(db_path)
        db_nutzer = db.execute('SELECT id, email, username, password FROM nutzer').fetchall()
        username_or_email = request.form['username_or_email']
        for nutzer in db_nutzer:
            if username_or_email in (nutzer['username'], nutzer['email']) and nutzer['password'] == request.form['password']:
                user, password, email, role, theme, appearance_mode = db.execute(
                    f'select username, password, email, role, theme, appearance_mode from nutzer where id = {nutzer["id"]}').fetchone()
                session['session_id'] = nutzer['id']
                session['session_user'] = user
                session['session_password'] = password
                session['session_email'] = email
                session['session_role'] = role
                session['session_theme'] = theme
                session['appearance_mode'] = appearance_mode
                flash(f"You were successfully logged in {session['session_email']}")
                return redirect(url_for('profile', username=session['session_user']))
        flash("Wrong Username or Password")
        return render_template('auth_login.html')
    else:
        if 'session_user' in session:
            return redirect(url_for('profile', username=session['session_user']))
        else:
            return render_template('auth_login.html')


@app.route('/logout')
def logout():
    session.pop('session_user', None)
    session.pop('session_id', None)
    return redirect(url_for('login'))


@app.route('/users/<username>', methods=['GET', 'POST'])
def profile(username):
    # Chech if post and if submit name is submit_theme
    if request.method == 'POST':
        # Requests
        theme = request.form.get('form-select')
        light_mode = request.form.get('dark_mode_checkbox')
        print(light_mode)
        # DB Executions
        db = get_db(db_path)
        if light_mode is None:
            db.execute(f'update nutzer set appearance_mode = 1 where username = "{session["session_user"]}"')
        elif light_mode == "on":
            db.execute(f'update nutzer set appearance_mode = 0 where username = "{session["session_user"]}"')
        db.execute(f'update nutzer set theme = "{theme}" where username = "{session["session_user"]}"')
        db.commit()
        session['session_theme'] = theme
        session['appearance_mode'] = light_mode
        flash("Appearance Changed Successfully")
        return render_template('profile.html', session_user=session['session_user'], light_mode=light_mode)
    if request.method == 'GET':
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
    # Check if user logged in
    if 'session_user' in session:
        return render_template('services.html', logged_in=True)
    else:
        return render_template('services.html', logged_in=False)


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


@app.route('/playground/<int:id>')
def playground(id):
    db = get_db(db_path)
    text_prompt = db.execute(f'SELECT text_prompt FROM marketplace_posts WHERE id = {id}').fetchone()[0]
    popularity = db.execute(f'SELECT popularity FROM marketplace_posts WHERE id = {id}').fetchone()[0]
    return render_template('js_test.html', id=id, text_prompt=text_prompt, popularity=popularity)


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
    # Get sample_paths from database
    conn = sqlite3.connect(sample_db_path)
    c = conn.cursor()
    sample_paths = c.execute('SELECT sample_path FROM sample_kick_gallery').fetchall()
    sample_names = c.execute('SELECT sample_name FROM sample_kick_gallery').fetchall()
    print(sample_paths)
    sample_names = [str(name[0]).replace("('", "").replace("',)", "") for name in sample_names]
    sample_paths = [str(path[0]).replace("('", "").replace("',)", "") for path in sample_paths]
    print(sample_paths)
    conn.close()
    static_url = url_for('static', filename='samples/drum_samples/')
    # {{ url_for('static', filename='samples/drum_samples/kick/' + kick) }}
    return render_template('js_test.html', kick_paths=sample_paths, kick_names=sample_names, static_url=static_url)


@app.route('/jstest2')
def jstest2():
    return render_template('js_test_2.html')


if __name__ == "__main__":
    app.run(debug=True, port=9875)
