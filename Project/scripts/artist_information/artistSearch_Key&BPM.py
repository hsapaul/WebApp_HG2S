import httpx
from selectolax.parser import HTMLParser
import time

# !!! This file is not implemented in the final version !!!

def get_keys_and_bpms(artist):
    url = f"https://www.notediscover.com/search?q={'+'.join(artist.split(' '))}"
    print(url)
    artist_keys = []
    artist_bpms = []
    resp = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"})
    html = HTMLParser(resp.text)
    table = html.css("tr")
    for row in table:
        if row.attributes.get("class") == "song":
            lol = row.css("h3")
            count = 0
            for l in lol:
                if count == 2:
                    artist_keys.append(l.text())
                elif count == 3:
                    artist_bpms.append(l.text())
                count += 1
    return artist_keys, artist_bpms


def main(artist):
    start_time = time.time()
    artist_keys, artist_bpms = get_keys_and_bpms(artist)
    print(artist_keys)
    print(artist_bpms)
    print(f"✅ [{round(time.time() - start_time, 2)}s] - Scraping of '{artist.upper()}'-Data ")
    print('------------------------')


if __name__ == "__main__":
    main("Drake")