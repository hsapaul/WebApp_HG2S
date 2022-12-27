from bs4 import BeautifulSoup
import ssl
import json
from urllib.request import Request, urlopen
import re

# For ignoring SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def metadataScraper(song, artist, genius_url, song_folder, song_id):
    """
    status_code = urllib.request.urlopen(genius_url)
    print(status_code)


    # Get real URL out of searching through site if direct URL not valid
    #status_code = requests.get(genius_url).status_code
    #urllib.request.urlopen('genius_url')

    if status_code == 404:
        search_url = "https://genius.com/search?q=" + "%20".join(str(song).split(" ")) + "%20" + "%20".join(str(artist).split(" "))
        print(search_url)
        search = Request(search_url, headers={'User-Agent': 'Mozilla/5.1'})
        searchpage = urlopen(search).read()
        soup_2 = BeautifulSoup(searchpage, 'html.parser')
        print(soup_2.prettify())
        genius_url = soup_2.find("div", text=re.compile('Top Result')).parent.findChild("a", href=True)["href"]
        print("link not there so: " + str(genius_url))

    """
    # Making the website believe that you are accessing it using a mozilla browser
    req = Request(genius_url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    # Creating a BeautifulSoup object of the html page for easy extraction of data.
    soup = BeautifulSoup(webpage, 'html.parser')
    html = soup.prettify('utf-8')
    song_json = {}

    # Scrape Title
    for title in soup.findAll('title'):
        song_json['Title'] = title.text.strip()

    # Scrape Release Date
    for span in soup.findAll('p'):
        if span.text == "Release Date":
            song_json['Release date'] = span.findNext("div").text

    # Scrape About
    # song_json['About'] = soup.find("h1", text=re.compile('About')).parent.findAll("p")
    paragraphs = soup.find("h1", text=re.compile('About')).parent.findAllNext("p")
    about = []
    for p in paragraphs:
        about.append(p.text)
    song_json['About'] = about

    # Scrape Credits
    interleave_words = ["Interpolations", "Covers", "Remixes", "Performances", "Interpolate", "Songs That Sample", "Release date"]
    credit_section = soup.find("div", text=re.compile('Credits')).parent.findAll("div")[2].findAll("div")
    # credit_list = [c.text for c in credit_section if any(x not in c.text for x in interleave_words)]
    credit_list = []

    for c in credit_section:
        if any(x in c.text for x in interleave_words):
            break
        else:
            credit_list.append(c.text)

    credit_tags = [c for index, c in enumerate(credit_list) if (index + 2) % 3 == 0]
    credit_names = [c for index, c in enumerate(credit_list) if (index + 1) % 3 == 0]
    credit_dict = dict(zip(credit_tags, credit_names))
    song_json["Credits"] = credit_dict

    # Extract the Lyrics of the song
    song_json['Lyrics'] = soup.find('div', attrs={'data-lyrics-container': 'true'}).text

    # Save the json created with the file name as title + .json
    json_name = f'textdata_{song_id}.json'
    with open(f'{song_folder}/{json_name}', 'w') as outfile:
        json.dump(song_json, outfile, indent=4)
        print(f'"{json_name}" CREATED')

    return song_json


def main(song, artist, song_folder):
    song_id = f"{'-'.join(artist.lower().split(' '))}-{'-'.join(song.lower().split(' '))}".replace("'", "").replace("`", "")
    genius_url = f"https://genius.com/{song_id}-lyrics"
    print("LYRICS AND CREDITS URL: " + genius_url)
    return metadataScraper(song, artist, genius_url, song_folder, song_id)


#if __name__ == "__main__":
#    main(song, artist, song_folder)
