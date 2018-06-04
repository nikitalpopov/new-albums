import lxml.html
import requests
from datetime import datetime
from operator import itemgetter


def extract(el, css_sel):
    ms = el.cssselect(css_sel)
    return None if len(ms) != 1 else ms[0].text


def get_albums(artist_id):
    url = "http://www.discogs.com/artist/" + str(artist_id) + "?limit=500"
    r = requests.get(url, headers={'User-Agent': 'I wish your API was better?'})
    root = lxml.html.fromstring(r.text)
    albums = []

    for row in root.cssselect("#artist tr"):
        section = extract(row, "td h3")
        if section is not None:
            if section == "Albums":
                continue
            if section == "Singles & EPs":
                break

        id = row.get("data-object-id")
        type = row.get("data-object-type")
        title = extract(row, ".title a")
        formats = extract(row, ".title .format")
        year = extract(row, "td[data-header=\"Year: \"]")
        try:
            date = datetime(int(year), 1, 1)
        except:
            date = datetime(1000, 1, 1)
        if formats is not None:
            if 'album' in formats.lower():
                albums.append({'id': id, 'title': title, 'date': date})
        albums = sorted(albums, key=itemgetter('date'), reverse=True)

    return albums
