from requests_html import HTMLSession
import chompjs


def fetch_top_search_result(song, artist):
    # REQUEST SEARCH SITE FOR GIVEN KEYWORDS
    s = HTMLSession()
    base_url = "https://www.ultimate-guitar.com/search.php?search_type=title&value="
    search_query = "%20".join(str(song).split(" ")) + "%20" + "%20".join(str(artist).split(" "))
    search_url = base_url + search_query
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
    # RETURN TOP RESULT FROM SEARCH LIST
    return max(dict_items, key=dict_items.get)


def main(song, artist, song_folder):
    return fetch_top_search_result(song, artist)


#if __name__ == '__main__':
#    main("titanium", "sia")
