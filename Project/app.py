"""
Rahmen: Werkstück - Bachelorarbeit (B.Sc.)
Studium: Interaktive Medien, Hochschule Augsburg
Titel: 'INTERAKTIVE WEBAPPLIKATION ZUR TEXTBASIERTEN MUSIKKOMPOSITION'
Autor: Paul Hitzler
"""

# EXTERNAL IMPORTS
from flask import Flask, g, render_template, request, redirect, url_for, session, flash
import datetime  # Saving time on clock to db with every Post
import sqlite3  # Connect to database
import time  # Measuring of Execution Times
from scripts.nlp import main as nlp_task
import scripts.artist_information.artistSearch_WikipediaInformation as artist_wiki
from dotenv import load_dotenv
import scripts.music_gallery_creation as mgc

# GLOBAL CONFIGURATIONS
load_dotenv()
app = Flask(__name__)  # Create Flask App
db_path = r"./models/database.db"
sample_db_path = r"./models/music_gallery.db"
app.secret_key = "123"


# DATABASE CONNECTION
def connect_db(db_path_new):
    # Connect to database with .env variable
    sql = sqlite3.connect(db_path_new)
    sql.row_factory = sqlite3.Row
    return sql


def get_db(db_path):
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db(db_path)
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


"""
HOME ROUTE LANDING PAGE
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    # Loading Site regularly
    if request.method == 'GET':
        return render_template('index.html')
    # One of the Buttons was pressed
    if request.method == 'POST':
        # Responsible Button: "Submit" (Text Prompt)
        if 'submit_button' in request.form:
            start_time = time.time()
            text_prompt = request.form['text_prompt']
            # get static url
            static_url = request.url_root + "static/"
            # Call NLP Task
            found_artists, found_instruments, found_genres, found_time, key_and_bpm = nlp_task(text_prompt, static_url)
            artist_objects = []
            instrument_objects = []
            if len(found_artists) >= 1:
                for artist in found_artists:
                    print(artist)
                    artist_objects.append(artist_wiki.wikipedia_search(artist))
                # Clear out empty artist objects
            print(artist_objects)
            artist_objects = [x for x in artist_objects if x != None]
            # Save Session Data so it can be accessed when posting to marketplace/databse
            session['text_prompt'] = text_prompt
            session['artists'] = artist_objects
            session['instruments'] = found_instruments
            session['genres'] = found_genres
            session['key_and_bpm'] = key_and_bpm
            creation_date = str(datetime.datetime.now())[:-10]
            execution_time = round(time.time() - start_time, 2)
            # Save to Temporary Database "temp_prompt_history" if logged in
            p1_found_entities = [artist_objects, found_instruments, found_genres, found_time, key_and_bpm]
            p2_music_configurations = []
            if 'session_id' in session:
                user_id = session['session_id']
                db = get_db(db_path)
                db.execute('INSERT INTO temp_prompt_history (user_id, text_prompt, p1_found_entities, '
                           f'p2_music_configurations, creation_date, saved_to_marketplace) VALUES ("{user_id}", '
                           f'"{text_prompt}", "{p1_found_entities}", "{p2_music_configurations}", "{creation_date}", 0)')
                db.commit()
            return render_template('index.html', text_prompt=text_prompt, artist_objects=artist_objects,
                                   instruments=found_instruments, key_and_bpm=key_and_bpm, genres=found_genres,
                                   end_time=execution_time)
        # Responsible Button: "Post to Marketplace"
        elif 'post_button' in request.form:
            text_prompt, artists, instruments = session['text_prompt'], session['artists'], session['instruments']
            genres, key_and_bpm = session['genres'], session['key_and_bpm']
            # Get names out of the dictionary
            artist_names = [artist["name"] for artist in artists]
            # Get date and time
            datum = str(datetime.datetime.now())[:-10]
            # Save data to database
            db = get_db(db_path)
            p1_found_entities = [artist_names, instruments, genres, key_and_bpm]
            p2_music_configurations = []
            # Get if user is logged in
            if 'session_user' in session:
                user_name = session['session_user']
            else:
                user_name = "Guest"
            db.execute(
                'INSERT INTO marktplatz_posts (user_name, text_prompt, p1_found_entities, p2_music_configurations, '
                f'post_datum, creation_date, popularity) VALUES ("{user_name}", "{text_prompt}", '
                f'"{p1_found_entities}", "{p2_music_configurations}", "{datum}", "{datum}", 0)')
            for artist in artists:
                print(artist)
                name, genres, instruments, occupation, year = artist["name"], artist["genres"], artist["instruments"], \
                                                              artist["occupation"], artist["year"]
                db.execute(
                    f'INSERT INTO found_artists (artist_name, artist_year, occupations, genres, instruments) VALUES '
                    f'("{name}", "{year}", "{occupation}", "{genres}", "{instruments}")')
            db.commit()
            flash("Your post was successfully submitted!")
            return redirect(url_for('marktplatz'))
        # Responsible Button: "Enter Playground"
        elif 'playground_button' in request.form:
            text_prompt = session['text_prompt']
            return redirect(url_for('playground', text_prompt=text_prompt))


@app.route('/documentation')
def documentation():
    return render_template('documentation.html')


@app.route('/marktplatz', methods=['GET', 'POST'])
def marktplatz():
    # Get data from database
    db = get_db(db_path)
    all_posts = db.execute('select * from marktplatz_posts').fetchall()
    # post_user_names = db.execute('select user_id from marktplatz_posts').fetchall()
    all_found_artists = db.execute('select * from found_artists').fetchall()
    # Regular page call
    if request.method == 'GET':
        return render_template('marketplace.html', posts=all_posts,
                               artists_db=all_found_artists,
                               today=str(datetime.datetime.now())[:10], sort_alg='Popular Posts')
    # Resort the posts
    elif request.method == 'POST':
        sort_alg = request.form.get('form-select')
        if sort_alg == 'Recently Posted':
            posts = sorted(all_posts, key=lambda x: x[3], reverse=True)
        elif sort_alg == 'Most Popular':
            posts = sorted(all_posts, key=lambda x: x[8], reverse=True)
            print(posts)
        return render_template('marketplace.html', posts=posts, artists_db=all_found_artists,
                               today=str(datetime.datetime.now())[:10], sort_alg=sort_alg)


"""
CRUD Operations & Changes by User & Upvotes
"""


@app.route('/delete_post/<int:id>')
def delete(id):
    try:
        db = get_db(db_path)
        db.execute('DELETE FROM marktplatz_posts WHERE id = ?', (id,))
        db.commit()
        flash("Successfully deleted Post!")
        return redirect(url_for('marktplatz'))
    except:
        flash("Something went wrong. Please try again.")
        return redirect(url_for('marktplatz'))


# Post to Marketplace from temp_prompt_history (Profile)
@app.route('/post_to_marketplace/<int:id>')
def post_to_marketplace(id):
    try:
        db = get_db(db_path)
        # Get data from database
        post = db.execute('select * from temp_prompt_history WHERE id = ?', (id,)).fetchone()
        # Get date and time
        datum = str(datetime.datetime.now())[:-10]
        # Save data to database
        username = session['session_user']
        db.execute(
            'INSERT INTO marktplatz_posts (user_name, text_prompt, p1_found_entities, p2_music_configurations, '
            f'post_datum, creation_date, popularity) VALUES ("{username}", "{post[2]}", '
            f'"{post[3]}", "{post[4]}", "{datum}", "{datum}", 0)')
        db.commit()
        flash("Your post was successfully submitted!")
        return redirect(url_for('marktplatz'))
    except:
        flash("Something went wrong. Please try again.")
        return redirect(url_for('marktplatz'))


@app.route('/upvote_post/<int:id>')
def upvote(id):
    # try:
    db = get_db(db_path)
    # Look if user has already upvoted
    if 'session_user' not in session:
        flash("You need to be logged in to upvote!")
        return redirect(url_for('login'))
    else:
        cur = db.execute(f'SELECT liked_post_ids FROM nutzer WHERE id = "{session["session_id"]}"')
        if str(id) in str(cur).split(","):
            flash("You have already upvoted this post!")
            return redirect(url_for('marketplace'))
        else:
            db.execute(f'UPDATE marktplatz_posts SET popularity = popularity + 1 WHERE id = {id}')
            db.execute(
                f'UPDATE nutzer SET liked_post_ids = "{str(cur) + str(id) + ","}" WHERE id = "{session["session_id"]}"')
            db.commit()
        return redirect(url_for('marktplatz'))


@app.route('/change_user_name', methods=['GET', 'POST'])
def change_user_name():
    if request.method == 'POST':
        if request.form['password'] == session['session_password']:
            try:
                db = get_db(db_path)
                db.execute(
                    f'UPDATE nutzer SET username = "{request.form["new_user_name"]}" '
                    f'WHERE username = "{session["session_user"]}"')
                session['session_user'] = request.form['new_user_name']
                db.commit()
                flash("Username changed successfully")
                return redirect(url_for('profile'))
            except:
                flash("There was a problem changing your username")
                return redirect(url_for('profile', username=session['session_user']))
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


@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username, email, password, repeat_password = request.form['username'], request.form['email'], request.form[
            'password'], request.form['repeat_password']
        if password == repeat_password:
            db = get_db(db_path)
            db_nutzer = db.execute('SELECT username, password, email FROM nutzer').fetchall()
            for n in db_nutzer:
                if request.form['username'] == n['username']:
                    flash("Username already taken")
                    return render_template('auth_signup.html', error='Username already taken!')
                elif request.form['email'] == n['email'] and request.form['email'] != "":
                    flash("Email already taken")
                    return render_template('auth_signup.html', error='Email already taken!')
            db.execute(
                'INSERT INTO nutzer (username, email, password, marketplace_post_ids, temp_post_ids, '
                'liked_post_ids, appearance_theme, appearance_light_mode) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                [request.form['username'], request.form['email'], request.form['password'], None, None, None, "default",
                 0])
            db.commit()
            session['session_id'] = db.execute('SELECT id FROM nutzer WHERE username = ?',
                                               [request.form['username']]).fetchone()[0]
            session['session_user'], session['session_password'] = request.form['username'], request.form['password']
            session['session_email'], session['session_theme'] = request.form['email'], "default"
            flash("Signed up successfully!")
            flash("Access the Main Home Page by pressing the Logo in the upper left")
            return redirect(url_for('profile', username=session['session_user']))
        else:
            flash("Passwords don't match")
            return render_template('auth_signup.html')
    return render_template('auth_signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        db = get_db(db_path)
        db_nutzer = db.execute('SELECT id, username, email, password FROM nutzer').fetchall()
        username_or_email = request.form['username_or_email']
        for nutzer in db_nutzer:
            # Check for each User: Username or Email must be correct and the password as well
            if username_or_email in (nutzer['username'], nutzer['email']) \
                    and nutzer['password'] == request.form['password']:
                username, password, email, appearance_theme, appearance_light_mode = db.execute(
                    f'SELECT username, password, email, appearance_theme, appearance_light_mode '
                    f'FROM nutzer WHERE id = {nutzer["id"]}').fetchone()
                session['session_id'], session['session_user'] = nutzer['id'], username
                session['session_password'], session['session_email'] = password, email
                session['session_theme'], session['session_light_mode'] = appearance_theme, appearance_light_mode
                flash(f"Welcome {session['session_user']}! You were successfully logged in. ")
                flash("By pressing on the logo icon on the upper left you get to the Prompt Area")
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


"""
 USER PROFILE - individual per User
"""


@app.route('/users/<username>', methods=['GET', 'POST'])
def profile(username):
    # Get Temp Prompt History
    db = get_db(db_path)
    prompts_for_user_id = db.execute('SELECT id, text_prompt, p1_found_entities, p2_music_configurations, '
                                     'creation_date, saved_to_marketplace FROM temp_prompt_history '
                                     f'WHERE user_id = {session["session_id"]}').fetchall()
    # Chech if post and if submit name is submit_theme
    if request.method == 'GET':
        if 'session_user' in session:
            return render_template('profile.html', session_user=session['session_user'],
                                   your_last_prompts=prompts_for_user_id)
        else:
            return redirect(url_for('login'))
    elif request.method == 'POST':
        if "submit_theme" in request.form:
            # Get requested Theme and Mode
            theme = request.form.get('form-select')
            light_mode = request.form.get('dark_mode_checkbox')
            # Update Theme and Mode in DB
            db = get_db(db_path)
            light_mode = 1 if light_mode == "on" else 0
            db.execute(f'UPDATE nutzer SET appearance_theme = "{theme}", appearance_light_mode = {light_mode} '
                       f'WHERE id = {session["session_id"]}')
            db.commit()
            # Set Session Data and Redirect to Profile
            session['session_theme'], session['session_light_mode'] = theme, light_mode
            flash("Appearance Changed Successfully")
            print(session['session_theme'], session['session_light_mode'])
            return redirect(url_for('profile', username=session['session_user']))


"""
 PROMPT PLAYGROUND - Templates individual per Prompt
"""


@app.route('/playground/<string:text_prompt>')
def playground(text_prompt):
    # Get sample_paths from database
    conn = sqlite3.connect(sample_db_path)
    c = conn.cursor()
    # FETCH SAMPLE PATHS AND NAMES
    sub_folders = ["kicks", "snares", "hihats", "claps", "percussions"]
    sample_dict = {}
    for sub_folder in sub_folders:
        sample_dict[sub_folder] = c.execute(f'SELECT name FROM {sub_folder}').fetchall()
    conn.close()
    static_url = url_for('static', filename='samples/drum_samples/')
    return render_template('playground.html', sample_dict=sample_dict, static_url=static_url, text_prompt=text_prompt)


"""
 TABLE CHECK - Initial Verification of table existence
"""


def create_tables_if_not_exist():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Table for Users - General Settings, Interaction&Activity and Appearance Settings
    c.execute('CREATE TABLE IF NOT EXISTS nutzer (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
              'username TEXT UNIQUE, email TEXT UNIQUE, password TEXT, '
              'marketplace_post_ids TEXT, temp_post_ids TEXT, liked_post_ids TEXT, '
              'appearance_theme TEXT, appearance_light_mode INTEGER)')
    # Table for Posts - Prompt Results, Time Data and Popularity (w/ References to User)
    c.execute('CREATE TABLE IF NOT EXISTS marktplatz_posts (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
              'user_name TEXT, text_prompt TEXT, p1_found_entities TEXT, '
              'p2_music_configurations TEXT, post_datum TEXT, creation_date TEXT, '
              'popularity INTEGER, FOREIGN KEY(user_name) REFERENCES nutzer(username))')
    # Table for History - Prompt Results, Time Data and Popularity (w/ References to User)
    c.execute('CREATE TABLE IF NOT EXISTS temp_prompt_history (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
              'user_id INTEGER, text_prompt TEXT, p1_found_entities TEXT, '
              'p2_music_configurations TEXT, creation_date TEXT, saved_to_marketplace INTEGER, '
              'FOREIGN KEY(user_id) REFERENCES nutzer(id))')
    # Table for Found Artists
    c.execute('CREATE TABLE IF NOT EXISTS found_artists (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
              'artist_name TEXT, artist_year INT, occupation TEXT, genres TEXT, instruments TEXT)')
    conn.commit()
    conn.close()


"""
 APP START - "Interactive Webapplication for text-based music generation"
"""
if __name__ == "__main__":
    create_tables_if_not_exist()
    mgc.fill_sample_db(sample_db_path)
    app.run(debug=True, port=9875)
