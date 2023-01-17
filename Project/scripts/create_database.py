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
    project_folder = os.path.dirname(momentary_path)
    drum_sample_path = os.path.join(project_folder, "static", "samples", "drum_samples")
    print("DRUM SAMPLE PATH:", drum_sample_path)  # DEBUG

    # Database Path
    music_gallery_db_path = os.path.join(project_folder, "models", "music_gallery.db")
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
    sub_folders = ["kicks", "snares", "hihats", "claps", "percussion"]
    for sub_folder in sub_folders:
        cursor.execute("CREATE TABLE IF NOT EXISTS " + sub_folder + " (id INTEGER PRIMARY KEY, name TEXT, path TEXT, type TEXT)")
        current_sample_names = cursor.execute("SELECT name FROM " + sub_folder).fetchall()
        for sample in os.listdir(os.path.join(drum_sample_path, sub_folder)):
            if sample.endswith(".wav") and (sample,) not in current_sample_names:
                cursor.execute("INSERT INTO " + sub_folder + " (name, path, type) VALUES (?, ?, ?)", (sample, os.path.join(drum_sample_path, sub_folder, sample), sub_folder))
                db.commit()
    db.close()


def main():
    fill_database(get_absolute_paths())


if __name__ == "__main__":
    main()




# # Connect to db_path via sqlite3
# def connect_to_db_and_add_samples():
#     conn = sqlite3.connect(db_path)
#     c = conn.cursor()
#     c.execute("SELECT * FROM sample_kick_gallery")
#     for file in os.listdir(kicks_path):
#         if file.endswith(".wav"):
#             print(file)
#             kick_path = os.path.join(kicks_path, file).replace("\\", "/")
#             c.execute(f"INSERT INTO sample_kick_gallery (sample_name, sample_path, sample_type) VALUES ('{file}', '{kick_path}', 'kick')")
#     conn.commit()
#     conn.close()
#
#
# def main():
#     connect_to_db_and_add_samples()
#     #
#     # if not os.path.exists("music_gallery.db"):
#     #     conn = sqlite3.connect("music_gallery.db")
#     #     c = conn.cursor()
#     #     c.execute("""CREATE TABLE kick_gallery (
#     #             id integer PRIMARY KEY,
#     #             sample_name text,
#     #             sample_path text,
#     #             type text,
#     #             key text,
#     #             genre text,
#     #             subgenre text,
#     #             description text
#     #             )""")
#     #     conn.commit()
#     #     conn.close()
#     #     print("Database created successfully.")
#     #
#     #     conn = sqlite3.connect("music_gallery.db")
#     #     c = conn.cursor()
#     #     for file in os.listdir(kick_path):
#     #         c.execute("INSERT INTO kick_gallery VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", (file, kick_path, "kick", "", "", "", ""))
#     #     conn.commit()
#     #     conn.close()
#     #     print("Kick Gallery added successfully.")
#
#
# if __name__ == "__main__":
#     main()


