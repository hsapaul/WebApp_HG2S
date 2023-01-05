"""
INPUT: artist_name
OUTPUT: artist_object
"""

# «──────────── « ⋅ʚ IMPORT LIBRARIES ɞ⋅ » ────────────»
import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass, asdict
import time
import sqlite3


# «──────────── « ⋅ʚ DATACLASS ɞ⋅ » ────────────»
@dataclass
class Artist:
    name: str
    year: int
    occupation: list
    genres: list
    instruments: list


def get_wiki_html(artist_name):
    search_url = f"https://en.wikipedia.org/wiki/{'_'.join(artist_name.split(' '))}"
    print("url : ", search_url)
    resp = httpx.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
    return HTMLParser(resp.text)


# Only for Bands --> Get Band Instruments from Band Member Wiki Pages
def get_band_instruments_and_occupations(href):
    url = f"https://en.wikipedia.org{href}"
    resp = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"})
    html = HTMLParser(resp.text)
    info_box = html.css_first("tbody")
    if info_box is None:
        return None, None
    info_rows = info_box.css("tr")
    new_instruments = []
    new_occupations = []
    for row in info_rows:
        row_label = row.css_first("th")
        if row_label is not None:
            if row_label.text() == "Instruments" or row_label.text() == "Instrument(s)":
                instruments = row.css_first("ul")
                if instruments is not None:
                    new_instruments = [item.text() for item in instruments.css("li")]
            elif row_label.text() == "Occupation" or row_label.text() == "Occupation(s)" or row_label.text() == "Occupations":
                occupations = row.css("ul")
                if len(occupations) > 0:
                    new_occupations = [item.text() for item in occupations[0].css("li")]
    return new_instruments, new_occupations


def parse_data(html, artist):
    info_box = html.css_first("tbody")
    info_rows = info_box.css("tr")
    artist_object = Artist(artist, [], [], [], [])
    for row in info_rows:
        row_label = row.css_first("th")
        if row_label is not None:
            if row_label.text() == "Born":
                year = row.css_first("span.bday").text()[0:4]
                artist_object.year.append(year)
            elif row_label.text() == "Years active":
                year = row.css_first("td").text()
                artist_object.year.append(year)
            elif row_label.text() == "Occupation" or row_label.text() == "Occupation(s)" or row_label.text() == "Occupations":
                occupations = row.css("ul")
                occupation_list = [item.text() for item in occupations[0].css("li")]
                artist_object.occupation = occupation_list
            elif row_label.text() == "Genres":
                if row.css_first("ul") is not None:
                    genres = row.css_first("ul")
                    genre_list = [item.text() for item in genres.css("li")]
                else:
                    genre_list = [row.css("td")[0].text()]
                artist_object.genres = genre_list
            elif row_label.text() == "Instruments" or row_label.text() == "Instrument(s)":
                if row.css_first("ul") is not None:
                    instruments = row.css_first("ul")
                    instrument_list = [item.text() for item in instruments.css("li")]
                else:
                    instrument_list = [row.css("td")[0].text()]
                artist_object.instruments = instrument_list
            elif row_label.text() == "Members" or row_label.text() == "Past members":
                members = row.css_first("ul").css("li")
                member_urls = [item.css_first("a").attributes["href"] for item in members if
                               item.css_first("a") is not None]
                for member_url in member_urls:
                    new_instruments, new_occupations = get_band_instruments_and_occupations(member_url)
                    artist_object.instruments.append(new_instruments)
                    artist_object.occupation.append(new_occupations)
    return artist_object


def print_artist_object(artist_object):
    unwanted_characters = ["[", "]", "'", '"']
    for row in asdict(artist_object).items():
        if row[0] != "name":
            print(row[0], ": ", end="")
            for item in row[1]:
                for character in unwanted_characters:
                    item = str(item).replace(character, "")
                print(item, end=", ")
            print()


def add_to_database(artist_object):
    conn = sqlite3.connect("musicgallery.db")
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS artist_new (artist_name TEXT, artist_year INT, occupation TEXT, genres TEXT, instruments TEXT)")
    c.execute("INSERT INTO artist_new VALUES (?, ?, ?, ?, ?)", (
    str(artist_object.name), str(artist_object.year), str(artist_object.occupation), str(artist_object.genres),
    str(artist_object.instruments)))
    conn.commit()
    conn.close()


def wikipedia_search(artist):
    start_time = time.time()
    try:
        artist = " ".join([word.capitalize() for word in artist.split(" ")])
        print(artist)
        print(f'-------{str(artist)}-------')
        html = get_wiki_html(artist)
        # print(html.text())
        artist_object = parse_data(html, artist)
        print_artist_object(artist_object)
        # add_to_database(artist_object)
        print(f"✅ [{round(time.time() - start_time, 2)}s] - Scraping of '{artist.upper()}'-Data ")
        print('------------------------')
        return artist_object
    except Exception as e:
        print(e)
        print("Error")
        return None


def scrape_artist_names():
    end_goal_url = "https://en.wikipedia.org/wiki/Lists_of_musicians"
    url = "https://en.wikipedia.org/wiki/List_of_best-selling_music_artists"
    resp = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"})
    html = HTMLParser(resp.text)
    tables = html.css("th.scope.row")
    for table in tables:
        print(table.text())


if __name__ == "__main__":
    list = wikipedia_search("jazz")

# Bug Fixing:
# Nirvana --> wrong page
# Killerpilze --> gibt keine genres zurück
# Drake --> musician fehlt
