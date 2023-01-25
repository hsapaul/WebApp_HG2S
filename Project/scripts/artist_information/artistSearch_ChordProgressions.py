""" --------------------------------- '''

!!! This file is not implemented in the final version !!!

artistSearch_ChordProgressions.py
Input: Artist Name
Output: List of Chord Dictionaries

''' --------------------------------- """

# «──────────── « ⋅ʚ IMPORT LIBRARIES ɞ⋅ » ────────────»
# Get Top Song Names for Artist Input
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
# Scrape Most Popular Chord Tab for each of the top X Songs
import json
import chompjs
from requests_html import HTMLSession
import html
from typing import NamedTuple, Iterator, Union
import typedload
from urllib import request as r
import re
import time

# «──────────── « ⋅ʚ GLOBAL VARIABLES ɞ⋅ » ────────────»
SPOTIPY_CLIENT_ID = "219ba74a35424294b39fb87b279d137b"
SPOTIPY_CLIENT_SECRET = "cfc5da6d3e9e482ebf3900f81b4f04d9"


# Analysing the Chords
class Chord(str):
    @property
    def is_fis(self) -> bool:
        try:
            return self[1] in {'#', '♯'}
        except IndexError:
            return False

    @property
    def is_b(self) -> bool:
        try:
            return self[1] in {'b', '♭'}
        except IndexError:
            return False

    @property
    def is_extra(self) -> bool:
        # Return the details of the chord, e.g. 'm7' or '7sus4'
        start = 1
        if self.diesis or self.bemolle:
            start += 1
        return self[start:]

    @property
    def dominant(self) -> int:
        TABLE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
        value = TABLE[self[0].upper()]
        if self.is_b:
            value -= 1
        elif self.is_fis:
            value += 1
        return value % 12


class TabClass(NamedTuple):
    content: str

    def tokenize(self) -> Iterator[Union[str, Chord]]:
        for i in self.content.split('[ch]'):
            s = i.split('[/ch]', 1)
            if len(s) > 1:
                sep = ''
                for j in s[0].split('/'):
                    yield sep
                    yield Chord(j)
                    sep = '/'
                yield s[1]
            else:
                yield s[0]

    def make_chord_dict(self):
        chord_dict = {}  # Endprodukt
        chord_progression = []  # Liste mit den Akkorden
        chord_sequence = []  # Temporäre Akkorde von momentaner Sequenz
        content = self.content  # Content noch mit html tags

        for index, i in enumerate(self.tokenize()):
            if isinstance(i, Chord):
                chord_sequence.append(i)
            else:
                i = i.replace('[tab]', '').replace('[/tab]', '')
                if "[" in i:
                    i = i.replace("\r", "")
                    i = i.replace("\n", "")
                    i = i[i.find("[") + 1:i.find("]")]
                    chord_progression.append(chord_sequence)
                    chord_sequence = []
                    chord_sequence.append(i)
        chord_dict = {chord_progression[number][0]: ", ".join(chord_progression[number][1:]) for number, section in
                      enumerate(chord_progression) for index, chord in enumerate(section)}
        return chord_dict


class ViewTabs(NamedTuple):
    wiki_tab: TabClass


def get_top_songs(artist):
    # Get Top 5 Songs by Artist
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    top_5_results = sp.search(q=f"artist:{artist}", type="track", limit=5)
    top_5_songs = [str(song["name"]).split(" - ")[0]for song in top_5_results["tracks"]["items"]]
    top_5_songs = [re.sub(r'\([^)]*\)', '', song).strip() for song in top_5_songs]
    chars_to_remove = ["(", ")", "[", "]", "{", "}", ":", ";", ",", ".", "!", "?", "’", "'", '"']
    top_5_songs = ["".join([char for char in song if char not in chars_to_remove]) for song in top_5_songs]
    return top_5_songs


def get_chord_urls(artist, songs):
    chord_urls = []
    s = HTMLSession()
    # Get URL for each Song
    base_url = "https://www.ultimate-guitar.com/search.php?search_type=title&value="
    for song in songs:
        search_url = base_url + "%20".join(str(artist).split(" ")) + "%20" + "%20".join(str(song).split(" "))
        r = s.get(search_url)
        # NAVIGATE THROUGH HTML AND JSON
        items = r.html.find('div')
        item = items[2]
        first_link = item.attrs['data-content']
        data = chompjs.parse_js_object(first_link)
        results = data['store']['page']['data']['results']
        # LIST COMPREHENSION WITHOUT ITEMS WITHOUT VOTES OR DONT CONTAIN WORDS
        dict_items = {result['tab_url']: result['votes'] for result in results if
                      "chords" in str(result['tab_url']) and result['votes'] > 0}
        #print(json.dumps(dict_items, indent=4))
        # RETURN TOP RESULT FROM SEARCH LIST
        chord_urls.append(max(dict_items, key=dict_items.get))
    return chord_urls


def get_chords(url):
    req = r.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    lineheader = b'<div class="js-store" data-content="'
    with r.urlopen(req) as f:
        for i in f:
            i = i.strip()
            if i.startswith(lineheader):
                content = i[len(lineheader):-1].split(b'"', 1)[0]
                unescaped = html.unescape(content.decode('utf8'))
                content = unescaped.encode('utf8')
                page_data = json.loads(content)['store']['page']['data']['tab_view']
                a = typedload.load(page_data, ViewTabs)
                return a.wiki_tab.make_chord_dict()


def main(artist_name):
    start_time = time.time()
    print(f'-----{str(artist_name)}-----')
    list_of_chord_dicts = []
    # Get Top 5 Songs by Artist
    songs = get_top_songs(artist_name)
    print(f"Top 5 Songs : {', '.join(songs)}")
    # Get URL for each Song
    urls = get_chord_urls(artist_name, songs)
    # print(f"URLs : {', '.join(urls)}")
    # Get Chords for each Song
    for index, url in enumerate(urls):
        chord_dict = get_chords(url)
        expanded_chord_dict = {"song": songs[index], "chords": chord_dict}
        list_of_chord_dicts.append(expanded_chord_dict)
    for chord_dict in list_of_chord_dicts:
        print(chord_dict)
    print(f"✅ [{round(time.time() - start_time, 2)}s] - Scraping of '{artist_name.upper()}'-Chords ")
    print('------------------------')


# «──────────── « ⋅ʚ TEST THE FILE ɞ⋅ » ────────────»
if __name__ == "__main__":
    main("The Beatles")