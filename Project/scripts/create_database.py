import sqlite3
import os

# Falscher pfad
kicks_path = r"C:\Users\franz\Desktop\WebApp (Werkstück)\Project\static\samples\Drum Samples\Kicks"
db_path = r"C:\Users\franz\Desktop\WebApp (Werkstück)\Music Gallery (Database)\music_gallery.db"


# Connect to db_path via sqlite3
def connect_to_db_and_add_samples():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM sample_kick_gallery")
    for file in os.listdir(kicks_path):
        if file.endswith(".wav"):
            print(file)
            kick_path = os.path.join(kicks_path, file).replace("\\", "/")
            c.execute(f"INSERT INTO sample_kick_gallery (sample_name, sample_path, sample_type) VALUES ('{file}', '{kick_path}', 'kick')")
    conn.commit()
    conn.close()


def main():
    connect_to_db_and_add_samples()
    #
    # if not os.path.exists("music_gallery.db"):
    #     conn = sqlite3.connect("music_gallery.db")
    #     c = conn.cursor()
    #     c.execute("""CREATE TABLE kick_gallery (
    #             id integer PRIMARY KEY,
    #             sample_name text,
    #             sample_path text,
    #             type text,
    #             key text,
    #             genre text,
    #             subgenre text,
    #             description text
    #             )""")
    #     conn.commit()
    #     conn.close()
    #     print("Database created successfully.")
    #
    #     conn = sqlite3.connect("music_gallery.db")
    #     c = conn.cursor()
    #     for file in os.listdir(kick_path):
    #         c.execute("INSERT INTO kick_gallery VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", (file, kick_path, "kick", "", "", "", ""))
    #     conn.commit()
    #     conn.close()
    #     print("Kick Gallery added successfully.")


if __name__ == "__main__":
    main()


