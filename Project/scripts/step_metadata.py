# IMPORTING LIBRARIES
from bs4 import BeautifulSoup
import requests
import json
import os

search_base_url = "https://www.notediscover.com/search?q="


def get_song_key_and_bpm(song, artist, song_folder):

    json_path = f"{song_folder}\\metadata_{artist}-{song}.json"

    if not os.path.isdir(json_path):
        url = search_base_url + "+".join(str(song + " " + artist).split(" "))

        page = requests.get(url)
        soup = BeautifulSoup(page.content, features="html.parser")
        song_tables = soup.find("tr", {"class": "song"})
        h6 = song_tables.findAll("h6")
        for h in h6:
            if h.text == "BPM":
                song_bpm = h.findPrevious("h3").text
            if h.text == "KEY":
                song_key = h.findPrevious("h3").text

        dictionary = {
            "SONG": song,
            "ARTIST": artist,
            "BPM": song_bpm,
            "KEY": song_key,
        }

        # Serializing json
        json_object = json.dumps(dictionary, indent=4)

        # Writing to sample.json
        with open(json_path, "w") as outfile:
            outfile.write(json_object)

    print("BPM - " + song_bpm)
    print("KEY - " + song_key)

    bpm_and_key = (song_bpm, song_key)

    return bpm_and_key

