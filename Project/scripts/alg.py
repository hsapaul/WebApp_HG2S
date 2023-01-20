"""
This File contains the "decision algorithms" for the project.
1. The first algorithm decides which key and bpm the song is mostly expected to be in.


Input:
    song_info:
        found_artists
        found_instruments
        found_genres
        found_time_information

tonic_dict = {"C": 0, "C#":0, "D":0, "D#":0, "E":0, "F":0, "F#":0, "G":0, "G#":0, "A":0, "A#":0, "B":0}

def decide_on_tonic(song_info_dict):
    if tonic was given in text prompt:
        return tonic
    if artist was given in text prompt:
        get artist's top 20 song names
        get tonics of those songs
        add +1 to tonic_dict for each collected tonic
    if genre was given in text prompt:
        get genre's top 20 song names
        get tonics of those songs
        add +2 to tonic_dict for each collected tonic
    return max(tonic_dict)

    artists -> top 20 songs -> 20 keys

"""

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import re
import json
import wikipedia
import requests
from urllib.parse import urlparse, parse_qs

# «──────────── « ⋅ʚ GLOBAL VARIABLES ɞ⋅ » ────────────»
SPOTIPY_CLIENT_ID = "219ba74a35424294b39fb87b279d137b"
SPOTIPY_CLIENT_SECRET = "cfc5da6d3e9e482ebf3900f81b4f04d9"
GET_SONG_KEY_API_KEY = "d3f9654fb2153c3b40c89c676bab2871"


def get_song_key(*search_info):
    search_term = " ".join(search_info)
    # # Get song key from API with "Web API base url", "method"=get and authorization as api key or x-api-key
    # url_params = {"method": "track.search", "track": search_term, "format": "json", "api_key": GET_SONG_KEY_API_KEY}
    # response = requests.get("https://api.getsongbpm.com", params=url_params)
    # # Get the key from the response
    # print(response)
    response = requests.get(f"https://api.getsongbpm.com/track/search/?api_key={GET_SONG_KEY_API_KEY}&format=json&track={search_term}",
                            params={"key": GET_SONG_KEY_API_KEY})
    print(response)


def get_top_songs_from_genre(genre):
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    top_results = sp.search(q=f"genre:{genre}", type="track", limit=10)
    top_songs = [str(song["name"]).split(" - ")[0]for song in top_results["tracks"]["items"]]
    top_songs = [re.sub(r'\([^)]*\)', '', song).strip() for song in top_songs]
    chars_to_remove = ["(", ")", "[", "]", "{", "}", ":", ";", ",", ".", "!", "?", "’", "'", '"']
    top_songs = ["".join([char for char in song if char not in chars_to_remove]) for song in top_songs]
    return top_songs


def find_genres_for_instruments(instrument):
    # Get wikipedia article for instrument
    article = wikipedia.page(instrument).content
    genre_txt_path = r"C:\Users\franz\Desktop\WebApp (Werkstück)\Music Gallery (Database)\1. Natural Language Processing\genres\spotify_genres.txt"
    # Check if any of the genres are in the article and save them in the dictionary with a counter
    genre_dict = {}
    with open(genre_txt_path, "r") as f:
        for line in f:
            if line.strip() in article:
                # Count plus 1 for each genre found
                genre_dict[line.strip()] = genre_dict.get(line.strip(), 0) + 1
    return genre_dict


# Get the top 20 songs of an artist with the Spotify API
def get_artist_top_20_songs(artist):
    # Get Top 5 Songs by Artist
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    top_results = sp.search(q=f"artist:{artist}", type="track", limit=2)
    top_songs = [str(song["name"]).split(" - ")[0]for song in top_results["tracks"]["items"]]
    top_songs = [re.sub(r'\([^)]*\)', '', song).strip() for song in top_songs]
    chars_to_remove = ["(", ")", "[", "]", "{", "}", ":", ";", ",", ".", "!", "?", "’", "'", '"']
    top_songs = ["".join([char for char in song if char not in chars_to_remove]) for song in top_songs]
    return top_songs


# Get artist genre
def get_artist_genre(artist):
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    artist_info = sp.search(q=f"artist:{artist}", type="artist", limit=1)
    artist_genre = artist_info["artists"]["items"][0]["genres"]
    return artist_genre if artist_genre else None


"""
Algorithms
"""


# Input: Integer Dictionary e.g. ["Pop":5,"Rock":3,"Jazz":2]
# Output: Percentage-Probability Dict. ["Pop":50%,"Rock":30%,"Jazz":20%]
def calc_probabilities(dict):
    total = sum(dict.values())
    for key in dict:
        dict[key] = str(int(dict[key] / total * 100)) + "%"
    return dict


def decide_on_tonic(song_info_dict):
    tonic_dict = {"C": 0, "C#": 0, "D": 0, "D#": 0, "E": 0, "F": 0,
                  "F#": 0, "G": 0, "G#": 0, "A": 0, "A#": 0, "B": 0}
    if "found_artists" in song_info_dict:
        for artist in song_info_dict["found_artists"]:
            print(artist)
            # Get Top 20 Songs by Artist
            top_songs = get_artist_top_20_songs(artist)
            print(top_songs)
            # Get Tonic of Top 20 Songs
            for song in top_songs:
                tonic = get_tonic_of_song(song)
                tonic_dict[tonic] += 1

def get_artist_genres(artist):
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    artist_info = sp.search(q=f"artist:{artist}", type="artist", limit=1)
    artist_genre = artist_info["artists"]["items"][0]["genres"]
    return artist_genre if artist_genre else None


def algorithm_genre(song_info_dict):
    genre_dict = {}
    if "found_genres" in song_info_dict:
        for genre in song_info_dict["found_genres"]:
            genre_dict[genre] = 5
    if "found_artists" in song_info_dict:
        for artist in song_info_dict["found_artists"]:
            artist_genre = get_artist_genre(artist)
            if artist_genre:
                for genre in artist_genre:
                    if genre in genre_dict:
                        genre_dict[genre] += 3
                    else:
                        genre_dict[genre] = 3
    if "found_instruments" in song_info_dict:
        for instrument in song_info_dict["found_instruments"]:
            genres = find_genres_for_instruments(instrument)
            # Merge dictionaries
            for genre in genres:
                if genre in genre_dict:
                    genre_dict[genre] += genres[genre]
                else:
                    genre_dict[genre] = genres[genre]
    #print(genre_dict)
    return calc_probabilities(genre_dict)


def main(found_entities):
    # # if "Tonic" not in song_info_dict:
    # #     decide_on_tonic(song_info_dict)
    # genre_dict = algorithm_genre(found_entities)
    #
    # print(json.dumps(genre_dict, indent=4))
    #
    # song_dict = {}
    #
    #
    # top_songs_of_genre = get_top_songs_from_genre("classic rock")
    # print(json.dumps(top_songs_of_genre, indent=4))
    get_song_key("The Beatles", "Yesterday", "Let it Be")


if __name__ == "__main__":
    main({"mode": "major", "found_artists": [], "found_genres": [],
          "found_instruments": ["flute"], "bpm": 120})
