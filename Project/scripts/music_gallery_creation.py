"""
This Script fills the database with the samples from the sample folders.
"""
import sqlite3
import os


def get_absolute_paths():
    # GET FOLDER PATH OF THIS FILE | ALTERNATIVE: momentary_path = os.path.dirname(os.path.abspath(__file__))
    momentary_path = os.getcwd()
    print("MOMENTARY PATH: ", momentary_path)  # DEBUG

    # Drum Sample Path
    drum_sample_path = os.path.join(momentary_path, "static", "samples", "drum_samples")
    print("DRUM SAMPLE PATH:", drum_sample_path)  # DEBUG

    # Database Path
    music_gallery_db_path = os.path.join(momentary_path, "models", "music_gallery.db")
    print("DATABASE PATH:", music_gallery_db_path)  # DEBUG

    return [drum_sample_path, music_gallery_db_path]


def fill_database(args):
    drum_sample_path, music_gallery_db_path = args
    # Convert db path to double backslashes
    music_gallery_db_path = music_gallery_db_path.replace("\\", "\\\\")
    print(music_gallery_db_path)  # DEBUG
    # Connect to Database
    db = sqlite3.connect(music_gallery_db_path)
    cursor = db.cursor()
    # Get all Subfolders
    sub_folders = ["kicks", "snares", "hihats", "claps", "percussions"]
    for sub_folder in sub_folders:
        cursor.execute("CREATE TABLE IF NOT EXISTS " + sub_folder + " (id INTEGER PRIMARY KEY, name TEXT, path TEXT, type TEXT)")
        current_sample_names = cursor.execute("SELECT name FROM " + sub_folder).fetchall()
        for sample in os.listdir(os.path.join(drum_sample_path, sub_folder)):
            if sample.endswith(".wav") and (sample,) not in current_sample_names:
                cursor.execute("INSERT INTO " + sub_folder + " (name, path, type) VALUES (?, ?, ?)", (sample, os.path.join(drum_sample_path, sub_folder, sample), sub_folder))
                db.commit()
    db.close()


def fill_sample_db(sample_db_path):
    fill_database(get_absolute_paths())


if __name__ == "__main__":
    fill_sample_db()
