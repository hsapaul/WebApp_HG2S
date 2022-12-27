import argparse
import gzip
import hashlib
import html
import json
import os
from typing import *
from urllib.request import urlopen
import json

import typedload
#import xtermcolor  # Fürs Colorieren der cmd

from bs4 import BeautifulSoup
import requests
import json
import os

VERSION = '1.2'


class Cache:
    def __init__(self) -> None:
        cachedir = os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~') + '/.cache')
        if not os.path.exists(cachedir):
            raise FileNotFoundError('No cache directory present: %s' % cachedir)
        uugcache = cachedir + '/ultimateultimateguitar/'
        if not os.path.exists(uugcache):
            os.mkdir(uugcache)
        self._cachedir = uugcache

    @staticmethod
    def sha(key: str) -> str:
        return hashlib.sha256(key.encode('utf8')).hexdigest()

    def get(self, key: str) -> Optional[bytes]:
        fname = self._cachedir + str(self.sha(VERSION + key))
        if not os.path.exists(fname):
            return None
        with gzip.open(fname, 'rb') as f:
            return f.read()

    def set(self, key: str, content: bytes) -> None:
        fname = self._cachedir + str(self.sha(VERSION + key))
        with gzip.open(fname, 'wb') as f:
            f.write(content)


class Chord(str):
    @property
    def diesis(self) -> bool:
        """
        True if the chord has a ♯
        """
        try:
            return self[1] in {'#', '♯'}
        except IndexError:
            return False

    @property
    def bemolle(self) -> bool:
        """
        True if the chord has a ♭
        """
        try:
            return self[1] in {'b', '♭'}
        except IndexError:
            return False

    @property
    def details(self) -> str:
        """
        Returns whatever is left after the dominant of the chord

        eg: m, 7, and so on.
        """
        start = 1
        if self.diesis or self.bemolle:
            start += 1
        return self[start:]

    @property
    def dominant(self) -> int:
        TABLE = {
            'C': 0,
            'D': 2,
            'E': 4,
            'F': 5,
            'G': 7,
            'A': 9,
            'B': 11,
        }
        value = TABLE[self[0].upper()]
        if self.bemolle:
            value -= 1
        elif self.diesis:
            value += 1
        return value % 12

    def transpose(self, semitones: int) -> 'Chord':
        TABLE = [
            'C',
            'C♯',
            'D',
            'D♯',
            'E',
            'F',
            'F♯',
            'G',
            'G♯',
            'A',
            'B♭',
            'B',
        ]
        dominant = TABLE[(self.dominant + semitones) % 12]
        return Chord(dominant + self.details)


class WikiTab(NamedTuple):
    content: str

    def get_tokens(self, transpose: int = 0) -> Iterator[Union[str, Chord]]:
        for i in self.content.split('[ch]'):
            s = i.split('[/ch]', 1)
            if len(s) > 1:
                sep = ''
                for j in s[0].split('/'):
                    yield sep
                    yield Chord(j).transpose(transpose)
                    sep = '/'
                yield s[1]
            else:
                yield s[0]

    def print(self, song, artist, song_folder, song_id) -> None:
        content = self.content  # mit html tags
        chord_progression = []
        chord_sequence = []
        for index, i in enumerate(self.get_tokens(0)):
            if isinstance(i, Chord):  # i: Em & Chord: <class '__main__.Chord'>
                # print(xtermcolor.colorize(i, 0x00FF00), end='')
                chord_sequence.append(i)
            else:  # Lyrics and Song-Section
                i = i.replace('[tab]', '').replace('[/tab]', '')
                if "[" in i:
                    i = i.replace("\r", "")
                    i = i.replace("\n", "")
                    i = i[i.find("[") + 1:i.find("]")]
                    chord_progression.append(chord_sequence)
                    chord_sequence = []
                    chord_sequence.append(i)
                # print(i, end='')
        try:
            del chord_progression[0]
        except Exception:
            print("Finding Chords Failed")
            pass

        chord_dict = {chord_progression[number][0]: ", ".join(chord_progression[number][1:]) for number, section in
                      enumerate(chord_progression) for index, chord in enumerate(section)}
        json_object = json.dumps(chord_dict, indent=4)

        # Writing to sample.json
        json_name = f"chords_{song_id}.json"
        with open(f"{song_folder}\{json_name}", "w") as outfile:
            outfile.write(json_object)
        print(f'"{json_name}" CREATED')
        return json_object


class TabView(NamedTuple):
    wiki_tab: WikiTab
    # TODO recommendations
    # TODO applicature


def get_data(url: str) -> Dict[str, Any]:
    """
    From a url of ultimate-guitar, this function returns
    the actual data, which is stored as json.
    """
    lineheader = b'<div class="js-store" data-content="'
    cache = Cache()

    content = cache.get(url)

    if content is None:
        with urlopen(url) as f:
            for i in f:
                i = i.strip()
                if i.startswith(lineheader):
                    content = i[len(lineheader):-1].split(b'"', 1)[0]
                    unescaped = html.unescape(content.decode('utf8'))
                    content = unescaped.encode('utf8')
                    cache.set(url, content)
                    return json.loads(content)
    else:
        return json.loads(content)
    raise ValueError('Unable to parse song data')


def main(url, song, artist, song_folder):
    song_id = f"{'-'.join(artist.lower().split(' '))}-{'-'.join(song.lower().split(' '))}".replace("'", "").replace("`", "")
    print("CHORDS URL: " + str(url))
    # Get json data
    data = get_data(url)
    # Remove useless crap
    data = data['store']['page']['data']['tab_view']

    a = typedload.load(data, TabView)
    return a.wiki_tab.print(song, artist, song_folder, song_id)


if __name__ == '__main__':
    main('https://tabs.ultimate-guitar.com/tab/the-beatles/let-it-be-chords-17427')
